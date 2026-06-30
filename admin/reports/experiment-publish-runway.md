# Experiment Publish Runway - Lily Roo

Generated: 2026-06-30T13:49:58.840371Z

## Summary
- Manual rows ready for review: **0**
- Postable now: **0**
- Public URLs needed: **0**
- Pending result fields: **83**
- Winner-ready formats: **1 / 3**
- Blocked platform rows: **5**

## Next Publish Action
- Collect experiment results when public URLs and measurement values are available.

## Manual Review Rows
- None.

## Runway Steps
- **collect_results** - `waiting_for_measurement_window`
  - Preview: `python3 scripts/update_experiment_results.py --from-csv data/experiment_result_entry_template.csv --dry-run`
  - Guardrail: Fill only visible platform analytics values with evidence notes.

## Blocked Platform Rows
- `FP-AUTO-267` Instagram - instagram_business_account_unresolved
- `FP-AUTO-272` Instagram - instagram_business_account_unresolved
- `FP-AUTO-277` Instagram - instagram_business_account_unresolved
- `FP-PLAN-TWELVE-DOLLARS-INSTAGRAM` Instagram - max_attempts_exceeded
- `FP-AUTO-279` TikTok - tiktok_public_posting_not_approved
