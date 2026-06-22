# Experiment Result Clipboard - Lily Roo

Generated: 2026-06-22T08:45:25.207309Z

## Summary
- Status: **needs_values**
- Metric cards: **3**
- Missing public URLs: **13**
- Measurement priorities: **12**
- Post-log handoff rows: **3**
- Pending result fields: **5**
- Ready to import: **0**
- Wide rows ready to import: **0**
- Entry CSV: `data/experiment_result_entry_template.csv`
- Wide entry CSV: `data/experiment_result_entry_wide_template.csv`
- Preview import: `python3 scripts/update_experiment_results.py --from-csv data/experiment_result_entry_template.csv --dry-run`
- Preview wide import: `python3 scripts/update_experiment_results.py --from-wide-csv data/experiment_result_entry_wide_template.csv --dry-run`
- Apply after review: `blocked until values/evidence are filled`

## Metric Cards
### X - I Learned It All in Fifteen Seconds (`FP-AUTO-257`)
- Format: Release-art image + story hook
- URL: https://x.com/i/web/status/2062920257577029712
- Published: 2026-06-05; Published_Log row: `16`
- Pending fields: `subs_delta`
- Wide-ready fields: `none`
- Wide entry instruction: Fill one wide entry CSV row in data/experiment_result_entry_wide_template.csv for this post; keep unknown metrics blank and include one evidence_note.
- Wide CSV target: post_id `FP-AUTO-257`, source_row `16`, fill `subs_delta`.
- Evidence sources:
  - Logged public post: https://x.com/i/web/status/2062920257577029712 - Open the public post to confirm the URL and visible engagement before entering metrics.
  - X Analytics: https://analytics.x.com/ - Use the logged post URL or post ID to find the post and copy visible analytics values.
- Collection checklist:
  - Open the logged public post and confirm it matches this post_id.
  - Open the platform analytics or insights source listed for this card.
  - Copy only numeric values that are visible in the source.
  - Enter values in the wide entry CSV row for this post_id and source_row.
  - Add an evidence_note with source and collection date before import preview.
  - `subs_delta`: Open X analytics for https://x.com/i/web/status/2062920257577029712 and record subs_delta.
### Facebook - I Learned It All in Fifteen Seconds (`FP-AUTO-260`)
- Format: Release-art image + story hook
- URL: https://www.facebook.com/903693509504290_122118326547249470
- Published: 2026-06-07; Published_Log row: `18`
- Pending fields: `views, saves, subs_delta`
- Wide-ready fields: `none`
- Wide entry instruction: Fill one wide entry CSV row in data/experiment_result_entry_wide_template.csv for this post; keep unknown metrics blank and include one evidence_note.
- Wide CSV target: post_id `FP-AUTO-260`, source_row `18`, fill `views, saves, subs_delta`.
- Evidence sources:
  - Logged public post: https://www.facebook.com/903693509504290_122118326547249470 - Open the public post to confirm the URL and visible engagement before entering metrics.
  - Meta Business Suite: https://business.facebook.com/latest/insights - Open post insights for the Lily Roo page post and copy the available result values.
- Collection checklist:
  - Open the logged public post and confirm it matches this post_id.
  - Open the platform analytics or insights source listed for this card.
  - Copy only numeric values that are visible in the source.
  - Enter values in the wide entry CSV row for this post_id and source_row.
  - Add an evidence_note with source and collection date before import preview.
  - `views`: Open Meta Business Suite for https://www.facebook.com/903693509504290_122118326547249470 and record views.
  - `saves`: Open Meta Business Suite for https://www.facebook.com/903693509504290_122118326547249470 and record saves.
  - `subs_delta`: Open Meta Business Suite for https://www.facebook.com/903693509504290_122118326547249470 and record subs_delta.
### X - I Learned It All in Fifteen Seconds (`FP-AUTO-262`)
- Format: Release-art image + story hook
- URL: https://x.com/i/web/status/2063600780834136468
- Published: 2026-06-07; Published_Log row: `17`
- Pending fields: `subs_delta`
- Wide-ready fields: `none`
- Wide entry instruction: Fill one wide entry CSV row in data/experiment_result_entry_wide_template.csv for this post; keep unknown metrics blank and include one evidence_note.
- Wide CSV target: post_id `FP-AUTO-262`, source_row `17`, fill `subs_delta`.
- Evidence sources:
  - Logged public post: https://x.com/i/web/status/2063600780834136468 - Open the public post to confirm the URL and visible engagement before entering metrics.
  - X Analytics: https://analytics.x.com/ - Use the logged post URL or post ID to find the post and copy visible analytics values.
