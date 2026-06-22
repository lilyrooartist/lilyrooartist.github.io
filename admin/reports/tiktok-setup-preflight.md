# TikTok Setup Preflight - Lily Roo

Generated: 2026-06-22T06:28:09.114928Z

## Summary
- Status: **blocked**
- Posting mode: **api**
- API strategy confirmed: **True**
- Checks: **11**
- Blocked checks: **7**
- Ready to push worker secrets: **False**
- Ready to post publicly: **False**
- Local posting helper uses refresh token: **True**
- Local post preview: `python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --dry-run`
- Local draft upload preview: `python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --mode upload --dry-run`
- Earliest TikTok API path: video.upload inbox draft; final public URL still requires human publish and URL logging.
- Local public posting approval confirmed: **False**
- Public posting approved: **False**
- Default privacy: **PUBLIC_TO_EVERYONE**
- Worker posting mode: **upload**
- Brand content disclosure: **False**
- Brand organic disclosure: **True**
- AIGC label enabled: **True**

## Credential Handoff
- Status: **needs_local_values**
- Required names: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
- Handoff template: `data/tiktok_secret_handoff_template.env`
- OAuth helper: `scripts/tiktok_oauth_handoff.py`
- Requested OAuth scopes: `user.info.basic, video.upload, video.publish`
- Missing locally: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
- Missing for auth URL: `TIKTOK_CLIENT_KEY, TIKTOK_REDIRECT_URI`
- Missing for token exchange: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REDIRECT_URI`
- Missing in worker: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
- Brand content disclosure: **False**
- Worker posting mode: **upload**
- Brand organic disclosure: **True**
- AIGC label enabled: **True**
- OAuth preview: `python3 scripts/tiktok_oauth_handoff.py`
- OAuth auth URL: `python3 scripts/tiktok_oauth_handoff.py --print-auth-url`
- OAuth code exchange: `python3 scripts/tiktok_oauth_handoff.py --exchange-code CODE --apply`
- Dry-run first: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
- Apply after review: `not available until local secrets exist`
- Public posting approval preview: `python3 scripts/set_tiktok_public_posting_approval.py --approved`
- Public posting approval apply: `not available until local approval is confirmed`
- Public posting approval deploy: `not available until local approval is confirmed`
- Post-apply verification:
  - `python3 scripts/capture_executor_readiness.py`
  - `python3 scripts/refresh_promo_admin.py`
  - `python3 scripts/validate_content_system.py`
- Completion evidence:
  - data/tiktok_setup_preflight.json reports ready_to_push_worker_secrets true.
  - data/executor_readiness_snapshot.json reports TikTok refresh configuration present.
  - data/platform_repair_status.json no longer lists TikTok as blocked by missing credentials.

## Checks
- **oauth_authorization_url**: `blocked`
  - secrets/social_api.env is missing auth URL values: TIKTOK_CLIENT_KEY, TIKTOK_REDIRECT_URI.
  - Command: `python3 scripts/tiktok_oauth_handoff.py --print-auth-url`
- **oauth_token_exchange**: `blocked`
  - secrets/social_api.env is missing token exchange values: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REDIRECT_URI.
  - Command: `python3 scripts/tiktok_oauth_handoff.py --exchange-code CODE --apply`
- **local_refresh_credentials**: `blocked`
  - secrets/social_api.env is missing: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN.
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
- **local_posting_token_path**: `blocked`
  - Local TikTok posting helper needs TIKTOK_ACCESS_TOKEN or refresh credentials.
  - Command: `python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --dry-run`
- **worker_refresh_credentials**: `blocked`
  - Worker readiness reports missing secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN.
  - Command: `python3 scripts/capture_executor_readiness.py`
- **worker_token_path**: `blocked`
  - Worker has neither access token nor refresh credentials.
  - Command: `python3 scripts/capture_executor_readiness.py`
- **public_posting_approval**: `blocked`
  - TikTok public posting approval is not enabled.
  - Command: `python3 scripts/set_tiktok_public_posting_approval.py --approved`
- **default_privacy**: `pass`
  - TikTok default privacy is PUBLIC_TO_EVERYONE.
- **commercial_disclosure_defaults**: `pass`
  - TikTok disclosure defaults are brand_content_toggle=False, brand_organic_toggle=True.
- **aigc_label_default**: `pass`
  - TikTok AI-generated-content label default is True.
- **admin_refresh_after_repair**: `waiting`
  - After credentials and public posting approval are fixed, refresh Admin to recapture readiness, execution, blocker, handoff, and consistency state.
  - Command: `python3 scripts/refresh_promo_admin.py`

## Commands
- Preview OAuth handoff: `python3 scripts/tiktok_oauth_handoff.py`
- Generate OAuth auth URL: `python3 scripts/tiktok_oauth_handoff.py --print-auth-url`
- Exchange OAuth code after authorization: `python3 scripts/tiktok_oauth_handoff.py --exchange-code CODE --apply`
- Preview local secrets: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
- Preview inbox draft upload: `python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --mode upload --dry-run`
- Push after local credentials are present: `not available until local secrets exist`
- Preview public posting approval flag: `python3 scripts/set_tiktok_public_posting_approval.py --approved`
- Apply public posting approval flag: `not available until local approval is confirmed`
- Deploy public posting approval flag: `not available until local approval is confirmed`
- Refresh after repair: `python3 scripts/refresh_promo_admin.py`

## Guardrails
- This preflight does not push secrets, approve posts, publish posts, or write credentials.
- Secret values are redacted; only presence and readiness booleans are recorded.
- Public posting approval must be confirmed before TikTok auto-posting is treated as ready.
