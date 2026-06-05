# Weekly Social Report — Lily Roo

**Period:** 2026-05-30 to 2026-06-05
**Last updated:** 2026-06-05 09:54 AM EDT

## KPI Goal
- Primary growth target: **1,000 YouTube subscribers** (monetization milestone)

## Platform Snapshot

### YouTube
- Subscribers: **6**
- Last 28 days views: **109**
- Last 28 days watch time: **3.4 hours**
- API status: **YouTube OAuth refresh token invalid_grant; run scripts/youtube_oauth_browser_helper.py and redeploy/push the refreshed token**

### Spotify
- First single: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi
- Artist followers: **pending**
- Monthly listeners: **pending**
- Release streams: **pending**
- Saves: **pending**

### TikTok
- Followers: **pending**
- Profile views (7d): **pending**
- Latest post: https://www.tiktok.com/@lilyroo930/video/7611932426557754654

### Instagram
- Followers: **0**
- Profile visits (7d): **pending**
- Latest post: posted

### X (Twitter)
- Followers: **pending**
- Impressions (7d): **pending**
- Latest post: https://x.com/i/web/status/2048245628736622826

### Facebook
- Followers/Page likes: **0**
- Reach (7d): **pending**
- Latest post: https://www.facebook.com/903693509504290_122113878687249470

## Metrics Snapshot
- Live API captured: **2026-06-05T13:54:23.842Z**
- Snapshot file: `data/live_social_metrics.json`

## Weekly Activity Log
- Admin site now uses Dashboard / Backstory / Songs / Promo navigation
- Backstory and visual packs generated for all archive songs
- Upcoming 7-day queue supports redo variants, imagery previews, and shareable filtered views

## Next-week priorities
1. Publish at least 5 short-form posts from queue
2. Use hard YouTube subscribe CTA every 2–3 posts
3. Fill manual_social_stats.json values for platform deltas, including Spotify release streams once Spotify for Artists exposes them

## Reporting cadence
- Capture live API metrics: `python3 scripts/capture_live_metrics.py`
- Regenerate via: `python3 scripts/update_weekly_report.py`
- Source overrides: `data/manual_social_stats.json`
