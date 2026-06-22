# TikTok Setup Preflight - Lily Roo

Generated: 2026-06-22T11:25:36.854292Z

## Summary
- Status: **blocked**
- Posting mode: **api**
- API strategy confirmed: **True**
- Checks: **12**
- Blocked checks: **7**
- Ready to push worker secrets: **False**
- Ready to upload inbox drafts: **False**
- Ready to post publicly: **False**
- Local posting helper uses refresh token: **True**
- First TikTok asset ready for upload mode: **True** (`FP-AUTO-264`)
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

## What We Need From Tod
- Status: **blocked_until_user_input**
- Answer: Yes, fix the TikTok connector after the current manual YouTube evidence loop; it unlocks the short-video growth format.
- Needed inputs: **3**
- Next safe action: `python3 scripts/tiktok_oauth_handoff.py`
- First growth row unblocked: `FP-AUTO-264`
- Format unblocked: Short video clip + platform-native CTA
- **Add Lily Roo TikTok developer app values locally.** (`tiktok_developer_app_credentials`)
  - Values needed: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REDIRECT_URI, TIKTOK_REFRESH_TOKEN`
  - Safe storage: `secrets/social_api.env`
  - Why: The connector cannot generate an OAuth URL, exchange a code, or refresh TikTok access without these app values.
  - Next command: `python3 scripts/tiktok_oauth_handoff.py --print-auth-url --posting-mode upload`
- **Authorize the Lily Roo TikTok account after the OAuth URL is generated.** (`authorize_lily_roo_tiktok_account`)
  - Values needed: `short-lived TikTok authorization code`
  - Safe storage: `secrets/social_api.env`
  - Why: The refresh token is created only after the Lily Roo account authorizes the app with the requested scopes.
  - Next command: `python3 scripts/tiktok_oauth_handoff.py --exchange-code CODE --apply --posting-mode upload`
- **Confirm whether Lily Roo TikTok has public Content Posting API approval and PUBLIC_TO_EVERYONE posting is allowed.** (`public_posting_approval`)
  - Values needed: `TIKTOK_PUBLIC_POSTING_APPROVED=true confirmation`
  - Safe storage: `Worker variable via guarded approval helper`
  - Why: Direct public TikTok publishing must stay blocked until this approval is explicit.
  - Next command: `python3 scripts/set_tiktok_public_posting_approval.py --approved`
- Codex can do now:
  - Keep TikTok blockers visible in admin/status output.
  - Run safe preflight and dry-run helpers.
  - Push upload-mode connector secrets after local TikTok values exist and the dry-run is reviewed.
  - Refresh admin and validation after the connector state changes.

## Credential Handoff
- Status: **needs_local_values**
- Required names: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
- Handoff template: `data/tiktok_secret_handoff_template.env`
- OAuth helper: `scripts/tiktok_oauth_handoff.py`
- Requested OAuth scopes: `user.info.basic, video.upload`
- Direct post OAuth scopes: `user.info.basic, video.upload, video.publish`
- Scope strategy: Request only video.upload for the first inbox-draft connector path; add video.publish only after direct public posting approval exists.
- Local secret env: `secrets/social_api.env`
- Local secret env exists: **False**
- Initialize local secret env: `mkdir -p ../secrets && test -f ../secrets/social_api.env || cp data/tiktok_secret_handoff_template.env ../secrets/social_api.env`
- Missing locally: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
- Missing for auth URL: `TIKTOK_CLIENT_KEY, TIKTOK_REDIRECT_URI`
- Missing for token exchange: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REDIRECT_URI`
- Missing in worker: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
- Brand content disclosure: **False**
- Worker posting mode: **upload**
- Brand organic disclosure: **True**
- AIGC label enabled: **True**
- OAuth preview: `python3 scripts/tiktok_oauth_handoff.py`
- OAuth auth URL: `python3 scripts/tiktok_oauth_handoff.py --print-auth-url --posting-mode upload`
- OAuth code exchange: `python3 scripts/tiktok_oauth_handoff.py --exchange-code CODE --apply --posting-mode upload`
- Dry-run first: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
- Apply upload-mode secrets after review: `not available until local secrets exist`
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
  - data/tiktok_setup_preflight.json reports first_tiktok_asset.ready_for_upload_mode true.
  - data/tiktok_setup_preflight.json reports ready_to_upload_drafts true for the upload-mode connector path.
  - data/platform_repair_status.json no longer lists TikTok as blocked by missing credentials.

## Checks
- **local_secret_env_file**: `waiting`
  - Initialize secrets/social_api.env from the blank handoff template before adding TikTok app values.
  - Command: `mkdir -p ../secrets && test -f ../secrets/social_api.env || cp data/tiktok_secret_handoff_template.env ../secrets/social_api.env`
- **oauth_authorization_url**: `blocked`
  - secrets/social_api.env is missing auth URL values: TIKTOK_CLIENT_KEY, TIKTOK_REDIRECT_URI.
  - Command: `python3 scripts/tiktok_oauth_handoff.py --print-auth-url --posting-mode upload`
- **oauth_token_exchange**: `blocked`
  - secrets/social_api.env is missing token exchange values: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REDIRECT_URI.
  - Command: `python3 scripts/tiktok_oauth_handoff.py --exchange-code CODE --apply --posting-mode upload`
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
- Generate OAuth auth URL: `python3 scripts/tiktok_oauth_handoff.py --print-auth-url --posting-mode upload`
- Exchange OAuth code after authorization: `python3 scripts/tiktok_oauth_handoff.py --exchange-code CODE --apply --posting-mode upload`
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
- Public posting approval must be confirmed before direct public TikTok posting is treated as ready.
