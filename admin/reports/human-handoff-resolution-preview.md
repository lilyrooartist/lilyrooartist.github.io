# Human Handoff Resolution Preview - Lily Roo

Generated: 2026-07-03T07:28:22.018938Z

## Summary
- Worksheet rows: **3**
- Executed previews: **3**
- Skipped previews: **0**
- Status counts: `{"input_missing": 3}`
- Policy: Only python3 scripts/* commands with --dry-run, or reschedule previews without --apply, are executed.
- Guardrail: This preview runner never executes apply, refresh-admin, PUBLIC_URL placeholder, non-python, or unsupported commands.

## Previews
- **platform-setup-FP-AUTO-264** (`input_missing`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `safe_preview` (dry_run_command)
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - Output: ERROR: TIKTOK_CLIENT_KEY is missing from secrets/social_api.env | ERROR: TIKTOK_CLIENT_SECRET is missing from secrets/social_api.env | ERROR: TIKTOK_REFRESH_TOKEN is missing from secrets/social_api.env
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
