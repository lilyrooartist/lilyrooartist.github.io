#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timedelta
import json, csv, re

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / 'admin' / 'reports' / 'weekly-social-report.md'
MANUAL = ROOT / 'data' / 'manual_social_stats.json'
LIVE = ROOT / 'data' / 'live_social_metrics.json'
SPOTIFY_SNAPSHOT = ROOT / 'data' / 'spotify_release_snapshot.json'
APPLE_MUSIC_SNAPSHOT = ROOT / 'data' / 'apple_music_release_snapshot.json'
YOUTUBE_PUBLIC = ROOT / 'data' / 'youtube_public_snapshot.json'
YOUTUBE_TITLE_TRACK = ROOT / 'data' / 'youtube_title_track_snapshot.json'
YOUTUBE_MUSIC_SNAPSHOT = ROOT / 'data' / 'youtube_music_release_snapshot.json'
HYPERFOLLOW_SNAPSHOT = ROOT / 'data' / 'hyperfollow_store_links_snapshot.json'
STORE_VERIFICATION_HISTORY = ROOT / 'data' / 'store_verification_history.json'
ALIGNMENT_AUDIT = ROOT / 'data' / 'first_single_alignment_audit.json'
DISTROKID_RELEASE_STATUS = ROOT / 'data' / 'distrokid_release_status.json'
PUBLISHED = ROOT / 'admin' / 'content' / 'Published_Log.csv'
ADMIN_INDEX = ROOT / 'admin' / 'index.html'

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
live = json.loads(LIVE.read_text(encoding='utf-8')) if LIVE.exists() else {}
spotify_snapshot = json.loads(SPOTIFY_SNAPSHOT.read_text(encoding='utf-8')) if SPOTIFY_SNAPSHOT.exists() else {}
apple_music_snapshot = json.loads(APPLE_MUSIC_SNAPSHOT.read_text(encoding='utf-8')) if APPLE_MUSIC_SNAPSHOT.exists() else {}
youtube_public = json.loads(YOUTUBE_PUBLIC.read_text(encoding='utf-8')) if YOUTUBE_PUBLIC.exists() else {}
youtube_title_track = json.loads(YOUTUBE_TITLE_TRACK.read_text(encoding='utf-8')) if YOUTUBE_TITLE_TRACK.exists() else {}
youtube_music_snapshot = json.loads(YOUTUBE_MUSIC_SNAPSHOT.read_text(encoding='utf-8')) if YOUTUBE_MUSIC_SNAPSHOT.exists() else {}
hyperfollow_snapshot = json.loads(HYPERFOLLOW_SNAPSHOT.read_text(encoding='utf-8')) if HYPERFOLLOW_SNAPSHOT.exists() else {}
store_verification_history = json.loads(STORE_VERIFICATION_HISTORY.read_text(encoding='utf-8')) if STORE_VERIFICATION_HISTORY.exists() else {}
alignment_audit = json.loads(ALIGNMENT_AUDIT.read_text(encoding='utf-8')) if ALIGNMENT_AUDIT.exists() else {}
distrokid_release_status = json.loads(DISTROKID_RELEASE_STATUS.read_text(encoding='utf-8')) if DISTROKID_RELEASE_STATUS.exists() else {}
youtube = manual.get('youtube', {})
spotify = manual.get('spotify', {})
live_platforms = live.get('platforms', {}) if isinstance(live, dict) else {}


def live_metric(platform, key):
    metrics = live_platforms.get(platform, {}).get('metrics', {})
    value = metrics.get(key)
    return value if value not in (None, '') else None


def live_reason(platform):
    return live_platforms.get(platform, {}).get('reason', '')


def status_text(reason):
    reason = str(reason or '').strip()
    if 'invalid_grant' in reason:
        return 'YouTube OAuth refresh token invalid_grant; run scripts/youtube_oauth_browser_helper.py, then run scripts/update_youtube_video_title.py --apply and redeploy/push the refreshed token'
    return reason or 'manual fallback'


