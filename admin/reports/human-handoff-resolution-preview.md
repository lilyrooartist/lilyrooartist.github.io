# Human Handoff Resolution Preview - Lily Roo

Generated: 2026-06-23T08:49:09.759339Z

## Summary
- Worksheet rows: **8**
- Executed previews: **4**
- Skipped previews: **4**
- Status counts: `{"input_missing": 3, "preview_ok_with_warning": 1, "skipped": 4}`
- Policy: Only python3 scripts/* commands with --dry-run, or reschedule previews without --apply, are executed.
- Guardrail: This preview runner never executes apply, refresh-admin, PUBLIC_URL placeholder, non-python, or unsupported commands.

## Previews
- **platform-setup-FP-AUTO-258** (`skipped`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `skipped` (not_marked_preview_safe)
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-258`
  - Guardrail: Push worker secrets only after local platform setup is complete.
- **platform-setup-FP-AUTO-263** (`skipped`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `skipped` (not_marked_preview_safe)
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-263`
  - Guardrail: Push worker secrets only after local platform setup is complete.
- **platform-setup-FP-AUTO-264** (`input_missing`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `safe_preview` (dry_run_command)
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - Output: ERROR: TIKTOK_CLIENT_KEY is missing from secrets/social_api.env | ERROR: TIKTOK_CLIENT_SECRET is missing from secrets/social_api.env | ERROR: TIKTOK_REFRESH_TOKEN is missing from secrets/social_api.env
  - Guardrail: Run the TikTok preflight before pushing secrets; push upload-mode secrets only after local OAuth setup is complete. Keep direct public posting blocked until approval is confirmed.
- **platform-setup-FP-AUTO-265** (`skipped`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `skipped` (not_marked_preview_safe)
  - Command: `python3 scripts/check_facebook_publishing.py --post-id 'FP-AUTO-265' --check-worker-dry-run`
  - Guardrail: Push worker secrets only after local platform setup is complete.
- **platform-setup-FP-PLAN-TWELVE-DOLLARS-INSTAGRAM** (`skipped`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `skipped` (not_marked_preview_safe)
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`
  - Guardrail: Push worker secrets only after local platform setup is complete.
- **backlog-reschedule** (`preview_ok_with_warning`)
  - Phase: `Backlog recovery`; input needed: `clearance_confirmation`
  - Safety: `safe_preview` (reschedule_preview_command)
  - Command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-24T10:00:00+08:00' --spacing-hours 24`
  - Output: Rows selected: 2 | - FP-AUTO-258 Instagram I Learned It All in Fifteen Seconds: 2026-06-23T10:00:00+08:00 -> 2026-06-24T10:00:00+08:00 |   WARNING: known blocker: Instagram posting could not resolve instagram_business_account; reconnect or set IG_BUSINESS_ACCOUNT_ID. | - FP-AUTO-264 TikTok I Learned It All in Fifteen Seconds: 2026-06-23T10:00:00+08:00 -> 2026-06-25T10:00:00+08:00 |   WARNING: known blocker: tiktok_credentials_missing | Dry run only. Re-run with --apply to write the schedule.
  - Guardrail: Normal apply stays hidden until known executor/platform blockers clear.
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
