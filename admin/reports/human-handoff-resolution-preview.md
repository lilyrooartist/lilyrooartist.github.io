# Human Handoff Resolution Preview - Lily Roo

Generated: 2026-07-02T01:10:12.745720Z

## Summary
- Worksheet rows: **8**
- Executed previews: **8**
- Skipped previews: **0**
- Status counts: `{"input_missing": 5, "preview_ok": 3}`
- Policy: Only python3 scripts/* commands with --dry-run, or reschedule previews without --apply, are executed.
- Guardrail: This preview runner never executes apply, refresh-admin, PUBLIC_URL placeholder, non-python, or unsupported commands.

## Previews
- **backlog-reschedule** (`preview_ok`)
  - Phase: `Backlog recovery`; input needed: `clearance_confirmation`
  - Safety: `safe_preview` (reschedule_preview_command)
  - Command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-02T10:00:00-04:00' --spacing-hours 24`
  - Output: Rows selected: 0 | Dry run only. Re-run with --apply to write the schedule.
  - Guardrail: Normal apply stays hidden until known executor/platform blockers clear.
- **platform-setup-FP-AUTO-272** (`input_missing`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `safe_preview` (dry_run_command)
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run IG_BUSINESS_ACCOUNT_ID`
  - Output: ERROR: IG_BUSINESS_ACCOUNT_ID is missing from secrets/social_api.env
  - Guardrail: Push worker secrets only after local platform setup is complete.
- **platform-setup-FP-AUTO-277** (`input_missing`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `safe_preview` (dry_run_command)
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run IG_BUSINESS_ACCOUNT_ID`
  - Output: ERROR: IG_BUSINESS_ACCOUNT_ID is missing from secrets/social_api.env
  - Guardrail: Push worker secrets only after local platform setup is complete.
- **platform-setup-FP-AUTO-279** (`preview_ok`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `safe_preview` (dry_run_command)
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - Output: would update TIKTOK_CLIENT_KEY (16 characters loaded locally) | would update TIKTOK_CLIENT_SECRET (32 characters loaded locally) | would update TIKTOK_REFRESH_TOKEN (72 characters loaded locally)
  - Guardrail: Run the TikTok preflight before pushing secrets; push upload-mode secrets only after local OAuth setup is complete. Keep direct public posting blocked until approval is confirmed.
- **platform-setup-FP-AUTO-282** (`input_missing`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `safe_preview` (dry_run_command)
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run IG_BUSINESS_ACCOUNT_ID`
  - Output: ERROR: IG_BUSINESS_ACCOUNT_ID is missing from secrets/social_api.env
  - Guardrail: Push worker secrets only after local platform setup is complete.
- **platform-setup-FP-AUTO-284** (`preview_ok`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `safe_preview` (dry_run_command)
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - Output: would update TIKTOK_CLIENT_KEY (16 characters loaded locally) | would update TIKTOK_CLIENT_SECRET (32 characters loaded locally) | would update TIKTOK_REFRESH_TOKEN (72 characters loaded locally)
  - Guardrail: Run the TikTok preflight before pushing secrets; push upload-mode secrets only after local OAuth setup is complete. Keep direct public posting blocked until approval is confirmed.
- **manual-metrics-priority-2** (`input_missing`)
  - Phase: `Manual metrics`; input needed: `private_metric_values`
  - Safety: `safe_preview` (dry_run_command)
  - Command: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Output: No metric assignments supplied. Add platform.metric=value args or fill new_value cells and use --from-csv.
  - Guardrail: Only import nonnegative numeric values copied from the named source; leave unknown values blank instead of guessing.
- **manual-metrics-priority-3** (`input_missing`)
  - Phase: `Manual metrics`; input needed: `private_metric_values`
  - Safety: `safe_preview` (dry_run_command)
  - Command: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Output: No metric assignments supplied. Add platform.metric=value args or fill new_value cells and use --from-csv.
  - Guardrail: Only import nonnegative numeric values copied from the named source; leave unknown values blank instead of guessing.

## Guardrails
- This preview does not approve, post, publish, push secrets, log URLs, import metrics, or refresh admin state.
- Missing values and blocked platform setup are reported as input_missing, not repaired automatically.
