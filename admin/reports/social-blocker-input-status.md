# Social Blocker Input Status - Lily Roo

Generated: 2026-06-23T08:54:01.003126Z

## Summary
- Status: **missing_local_input**
- Ready groups: **0 / 5**
- Missing local input: **4**
- External action needed: **1**
- GitHub Actions missing secrets: **2**
- Local secret env exists: **True**
- Template: `data/social_blocker_secret_template.env`
- Next action: Add one of LILYROO_EXECUTOR_BEARER_TOKEN, EXECUTOR_BEARER_TOKEN, LILYROO_ADMIN_PASSWORD, ADMIN_PASSWORD to /Users/tod.famous/Documents/New project/secrets/social_api.env.

## Groups
- **Scheduler and executor auth** - `missing_local_input`
  - Required one of: LILYROO_EXECUTOR_BEARER_TOKEN, EXECUTOR_BEARER_TOKEN, LILYROO_ADMIN_PASSWORD, ADMIN_PASSWORD
  - GitHub Actions secrets: LILYROO_EXECUTOR_BEARER_TOKEN, LILYROO_ADMIN_PASSWORD
  - GitHub Actions status: missing
  - Preview GitHub secret push: `python3 scripts/push_github_actions_secrets.py`
  - Apply GitHub secret push: `python3 scripts/push_github_actions_secrets.py --apply`
  - Unblocks: Scheduler dry-run, executor readiness capture, and execution history capture.
  - Verify: `python3 scripts/capture_scheduler_dry_run.py && python3 scripts/capture_social_executions.py`
  - Next: Add one of LILYROO_EXECUTOR_BEARER_TOKEN, EXECUTOR_BEARER_TOKEN, LILYROO_ADMIN_PASSWORD, ADMIN_PASSWORD to /Users/tod.famous/Documents/New project/secrets/social_api.env.
- **Instagram business account** - `missing_local_input`
  - Required all: IG_BUSINESS_ACCOUNT_ID
  - Unblocks: Instagram executor rows after the Worker secret is pushed and readiness is recaptured.
  - Verify: `python3 scripts/check_social_executor_dry_run.py --post-id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`
  - Next: Add IG_BUSINESS_ACCOUNT_ID to /Users/tod.famous/Documents/New project/secrets/social_api.env.
- **TikTok OAuth app values** - `missing_local_input`
  - Required all: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REDIRECT_URI
  - Unblocks: TikTok OAuth authorization URL generation and authorization-code exchange.
  - Verify: `python3 scripts/tiktok_oauth_handoff.py --print-auth-url --posting-mode upload`
  - Next: Add TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REDIRECT_URI to /Users/tod.famous/Documents/New project/secrets/social_api.env.
- **TikTok upload-mode worker secrets** - `missing_local_input`
  - Required all: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN
  - Unblocks: TikTok upload-draft automation for the first ready TikTok asset.
  - Verify: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - Next: Add TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN to /Users/tod.famous/Documents/New project/secrets/social_api.env.
- **Facebook Page identity checkpoint** - `external_action_needed`
  - Unblocks: The Facebook executor row blocked by Meta identity confirmation.
  - Verify: `python3 scripts/check_facebook_publishing.py --post-id 'FP-AUTO-265' --check-worker-dry-run`
  - Next: Complete the external platform checkpoint, then rerun the verification command.

## Guardrails
- Generated files report presence only. They must never contain real secret values.
- Put real values in `../secrets/social_api.env` locally and GitHub Actions secrets where listed.
- Push Worker secrets only after local dry-runs prove the required values are present.
