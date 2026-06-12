# lilyrooartist.github.io

Static site and admin workspace for Lily Roo.

## Repo Map

| Path | Purpose |
| --- | --- |
| `index.html`, `music.html`, `press.html`, `contact.html` | Public GitHub Pages site. |
| `style.css`, `script.js` | Shared public-site styling and small client behavior. |
| `admin/index.html` | Local/admin operations surface: dashboard, backstory library, song pack browser, and promo queue. |
| `admin/content/` | Canon, voice, backstory, quips, promo strategy, reporting logs. |
| `admin/content/packs/` | Per-song backstory and visual packs. |
| `admin/backstory/` | JSON data and browser surface for song backstory browsing. |
| `data/scheduled_posts.csv` | Source of truth for the upcoming posting queue. |
| `admin/future-posts.json` | Generated admin queue payload. Do not hand-edit. |
| `scripts/` | Queue sync, reporting, content indexing, publishing checks, media helpers. |
| `scripts/aol_gmail_bridge.py` | Local IMAP bridge for copying new AOL mail into Gmail. |
| `workers/social-executor/` | Cloudflare Worker for authenticated social publishing. |
| `assets/` | Public images, audio, lyrics, video, icons, and release media. |

## Content Workflow

After editing canon, backstory, quips, queue, or reports:

```bash
python3 scripts/build_content_index.py
python3 scripts/sync_future_posts.py
python3 scripts/capture_youtube_public.py
python3 scripts/capture_spotify_release.py
python3 scripts/capture_live_metrics.py
python3 scripts/update_weekly_report.py
python3 scripts/validate_content_system.py
```

Promo/admin freshness is also automated by `.github/workflows/promo-admin-refresh.yml`.
It runs the safe refresh pipeline every 6 hours and can be run manually from GitHub Actions.
The workflow only captures metrics/status, rebuilds admin reports, validates the content system, and commits changed `admin/` or `data/` snapshots. It does not approve, apply, or publish posts.
For authenticated executor captures, configure repository secrets `LILYROO_ADMIN_PASSWORD` or `LILYROO_EXECUTOR_BEARER_TOKEN`.

The admin page can be opened from a local server or directly as a file. The served path is preferred:

```bash
python3 -m http.server 4177 --bind 127.0.0.1
```

Then open:

`http://127.0.0.1:4177/admin/`

## AOL Mail Bridge

The AOL-to-Gmail bridge is local-only and uses app passwords from `../secrets/aol-gmail-bridge.env`.
Setup and run instructions live in `admin/content/21_AOL_GMAIL_BRIDGE.md`.
After both app passwords are stored, `scripts/install_aol_gmail_bridge_launchd.sh` installs the 5-minute local runner.
For safer password entry, run `python3 scripts/aol_gmail_bridge_setup_helper.py` and paste the app passwords into the local form.
The installer copies the launchd runtime into `~/Library/Application Support/LilyRoo/AOLGmailBridge`.

## Content Source Rules

- `admin/content/README.md` explains the source-of-truth map.
- `admin/content/01_VOICE_SYSTEM.md` defines Lily's posting voice.
- `admin/content/CONTENT_INDEX.md` and `admin/content/content_index.json` are generated inventory files.
- `data/scheduled_posts.csv` drives the Promo tab and upcoming queue.
- `admin/content/Published_Log.csv` drives Dashboard publishing metrics.

## Deployment Note

This repo is designed for GitHub Pages through `CNAME` (`www.lilyroo.com`). Local edits are not live until committed and pushed through the normal Pages workflow.
