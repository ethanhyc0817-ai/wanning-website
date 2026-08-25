# Wanning website — working notes

- After completing any change, always commit and `git push origin HEAD` directly. Ethan does not want to be asked — pushing is part of finishing the task.
- Site deploys automatically on push (Vercel).
- `index.html` is a single-page app using `showPage()`; the rates board now has THREE copies — the homepage `#rates` section, the wavepool panel, and the standalone `pages/rates.html` — keep all three consistent when editing pricing.
- Buyout prices live in `Assets/sc-pricing.js` (machine-synced). `pages/design-your-buyout.html` and `pages/rates.html` carry those CNY prices in static HTML (`data-sc-num` spans, runtime-refreshed) AND in JSON-LD blocks that are NOT runtime-refreshed — a price sync must update the JSON-LD numbers on both pages too.
- SEO decisions (Aug 2026): prices in client-facing static copy/schema are CNY; no author bylines on blog posts; no About/Team page for now. `index.html` must keep exactly ONE `<h1>` (the hero) — SPA panel titles are `<h2 class="page-title">`.
- `.github/workflows/indexnow.yml` pings IndexNow (Bing/Yandex) with changed page URLs on every push; the key file `da871c4474c953d2ff65ddd030275b6d.txt` at repo root must stay deployed.
- `/Assets` images, video and fonts are cached for a week (`vercel.json` headers).
  Filenames are not content-hashed, so when you replace an asset in place, either
  rename it or add `?v=N` to the reference — otherwise repeat visitors keep the old
  file for up to 7 days. PDFs and HTML are excluded and still revalidate every time.
- The hero `<link rel="preload">` tags must mirror the `<picture>` AVIF `srcset`/`sizes`
  exactly. If they drift, the browser downloads both the preloaded file and the one
  `<picture>` actually picks.
