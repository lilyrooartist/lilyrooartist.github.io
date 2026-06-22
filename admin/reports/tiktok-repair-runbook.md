# TikTok Repair Runbook - Lily Roo

Generated: 2026-06-22T11:24:41.205270Z

## Summary
- Status: **blocked**
- Posting mode: **api**
- API strategy confirmed: **True**
- Phases: **10**
- Steps: **11**
- Blocked steps: **10**
- Local public posting approval confirmed: **False**
- Public posting approved: **False**
- Worker posting mode: **upload**
- Brand content disclosure: **False**
- Brand organic disclosure: **True**
- AIGC label enabled: **True**
- Local posting helper uses refresh token: **True**
- Local post preview: `python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --dry-run`
- Local draft upload preview: `python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --mode upload --dry-run`
- Earliest TikTok API path: video.upload inbox draft; final public URL still requires human publish and URL logging.
- Handoff template: `data/tiktok_secret_handoff_template.env`
- Local secret env exists: **True**
- Initialize local secret env: `not needed`
- Ready to apply worker secrets: **False**
- Ready to upload inbox drafts: **False**
- Ready for direct public posting: **False**
- Ready to clear backlog gate: **False**
- Public posting approval apply: `not available until local approval is confirmed`
- Public posting approval deploy: `not available until local approval is confirmed`

## Sequence
- **Prepare local env - Create the local TikTok secret env file**: `pass`
  - Create the local social API env file from the blank TikTok handoff template before adding TikTok app values. The command is non-overwriting, so an existing env file is preserved.
- **Collect credentials - Add TikTok OAuth credentials locally**: `blocked`
  - Use the redacted TikTok handoff template to populate the local social API env file with the TikTok client key, client secret, redirect URI, and refresh-token path. Values stay local and are never written to generated reports.
  - Blocked by: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN
  - Command: `python3 scripts/tiktok_oauth_handoff.py`
- **Authorize account - Generate TikTok authorization URL**: `blocked`
  - Create the TikTok authorization URL for the upload-draft scope bundle, open it, and sign in as the Lily Roo TikTok account. The returned code is short-lived and should be exchanged immediately.
  - Blocked by: TIKTOK_CLIENT_KEY, TIKTOK_REDIRECT_URI
  - Command: `python3 scripts/tiktok_oauth_handoff.py --print-auth-url --posting-mode upload`
- **Authorize account - Exchange authorization code**: `blocked`
  - Exchange the returned TikTok authorization code for local access and refresh tokens using the same upload-mode scope path. The helper writes token values only with --apply and never prints them.
  - Blocked by: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REDIRECT_URI
  - Command: `python3 scripts/tiktok_oauth_handoff.py --exchange-code CODE --apply --posting-mode upload`
- **Confirm approval - Confirm public posting approval**: `blocked`
  - Set TikTok public posting approval only after Lily Roo is approved for public TikTok posting and PUBLIC_TO_EVERYONE is intentionally allowed. If approval is confirmed locally, apply and deploy the guarded Worker var update.
  - Blocked by: TIKTOK_PUBLIC_POSTING_APPROVED
- **Preview push - Dry-run worker secret push**: `blocked`
  - Preview the exact secret names that would be pushed to the worker before any apply command is available.
  - Blocked by: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
- **Preview local post - Dry-run local TikTok post helper**: `blocked`
  - Confirm the local posting helper can resolve media and use refresh credentials without requiring a manually copied access token.
  - Blocked by: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN
  - Command: `python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --dry-run`
- **Preview draft upload - Dry-run TikTok inbox draft upload**: `blocked`
  - Confirm the safer video.upload path can prepare a TikTok inbox draft before public direct-posting approval is available.
  - Blocked by: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN
  - Command: `python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --mode upload --dry-run`
- **Apply push - Push upload-mode worker secrets after review**: `blocked`
  - Run the apply command after local refresh credentials exist and the dry-run is reviewed. Public-posting approval is a separate direct-posting gate.
  - Blocked by: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN
- **Verify repair - Recapture executor readiness**: `blocked`
  - After applying secrets, recapture worker readiness and rebuild the admin packets so platform repair, blocker, handoff, and backlog state agree.
  - Blocked by: apply_worker_secret_push
  - Command: `python3 scripts/refresh_promo_admin.py`
- **Clear gate - Clear TikTok backlog gate**: `blocked`
  - Once worker readiness is clean, rerun the backlog reschedule preview and apply the approved row only if the gate reports safe apply available. Upload mode creates an inbox draft that still needs human publish and URL logging.
  - Blocked by: worker_refresh_credentials

## Guardrails
- This runbook does not push secrets, approve public posting, publish posts, or clear backlog rows.
- Use the dry-run secret push before any apply command.
- Do not run a TikTok backlog apply until fresh admin evidence shows TikTok upload readiness is clean.
- Public-posting approval is required only for direct public TikTok posting; upload mode still requires human review, publish, and URL logging.
- Secret values are never written to this runbook; only required names, missing names, and presence-derived readiness are recorded.
