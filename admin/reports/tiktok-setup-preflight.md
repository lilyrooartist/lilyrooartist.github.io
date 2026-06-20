# TikTok Setup Preflight - Lily Roo

Generated: 2026-06-20T09:46:13.378778Z

## Summary
- Status: **blocked**
- Checks: **6**
- Blocked checks: **4**
- Ready to push worker secrets: **False**
- Ready to post publicly: **False**
- Public posting approved: **False**
- Default privacy: **PUBLIC_TO_EVERYONE**

## Credential Handoff
- Status: **needs_local_values**
- Required names: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
- Handoff template: `data/tiktok_secret_handoff_template.env`
- Missing locally: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
- Missing in worker: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
- Dry-run first: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
- Apply after review: `not available until local secrets exist`
- Post-apply verification:
  - `python3 scripts/capture_executor_readiness.py`
  - `python3 scripts/refresh_promo_admin.py`
  - `python3 scripts/validate_content_system.py`
- Completion evidence:
  - data/tiktok_setup_preflight.json reports ready_to_push_worker_secrets true.
  - data/executor_readiness_snapshot.json reports TikTok refresh configuration present.
  - data/platform_repair_status.json no longer lists TikTok as blocked by missing credentials.

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