def release_rollout_section(status):
    releases = status.get('releases') or []
    if not releases:
        return '## Release Rollout\n- No DistroKid release status file found.\n'
    lines = ['## Release Rollout']
    for release in releases:
        title = release.get('title') or 'Untitled release'
        lines.extend([
            '',
            f"### {title}",
            f"- Type: **{release.get('type', 'release')}**",
            f"- Tracks: **{release.get('track_count', 'pending')}**",
            f"- DistroKid status: **{release.get('distrokid_status', 'pending')}**",
            f"- Store status: **{release.get('store_status', 'pending')}**",
            f"- Release date: **{release.get('release_date', 'pending')}**",
            f"- Primary CTA: **{release.get('primary_cta', 'pending')}**",
        ])
        links = [
            ('Spotify', release.get('spotify_url')),
            ('Apple Music', release.get('apple_music_url')),
            ('YouTube Music', release.get('youtube_music_url')),
            ('HyperFollow', release.get('hyperfollow_url')),
            ('YouTube playlist', release.get('youtube_playlist_url')),
        ]
        for label, url in links:
            if url:
                lines.append(f"- {label}: {url}")
        notes = release.get('notes') or []
        for note in notes:
            lines.append(f"- Note: {note}")
    open_checks = status.get('open_checks') or []
    if open_checks:
        lines.extend(['', '### Open Store Checks'])
        for check in open_checks:
            lines.append(f"- {check}")
    return '\n'.join(lines) + '\n'


def stat(platform, key, fallback='pending'):
    value = live_metric(platform, key)
    return str(value) if value is not None else str(fallback)

yt_subs = stat('youtube', 'subscribers', youtube.get('subscribers', 'pending'))
yt_views_28d = stat('youtube', 'views_28d', youtube.get('views_28d', 'pending'))
yt_watch_28d = stat('youtube', 'watch_time_hours_28d', youtube.get('watch_time_hours_28d', 'pending'))
youtube_status = 'live API' if live_platforms.get('youtube', {}).get('ok') else status_text(live_reason('youtube'))
youtube_public_count = youtube_public.get('recent_video_count', 'pending')
youtube_public_views = youtube_public.get('recent_public_views_total', 'pending')
youtube_latest = youtube_public.get('latest_video') or {}
youtube_latest_title = youtube_latest.get('title') or 'pending'
youtube_latest_views = youtube_latest.get('views', 'pending')
youtube_public_time = youtube_public.get('updated_at') or 'not captured'
youtube_title_track_time = youtube_title_track.get('updated_at') or 'not captured'
youtube_title_track_url = youtube_title_track.get('url') or 'https://www.youtube.com/watch?v=vK0mDIW65o4'
youtube_public_title = youtube_title_track.get('public_title') or 'pending'
youtube_official_title = youtube_title_track.get('official_title') or 'I Learned It All in Fifteen Seconds'
youtube_title_match = youtube_title_track.get('title_matches_official')
youtube_title_status = 'matches official title' if youtube_title_match is True else 'needs title capitalization update'
youtube_music_release_url = youtube_music_snapshot.get('release_url') or 'pending'
youtube_music_public_title = youtube_music_snapshot.get('public_title') or 'pending'
youtube_music_title_match = youtube_music_snapshot.get('title_matches_official')
youtube_music_title_status = 'matches official title' if youtube_music_title_match is True else 'mirrors YouTube title capitalization mismatch'
youtube_music_snapshot_time = youtube_music_snapshot.get('updated_at') or 'not captured'
hyperfollow_url = hyperfollow_snapshot.get('hyperfollow_url') or 'pending'
hyperfollow_stores = ', '.join(hyperfollow_snapshot.get('stores') or []) or 'pending'
amazon_music_status = 'verified in HyperFollow' if hyperfollow_snapshot.get('amazon_music_available') else 'pending verified public URL; not exposed by current HyperFollow store list'
hyperfollow_snapshot_time = hyperfollow_snapshot.get('updated_at') or 'not captured'
store_history_summary = store_verification_history.get('summary') or {}
store_history_time = store_verification_history.get('generated_at') or 'not captured'
store_history_status = (
    f"{store_history_summary.get('live', 0)} live, "
    f"{store_history_summary.get('checked_pending', 0)} checked pending, "
    f"{store_history_summary.get('pending', 0)} pending, "
    f"{store_history_summary.get('snapshot_count', 0)} snapshots"
)
alignment_action_required = ', '.join(alignment_audit.get('action_required') or []) or 'none'
alignment_pending = ', '.join(alignment_audit.get('pending') or []) or 'none'
alignment_status = 'aligned' if alignment_audit.get('ok') else 'needs attention'
alignment_snapshot_time = alignment_audit.get('updated_at') or 'not captured'
spotify_release_url = spotify.get('release_url', 'pending')
spotify_artist_url = spotify.get('artist_url') or spotify_snapshot.get('artist_url') or 'pending'
spotify_artist_followers = spotify.get('artist_followers', 'pending')
spotify_monthly_listeners = spotify.get('monthly_listeners', 'pending')
spotify_release_streams = spotify.get('release_streams', 'pending')
spotify_saves = spotify.get('saves', 'pending')
spotify_verified_title = spotify_snapshot.get('title') or 'pending'
spotify_artwork = spotify_snapshot.get('thumbnail_url') or 'pending'
spotify_snapshot_time = spotify_snapshot.get('updated_at') or 'not captured'
spotify_analytics_status = spotify_snapshot.get('analytics_status') or 'manual Spotify for Artists export required'
apple_music_release_url = apple_music_snapshot.get('release_url') or 'pending'
apple_music_artist_url = apple_music_snapshot.get('artist_url') or 'pending'
apple_music_verified_title = apple_music_snapshot.get('collection_name') or 'pending'
apple_music_explicitness = apple_music_snapshot.get('explicitness') or 'pending'
apple_music_snapshot_time = apple_music_snapshot.get('updated_at') or 'not captured'
tiktok_followers = stat('tiktok', 'followers', manual.get('tiktok',{}).get('followers','pending'))
tiktok_profile_views = stat('tiktok', 'profile_views_7d', manual.get('tiktok',{}).get('profile_views_7d','pending'))
instagram_followers = stat('instagram', 'followers', manual.get('instagram',{}).get('followers','pending'))
instagram_profile_visits = stat('instagram', 'profile_visits_7d', manual.get('instagram',{}).get('profile_visits_7d','pending'))
x_followers = stat('x', 'followers', manual.get('x',{}).get('followers','pending'))
x_impressions = stat('x', 'impressions_7d', manual.get('x',{}).get('impressions_7d','pending'))
facebook_followers = stat('facebook', 'followers', manual.get('facebook',{}).get('followers','pending'))
facebook_reach = stat('facebook', 'reach_7d', manual.get('facebook',{}).get('reach_7d','pending'))
metrics_snapshot = live.get('updated_at', 'not captured')

