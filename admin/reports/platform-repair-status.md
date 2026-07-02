# Platform Repair Status - Lily Roo

Generated: 2026-07-02T14:30:07.961530Z

## Summary
- Platform fixes: **3**
- Blocked rows: **3**
- Preview commands: **3**
- Apply commands: **0**
- Checklist items: **9**
- Checklist blocked: **3**
- Platforms: **Instagram**

## Repair Checklist
- **Instagram** (`FP-AUTO-258`)
  - Status: `failed`; reason: `max_attempts_exceeded`
  - Error: Instagram retry cap reached; verify instagram_business_account repair before resetting execution state.
  - Repair: Worker cannot resolve instagram_business_account from FB_PAGE_ID. Local secret source is missing: IG_BUSINESS_ACCOUNT_ID. Set IG_BUSINESS_ACCOUNT_ID from Meta Business/Instagram Graph, push it to the Worker, then recapture readiness.
  - Missing locally: IG_BUSINESS_ACCOUNT_ID
  - Local source: `secrets/social_api.env`
  - Checklist:
    - `pass` Worker secrets: Worker readiness snapshot reports required secrets present.
    - `blocked` Local secret source: secrets/social_api.env is missing: IG_BUSINESS_ACCOUNT_ID.
    - `review` Refresh verification: After repair, refresh admin so readiness, scheduler, blocker, and backlog state update together. Command: `python3 scripts/refresh_promo_admin.py`
  - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-258`
  - Blocked apply command: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
  - Apply blocked by: local_secret_source_missing:IG_BUSINESS_ACCOUNT_ID
  - Verify before retry reset: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-258`
  - Preview retry reset after platform repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-258`
  - Apply retry reset after platform repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-258 --apply`
  - Retry reset note: Run the dry-run verification command first. Apply the retry reset only when the worker reports the row is executable.
- **Instagram** (`FP-AUTO-263`)
  - Status: `failed`; reason: `max_attempts_exceeded`
  - Error: Instagram retry cap reached; verify instagram_business_account repair before resetting execution state.
  - Repair: Worker cannot resolve instagram_business_account from FB_PAGE_ID. Local secret source is missing: IG_BUSINESS_ACCOUNT_ID. Set IG_BUSINESS_ACCOUNT_ID from Meta Business/Instagram Graph, push it to the Worker, then recapture readiness.
  - Missing locally: IG_BUSINESS_ACCOUNT_ID
  - Local source: `secrets/social_api.env`
  - Checklist:
    - `pass` Worker secrets: Worker readiness snapshot reports required secrets present.
    - `blocked` Local secret source: secrets/social_api.env is missing: IG_BUSINESS_ACCOUNT_ID.
    - `review` Refresh verification: After repair, refresh admin so readiness, scheduler, blocker, and backlog state update together. Command: `python3 scripts/refresh_promo_admin.py`
  - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-263`
  - Blocked apply command: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
  - Apply blocked by: local_secret_source_missing:IG_BUSINESS_ACCOUNT_ID
  - Verify before retry reset: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-263`
  - Preview retry reset after platform repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-263`
  - Apply retry reset after platform repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-263 --apply`
  - Retry reset note: Run the dry-run verification command first. Apply the retry reset only when the worker reports the row is executable.
- **Instagram** (`FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`)
  - Status: `failed`; reason: `max_attempts_exceeded`
  - Error: Instagram retry cap reached; verify instagram_business_account repair before resetting execution state.
  - Repair: Worker cannot resolve instagram_business_account from FB_PAGE_ID. Local secret source is missing: IG_BUSINESS_ACCOUNT_ID. Set IG_BUSINESS_ACCOUNT_ID from Meta Business/Instagram Graph, push it to the Worker, then recapture readiness.
  - Missing locally: IG_BUSINESS_ACCOUNT_ID
  - Local source: `secrets/social_api.env`
  - Checklist:
    - `pass` Worker secrets: Worker readiness snapshot reports required secrets present.
    - `blocked` Local secret source: secrets/social_api.env is missing: IG_BUSINESS_ACCOUNT_ID.
    - `review` Refresh verification: After repair, refresh admin so readiness, scheduler, blocker, and backlog state update together. Command: `python3 scripts/refresh_promo_admin.py`
  - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`
  - Blocked apply command: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
  - Apply blocked by: local_secret_source_missing:IG_BUSINESS_ACCOUNT_ID
  - Verify before retry reset: `python3 scripts/check_social_executor_dry_run.py --post-id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`
  - Preview retry reset after platform repair: `python3 scripts/reset_social_execution_state.py FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`
  - Apply retry reset after platform repair: `python3 scripts/reset_social_execution_state.py FP-PLAN-TWELVE-DOLLARS-INSTAGRAM --apply`
  - Retry reset note: Run the dry-run verification command first. Apply the retry reset only when the worker reports the row is executable.

## Guardrails
- This report does not push secrets, reconnect accounts, approve posts, or publish posts.
- Run preview/check commands before any repair apply command.
- Re-run the safe admin refresh after repairs so backlog and readiness state update together.
