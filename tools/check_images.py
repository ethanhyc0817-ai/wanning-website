#!/usr/bin/env python3
"""Fail the build when a page ships images it should not.

Every rule here exists because the thing it checks actually went wrong once.
Run locally with `python3 tools/check_images.py`; CI runs it on every push.

  --fix-hint   print the exact command to fix each failure (default on)
  --budget-only  skip the per-image rules, only check page weight
"""
import html as htmlmod
import os, re, sys, glob, json
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# --- thresholds -------------------------------------------------------------
# Set above today's worst case so this catches regressions, not the status quo.
MAX_SOURCE_IMAGE_KB   = 4500   # a single source file in Assets/
MAX_UNWRAPPED_KB      = 150    # a raster <img> with no <picture>/srcset around it
MAX_PAGE_IMAGE_MB     = 4.0    # see note below
MIN_DISPLAY_WIDTH     = 200    # below this an <img> is a logo; exempt
ROOT_PUBLISHABLE_EXT  = ('.png', '.jpg', '.jpeg', '.pdf', '.html')

WIDTHS = json.load(open('tools/img-display-widths.json')) if os.path.exists('tools/img-display-widths.json') else {}
PAGES = ['index.html'] + sorted(glob.glob('pages/*.html'))
RASTER = re.compile(r'\.(jpe?g|png)$', re.I)
failures, warnings = [], []


def resolve(src, page):
    """HTML src -> path on disk. Handles &amp;, %20 and page-relative paths."""
    s = unquote(htmlmod.unescape(src))
    if s.startswith('http') or s.startswith('data:'):
        return None
    return s.lstrip('/') if s.startswith('/') else os.path.normpath(os.path.join(os.path.dirname(page), s))


def in_picture(html, pos):
    before = html[:pos]
    return before.rfind('<picture') > before.rfind('</picture>')


# 1. A raster <img> with no <picture> around it, over the byte threshold.
#    This is the original bug: full-size JPEGs shipped to phones.
for page in PAGES:
    s = open(page, encoding='utf-8').read()
    for m in re.finditer(r'<img\b[^>]*?>', s):
        src = (re.search(r'src="([^"]*)"', m.group(0)) or [None, ''])[1]
        if not src or not RASTER.search(unquote(src)):
            continue
        p = resolve(src, page)
        if not p or not os.path.exists(p) or in_picture(s, m.start()):
            continue
        key = p
        w = WIDTHS.get(key, {})
        if max(w.get('m', 0), w.get('d', 0)) and max(w.get('m', 0), w.get('d', 0)) < MIN_DISPLAY_WIDTH:
            continue                      # logo / icon, exempt by design
        kb = os.path.getsize(p) / 1024
        if kb > MAX_UNWRAPPED_KB:
            failures.append(f'{page}: <img> ships {kb:.0f}KB unoptimised — {src}')

# 2. Referenced but missing files (a typo, or a variant that was never generated).
for page in PAGES:
    s = open(page, encoding='utf-8').read()
    for ss in re.findall(r'srcset="([^"]+)"', s):
        for cand in [x.strip().split(' ')[0] for x in ss.split(',')]:
            if not cand or cand.startswith('http'):
                continue
            p = resolve(cand, page)
            if p and not os.path.exists(p):
                failures.append(f'{page}: srcset points at a missing file — {cand}')

# 3. <picture> markup that would break layout.
for page in PAGES:
    s = re.sub(r'<!--.*?-->', '', open(page, encoding='utf-8').read(), flags=re.S)
    if s.count('<picture') != s.count('</picture>'):
        failures.append(f'{page}: unbalanced <picture> tags')
    if re.search(r'<picture[^>]*>(?:(?!</picture>).)*<picture', s, re.S):
        failures.append(f'{page}: nested <picture>')
    # Wrapping an <img> only stays layout-neutral with these two rules present.
    if '<picture' in s and 'picture{display:contents}' not in s:
        failures.append(f'{page}: has <picture> but is missing picture{{display:contents}}')
    if 'picture{display:contents}' in s and 'picture>source{display:none}' not in s:
        failures.append(f'{page}: display:contents without picture>source{{display:none}} '
                        '(sources become grid items)')

