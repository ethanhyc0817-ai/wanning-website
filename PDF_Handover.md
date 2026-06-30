# Surf & Golf — Hainan Brochure · Handover

A handover document for the `Surf_and_Golf_Hainan_Brochure.pdf` proposal sent to Western clients. Last updated: 2026-05-18.

---

## 1. What this is

An 11-page A4 PDF brochure presenting two private travel packages — **Premium Surf & Golf Escape** and **Ultra Luxury Surf & Golf Escape** — to Western prospects. Designed to be emailed as a self-contained proposal.

**Audience:** Western travelers (US / UK / EU / AU), couples or pairs of friends who both surf and golf. Premium → mid-luxury; Ultra → top-tier with Ritz-Carlton.

**Tone:** Premium travel agency. Confident but not salesy. English-only.

---

## 2. Files

| File | What it is | Path |
|---|---|---|
| **Output PDF** | The deliverable | `/Users/ethanhuang/Documents/Wanning/Surf_and_Golf_Hainan_Brochure.pdf` |
| **Generator script** | Python source that builds the PDF | session outputs `build/make_pdf.py` (not persisted on disk — regenerate from this doc + ChatGPT/Claude if lost) |
| **Image folder** | All photos used | `/Users/ethanhuang/Documents/Wanning/Assets/planner/` |
| **Mission Hills cropped** | Auto-generated 3:2 versions | session outputs `build/mh_cropped/` (regenerated on each build) |

**Tech stack:** Python 3 + ReportLab + Pillow. No external CSS / HTML.

---

## 3. How to regenerate the PDF

If a future Claude session needs to rebuild from scratch, the workflow is:

```bash
# 1) crop Mission Hills images to uniform 3:2 ratio
python3 <<'EOF'
from PIL import Image
import os
src = "/path/to/Wanning/Assets/planner/观澜湖"
dst = "/tmp/mh_cropped"
os.makedirs(dst, exist_ok=True)
TARGET = 1.50
for fn in sorted(os.listdir(src)):
    if fn.startswith('.') or not fn.lower().endswith(('.jpg','.jpeg','.png')):
        continue
    with Image.open(os.path.join(src, fn)) as im:
        w, h = im.size
        r = w/h
        if r > TARGET:
            new_w = int(h * TARGET); left = (w - new_w)//2
            im2 = im.crop((left, 0, left + new_w, h))
        else:
            new_h = int(w / TARGET); top = (h - new_h)//2
            im2 = im.crop((0, top, w, top + new_h))
        im2.save(os.path.join(dst, fn), quality=90)
EOF

# 2) Run make_pdf.py (or have Claude regenerate it from this handover doc)
python3 make_pdf.py
```

---

## 4. Page-by-page structure

