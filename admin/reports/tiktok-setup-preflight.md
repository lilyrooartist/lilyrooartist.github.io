# TikTok Setup Preflight - Lily Roo

Generated: 2026-07-02T01:10:12.309730Z

## Summary
- Status: **blocked**
- Posting mode: **api**
- API strategy confirmed: **True**
- Checks: **12**
- Blocked checks: **1**
- Ready to push worker secrets: **True**
- Ready to upload inbox drafts: **False**
- Ready to post publicly: **False**
- Local posting helper uses refresh token: **True**
- First TikTok asset ready for upload mode: **False** (`FP-AUTO-264`)
- Local post preview: `python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --dry-run`
- Local draft upload preview: `python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --mode upload --dry-run`
- Earliest TikTok API path: video.upload inbox draft; final public URL still requires human publish and URL logging.
- Upload-mode lane: **asset_blocked**; public approval required: **False**
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
- Answer: Yes, fix the TikTok connector after the current manual YouTube evidence loop; it unlocks the short-video growth format.
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
  - Run safe preflight and dry-run helpers.
  - Push upload-mode connector secrets after local TikTok values exist and the dry-run is reviewed.
  - Refresh admin and validation after the connector state changes.

## Upload-Mode Repair Ladder
- Immediate lane status: **asset_blocked**
- First post ID: `FP-AUTO-264`
- Scopes: `user.info.basic, video.upload`
- Public posting approval required now: **False**
- Human finish required: **True**
- Handoff: TikTok API creates an inbox draft; Lily Roo reviews/publishes in TikTok, then the public URL is logged back into the promo engine.
- Direct public lane: **deferred_until_tiktok_approval**
- Direct public guardrail: Do not treat direct public TikTok publishing as ready until TikTok approval is explicit and the guarded Worker flag is deployed.
- After-input command sequence:
  - `generate_oauth_url`: after TIKTOK_CLIENT_KEY and TIKTOK_REDIRECT_URI are present locally -> `python3 scripts/tiktok_oauth_handoff.py --print-auth-url --posting-mode upload`
  - `exchange_authorization_code`: immediately after Lily Roo authorizes the TikTok OAuth URL -> `python3 scripts/tiktok_oauth_handoff.py --exchange-code CODE --apply --posting-mode upload`
  - `preview_worker_secret_push`: after local refresh credentials exist -> `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - `preview_first_upload_draft`: after the secret push dry-run is reviewed and credentials are available to the helper -> `python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --mode upload --dry-run`
  - `refresh_admin_evidence`: after credentials or Worker state changes -> `python3 scripts/refresh_promo_admin.py`

## Credential Handoff
- Status: **ready_to_push**
- Required names: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
- Handoff template: `data/tiktok_secret_handoff_template.env`
- OAuth helper: `scripts/tiktok_oauth_handoff.py`
- Requested OAuth scopes: `user.info.basic, video.upload`
- Direct post OAuth scopes: `user.info.basic, video.upload, video.publish`
- Scope strategy: Request only video.upload for the first inbox-draft connector path; add video.publish only after direct public posting approval exists.
- Local secret env: `secrets/social_api.env`
- Local secret env prepared: **True**
- Runtime local env file exists: **True**
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
- OAuth auth URL: `python3 scripts/tiktok_oauth_handoff.py --print-auth-url --posting-mode upload`
- OAuth code exchange: `python3 scripts/tiktok_oauth_handoff.py --exchange-code CODE --apply --posting-mode upload`
- Dry-run first: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
- Apply upload-mode secrets after review: `python3 scripts/push_social_worker_secrets.py TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN && python3 scripts/refresh_promo_admin.py`
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
- **local_secret_env_file**: `pass`
  - Local secret env exists at secrets/social_api.env.
- **oauth_authorization_url**: `pass`
  - TikTok OAuth authorization URL can be generated locally.
  - Command: `python3 scripts/tiktok_oauth_handoff.py --print-auth-url --posting-mode upload`
- **oauth_token_exchange**: `pass`
  - TikTok OAuth authorization codes can be exchanged locally.
  - Command: `python3 scripts/tiktok_oauth_handoff.py --exchange-code CODE --apply --posting-mode upload`
- **local_refresh_credentials**: `pass`
  - Local refresh credentials are present.
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
- **local_posting_token_path**: `pass`
  - Local TikTok posting helper can use an existing access token.
  - Command: `python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --dry-run`
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
- Generate OAuth auth URL: `python3 scripts/tiktok_oauth_handoff.py --print-auth-url --posting-mode upload`
- Exchange OAuth code after authorization: `python3 scripts/tiktok_oauth_handoff.py --exchange-code CODE --apply --posting-mode upload`
- Preview local secrets: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
- Preview inbox draft upload: `python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --mode upload --dry-run`
- Push after local credentials are present: `python3 scripts/push_social_worker_secrets.py TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN && python3 scripts/refresh_promo_admin.py`
- Preview public posting approval flag: `python3 scripts/set_tiktok_public_posting_approval.py --approved`
- Apply public posting approval flag: `not available until local approval is confirmed`
- Deploy public posting approval flag: `not available until local approval is confirmed`
- Refresh after repair: `python3 scripts/refresh_promo_admin.py`

## Guardrails
- This preflight does not push secrets, approve posts, publish posts, or write credentials.
- Secret values are redacted; only presence and readiness booleans are recorded.
- Public posting approval must be confirmed before direct public TikTok posting is treated as ready.
