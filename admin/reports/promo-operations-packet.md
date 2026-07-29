# Promo Operations Packet - Lily Roo

Generated: 2026-07-29T16:48:21.036442Z

## Summary
- Actions: **22**
- User review: **0**
- Platform fixes: **13**
- Scheduled approval batches: **0**
- Manual distribution actions: **0**
- Experiment result actions: **1**
- Store checks: **4**
- Manual metric updates: **2**
- Safe apply commands ready: **0**
- Urgency: **blocked: 1, high: 15, low: 2, medium: 4**

## Phase Counts
- Collect experiment results: **1**
- Fill manual metrics: **2**
- Measure active brand campaign: **1**
- Repair executor: **13**
- Reschedule approved backlog: **1**
- Verify music sites: **4**

## Top Actions

### Reschedule approved backlog
- **[blocked] Preview reschedule for approved past-due posts**
  - Why: All approved past-due posts are behind executor/platform repair gates; fix those before rescheduling.
  - Detail: Preview first. Normal apply is hidden until known executor/platform blockers clear; override requires deliberate review.
  - Command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-30T10:00:00+00:00' --spacing-hours 24`

### Repair executor
- **[high] Fix YouTube executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: API request failed (400): {"error":"invalid_grant","error_description":"Token has been expired or revoked."}
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-09-NO-MORTGAGE-LYRIC-PUNCH-LINE-YOUTUBE`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-09-NO-MORTGAGE-LYRIC-PUNCH-LINE-YOUTUBE`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-09-NO-MORTGAGE-LYRIC-PUNCH-LINE-YOUTUBE --apply`
- **[high] Fix YouTube executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: API request failed (400): {"error":"invalid_grant","error_description":"Token has been expired or revoked."}
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-08-SPILLING-THE-TEA-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-08-SPILLING-THE-TEA-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-08-SPILLING-THE-TEA-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE --apply`
- **[high] Fix Facebook executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Facebook Reel hosted upload failed (422): {"debug_info":{"retriable":false,"type":"FileUrlProcessingError","message":"Unable to fetch media from URL, got status code: 403 Restricted by robots.txt"}}
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-07-SPILLING-THE-TEA-VISUAL-STORY-FACEBOOK`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-07-SPILLING-THE-TEA-VISUAL-STORY-FACEBOOK`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-07-SPILLING-THE-TEA-VISUAL-STORY-FACEBOOK --apply`
- **[high] Fix YouTube executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: API request failed (400): {"error":"invalid_grant","error_description":"Token has been expired or revoked."}
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-07-SPILLING-THE-TEA-VISUAL-STORY-YOUTUBE`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-07-SPILLING-THE-TEA-VISUAL-STORY-YOUTUBE`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-07-SPILLING-THE-TEA-VISUAL-STORY-YOUTUBE --apply`
- **[high] Fix Facebook executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Facebook Reel hosted upload failed (422): {"debug_info":{"retriable":false,"type":"FileUrlProcessingError","message":"Unable to fetch media from URL, got status code: 403 Restricted by robots.txt"}}
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-06-SPILLING-THE-TEA-RELATABLE-SITUATION-FACEBOOK`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-06-SPILLING-THE-TEA-RELATABLE-SITUATION-FACEBOOK`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-06-SPILLING-THE-TEA-RELATABLE-SITUATION-FACEBOOK --apply`
- **[high] Fix YouTube executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: API request failed (400): {"error":"invalid_grant","error_description":"Token has been expired or revoked."}
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-06-SPILLING-THE-TEA-RELATABLE-SITUATION-YOUTUBE`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-06-SPILLING-THE-TEA-RELATABLE-SITUATION-YOUTUBE`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-06-SPILLING-THE-TEA-RELATABLE-SITUATION-YOUTUBE --apply`
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

## Guardrails
- This packet does not publish, approve, apply, or post anything.
- Review copy before running approval commands.
- Apply commands only move already-approved rows into the local/live queue; they do not directly post externally.
