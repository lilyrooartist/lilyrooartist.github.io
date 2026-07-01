# Experiment Result Collection - Lily Roo

Generated: 2026-07-01T21:59:14.832494Z

## Summary
- Experiment count: **3**
- Published experiment posts: **18**
- Missing published log posts: **7**
- Pending result fields: **95**
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
- `FP-PLAN-TWELVE-DOLLARS-INSTAGRAM` (Release-art image + story hook): Publish or log the public URL before result metrics can be collected.
- `FP-AUTO-267` (Release-art image + story hook): Publish or log the public URL before result metrics can be collected.
- `FP-AUTO-272` (Release-art image + story hook): Publish or log the public URL before result metrics can be collected.
- `FP-AUTO-269` (Short video clip + platform-native CTA): Publish or log the public URL before result metrics can be collected.
- `FP-AUTO-274` (Short video clip + platform-native CTA): Publish or log the public URL before result metrics can be collected.
- `FP-AUTO-279` (Short video clip + platform-native CTA): Publish or log the public URL before result metrics can be collected.
- `FP-AUTO-284` (Short video clip + platform-native CTA): Publish or log the public URL before result metrics can be collected.

## Pending Result Fields
- `FP-AUTO-257` X `subs_delta` from row 16: Open X analytics for https://x.com/i/web/status/2062920257577029712 and record subs_delta.
- `FP-AUTO-260` Facebook `views` from row 18: Open Meta Business Suite for https://www.facebook.com/903693509504290_122118326547249470 and record views.
- `FP-AUTO-260` Facebook `saves` from row 18: Open Meta Business Suite for https://www.facebook.com/903693509504290_122118326547249470 and record saves.
- `FP-AUTO-260` Facebook `subs_delta` from row 18: Open Meta Business Suite for https://www.facebook.com/903693509504290_122118326547249470 and record subs_delta.
- `FP-AUTO-262` X `subs_delta` from row 17: Open X analytics for https://x.com/i/web/status/2063600780834136468 and record subs_delta.
- `FP-AUTO-265` Facebook `views` from row 33: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594493249470 and record views.
- `FP-AUTO-265` Facebook `likes` from row 33: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594493249470 and record likes.
- `FP-AUTO-265` Facebook `comments` from row 33: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594493249470 and record comments.
- `FP-AUTO-265` Facebook `shares` from row 33: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594493249470 and record shares.
- `FP-AUTO-265` Facebook `saves` from row 33: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594493249470 and record saves.
- `FP-AUTO-265` Facebook `subs_delta` from row 33: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594493249470 and record subs_delta.
- `FP-PLAN-TWELVE-DOLLARS-X` X `views` from row 24: Open X analytics for https://x.com/i/web/status/2068336870803587325 and record views.
- `FP-PLAN-TWELVE-DOLLARS-X` X `likes` from row 24: Open X analytics for https://x.com/i/web/status/2068336870803587325 and record likes.
- `FP-PLAN-TWELVE-DOLLARS-X` X `comments` from row 24: Open X analytics for https://x.com/i/web/status/2068336870803587325 and record comments.
- `FP-PLAN-TWELVE-DOLLARS-X` X `shares` from row 24: Open X analytics for https://x.com/i/web/status/2068336870803587325 and record shares.
- `FP-PLAN-TWELVE-DOLLARS-X` X `saves` from row 24: Open X analytics for https://x.com/i/web/status/2068336870803587325 and record saves.
- `FP-PLAN-TWELVE-DOLLARS-X` X `subs_delta` from row 24: Open X analytics for https://x.com/i/web/status/2068336870803587325 and record subs_delta.
- `FP-PLAN-TWELVE-DOLLARS-FACEBOOK` Facebook `views` from row 37: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594247249470 and record views.
- `FP-PLAN-TWELVE-DOLLARS-FACEBOOK` Facebook `likes` from row 37: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594247249470 and record likes.
- `FP-PLAN-TWELVE-DOLLARS-FACEBOOK` Facebook `comments` from row 37: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594247249470 and record comments.
- `FP-PLAN-TWELVE-DOLLARS-FACEBOOK` Facebook `shares` from row 37: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594247249470 and record shares.
- `FP-PLAN-TWELVE-DOLLARS-FACEBOOK` Facebook `saves` from row 37: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594247249470 and record saves.
- `FP-PLAN-TWELVE-DOLLARS-FACEBOOK` Facebook `subs_delta` from row 37: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594247249470 and record subs_delta.
- `FP-WIN-ANALOG-MYTH-X-RELEASE-ART-IMAGE-STORY-HOOK` X `views` from row 23: Open X analytics for https://x.com/i/web/status/2069786481556635841 and record views.
- `FP-WIN-ANALOG-MYTH-X-RELEASE-ART-IMAGE-STORY-HOOK` X `likes` from row 23: Open X analytics for https://x.com/i/web/status/2069786481556635841 and record likes.
- ...and 70 more rows in `data/experiment_result_entry_template.csv`.
