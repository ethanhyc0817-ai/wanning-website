"""
Surf & Golf — Hainan
Premium & Luxury package brochure (PDF)

HOW TO BUILD:
    python3 build_brochure.py
Output: Surf_and_Golf_Hainan_Brochure.pdf in this folder.

Requires:  pip install reportlab pillow
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, NextPageTemplate,
    Paragraph, Spacer, Image, Table, TableStyle, PageBreak,
    KeepTogether, Flowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from PIL import Image as PILImage
import os
import glob

# ---- Paths ----
# Auto-detect the Wanning folder: try local Mac path, then Cowork session mount,
# otherwise fall back to the directory this script lives in.
def _find_wanning_dir():
    candidates = [
        "/Users/ethanhuang/Documents/Wanning",
        *glob.glob("/sessions/*/mnt/Wanning"),
        os.path.dirname(os.path.abspath(__file__)),
    ]
    for c in candidates:
        if os.path.isdir(os.path.join(c, "Assets", "planner")):
            return c
    raise RuntimeError(
        "Could not locate the Wanning folder. Set WANNING_DIR manually.")

WANNING_DIR = _find_wanning_dir()
ROOT = os.path.join(WANNING_DIR, "Assets", "planner")
MH_CROP = os.path.join(ROOT, "观澜湖_cropped")  # 3:2 cropped Mission Hills
OUTPUT_PDF = os.path.join(WANNING_DIR, "Surf_and_Golf_Hainan_Brochure.pdf")


# ---- Auto-crop Mission Hills photos to uniform 3:2 ----
# Runs every build. Skips files that are already up-to-date (source not newer
# than the cropped version), so it's cheap on re-runs. Add a new photo to
# 观澜湖/ and the cropped copy appears automatically.
def _ensure_mh_cropped():
    src_dir = os.path.join(ROOT, "观澜湖")
    if not os.path.isdir(src_dir):
        return
    os.makedirs(MH_CROP, exist_ok=True)
    TARGET = 1.50  # 3:2
    for fn in sorted(os.listdir(src_dir)):
        if fn.startswith('.') or not fn.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
        s = os.path.join(src_dir, fn)
        d = os.path.join(MH_CROP, fn)
        if os.path.exists(d) and os.path.getmtime(d) >= os.path.getmtime(s):
            continue
        with PILImage.open(s) as im:
            w, h = im.size
            r = w / h
            if r > TARGET:
                new_w = int(h * TARGET)
                left = (w - new_w) // 2
                im2 = im.crop((left, 0, left + new_w, h))
            else:
                new_h = int(w / TARGET)
                top = (h - new_h) // 2
                im2 = im.crop((0, top, w, top + new_h))
            im2.save(d, quality=90)

_ensure_mh_cropped()

# ---- Colors ----
NAVY    = HexColor("#0B2545")    # deep ocean navy
GOLD    = HexColor("#C9A86A")    # muted gold / sand accent
CORAL   = HexColor("#D87C5A")    # sunset coral
CREAM   = HexColor("#F5EFE6")    # warm off-white
SAND    = HexColor("#EFE6D6")
INK     = HexColor("#1A1A1A")
GREY    = HexColor("#5C5C5C")
LIGHTL  = HexColor("#E5DDC8")    # divider line
GREEN   = HexColor("#2D5F4A")    # tropical green

# ---- Page setup ----
PAGE_W, PAGE_H = A4
MARGIN_L = 18 * mm
MARGIN_R = 18 * mm
MARGIN_T = 22 * mm
MARGIN_B = 22 * mm
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R

# ---- Styles ----
styles = getSampleStyleSheet()

style_hero_title = ParagraphStyle(
    "HeroTitle", parent=styles["Title"],
    fontName="Helvetica-Bold", fontSize=46, leading=52,
    textColor=colors.white, alignment=TA_LEFT, spaceBefore=0, spaceAfter=6,
)
style_hero_sub = ParagraphStyle(
    "HeroSub", parent=styles["Normal"],
    fontName="Helvetica", fontSize=13, leading=18,
    textColor=colors.white, alignment=TA_LEFT, spaceAfter=4,
)
style_hero_kicker = ParagraphStyle(
    "HeroKicker", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=10, leading=12,
    textColor=GOLD, alignment=TA_LEFT, spaceAfter=10,
)
style_section_kicker = ParagraphStyle(
    "SectionKicker", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=9, leading=12,
    textColor=CORAL, alignment=TA_LEFT, spaceAfter=4,
)
style_h1 = ParagraphStyle(
    "H1", parent=styles["Heading1"],
    fontName="Helvetica-Bold", fontSize=28, leading=32,
    textColor=NAVY, alignment=TA_LEFT, spaceBefore=0, spaceAfter=8,
)
style_h2 = ParagraphStyle(
    "H2", parent=styles["Heading2"],
    fontName="Helvetica-Bold", fontSize=16, leading=20,
    textColor=NAVY, alignment=TA_LEFT, spaceBefore=6, spaceAfter=6,
)
style_h3 = ParagraphStyle(
    "H3", parent=styles["Heading3"],
    fontName="Helvetica-Bold", fontSize=11, leading=14,
    textColor=NAVY, alignment=TA_LEFT, spaceBefore=4, spaceAfter=4,
)
style_body = ParagraphStyle(
    "Body", parent=styles["Normal"],
    fontName="Helvetica", fontSize=10, leading=15,
    textColor=INK, alignment=TA_LEFT, spaceAfter=6,
)
style_body_justify = ParagraphStyle(
    "BodyJ", parent=style_body, alignment=TA_JUSTIFY,
)
style_lead = ParagraphStyle(
    "Lead", parent=styles["Normal"],
    fontName="Helvetica", fontSize=12, leading=18,
    textColor=INK, alignment=TA_LEFT, spaceAfter=8,
)
style_small = ParagraphStyle(
    "Small", parent=styles["Normal"],
    fontName="Helvetica", fontSize=8.5, leading=12,
    textColor=GREY, alignment=TA_LEFT, spaceAfter=4,
)
style_caption = ParagraphStyle(
    "Caption", parent=styles["Normal"],
    fontName="Helvetica-Oblique", fontSize=8.5, leading=11,
    textColor=GREY, alignment=TA_CENTER, spaceAfter=2,
)
style_price = ParagraphStyle(
    "Price", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=22, leading=24,
    textColor=NAVY, alignment=TA_LEFT, spaceAfter=2,
)
style_price_sub = ParagraphStyle(
    "PriceSub", parent=styles["Normal"],
    fontName="Helvetica", fontSize=9, leading=12,
    textColor=GREY, alignment=TA_LEFT, spaceAfter=8,
)
style_tag = ParagraphStyle(
    "Tag", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=8, leading=10,
    textColor=colors.white, alignment=TA_CENTER,
)
style_quote = ParagraphStyle(
    "Quote", parent=styles["Normal"],
    fontName="Helvetica-Oblique", fontSize=12, leading=18,
    textColor=NAVY, alignment=TA_LEFT, leftIndent=14, rightIndent=8,
    spaceAfter=8, spaceBefore=4,
)
style_bullet = ParagraphStyle(
    "Bullet", parent=style_body,
    leftIndent=14, bulletIndent=2, spaceAfter=3,
)
style_footer = ParagraphStyle(
    "Footer", parent=styles["Normal"],
    fontName="Helvetica", fontSize=7.5, leading=10,
    textColor=GREY, alignment=TA_CENTER,
)


# ---- Helpers ----

def sized_image(path, width):
    """Image scaled to a target width, preserving aspect ratio."""
    with PILImage.open(path) as im:
        w, h = im.size
    height = width * h / w
    img = Image(path, width=width, height=height)
    return img


def image_grid(paths, cols, total_width, gutter=4, row_height=None):
    """Build a Table with images arranged in cols. If row_height given, all
    images are forced to that height (cropping the aspect via width adjustment)."""
    cell_w = (total_width - gutter * (cols - 1)) / cols
    rows = []
    row = []
    for p in paths:
        with PILImage.open(p) as im:
            iw, ih = im.size
        if row_height:
            h = row_height
            w = cell_w
        else:
            h = cell_w * ih / iw
            w = cell_w
        row.append(Image(p, width=w, height=h))
        if len(row) == cols:
            rows.append(row)
            row = []
    if row:
        while len(row) < cols:
            row.append("")
        rows.append(row)
    t = Table(rows, colWidths=[cell_w] * cols)
    t.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return t


def hr(thickness=0.5, color=LIGHTL, space_before=4, space_after=6):
    class HR(Flowable):
        def __init__(self):
            Flowable.__init__(self)
            self.width = CONTENT_W
            self.height = thickness + space_before + space_after
        def draw(self):
            self.canv.setStrokeColor(color)
            self.canv.setLineWidth(thickness)
            y = space_after
            self.canv.line(0, y, self.width, y)
    return HR()


def chip(text, fill=NAVY, txt=colors.white):
    t = Table([[Paragraph(f'<font color="{txt.hexval()[2:]}">{text}</font>'
                          if hasattr(txt, "hexval")
                          else f'<font color="white">{text}</font>',
                          ParagraphStyle("c", parent=style_tag))]],
              colWidths=[None])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), fill),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


# ---- Page templates ----

def draw_cover_bg(canv, doc):
    """Cover page: full-bleed image with dark overlay + brand mark + footer."""
    canv.saveState()
    # background image — cover-fit: fill entire page, crop excess
    bg_path = os.path.join(ROOT, "神州半岛", "IMG_cover.JPG")
    with PILImage.open(bg_path) as _im:
        iw, ih = _im.size
    img_ratio = iw / ih
    page_ratio = PAGE_W / PAGE_H
    if img_ratio > page_ratio:
        # image relatively wider → fit height, crop sides
        h = PAGE_H
        w = h * img_ratio
        x = (PAGE_W - w) / 2
        y = 0
    else:
        # image relatively taller → fit width, crop top/bottom
        w = PAGE_W
        h = w / img_ratio
        x = 0
        y = (PAGE_H - h) / 2
    canv.drawImage(bg_path, x, y, width=w, height=h,
                   preserveAspectRatio=False, mask=None)
    # dark gradient overlay using two rectangles (subtle)
    canv.setFillColor(HexColor("#000000"))
    canv.setFillAlpha(0.55)
    canv.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    # bottom navy band
    canv.setFillColor(NAVY)
    canv.setFillAlpha(0.92)
    canv.rect(0, 0, PAGE_W, 90 * mm, stroke=0, fill=1)
    # gold accent line
    canv.setFillColor(GOLD)
    canv.setFillAlpha(1.0)
    canv.rect(MARGIN_L, 90 * mm, 36 * mm, 0.8 * mm, stroke=0, fill=1)
    # brand mark top
    canv.setFillColor(colors.white)
    canv.setFillAlpha(1.0)
    canv.setFont("Helvetica-Bold", 11)
    canv.drawString(MARGIN_L, PAGE_H - MARGIN_T, "SURFCHINA  ·  WANNING, HAINAN")
    canv.setFont("Helvetica", 9)
    canv.setFillColor(GOLD)
    canv.drawRightString(PAGE_W - MARGIN_R, PAGE_H - MARGIN_T,
                         "TRIP GUIDE  ·  2026 SEASON")
    # contact line at the very bottom of the navy band
    canv.setFillColor(HexColor("#A89878"))  # muted gold
    canv.setFont("Helvetica", 8)
    canv.drawCentredString(PAGE_W / 2, 10 * mm,
                           "surfchinaco@gmail.com   ·   "
                           "WhatsApp +86 138 9340 2173   ·   "
                           "IG @surfchina.co")
    canv.restoreState()


CONTACT_LINE = (
    "surfchinaco@gmail.com   ·   WhatsApp +86 138 9340 2173   ·   "
    "IG @surfchina.co"
)


def draw_page_chrome(canv, doc):
    """Standard page: top thin gold rule + bottom footer."""
    canv.saveState()
    # top header strip
    canv.setFillColor(NAVY)
    canv.rect(0, PAGE_H - 12 * mm, PAGE_W, 12 * mm, stroke=0, fill=1)
    canv.setFillColor(colors.white)
    canv.setFont("Helvetica-Bold", 8.5)
    canv.drawString(MARGIN_L, PAGE_H - 8 * mm, "SURFCHINA  ·  SURF & GOLF — HAINAN")
    canv.setFillColor(GOLD)
    canv.setFont("Helvetica", 8.5)
    canv.drawRightString(PAGE_W - MARGIN_R, PAGE_H - 8 * mm, "Trip Guide")
    # gold rule below header
    canv.setFillColor(GOLD)
    canv.rect(0, PAGE_H - 13 * mm, PAGE_W, 0.6 * mm, stroke=0, fill=1)
    # footer — contact line (left) + page number (right)
    canv.setFillColor(GREY)
    canv.setFont("Helvetica", 7.5)
    canv.drawString(MARGIN_L, 10 * mm, CONTACT_LINE)
    canv.drawRightString(PAGE_W - MARGIN_R, 10 * mm, f"Page {doc.page - 1}")
    # bottom gold rule
    canv.setFillColor(GOLD)
    canv.setFillAlpha(0.6)
    canv.rect(MARGIN_L, 14 * mm, CONTENT_W, 0.3 * mm, stroke=0, fill=1)
    canv.restoreState()


# ---- Document ----
doc = BaseDocTemplate(
    OUTPUT_PDF,
    pagesize=A4,
    leftMargin=MARGIN_L, rightMargin=MARGIN_R,
    topMargin=18 * mm, bottomMargin=18 * mm,
    title="Surf & Golf — Hainan",
    author="SurfChina",
)

cover_frame = Frame(MARGIN_L, 0, PAGE_W - MARGIN_L - MARGIN_R, PAGE_H,
                    leftPadding=0, bottomPadding=0,
                    rightPadding=0, topPadding=0, showBoundary=0)
content_frame = Frame(MARGIN_L, MARGIN_B,
                      CONTENT_W, PAGE_H - MARGIN_T - MARGIN_B,
                      leftPadding=0, bottomPadding=0,
                      rightPadding=0, topPadding=0, showBoundary=0)

doc.addPageTemplates([
    PageTemplate(id="cover", frames=[cover_frame], onPage=draw_cover_bg),
    PageTemplate(id="content", frames=[content_frame], onPage=draw_page_chrome),
])

story = []

# =====================================================
# COVER PAGE
# =====================================================
# Push content so it lands in the bottom navy band (~75mm tall)
story.append(Spacer(1, PAGE_H - 78 * mm))
story.append(Paragraph("TRIP GUIDE &middot; HAINAN ISLAND &middot; 2026",
                       style_hero_kicker))
story.append(Paragraph("Surf, Golf<br/>&amp; Hainan", style_hero_title))
story.append(Paragraph(
    "Surf in the morning. Tee off after lunch.<br/>"
    "Yacht the next day. More than golf and surf.",
    style_hero_sub))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "Wanning &middot; Hainan Island &middot; The South China Sea",
    ParagraphStyle("c2", parent=style_hero_sub, textColor=GOLD,
                   fontName="Helvetica-Bold", fontSize=9.5)))

# Move to content pages
story.append(NextPageTemplate("content"))
story.append(PageBreak())

# =====================================================
# PAGE 2 — THE PITCH
# =====================================================
story.append(Spacer(1, 4))
story.append(Paragraph("THE PROPOSAL", style_section_kicker))
story.append(Paragraph("Surf in the morning. Tee off after lunch.", style_h1))
story.append(hr())

story.append(Paragraph(
    "There aren't many places in the world where you can paddle into a "
    "shoulder-high wave at sunrise and walk a championship golf course by "
    "lunch. Hainan is one of them. Built for surfers and golfers &mdash; "
    "whether you're traveling solo, as a couple, or with a crew &mdash; "
    "designed around a custom wave pool, two of the highest-ranked courses "
    "in China, and the kind of stay you remember years later.",
    style_lead))

story.append(Spacer(1, 6))

# -------- Side-by-side comparison table --------
feat_label_style = ParagraphStyle(
    "feat", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=8.5, leading=11,
    textColor=NAVY, alignment=TA_LEFT)
pkg_tag_style = ParagraphStyle(
    "pkgtag", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=10, leading=12,
    textColor=colors.white, alignment=TA_CENTER)
pkg_price_style = ParagraphStyle(
    "pkgprice", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=20, leading=22,
    textColor=NAVY, alignment=TA_CENTER, spaceBefore=4, spaceAfter=0)
pkg_pp_style = ParagraphStyle(
    "pkgpp", parent=styles["Normal"],
    fontName="Helvetica", fontSize=8, leading=10,
    textColor=GREY, alignment=TA_CENTER, spaceBefore=2)
cell_text_style = ParagraphStyle(
    "celltext", parent=styles["Normal"],
    fontName="Helvetica", fontSize=9.5, leading=13,
    textColor=INK, alignment=TA_LEFT)

# Column widths
FEAT_W = 28 * mm
COL_W = (CONTENT_W - FEAT_W) / 2

def pkg_banner(label, color, w):
    t = Table([[Paragraph(label, pkg_tag_style)]], colWidths=[w])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t

def stacked_header(banner, price, w):
    inner = Table([
        [banner],
        [Paragraph(price, pkg_price_style)],
        [Paragraph("per person, USD", pkg_pp_style)],
    ], colWidths=[w])
    inner.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (0, 0), 0),
        ("TOPPADDING", (0, 1), (-1, 1), 4),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 6),
        ("BACKGROUND", (0, 1), (-1, -1), CREAM),
    ]))
    return inner

hdr_prem = stacked_header(pkg_banner("PREMIUM", NAVY, COL_W),
                          "FROM <b>$3,043</b>", COL_W)
hdr_lux = stacked_header(pkg_banner("LUXURY", CORAL, COL_W),
                         "FROM <b>$6,625</b>", COL_W)

# Feature rows — quantities shown PER PERSON (matches per-person price).
features = [
    ("DURATION",
     "7 nights / 8 days",
     "11 nights / 12 days"),
    ("CITIES",
     "Wanning &middot; Haikou",
     "Wanning &middot; <b>Sanya</b> &middot; Haikou"),
    ("STAY",
     "<b>Wave Pool Resort</b> &middot; 5 nights<br/>"
     "Ocean &amp; Pool View Room<br/>"
     "<b>+ Ritz-Carlton, Haikou</b> &middot; 2 nights<br/>"
     "Deluxe Golf Ocean View",
     "<b>Wave Pool Resort</b> &middot; 4 nights<br/>"
     "Owner&rsquo;s Suite<br/>"
     "<b>+ Rosewood Sanya</b> &middot; 5 nights<br/>"
     "Deluxe Ocean View (Haitang Bay)<br/>"
     "<b>+ Ritz-Carlton, Haikou</b> &middot; 2 nights<br/>"
     "Golf Suite (100+ sqm)"),
    ("SURF",
     "3 PerfectSwell&reg; sessions<br/>"
     "soft-top board rental",
     "3 PerfectSwell&reg; sessions<br/>"
     "premium board rental<br/>"
     "<font size=8 color='#5C5C5C'>private pool buyout available as add-on</font>"),
    ("GOLF<br/><font color='#5C5C5C'>3 rounds<br/>"
     "<font size=7>caddies included</font></font>",
     "<b>The Dunes at Shenzhou</b> &middot; 2 rounds<br/>"
     "<b>Mission Hills</b> Blackstone &middot; 1 round",
     "<b>The Dunes at Shenzhou</b> &middot; 1 round<br/>"
     "<b>Lu Hui Tou, Sanya</b> &middot; 1 round<br/>"
     "<b>Mission Hills</b> Blackstone &middot; 1 round"),
    ("YACHT",
     "&mdash;",
     "<b>Full-day private yacht charter</b><br/>"
     "<font size=8 color='#5C5C5C'>Sanya Bay / Yalong Bay &middot; "
     "swim, paddle, lunch on board</font>"),
    ("CULTURE",
     "Haikou city tour<br/>"
     "<font size=8 color='#5C5C5C'>Qilou Old Street</font>",
     "Haikou city tour<br/>"
     "<b>+ Nanshan Temple</b><br/>"
     "<b>+ Areca Manor</b><br/>"
     "<b>+ Sanya night market</b>"),
    ("VIDEO + DRONE",
     "2 photo sessions",
     "4 photo + 2 drone sessions"),
]

comp_rows = [["", hdr_prem, hdr_lux]]
for feat, prem, lux in features:
    comp_rows.append([
        Paragraph(feat, feat_label_style),
        Paragraph(prem, cell_text_style),
        Paragraph(lux, cell_text_style),
    ])

comp_tbl = Table(comp_rows, colWidths=[FEAT_W, COL_W, COL_W])
comp_tbl.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    # Body rows
    ("LEFTPADDING", (0, 1), (-1, -1), 7),
    ("RIGHTPADDING", (0, 1), (-1, -1), 7),
    ("TOPPADDING", (0, 1), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
    # Header row no padding (banners self-pad)
    ("LEFTPADDING", (0, 0), (-1, 0), 0),
    ("RIGHTPADDING", (0, 0), (-1, 0), 0),
    ("TOPPADDING", (0, 0), (-1, 0), 0),
    ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
    # Feature column cream background
    ("BACKGROUND", (0, 1), (0, -1), CREAM),
    # Horizontal rules between feature rows
    ("LINEBELOW", (0, 1), (-1, -2), 0.3, LIGHTL),
    # Vertical separator between the two packages
    ("LINEBEFORE", (2, 1), (2, -1), 0.5, LIGHTL),
]))
story.append(comp_tbl)

story.append(Spacer(1, 8))

# Footer note: per-person framing
story.append(Paragraph(
    "<i>All quantities shown per person, based on 2 guests sharing. "
    "Solo, couple, or group? Rates on request.</i>",
    ParagraphStyle("note2", parent=style_small, alignment=TA_CENTER,
                   textColor=GREY)))

# (Comparison table replaced the cards; teaser strip removed to keep one page.)

story.append(PageBreak())

# =====================================================
# PAGE 3 — PREMIUM PACKAGE
# =====================================================
story.append(Paragraph("OPTION 1 &middot; PREMIUM", style_section_kicker))
story.append(Paragraph("Premium Surf &amp; Golf Escape", style_h1))
story.append(hr())

# Lead row: image + price block
lead_img = sized_image(
    os.path.join(ROOT, "wavepool", "wavepool-use.JPG"),
    width=CONTENT_W * 0.55,
)
price_block = [
    [Paragraph("FROM", style_section_kicker)],
    [Paragraph("$3,043 USD", style_price)],
    [Paragraph("<b>per person</b> &middot; based on 2 guests sharing<br/>"
               "Package total <b>$6,086 USD</b> &middot; 7N / 8D<br/>"
               "<i>Solo, couple, or group? Rates on request.</i>",
               style_price_sub)],
    [Spacer(1, 4)],
    [Paragraph("STAY", style_h3)],
    [Paragraph("5N Ocean &amp; Pool View, Wave Pool Resort<br/>"
               "2N Deluxe Golf Ocean View, Ritz-Carlton",
               style_body)],
    [Paragraph("SURF + GOLF", style_h3)],
    [Paragraph("3 PerfectSwell&reg; sessions &middot; soft-top board<br/>"
               "3 rounds: Shenzhou &times; 2 &middot; Mission Hills &times; 1<br/>"
               "Caddies included throughout.",
               style_body)],
    [Paragraph("BEYOND", style_h3)],
    [Paragraph("Haikou city tour with English guide &middot; "
               "Qilou Old Street.",
               style_body)],
]
pb_tbl = Table(price_block, colWidths=[CONTENT_W * 0.42])
pb_tbl.setStyle(TableStyle([
    ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 1),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ("LINEBEFORE", (0, 0), (0, -1), 2, GOLD),
]))

lead = Table([[lead_img, pb_tbl]],
             colWidths=[CONTENT_W * 0.55 + 4, CONTENT_W * 0.45 - 4])
lead.setStyle(TableStyle([
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
]))
story.append(lead)
story.append(Spacer(1, 8))

# Included / not-included two columns
prem_included = [
    "Wave Pool Resort &middot; Ocean &amp; Pool View &middot; 5 nights",
    "Ritz-Carlton Haikou &middot; Deluxe Golf Ocean View &middot; 2 nights",
    "3 PerfectSwell&reg; surf sessions &middot; photo coverage",
    "Soft-top board rental throughout Wanning",
    "3 golf rounds &middot; 2 Dunes, 1 Mission Hills",
    "<b>All caddie fees</b> &mdash; every round",
    "4 days private charter car + Premium Car airport transfers",
    "1 day English-speaking guide (Haikou city tour)",
    "Daily breakfast &middot; 24/7 English trip support",
]
prem_not = [
    "International &amp; domestic flights",
    "Meals outside breakfast",
    "Alcohol",
    "Spa / recovery treatments",
    "Private pool buyout (add-on)",
    "Drone coverage (Luxury or add-on)",
    "Additional surf or golf rounds",
    "Personal gratuities",
]

def two_col_lists(left_title, left_items, right_title, right_items,
                  left_color=GREEN, right_color=CORAL):
    def col(title, items, color):
        rows = [[Paragraph(f'<font color="white"><b>{title}</b></font>',
                           ParagraphStyle("h", parent=style_tag, alignment=TA_LEFT))]]
        # color header
        head = Table(rows, colWidths=[CONTENT_W / 2 - 6])
        head.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), color),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        body = [[head]]
        for it in items:
            body.append([Paragraph(f"&bull;&nbsp;&nbsp;{it}", style_bullet)])
        t = Table(body, colWidths=[CONTENT_W / 2 - 6])
        t.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 1), (-1, -1), CREAM),
            ("TOPPADDING", (0, 1), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
            ("LEFTPADDING", (0, 1), (-1, -1), 10),
            ("RIGHTPADDING", (0, 1), (-1, -1), 10),
        ]))
        return t

    left = col(left_title, left_items, left_color)
    right = col(right_title, right_items, right_color)
    t = Table([[left, "", right]],
              colWidths=[CONTENT_W / 2 - 6, 12, CONTENT_W / 2 - 6])
    t.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


story.append(two_col_lists("INCLUDED", prem_included,
                          "NOT INCLUDED", prem_not))
story.append(Spacer(1, 6))

# Image strip — surf action, Shenzhou widescreen, Shenzhou course
strip_paths = [
    os.path.join(ROOT, "wavepool", "wavepool-surfer-action-01.jpg"),
    os.path.join(ROOT, "神州半岛",
                 "24EDDBE1-764E-4F6B-BEF4-306BB565F438.jpg"),
    os.path.join(ROOT, "神州半岛", "IMG_6996.jpg"),
]
story.append(image_grid(strip_paths, cols=3, total_width=CONTENT_W,
                        gutter=4, row_height=30 * mm))

story.append(PageBreak())

# =====================================================
# PAGE 4 — LUXURY PACKAGE
# =====================================================
story.append(Paragraph("OPTION 2 &middot; LUXURY", style_section_kicker))
story.append(Paragraph("Luxury Surf &amp; Golf Escape", style_h1))
story.append(hr())

ultra_lead_img = sized_image(
    os.path.join(ROOT, "神州半岛", "lux.jpg"),
    width=CONTENT_W * 0.55,
)

ultra_price_block = [
    [Paragraph("FROM", style_section_kicker)],
    [Paragraph("$6,625 USD", style_price)],
    [Paragraph("<b>per person</b> &middot; based on 2 guests sharing<br/>"
               "Package total <b>$13,250 USD</b> &middot; 11N / 12D<br/>"
               "<i>Solo, couple, or group? Rates on request.</i>",
               style_price_sub)],
    [Spacer(1, 4)],
    [Paragraph("STAY &middot; 3 CITIES", style_h3)],
    [Paragraph("4N Owner&rsquo;s Suite, Wave Pool Resort<br/>"
               "5N <b>Rosewood Sanya</b>, Haitang Bay<br/>"
               "2N Golf Suite, Ritz-Carlton Haikou",
               style_body)],
    [Paragraph("SURF + GOLF", style_h3)],
    [Paragraph("3 PerfectSwell&reg; &middot; premium board<br/>"
               "3 rounds: Dunes &middot; Lu Hui Tou &middot; Mission Hills<br/>"
               "Caddies included.",
               style_body)],
    [Paragraph("BEYOND", style_h3)],
    [Paragraph("Full-day private yacht &middot; <b>Nanshan Guanyin</b> "
               "(world&rsquo;s tallest) &middot; <b>Areca Manor</b> &middot; "
               "Sanya night market &middot; Haikou city tour.",
               style_body)],
]
upb = Table(ultra_price_block, colWidths=[CONTENT_W * 0.42])
upb.setStyle(TableStyle([
    ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 1),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ("LINEBEFORE", (0, 0), (0, -1), 2, CORAL),
]))
ultra_lead = Table([[ultra_lead_img, upb]],
                   colWidths=[CONTENT_W * 0.55 + 4, CONTENT_W * 0.45 - 4])
ultra_lead.setStyle(TableStyle([
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
]))
story.append(ultra_lead)
story.append(Spacer(1, 8))

# Detailed Luxury inclusion table — compact, headline items only
ultra_table_data = [
    ["INCLUSION", "QTY"],
    ["Owner's Suite, Wave Pool Resort", "4 nights"],
    ["Deluxe Ocean View, Rosewood Sanya · Haitang Bay", "5 nights"],
    ["Golf Suite, Ritz-Carlton Haikou", "2 nights"],
    ["PerfectSwell® surf sessions · premium board rental", "3 sessions"],
    ["Golf — 18-hole rounds (caddies all included)", "3 rounds"],
    ["   — Dunes · Lu Hui Tou · Mission Hills Blackstone", "1 each"],
    ["Full-day private yacht charter (Sanya)", "1 day"],
    ["Private charter car days", "7 days"],
    ["English-speaking guide days", "4 days"],
    ["Round-trip Executive Van airport transfer", "2 trips"],
    ["Professional video + drone sessions", "4 + 2"],
    ["Daily breakfast · 24/7 English trip support", "—"],
]
itable = Table(ultra_table_data, colWidths=[CONTENT_W * 0.72, CONTENT_W * 0.28])
itable.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, 0), 9),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
    ("FONTSIZE", (0, 1), (-1, -1), 9.5),
    ("TEXTCOLOR", (0, 1), (-1, -1), INK),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CREAM, colors.white]),
    ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("LINEBELOW", (0, 0), (-1, 0), 0.5, GOLD),
    ("FONTNAME", (0, 5), (-1, 5), "Helvetica-Bold"),
]))
story.append(itable)

story.append(PageBreak())

# =====================================================
# Helper: AWARDS BLOCK (used for both courses)
# =====================================================
def awards_block(items, bg=NAVY, accent=GOLD):
    """items: list of (big, small, source) tuples (HTML allowed)"""
    big_style = ParagraphStyle(
        "abig", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=24, leading=26,
        textColor=accent, alignment=TA_CENTER)
    small_style = ParagraphStyle(
        "asmall", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=9, leading=12,
        textColor=colors.white, alignment=TA_CENTER, spaceBefore=3)
    src_style = ParagraphStyle(
        "asrc", parent=styles["Normal"],
        fontName="Helvetica", fontSize=7.5, leading=10,
        textColor=accent, alignment=TA_CENTER, spaceBefore=4)
    n = len(items)
    cell_w = CONTENT_W / n
    cell_tbls = []
    for big, small, src in items:
        rows = [
            [Paragraph(big, big_style)],
            [Paragraph(small, small_style)],
            [Paragraph(src, src_style)],
        ]
        t = Table(rows, colWidths=[cell_w])
        t.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        cell_tbls.append(t)
    row_tbl = Table([cell_tbls], colWidths=[cell_w] * n)
    row_tbl.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    kicker = Paragraph(
        "RANKED &nbsp;&middot;&nbsp; RECOGNIZED &nbsp;&middot;&nbsp; AWARDED",
        ParagraphStyle("akick", parent=style_section_kicker,
                       textColor=accent, alignment=TA_CENTER, fontSize=8))
    outer = Table([[kicker], [row_tbl]], colWidths=[CONTENT_W])
    outer.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (0, 0), 12),
        ("BOTTOMPADDING", (0, 0), (0, 0), 4),
        ("TOPPADDING", (0, 1), (-1, 1), 2),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 14),
        ("LINEABOVE", (0, 0), (-1, 0), 1.2, accent),
        ("LINEBELOW", (0, -1), (-1, -1), 1.2, accent),
    ]))
    return outer


# =====================================================
# PAGES 5–7 — SAMPLE JOURNEYS (Premium + Luxury)
# =====================================================

# Day-label / title / body styles (reused across all journey pages)
day_label_style = ParagraphStyle(
    "dlabel", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=10, leading=12,
    textColor=GOLD, alignment=TA_LEFT)
day_title_style = ParagraphStyle(
    "dtitle", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=11, leading=14,
    textColor=NAVY, alignment=TA_LEFT, spaceAfter=2)
day_body_style = ParagraphStyle(
    "dbody", parent=styles["Normal"],
    fontName="Helvetica", fontSize=9.5, leading=13,
    textColor=INK, alignment=TA_LEFT)


def journey_timeline(days, content_w=CONTENT_W, label_w=24 * mm):
    rows = []
    for day, title, body in days:
        label_cell = Paragraph(day, day_label_style)
        content_cell = Table([
            [Paragraph(title, day_title_style)],
            [Paragraph(body, day_body_style)],
        ], colWidths=[content_w - label_w - 4 * mm])
        content_cell.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        rows.append([label_cell, content_cell])
    tbl = Table(rows, colWidths=[label_w, content_w - label_w])
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBEFORE", (1, 0), (1, -1), 0.8, GOLD),
        ("LEFTPADDING", (1, 0), (1, -1), 12),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, LIGHTL),
    ]))
    return tbl


def flex_note():
    return Paragraph(
        "<i>A reference, not a contract. Every trip is shaped around weather, "
        "tides, tee times, and your energy &mdash; move any day around freely.</i>",
        ParagraphStyle("flex", parent=style_body,
                       fontSize=10, leading=14, textColor=GREY,
                       spaceAfter=10))


# ----- PAGE 5 — PREMIUM SAMPLE JOURNEY -----
story.append(Paragraph("SAMPLE JOURNEY &middot; PREMIUM", style_section_kicker))
story.append(Paragraph("7 nights, 2 cities, 3 surfs, 3 rounds.", style_h1))
story.append(hr())
story.append(flex_note())

premium_days = [
    ("DAY 1", "ARRIVAL &mdash; Wanning",
     "Private Premium Car pickup from Sanya or Haikou. Check in to the "
     "<b>Ocean &amp; Pool View Room</b> at the Wave Pool Resort. "
     "Casual dinner on site."),
    ("DAY 2", "PERFECTSWELL &middot; SESSION 1",
     "Morning surf at PerfectSwell&reg; Hainan &mdash; Asia&rsquo;s only "
     "Kelly Slater-tech wave pool. Photo coverage during your session. "
     "Free afternoon."),
    ("DAY 3", "GOLF &middot; THE DUNES (ROUND 1)",
     "Private charter to <b>The Dunes at Shenzhou Peninsula</b> "
     "(~30 min). 18 holes at China&rsquo;s #2 course &mdash; Tom Weiskopf "
     "links design. Caddy included."),
    ("DAY 4", "PERFECTSWELL &middot; SESSION 2",
     "Second surf session. Photo coverage. Free afternoon &mdash; "
     "beach, pool, recovery."),
    ("DAY 5", "GOLF &middot; THE DUNES (ROUND 2)",
     "Private charter back to The Dunes. Second look at the course, "
     "this time with reads on wind and greens. Caddy included."),
    ("DAY 6", "FINAL SURF &mdash; TRANSFER TO HAIKOU",
     "Morning PerfectSwell&reg; session #3. Afternoon charter to Haikou "
     "(~2 hrs). Check in to <b>Deluxe Golf Ocean View</b> at the "
     "Ritz-Carlton Haikou at Mission Hills."),
    ("DAY 7", "GOLF &middot; MISSION HILLS BLACKSTONE",
     "Round 3 at <b>Mission Hills Blackstone</b> &mdash; #1 in China, "
     "World Top 100, the Tiger Woods &times; Rory McIlroy venue. "
     "Volcanic lava-rock terrain unlike anywhere else in Asia."),
    ("DAY 8", "HAIKOU CITY TOUR &mdash; DEPARTURE",
     "Morning city tour with English-speaking guide: <b>Qilou Old "
     "Street</b>, Haikou&rsquo;s historic Southeast-Asian-influenced "
     "arcaded shopping district. Sedan transfer to Haikou Meilan Intl."),
]
story.append(journey_timeline(premium_days))

story.append(PageBreak())

# ----- PAGE 6 — LUXURY SAMPLE JOURNEY · PART 1 (Wanning leg) -----
story.append(Paragraph("SAMPLE JOURNEY &middot; LUXURY",
                       style_section_kicker))
story.append(Paragraph("11 nights, 3 cities &mdash; the Wanning leg.",
                       style_h1))
story.append(hr())
story.append(flex_note())

luxury_days_p1 = [
    ("DAY 1", "ARRIVAL &mdash; Wanning",
     "Private Executive Van pickup from Sanya or Haikou. Check in to the "
     "<b>Owner&rsquo;s Suite</b> at the Wave Pool Resort &mdash; the "
     "top-tier accommodation inside the surf complex."),
    ("DAY 2", "PERFECTSWELL + DRONE",
     "Morning PerfectSwell&reg; session #1 with <b>premium board "
     "rental</b> &mdash; pick the board that matches the day&rsquo;s "
     "setting. Drone photography session in the afternoon."),
    ("DAY 3", "PERFECTSWELL + COVERAGE",
     "PerfectSwell&reg; session #2 with drone coverage. Free afternoon "
     "&mdash; or upgrade to a <b>private pool buyout</b> "
     "(see add-ons)."),
    ("DAY 4", "GOLF &middot; THE DUNES",
     "Private charter to <b>The Dunes at Shenzhou Peninsula</b>. "
     "18 holes at China&rsquo;s #2 course &mdash; coastal links, "
     "Tom Weiskopf, sea breeze. Caddy included."),
    ("DAY 5", "FINAL SURF &mdash; TRANSFER TO SANYA",
     "Morning PerfectSwell&reg; session #3 &mdash; last waves before "
     "heading south. Afternoon charter Wanning &rarr; Sanya (~3 hrs "
     "coastal highway). Check in to <b>Deluxe Ocean View Room at "
     "Rosewood Sanya</b> on Haitang Bay."),
]
story.append(journey_timeline(luxury_days_p1))

story.append(PageBreak())

# ----- PAGE 7 — LUXURY SAMPLE JOURNEY · PART 2 (Sanya + Haikou) -----
story.append(Paragraph("SAMPLE JOURNEY &middot; LUXURY &middot; CONTINUED",
                       style_section_kicker))
story.append(Paragraph("The Sanya &amp; Haikou legs.", style_h1))
story.append(hr())

luxury_days_p2 = [
    ("DAY 6", "SANYA &middot; PRIVATE YACHT",
     "Full-day <b>private yacht charter</b> out of Sanya Bay or Yalong "
     "Bay. Cruise, swim, paddle, lunch on board. From the water you "
     "can see the <b>108-metre Nanshan Guanyin</b> &mdash; the tallest "
     "statue of Guanyin in the world, rising over the South China Sea. "
     "Drone coverage of the yacht and coastline."),
    ("DAY 7", "CULTURE DAY &middot; ARECA MANOR + NIGHT MARKET",
     "<b>Areca Manor</b> &mdash; the first national 5A "
     "cultural park of its kind in China, preserving Li and Miao "
     "minority traditions. The Li nationality&rsquo;s spinning, "
     "weaving, dyeing, and embroidery techniques are on UNESCO&rsquo;s "
     "urgent-protection list. Evening: <b>Sanya night market</b> "
     "&mdash; tropical fruit, fresh seafood by the kilo, Hainanese "
     "street food."),
    ("DAY 8", "GOLF &middot; LU HUI TOU",
     "Private charter to <b>Lu Hui Tou Golf Club</b>. 18 holes facing "
     "the South China Sea on the Lu Hui Tou peninsula &mdash; "
     "Nelson &amp; Haworth design, 64 bunkers, seashore paspalum "
     "greens. Caddy included."),
    ("DAY 9", "SANYA &middot; FREE DAY",
     "Rest day. Beach, spa, pool &mdash; or arrange an add-on "
     "(additional yacht day, scuba, hot springs, spa treatments)."),
    ("DAY 10", "SANYA &rarr; HAIKOU",
     "Private charter Sanya &rarr; Haikou (~3 hrs). Check in to the "
     "<b>Golf Suite at the Ritz-Carlton Haikou</b> at Mission Hills "
     "&mdash; 100+ sqm, 360&deg; course panorama."),
    ("DAY 11", "GOLF &middot; MISSION HILLS BLACKSTONE",
     "Round 3 at <b>Mission Hills Blackstone</b> &mdash; #1 in China, "
     "World Top 100, the Tiger Woods &times; Rory McIlroy venue. "
     "Evening photo session at the resort."),
    ("DAY 12", "HAIKOU CITY TOUR &mdash; DEPARTURE",
     "Morning tour with English-speaking guide: <b>Qilou Old Street</b>, "
     "Haikou&rsquo;s historic arcaded district. "
     "Executive Van transfer to Haikou Meilan Intl."),
]
story.append(journey_timeline(luxury_days_p2))

story.append(PageBreak())

# =====================================================
# PAGES 6–7 — THE GOLF (MISSION HILLS HAIKOU — BLACKSTONE)
# =====================================================
# --- Page 5: title + AWARDS + brief lead + small designer body + hero ---
story.append(Paragraph("THE GOLF &middot; COURSE I", style_section_kicker))
story.append(Paragraph("Mission Hills Haikou &mdash; Blackstone Course", style_h1))
story.append(hr())

# Awards block — the focus
story.append(awards_block([
    ("#1", "Ranked Course in China", "Asian Golf Monthly"),
    ("BEST", "New Course in Asia", "GOLF Magazine"),
    ("WORLD<br/>TOP 100", "World&rsquo;s Greatest Courses", "Golf Digest"),
]))
story.append(Spacer(1, 10))

# Concise lead: name-drops Tiger & Rory, no date
story.append(Paragraph(
    "Where <b>Tiger Woods</b> and <b>Rory McIlroy</b> have gone head-to-head. "
    "A course built for the world&rsquo;s best.",
    style_lead))

# Designer / technical info, smaller
story.append(Paragraph(
    "Schmidt-Curley design &middot; 350 acres of black volcanic lava rock "
    "&middot; 7,800+ yards from the championship tees &middot; no rough, "
    "wild bunker edges, jungle backdrops.",
    style_small))

story.append(Spacer(1, 8))

# Hero at full CONTENT_W (matches awards block width above)
story.append(sized_image(os.path.join(MH_CROP, "IMG_5950 3.jpg"),
                         width=CONTENT_W))

story.append(PageBreak())

# --- Page 6: Mission Hills gallery (3:2 cropped photos in clean grid) ---
story.append(Paragraph(
    "THE GOLF &middot; COURSE I &middot; THE GALLERY", style_section_kicker))
story.append(Paragraph("Like nowhere else in golf.", style_h1))
story.append(hr())

story.append(Paragraph(
    "Six holes from Blackstone &mdash; wild bunker edges, lava-rock waste "
    "areas, and a landscape that simply does not look or play like "
    "anywhere else.",
    style_lead))

story.append(Spacer(1, 8))

# Uniform 3:2 grid: 3 rows of 2 images
story.append(image_grid([
    os.path.join(MH_CROP, "IMG_5957 3.jpg"),
    os.path.join(MH_CROP, "IMG_5955.jpg"),
], cols=2, total_width=CONTENT_W, gutter=4))
story.append(Spacer(1, 4))
story.append(image_grid([
    os.path.join(MH_CROP, "IMG_5953.jpg"),
    os.path.join(MH_CROP, "IMG_5954.jpg"),
], cols=2, total_width=CONTENT_W, gutter=4))
story.append(Spacer(1, 4))
story.append(image_grid([
    os.path.join(MH_CROP, "IMG_5956 3.jpg"),
    os.path.join(MH_CROP, "IMG_5952 3.jpg"),
], cols=2, total_width=CONTENT_W, gutter=4))

story.append(PageBreak())

# =====================================================
# PAGES 7–8 — THE GOLF (SHENZHOU PENINSULA — THE DUNES)
# =====================================================
# --- Page 7: title + AWARDS + brief lead + designer body + hero ---
story.append(Paragraph("THE GOLF &middot; COURSE II", style_section_kicker))
story.append(Paragraph(
    "The Dunes at Shenzhou Peninsula", style_h1))
story.append(hr())

story.append(awards_block([
    ("#2", "Ranked Course in China", "Golf Digest, 2022"),
    ("TOP 10", "Best Courses in Asia", "Forbes"),
    ("BEST", "New International Course", "U.S. Golf Magazine"),
]))
story.append(Spacer(1, 10))

# Brief lead
story.append(Paragraph(
    "Asia&rsquo;s true seaside links. Ocean fairways. Towering dunes. "
    "The wind off the South China Sea making every club selection a "
    "real decision.",
    style_lead))

# Designer info small
story.append(Paragraph(
    "Designed by major-winner <b>Tom Weiskopf</b> &middot; 36 holes routed "
    "through natural sandhills along Hainan&rsquo;s untouched east coast "
    "&middot; East and West courses both touch the bays and beaches "
    "directly &middot; twenty minutes from your base at the Wave Pool.",
    style_small))

story.append(Spacer(1, 8))

# Hero centered — full width
story.append(sized_image(
    os.path.join(ROOT, "神州半岛", "IMG_6996.jpg"),
    width=CONTENT_W))

story.append(PageBreak())

# --- Page 8: Shenzhou gallery ---
story.append(Paragraph(
    "THE GOLF &middot; COURSE II &middot; THE GALLERY", style_section_kicker))
story.append(Paragraph("On the peninsula.", style_h1))
story.append(hr())

story.append(Paragraph(
    "From elevated tee boxes looking out across the bay, to fairways "
    "bordered by native dunes and beach grass.",
    style_lead))

story.append(Spacer(1, 8))

# Two widescreen landscapes side-by-side
story.append(image_grid([
    os.path.join(ROOT, "神州半岛", "24EDDBE1-764E-4F6B-BEF4-306BB565F438.jpg"),
    os.path.join(ROOT, "神州半岛", "7820C2B6-CB3E-4318-82E3-E5DA2AE0BD56.jpg"),
], cols=2, total_width=CONTENT_W, gutter=4))
story.append(Spacer(1, 6))

# Lower row: 1 wide landscape + 1 portrait
sz_low_w = (CONTENT_W - 6) * 0.62
sz_low_p_w = (CONTENT_W - 6) * 0.38
sz_low = Table([[
    sized_image(os.path.join(ROOT, "神州半岛", "IMG_6996 2.JPG"),
                width=sz_low_w),
    "",
    sized_image(os.path.join(ROOT, "神州半岛", "IMG_6993.jpg"),
                width=sz_low_p_w),
]], colWidths=[sz_low_w, 6, sz_low_p_w])
sz_low.setStyle(TableStyle([
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
]))
story.append(sz_low)

story.append(PageBreak())

# =====================================================
# PAGE 12 — THE GOLF · COURSE III (LU HUI TOU, SANYA — LUXURY ONLY)
# =====================================================
story.append(Paragraph("THE GOLF &middot; COURSE III &middot; LUXURY",
                       style_section_kicker))
story.append(Paragraph(
    "Lu Hui Tou Golf Club &mdash; Sanya", style_h1))
story.append(hr())

story.append(awards_block([
    ("SEA-<br/>FACING", "South China Sea fairways",
     "Lu Hui Tou Peninsula"),
    ("64", "Sweeping bunkers",
     "Nelson &amp; Haworth design"),
    ("TROPICAL<br/>LINKS", "Seashore paspalum greens",
     "Designed for the sub-tropics"),
]))
story.append(Spacer(1, 10))

story.append(Paragraph(
    "Sanya&rsquo;s most dramatic golf address &mdash; a parkland-meets-"
    "links course on the Lu Hui Tou peninsula, with the South China Sea "
    "as your constant backdrop.",
    style_lead))

story.append(Paragraph(
    "Designed by <b>Robin Nelson &amp; Neil Haworth</b> "
    "(Nelson &amp; Haworth) &middot; opened 2009 &middot; 18 holes, "
    "par 72 &middot; 1.7 sq km across the southern tip of the peninsula "
    "&middot; coconut-palm-lined fairways, large greens guarded by "
    "64 sweeping bunkers, multiple water hazards, and salt-tolerant "
    "seashore paspalum turf that thrives in the tropics.",
    style_small))

story.append(Spacer(1, 8))

# Placeholder image (using a Shenzhou shot — Lu Hui Tou photos TBD)
story.append(sized_image(
    os.path.join(ROOT, "神州半岛", "IMG_6996.jpg"),
    width=CONTENT_W))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "<i>Course photography pending &mdash; representative coastal Hainan "
    "fairway shown above.</i>",
    style_caption))

story.append(PageBreak())

# =====================================================
# PAGE 13 — THE STAY (RITZ-CARLTON HAIKOU)
# =====================================================
story.append(Paragraph("THE STAY", style_section_kicker))
story.append(Paragraph(
    "The Ritz-Carlton, Haikou &mdash; right above the course",
    style_h1))
story.append(hr())

story.append(Paragraph(
    "The Ritz-Carlton, Haikou is the first Ritz-Carlton golf resort in "
    "China &mdash; and it is built <i>inside</i> the Mission Hills "
    "complex itself, perched directly above the courses. Every guest "
    "room looks out across the championship layouts; the rooftop bar "
    "watches the sun set over the fairways. From your room, you can see "
    "the course you&rsquo;ll play in the morning.",
    style_lead))

story.append(Paragraph(
    "For the Luxury package, we book the <b>Golf Suite</b> &mdash; "
    "more than <b>100 square meters</b> (over 1,000 square feet) of "
    "private space, with a 360-degree panorama of the Blackstone Course, "
    "a generous living area, dressing room, and a marble bathroom with "
    "deep soaking tub. It is one of the most spacious suites you will "
    "find on the island.",
    style_body_justify))

# Ritz image row
story.append(Spacer(1, 6))
story.append(image_grid([
    os.path.join(ROOT, "ritz", "rz-hakrz-golf-view-suite-bedroom-42284-Classic-Hor.jpeg"),
    os.path.join(ROOT, "ritz", "rz-hakrz-deluxe-golf-view-balcony-13103-Classic-Hor.jpeg"),
], cols=2, total_width=CONTENT_W, gutter=4, row_height=44 * mm))
story.append(Spacer(1, 4))
story.append(image_grid([
    os.path.join(ROOT, "ritz", "hakrz-club-0006-hor-wide.jpg"),
    os.path.join(ROOT, "ritz", "rz-hakrz-golf-view-suite-bathroom-35899-Classic-Hor.jpeg"),
    os.path.join(ROOT, "ritz", "IMG_7017.jpg"),
], cols=3, total_width=CONTENT_W, gutter=4, row_height=30 * mm))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "The Ritz-Carlton, Haikou &mdash; Golf Suite bedroom, golf-view balcony, "
    "Club Lounge, marble bathroom, course views.", style_caption))

story.append(PageBreak())

# =====================================================
# PAGE 10 — WAVE POOL RESORT (Ocean & Pool + Owner's Suite, ALL photos)
# =====================================================
story.append(Paragraph("THE STAY &middot; WANNING", style_section_kicker))
story.append(Paragraph("The Wave Pool Resort", style_h1))
story.append(hr())

story.append(Paragraph(
    "Your base for surf days. The Wave Pool Resort sits steps from the "
    "PerfectSwell&reg; pool itself &mdash; the same American Wave Machines "
    "technology behind Waco and Praia da Grama. You can be in the water "
    "five minutes after breakfast.",
    style_lead))

# -- Ocean & Pool View Room block (PREMIUM)
def room_header(label, color, w):
    head = Table([[Paragraph(
        f'<font color="white"><b>{label}</b></font>',
        ParagraphStyle("hh", parent=style_tag, alignment=TA_LEFT))]],
        colWidths=[w])
    head.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return head

story.append(Spacer(1, 6))

# Two side-by-side columns, each with header + 1 lead + 2-up sub-row
ocean_paths = [os.path.join(ROOT, "wavepool_hotel",
                            "ocean & pool view room", f) for f in [
    "bigpic.jpeg",                                          # lead
    "655B29D8-2BF7-4581-A96A-FC2D6CFACF14 2 Large.jpeg",   # thumb
    "main-hotel-entrance-01.jpg",                          # thumb
    "481DF200-3322-4BF2-BF7B-A0BABA02D5F2 Large.jpeg",     # thumb
]]
owner_paths = [os.path.join(ROOT, "wavepool_hotel",
                            "Owner's suite", f) for f in [
    "bigpic.jpeg",                                          # lead
    "main-hotel-room-05.jpg",                              # thumb
    "CE9FCB19-AFF9-491A-A599-5D9E7168380B Large.jpeg",     # thumb
    "7A36E8BD-C170-4B9B-A14C-4EA4D2C79167 Large.jpeg",     # thumb
]]

col_w = (CONTENT_W - 12) / 2  # half-width with gutter

def wave_column(label, color, paths, w):
    # Header
    head = Table([[Paragraph(
        f'<font color="white"><b>{label}</b></font>',
        ParagraphStyle("wh", parent=style_tag, alignment=TA_LEFT, fontSize=8.5))]],
        colWidths=[w])
    head.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    # Lead at full column width
    lead = sized_image(paths[0], width=w)
    # 3-up sub-row across column width (each cell ~w/3 × 1/1.5 tall)
    sub_w = (w - 6) / 3
    sub = Table([[sized_image(p, width=sub_w) for p in paths[1:4]]],
                colWidths=[sub_w] * 3, hAlign='LEFT')
    sub.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-2, -1), 3),
        ("RIGHTPADDING", (-1, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    column = Table([[head], [lead], [Spacer(1, 4)], [sub]],
                   colWidths=[w])
    column.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 1), (-1, 1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return column

left = wave_column("OCEAN &amp; POOL VIEW ROOM &nbsp;&middot;&nbsp; PREMIUM",
                   GREEN, ocean_paths, col_w)
right = wave_column("OWNER&rsquo;S SUITE &nbsp;&middot;&nbsp; LUXURY",
                    CORAL, owner_paths, col_w)
twocol = Table([[left, "", right]],
               colWidths=[col_w, 12, col_w])
twocol.setStyle(TableStyle([
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
]))
story.append(twocol)

story.append(PageBreak())

# =====================================================
# PAGE 16 — ROSEWOOD SANYA (LUXURY ONLY)
# =====================================================
story.append(Paragraph("THE STAY &middot; SANYA &middot; LUXURY",
                       style_section_kicker))
story.append(Paragraph(
    "Rosewood Sanya &mdash; Haitang Bay.", style_h1))
story.append(hr())

story.append(awards_block([
    ("FORBES", "Four-Star Spa",
     "Forbes Travel Guide"),
    ("FORBES", "Best Luxury<br/>Guestroom Design",
     "Forbes Travel Guide"),
    ("FIRST", "Rosewood Resort<br/>in mainland China",
     "Opened August 2017"),
]))
story.append(Spacer(1, 10))

story.append(Paragraph(
    "Five nights on Haitang Bay &mdash; a private stretch of white sand "
    "on Sanya&rsquo;s most exclusive coastline. <b>Rosewood Sanya</b> "
    "is one of the finest luxury resorts in China.",
    style_lead))

story.append(Paragraph(
    "241 panoramic sea-view rooms &middot; 5 restaurants &amp; lounges "
    "&middot; Forbes-rated <b>Asaya Spa</b> &middot; direct beachfront "
    "access &middot; the resort&rsquo;s signature Chop House grill "
    "named <i>Outstanding Grill of the Year</i> by the Food &amp; Drink "
    "Awards. For Luxury guests we book a <b>Deluxe Ocean View Room</b> "
    "facing the South China Sea.",
    style_small))

story.append(Spacer(1, 8))

# Hero image — slightly less than full width so strip below fits
rw_hero = sized_image(
    os.path.join(ROOT, "rosewoods", "IMG_7067.JPG"),
    width=CONTENT_W * 0.75)
rw_hero_tbl = Table([[rw_hero]], colWidths=[CONTENT_W])
rw_hero_tbl.setStyle(TableStyle([
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
]))
story.append(rw_hero_tbl)
story.append(Spacer(1, 4))

# Image strip with remaining Rosewood photos
story.append(image_grid([
    os.path.join(ROOT, "rosewoods", "IMG_7068.JPG"),
    os.path.join(ROOT, "rosewoods", "IMG_7069.jpg"),
    os.path.join(ROOT, "rosewoods", "IMG_7070.jpg"),
    os.path.join(ROOT, "rosewoods", "IMG_7071.jpg"),
], cols=4, total_width=CONTENT_W, gutter=4))

story.append(PageBreak())

# =====================================================
# PAGES 17–19 — MORE THAN GOLF AND SURF (Sanya Experiences, 3 pages)
# =====================================================

# ----- PAGE 17 — ON THE WATER (Yacht + Nanshan combined) -----
story.append(Paragraph("MORE THAN GOLF AND SURF &middot; LUXURY",
                       style_section_kicker))
story.append(Paragraph("On the water.", style_h1))
story.append(hr())

story.append(Paragraph(
    "The Luxury journey opens four full days in Sanya &mdash; on the "
    "South China Sea, inside temples a thousand years old, deep in "
    "the cultures of Hainan&rsquo;s original peoples, and out among the "
    "seafood stalls at night.",
    style_lead))

# --- Yacht hero strip — sized smaller so Nanshan section fits below ---
story.append(Spacer(1, 6))
y_hero = sized_image(
    os.path.join(ROOT, "yacht", "d8d57e2240a16b138296a87ace1eb966.jpg"),
    width=CONTENT_W * 0.68)
y_hero_tbl = Table([[y_hero]], colWidths=[CONTENT_W])
y_hero_tbl.setStyle(TableStyle([
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
]))
story.append(y_hero_tbl)
story.append(Spacer(1, 4))

# Yacht caption / body
story.append(Paragraph(
    "<b>Private yacht charter</b> &middot; <font color='#C9A86A'>"
    "SANYA BAY &middot; YALONG BAY &middot; FULL DAY</font><br/>"
    "Your own boat with an English-speaking guide. Cruise, swim, paddle, "
    "lunch on board. From the water you can look back at the "
    "<b>108-metre Nanshan Guanyin</b> &mdash; the world&rsquo;s tallest "
    "statue of the goddess of mercy, rising directly out of the South "
    "China Sea. Drone coverage included.",
    ParagraphStyle("yacht_body", parent=style_body,
                   fontSize=9.5, leading=13, spaceAfter=10)))

# --- Nanshan section ---
story.append(Paragraph("NANSHAN TEMPLE &amp; GUANYIN",
                       ParagraphStyle("nsh", parent=style_section_kicker,
                                      fontSize=9, textColor=GOLD,
                                      spaceBefore=4)))
story.append(Paragraph("Taller than the Statue of Liberty.",
                       ParagraphStyle("nsh_h", parent=style_h2,
                                      fontSize=18, leading=22,
                                      spaceBefore=2, spaceAfter=6)))
story.append(Paragraph(
    "108 metres tall, 2,600 tons, six years to build, consecrated 2005. "
    "Three faces, one inland, two facing the South China Sea &mdash; "
    "representing protection over China and the world. The temple "
    "complex around it covers 50 square kilometres of coastline.",
    ParagraphStyle("nsh_b", parent=style_body,
                   fontSize=9.5, leading=13, spaceAfter=8)))

# 4 Nanshan portraits side-by-side
story.append(image_grid([
    os.path.join(ROOT, "南山寺", "IMG_7046.jpg"),
    os.path.join(ROOT, "南山寺", "IMG_7051.jpg"),
    os.path.join(ROOT, "南山寺", "IMG_7052.jpg"),
    os.path.join(ROOT, "南山寺", "IMG_7053.jpg"),
], cols=4, total_width=CONTENT_W, gutter=4))

story.append(PageBreak())

# ----- PAGE 19 — INSIDE HAINAN (Areca Manor — Li & Miao culture) -----
story.append(Paragraph("MORE THAN GOLF AND SURF &middot; SANYA",
                       style_section_kicker))
story.append(Paragraph("Inside Hainan&rsquo;s first peoples.", style_h1))
story.append(hr())

story.append(awards_block([
    ("5A", "National Scenic Site",
     "China&rsquo;s highest cultural tier"),
    ("UNESCO", "Urgent-Protection Heritage",
     "Li weaving, dyeing &amp; embroidery"),
    ("333", "Hectares of betel-nut forest",
     "Original Li &amp; Miao villages"),
]))
story.append(Spacer(1, 10))

story.append(Paragraph(
    "<b>Areca Manor</b> &mdash; China&rsquo;s first national 5A "
    "cultural heritage park dedicated to an ethnic minority &mdash; "
    "preserves the original Li and Miao villages that have lived on "
    "this island for thousands of years.",
    style_lead))

story.append(Paragraph(
    "The Li nationality&rsquo;s spinning, weaving, dyeing and embroidery "
    "techniques are on UNESCO&rsquo;s urgent-protection list of "
    "intangible cultural heritage &mdash; you watch elders work the "
    "looms by hand. Inside the park: live song-and-dance performance, "
    "the dragon-quilt museum, traditional fire-making, archery, and "
    "the betel-nut tree groves the place is named for.",
    style_body))

story.append(Spacer(1, 8))

# 4 portraits in a row
story.append(image_grid([
    os.path.join(ROOT, "槟榔谷", "li-elder-portrait-01.jpg"),
    os.path.join(ROOT, "槟榔谷", "IMG_5937.jpg"),
    os.path.join(ROOT, "槟榔谷", "IMG_5940 3.jpg"),
    os.path.join(ROOT, "槟榔谷", "IMG_7108.jpg"),
], cols=4, total_width=CONTENT_W, gutter=4))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "Li elder &middot; traditional dress &middot; dance performance "
    "&middot; village life inside the park.",
    style_caption))

story.append(PageBreak())

# ----- PAGE 20 — AFTER DARK (Sanya Night Market) -----
story.append(Paragraph("MORE THAN GOLF AND SURF &middot; SANYA",
                       style_section_kicker))
story.append(Paragraph("After dark &mdash; the night market.", style_h1))
story.append(hr())

story.append(Paragraph(
    "Every Sanya local eats here at least once a week. The night market "
    "(<b>Di Yi Shi Chang</b>) is the antidote to the resort: "
    "loud, fluorescent, hot, alive.",
    style_lead))

story.append(Paragraph(
    "Tropical fruit by the kilo (passion fruit, mangosteen, custard "
    "apple, durian for the brave). Fresh seafood &mdash; you point at "
    "what swims, they wok it three ways. Hainanese street food the "
    "locals eat: coconut rice, suckling pig, Wenchang chicken, beef "
    "noodle soup. Best done with our English-speaking guide so you "
    "order what&rsquo;s good rather than what&rsquo;s easy.",
    style_body))

story.append(Spacer(1, 8))

# 3 photos in a row
story.append(image_grid([
    os.path.join(ROOT, "夜市", "IMG_7097.JPG"),
    os.path.join(ROOT, "夜市", "IMG_7099.jpg"),
    os.path.join(ROOT, "夜市", "IMG_7105.jpg"),
], cols=3, total_width=CONTENT_W, gutter=4))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "Stall life at Di Yi Shi Chang &mdash; tropical fruit, fresh "
    "seafood, Hainanese street food.",
    style_caption))

story.append(PageBreak())

# =====================================================
# PAGE 18 — ADD-ONS & CUSTOMIZE
# =====================================================
story.append(Paragraph("ADD-ONS &middot; CUSTOMIZE", style_section_kicker))
story.append(Paragraph("Build your trip up.", style_h1))
story.append(hr())

story.append(Paragraph(
    "Every trip is built around what you actually want. The packages above "
    "are the spine &mdash; here are the most-requested upgrades. Add any "
    "of them at booking or while you&rsquo;re here.",
    style_lead))

story.append(Spacer(1, 8))

# Featured add-on: Private Pool Buyout (highlighted)
buyout_title = Paragraph(
    "Private Pool Buyout &mdash; 1 hour, Master Wave",
    ParagraphStyle("buy_t", parent=styles["Normal"],
                   fontName="Helvetica-Bold", fontSize=16, leading=20,
                   textColor=colors.white))
buyout_kicker = Paragraph(
    "FEATURED ADD-ON &middot; LUXURY",
    ParagraphStyle("buy_k", parent=style_section_kicker,
                   textColor=GOLD, fontSize=8))
buyout_body = Paragraph(
    "The entire PerfectSwell&reg; pool to yourselves &mdash; just you, "
    "your crew, your choice of every wave. Master-wave settings, "
    "maximum quality wave count, no rotation. Slot into Day 2 or Day 3 "
    "in Wanning.",
    ParagraphStyle("buy_b", parent=styles["Normal"],
                   fontName="Helvetica", fontSize=10.5, leading=15,
                   textColor=colors.white, alignment=TA_LEFT,
                   spaceBefore=4))

buyout_box = Table([
    [buyout_kicker],
    [Spacer(1, 4)],
    [buyout_title],
    [Spacer(1, 6)],
    [buyout_body],
], colWidths=[CONTENT_W])
buyout_box.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), NAVY),
    ("LEFTPADDING", (0, 0), (-1, -1), 22),
    ("RIGHTPADDING", (0, 0), (-1, -1), 22),
    ("TOPPADDING", (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (0, 0), 18),
    ("BOTTOMPADDING", (0, -1), (-1, -1), 18),
    ("LINEABOVE", (0, 0), (-1, 0), 1.5, GOLD),
    ("LINEBELOW", (0, -1), (-1, -1), 1.5, GOLD),
]))
story.append(buyout_box)
story.append(Spacer(1, 14))

# Two-column list of other add-ons
other_addons_left = [
    "<b>Additional yacht day</b> (Sanya)",
    "<b>Scuba diving</b> (Sanya, Yalong Bay reefs)",
    "<b>Hot springs day trip</b> (Baoting)",
    "<b>Asaya Spa</b> treatments (Rosewood Sanya)",
]
other_addons_right = [
    "<b>Additional PerfectSwell&reg; sessions</b>",
    "<b>Additional golf rounds</b> (any Hainan course)",
    "<b>Room upgrade</b> to Rosewood Sanya suite",
    "<b>Drone &amp; video coverage</b> (Premium upgrade)",
]

def addons_col(items, w):
    rows = []
    for it in items:
        rows.append([Paragraph(
            f"<font color='#C9A86A'>+</font>&nbsp;&nbsp;{it}",
            style_body)])
    t = Table(rows, colWidths=[w])
    t.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t

col_w_ao = (CONTENT_W - 16) / 2
left_ao = addons_col(other_addons_left, col_w_ao)
right_ao = addons_col(other_addons_right, col_w_ao)

addons_tbl = Table([[left_ao, "", right_ao]],
                   colWidths=[col_w_ao, 16, col_w_ao])
addons_tbl.setStyle(TableStyle([
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
]))
story.append(addons_tbl)

story.append(Spacer(1, 12))
story.append(Paragraph(
    "<i>All add-ons quoted on request. We'll fit them into your week.</i>",
    ParagraphStyle("anote", parent=style_small, alignment=TA_CENTER,
                   textColor=GREY)))

story.append(PageBreak())

# =====================================================
# CLOSING PAGE — SHANQIN BAY
# =====================================================
story.append(Paragraph("BEYOND THE PACKAGE", style_section_kicker))
story.append(Paragraph("More golf, your way.", style_h1))
story.append(hr())

story.append(Paragraph(
    "Hainan has more than <b>40 golf courses</b>. The two we&rsquo;ve "
    "selected for these packages are, in our view, the best fit for a "
    "surf-and-golf week &mdash; but they are far from your only options. "
    "<b>Additional rounds can be added to either package at any time</b>, "
    "at any course you&rsquo;d like to play. Tell us the courses on your "
    "wish list and we&rsquo;ll build the schedule around them.",
    style_lead))

# --- Shanqin Bay teaser — dramatic full-width hero block ---

# Small kicker
shanqin_kicker = Paragraph(
    "AND ONE MORE THING&hellip;",
    ParagraphStyle("sk_kick", parent=styles["Normal"],
                   fontName="Helvetica-Bold", fontSize=10, leading=12,
                   textColor=GOLD, alignment=TA_LEFT,
                   spaceBefore=0, spaceAfter=0))

# Huge headline
shanqin_head = Paragraph(
    "Shanqin Bay.",
    ParagraphStyle("sk_head", parent=styles["Normal"],
                   fontName="Helvetica-Bold", fontSize=44, leading=48,
                   textColor=colors.white, alignment=TA_LEFT,
                   spaceBefore=2, spaceAfter=2))

# Subhead — strong but smaller
shanqin_sub = Paragraph(
    "The most exclusive golf club in China.<br/>"
    "One of the most exclusive in all of Asia.",
    ParagraphStyle("sk_sub", parent=styles["Normal"],
                   fontName="Helvetica-Bold", fontSize=14, leading=18,
                   textColor=GOLD, alignment=TA_LEFT,
                   spaceBefore=6, spaceAfter=10))

# Body
shanqin_body = Paragraph(
    "Only a very, very few people have ever played there. "
    "Tee times are not bookable in the usual sense &mdash; "
    "they are arranged. Quietly, and only on inquiry.",
    ParagraphStyle("sk_body", parent=styles["Normal"],
                   fontName="Helvetica", fontSize=11, leading=16,
                   textColor=colors.white, alignment=TA_LEFT,
                   spaceBefore=0, spaceAfter=14))

# Call to action — stand-out bar at the bottom
shanqin_cta = Paragraph(
    "&mdash;&nbsp;&nbsp;ASK US PRIVATELY&nbsp;&nbsp;&mdash;",
    ParagraphStyle("sk_cta", parent=styles["Normal"],
                   fontName="Helvetica-Bold", fontSize=13, leading=16,
                   textColor=GOLD, alignment=TA_LEFT,
                   spaceBefore=4, spaceAfter=0))

shanqin_box = Table([
    [shanqin_kicker],
    [Spacer(1, 4)],
    [shanqin_head],
    [Spacer(1, 10)],
    [shanqin_sub],
    [Spacer(1, 10)],
    [shanqin_body],
    [Spacer(1, 6)],
    [shanqin_cta],
], colWidths=[CONTENT_W])
shanqin_box.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), NAVY),
    ("LEFTPADDING", (0, 0), (-1, -1), 26),
    ("RIGHTPADDING", (0, 0), (-1, -1), 26),
    ("TOPPADDING", (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (0, 0), 24),
    ("BOTTOMPADDING", (0, -1), (-1, -1), 24),
    ("LINEABOVE", (0, 0), (-1, 0), 2, GOLD),
    ("LINEBELOW", (0, -1), (-1, -1), 2, GOLD),
]))
story.append(shanqin_box)
story.append(Spacer(1, 16))

# (Closing page intentionally ends with the Shanqin Bay block)

# Build
doc.build(story)
print("Wrote:", OUTPUT_PDF)
print("Size:", os.path.getsize(OUTPUT_PDF), "bytes")
