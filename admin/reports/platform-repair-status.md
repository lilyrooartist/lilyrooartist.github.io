# Platform Repair Status - Lily Roo

Generated: 2026-06-14T14:29:51.539290Z

## Summary
- Platform fixes: **3**
- Blocked rows: **3**
- Preview commands: **3**
- Apply commands: **2**
- Platforms: **Facebook, Instagram, TikTok**

## Repair Checklist
- **Instagram** (`FP-AUTO-263`)
  - Status: `failed`; reason: `max_attempts_exceeded`
  - Error: Instagram posting could not resolve instagram_business_account; reconnect or set IG_BUSINESS_ACCOUNT_ID.
  - Repair: Reconnect the Instagram Business/Creator account to the Facebook Page or set IG_BUSINESS_ACCOUNT_ID, then push the worker secret and recapture readiness.
  - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run IG_BUSINESS_ACCOUNT_ID`
  - Apply after review: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
- **Facebook** (`FP-AUTO-265`)
  - Status: `failed`; reason: `max_attempts_exceeded`
  - Error: Facebook blocked Page publishing until identity is confirmed in the Facebook app.
  - Repair: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
  - Preview/check: `python3 scripts/check_facebook_publishing.py --post-id 'FP-AUTO-265' --check-worker-dry-run`
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
