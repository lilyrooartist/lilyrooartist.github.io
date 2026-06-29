# Human Handoff Resolution Preview - Lily Roo

Generated: 2026-06-29T16:26:29.045161Z

## Summary
- Worksheet rows: **8**
- Executed previews: **4**
- Skipped previews: **4**
- Status counts: `{"input_missing": 3, "preview_ok_with_warning": 1, "skipped": 4}`
- Policy: Only python3 scripts/* commands with --dry-run, or reschedule previews without --apply, are executed.
- Guardrail: This preview runner never executes apply, refresh-admin, PUBLIC_URL placeholder, non-python, or unsupported commands.

## Previews
- **platform-setup-FP-AUTO-265** (`skipped`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `skipped` (not_marked_preview_safe)
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-265`
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
- **platform-setup-FP-STORY-ANALOG-MYTH-FACEBOOK-ARCHIVE-CTA** (`skipped`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `skipped` (not_marked_preview_safe)
  - Command: `python3 scripts/check_facebook_publishing.py --post-id 'FP-STORY-ANALOG-MYTH-FACEBOOK-ARCHIVE-CTA' --check-worker-dry-run`
  - Guardrail: Push worker secrets only after local platform setup is complete.
- **backlog-reschedule** (`preview_ok_with_warning`)
  - Phase: `Backlog recovery`; input needed: `clearance_confirmation`
  - Safety: `safe_preview` (reschedule_preview_command)
  - Command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-30T10:00:00-04:00' --spacing-hours 24`
  - Output: Rows selected: 24 | - FP-AUTO-258 Instagram I Learned It All in Fifteen Seconds: 2026-06-23T10:00:00+08:00 -> 2026-06-30T10:00:00-04:00 | - FP-AUTO-264 TikTok I Learned It All in Fifteen Seconds: 2026-06-23T10:00:00+08:00 -> 2026-07-01T10:00:00-04:00 | - FP-PLAN-TWELVE-DOLLARS-FACEBOOK Facebook Twelve Dollars: 2026-06-23T11:20:00-04:00 -> 2026-07-02T10:00:00-04:00 | - FP-AUTO-261 YouTube I Learned It All in Fifteen Seconds: 2026-06-24T10:00:00+08:00 -> 2026-07-03T10:00:00-04:00 | - FP-AUTO-263 Instagram I Learned It All in Fifteen Seconds: 2026-06-24T10:00:00+08:00 -> 2026-07-04T10:00:00-04:00 | - FP-WIN-ANALOG-MYTH-X-RELEASE-ART-IMAGE-STORY-HOOK X Analog Myth: 2026-06-24T10:15:00-04:00 -> 2026-07-05T10:00:00-04:00 | - FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY YouTube Twelve Dollars: 2026-06-24T18:30:00-04:00 -> 2026-07-06T10:00:00-04:00 | - FP-PLAN-TWELVE-DOLLARS-INSTAGRAM Instagram Twelve Dollars: 2026-06-25T10:00:00+08:00 -> 2026-07-07T10:00:00-04:00 | - FP-WIN-ANALOG-MYTH-FACEBOOK-RELEASE-ART-IMAGE-STORY-HOOK Facebook Analog Myth: 2026-06-25T11:20:00-04:00 -> 2026-07-08T10:00:00-04:00 | - FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY YouTube Analog Myth: 2026-06-25T18:30:00-04:00 -> 2026-07-09T10:00:00-04:00 | - FP-PLAN-TWELVE-DOLLARS-X X Twelve Dollars: 2026-06-26T10:00:00+08:00 -> 2026-07-10T10:00:00-04:00 | - FP-STORY-TWELVE-DOLLARS-X-ARCHIVE-CTA X Twelve Dollars: 2026-06-26T10:15:00-04:00 -> 2026-07-11T10:00:00-04:00 | - FP-STORY-TWELVE-DOLLARS-FACEBOOK-ARCHIVE-CTA Facebook Twelve Dollars: 2026-06-27T11:20:00-04:00 -> 2026-07-12T10:00:00-04:00 | - FP-SHORT-TWELVE-DOLLARS-YOUTUBE-SHORTS-CTA YouTube Twelve Dollars: 2026-06-27T18:30:00+08:00 -> 2026-07-13T10:00:00-04:00 | - FP-AUTO-267 Instagram Brain Rot: 2026-06-27T21:35:00-04:00 -> 2026-07-14T10:00:00-04:00 | - FP-AUTO-268 Facebook Brain Rot: 2026-06-27T21:55:00-04:00 -> 2026-07-15T10:00:00-04:00 | - FP-AUTO-269 TikTok Brain Rot: 2026-06-27T22:15:00-04:00 -> 2026-07-16T10:00:00-04:00 | - FP-AUTO-265 Facebook I Learned It All in Fifteen Seconds: 2026-06
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
