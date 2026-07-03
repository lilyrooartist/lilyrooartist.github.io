# Human Handoff Resolution Preview - Lily Roo

Generated: 2026-07-03T05:44:25.730272Z

## Summary
- Worksheet rows: **5**
- Executed previews: **2**
- Skipped previews: **3**
- Status counts: `{"input_missing": 2, "skipped": 3}`
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
- **platform-setup-FP-PLAN-TWELVE-DOLLARS-INSTAGRAM** (`skipped`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `skipped` (not_marked_preview_safe)
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`
  - Guardrail: Push worker secrets only after local platform setup is complete.
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
