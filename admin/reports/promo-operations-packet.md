# Promo Operations Packet - Lily Roo

Generated: 2026-06-20T01:46:21.072204Z

## Summary
- Actions: **18**
- User review: **3**
- Platform fixes: **1**
- Scheduled approval batches: **1**
- Store checks: **7**
- Manual metric updates: **5**
- Safe apply commands ready: **0**
- Urgency: **blocked: 1, high: 3, low: 5, medium: 9**

## Phase Counts
- Fill manual metrics: **5**
- Repair executor: **1**
- Reschedule approved backlog: **1**
- Review blocked drafts: **1**
- Review draft posts: **2**
- Review scheduled approvals: **1**
- Verify music sites: **7**

## Top Actions

### Review blocked drafts
- **[blocked] Review TikTok draft for Twelve Dollars**
  - Why: Executor setup is not ready for this draft.
  - Detail: Executor credentials or platform setup are not ready.
  - Missing secrets: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
  - Public posting approved: `False`
  - Command: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-TIKTOK --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-TIKTOK --refresh-admin`

### Review scheduled approvals
- **[high] Preview checked scheduled approval batch**
  - Why: Scheduled executor records are blocked until reviewed approval is applied.
  - Detail: Review all passing rows first. The checked batch excludes rows with failed review checks.
  - Command: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-258 FP-AUTO-261 --dry-run`
  - Apply after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-258 FP-AUTO-261 --refresh-admin`

### Reschedule approved backlog
- **[high] Preview reschedule for approved past-due posts**
  - Why: Approved posts are past due; preview a new schedule before any apply step.
  - Detail: Preview first. Apply refuses rows with known executor blockers unless blockers are fixed or --allow-blocked is used after deliberate review.
  - Command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-21T10:00:00+09:00' --spacing-hours 24`
  - Apply after review: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-21T10:00:00+09:00' --spacing-hours 24 --apply --refresh-admin`

### Repair executor
- **[high] Fix TikTok executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Missing worker secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. TikTok public posting approval is false. Local secret source is also missing: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. Complete TikTok OAuth/public posting setup locally, then push secrets and refresh Admin.
  - Missing secrets: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
  - Missing locally: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
  - Local source: `secrets/social_api.env`
  - Public posting approved: `False`
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - Apply repair after preview: `python3 scripts/push_social_worker_secrets.py TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN && python3 scripts/refresh_promo_admin.py`

### Review draft posts
- **[medium] Review YouTube Community draft for Twelve Dollars**
  - Why: Draft is scheduled within 72 hours.
  - Detail: YouTube Community posts are copy-ready manual workflow.
  - Command: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --refresh-admin`
- **[medium] Review YouTube Community draft for Analog Myth**
  - Why: Draft is scheduled within 72 hours.
  - Detail: YouTube Community posts are copy-ready manual workflow.
  - Command: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --refresh-admin`

### Verify music sites
- **[medium] Re-check Twelve Dollars on Spotify**
  - Why: Public store links should be checked until DistroKid exposes them.
  - Detail: Searches public web results for Spotify album URLs, then validates exact-title candidates with Spotify oEmbed. Latest snapshot found no public URL; keep this pending until DistroKid exposes the release.
  - Latest snapshot checked: `2026-06-19T23:43:42.534174Z`
  - Command: `python3 scripts/search_spotify_release.py --artist 'Lily Roo' --title 'Twelve Dollars' --out 'data/store-verification/twelve-dollars/spotify_release_snapshot.json'`
- **[medium] Re-check Twelve Dollars on Apple Music**
  - Why: Public store links should be checked until DistroKid exposes them.
  - Detail: Uses the public iTunes Search API; if it finds the release, copy release_url into data/distrokid_release_status.json. Latest snapshot found no public URL; keep this pending until DistroKid exposes the release.
  - Latest snapshot checked: `2026-06-19T23:43:44.331902Z`
  - Command: `python3 scripts/capture_apple_music_release.py --artist 'Lily Roo' --title 'Twelve Dollars' --out 'data/store-verification/twelve-dollars/apple_music_release_snapshot.json'`
- **[medium] Re-check Twelve Dollars on HyperFollow**
  - Why: Public store links should be checked until DistroKid exposes them.
  - Detail: Captures the public HyperFollow store buttons; confirm the guessed URL if DistroKid used a different slug. Latest snapshot found no public URL; keep this pending until DistroKid exposes the release.
  - Latest snapshot checked: `2026-06-19T23:43:44.693284Z`
  - Command: `python3 scripts/capture_hyperfollow_store_links.py --url 'https://distrokid.com/hyperfollow/lilyroo/twelve-dollars' --out 'data/store-verification/twelve-dollars/hyperfollow_store_links_snapshot.json'`
- **[medium] Re-check Analog Myth on Spotify**
  - Why: Public store links should be checked as the July 1 release approaches.
  - Detail: Searches public web results for Spotify album URLs, then validates exact-title candidates with Spotify oEmbed. Latest snapshot found no public URL; keep this pending until DistroKid exposes the release.
  - Latest snapshot checked: `2026-06-19T23:43:44.750461Z`
  - Command: `python3 scripts/search_spotify_release.py --artist 'Lily Roo' --title 'Analog Myth' --out 'data/store-verification/analog-myth/spotify_release_snapshot.json'`
- **[medium] Re-check Analog Myth on Apple Music**
  - Why: Public store links should be checked as the July 1 release approaches.
  - Detail: Uses the public iTunes Search API; if it finds the release, copy release_url into data/distrokid_release_status.json. Latest snapshot found no public URL; keep this pending until DistroKid exposes the release.
  - Latest snapshot checked: `2026-06-19T23:43:46.535618Z`
  - Command: `python3 scripts/capture_apple_music_release.py --artist 'Lily Roo' --title 'Analog Myth' --out 'data/store-verification/analog-myth/apple_music_release_snapshot.json'`
- **[medium] Re-check Analog Myth on YouTube Music**
  - Why: Public store links should be checked as the July 1 release approaches.
  - Detail: Searches public web results for YouTube Music watch URLs, then validates the public title. Latest snapshot found no public URL; keep this pending until DistroKid exposes the release.
  - Latest snapshot checked: `2026-06-19T23:43:46.590983Z`
  - Command: `python3 scripts/search_youtube_music_release.py --artist 'Lily Roo' --title 'Analog Myth' --out 'data/store-verification/analog-myth/youtube_music_release_snapshot.json'`

## Guardrails
- This packet does not publish, approve, apply, or post anything.
- Review copy before running approval commands.
- Apply commands only move already-approved rows into the local/live queue; they do not directly post externally.
