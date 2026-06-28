# Experiment Publish Runway - Lily Roo

Generated: 2026-06-28T00:52:27.297655Z

## Summary
- Manual rows ready for review: **0**
- Postable now: **4**
- Public URLs needed: **4**
- Pending result fields: **5**
- Winner-ready formats: **1 / 3**
- Blocked platform rows: **4**

## Next Publish Action
- Post manual YouTube Community cards, copy real public URLs, then log them.

## Manual Review Rows
- None.

## Runway Steps
- **review_manual_youtube_community** - `clear`
  - Guardrail: Manual-only approvals do not auto-post; posting and public URL logging remain separate.
- **queue_approved_manual_rows** - `waiting_for_approval`
  - Guardrail: Apply only after the matching promo plan rows have approved=yes.
- **post_manual_youtube_community** - `postable_now`
  - Guardrail: Post manually using the reviewed copy and local asset evidence; do not log placeholder URLs.
- **log_public_urls** - `waiting_for_manual_post`
  - Preview: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv`
  - Apply after review: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --apply --refresh-admin`
  - Guardrail: Every CSV row must contain a real public_url before apply.
- **collect_results** - `waiting_for_measurement_window`
  - Preview: `python3 scripts/update_experiment_results.py --from-csv data/experiment_result_entry_template.csv --dry-run`
  - Guardrail: Fill only visible platform analytics values with evidence notes.

## Blocked Platform Rows
- `FP-AUTO-258` Instagram - max_attempts_exceeded
- `FP-AUTO-263` Instagram - max_attempts_exceeded
- `FP-PLAN-TWELVE-DOLLARS-INSTAGRAM` Instagram - max_attempts_exceeded
- `FP-AUTO-265` Facebook - needs_fix
