# TikTok Setup Preflight - Lily Roo

Generated: 2026-07-05T21:36:14.240209Z

## Summary
- Status: **blocked**
- Posting mode: **api**
- API strategy confirmed: **True**
- Checks: **12**
- Blocked checks: **1**
- Ready to push worker secrets: **False**
- Ready to upload inbox drafts: **False** (excluded from active plan because drafts require manual finish)
- Ready to post publicly: **False**
- Local posting helper uses refresh token: **True**
- First TikTok asset media ready: **True** (`FP-AUTO-264`)
- Local post preview: `python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --mode direct --dry-run`
- Local draft upload preview: `not in active plan`
- Earliest TikTok API path: Direct public Content Posting API after explicit TikTok approval; video.upload inbox drafts are manual-finish and excluded from the active plan.
- Upload-mode lane: **excluded_manual_finish**; public approval required: **False**
- Direct public lane: **deferred_until_tiktok_approval**; public approval required: **True**
- Local public posting approval confirmed: **False**
- Public posting approved: **False**
- Default privacy: **PUBLIC_TO_EVERYONE**
- Worker posting mode: **direct**
- Brand content disclosure: **False**
- Brand organic disclosure: **True**
- AIGC label enabled: **True**

## What We Need From Tod
- Status: **blocked_until_user_input**
- Answer: Keep the TikTok connector out of the active posting plan until direct public API publishing is approved; upload-draft mode is diagnostic only because it requires manual finish.
- Needed inputs: **1**
- Next safe action: `python3 scripts/set_tiktok_public_posting_approval.py --approved`
- First growth row unblocked: `FP-AUTO-264`
- Format unblocked: Short video clip + platform-native CTA
- **Confirm whether Lily Roo TikTok has public Content Posting API approval and PUBLIC_TO_EVERYONE posting is allowed.** (`public_posting_approval`)
  - Values needed: `TIKTOK_PUBLIC_POSTING_APPROVED=true confirmation`
  - Safe storage: `Worker variable via guarded approval helper`
  - Why: Direct public TikTok publishing must stay blocked until this approval is explicit.
  - Next command: `python3 scripts/set_tiktok_public_posting_approval.py --approved`
- Codex can do now:
  - Keep TikTok blockers visible in admin/status output.
  - Run safe preflight helpers.
  - Prepare direct public posting only after TikTok approval is explicit.
  - Refresh admin and validation after the connector state changes.

## Manual-Finish Upload Lane
- Immediate lane status: **excluded_manual_finish**
- First post ID: `FP-AUTO-264`
- Scopes: `user.info.basic, video.upload`
- Public posting approval required now: **False**
- Human finish required: **True**
- Handoff: Excluded from the active plan because TikTok inbox drafts still require human publish and URL logging.
- Active plan allowed: **False**
- Direct public lane: **deferred_until_tiktok_approval**
- Direct public guardrail: Do not treat direct public TikTok publishing as ready until TikTok approval is explicit and the guarded Worker flag is deployed.
- After-input command sequence:
  - `generate_oauth_url`: after TIKTOK_CLIENT_KEY and TIKTOK_REDIRECT_URI are present locally -> `python3 scripts/tiktok_oauth_handoff.py --print-auth-url --posting-mode direct`
  - `exchange_authorization_code`: immediately after Lily Roo authorizes the TikTok OAuth URL -> `python3 scripts/tiktok_oauth_handoff.py --exchange-code CODE --apply --posting-mode direct`
  - `preview_worker_secret_push`: after local refresh credentials exist -> `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - `refresh_admin_evidence`: after credentials or Worker state changes -> `python3 scripts/refresh_promo_admin.py`

## Credential Handoff
- Status: **needs_local_values**
- Required names: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
- Handoff template: `data/tiktok_secret_handoff_template.env`
- OAuth helper: `scripts/tiktok_oauth_handoff.py`
- Requested OAuth scopes: `user.info.basic, video.upload, video.publish`
- Direct post OAuth scopes: `user.info.basic, video.upload, video.publish`
- Scope strategy: Keep video.upload out of the active plan because it requires manual finish; use video.publish only after direct public posting approval exists.
- Local secret env: `secrets/social_api.env`
- Local secret env prepared: **True**
- Runtime local env file exists: **False**
- Local handoff marker: `data/tiktok_local_handoff_status.json`
- Initialize local secret env: `not needed`
- Missing locally: `none`
- Missing for auth URL: `none`
- Missing for token exchange: `none`
- Missing in worker: `none`
- Brand content disclosure: **False**
- Worker posting mode: **direct**
- Brand organic disclosure: **True**
- AIGC label enabled: **True**
- OAuth preview: `python3 scripts/tiktok_oauth_handoff.py`
- OAuth auth URL: `python3 scripts/tiktok_oauth_handoff.py --print-auth-url --posting-mode direct`
- OAuth code exchange: `python3 scripts/tiktok_oauth_handoff.py --exchange-code CODE --apply --posting-mode direct`
- Dry-run first: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
- Push direct-public secrets after review: `not available until local secrets exist and public posting approval is confirmed`
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
  - data/tiktok_setup_preflight.json reports ready_to_upload_drafts false while upload-draft posting is excluded.
  - data/tiktok_setup_preflight.json reports direct public posting only after TikTok approval is explicit.
  - data/platform_repair_status.json no longer lists TikTok as blocked by missing credentials.

## Checks
- **local_secret_env_file**: `pass`
  - Local secret env handoff is initialized at secrets/social_api.env; this runtime cannot inspect the local file.
- **oauth_authorization_url**: `remote_only`
  - This runner cannot inspect local TikTok handoff secrets, but Worker readiness reports the upload token path is configured.
  - Command: `python3 scripts/tiktok_oauth_handoff.py --print-auth-url --posting-mode direct`
- **oauth_token_exchange**: `remote_only`
  - This runner cannot inspect local TikTok handoff secrets, but Worker readiness reports the upload token path is configured.
  - Command: `python3 scripts/tiktok_oauth_handoff.py --exchange-code CODE --apply --posting-mode direct`
- **local_refresh_credentials**: `remote_only`
  - This runner cannot inspect local TikTok handoff secrets, but Worker readiness reports the upload token path is configured.
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
- **local_posting_token_path**: `remote_only`
  - This runner cannot inspect local TikTok handoff secrets, but Worker readiness reports the upload token path is configured.
  - Command: `python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --mode direct --dry-run`
- **worker_refresh_credentials**: `pass`
  - Worker readiness reports TikTok refresh credentials present.
  - Command: `python3 scripts/capture_executor_readiness.py`
- **worker_token_path**: `pass`
  - Worker has either an access token or refresh credentials available.
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
- Generate OAuth auth URL: `python3 scripts/tiktok_oauth_handoff.py --print-auth-url --posting-mode direct`
- Exchange OAuth code after authorization: `python3 scripts/tiktok_oauth_handoff.py --exchange-code CODE --apply --posting-mode direct`
- Preview local secrets: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
- Preview inbox draft upload: `not in active plan`
- Push after local credentials are present: `not available until local secrets exist`
- Preview public posting approval flag: `python3 scripts/set_tiktok_public_posting_approval.py --approved`
- Apply public posting approval flag: `not available until local approval is confirmed`
- Deploy public posting approval flag: `not available until local approval is confirmed`
- Refresh after repair: `python3 scripts/refresh_promo_admin.py`

## Guardrails
- This preflight does not push secrets, approve posts, publish posts, or write credentials.
- Secret values are redacted; only presence and readiness booleans are recorded.
- Public posting approval must be confirmed before direct public TikTok posting is treated as ready.
