#!/usr/bin/env python3
"""Generate AVIF/WebP variants for site images and wrap <img> tags in <picture>.

Idempotent: re-running skips variants that are already newer than their source
and leaves <img> tags that are already inside a <picture> alone.

The srcset widths and the `sizes` attribute come from tools/img-display-widths.json,
which records how wide each image actually renders at 390px and 1440px viewports
(produced by measuring the real pages in a headless browser). Without that, `sizes`
is guesswork and the browser happily downloads a 2560px file for a 440px slot.

Usage:
  python3 tools/build_responsive_images.py            # whole site
  python3 tools/build_responsive_images.py pages/accommodation.html
  python3 tools/build_responsive_images.py --dry-run
"""
import json, os, re, sys, glob
from urllib.parse import quote, unquote
import html as htmlmod
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIDTHS = json.load(open(os.path.join(ROOT, 'tools/img-display-widths.json')))
RASTER = re.compile(r'\.(jpe?g|png)$', re.I)
DEFAULT_MOBILE, DEFAULT_DESKTOP = 390, 900
AVIF_Q, WEBP_Q = 55, 72
MAX_LADDER = 2                      # variants per format; 2 covers 1x and 2x
DRY = '--dry-run' in sys.argv


def round100(n):
    """Round UP to the next 100.

    Rounding to nearest would put a 1440px slot's candidate at 1400w, which is
    narrower than the slot — so the browser skips it and takes the next rung up
    (often the 2560w original), downloading more than before.
    """
    return max(200, int(-(-n // 100) * 100))


def ladder_for(key, intrinsic_w):
    """Widths to generate: mobile@2x/desktop@1x, then desktop@2x. Capped at intrinsic."""
    info = WIDTHS.get(key) or {}
    m = info.get('m') or DEFAULT_MOBILE
    d = info.get('d') or DEFAULT_DESKTOP
    if not m: m = DEFAULT_MOBILE
    if not d: d = DEFAULT_DESKTOP
    cands = [round100(max(m * 2, d)), round100(d * 2)]
    out = []
    for w in cands:
        w = min(w, intrinsic_w)
        if w not in out:
            out.append(w)
    return sorted(out)[:MAX_LADDER], m, d


def variant_path(src, w, ext):
    stem, _ = os.path.splitext(src)
    return f'{stem}-{w}.{ext}'


def url_quote(path):
    """Percent-encode a path for use in srcset.

    A literal space inside srcset separates the URL from its width descriptor,
    so any asset whose folder or filename contains a space (several of ours do)
    silently breaks the whole candidate list unless it is encoded.
    """
    return quote(path, safe='/-_.~()')


def generate(src_rel):
    """Make the AVIF/WebP variants for one image. Returns (widths, sizes_m, sizes_d, intrinsic)."""
    src_abs = os.path.join(ROOT, src_rel)
    if not os.path.exists(src_abs):
        return None
    try:
        im = Image.open(src_abs)
    except Exception:
        return None
    intrinsic = im.width
    widths, m, d = ladder_for(src_rel, intrinsic)
    if not widths:
        return None
    src_mtime = os.path.getmtime(src_abs)
    made = []
    for w in widths:
        for ext, q in (('avif', AVIF_Q), ('webp', WEBP_Q)):
            out_rel = variant_path(src_rel, w, ext)
            out_abs = os.path.join(ROOT, out_rel)
            if os.path.exists(out_abs) and os.path.getmtime(out_abs) >= src_mtime:
                continue
            if DRY:
                made.append(out_rel); continue
            img = Image.open(src_abs)
            if img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGB')
            if img.width != w:
                img = img.resize((w, round(img.height * w / img.width)), Image.LANCZOS)
            os.makedirs(os.path.dirname(out_abs), exist_ok=True)
            try:
                img.save(out_abs, ext.upper(), quality=q, **({'method': 6} if ext == 'webp' else {}))
                made.append(out_rel)
            except Exception as e:
                print(f'  ! {out_rel}: {e}')
    return widths, m, d, intrinsic, made


IMG_TAG = re.compile(r'<img\b[^>]*?>', re.S)
ATTR = lambda tag, name: (re.search(rf'\b{name}="([^"]*)"', tag) or [None, None])[1]


def in_picture(html, pos):
    """True if the <img> at pos sits inside a <picture> element."""
    before = html[:pos]
    return before.rfind('<picture') > before.rfind('</picture>')


def process_html(path):
    rel = os.path.relpath(path, ROOT)
    html = open(path, encoding='utf-8').read()
    original = html
    out = []
    last = 0
    wrapped = skipped = 0
    for m in IMG_TAG.finditer(html):
        tag = m.group(0)
        src = ATTR(tag, 'src')
        if not src or src.startswith(('http', 'data:')) or not RASTER.search(src):
            continue
        if in_picture(html, m.start()):
            skipped += 1
            continue
        # `src` is raw HTML: it may carry entities (&amp;) and may be written
        # relative to the page (../Assets/...) rather than site-absolute. Resolve
        # it to a repo-relative path for disk work, and remember how to write the
        # variant back out in the same style the page already uses.
        src_dec = htmlmod.unescape(src)
        page_dir_rel = os.path.dirname(rel)
        if src_dec.startswith('/'):
            key = src_dec.lstrip('/')
            def to_url(variant_rel):
                return '/' + url_quote(variant_rel)
        else:
            key = os.path.normpath(os.path.join(page_dir_rel, src_dec))
            def to_url(variant_rel, _base=page_dir_rel):
                return url_quote(os.path.relpath(variant_rel, _base).replace(os.sep, '/'))
        res = generate(key)
        if not res:
            skipped += 1
            continue
        widths, mw, dw, intrinsic, _made = res
        if len(widths) == 1 and widths[0] >= intrinsic * 0.95:
            # Nothing to gain: the image is already about the size it is displayed at.
            skipped += 1
            continue
        def srcset(ext):
            return ', '.join(f'{to_url(variant_path(key, w, ext))} {w}w' for w in widths)
        sizes = f'(max-width: 768px) {mw}px, {dw}px'
        # Give the fallback <img> intrinsic dimensions so the slot does not jump.
        newtag = tag
        if not ATTR(tag, 'width'):
            try:
                iw, ih = Image.open(os.path.join(ROOT, key)).size
                newtag = newtag[:-1].rstrip() + f' width="{iw}" height="{ih}">'
            except Exception:
                pass
        if not ATTR(newtag, 'decoding'):
            newtag = newtag[:-1].rstrip() + ' decoding="async">'
        picture = (
            '<picture>'
            f'<source type="image/avif" sizes="{sizes}" srcset="{srcset("avif")}">'
            f'<source type="image/webp" sizes="{sizes}" srcset="{srcset("webp")}">'
            f'{newtag}</picture>'
        )
        out.append(html[last:m.start()]); out.append(picture)
        last = m.end()
        wrapped += 1
    out.append(html[last:])
    result = ''.join(out)
    if result != original and not DRY:
        open(path, 'w', encoding='utf-8').write(result)
    print(f'{rel}: wrapped {wrapped}, skipped {skipped}')
    return wrapped


targets = [a for a in sys.argv[1:] if not a.startswith('--')]
if not targets:
    targets = ['index.html'] + sorted(glob.glob(os.path.join(ROOT, 'pages/*.html')))
total = 0
for t in targets:
    p = t if os.path.isabs(t) else os.path.join(ROOT, t)
    if os.path.exists(p):
        total += process_html(p)
print(f'\n{"DRY RUN — " if DRY else ""}wrapped {total} <img> tags')


# ---------------------------------------------------------------------------
# CSS background images.
#
# background-image: url(...) cannot use <picture>, so each one gets a single
# capped WebP instead. Not responsive, but a 1600px WebP still beats a 4000px
# camera original by an order of magnitude. The original file stays on disk.
# Run with --css.
# ---------------------------------------------------------------------------
CSS_URL = re.compile(r"url\(\s*'?\"?((?!https?:|data:)[^\"')]+\.(?:jpe?g|png))'?\"?\s*\)", re.I)
BG_WIDTH, BG_Q = 1600, 74


def build_css_backgrounds(paths):
    converted = saved = 0
    for path in paths:
        html = open(path, encoding='utf-8').read()
        original = html
        for src in sorted(set(CSS_URL.findall(html))):
            key = unquote(src.lstrip('/'))
            src_abs = os.path.join(ROOT, key)
            if not os.path.exists(src_abs):
                continue
            stem, _ = os.path.splitext(key)
            out_rel = f'{stem}-bg{BG_WIDTH}.webp'
            out_abs = os.path.join(ROOT, out_rel)
            if not os.path.exists(out_abs) or os.path.getmtime(out_abs) < os.path.getmtime(src_abs):
                if DRY:
                    converted += 1
                    continue
                img = Image.open(src_abs)
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')
                if img.width > BG_WIDTH:
                    img = img.resize((BG_WIDTH, round(img.height * BG_WIDTH / img.width)), Image.LANCZOS)
                img.save(out_abs, 'WEBP', quality=BG_Q, method=6)
            # Only adopt the WebP if it is actually smaller than the original.
            if os.path.getsize(out_abs) >= os.path.getsize(src_abs):
                os.remove(out_abs)
                continue
            saved += os.path.getsize(src_abs) - os.path.getsize(out_abs)
            prefix = '/' if src.startswith('/') else ''
            html = html.replace(f'{src}', f'{prefix}{url_quote(out_rel)}' if not src.startswith('/') else url_quote('/' + out_rel))
            converted += 1
        if html != original and not DRY:
            open(path, 'w', encoding='utf-8').write(html)
    print(f'CSS backgrounds converted: {converted}, saved {saved/1024/1024:.1f} MB')


if '--css' in sys.argv:
    build_css_backgrounds([p if os.path.isabs(p) else os.path.join(ROOT, p) for p in targets])
