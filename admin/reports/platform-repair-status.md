# Platform Repair Status - Lily Roo

Generated: 2026-06-20T09:45:34.569471Z

## Summary
- Platform fixes: **1**
- Blocked rows: **1**
- Preview commands: **1**
- Apply commands: **0**
- Checklist items: **4**
- Checklist blocked: **3**
- Platforms: **TikTok**

## Repair Checklist
- **TikTok** (`FP-AUTO-264`)
  - Status: `blocked`; reason: `tiktok_credentials_missing`
  - Repair: Missing worker secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. TikTok public posting approval is false. Local secret source is also missing: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. Complete TikTok OAuth/public posting setup locally, then push secrets and refresh Admin.
  - Missing secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN
  - Missing locally: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN
  - Local source: `secrets/social_api.env`
  - Setup preflight: `blocked`; blocked checks: `4`
  - Rebuild setup preflight: `python3 scripts/build_tiktok_setup_preflight.py`
  - Preflight report: `admin/reports/tiktok-setup-preflight.md`
  - Checklist:
    - `blocked` Worker secrets: Missing remote worker secret(s): TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. Command: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
    - `blocked` Local secret source: secrets/social_api.env is missing: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN.
    - `blocked` Public posting approval: Platform readiness says public posting approval is false.
    - `review` Refresh verification: After repair, refresh admin so readiness, scheduler, blocker, and backlog state update together. Command: `python3 scripts/refresh_promo_admin.py`
  - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - Blocked apply command: `python3 scripts/push_social_worker_secrets.py TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN && python3 scripts/refresh_promo_admin.py`
  - Apply blocked by: local_secret_source_missing:TIKTOK_CLIENT_KEY,TIKTOK_CLIENT_SECRET,TIKTOK_REFRESH_TOKEN, public_posting_approval_not_confirmed

## Guardrails
- This report does not push secrets, reconnect accounts, approve posts, or publish posts.
- Run preview/check commands before any repair apply command.
- Re-run the safe admin refresh after repairs so backlog and readiness state update together.
