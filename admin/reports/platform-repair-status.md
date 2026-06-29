# Platform Repair Status - Lily Roo

Generated: 2026-06-29T21:20:06.326987Z

## Summary
- Platform fixes: **5**
- Blocked rows: **5**
- Preview commands: **5**
- Apply commands: **0**
- Checklist items: **11**
- Checklist blocked: **1**
- Platforms: **Facebook, Instagram**

## Repair Checklist
- **Instagram** (`FP-AUTO-272`)
  - Status: `blocked`; reason: `instagram_business_account_unresolved`
  - Repair: Worker cannot resolve instagram_business_account from FB_PAGE_ID. Local secret source is missing: IG_BUSINESS_ACCOUNT_ID. Set IG_BUSINESS_ACCOUNT_ID from Meta Business/Instagram Graph, push it to the Worker, then recapture readiness.
  - Missing locally: IG_BUSINESS_ACCOUNT_ID
  - Local source: `secrets/social_api.env`
  - Checklist:
    - `pass` Worker secrets: Worker readiness snapshot reports required secrets present.
    - `blocked` Local secret source: secrets/social_api.env is missing: IG_BUSINESS_ACCOUNT_ID.
    - `review` Refresh verification: After repair, refresh admin so readiness, scheduler, blocker, and backlog state update together. Command: `python3 scripts/refresh_promo_admin.py`
  - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run IG_BUSINESS_ACCOUNT_ID`
  - Blocked apply command: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
  - Apply blocked by: local_secret_source_missing:IG_BUSINESS_ACCOUNT_ID
- **Facebook** (`FP-AUTO-265`)
  - Status: `failed`; reason: `max_attempts_exceeded`
  - Error: Facebook blocked Page publishing until identity is confirmed in the Facebook app.
  - Repair: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
  - Checklist:
    - `pass` Worker secrets: Worker readiness snapshot reports required secrets present.
    - `review` Refresh verification: After repair, refresh admin so readiness, scheduler, blocker, and backlog state update together. Command: `python3 scripts/refresh_promo_admin.py`
  - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-265`
  - Verify before retry reset: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-265`
  - Preview retry reset after platform repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-265`
  - Apply retry reset after platform repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-265 --apply`
  - Retry reset note: Run the dry-run verification command first. Apply the retry reset only when the worker reports the row is executable.
- **Facebook** (`FP-AUTO-268`)
  - Status: `failed`; reason: `max_attempts_exceeded`
  - Error: Facebook blocked Page publishing until identity is confirmed in the Facebook app.
  - Repair: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
  - Checklist:
    - `pass` Worker secrets: Worker readiness snapshot reports required secrets present.
    - `review` Refresh verification: After repair, refresh admin so readiness, scheduler, blocker, and backlog state update together. Command: `python3 scripts/refresh_promo_admin.py`
  - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-268`
  - Verify before retry reset: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-268`
  - Preview retry reset after platform repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-268`
  - Apply retry reset after platform repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-268 --apply`
  - Retry reset note: Run the dry-run verification command first. Apply the retry reset only when the worker reports the row is executable.
- **Facebook** (`FP-AUTO-273`)
  - Status: `failed`; reason: `max_attempts_exceeded`
  - Error: Facebook blocked Page publishing until identity is confirmed in the Facebook app.
  - Repair: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
  - Checklist:
    - `pass` Worker secrets: Worker readiness snapshot reports required secrets present.
    - `review` Refresh verification: After repair, refresh admin so readiness, scheduler, blocker, and backlog state update together. Command: `python3 scripts/refresh_promo_admin.py`
  - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-273`
  - Verify before retry reset: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-273`
  - Preview retry reset after platform repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-273`
  - Apply retry reset after platform repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-273 --apply`
  - Retry reset note: Run the dry-run verification command first. Apply the retry reset only when the worker reports the row is executable.
- **Facebook** (`FP-STORY-ANALOG-MYTH-FACEBOOK-ARCHIVE-CTA`)
  - Status: `failed`; reason: `max_attempts_exceeded`
  - Error: Facebook blocked Page publishing until identity is confirmed in the Facebook app.
  - Repair: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
  - Checklist:
    - `pass` Worker secrets: Worker readiness snapshot reports required secrets present.
    - `review` Refresh verification: After repair, refresh admin so readiness, scheduler, blocker, and backlog state update together. Command: `python3 scripts/refresh_promo_admin.py`
  - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-STORY-ANALOG-MYTH-FACEBOOK-ARCHIVE-CTA`
  - Verify before retry reset: `python3 scripts/check_social_executor_dry_run.py --post-id FP-STORY-ANALOG-MYTH-FACEBOOK-ARCHIVE-CTA`
  - Preview retry reset after platform repair: `python3 scripts/reset_social_execution_state.py FP-STORY-ANALOG-MYTH-FACEBOOK-ARCHIVE-CTA`
  - Apply retry reset after platform repair: `python3 scripts/reset_social_execution_state.py FP-STORY-ANALOG-MYTH-FACEBOOK-ARCHIVE-CTA --apply`
  - Retry reset note: Run the dry-run verification command first. Apply the retry reset only when the worker reports the row is executable.

## Guardrails
- This report does not push secrets, reconnect accounts, approve posts, or publish posts.
- Run preview/check commands before any repair apply command.
- Re-run the safe admin refresh after repairs so backlog and readiness state update together.