- Collection checklist:
  - Open the logged public post and confirm it matches this post_id.
  - Open the platform analytics or insights source listed for this card.
  - Copy only numeric values that are visible in the source.
  - Enter values in the wide entry CSV row for this post_id and source_row.
  - Add an evidence_note with source and collection date before import preview.
  - `subs_delta`: Open X analytics for https://x.com/i/web/status/2063600780834136468 and record subs_delta.

## Measurement Priorities
- **Collect metrics** `FP-AUTO-260` Facebook / Release-art image + story hook: Already published and logged; measuring it reduces the Release-art image + story hook evidence gap. 3 logged post(s), 8 missing URL(s) in this format.
  - Direct preview template: `python3 scripts/update_experiment_results.py --post-id FP-AUTO-260 --source-row 18 --views VALUE --evidence-note 'SOURCE analytics YYYY-MM-DD' --dry-run`
  - Direct apply template: `python3 scripts/update_experiment_results.py --post-id FP-AUTO-260 --source-row 18 --views VALUE --evidence-note 'SOURCE analytics YYYY-MM-DD' --apply --refresh-admin`
- **Collect metrics** `FP-AUTO-257` X / Release-art image + story hook: Already published and logged; measuring it reduces the Release-art image + story hook evidence gap. 3 logged post(s), 8 missing URL(s) in this format.
  - Direct preview template: `python3 scripts/update_experiment_results.py --post-id FP-AUTO-257 --source-row 16 --subs-delta VALUE --evidence-note 'SOURCE analytics YYYY-MM-DD' --dry-run`
  - Direct apply template: `python3 scripts/update_experiment_results.py --post-id FP-AUTO-257 --source-row 16 --subs-delta VALUE --evidence-note 'SOURCE analytics YYYY-MM-DD' --apply --refresh-admin`
- **Collect metrics** `FP-AUTO-262` X / Release-art image + story hook: Already published and logged; measuring it reduces the Release-art image + story hook evidence gap. 3 logged post(s), 8 missing URL(s) in this format.
  - Direct preview template: `python3 scripts/update_experiment_results.py --post-id FP-AUTO-262 --source-row 17 --subs-delta VALUE --evidence-note 'SOURCE analytics YYYY-MM-DD' --dry-run`
  - Direct apply template: `python3 scripts/update_experiment_results.py --post-id FP-AUTO-262 --source-row 17 --subs-delta VALUE --evidence-note 'SOURCE analytics YYYY-MM-DD' --apply --refresh-admin`
- **Post and log public URL** `FP-AUTO-261` YouTube Community / YouTube Community archive/playlist CTA: Postable now in the Manual Posting Clipboard; publish it and log the public URL so metrics can start. 0 logged post(s), 3 missing URL(s) in this format.
  - Paste file: `data/manual-posting-cards/fp-auto-261.txt`
  - Community surface: https://www.youtube.com/@lilyroo.artist/community
  - Log preview after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url PUBLIC_URL`
  - Log apply after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url PUBLIC_URL --apply --refresh-admin`
- **Post and log public URL** `FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY` YouTube Community / YouTube Community archive/playlist CTA: Postable now in the Manual Posting Clipboard; publish it and log the public URL so metrics can start. 0 logged post(s), 3 missing URL(s) in this format.
  - Paste file: `data/manual-posting-cards/fp-plan-analog-myth-youtube-community.txt`
  - Community surface: https://www.youtube.com/@lilyroo.artist/community
  - Log preview after posting: `python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url PUBLIC_URL`
  - Log apply after posting: `python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url PUBLIC_URL --apply --refresh-admin`
- **Post and log public URL** `FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY` YouTube Community / YouTube Community archive/playlist CTA: Postable now in the Manual Posting Clipboard; publish it and log the public URL so metrics can start. 0 logged post(s), 3 missing URL(s) in this format.
  - Paste file: `data/manual-posting-cards/fp-plan-twelve-dollars-youtube-community.txt`
  - Community surface: https://www.youtube.com/@lilyroo.artist/community
  - Log preview after posting: `python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url PUBLIC_URL`
  - Log apply after posting: `python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url PUBLIC_URL --apply --refresh-admin`
