# Promo Operations Packet - Lily Roo

Generated: 2026-07-21T19:53:51.335262Z

## Summary
- Actions: **16**
- User review: **0**
- Platform fixes: **7**
- Scheduled approval batches: **0**
- Manual distribution actions: **0**
- Experiment result actions: **1**
- Store checks: **4**
- Manual metric updates: **2**
- Safe apply commands ready: **0**
- Urgency: **blocked: 1, high: 9, low: 2, medium: 4**

## Phase Counts
- Collect experiment results: **1**
- Fill manual metrics: **2**
- Measure active brand campaign: **1**
- Repair executor: **7**
- Reschedule approved backlog: **1**
- Verify music sites: **4**

## Top Actions

### Reschedule approved backlog
- **[blocked] Preview reschedule for approved past-due posts**
  - Why: All approved past-due posts are behind executor/platform repair gates; fix those before rescheduling.
  - Detail: Preview first. Normal apply is hidden until known executor/platform blockers clear; override requires deliberate review.
  - Command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-22T10:00:00+00:00' --spacing-hours 24`

### Repair executor
- **[high] Fix Facebook executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Facebook Reel hosted upload failed (422): {"debug_info":{"retriable":false,"type":"FileUrlProcessingError","message":"Unable to fetch media from URL, got status code: 403 Restricted by robots.txt"}}
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-05-SPILLING-THE-TEA-LYRIC-PUNCH-LINE-FACEBOOK`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-05-SPILLING-THE-TEA-LYRIC-PUNCH-LINE-FACEBOOK`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-05-SPILLING-THE-TEA-LYRIC-PUNCH-LINE-FACEBOOK --apply`
- **[high] Fix YouTube executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: API request failed (400): {"error":"invalid_grant","error_description":"Token has been expired or revoked."}
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-05-SPILLING-THE-TEA-LYRIC-PUNCH-LINE-YOUTUBE`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-05-SPILLING-THE-TEA-LYRIC-PUNCH-LINE-YOUTUBE`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-05-SPILLING-THE-TEA-LYRIC-PUNCH-LINE-YOUTUBE --apply`
- **[high] Fix Facebook executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Facebook Reel hosted upload failed (422): {"debug_info":{"retriable":false,"type":"FileUrlProcessingError","message":"Unable to fetch media from URL, got status code: 403 Restricted by robots.txt"}}
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-FACEBOOK`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-FACEBOOK`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-FACEBOOK --apply`
- **[high] Fix YouTube executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: API request failed (400): {"error":"invalid_grant","error_description":"Token has been expired or revoked."}
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE --apply`
- **[high] Fix Facebook executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Facebook Reel hosted upload failed (422): {"debug_info":{"retriable":false,"type":"FileUrlProcessingError","message":"Unable to fetch media from URL, got status code: 403 Restricted by robots.txt"}}
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-03-SLOW-WALK-VISUAL-STORY-FACEBOOK`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-03-SLOW-WALK-VISUAL-STORY-FACEBOOK`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-03-SLOW-WALK-VISUAL-STORY-FACEBOOK --apply`
- **[high] Fix Facebook executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Facebook Reel hosted upload failed (422): {"debug_info":{"retriable":false,"type":"FileUrlProcessingError","message":"Unable to fetch media from URL, got status code: 403 Restricted by robots.txt"}}
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-FACEBOOK`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-FACEBOOK`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-FACEBOOK --apply`
- **[high] Fix Facebook executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Facebook Reel hosted upload failed (422): {"debug_info":{"retriable":false,"type":"FileUrlProcessingError","message":"Unable to fetch media from URL, got status code: 403 Restricted by robots.txt"}}
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-FACEBOOK`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-FACEBOOK`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-FACEBOOK --apply`

### Measure active brand campaign
- **[high] Connect automated brand metrics capture**
  - Why: 22 fresh Analog Myth post(s) are ready to measure once X/Meta metric credentials are connected.
  - Detail: Fresh Analog Myth posts are ready for measurement, but X/Meta result capture is waiting on API credentials. Add the missing names to ../secrets/social_api.env, use the scoped GitHub Actions secret push, then rerun the capture commands.
  - Local source: `secrets/social_api.env`
  - Command: `python3 scripts/push_github_actions_secrets.py --name FB_PAGE_ID --name META_LONG_LIVED_TOKEN --name X_ACCESS_TOKEN --name X_ACCESS_TOKEN_SECRET --name X_API_KEY --name X_API_SECRET`
  - Packet: `admin/reports/brand-growth-readout.md`

### Collect experiment results
- **[high] Collect experiment result metrics**
  - Why: 19 logged experiment post(s) have 105 result field(s) waiting; these results rank repeatable formats.
  - Detail: Fill measured result values with evidence notes, preview the import, then apply only after review.
  - Command: `python3 scripts/update_experiment_results.py --from-wide-csv data/experiment_result_entry_wide_template.csv --dry-run`
  - Packet: `admin/reports/experiment-result-clipboard.md`
  - Metric cards: **19**; pending fields: **105**
  - Measurement priorities: **12**
  - Wide entry CSV: `data/experiment_result_entry_wide_template.csv`
  - Preview result import: `python3 scripts/update_experiment_results.py --from-wide-csv data/experiment_result_entry_wide_template.csv --dry-run`

### Verify music sites
- **[medium] Re-check Twelve Dollars on Spotify**
  - Why: Public store links should be checked until DistroKid exposes them.
  - Detail: Searches public web results for Spotify album URLs, then validates exact-title candidates with Spotify oEmbed. Latest snapshot found no public URL; next recommended re-check after 2026-07-22T19:53:24.776379+00:00. Status: waiting_for_release_propagation.
  - Latest snapshot checked: `2026-07-21T19:53:24.776379+00:00`
  - Command: `python3 scripts/search_spotify_release.py --artist 'Lily Roo' --title 'Twelve Dollars' --out 'data/store-verification/twelve-dollars/spotify_release_snapshot.json'`
- **[medium] Re-check Twelve Dollars on Apple Music**
  - Why: Public store links should be checked until DistroKid exposes them.
  - Detail: Uses the public iTunes Search API; if it finds the release, copy release_url into data/distrokid_release_status.json. Latest snapshot found no public URL; next recommended re-check after 2026-07-22T19:53:26.406913+00:00. Status: waiting_for_release_propagation.
  - Latest snapshot checked: `2026-07-21T19:53:26.406913+00:00`
  - Command: `python3 scripts/capture_apple_music_release.py --artist 'Lily Roo' --title 'Twelve Dollars' --out 'data/store-verification/twelve-dollars/apple_music_release_snapshot.json'`

## Guardrails
- This packet does not publish, approve, apply, or post anything.
- Review copy before running approval commands.
- Apply commands only move already-approved rows into the local/live queue; they do not directly post externally.
