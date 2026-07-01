# Experiment Publish Runway - Lily Roo

Generated: 2026-07-01T22:21:52.036288Z

## Summary
- Manual rows ready for review: **0**
- Postable now: **0**
- Public URLs needed: **0**
- Pending result fields: **95**
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
- `FP-AUTO-272` Instagram - analog_myth_launch_day
- `FP-AUTO-277` Instagram - analog_myth_launch_day
- `FP-AUTO-282` Instagram - analog_myth_launch_day
- `FP-AUTO-279` TikTok - analog_myth_launch_day
- `FP-AUTO-284` TikTok - analog_myth_launch_day
