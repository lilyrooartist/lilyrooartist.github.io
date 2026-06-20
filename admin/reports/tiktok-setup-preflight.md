# TikTok Setup Preflight - Lily Roo

Generated: 2026-06-20T07:50:25.343597Z

## Summary
- Status: **blocked**
- Checks: **6**
- Blocked checks: **4**
- Ready to push worker secrets: **False**
- Ready to post publicly: **False**
- Public posting approved: **False**
- Default privacy: **PUBLIC_TO_EVERYONE**

## Checks
- **local_refresh_credentials**: `blocked`
  - secrets/social_api.env is missing: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN.
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
- **worker_refresh_credentials**: `blocked`
  - Worker readiness reports missing secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN.
  - Command: `python3 scripts/capture_executor_readiness.py`
- **worker_token_path**: `blocked`
  - Worker has neither access token nor refresh credentials.
  - Command: `python3 scripts/capture_executor_readiness.py`
- **public_posting_approval**: `blocked`
  - TikTok public posting approval is not enabled.
- **default_privacy**: `pass`
  - TikTok default privacy is PUBLIC_TO_EVERYONE.
- **admin_refresh_after_repair**: `waiting`
  - After credentials and public posting approval are fixed, refresh Admin to recapture readiness, execution, blocker, handoff, and consistency state.
  - Command: `python3 scripts/refresh_promo_admin.py`

## Commands
- Preview local secrets: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
- Push after local credentials are present: `not available until local secrets exist`
- Refresh after repair: `python3 scripts/refresh_promo_admin.py`

## Guardrails
- This preflight does not push secrets, approve posts, publish posts, or write credentials.
- Secret values are redacted; only presence and readiness booleans are recorded.
- Public posting approval must be confirmed before TikTok auto-posting is treated as ready.
