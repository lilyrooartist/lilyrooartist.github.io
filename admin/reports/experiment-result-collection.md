# Experiment Result Collection - Lily Roo

Generated: 2026-07-06T01:16:29.117972Z

## Summary
- Experiment count: **3**
- Published experiment posts: **15**
- Missing published log posts: **6**
- Pending result fields: **84**
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
- `FP-AUTO-272` (Release-art image + story hook): Publish or log the public URL before result metrics can be collected.
- `FP-AUTO-277` (Release-art image + story hook): Publish or log the public URL before result metrics can be collected.
- `FP-AUTO-282` (Release-art image + story hook): Publish or log the public URL before result metrics can be collected.
- `FP-AUTO-274` (Short video clip + platform-native CTA): Publish or log the public URL before result metrics can be collected.
- `FP-AUTO-279` (Short video clip + platform-native CTA): Publish or log the public URL before result metrics can be collected.
- `FP-AUTO-284` (Short video clip + platform-native CTA): Publish or log the public URL before result metrics can be collected.

## Pending Result Fields
- `FP-WIN-ANALOG-MYTH-X-RELEASE-ART-IMAGE-STORY-HOOK` X `views` from row 23: Open X analytics for https://x.com/i/web/status/2069786481556635841 and record views.
- `FP-WIN-ANALOG-MYTH-X-RELEASE-ART-IMAGE-STORY-HOOK` X `likes` from row 23: Open X analytics for https://x.com/i/web/status/2069786481556635841 and record likes.
- `FP-WIN-ANALOG-MYTH-X-RELEASE-ART-IMAGE-STORY-HOOK` X `comments` from row 23: Open X analytics for https://x.com/i/web/status/2069786481556635841 and record comments.
- `FP-WIN-ANALOG-MYTH-X-RELEASE-ART-IMAGE-STORY-HOOK` X `shares` from row 23: Open X analytics for https://x.com/i/web/status/2069786481556635841 and record shares.
- `FP-WIN-ANALOG-MYTH-X-RELEASE-ART-IMAGE-STORY-HOOK` X `saves` from row 23: Open X analytics for https://x.com/i/web/status/2069786481556635841 and record saves.
- `FP-WIN-ANALOG-MYTH-X-RELEASE-ART-IMAGE-STORY-HOOK` X `subs_delta` from row 23: Open X analytics for https://x.com/i/web/status/2069786481556635841 and record subs_delta.
- `FP-WIN-ANALOG-MYTH-FACEBOOK-RELEASE-ART-IMAGE-STORY-HOOK` Facebook `views` from row 36: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594301249470 and record views.
- `FP-WIN-ANALOG-MYTH-FACEBOOK-RELEASE-ART-IMAGE-STORY-HOOK` Facebook `likes` from row 36: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594301249470 and record likes.
- `FP-WIN-ANALOG-MYTH-FACEBOOK-RELEASE-ART-IMAGE-STORY-HOOK` Facebook `comments` from row 36: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594301249470 and record comments.
- `FP-WIN-ANALOG-MYTH-FACEBOOK-RELEASE-ART-IMAGE-STORY-HOOK` Facebook `shares` from row 36: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594301249470 and record shares.
- `FP-WIN-ANALOG-MYTH-FACEBOOK-RELEASE-ART-IMAGE-STORY-HOOK` Facebook `saves` from row 36: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594301249470 and record saves.
- `FP-WIN-ANALOG-MYTH-FACEBOOK-RELEASE-ART-IMAGE-STORY-HOOK` Facebook `subs_delta` from row 36: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594301249470 and record subs_delta.
- `FP-AUTO-273` Facebook `views` from row 32: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594571249470 and record views.
- `FP-AUTO-273` Facebook `likes` from row 32: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594571249470 and record likes.
- `FP-AUTO-273` Facebook `comments` from row 32: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594571249470 and record comments.
- `FP-AUTO-273` Facebook `shares` from row 32: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594571249470 and record shares.
- `FP-AUTO-273` Facebook `saves` from row 32: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594571249470 and record saves.
- `FP-AUTO-273` Facebook `subs_delta` from row 32: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594571249470 and record subs_delta.
- `FP-AUTO-276` X `views` from row 38: Open X analytics for https://x.com/i/web/status/2071764617978950017 and record views.
- `FP-AUTO-276` X `likes` from row 38: Open X analytics for https://x.com/i/web/status/2071764617978950017 and record likes.
- `FP-AUTO-276` X `comments` from row 38: Open X analytics for https://x.com/i/web/status/2071764617978950017 and record comments.
- `FP-AUTO-276` X `shares` from row 38: Open X analytics for https://x.com/i/web/status/2071764617978950017 and record shares.
- `FP-AUTO-276` X `saves` from row 38: Open X analytics for https://x.com/i/web/status/2071764617978950017 and record saves.
- `FP-AUTO-276` X `subs_delta` from row 38: Open X analytics for https://x.com/i/web/status/2071764617978950017 and record subs_delta.
- `FP-AUTO-278` Facebook `views` from row 30: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120594715249470 and record views.
- ...and 59 more rows in `data/experiment_result_entry_template.csv`.
