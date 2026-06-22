# Platform Repair Status - Lily Roo

Generated: 2026-06-22T10:21:55.958996Z

## Summary
- Platform fixes: **4**
- Blocked rows: **4**
- Preview commands: **4**
- Apply commands: **0**
- Checklist items: **12**
- Checklist blocked: **5**
- Platforms: **Facebook, Instagram, TikTok**

## Repair Checklist
- **Instagram** (`FP-AUTO-263`)
  - Status: `failed`; reason: `max_attempts_exceeded`
  - Error: Instagram posting could not resolve instagram_business_account; reconnect or set IG_BUSINESS_ACCOUNT_ID.
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
  - Error: Instagram posting could not resolve instagram_business_account; reconnect or set IG_BUSINESS_ACCOUNT_ID.
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
- **Facebook** (`FP-AUTO-265`)
  - Status: `failed`; reason: ``
  - Error: Facebook blocked Page publishing until identity is confirmed in the Facebook app.
  - Repair: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
  - Checklist:
    - `pass` Worker secrets: Worker readiness snapshot reports required secrets present.
    - `review` Refresh verification: After repair, refresh admin so readiness, scheduler, blocker, and backlog state update together. Command: `python3 scripts/refresh_promo_admin.py`
  - Preview/check: `python3 scripts/check_facebook_publishing.py --post-id 'FP-AUTO-265' --check-worker-dry-run`
- **TikTok** (`FP-AUTO-264`)
  - Status: `blocked`; reason: `tiktok_credentials_missing`
  - Repair: Missing worker secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. TikTok direct public posting approval is false, but upload-draft mode can proceed after credentials. Local secret source is also missing: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. Complete TikTok OAuth setup locally, then push upload-mode secrets and refresh Admin.
  - Missing secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN
  - Missing locally: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN
  - Local source: `secrets/social_api.env`
  - Setup preflight: `blocked`; blocked checks: `7`
  - Rebuild setup preflight: `python3 scripts/build_tiktok_setup_preflight.py`
  - Preflight report: `admin/reports/tiktok-setup-preflight.md`
  - Checklist:
    - `blocked` Worker secrets: Missing remote worker secret(s): TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. Command: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
    - `blocked` Local secret source: secrets/social_api.env is missing: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN.
    - `blocked` Direct public posting approval: Direct public posting approval is false; TikTok upload-draft mode can still proceed after credentials.
    - `review` Refresh verification: After repair, refresh admin so readiness, scheduler, blocker, and backlog state update together. Command: `python3 scripts/refresh_promo_admin.py`
  - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - Blocked apply command: `python3 scripts/push_social_worker_secrets.py TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN && python3 scripts/refresh_promo_admin.py`
  - Apply blocked by: local_secret_source_missing:TIKTOK_CLIENT_KEY,TIKTOK_CLIENT_SECRET,TIKTOK_REFRESH_TOKEN

## Guardrails
- This report does not push secrets, reconnect accounts, approve posts, or publish posts.
- Run preview/check commands before any repair apply command.
- Re-run the safe admin refresh after repairs so backlog and readiness state update together.
