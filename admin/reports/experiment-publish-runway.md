# Experiment Publish Runway - Lily Roo

Generated: 2026-07-08T14:42:02.044138Z

## Summary
- Manual rows ready for review: **0**
- Postable now: **0**
- Public URLs needed: **0**
- Pending result fields: **96**
- Winner-ready formats: **3 / 3**
- Blocked platform rows: **0**

## Next Publish Action
- Collect experiment results when public URLs and measurement values are available.

## Manual Review Rows
- None.

## Runway Steps
- **manual_distribution_lane_removed** - `clear`
  - Guardrail: Manual YouTube Community posting is not part of the active plan; no review, queue, posting, or URL-logging commands are emitted for this lane.
- **collect_results** - `waiting_for_measurement_window`
  - Preview: `python3 scripts/update_experiment_results.py --from-csv data/experiment_result_entry_template.csv --dry-run`
  - Guardrail: Fill only visible platform analytics values with evidence notes.

## Blocked Platform Rows
- None.
