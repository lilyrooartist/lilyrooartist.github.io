# Human Handoff Resolution Preview - Lily Roo

Generated: 2026-06-29T15:13:35.125428Z

## Summary
- Worksheet rows: **9**
- Executed previews: **5**
- Skipped previews: **4**
- Status counts: `{"input_missing": 3, "preview_ok": 1, "preview_ok_with_warning": 1, "skipped": 4}`
- Policy: Only python3 scripts/* commands with --dry-run, or reschedule previews without --apply, are executed.
- Guardrail: This preview runner never executes apply, refresh-admin, PUBLIC_URL placeholder, non-python, or unsupported commands.

## Previews
- **approve-checked-scheduled-batch** (`preview_ok`)
  - Phase: `Approval`; input needed: `human_review_decision`
  - Safety: `safe_preview` (dry_run_command)
  - Command: `python3 scripts/update_scheduled_post_approval.py --checked-batch --dry-run`
  - Output: FP-AUTO-259: approved 'no' -> 'yes' | Checked batch guard: 1 checked id(s); 1 requested; 0 unchecked; 1 change(s). | Dry run only; did not update data/scheduled_posts.csv
  - Guardrail: Use --checked-batch so only rows that passed review checks are approved.
- **platform-setup-FP-AUTO-265** (`skipped`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `skipped` (not_marked_preview_safe)
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-265`
  - Guardrail: Push worker secrets only after local platform setup is complete.
- **platform-setup-FP-AUTO-268** (`skipped`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `skipped` (not_marked_preview_safe)
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-268`
  - Guardrail: Push worker secrets only after local platform setup is complete.
- **platform-setup-FP-AUTO-272** (`input_missing`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `safe_preview` (dry_run_command)
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run IG_BUSINESS_ACCOUNT_ID`
  - Output: ERROR: IG_BUSINESS_ACCOUNT_ID is missing from secrets/social_api.env
  - Guardrail: Push worker secrets only after local platform setup is complete.
- **platform-setup-FP-AUTO-273** (`skipped`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `skipped` (not_marked_preview_safe)
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-273`
  - Guardrail: Push worker secrets only after local platform setup is complete.
- **platform-setup-FP-SHORT-ANALOG-MYTH-YOUTUBE-SHORTS-CTA** (`skipped`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `skipped` (not_marked_preview_safe)
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-SHORT-ANALOG-MYTH-YOUTUBE-SHORTS-CTA`
  - Guardrail: Push worker secrets only after local platform setup is complete.
- **backlog-reschedule** (`preview_ok_with_warning`)
  - Phase: `Backlog recovery`; input needed: `clearance_confirmation`
  - Safety: `safe_preview` (reschedule_preview_command)
  - Command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-30T10:00:00-04:00' --spacing-hours 24`
  - Output: Rows selected: 23 | - FP-AUTO-258 Instagram I Learned It All in Fifteen Seconds: 2026-06-23T10:00:00+08:00 -> 2026-06-30T10:00:00-04:00 | - FP-AUTO-264 TikTok I Learned It All in Fifteen Seconds: 2026-06-23T10:00:00+08:00 -> 2026-07-01T10:00:00-04:00 | - FP-PLAN-TWELVE-DOLLARS-FACEBOOK Facebook Twelve Dollars: 2026-06-23T11:20:00-04:00 -> 2026-07-02T10:00:00-04:00 | - FP-AUTO-261 YouTube I Learned It All in Fifteen Seconds: 2026-06-24T10:00:00+08:00 -> 2026-07-03T10:00:00-04:00 | - FP-AUTO-263 Instagram I Learned It All in Fifteen Seconds: 2026-06-24T10:00:00+08:00 -> 2026-07-04T10:00:00-04:00 | - FP-WIN-ANALOG-MYTH-X-RELEASE-ART-IMAGE-STORY-HOOK X Analog Myth: 2026-06-24T10:15:00-04:00 -> 2026-07-05T10:00:00-04:00 | - FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY YouTube Twelve Dollars: 2026-06-24T18:30:00-04:00 -> 2026-07-06T10:00:00-04:00 | - FP-PLAN-TWELVE-DOLLARS-INSTAGRAM Instagram Twelve Dollars: 2026-06-25T10:00:00+08:00 -> 2026-07-07T10:00:00-04:00 | - FP-WIN-ANALOG-MYTH-FACEBOOK-RELEASE-ART-IMAGE-STORY-HOOK Facebook Analog Myth: 2026-06-25T11:20:00-04:00 -> 2026-07-08T10:00:00-04:00 | - FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY YouTube Analog Myth: 2026-06-25T18:30:00-04:00 -> 2026-07-09T10:00:00-04:00 | - FP-PLAN-TWELVE-DOLLARS-X X Twelve Dollars: 2026-06-26T10:00:00+08:00 -> 2026-07-10T10:00:00-04:00 | - FP-STORY-TWELVE-DOLLARS-X-ARCHIVE-CTA X Twelve Dollars: 2026-06-26T10:15:00-04:00 -> 2026-07-11T10:00:00-04:00 | - FP-STORY-TWELVE-DOLLARS-FACEBOOK-ARCHIVE-CTA Facebook Twelve Dollars: 2026-06-27T11:20:00-04:00 -> 2026-07-12T10:00:00-04:00 | - FP-SHORT-TWELVE-DOLLARS-YOUTUBE-SHORTS-CTA YouTube Twelve Dollars: 2026-06-27T18:30:00+08:00 -> 2026-07-13T10:00:00-04:00 | - FP-AUTO-267 Instagram Brain Rot: 2026-06-27T21:35:00-04:00 -> 2026-07-14T10:00:00-04:00 | - FP-AUTO-268 Facebook Brain Rot: 2026-06-27T21:55:00-04:00 -> 2026-07-15T10:00:00-04:00 |   WARNING: known blocker: Facebook blocked Page publishing until identity is confirmed in the Facebook app. | - FP-AUTO-269 TikTok Brain Rot: 2026-06-27T22:
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
