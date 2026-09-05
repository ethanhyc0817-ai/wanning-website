# Wanning Website

A website showcasing Wanning — surf, hotel, nature, culture, and food.

## Tech
- Pure HTML/CSS/JS single-page site
- Images stored locally in `Assets/`
- Videos served via Cloudinary CDN

## Local preview
`python3 tools/devserver.py` then open http://127.0.0.1:8765. It applies the `vercel.json` rewrites and redirects, so `/#contact` (which frames `/book-your-wave`), `/golf.html` and the short URLs resolve like production. Opening `index.html` straight from disk leaves the booking panel empty.

## Deploy
Connected to Vercel/Netlify/Cloudflare Pages — every push to `main` auto-deploys.
