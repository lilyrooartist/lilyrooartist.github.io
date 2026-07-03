# Platform Repair Status - Lily Roo

Generated: 2026-07-03T09:21:29.594447Z

## Summary
- Platform fixes: **1**
- Blocked rows: **1**
- Preview commands: **1**
- Apply commands: **0**
- Checklist items: **4**
- Checklist blocked: **2**
- Platforms: **TikTok**

## Repair Checklist
- **TikTok** (`FP-AUTO-264`)
  - Status: `needs_fix`; reason: `tiktok_setup_preflight_blocked`
  - Repair: Local upload-mode OAuth credentials missing: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. Complete TikTok OAuth setup locally, then push upload-mode secrets and refresh Admin.
  - Missing locally: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN
  - Local source: `secrets/social_api.env`
  - Setup preflight: `blocked`; blocked checks: `5`
  - Rebuild setup preflight: `python3 scripts/build_tiktok_setup_preflight.py`
  - Preflight report: `admin/reports/tiktok-setup-preflight.md`
  - Checklist:
    - `pass` Worker secrets: Worker readiness snapshot reports required secrets present.
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
