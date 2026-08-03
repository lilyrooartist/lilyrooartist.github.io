# Experiment Publish Runway - Lily Roo

Generated: 2026-08-03T17:53:45.927886Z

## Summary
- Manual rows ready for review: **0**
- Postable now: **0**
- Public URLs needed: **0**
- Pending result fields: **105**
- Winner-ready formats: **3 / 3**
- Blocked platform rows: **15**

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
- `FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-FACEBOOK` Facebook - max_attempts_exceeded
- `FP-GROWTH-RESET-03-SLOW-WALK-VISUAL-STORY-FACEBOOK` Facebook - max_attempts_exceeded
- `FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-FACEBOOK` Facebook - max_attempts_exceeded
- `FP-GROWTH-RESET-05-SPILLING-THE-TEA-LYRIC-PUNCH-LINE-FACEBOOK` Facebook - max_attempts_exceeded
- `FP-GROWTH-RESET-06-SPILLING-THE-TEA-RELATABLE-SITUATION-FACEBOOK` Facebook - max_attempts_exceeded
- `FP-GROWTH-RESET-07-SPILLING-THE-TEA-VISUAL-STORY-FACEBOOK` Facebook - max_attempts_exceeded
- `FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE` YouTube - max_attempts_exceeded
- `FP-GROWTH-RESET-05-SPILLING-THE-TEA-LYRIC-PUNCH-LINE-YOUTUBE` YouTube - max_attempts_exceeded
- `FP-GROWTH-RESET-06-SPILLING-THE-TEA-RELATABLE-SITUATION-YOUTUBE` YouTube - max_attempts_exceeded
- `FP-GROWTH-RESET-07-SPILLING-THE-TEA-VISUAL-STORY-YOUTUBE` YouTube - max_attempts_exceeded
- `FP-GROWTH-RESET-08-SPILLING-THE-TEA-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE` YouTube - max_attempts_exceeded
- `FP-GROWTH-RESET-09-NO-MORTGAGE-LYRIC-PUNCH-LINE-YOUTUBE` YouTube - max_attempts_exceeded
- `FP-GROWTH-RESET-10-NO-MORTGAGE-RELATABLE-SITUATION-YOUTUBE` YouTube - max_attempts_exceeded
- `FP-GROWTH-RESET-11-NO-MORTGAGE-VISUAL-STORY-YOUTUBE` YouTube - max_attempts_exceeded
