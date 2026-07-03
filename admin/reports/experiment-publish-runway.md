# Experiment Publish Runway - Lily Roo

Generated: 2026-07-03T06:48:08.139414Z

## Summary
- Manual rows ready for review: **0**
- Postable now: **0**
- Public URLs needed: **0**
- Pending result fields: **114**
- Winner-ready formats: **1 / 3**
- Blocked platform rows: **0**

## Next Publish Action
- Collect experiment results when public URLs and measurement values are available.

## Manual Review Rows
- None.

## Runway Steps
- **review_manual_youtube_community** - `clear`
  - Guardrail: Manual Community approval lane is inactive unless post_ids are present; no manual posting is requested from a clear step.
- **queue_approved_manual_rows** - `clear`
  - Guardrail: Queue nothing while the manual lane is clear; apply only after matching rows have approved=yes.
- **post_manual_youtube_community** - `clear`
  - Guardrail: No manual Community posting is requested when post_ids is empty.
- **log_public_urls** - `clear`
  - Preview: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv`
  - Apply after review: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --apply --refresh-admin`
  - Guardrail: Every CSV row must contain a real public_url before apply; clear lane means no URL logging is pending.
- **collect_results** - `waiting_for_measurement_window`
  - Preview: `python3 scripts/update_experiment_results.py --from-csv data/experiment_result_entry_template.csv --dry-run`
  - Guardrail: Fill only visible platform analytics values with evidence notes.

## Blocked Platform Rows
- None.
