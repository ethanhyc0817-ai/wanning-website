# How to rebuild the brochure on another Claude account

Three files in this folder are all you need to reproduce the PDF exactly:

| File | What it is |
|---|---|
| `build_brochure.py` | The full Python source — 1,100 lines, ReportLab |
| `Assets/` | All photos referenced by the script |
| `PDF_Handover.md` | Design rationale and copy specs (optional, but useful) |

The script auto-detects the `Wanning` folder location, so it runs unchanged on any Mac.

---

## Option A · Easiest (Cowork mode, any Claude account)

1. Open Cowork mode in the new Claude account.
2. Use **Add folder** to select your `Wanning` folder. Make sure `build_brochure.py` and the `Assets/` folder are inside it.
3. Send this single prompt:

   > Please run `build_brochure.py` in my Wanning folder. It will produce `Surf_and_Golf_Hainan_Brochure.pdf` in the same folder.

That's it. Claude will execute the script and the PDF will appear in your Wanning folder, identical to the current one.

---

## Option B · From the command line on your Mac (no Claude needed)

If you ever want to regenerate without using Claude at all:

```bash
# 1) Install the two Python libraries the script needs
pip3 install reportlab pillow --break-system-packages

# 2) Run the script
cd ~/Documents/Wanning
python3 build_brochure.py
```

The PDF gets written next to the script.

---

## Option C · Rebuild from scratch with a fresh Claude (if you lose the script)

If you only have the photos and `PDF_Handover.md`:

1. Share the `Assets/planner/` folder and `PDF_Handover.md` with the new Claude.
2. Ask: *"Rebuild this PDF brochure following the spec in PDF_Handover.md."*

This will get you something very close but **not byte-identical** — Claude will make small judgment calls. Use Option A or B for exact reproduction.

---

## What changes if you edit photos

The script auto-discovers files by name. So:

- **Replacing a photo:** keep the same filename, drop the new file into the same folder. Re-run the script — done.
- **Renaming or deleting:** open `build_brochure.py`, search for the old filename, replace with the new name.
- **Cropping Mission Hills photos:** there's a folder `Assets/planner/观澜湖_cropped/` with the 3:2 versions already cropped. If you replace a Mission Hills photo, re-crop it to 3:2 and drop it in that folder. Or ask Claude to "re-crop the Mission Hills photos to 3:2 ratio."

---

## What changes if you edit copy (prices, descriptions, etc.)

Open `build_brochure.py` in any text editor. The strings are in plain English — search for what you want to change:

| To change | Search for |
|---|---|
| Prices | `$2,200` or `$3,965` or `$4,400` or `$7,929` |
| Comparison table rows | `features = [` |
| Itinerary days | `itinerary_days = [` |
| Awards on course pages | `awards_block([` |
| Cover title or subtitle | `"Surf &amp; Golf"` or `"A PRIVATE PROPOSAL"` |
| Footer contact line | `CONTACT_LINE = (` |

Save and re-run the script.

---

## Page-by-page reference

| Page | Section | Edit location in script |
|---|---|---|
| 1 | Cover | `# COVER PAGE` block |
| 2 | Comparison table | `features = [` and surrounding |
| 3 | Premium detail | `# PAGE 3 — PREMIUM PACKAGE` |
| 4 | Luxury detail | `# PAGE 4 — LUXURY PACKAGE` |
| 5 | Sample journey | `itinerary_days = [` |
| 6–7 | Mission Hills | `awards_block([("#1", ...)` |
| 8–9 | Shenzhou Peninsula | `awards_block([("#2", ...)` |
| 10 | The Ritz-Carlton | search `Ritz-Carlton, Haikou` |
| 11 | Wave Pool Resort | search `The Wave Pool Resort` |
| 12 | Beyond / Shanqin Bay | search `Shanqin Bay` |

---

That's all. Keep these three files together and the brochure will be reproducible forever.
