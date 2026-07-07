# TikTok Repair Runbook - Lily Roo

Generated: 2026-07-07T20:16:58.609697Z

## Summary
- Status: **ready_for_backlog_clearance**
- Posting mode: **api**
- API strategy confirmed: **True**
- Phases: **9**
- Steps: **10**
- Blocked steps: **1**
- Local public posting approval confirmed: **False**
- Public posting approved: **False**
- Worker posting mode: **direct**
- Brand content disclosure: **False**
- Brand organic disclosure: **True**
- AIGC label enabled: **True**
- Local posting helper uses refresh token: **True**
- Local post preview: `python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --mode direct --dry-run`
- Local draft upload preview: `not in active plan`
- Earliest TikTok API path: Direct public Content Posting API after explicit TikTok approval; video.upload inbox drafts are manual-finish and excluded from the active plan.
- Upload-mode lane: **excluded_manual_finish**
- Direct public lane: **deferred_until_tiktok_approval**
- Handoff template: `data/tiktok_secret_handoff_template.env`
- Local secret env exists: **True**
- Initialize local secret env: `not needed`
- Ready to apply worker secrets: **True**
- Ready to upload inbox drafts: **False**
- Ready for direct public posting: **False**
- Ready to clear backlog gate: **True**
- Public posting approval apply: `not available until local approval is confirmed`
- Public posting approval deploy: `not available until local approval is confirmed`

## Manual-Finish Upload Lane
- First row: `FP-AUTO-264`
- First asset ready: **True**
- Public posting approval required for upload mode: **False**
- Human finish required: **True**
- Active plan allowed: **False**
- Handoff: Excluded from the active plan because TikTok inbox drafts still require human publish and URL logging.
- Direct public guardrail: Do not treat direct public TikTok publishing as ready until TikTok approval is explicit and the guarded Worker flag is deployed.
- After-input command sequence:
  - `generate_oauth_url`: after TIKTOK_CLIENT_KEY and TIKTOK_REDIRECT_URI are present locally -> `python3 scripts/tiktok_oauth_handoff.py --print-auth-url --posting-mode direct`
  - `exchange_authorization_code`: immediately after Lily Roo authorizes the TikTok OAuth URL -> `python3 scripts/tiktok_oauth_handoff.py --exchange-code CODE --apply --posting-mode direct`
  - `preview_worker_secret_push`: after local refresh credentials exist -> `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - `refresh_admin_evidence`: after credentials or Worker state changes -> `python3 scripts/refresh_promo_admin.py`

## Sequence
- **Prepare local env - Create the local TikTok secret env file**: `pass`
  - Create the local social API env file from the blank TikTok handoff template before adding TikTok app values. The command is non-overwriting, so an existing env file is preserved.
- **Collect credentials - Add TikTok OAuth credentials locally**: `pass`
  - Use the redacted TikTok handoff template to populate the local social API env file with the TikTok client key, client secret, redirect URI, and refresh-token path. Values stay local and are never written to generated reports.
  - Command: `python3 scripts/tiktok_oauth_handoff.py`
- **Authorize account - Generate TikTok authorization URL**: `ready`
  - Create the TikTok authorization URL for the direct-public scope bundle only after approval is explicit, open it, and sign in as the Lily Roo TikTok account. The returned code is short-lived and should be exchanged immediately.
  - Command: `python3 scripts/tiktok_oauth_handoff.py --print-auth-url --posting-mode direct`
- **Authorize account - Exchange authorization code**: `ready`
  - Exchange the returned TikTok authorization code for local access and refresh tokens using the same direct-public scope path. The helper writes token values only with --apply and never prints them.
  - Command: `python3 scripts/tiktok_oauth_handoff.py --exchange-code CODE --apply --posting-mode direct`
- **Confirm approval - Confirm public posting approval**: `blocked`
  - Set TikTok public posting approval only after Lily Roo is approved for public TikTok posting and PUBLIC_TO_EVERYONE is intentionally allowed. If approval is confirmed locally, apply and deploy the guarded Worker var update.
  - Blocked by: TIKTOK_PUBLIC_POSTING_APPROVED
- **Preview push - Dry-run worker secret push**: `ready`
  - Preview the exact secret names that would be pushed to the worker before any apply command is available.
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
- **Preview local post - Dry-run local TikTok post helper**: `ready`
  - Confirm the local posting helper can resolve media and use refresh credentials without requiring a manually copied access token.
  - Command: `python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --mode direct --dry-run`
- **Apply push - Push direct-public worker secrets after review**: `ready`
  - Run the apply command only after local refresh credentials exist and direct public-posting approval is explicit.
- **Verify repair - Recapture executor readiness**: `waiting`
  - After applying secrets, recapture worker readiness and rebuild the admin packets so platform repair, blocker, handoff, and backlog state agree.
  - Command: `python3 scripts/capture_executor_readiness.py && python3 scripts/refresh_promo_admin.py`
- **Clear gate - Clear TikTok backlog gate**: `ready`
  - Once direct public worker readiness is clean, rerun the backlog reschedule preview and apply TikTok rows only if they can publish without manual finish.
  - Command: `python3 scripts/build_backlog_reschedule_preview.py && python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-08T10:00:00+00:00' --spacing-hours 24`

## Guardrails
- This runbook does not push secrets, approve public posting, publish posts, or clear backlog rows.
- Use the dry-run secret push before any apply command.
- Do not run a TikTok backlog apply until fresh admin evidence shows direct public TikTok posting is approved and clean.
- TikTok upload mode is diagnostic only; inbox drafts still require manual finish and are excluded from the active plan.
- Secret values are never written to this runbook; only required names, missing names, and presence-derived readiness are recorded.
