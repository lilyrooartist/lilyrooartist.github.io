---
name: website-ops
description: "Maintain and ship updates to a simple static website hosted on GitHub Pages (HTML/CSS/JS) with a fast, safe workflow: edit pages, add new pages, update links/embeds, improve SEO/OpenGraph, validate locally, commit/push, and confirm deploy. Use when working on lilyroo.com / lilyrooartist.github.io or similar static sites."
---

# Website Ops (GitHub Pages)

## Working repo (Lily Roo)
- Repo directory (local): `~/ .openclaw/workspace/lilyrooartist.github.io`
- Branch: `main`
- Pages hostname: `lilyroo.com` (via CNAME)

## Ship loop
1) `cd lilyrooartist.github.io && git pull`
2) Make smallest possible change.
3) Quick sanity checks
   - Open the file(s) and scan for broken tags/quotes.
   - Ensure internal links are absolute-root (`/music.html`) not relative.
   - Confirm embeds use privacy-friendly variants when possible (e.g., `youtube-nocookie.com`).
4) Commit with a descriptive message.
5) `git push`.
6) Confirm deploy by spot-checking the page in a browser.

## Content rules (site tone)
- Homepage should be conversion-oriented: **Play** + **Subscribe** above the fold.
- When in “AI lore” mode, keep mystery *tasteful*: clear CTAs, lore in copy.

## SEO/OpenGraph checklist (minimum)
- `<meta name="description">` is specific and not generic.
- Open Graph tags: `og:title`, `og:description`, `og:url`, `og:image`, `og:type`.
- `twitter:card` is set.
- `og:image` is a stable absolute URL.

## Safe patterns
- Prefer adding small reusable CSS utility classes over inline style.
- Avoid heavy JS. Keep it static.

## When adding pages
- Use same visual system (colors, radius, type).
- Add nav links on home.
- Add “← Back to home”.

## References
- See `references/lilyroo-site-map.md` for page inventory + conventions.
