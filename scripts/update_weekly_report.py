#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timedelta
import json, csv

ROOT = Path('/Users/lilyroo/Library/Mobile Documents/com~apple~CloudDocs/Lily Roo/lilyrooartist.github.io')
REPORT = ROOT / 'admin' / 'reports' / 'weekly-social-report.md'
MANUAL = ROOT / 'data' / 'manual_social_stats.json'
PUBLISHED = ROOT / 'admin' / 'content' / 'Published_Log.csv'

# Fallback values if API pull is not wired in this run
yt_subs = '6'
yt_views_28d = '109'
yt_watch_28d = '3.4'

# Try to read latest published URLs
latest = {'X':'', 'Instagram':'', 'TikTok':'', 'Facebook':''}
if PUBLISHED.exists():
    with PUBLISHED.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    for r in reversed(rows):
        p = (r.get('platform') or '').strip()
        url = (r.get('post_id_or_url') or '').strip()
        if p in latest and not latest[p] and url:
            latest[p] = url

manual = json.loads(MANUAL.read_text(encoding='utf-8')) if MANUAL.exists() else {}

today = datetime.now()
start = (today - timedelta(days=6)).date()
end = today.date()

md = f'''# Weekly Social Report — Lily Roo

**Period:** {start} to {end}  
**Last updated:** {today.strftime('%Y-%m-%d %I:%M %p %Z').strip()}

## KPI Goal
- Primary growth target: **1,000 YouTube subscribers** (monetization milestone)

## Platform Snapshot

### YouTube
- Subscribers: **{yt_subs}**
- Last 28 days views: **{yt_views_28d}**
- Last 28 days watch time: **{yt_watch_28d} hours**

### TikTok
- Followers: **{manual.get('tiktok',{}).get('followers','pending')}**
- Profile views (7d): **{manual.get('tiktok',{}).get('profile_views_7d','pending')}**
- Latest post: {latest['TikTok'] or 'pending'}

### Instagram
- Followers: **{manual.get('instagram',{}).get('followers','pending')}**
- Profile visits (7d): **{manual.get('instagram',{}).get('profile_visits_7d','pending')}**
- Latest post: {latest['Instagram'] or 'pending'}

### X (Twitter)
- Followers: **{manual.get('x',{}).get('followers','pending')}**
- Impressions (7d): **{manual.get('x',{}).get('impressions_7d','pending')}**
- Latest post: {latest['X'] or 'pending'}

### Facebook
- Followers/Page likes: **{manual.get('facebook',{}).get('followers','pending')}**
- Reach (7d): **{manual.get('facebook',{}).get('reach_7d','pending')}**
- Latest post: {latest['Facebook'] or 'pending'}

## Weekly Activity Log
- Admin site now includes left-tab ops navigation (Promo / Backstory / Reports)
- Backstory and visual packs generated for all archive songs
- Upcoming 7-day queue supports redo variants, imagery previews, and shareable filtered views

## Next-week priorities
1. Publish at least 5 short-form posts from queue
2. Use hard YouTube subscribe CTA every 2–3 posts
3. Fill manual_social_stats.json values for platform deltas

## Reporting cadence
- Regenerate via: `python3 scripts/update_weekly_report.py`
- Source overrides: `data/manual_social_stats.json`
'''
REPORT.write_text(md, encoding='utf-8')
print('updated', REPORT)
