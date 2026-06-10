# Promo Operations Packet - Lily Roo

Generated: 2026-06-10T01:54:46.705293Z

## Summary
- Actions: **20**
- User review: **6**
- Platform fixes: **2**
- Store checks: **7**
- Manual metric updates: **5**
- Safe apply commands ready: **0**
- Urgency: **blocked: 1, high: 3, low: 5, medium: 11**

## Phase Counts
- Fill manual metrics: **5**
- Repair executor: **2**
- Review blocked drafts: **1**
- Review draft posts: **5**
- Verify music sites: **7**

## Top Actions

### Review blocked drafts
- **[blocked] Review TikTok draft for Twelve Dollars**
  - Why: Executor setup is not ready for this draft.
  - Detail: Executor credentials or platform setup are not ready.
  - Command: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-TIKTOK --refresh-admin`

### Repair executor
- **[high] Fix TikTok executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Command: `LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_social_executions.py`
- **[high] Fix Instagram executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Instagram posting could not resolve instagram_business_account; reconnect or set IG_BUSINESS_ACCOUNT_ID.
  - Command: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`

### Review draft posts
- **[high] Review X draft for Twelve Dollars**
  - Why: Draft is scheduled within 24 hours.
  - Detail: Ready after approval.
  - Command: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-X --refresh-admin`
- **[medium] Review Instagram draft for Twelve Dollars**
  - Why: Draft is scheduled within 72 hours.
  - Detail: Ready after approval.
  - Command: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM --refresh-admin`
- **[medium] Review Facebook draft for Twelve Dollars**
  - Why: Auto draft is ready once reviewed and approved.
  - Detail: Ready after approval.
  - Command: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-FACEBOOK --refresh-admin`
- **[medium] Review YouTube Community draft for Twelve Dollars**
  - Why: Manual copy is ready for human posting workflow.
  - Detail: YouTube Community posts are copy-ready manual workflow.
  - Command: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --refresh-admin`
- **[medium] Review YouTube Community draft for Analog Myth**
  - Why: Manual copy is ready for human posting workflow.
  - Detail: YouTube Community posts are copy-ready manual workflow.
  - Command: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --refresh-admin`

### Verify music sites
- **[medium] Verify Twelve Dollars on Spotify**
  - Why: Public store links should be checked until DistroKid exposes them.
  - Command: `open 'https://open.spotify.com/search/twelve%20dollars%20Lily%20Roo/albums' && python3 scripts/capture_spotify_release.py --release-url SPOTIFY_ALBUM_URL --out 'data/store-verification/twelve-dollars/spotify_release_snapshot.json'`
- **[medium] Verify Twelve Dollars on Apple Music**
  - Why: Public store links should be checked until DistroKid exposes them.
  - Command: `python3 scripts/capture_apple_music_release.py --artist 'Lily Roo' --title 'Twelve Dollars' --out 'data/store-verification/twelve-dollars/apple_music_release_snapshot.json'`
- **[medium] Verify Twelve Dollars on HyperFollow**
  - Why: Public store links should be checked until DistroKid exposes them.
  - Command: `python3 scripts/capture_hyperfollow_store_links.py --url 'https://distrokid.com/hyperfollow/lilyroo/twelve-dollars' --out 'data/store-verification/twelve-dollars/hyperfollow_store_links_snapshot.json'`
- **[medium] Verify Analog Myth on Spotify**
  - Why: Public store links should be checked as the July 1 release approaches.
  - Command: `open 'https://open.spotify.com/search/analog%20myth%20Lily%20Roo/albums' && python3 scripts/capture_spotify_release.py --release-url SPOTIFY_ALBUM_URL --out 'data/store-verification/analog-myth/spotify_release_snapshot.json'`

## Guardrails
- This packet does not publish, approve, apply, or post anything.
- Review copy before running approval commands.
- Apply commands only move already-approved rows into the local/live queue; they do not directly post externally.
