# Facebook Post Results - Lily Roo

Generated: 2026-06-22T08:28:20.047937Z

## Summary
- Status: **no_open_facebook_result_fields**
- Captured posts: **2**
- Fillable posts: **0**
- Fillable result fields: **0**
- Apply command: `python3 scripts/capture_facebook_post_results.py --apply-results --refresh-admin`

## Rows
- **FP-AUTO-210** row `7`
  - URL: https://www.facebook.com/903693509504290_122113878687249470
  - Lookup: `ok`
  - Likes: `0`; comments: `0`; shares: `0`
  - Post clicks captured but not imported as views: `0`
  - Fillable fields: `none`
  - Evidence: Facebook Graph post metrics 2026-06-22
- **FP-AUTO-260** row `18`
  - URL: https://www.facebook.com/903693509504290_122118326547249470
  - Lookup: `ok`
  - Likes: `0`; comments: `0`; shares: `0`
  - Post clicks captured but not imported as views: `0`
  - Fillable fields: `none`
  - Evidence: Facebook Graph post metrics 2026-06-22

## Guardrails
- Metrics come from the Facebook Graph API for already-published Lily Roo posts.
- This report does not contain Meta credentials.
- Post clicks are not treated as views.
- Applying results goes through scripts/update_experiment_results.py so Published_Log.csv row IDs are verified.
