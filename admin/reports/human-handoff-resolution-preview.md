# Human Handoff Resolution Preview - Lily Roo

Generated: 2026-06-30T13:49:56.546491Z

## Summary
- Worksheet rows: **8**
- Executed previews: **7**
- Skipped previews: **1**
- Status counts: `{"input_missing": 5, "preview_ok": 1, "preview_ok_with_warning": 1, "skipped": 1}`
- Policy: Only python3 scripts/* commands with --dry-run, or reschedule previews without --apply, are executed.
- Guardrail: This preview runner never executes apply, refresh-admin, PUBLIC_URL placeholder, non-python, or unsupported commands.

## Previews
- **platform-setup-FP-AUTO-267** (`input_missing`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `safe_preview` (dry_run_command)
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run IG_BUSINESS_ACCOUNT_ID`
  - Output: ERROR: IG_BUSINESS_ACCOUNT_ID is missing from secrets/social_api.env
  - Guardrail: Push worker secrets only after local platform setup is complete.
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
- **platform-setup-FP-PLAN-TWELVE-DOLLARS-INSTAGRAM** (`skipped`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `skipped` (not_marked_preview_safe)
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`
  - Guardrail: Push worker secrets only after local platform setup is complete.
- **backlog-reschedule** (`preview_ok_with_warning`)
  - Phase: `Backlog recovery`; input needed: `clearance_confirmation`
  - Safety: `safe_preview` (reschedule_preview_command)
  - Command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-01T10:00:00-04:00' --spacing-hours 24`
  - Output: Rows selected: 22 | - FP-AUTO-258 Instagram I Learned It All in Fifteen Seconds: 2026-06-23T10:00:00+08:00 -> 2026-07-01T10:00:00-04:00 | - FP-AUTO-264 TikTok I Learned It All in Fifteen Seconds: 2026-06-23T10:00:00+08:00 -> 2026-07-02T10:00:00-04:00 | - FP-PLAN-TWELVE-DOLLARS-FACEBOOK Facebook Twelve Dollars: 2026-06-23T11:20:00-04:00 -> 2026-07-03T10:00:00-04:00 | - FP-AUTO-263 Instagram I Learned It All in Fifteen Seconds: 2026-06-24T10:00:00+08:00 -> 2026-07-04T10:00:00-04:00 | - FP-WIN-ANALOG-MYTH-X-RELEASE-ART-IMAGE-STORY-HOOK X Analog Myth: 2026-06-24T10:15:00-04:00 -> 2026-07-05T10:00:00-04:00 | - FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY YouTube Twelve Dollars: 2026-06-24T18:30:00-04:00 -> 2026-07-06T10:00:00-04:00 | - FP-PLAN-TWELVE-DOLLARS-INSTAGRAM Instagram Twelve Dollars: 2026-06-25T10:00:00+08:00 -> 2026-07-07T10:00:00-04:00 |   WARNING: known blocker: Instagram posting could not resolve instagram_business_account; reconnect or set IG_BUSINESS_ACCOUNT_ID. | - FP-WIN-ANALOG-MYTH-FACEBOOK-RELEASE-ART-IMAGE-STORY-HOOK Facebook Analog Myth: 2026-06-25T11:20:00-04:00 -> 2026-07-08T10:00:00-04:00 | - FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY YouTube Analog Myth: 2026-06-25T18:30:00-04:00 -> 2026-07-09T10:00:00-04:00 | - FP-PLAN-TWELVE-DOLLARS-X X Twelve Dollars: 2026-06-26T10:00:00+08:00 -> 2026-07-10T10:00:00-04:00 | - FP-STORY-TWELVE-DOLLARS-X-ARCHIVE-CTA X Twelve Dollars: 2026-06-26T10:15:00-04:00 -> 2026-07-11T10:00:00-04:00 | - FP-STORY-TWELVE-DOLLARS-FACEBOOK-ARCHIVE-CTA Facebook Twelve Dollars: 2026-06-27T11:20:00-04:00 -> 2026-07-12T10:00:00-04:00 | - FP-SHORT-TWELVE-DOLLARS-YOUTUBE-SHORTS-CTA YouTube Twelve Dollars: 2026-06-27T18:30:00+08:00 -> 2026-07-13T10:00:00-04:00 | - FP-AUTO-267 Instagram Brain Rot: 2026-06-27T21:35:00-04:00 -> 2026-07-14T10:00:00-04:00 |   WARNING: known blocker: instagram_business_account_unresolved | - FP-AUTO-269 TikTok Brain Rot: 2026-06-27T22:15:00-04:00 -> 2026-07-15T10:00:00-04:00 | - FP-STORY-ANALOG-MYTH-X-ARCHIVE-CTA X Analog Myth: 2026-06-28T10:15:00-04:
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
