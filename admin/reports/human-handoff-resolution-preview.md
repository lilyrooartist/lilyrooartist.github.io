# Human Handoff Resolution Preview - Lily Roo

Generated: 2026-06-22T06:08:21.096740Z

## Summary
- Worksheet rows: **10**
- Executed previews: **4**
- Skipped previews: **6**
- Status counts: `{"input_missing": 3, "preview_ok_with_warning": 1, "skipped": 6}`
- Policy: Only python3 scripts/* commands with --dry-run, or reschedule previews without --apply, are executed.
- Guardrail: This preview runner never executes apply, refresh-admin, PUBLIC_URL placeholder, non-python, or unsupported commands.

## Previews
- **platform-setup-FP-AUTO-263** (`skipped`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `skipped` (not_marked_preview_safe)
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-263`
  - Guardrail: Push worker secrets only after local OAuth/public posting setup is complete.
- **platform-setup-FP-AUTO-264** (`input_missing`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `safe_preview` (dry_run_command)
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - Output: ERROR: TIKTOK_CLIENT_KEY is missing from secrets/social_api.env | ERROR: TIKTOK_CLIENT_SECRET is missing from secrets/social_api.env | ERROR: TIKTOK_REFRESH_TOKEN is missing from secrets/social_api.env
  - Guardrail: Run the TikTok preflight before pushing secrets; push worker secrets only after local OAuth/public posting setup is complete.
- **platform-setup-FP-AUTO-265** (`skipped`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `skipped` (not_marked_preview_safe)
  - Command: `python3 scripts/check_facebook_publishing.py --post-id 'FP-AUTO-265' --check-worker-dry-run`
  - Guardrail: Push worker secrets only after local OAuth/public posting setup is complete.
- **platform-setup-FP-PLAN-TWELVE-DOLLARS-INSTAGRAM** (`skipped`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `skipped` (not_marked_preview_safe)
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`
  - Guardrail: Push worker secrets only after local OAuth/public posting setup is complete.
- **backlog-reschedule** (`preview_ok_with_warning`)
  - Phase: `Backlog recovery`; input needed: `clearance_confirmation`
  - Safety: `safe_preview` (reschedule_preview_command)
  - Command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-23T10:00:00+00:00' --spacing-hours 24`
  - Output: Rows selected: 3 | - FP-AUTO-264 TikTok I Learned It All in Fifteen Seconds: 2026-06-09T21:25:00-04:00 -> 2026-06-23T10:00:00+00:00 |   WARNING: known blocker: tiktok_credentials_missing | - FP-AUTO-263 Instagram I Learned It All in Fifteen Seconds: 2026-06-21T10:00:00+09:00 -> 2026-06-24T10:00:00+00:00 |   WARNING: known blocker: Instagram posting could not resolve instagram_business_account; reconnect or set IG_BUSINESS_ACCOUNT_ID. | - FP-PLAN-TWELVE-DOLLARS-INSTAGRAM Instagram Twelve Dollars: 2026-06-21T14:05:00-04:00 -> 2026-06-25T10:00:00+00:00 |   WARNING: known blocker: Instagram posting could not resolve instagram_business_account; reconnect or set IG_BUSINESS_ACCOUNT_ID. | Dry run only. Re-run with --apply to write the schedule.
  - Guardrail: Normal apply stays hidden until known executor/platform blockers clear.
- **manual-distribution-FP-AUTO-261** (`skipped`)
  - Phase: `Manual distribution`; input needed: `public_post_url`
  - Safety: `skipped` (placeholder_public_url)
  - Command: `python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url PUBLIC_URL`
  - Guardrail: Do not log a manual post until a real public URL exists.
- **manual-distribution-FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY** (`skipped`)
  - Phase: `Manual distribution`; input needed: `public_post_url`
  - Safety: `skipped` (placeholder_public_url)
  - Command: `python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url PUBLIC_URL`
  - Guardrail: Do not log a manual post until a real public URL exists.
- **manual-distribution-FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY** (`skipped`)
  - Phase: `Manual distribution`; input needed: `public_post_url`
  - Safety: `skipped` (placeholder_public_url)
  - Command: `python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url PUBLIC_URL`
  - Guardrail: Do not log a manual post until a real public URL exists.
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
