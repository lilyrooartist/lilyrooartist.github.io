# X Post Results - Lily Roo

Generated: 2026-06-22T08:21:34.100125Z

## Summary
- Status: **no_open_x_result_fields**
- Captured posts: **5**
- Fillable posts: **0**
- Fillable result fields: **0**
- Apply command: `python3 scripts/capture_x_post_results.py --apply-results --refresh-admin`

## Rows
- **LR-ANEC-001** row `5`
  - URL: https://x.com/lilyrooartist/status/2027750321322148009
  - Lookup: `missing_from_x_api_response`
  - Views: `0`; likes: `0`; comments: `0`; shares: `0`; saves: `0`
  - Fillable fields: `none`
  - Evidence: X API tweet metrics 2026-06-22
- **FP-AUTO-208** row `10`
  - URL: https://x.com/i/web/status/2047879043295420822
  - Lookup: `ok`
  - Views: `2`; likes: `0`; comments: `0`; shares: `0`; saves: `0`
  - Fillable fields: `none`
  - Evidence: X API tweet metrics 2026-06-22
- **FP-AUTO-213** row `11`
  - URL: https://x.com/i/web/status/2048245628736622826
  - Lookup: `ok`
  - Views: `2`; likes: `0`; comments: `1`; shares: `0`; saves: `0`
  - Fillable fields: `none`
  - Evidence: X API tweet metrics 2026-06-22
- **FP-AUTO-257** row `16`
  - URL: https://x.com/i/web/status/2062920257577029712
  - Lookup: `ok`
  - Views: `4`; likes: `0`; comments: `1`; shares: `0`; saves: `0`
  - Fillable fields: `none`
  - Evidence: X API tweet metrics 2026-06-22
- **FP-AUTO-262** row `17`
  - URL: https://x.com/i/web/status/2063600780834136468
  - Lookup: `ok`
  - Views: `5`; likes: `0`; comments: `0`; shares: `0`; saves: `0`
  - Fillable fields: `none`
  - Evidence: X API tweet metrics 2026-06-22

## Guardrails
- Metrics come from the X API for already-published Lily Roo posts.
- This report does not contain OAuth credentials.
- Applying results goes through scripts/update_experiment_results.py so Published_Log.csv row IDs are verified.