| # | Title | Key content |
|---|---|---|
| 1 | **Cover** | Full-bleed cover image (`神州半岛/IMG_cover.JPG`), navy band bottom, "Surf & Golf" title, "A Private Proposal for Two" kicker. **Cover uses cover-fit math (not preserveAspectRatio) so it always fills the page edge-to-edge.** |
| 2 | **The Proposal** | Two side-by-side cards: Premium ($2,200 pp) / Ultra ($3,965 pp). Bottom: 3-image teaser (Mission Hills · Ritz-Carlton lounge · Shenzhou). |
| 3 | **Premium Surf & Golf Escape** | Lead image: `Assets/wavepool/wavepool-use.JPG`. Price block: "FROM $2,200 USD per person · package total $4,400 USD". Included/Not Included two-column. Bottom strip: surfer-action · Shenzhou widescreen · Shenzhou fairway. |
| 4 | **Ultra Luxury Surf & Golf Escape** | Lead image: Ritz-Carlton suite. Price block: "FROM $3,965 USD per person · package total $7,929 USD". Full inclusion table (5 nights Surf Pool Owner's Suite + 2 nights Ritz Golf Suite, 6 golf rounds split 2 Mission Hills / 4 Shenzhou, caddie fees included, 4 photo + 2 drone + 2 recovery). |
| 5 | **Mission Hills Haikou — Blackstone** | Awards block (navy + gold): **#1 in China · BEST New Course in Asia · WORLD TOP 100**. Brief mention of Tiger Woods and Rory McIlroy. Designer info (Schmidt-Curley, 350 acres lava, 7,800+ yds) in small text. Full-width hero image. |
| 6 | **Mission Hills — The Gallery** | 6 of the 3:2-cropped photos in a 2-up × 3-row grid. |
| 7 | **The Dunes at Shenzhou Peninsula** | Awards block: **#2 in China (Golf Digest 2022) · TOP 10 in Asia (Forbes) · BEST New International Course (US Golf Magazine)**. Tom Weiskopf credit in small text. Full-width hero image (IMG_6996). |
| 8 | **Shenzhou — The Gallery** | 2-up widescreen row + 1 landscape + 1 portrait combo. Uses 24EDDBE1, 7820C2B6, IMG_6996 2, IMG_6993. |
| 9 | **The Ritz-Carlton, Haikou** | Hotel description (built inside Mission Hills, 360° course views, Golf Suite = 100+ sqm / 1,000+ sqft). 5 Ritz-Carlton photos in 2+3 grid. |
| 10 | **The Surf Pool Resort** | Two side-by-side columns: left = Ocean & Pool View Room (green header, Premium), right = Owner's Suite (coral header, Ultra Luxury). Each column has `bigpic.jpeg` as lead + 3-up sub-row of thumbs. |
| 11 | **Beyond the Package / Shanqin Bay** | "Hainan has 40+ golf courses · additional rounds anytime, anywhere." Then a large dramatic navy block with gold accents: **Shanqin Bay.** "The most exclusive golf club in China. — ASK US PRIVATELY —" |

---

## 5. Key design decisions

### Pricing: per-person, not total
**Decision:** Lead with "FROM $2,200 per person" / "FROM $3,965 per person" rather than the total package price.
**Why:** Western luxury-travel standard. $4,400 looks scary at a glance; $2,200/pp for a 7-night surf+golf trip reads as a good deal. Per-person framing + "FROM" + total shown small underneath = transparent and digestible.

### Awards-first layout on golf course pages
**Decision:** On both Mission Hills and Shenzhou pages, the **first thing the eye sees below the title** is a big navy block with three columns of awards in large gold text (e.g., **#1 · BEST · WORLD TOP 100**). Designer name, yardage, and history go in small body text below.
**Why:** Western golfers care about course rankings. Putting awards huge + designer credit small establishes credibility instantly.

### Tiger Woods + Rory McIlroy mentioned without date
**Decision:** "Where Tiger Woods and Rory McIlroy have gone head-to-head" — no year given.
**Why:** Their 2013 match keeps the course relevant forever; specifying "2013" makes it feel dated.

### Caddie fees fully included
**Decision:** All caddie fees are listed in INCLUDED (Premium card list + Ultra Luxury inclusion table). Only "personal gratuities" remain in NOT INCLUDED.
**Why:** Removes a common point of friction for Western golfers who aren't used to Chinese caddie pricing conventions.

### Shanqin Bay as mysterious closing teaser
**Decision:** Final page ends with a dramatic full-width navy block ("Shanqin Bay. The most exclusive golf club in China. — ASK US PRIVATELY —"). No further contact info, no NEXT STEPS.
**Why:** Curiosity hook. Prospects who actually want Shanqin Bay will reach out directly. Keeps the mystique that the club itself trades on.

### Mission Hills photo crops to uniform 3:2
**Decision:** All 7 Mission Hills photos are programmatically cropped to a uniform 3:2 (1.50) aspect before being placed in the document.
**Why:** Original photos ranged from 1.45 to 1.82 ratio — looked uneven in the gallery. 3:2 matches the rest of the document's photography (Ritz-Carlton, surf pool hotel rooms are all 3:2).

### Footer email/WhatsApp removed
**Decision:** Page footers show only "Page N" — no `hello@surfchinaco.com · WhatsApp / WeChat available on request` line.
**Why:** Cleaner. Contact happens through whatever channel the prospect was sent the PDF on.

---

## 6. Image management

### Where photos live

```
Assets/planner/
├── 神州半岛/            # Shenzhou Peninsula golf course
│   ├── IMG_cover.JPG          # → used on Page 1 cover
│   ├── 24EDDBE1-...jpg        # widescreen 1.78
│   ├── 7820C2B6-...jpg        # widescreen 1.78
│   ├── IMG_6993.jpg           # portrait
│   ├── IMG_6996.jpg           # → page 7 hero
│   └── IMG_6996 2.JPG         # page 8
├── 观澜湖/              # Mission Hills (Blackstone)
│   └── IMG_5950 3.jpg, etc.   # 7 photos, all cropped to 3:2 at build time
├── ritz/                # Ritz-Carlton Haikou
│   ├── hakrz-suite-0003-hor-wide.jpg     # → page 4 Ultra Luxury lead
│   ├── hakrz-lounge-0013-hor-wide.jpg    # → page 2 teaser middle
│   ├── hakrz-club-0006-hor-wide.jpg
│   ├── rz-hakrz-*-suite-bedroom*.jpeg
│   ├── rz-hakrz-*-suite-bathroom*.jpeg
│   ├── rz-hakrz-deluxe-golf-view-balcony*.jpeg
│   └── IMG_7017.jpg
└── wavepool_hotel/      # Surf Pool Resort accommodation
    ├── ocean & pool view room/
    │   ├── bigpic.jpeg               # → page 10 Premium column lead
    │   ├── 655B29D8-...Large.jpeg    # → page 10 thumb
    │   ├── 481DF200-...Large.jpeg    # → page 10 thumb
    │   └── main-hotel-entrance-01.jpg # → page 10 thumb
    └── Owner's suite/
        ├── bigpic.jpeg               # → page 10 Ultra column lead
        ├── main-hotel-room-05.jpg    # → page 10 thumb
        ├── CE9FCB19-...Large.jpeg    # → page 10 thumb
        └── 7A36E8BD-...Large.jpeg    # → page 10 thumb

Assets/wavepool/             # Surf pool action shots (separate from hotel)
├── wavepool-use.JPG                   # → page 3 Premium lead
└── wavepool-surfer-action-01.jpg      # → page 3 strip thumb
```

### To swap a photo

If a photo gets renamed, replaced, or deleted, find the matching `os.path.join(...)` line in `make_pdf.py` and update the filename. Sizes are handled automatically by `sized_image()` / `image_grid()`.

### Adding new photos

Drop into the relevant folder. If they should appear in the brochure, add a reference in `make_pdf.py`.

---

## 7. Common edits

### Change pricing
- Cover cards (page 2): edit the `price` argument in `package_card(...)` calls.
- Premium detail (page 3): edit `price_block` paragraphs.
- Ultra detail (page 4): edit `ultra_price_block` paragraphs.
- All three places must be kept in sync.

### Change awards on a golf course page
- Mission Hills: edit the `awards_block([...])` call before the Page 5 hero.
- Shenzhou: edit the `awards_block([...])` call before the Page 7 hero.
- Format: `(big_text, small_subtitle, source_attribution)`.

### Change package inclusions
- Premium: edit `prem_included` and `prem_not` lists.
- Ultra Luxury: edit `ultra_table_data` (2D list, each row is `[description, quantity]`).

### Change package totals or per-person derivation
- Currently $2,200 pp × 2 = $4,400 total (Premium)
- Currently $3,965 pp × 2 = $7,930 total — listed as $7,929 (50¢ rounding artifact; acceptable in luxury context but can be adjusted)

### Replace cover image
- Edit `bg_path` inside `draw_cover_bg()`.
- The cover-fit math handles any aspect ratio automatically.

---

## 8. Open items / TODO

- **Round Ultra Luxury total to $7,930?** Currently $7,929; the per-person derivation is $3,964.50 which gets rounded to $3,965 in display. Cleaner option: bump total to $7,930.
- **Designer credits and rankings should be re-verified yearly.** Mission Hills #1 ranking is Asian Golf Monthly 2011–2015 — still cited, but consider checking for newer awards. Shenzhou #2 ranking is Golf Digest 2022.
- **Footer page numbers** start at "Page 1" on the 2nd PDF page (cover doesn't show a number). If renaming, the offset is `doc.page - 1`.
- **No print bleed configured.** Designed for screen / email PDF. If sending to print, add bleed marks and increase margins.

---

## 9. Quick reference — page math

| Quantity | Value |
|---|---|
| Page size | A4 (210 × 297 mm) |
| Margins (content pages) | L/R: 18 mm · Top: 22 mm · Bottom: 22 mm |
| Content width (`CONTENT_W`) | 174 mm |
| Available content height | ~253 mm |
| Brand colors | Navy `#0B2545` · Gold `#C9A86A` · Coral `#D87C5A` · Green `#2D5F4A` · Cream `#F5EFE6` |
| Body font | Helvetica · 10 pt / 15 pt leading |
| H1 | Helvetica-Bold · 28 pt / 32 pt leading · Navy |

---

End of handover.
