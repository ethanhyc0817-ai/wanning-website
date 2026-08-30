# Wanning website — working notes

- After completing any change, always commit and `git push origin HEAD` directly. Ethan does not want to be asked — pushing is part of finishing the task.
- Site deploys automatically on push (Vercel).
- `index.html` is a single-page app using `showPage()`; the rates board now has THREE copies — the homepage `#rates` section, the wavepool panel, and the standalone `pages/rates.html` — keep all three consistent when editing pricing.
- Sales rule (Aug 2026): public pricing must NOT advertise the 15% buyout promo
  ANYWHERE on the site, and the promo number must not SHIP AT ALL. `index.html`
  (rate board, wavepool panel, trip planner), `pages/rates.html`,
  `pages/design-your-buyout.html` and `pages/inquiry.html` publish the LIST rates
  (7,760 / 9,960) — no struck-through anchor, no percentage, no "was / now" pair,
  no "List rate vs Your price" columns, no derived saving. Instead a "Special
  offers · ask us for your rate" pill hints the price is negotiable.
  - `Assets/sc-pricing.js` is served to every visitor at `/Assets/sc-pricing.js`, so
    it carries LIST RATES ONLY. `buyoutPromoPct` and `buyout.*.promo` were removed
    (Aug 2026) — a discount left in that file is readable from devtools by anyone.
    Quote the promo by hand from `Pricing/calculator.xlsx`. If a sync skill tries to
    write `promo:` back into the config block, that is a regression, not a restore.
  - Every calculator carries `data-sc-listonly` on its `data-sc-wave` radios (now a
    no-op marker — the config has no promo to fall back to); design-your-buyout's
    WAVES array uses `now: SCB.<wave>.list`, and its `price()` computes ONE total,
    with no `was`/`save`/`ANCHOR` to diff back into the discount.
  - EXCEPTION, still outstanding: `pages/book-surf.html` (served at `/book/surf`,
    `noindex`, no inbound links, mid-redesign) still has a hardcoded struck price
    at line 331 and a `bkSumWas` anchor at line 550. It is a live 200 for anyone
    with the URL. Fix or block it when that redesign lands.
- Buyout prices live in `Assets/sc-pricing.js` (machine-synced). `pages/design-your-buyout.html` and `pages/rates.html` carry those CNY prices in static HTML (`data-sc-num` spans, runtime-refreshed) AND in JSON-LD blocks that are NOT runtime-refreshed — a price sync must update the JSON-LD numbers on both pages too.
- Public regular surf-session sell price (Aug 2026): publish CNY 550/person for Beginner, Intermediate and Advanced sessions. Do not restore the old park ticket/reference prices (358 / 349 / 448) on public rate boards or schema.
- SEO decisions (Aug 2026): prices in client-facing static copy/schema are CNY; no author bylines on blog posts; no About/Team page for now. `index.html` must keep exactly ONE `<h1>` (the hero) — SPA panel titles are `<h2 class="page-title">`.
- `.github/workflows/indexnow.yml` pings IndexNow (Bing/Yandex) with changed page URLs on every push; the key file `da871c4474c953d2ff65ddd030275b6d.txt` at repo root must stay deployed.
- `/Assets` images, video and fonts are cached for a week (`vercel.json` headers).
  Filenames are not content-hashed, so when you replace an asset in place, either
  rename it or add `?v=N` to the reference — otherwise repeat visitors keep the old
  file for up to 7 days. PDFs and HTML are excluded and still revalidate every time.
- The hero `<link rel="preload">` tags must mirror the `<picture>` AVIF `srcset`/`sizes`
  exactly. If they drift, the browser downloads both the preloaded file and the one
  `<picture>` actually picks.
