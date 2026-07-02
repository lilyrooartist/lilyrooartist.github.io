# Platform Repair Status - Lily Roo

Generated: 2026-07-02T01:22:30.673889Z

## Summary
- Platform fixes: **5**
- Blocked rows: **5**
- Preview commands: **5**
- Apply commands: **0**
- Checklist items: **15**
- Checklist blocked: **5**
- Platforms: **Instagram, TikTok**

## Repair Checklist
- **Instagram** (`FP-AUTO-272`)
  - Status: `skipped`; reason: `analog_myth_launch_day`
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
- **Instagram** (`FP-AUTO-277`)
  - Status: `skipped`; reason: `analog_myth_launch_day`
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
- **Instagram** (`FP-AUTO-282`)
  - Status: `skipped`; reason: `analog_myth_launch_day`
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
- **TikTok** (`FP-AUTO-279`)
  - Status: `skipped`; reason: `analog_myth_launch_day`
  - Repair: TikTok direct public posting approval is false, but upload-draft mode can proceed after credentials. Complete TikTok OAuth setup, push upload-mode secrets, then refresh Admin.
  - Setup preflight: `blocked`; blocked checks: `1`
  - Rebuild setup preflight: `python3 scripts/build_tiktok_setup_preflight.py`
  - Preflight report: `admin/reports/tiktok-setup-preflight.md`
  - Checklist:
    - `pass` Worker secrets: Worker readiness snapshot reports required secrets present.
    - `blocked` Direct public posting approval: Direct public posting approval is false; TikTok upload-draft mode can still proceed after credentials.
    - `review` Refresh verification: After repair, refresh admin so readiness, scheduler, blocker, and backlog state update together. Command: `python3 scripts/refresh_promo_admin.py`
  - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - Blocked apply command: `python3 scripts/push_social_worker_secrets.py TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN && python3 scripts/refresh_promo_admin.py`
  - Apply blocked by: public_posting_approval_not_confirmed_for_direct_posting
- **TikTok** (`FP-AUTO-284`)
  - Status: `skipped`; reason: `analog_myth_launch_day`
  - Repair: TikTok direct public posting approval is false, but upload-draft mode can proceed after credentials. Complete TikTok OAuth setup, push upload-mode secrets, then refresh Admin.
  - Setup preflight: `blocked`; blocked checks: `1`
  - Rebuild setup preflight: `python3 scripts/build_tiktok_setup_preflight.py`
  - Preflight report: `admin/reports/tiktok-setup-preflight.md`
  - Checklist:
    - `pass` Worker secrets: Worker readiness snapshot reports required secrets present.
    - `blocked` Direct public posting approval: Direct public posting approval is false; TikTok upload-draft mode can still proceed after credentials.
    - `review` Refresh verification: After repair, refresh admin so readiness, scheduler, blocker, and backlog state update together. Command: `python3 scripts/refresh_promo_admin.py`
  - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - Blocked apply command: `python3 scripts/push_social_worker_secrets.py TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN && python3 scripts/refresh_promo_admin.py`
  - Apply blocked by: public_posting_approval_not_confirmed_for_direct_posting

## Guardrails
- This report does not push secrets, reconnect accounts, approve posts, or publish posts.
- Run preview/check commands before any repair apply command.
- Re-run the safe admin refresh after repairs so backlog and readiness state update together.