- **Log public URL** `FP-PLAN-TWELVE-DOLLARS-FACEBOOK` Facebook / Release-art image + story hook: Cannot collect metrics until the public URL is logged. 3 logged post(s), 8 missing URL(s) in this format.
- **Log public URL** `FP-WIN-ANALOG-MYTH-FACEBOOK-RELEASE-ART-IMAGE-STORY-HOOK` Facebook / Release-art image + story hook: Cannot collect metrics until the public URL is logged. 3 logged post(s), 8 missing URL(s) in this format.
- **Log public URL** `FP-PLAN-TWELVE-DOLLARS-X` X / Release-art image + story hook: Cannot collect metrics until the public URL is logged. 3 logged post(s), 8 missing URL(s) in this format.
- **Log public URL** `FP-WIN-ANALOG-MYTH-X-RELEASE-ART-IMAGE-STORY-HOOK` X / Release-art image + story hook: Cannot collect metrics until the public URL is logged. 3 logged post(s), 8 missing URL(s) in this format.
- **Clear platform blocker** `FP-AUTO-265` Facebook / Release-art image + story hook: Platform work is blocked; clear the platform repair gate before URL logging can produce metrics. 3 logged post(s), 8 missing URL(s) in this format.
- **Clear platform blocker** `FP-AUTO-258` Instagram / Release-art image + story hook: Platform work is blocked; clear the platform repair gate before URL logging can produce metrics. 3 logged post(s), 8 missing URL(s) in this format.

## Post-Log Measurement Handoff
- Status: **waiting_for_public_urls**
- Source session: YouTube Community manual posting batch
- Manual posting report: `admin/reports/manual-posting-clipboard.md`
- Wide entry CSV after URL logging: `data/experiment_result_entry_wide_template.csv`
- Wide import preview after logging: `python3 scripts/update_experiment_results.py --from-wide-csv data/experiment_result_entry_wide_template.csv --dry-run`
- Guardrail: This handoff is a template; do not import metrics until a real public URL and source_row exist.
- Handoff sequence:
  - Post each manual-session card and log the real public URL.
  - Refresh Admin so Published_Log.csv rows become experiment result cards.
  - Collect first visible metrics from YouTube Studio Community analytics.
  - Fill one wide entry CSV row per logged Community post.
  - Run the wide result import preview before applying metrics.
- Handoff rows:
  - `1` `FP-AUTO-261` YouTube Community - collect `views, likes, comments, shares, saves, subs_delta` after `PUBLIC_URL` is real.
    - Log preview: `python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url PUBLIC_URL`
  - `2` `FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY` YouTube Community - collect `views, likes, comments, shares, saves, subs_delta` after `PUBLIC_URL` is real.
    - Log preview: `python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url PUBLIC_URL`
  - `3` `FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY` YouTube Community - collect `views, likes, comments, shares, saves, subs_delta` after `PUBLIC_URL` is real.
    - Log preview: `python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url PUBLIC_URL`
- Completion evidence:
  - Published_Log.csv contains the manual-session post URL.
  - data/experiment_result_clipboard.json shows the post as a metric card instead of a missing-public-url card.
  - data/experiment_result_entry_wide_template.csv has values plus evidence_note for the post.
  - The wide import preview reports only the intended metric updates.

## Missing Public URLs
- `FP-AUTO-258` Instagram / Release-art image + story hook: Publish or log the public URL before result metrics can be collected.
- `FP-AUTO-263` Instagram / Release-art image + story hook: Publish or log the public URL before result metrics can be collected.
- `FP-AUTO-265` Facebook / Release-art image + story hook: Publish or log the public URL before result metrics can be collected.
- `FP-PLAN-TWELVE-DOLLARS-X` X / Release-art image + story hook: Publish or log the public URL before result metrics can be collected.
- `FP-PLAN-TWELVE-DOLLARS-INSTAGRAM` Instagram / Release-art image + story hook: Publish or log the public URL before result metrics can be collected.
- `FP-PLAN-TWELVE-DOLLARS-FACEBOOK` Facebook / Release-art image + story hook: Publish or log the public URL before result metrics can be collected.
- `FP-WIN-ANALOG-MYTH-X-RELEASE-ART-IMAGE-STORY-HOOK` X / Release-art image + story hook: Publish or log the public URL before result metrics can be collected.
- `FP-WIN-ANALOG-MYTH-FACEBOOK-RELEASE-ART-IMAGE-STORY-HOOK` Facebook / Release-art image + story hook: Publish or log the public URL before result metrics can be collected.
- `FP-AUTO-261` YouTube Community / YouTube Community archive/playlist CTA: Publish or log the public URL before result metrics can be collected.
- `FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY` YouTube Community / YouTube Community archive/playlist CTA: Publish or log the public URL before result metrics can be collected.
- `FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY` YouTube Community / YouTube Community archive/playlist CTA: Publish or log the public URL before result metrics can be collected.
- `FP-AUTO-264` TikTok / Short video clip + platform-native CTA: Publish or log the public URL before result metrics can be collected.
- `FP-PLAN-TWELVE-DOLLARS-TIKTOK` TikTok / Short video clip + platform-native CTA: Publish or log the public URL before result metrics can be collected.

## Guardrails
- This clipboard does not fetch private analytics or write metrics.
- Do not use guessed result values.
- Posts without public URLs must be published or logged before result metrics can be collected.
- The post-log measurement handoff is only usable after real public URLs are logged.