# (A rule for stretched <img> used to live here. It flagged any width/height
# without an INLINE height, but the height usually comes from CSS it cannot see,
# so it only produced false positives. The real guard for stretching is the
# rendered pixel-diff, not a static scan.)

# 5. Total image weight per page — as a phone would actually download it.
#    This is the whole page, not first paint: lazy-loaded images below the fold
#    count, and index.html holds all 14 SPA sub-pages, so it totals ~3.7MB while
#    a real first load is ~1.3MB. The budget is set above today's worst page so
#    it flags growth. For true first-load numbers use the headless benchmark,
#    not this static scan.
#    Counting the <img> fallback instead would report 21MB for a page that
#    really pulls ~550KB, because the fallback is only for browsers with no AVIF.
for page in PAGES:
    s_ = open(page, encoding='utf-8').read()
    seen, total = set(), 0
    for pic in re.finditer(r'<picture>.*?</picture>', s_, re.S):
        block = pic.group(0)
        av = re.search(r'type="image/avif"[^>]*srcset="([^"]+)"', block)
        cands = []
        if av:
            for c in av.group(1).split(','):
                c = c.strip().split(' ')[0]
                q = resolve(c, page)
                if q and os.path.exists(q):
                    cands.append(q)
        if cands:
            pick = min(cands, key=os.path.getsize)      # narrowest rung = phone
        else:
            img = re.search(r'<img[^>]+src="([^"]+)"', block)
            pick = resolve(img.group(1), page) if img else None
        if pick and os.path.exists(pick) and pick not in seen:
            seen.add(pick); total += os.path.getsize(pick)
    # bare <img> (no <picture>) and CSS backgrounds count at full size
    for m in re.finditer(r'<img\b[^>]*?>', s_):
        if in_picture(s_, m.start()):
            continue
        src = (re.search(r'src="([^"]*)"', m.group(0)) or [None, ''])[1]
        q = resolve(src, page) if src else None
        if q and os.path.exists(q) and RASTER.search(q) and q not in seen:
            seen.add(q); total += os.path.getsize(q)
    for src in re.findall(r"url\(\s*'?\"?([^\"')]+)", s_):
        q = resolve(src, page)
        if q and os.path.exists(q) and RASTER.search(q) and q not in seen:
            seen.add(q); total += os.path.getsize(q)
    if total / 1048576 > MAX_PAGE_IMAGE_MB:
        failures.append(f'{page}: {total/1048576:.1f}MB of images on a phone (budget {MAX_PAGE_IMAGE_MB}MB)')

# 6. Oversized source files.
for p in glob.glob('Assets/**/*', recursive=True):
    if os.path.isfile(p) and RASTER.search(p):
        kb = os.path.getsize(p) / 1024
        if kb > MAX_SOURCE_IMAGE_KB:
            failures.append(f'{p}: source image is {kb/1024:.1f}MB (max {MAX_SOURCE_IMAGE_KB/1024:.1f}MB)')

# 7. Anything in the repo root Vercel would serve publicly. Two accidents so far:
#    four social-post mockups and a 24MB brochure build artifact.
import subprocess
_tracked_root = [f for f in subprocess.run(['git', 'ls-files'], capture_output=True, text=True)
                 .stdout.split('\n') if f and '/' not in f]
for f in _tracked_root:
    if f.lower().endswith(ROOT_PUBLISHABLE_EXT) and f not in ('index.html', 'favicon.ico'):
        warnings.append(f'{f}: sits in the repo root, so it is served publicly at surfchina.co/{f}')

for w in warnings:
    print(f'  warning  {w}')
if failures:
    print(f'\n{len(failures)} problem(s):\n')
    for f in failures:
        print(f'  FAIL  {f}')
    print('\nFix with:  python3 tools/build_responsive_images.py [page.html]')
    print('           python3 tools/build_responsive_images.py --css [page.html]')
    sys.exit(1)
print(f'\nimage checks passed ({len(PAGES)} pages)' + (f', {len(warnings)} warning(s)' if warnings else ''))
