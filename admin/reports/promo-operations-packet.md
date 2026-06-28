# Promo Operations Packet - Lily Roo

Generated: 2026-06-28T00:52:27.373579Z

## Summary
- Actions: **18**
- User review: **1**
- Platform fixes: **5**
- Scheduled approval batches: **0**
- Manual distribution actions: **1**
- Experiment result actions: **1**
- Store checks: **7**
- Manual metric updates: **2**
- Safe apply commands ready: **0**
- Urgency: **blocked: 2, high: 7, low: 2, medium: 7**

## Phase Counts
- Collect experiment results: **1**
- Fill manual metrics: **2**
- Publish manual posts: **1**
- Repair executor: **5**
- Reschedule approved backlog: **1**
- Review blocked drafts: **1**
- Verify music sites: **7**

## Top Actions

### Reschedule approved backlog
- **[blocked] Preview reschedule for approved past-due posts**
  - Why: All approved past-due posts are behind executor/platform repair gates; fix those before rescheduling.
  - Detail: Preview first. Normal apply is hidden until known executor/platform blockers clear; override requires deliberate review.
  - Command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-24T10:00:00+08:00' --spacing-hours 24`

### Review blocked drafts
- **[blocked] Review TikTok draft for Twelve Dollars**
  - Why: Executor setup is not ready for this draft.
  - Detail: Executor credentials or platform setup are not ready.
  - Public posting approved: `False`
  - Command: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-TIKTOK --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-TIKTOK --refresh-admin`

### Publish manual posts
- **[high] Post YouTube Community manual cards**
  - Why: 4 approved manual post(s) can publish now without waiting for broken auto executors.
  - Detail: Post each approved card manually, copy the real public URL, then log it with the manual distribution logger.
  - Open: https://www.youtube.com/@lilyroo.artist/community
  - Packet: `admin/reports/manual-posting-clipboard.md`
  - Postable cards: **4**
  - Pending URL logs: `FP-AUTO-270, FP-AUTO-275, FP-AUTO-280, FP-AUTO-285`
  - Preview URL logging: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv`
  - Apply URL logging after real URLs exist: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --apply --refresh-admin`

### Repair executor
- **[high] Fix TikTok executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: API request failed (403): {"error":{"code":"unaudited_client_can_only_post_to_private_accounts","message":"Please review our integration guidelines at https://developers.tiktok.com/doc/content-sharing-guidelines/","log_id":"2026062406115293
  - Public posting approved: `False`
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - Apply repair after preview: `python3 scripts/push_social_worker_secrets.py TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN && python3 scripts/refresh_promo_admin.py`
- **[high] Fix Instagram executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Instagram posting could not resolve instagram_business_account; reconnect or set IG_BUSINESS_ACCOUNT_ID.
  - Missing locally: `IG_BUSINESS_ACCOUNT_ID`
  - Local source: `secrets/social_api.env`
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-263`
  - Apply repair after preview: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-263`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-263 --apply`
- **[high] Fix YouTube executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: API request failed (400): {"error":"invalid_grant","error_description":"Token has been expired or revoked."}
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-261`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-261`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-261 --apply`
- **[high] Fix Facebook executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Facebook blocked Page publishing until identity is confirmed in the Facebook app.
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-PLAN-TWELVE-DOLLARS-FACEBOOK`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-PLAN-TWELVE-DOLLARS-FACEBOOK`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-PLAN-TWELVE-DOLLARS-FACEBOOK --apply`
- **[high] Fix Instagram executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Instagram posting could not resolve instagram_business_account; reconnect or set IG_BUSINESS_ACCOUNT_ID.
  - Missing locally: `IG_BUSINESS_ACCOUNT_ID`
  - Local source: `secrets/social_api.env`
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-258`
  - Apply repair after preview: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-258`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-258 --apply`

### Collect experiment results
- **[high] Collect experiment result metrics**
  - Why: 3 logged experiment post(s) have 5 result field(s) waiting; these results rank repeatable formats.
  - Detail: Fill measured result values with evidence notes, preview the import, then apply only after review.
  - Command: `python3 scripts/update_experiment_results.py --from-wide-csv data/experiment_result_entry_wide_template.csv --dry-run`
  - Packet: `admin/reports/experiment-result-clipboard.md`
  - Metric cards: **3**; pending fields: **5**
  - Measurement priorities: **12**
  - Wide entry CSV: `data/experiment_result_entry_wide_template.csv`
  - Preview result import: `python3 scripts/update_experiment_results.py --from-wide-csv data/experiment_result_entry_wide_template.csv --dry-run`

### Verify music sites
- **[medium] Re-check Twelve Dollars on Spotify**
  - Why: Public store links should be checked until DistroKid exposes them.
  - Detail: Searches public web results for Spotify album URLs, then validates exact-title candidates with Spotify oEmbed. Latest snapshot found no public URL; next recommended re-check after 2026-06-24T08:58:36.482600+00:00. Status: waiting_for_release_propagation.
  - Latest snapshot checked: `2026-06-23T08:58:36.482600+00:00`
  - Command: `python3 scripts/search_spotify_release.py --artist 'Lily Roo' --title 'Twelve Dollars' --out 'data/store-verification/twelve-dollars/spotify_release_snapshot.json'`
- **[medium] Re-check Twelve Dollars on Apple Music**
  - Why: Public store links should be checked until DistroKid exposes them.
  - Detail: Uses the public iTunes Search API; if it finds the release, copy release_url into data/distrokid_release_status.json. Latest snapshot found no public URL; next recommended re-check after 2026-06-24T08:58:38.981367+00:00. Status: waiting_for_release_propagation.
  - Latest snapshot checked: `2026-06-23T08:58:38.981367+00:00`
  - Command: `python3 scripts/capture_apple_music_release.py --artist 'Lily Roo' --title 'Twelve Dollars' --out 'data/store-verification/twelve-dollars/apple_music_release_snapshot.json'`
- **[medium] Re-check Twelve Dollars on HyperFollow**
  - Why: Public store links should be checked until DistroKid exposes them.
  - Detail: Captures the public HyperFollow store buttons; confirm the guessed URL if DistroKid used a different slug. Latest snapshot found no public URL; next recommended re-check after 2026-06-24T08:58:39.624071+00:00. Status: waiting_for_release_propagation.
  - Latest snapshot checked: `2026-06-23T08:58:39.624071+00:00`
  - Command: `python3 scripts/capture_hyperfollow_store_links.py --url 'https://distrokid.com/hyperfollow/lilyroo/twelve-dollars' --out 'data/store-verification/twelve-dollars/hyperfollow_store_links_snapshot.json'`

## Guardrails
- This packet does not publish, approve, apply, or post anything.
- Review copy before running approval commands.
- Apply commands only move already-approved rows into the local/live queue; they do not directly post externally.
