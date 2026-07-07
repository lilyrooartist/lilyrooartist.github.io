# Experiment Result Collection - Lily Roo

Generated: 2026-07-07T10:01:32.857852Z

## Summary
- Experiment count: **3**
- Published experiment posts: **17**
- Missing published log posts: **2**
- Pending result fields: **90**
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
- YouTube public-video evidence is limited to public views, likes, and comments.
- Fill only metrics visible in the platform analytics surface.

## Missing Published Log Rows
- `FP-AUTO-282` (Release-art image + story hook): Publish or log the public URL before result metrics can be collected.
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
- `FP-AUTO-281` X `views` from row 42: Open X analytics for https://x.com/i/web/status/2072127000391905619 and record views.
- `FP-AUTO-281` X `likes` from row 42: Open X analytics for https://x.com/i/web/status/2072127000391905619 and record likes.
- `FP-AUTO-281` X `comments` from row 42: Open X analytics for https://x.com/i/web/status/2072127000391905619 and record comments.
- `FP-AUTO-281` X `shares` from row 42: Open X analytics for https://x.com/i/web/status/2072127000391905619 and record shares.
- `FP-AUTO-281` X `saves` from row 42: Open X analytics for https://x.com/i/web/status/2072127000391905619 and record saves.
- `FP-AUTO-281` X `subs_delta` from row 42: Open X analytics for https://x.com/i/web/status/2072127000391905619 and record subs_delta.
- `FP-AUTO-283` Facebook `views` from row 41: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120643825249470 and record views.
- `FP-AUTO-283` Facebook `likes` from row 41: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120643825249470 and record likes.
- `FP-AUTO-283` Facebook `comments` from row 41: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120643825249470 and record comments.
- `FP-AUTO-283` Facebook `shares` from row 41: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120643825249470 and record shares.
- `FP-AUTO-283` Facebook `saves` from row 41: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120643825249470 and record saves.
- `FP-AUTO-283` Facebook `subs_delta` from row 41: Open Meta Business Suite for https://www.facebook.com/903693509504290_122120643825249470 and record subs_delta.
- `FP-LAUNCH-ANALOG-MYTH-X` X `views` from row 40: Open X analytics for https://x.com/i/web/status/2072179856264278171 and record views.
- ...and 65 more rows in `data/experiment_result_entry_template.csv`.
