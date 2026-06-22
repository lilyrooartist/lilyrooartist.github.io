# Promo Operations Packet - Lily Roo

Generated: 2026-06-22T06:02:35.714861Z

## Summary
- Actions: **17**
- User review: **3**
- Platform fixes: **4**
- Scheduled approval batches: **0**
- Store checks: **7**
- Manual metric updates: **2**
- Safe apply commands ready: **0**
- Urgency: **blocked: 1, high: 5, low: 2, medium: 9**

## Phase Counts
- Fill manual metrics: **2**
- Repair executor: **4**
- Reschedule approved backlog: **1**
- Review blocked drafts: **1**
- Review draft posts: **2**
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

### Reschedule approved backlog
- **[high] Preview clear approved backlog row**
  - Why: Approved posts are past due; preview a new schedule before any apply step.
  - Detail: Preview the first unblocked approved backlog row; blocked rows stay held behind their repair gates.
  - Command: `python3 scripts/reschedule_scheduled_posts.py --id FP-AUTO-258 --start-at '2026-06-23T10:00:00+08:00' --spacing-hours 24`

### Repair executor
- **[high] Fix Facebook executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Facebook blocked Page publishing until identity is confirmed in the Facebook app.
  - Command: `python3 scripts/check_facebook_publishing.py --post-id 'FP-AUTO-265' --check-worker-dry-run`
- **[high] Fix Instagram executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Instagram posting could not resolve instagram_business_account; reconnect or set IG_BUSINESS_ACCOUNT_ID.
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`
  - Apply repair after preview: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-PLAN-TWELVE-DOLLARS-INSTAGRAM --apply`
- **[high] Fix Instagram executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Instagram posting could not resolve instagram_business_account; reconnect or set IG_BUSINESS_ACCOUNT_ID.
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-263`
  - Apply repair after preview: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-263`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-263 --apply`
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
  - Why: Manual copy is ready for human posting workflow.
  - Detail: YouTube Community posts are copy-ready manual workflow.
  - Command: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --refresh-admin`

### Verify music sites
- **[medium] Re-check Twelve Dollars on Spotify**
  - Why: Public store links should be checked until DistroKid exposes them.
  - Detail: Searches public web results for Spotify album URLs, then validates exact-title candidates with Spotify oEmbed. Latest snapshot found no public URL; next recommended re-check after 2026-06-23T06:01:28.759862+00:00. Status: waiting_for_release_propagation.
  - Latest snapshot checked: `2026-06-22T06:01:28.759862+00:00`
  - Command: `python3 scripts/search_spotify_release.py --artist 'Lily Roo' --title 'Twelve Dollars' --out 'data/store-verification/twelve-dollars/spotify_release_snapshot.json'`
- **[medium] Re-check Twelve Dollars on Apple Music**
  - Why: Public store links should be checked until DistroKid exposes them.
  - Detail: Uses the public iTunes Search API; if it finds the release, copy release_url into data/distrokid_release_status.json. Latest snapshot found no public URL; next recommended re-check after 2026-06-23T06:01:48.902322+00:00. Status: waiting_for_release_propagation.
  - Latest snapshot checked: `2026-06-22T06:01:48.902322+00:00`
  - Command: `python3 scripts/capture_apple_music_release.py --artist 'Lily Roo' --title 'Twelve Dollars' --out 'data/store-verification/twelve-dollars/apple_music_release_snapshot.json'`
- **[medium] Re-check Twelve Dollars on HyperFollow**
  - Why: Public store links should be checked until DistroKid exposes them.
  - Detail: Captures the public HyperFollow store buttons; confirm the guessed URL if DistroKid used a different slug. Latest snapshot found no public URL; next recommended re-check after 2026-06-23T06:01:49.425726+00:00. Status: waiting_for_release_propagation.
  - Latest snapshot checked: `2026-06-22T06:01:49.425726+00:00`
  - Command: `python3 scripts/capture_hyperfollow_store_links.py --url 'https://distrokid.com/hyperfollow/lilyroo/twelve-dollars' --out 'data/store-verification/twelve-dollars/hyperfollow_store_links_snapshot.json'`
- **[medium] Re-check Analog Myth on Spotify**
  - Why: Public store links should be checked as the July 1 release approaches.
  - Detail: Searches public web results for Spotify album URLs, then validates exact-title candidates with Spotify oEmbed. Latest snapshot found no public URL; next recommended re-check after 2026-06-23T06:01:49.497095+00:00. Status: waiting_for_release_propagation.
  - Latest snapshot checked: `2026-06-22T06:01:49.497095+00:00`
  - Command: `python3 scripts/search_spotify_release.py --artist 'Lily Roo' --title 'Analog Myth' --out 'data/store-verification/analog-myth/spotify_release_snapshot.json'`

## Guardrails
- This packet does not publish, approve, apply, or post anything.
- Review copy before running approval commands.
- Apply commands only move already-approved rows into the local/live queue; they do not directly post externally.
