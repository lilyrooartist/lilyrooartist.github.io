# Experiment Result Collection - Lily Roo

Generated: 2026-06-22T07:15:28.937748Z

## Summary
- Experiment count: **3**
- Published experiment posts: **3**
- Missing published log posts: **6**
- Pending result fields: **18**
- Ready to import: **0**
- Entry CSV: `data/experiment_result_entry_template.csv`
- Wide entry CSV: `data/experiment_result_entry_wide_template.csv`

## Commands
- Fill `new_value` and `evidence_note` in `data/experiment_result_entry_template.csv`.
- Or fill one row per post in `data/experiment_result_entry_wide_template.csv`.
- Preview import: `python3 scripts/update_experiment_results.py --from-csv data/experiment_result_entry_template.csv --dry-run`
- Preview wide import: `python3 scripts/update_experiment_results.py --from-wide-csv data/experiment_result_entry_wide_template.csv --dry-run`
- Apply after review: `blocked until new_value/evidence_note cells are filled`

## Guardrails
- This packet is review-only; it does not write result metrics into Published_Log.csv.
- Do not log a placeholder URL or guessed metric value.
- Fill only metrics visible in the platform analytics surface.

## Missing Published Log Rows
- `FP-AUTO-258` (Release-art image + story hook): Publish or log the public URL before result metrics can be collected.
- `FP-AUTO-261` (YouTube Community archive/playlist CTA): Publish or log the public URL before result metrics can be collected.
- `FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY` (YouTube Community archive/playlist CTA): Publish or log the public URL before result metrics can be collected.
- `FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY` (YouTube Community archive/playlist CTA): Publish or log the public URL before result metrics can be collected.
- `FP-AUTO-264` (Short video clip + platform-native CTA): Publish or log the public URL before result metrics can be collected.
- `FP-PLAN-TWELVE-DOLLARS-TIKTOK` (Short video clip + platform-native CTA): Publish or log the public URL before result metrics can be collected.

## Pending Result Fields
- `FP-AUTO-257` X `views` from row 16: Open X analytics for https://x.com/i/web/status/2062920257577029712 and record views.
- `FP-AUTO-257` X `likes` from row 16: Open X analytics for https://x.com/i/web/status/2062920257577029712 and record likes.
- `FP-AUTO-257` X `comments` from row 16: Open X analytics for https://x.com/i/web/status/2062920257577029712 and record comments.
- `FP-AUTO-257` X `shares` from row 16: Open X analytics for https://x.com/i/web/status/2062920257577029712 and record shares.
- `FP-AUTO-257` X `saves` from row 16: Open X analytics for https://x.com/i/web/status/2062920257577029712 and record saves.
- `FP-AUTO-257` X `subs_delta` from row 16: Open X analytics for https://x.com/i/web/status/2062920257577029712 and record subs_delta.
- `FP-AUTO-260` Facebook `views` from row 18: Open Meta Business Suite for https://www.facebook.com/903693509504290_122118326547249470 and record views.
- `FP-AUTO-260` Facebook `likes` from row 18: Open Meta Business Suite for https://www.facebook.com/903693509504290_122118326547249470 and record likes.
- `FP-AUTO-260` Facebook `comments` from row 18: Open Meta Business Suite for https://www.facebook.com/903693509504290_122118326547249470 and record comments.
- `FP-AUTO-260` Facebook `shares` from row 18: Open Meta Business Suite for https://www.facebook.com/903693509504290_122118326547249470 and record shares.
- `FP-AUTO-260` Facebook `saves` from row 18: Open Meta Business Suite for https://www.facebook.com/903693509504290_122118326547249470 and record saves.
- `FP-AUTO-260` Facebook `subs_delta` from row 18: Open Meta Business Suite for https://www.facebook.com/903693509504290_122118326547249470 and record subs_delta.
- `FP-AUTO-262` X `views` from row 17: Open X analytics for https://x.com/i/web/status/2063600780834136468 and record views.
- `FP-AUTO-262` X `likes` from row 17: Open X analytics for https://x.com/i/web/status/2063600780834136468 and record likes.
- `FP-AUTO-262` X `comments` from row 17: Open X analytics for https://x.com/i/web/status/2063600780834136468 and record comments.
- `FP-AUTO-262` X `shares` from row 17: Open X analytics for https://x.com/i/web/status/2063600780834136468 and record shares.
- `FP-AUTO-262` X `saves` from row 17: Open X analytics for https://x.com/i/web/status/2063600780834136468 and record saves.
- `FP-AUTO-262` X `subs_delta` from row 17: Open X analytics for https://x.com/i/web/status/2063600780834136468 and record subs_delta.
