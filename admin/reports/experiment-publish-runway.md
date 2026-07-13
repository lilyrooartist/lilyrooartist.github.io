# Experiment Publish Runway - Lily Roo

Generated: 2026-07-13T19:51:49.431936Z

## Summary
- Manual rows ready for review: **0**
- Postable now: **0**
- Public URLs needed: **0**
- Pending result fields: **99**
- Winner-ready formats: **3 / 3**
- Blocked platform rows: **1**

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
- `FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-FACEBOOK` Facebook - max_attempts_exceeded
