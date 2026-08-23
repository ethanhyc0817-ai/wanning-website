# Wanning website — working notes

- After completing any change, always commit and `git push origin HEAD` directly. Ethan does not want to be asked — pushing is part of finishing the task.
- Site deploys automatically on push (Vercel).
- `index.html` is a single-page app using `showPage()`; the homepage and wavepool page each have a copy of the rates board — keep them consistent when editing pricing.
- `/Assets` images, video and fonts are cached for a week (`vercel.json` headers).
  Filenames are not content-hashed, so when you replace an asset in place, either
  rename it or add `?v=N` to the reference — otherwise repeat visitors keep the old
  file for up to 7 days. PDFs and HTML are excluded and still revalidate every time.
- The hero `<link rel="preload">` tags must mirror the `<picture>` AVIF `srcset`/`sizes`
  exactly. If they drift, the browser downloads both the preloaded file and the one
  `<picture>` actually picks.
