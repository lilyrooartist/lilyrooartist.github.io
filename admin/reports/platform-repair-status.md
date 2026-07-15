# Platform Repair Status - Lily Roo

Generated: 2026-07-15T17:19:13.786725Z

## Summary
- Platform fixes: **2**
- Blocked rows: **2**
- Preview commands: **2**
- Apply commands: **0**
- Checklist items: **4**
- Checklist blocked: **0**
- Platforms: **Facebook**

## Repair Checklist
- **Facebook** (`FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-FACEBOOK`)
  - Status: `failed`; reason: `max_attempts_exceeded`
  - Error: Facebook Reel hosted upload failed (422): {"debug_info":{"retriable":false,"type":"FileUrlProcessingError","message":"Unable to fetch media from URL, got status code: 403 Restricted by robots.txt"}}
  - Repair: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
  - Checklist:
    - `pass` Worker secrets: Worker readiness snapshot reports required secrets present.
    - `review` Refresh verification: After repair, refresh admin so readiness, scheduler, blocker, and backlog state update together. Command: `python3 scripts/refresh_promo_admin.py`
  - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-FACEBOOK`
  - Verify before retry reset: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-FACEBOOK`
  - Preview retry reset after platform repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-FACEBOOK`
  - Apply retry reset after platform repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-FACEBOOK --apply`
  - Retry reset note: Run the dry-run verification command first. Apply the retry reset only when the worker reports the row is executable.
- **Facebook** (`FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-FACEBOOK`)
  - Status: `failed`; reason: `max_attempts_exceeded`
  - Error: Facebook Reel hosted upload failed (422): {"debug_info":{"retriable":false,"type":"FileUrlProcessingError","message":"Unable to fetch media from URL, got status code: 403 Restricted by robots.txt"}}
  - Repair: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
  - Checklist:
    - `pass` Worker secrets: Worker readiness snapshot reports required secrets present.
    - `review` Refresh verification: After repair, refresh admin so readiness, scheduler, blocker, and backlog state update together. Command: `python3 scripts/refresh_promo_admin.py`
  - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-FACEBOOK`
  - Verify before retry reset: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-FACEBOOK`
  - Preview retry reset after platform repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-FACEBOOK`
  - Apply retry reset after platform repair: `python3 scripts/reset_social_execution_state.py FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-FACEBOOK --apply`
  - Retry reset note: Run the dry-run verification command first. Apply the retry reset only when the worker reports the row is executable.

## Guardrails
- This report does not push secrets, reconnect accounts, approve posts, or publish posts.
- Run preview/check commands before any repair apply command.
- Re-run the safe admin refresh after repairs so backlog and readiness state update together.
