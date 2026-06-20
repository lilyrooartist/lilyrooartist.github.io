# TikTok Repair Runbook - Lily Roo

Generated: 2026-06-20T05:58:27.120248Z

## Summary
- Status: **blocked**
- Phases: **6**
- Steps: **6**
- Blocked steps: **6**
- Public posting approved: **False**
- Ready to apply worker secrets: **False**
- Ready to clear backlog gate: **False**

## Sequence
- **Collect credentials - Add TikTok OAuth credentials locally**: `blocked`
  - Populate the local social API env file with the required TikTok refresh credential names. Values stay local and are never written to generated reports.
  - Blocked by: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN
- **Confirm approval - Confirm public posting approval**: `blocked`
  - Set TikTok public posting approval only after Lily Roo is approved for public TikTok posting and PUBLIC_TO_EVERYONE is intentionally allowed.
  - Blocked by: TIKTOK_PUBLIC_POSTING_APPROVED
- **Preview push - Dry-run worker secret push**: `blocked`
  - Preview the exact secret names that would be pushed to the worker before any apply command is available.
  - Blocked by: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
- **Apply push - Push worker secrets after review**: `blocked`
  - Run the apply command only after local credentials exist and public posting approval is confirmed.
  - Blocked by: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN, TIKTOK_PUBLIC_POSTING_APPROVED
- **Verify repair - Recapture executor readiness**: `blocked`
  - After applying secrets, recapture worker readiness and rebuild the admin packets so platform repair, blocker, handoff, and backlog state agree.
  - Blocked by: apply_worker_secret_push
  - Command: `python3 scripts/refresh_promo_admin.py`
- **Clear gate - Clear TikTok backlog gate**: `blocked`
  - Once readiness is clean, rerun the backlog reschedule preview and apply the approved row only if the gate reports safe apply available.
  - Blocked by: worker_refresh_credentials, public_posting_approval

## Guardrails
- This runbook does not push secrets, approve public posting, publish posts, or clear backlog rows.
- Use the dry-run secret push before any apply command.
- Do not run a TikTok backlog apply until fresh admin evidence shows TikTok readiness is clean.
- Secret values are never written to this runbook; only required names, missing names, and presence-derived readiness are recorded.
