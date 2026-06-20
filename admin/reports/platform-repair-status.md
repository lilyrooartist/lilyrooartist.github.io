# Platform Repair Status - Lily Roo

Generated: 2026-06-20T01:25:13.078847Z

## Summary
- Platform fixes: **1**
- Blocked rows: **1**
- Preview commands: **1**
- Apply commands: **1**
- Platforms: **TikTok**

## Repair Checklist
- **TikTok** (`FP-AUTO-264`)
  - Status: `blocked`; reason: `tiktok_credentials_missing`
  - Repair: Missing worker secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. TikTok public posting approval is false. Complete TikTok OAuth/public posting setup, push secrets, then refresh Admin.
  - Missing secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN
  - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - Apply after review: `python3 scripts/push_social_worker_secrets.py TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN && python3 scripts/refresh_promo_admin.py`

## Guardrails
- This report does not push secrets, reconnect accounts, approve posts, or publish posts.
- Run preview/check commands before any repair apply command.
- Re-run the safe admin refresh after repairs so backlog and readiness state update together.