today = datetime.now().astimezone()
start = (today - timedelta(days=6)).date()
end = today.date()

md = f'''# Weekly Social Report — Lily Roo

**Period:** {start} to {end}
**Last updated:** {today.strftime('%Y-%m-%d %I:%M %p %Z').strip()}

## KPI Goal
- Primary growth target: **1,000 YouTube subscribers** (monetization milestone)

{release_rollout_section(distrokid_release_status)}
## Platform Snapshot

### YouTube
- Subscribers: **{yt_subs}**
- Last 28 days views: **{yt_views_28d}**
- Last 28 days watch time: **{yt_watch_28d} hours**
- API status: **{youtube_status}**
- Public RSS recent-video views: **{youtube_public_views} across {youtube_public_count} videos**
- Latest public upload: **{youtube_latest_title}** ({youtube_latest_views} views)
- Title-track video: {youtube_title_track_url}
- Title-track public title: **{youtube_public_title}**
- Official title: **{youtube_official_title}**
- Title-track title status: **{youtube_title_status}**

### YouTube Music
- First single: {youtube_music_release_url}
- Public release check: **{youtube_music_public_title}**
- Title status: **{youtube_music_title_status}**

### Other Stores
- HyperFollow: {hyperfollow_url}
- HyperFollow stores: **{hyperfollow_stores}**
- Amazon Music: **{amazon_music_status}**
- All-release store verification: **{store_history_status}**

### First Single Alignment
- Status: **{alignment_status}**
- Action required: **{alignment_action_required}**
- Pending: **{alignment_pending}**

### Spotify
- First single: {spotify_release_url}
- Artist profile: {spotify_artist_url}
- Public release check: **{spotify_verified_title}**
- Remastered artwork thumbnail: {spotify_artwork}
- Artist followers: **{spotify_artist_followers}**
- Monthly listeners: **{spotify_monthly_listeners}**
- Release streams: **{spotify_release_streams}**
- Saves: **{spotify_saves}**
- Analytics status: **{spotify_analytics_status}**

### Apple Music
- First single: {apple_music_release_url}
- Artist profile: {apple_music_artist_url}
- Public release check: **{apple_music_verified_title}**
- Explicitness: **{apple_music_explicitness}**

### TikTok
- Followers: **{tiktok_followers}**
- Profile views (7d): **{tiktok_profile_views}**
- Latest post: {latest['TikTok'] or 'pending'}

### Instagram
- Followers: **{instagram_followers}**
- Profile visits (7d): **{instagram_profile_visits}**
- Latest post: {latest['Instagram'] or 'pending'}

### X (Twitter)
- Followers: **{x_followers}**
- Impressions (7d): **{x_impressions}**
- Latest post: {latest['X'] or 'pending'}

### Facebook
- Followers/Page likes: **{facebook_followers}**
- Reach (7d): **{facebook_reach}**
- Latest post: {latest['Facebook'] or 'pending'}

## Metrics Snapshot
- Live API captured: **{metrics_snapshot}**
- Snapshot file: `data/live_social_metrics.json`
- YouTube public RSS captured: **{youtube_public_time}**
- YouTube public snapshot file: `data/youtube_public_snapshot.json`
- YouTube title-track captured: **{youtube_title_track_time}**
- YouTube title-track snapshot file: `data/youtube_title_track_snapshot.json`
- YouTube Music public release captured: **{youtube_music_snapshot_time}**
- YouTube Music snapshot file: `data/youtube_music_release_snapshot.json`
- HyperFollow stores captured: **{hyperfollow_snapshot_time}**
- HyperFollow snapshot file: `data/hyperfollow_store_links_snapshot.json`
- All-release store verification captured: **{store_history_time}**
- All-release store verification file: `data/store_verification_history.json`
- First single alignment audit captured: **{alignment_snapshot_time}**
- First single alignment audit file: `data/first_single_alignment_audit.json`
- Spotify public release captured: **{spotify_snapshot_time}**
- Spotify snapshot file: `data/spotify_release_snapshot.json`
- Apple Music public release captured: **{apple_music_snapshot_time}**
- Apple Music snapshot file: `data/apple_music_release_snapshot.json`

## Weekly Activity Log
- Admin site now uses Dashboard / Backstory / Songs / Promo navigation
- Backstory and visual packs generated for all archive songs
- Upcoming 7-day queue supports redo variants, imagery previews, and shareable filtered views

## Next-week priorities
1. Publish at least 5 short-form posts from queue
2. Use hard YouTube subscribe CTA every 2–3 posts
3. Fill manual_social_stats.json values for platform deltas, including Spotify release streams once Spotify for Artists exposes them

## Reporting cadence
- Capture YouTube public video views: `python3 scripts/capture_youtube_public.py`
- Capture YouTube title-track public metadata: `python3 scripts/capture_youtube_title_track.py`
- Capture YouTube Music public release metadata: `python3 scripts/capture_youtube_music_release.py`
- Capture HyperFollow store links: `python3 scripts/capture_hyperfollow_store_links.py`
- Verify pending DistroKid store links: `python3 scripts/verify_pending_store_links.py --refresh-admin`
- Audit first single alignment: `python3 scripts/audit_first_single_alignment.py`
- Capture Spotify public release metadata: `python3 scripts/capture_spotify_release.py`
- Capture Apple Music public release metadata: `python3 scripts/capture_apple_music_release.py`
- Capture live API metrics: `python3 scripts/capture_live_metrics.py`
- Update metrics history: `python3 scripts/update_metrics_history.py --refresh-admin`
- Capture executor readiness: `LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
- Regenerate via: `python3 scripts/update_weekly_report.py`
- Source overrides: `data/manual_social_stats.json`
'''
REPORT.write_text(md, encoding='utf-8')


def replace_embedded_block(html, block_id, content):
    pattern = rf'(<script type="text/plain" id="{re.escape(block_id)}">)([\s\S]*?)(</script>)'
    return re.sub(pattern, lambda m: m.group(1) + content.rstrip() + m.group(3), html, count=1)


def sync_admin_embeds():
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding='utf-8')
    updated = replace_embedded_block(html, 'embedded-weekly-report', REPORT.read_text(encoding='utf-8'))
    if PUBLISHED.exists():
        updated = replace_embedded_block(updated, 'embedded-published-log', PUBLISHED.read_text(encoding='utf-8'))
    if updated != html:
        ADMIN_INDEX.write_text(updated, encoding='utf-8')


sync_admin_embeds()
print('updated', REPORT)
