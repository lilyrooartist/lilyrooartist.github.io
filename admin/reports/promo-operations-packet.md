# Promo Operations Packet - Lily Roo

Generated: 2026-06-29T15:09:58.539795Z

## Summary
- Actions: **17**
- User review: **0**
- Platform fixes: **5**
- Scheduled approval batches: **1**
- Manual distribution actions: **0**
- Experiment result actions: **1**
- Store checks: **7**
- Manual metric updates: **2**
- Safe apply commands ready: **0**
- Urgency: **high: 8, low: 2, medium: 7**

## Phase Counts
- Collect experiment results: **1**
- Fill manual metrics: **2**
- Repair executor: **5**
- Reschedule approved backlog: **1**
- Review scheduled approvals: **1**
- Verify music sites: **7**

## Top Actions

### Review scheduled approvals
- **[high] Preview checked scheduled approval batch**
  - Why: Scheduled executor records are blocked until reviewed approval is applied.
  - Detail: Review all passing rows first. The checked batch excludes rows with failed review checks.
  - Decision manifest: ready `FP-AUTO-259`; held `none`
  - Review runbook: **5** step(s), **1** checklist row(s)
  - Decision guardrail: Only ready_to_approve decisions may be applied through --checked-batch; held rows require repair first.
  - Approval impact: 1 checked change(s); 1 auto row(s), 0 manual row(s); held `none`
  - Command: `python3 scripts/update_scheduled_post_approval.py --checked-batch --dry-run`
  - Apply after review: `python3 scripts/update_scheduled_post_approval.py --checked-batch --refresh-admin`

### Reschedule approved backlog
- **[high] Preview clear approved backlog row**
  - Why: Approved posts are past due; preview a new schedule before any apply step.
  - Detail: Preview the first unblocked approved backlog row; blocked rows stay held behind their repair gates.
  - Command: `python3 scripts/reschedule_scheduled_posts.py --id FP-AUTO-258 --start-at '2026-06-30T10:00:00-04:00' --spacing-hours 24`

### Repair executor
- **[high] Fix Facebook executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Facebook blocked Page publishing until identity is confirmed in the Facebook app.
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-273`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-273`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-273 --apply`
- **[high] Fix Instagram executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Worker cannot resolve instagram_business_account from FB_PAGE_ID. Local secret source is missing: IG_BUSINESS_ACCOUNT_ID. Set IG_BUSINESS_ACCOUNT_ID from Meta Business/Instagram Graph, push it to the Worker, then recapture readiness.
  - Missing locally: `IG_BUSINESS_ACCOUNT_ID`
  - Local source: `secrets/social_api.env`
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run IG_BUSINESS_ACCOUNT_ID`
  - Apply repair after preview: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
- **[high] Fix YouTube executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: API request failed (400): {"error":"invalid_grant","error_description":"Bad Request"}
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-SHORT-ANALOG-MYTH-YOUTUBE-SHORTS-CTA`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-SHORT-ANALOG-MYTH-YOUTUBE-SHORTS-CTA`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-SHORT-ANALOG-MYTH-YOUTUBE-SHORTS-CTA --apply`
- **[high] Fix Facebook executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Facebook blocked Page publishing until identity is confirmed in the Facebook app.
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-265`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-265`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-265 --apply`
- **[high] Fix Facebook executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Facebook blocked Page publishing until identity is confirmed in the Facebook app.
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-268`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-268`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-268 --apply`

### Collect experiment results
- **[high] Collect experiment result metrics**
  - Why: 7 logged experiment post(s) have 29 result field(s) waiting; these results rank repeatable formats.
  - Detail: Fill measured result values with evidence notes, preview the import, then apply only after review.
  - Command: `python3 scripts/update_experiment_results.py --from-wide-csv data/experiment_result_entry_wide_template.csv --dry-run`
  - Packet: `admin/reports/experiment-result-clipboard.md`
  - Metric cards: **7**; pending fields: **29**
  - Measurement priorities: **12**
  - Wide entry CSV: `data/experiment_result_entry_wide_template.csv`
  - Preview result import: `python3 scripts/update_experiment_results.py --from-wide-csv data/experiment_result_entry_wide_template.csv --dry-run`

### Verify music sites
- **[medium] Re-check Twelve Dollars on Spotify**
  - Why: Public store links should be checked until DistroKid exposes them.
  - Detail: Searches public web results for Spotify album URLs, then validates exact-title candidates with Spotify oEmbed. Latest snapshot found no public URL; next recommended re-check after 2026-06-30T15:09:48.795544+00:00. Status: waiting_for_release_propagation.
  - Latest snapshot checked: `2026-06-29T15:09:48.795544+00:00`
  - Command: `python3 scripts/search_spotify_release.py --artist 'Lily Roo' --title 'Twelve Dollars' --out 'data/store-verification/twelve-dollars/spotify_release_snapshot.json'`
- **[medium] Re-check Twelve Dollars on Apple Music**
  - Why: Public store links should be checked until DistroKid exposes them.
  - Detail: Uses the public iTunes Search API; if it finds the release, copy release_url into data/distrokid_release_status.json. Latest snapshot found no public URL; next recommended re-check after 2026-06-30T15:09:49.849061+00:00. Status: waiting_for_release_propagation.
  - Latest snapshot checked: `2026-06-29T15:09:49.849061+00:00`
  - Command: `python3 scripts/capture_apple_music_release.py --artist 'Lily Roo' --title 'Twelve Dollars' --out 'data/store-verification/twelve-dollars/apple_music_release_snapshot.json'`
- **[medium] Re-check Twelve Dollars on HyperFollow**
  - Why: Public store links should be checked until DistroKid exposes them.
  - Detail: Captures the public HyperFollow store buttons; confirm the guessed URL if DistroKid used a different slug. Latest snapshot found no public URL; next recommended re-check after 2026-06-30T15:09:50.244075+00:00. Status: waiting_for_release_propagation.
  - Latest snapshot checked: `2026-06-29T15:09:50.244075+00:00`
  - Command: `python3 scripts/capture_hyperfollow_store_links.py --url 'https://distrokid.com/hyperfollow/lilyroo/twelve-dollars' --out 'data/store-verification/twelve-dollars/hyperfollow_store_links_snapshot.json'`
- **[medium] Re-check Analog Myth on Spotify**
  - Why: Public store links should be checked as the July 1 release approaches.
  - Detail: Searches public web results for Spotify album URLs, then validates exact-title candidates with Spotify oEmbed. Latest snapshot found no public URL; next recommended re-check after 2026-06-30T15:09:50.322430+00:00. Status: waiting_for_release_propagation.
  - Latest snapshot checked: `2026-06-29T15:09:50.322430+00:00`
  - Command: `python3 scripts/search_spotify_release.py --artist 'Lily Roo' --title 'Analog Myth' --out 'data/store-verification/analog-myth/spotify_release_snapshot.json'`

## Guardrails
- This packet does not publish, approve, apply, or post anything.
- Review copy before running approval commands.
- Apply commands only move already-approved rows into the local/live queue; they do not directly post externally.
