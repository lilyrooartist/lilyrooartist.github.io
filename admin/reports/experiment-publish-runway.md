# Experiment Publish Runway - Lily Roo

Generated: 2026-06-29T20:48:40.337086Z

## Summary
- Manual rows ready for review: **0**
- Postable now: **0**
- Public URLs needed: **0**
- Pending result fields: **29**
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
- `FP-AUTO-272` Instagram - instagram_business_account_unresolved
- `FP-AUTO-265` Facebook - max_attempts_exceeded
- `FP-AUTO-268` Facebook - max_attempts_exceeded
- `FP-AUTO-273` Facebook - max_attempts_exceeded
- `FP-STORY-ANALOG-MYTH-FACEBOOK-ARCHIVE-CTA` Facebook - max_attempts_exceeded
