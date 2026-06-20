# Human Handoff Resolution Preview - Lily Roo

Generated: 2026-06-20T09:21:18.533079Z

## Summary
- Worksheet rows: **7**
- Executed previews: **7**
- Skipped previews: **0**
- Status counts: `{"input_missing": 3, "preview_ok": 3, "preview_ok_with_warning": 1}`
- Policy: Only python3 scripts/* commands with --dry-run, or reschedule previews without --apply, are executed.
- Guardrail: This preview runner never executes apply, refresh-admin, PUBLIC_URL placeholder, non-python, or unsupported commands.

## Previews
- **approve-checked-scheduled-batch** (`preview_ok`)
  - Phase: `Approval`; input needed: `human_review_decision`
  - Safety: `safe_preview` (dry_run_command)
  - Command: `python3 scripts/update_scheduled_post_approval.py --checked-batch --dry-run`
  - Output: FP-AUTO-258: approved 'no' -> 'yes' | FP-AUTO-261: approved 'no' -> 'yes' | Checked batch guard: 2 checked id(s); 2 requested; 0 unchecked; 2 change(s). | Dry run only; did not update data/scheduled_posts.csv
  - Guardrail: Use --checked-batch so only rows that passed review checks are approved.
- **platform-setup-FP-AUTO-264** (`input_missing`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `safe_preview` (dry_run_command)
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - Output: ERROR: TIKTOK_CLIENT_KEY is missing from secrets/social_api.env | ERROR: TIKTOK_CLIENT_SECRET is missing from secrets/social_api.env | ERROR: TIKTOK_REFRESH_TOKEN is missing from secrets/social_api.env
  - Guardrail: Run the TikTok preflight before pushing secrets; push worker secrets only after local OAuth/public posting setup is complete.
- **backlog-reschedule** (`preview_ok_with_warning`)
  - Phase: `Backlog recovery`; input needed: `clearance_confirmation`
  - Safety: `safe_preview` (reschedule_preview_command)
  - Command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-21T10:00:00+00:00' --spacing-hours 24`
  - Output: Rows selected: 1 | - FP-AUTO-264 TikTok I Learned It All in Fifteen Seconds: 2026-06-09T21:25:00-04:00 -> 2026-06-21T10:00:00+00:00 |   WARNING: known blocker: tiktok_credentials_missing | Dry run only. Re-run with --apply to write the schedule.
  - Guardrail: Normal apply stays hidden until known executor/platform blockers clear.
- **manual-distribution-FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY** (`preview_ok`)
  - Phase: `Manual distribution`; input needed: `manual_post_review_and_public_url`
  - Safety: `safe_preview` (dry_run_command)
  - Command: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --dry-run`
  - Output: FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY: approved 'no' -> 'yes' | Dry run only; no changes written to data/promo_queue_plan.json
  - Guardrail: Do not log a manual post until a real public URL exists.
- **manual-distribution-FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY** (`preview_ok`)
  - Phase: `Manual distribution`; input needed: `manual_post_review_and_public_url`
  - Safety: `safe_preview` (dry_run_command)
  - Command: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --dry-run`
  - Output: FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY: approved 'no' -> 'yes' | Dry run only; no changes written to data/promo_queue_plan.json
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
