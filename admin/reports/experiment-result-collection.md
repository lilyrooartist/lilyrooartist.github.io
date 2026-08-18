# Experiment Result Collection - Lily Roo

Generated: 2026-08-18T16:32:24.057206Z

## Summary
- Experiment count: **3**
- Published experiment posts: **21**
- Missing published log posts: **12**
- Pending result fields: **105**
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
- `FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-FACEBOOK` (Short video clip + platform-native CTA): Publish or log the public URL before result metrics can be collected.
- `FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-FACEBOOK` (Short video clip + platform-native CTA): Publish or log the public URL before result metrics can be collected.
- `FP-GROWTH-RESET-03-SLOW-WALK-VISUAL-STORY-FACEBOOK` (Short video clip + platform-native CTA): Publish or log the public URL before result metrics can be collected.
- `FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE` (Short video clip + platform-native CTA): Publish or log the public URL before result metrics can be collected.
- `FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-FACEBOOK` (Short video clip + platform-native CTA): Publish or log the public URL before result metrics can be collected.
- `FP-GROWTH-RESET-05-SPILLING-THE-TEA-LYRIC-PUNCH-LINE-YOUTUBE` (Short video clip + platform-native CTA): Publish or log the public URL before result metrics can be collected.
- `FP-GROWTH-RESET-05-SPILLING-THE-TEA-LYRIC-PUNCH-LINE-FACEBOOK` (Short video clip + platform-native CTA): Publish or log the public URL before result metrics can be collected.
- `FP-GROWTH-RESET-06-SPILLING-THE-TEA-RELATABLE-SITUATION-YOUTUBE` (Short video clip + platform-native CTA): Publish or log the public URL before result metrics can be collected.
- `FP-GROWTH-RESET-06-SPILLING-THE-TEA-RELATABLE-SITUATION-FACEBOOK` (Short video clip + platform-native CTA): Publish or log the public URL before result metrics can be collected.
- `FP-GROWTH-RESET-07-SPILLING-THE-TEA-VISUAL-STORY-YOUTUBE` (Short video clip + platform-native CTA): Publish or log the public URL before result metrics can be collected.
- `FP-GROWTH-RESET-07-SPILLING-THE-TEA-VISUAL-STORY-FACEBOOK` (Short video clip + platform-native CTA): Publish or log the public URL before result metrics can be collected.
- `FP-GROWTH-RESET-08-SPILLING-THE-TEA-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE` (Short video clip + platform-native CTA): Publish or log the public URL before result metrics can be collected.

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
- `FP-LAUNCH-ANALOG-MYTH-X` X `views` from row 40: Open X analytics for https://x.com/i/web/status/2072179856264278171 and record views.
- `FP-LAUNCH-ANALOG-MYTH-X` X `likes` from row 40: Open X analytics for https://x.com/i/web/status/2072179856264278171 and record likes.
- `FP-LAUNCH-ANALOG-MYTH-X` X `comments` from row 40: Open X analytics for https://x.com/i/web/status/2072179856264278171 and record comments.
- `FP-LAUNCH-ANALOG-MYTH-X` X `shares` from row 40: Open X analytics for https://x.com/i/web/status/2072179856264278171 and record shares.
- `FP-LAUNCH-ANALOG-MYTH-X` X `saves` from row 40: Open X analytics for https://x.com/i/web/status/2072179856264278171 and record saves.
- `FP-LAUNCH-ANALOG-MYTH-X` X `subs_delta` from row 40: Open X analytics for https://x.com/i/web/status/2072179856264278171 and record subs_delta.
- `FP-LAUNCH-ANALOG-MYTH-FACEBOOK` Facebook `views` from row 39: Open Meta Business Suite for https://www.facebook.com/permalink.php?story_fbid=122120653563249470&id=903693509504290 and record views.
- `FP-LAUNCH-ANALOG-MYTH-FACEBOOK` Facebook `likes` from row 39: Open Meta Business Suite for https://www.facebook.com/permalink.php?story_fbid=122120653563249470&id=903693509504290 and record likes.
- `FP-LAUNCH-ANALOG-MYTH-FACEBOOK` Facebook `comments` from row 39: Open Meta Business Suite for https://www.facebook.com/permalink.php?story_fbid=122120653563249470&id=903693509504290 and record comments.
- `FP-LAUNCH-ANALOG-MYTH-FACEBOOK` Facebook `shares` from row 39: Open Meta Business Suite for https://www.facebook.com/permalink.php?story_fbid=122120653563249470&id=903693509504290 and record shares.
- `FP-LAUNCH-ANALOG-MYTH-FACEBOOK` Facebook `saves` from row 39: Open Meta Business Suite for https://www.facebook.com/permalink.php?story_fbid=122120653563249470&id=903693509504290 and record saves.
- `FP-LAUNCH-ANALOG-MYTH-FACEBOOK` Facebook `subs_delta` from row 39: Open Meta Business Suite for https://www.facebook.com/permalink.php?story_fbid=122120653563249470&id=903693509504290 and record subs_delta.
- `FP-LAUNCH-ANALOG-MYTH-X-EVENING` X `views` from row 47: Open X analytics for https://x.com/i/web/status/2072445477686026289 and record views.
- ...and 80 more rows in `data/experiment_result_entry_template.csv`.
