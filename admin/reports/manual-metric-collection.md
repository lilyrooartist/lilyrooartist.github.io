# Manual Metric Collection - Lily Roo

Generated: 2026-06-22T06:04:48.596563Z

Pending fields: **6**

Live-importable fields: **0**
Manual collection required: **6**

Fill `new_value` in `data/manual_metric_entry_template.csv` for the short entry workflow, then run:

`python3 scripts/update_manual_social_stats.py --from-csv data/manual_metric_entry_template.csv --dry-run`

If the preview looks right, run:

`python3 scripts/update_manual_social_stats.py --from-csv data/manual_metric_entry_template.csv --refresh-admin`

The detailed worksheet remains available at `data/manual_metric_collection_template.csv`:

`python3 scripts/update_manual_social_stats.py --from-csv --dry-run`

If the preview looks right, run:

`python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`

To sync metrics already covered by `data/live_social_metrics.json`, run:

`python3 scripts/update_manual_social_stats.py --from-live --dry-run`

If the preview looks right, run:

`python3 scripts/update_manual_social_stats.py --from-live --refresh-admin`

You can still run a platform update command directly if you only collect one platform.

## Metric Collection Docket

- Status: **needs_values**
- Platforms: **5**
- Waiting fields: **6**
- Ready to import: **0**
- CSV: `data/manual_metric_collection_template.csv`
- Short entry CSV: `data/manual_metric_entry_template.csv`
- Preview worksheet import: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
- Apply worksheet import after review: `python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`
- Preview short entry import: `python3 scripts/update_manual_social_stats.py --from-csv data/manual_metric_entry_template.csv --dry-run`
- Apply short entry import after review: `python3 scripts/update_manual_social_stats.py --from-csv data/manual_metric_entry_template.csv --refresh-admin`

### Priority 2: Recent discovery and traffic
- Status: `needs_values`; waiting: **4**; ready: **0**
- Platforms: `facebook, instagram, tiktok, x`
- Access: `private_analytics`
- CSV rows: `2, 3, 6, 7`
- Row `2` `facebook.reach_7d`
  - Enter reach for the last 7 days.
  - Evidence: Use the last-7-days reach value from Meta insights.
- Row `3` `instagram.profile_visits_7d`
  - Enter profile visits for the last 7 days.
  - Evidence: Use the last-7-days profile visits value from the professional dashboard.
- Row `6` `tiktok.profile_views_7d`
  - Enter profile views for the last 7 days.
  - Evidence: Use the last-7-days profile views value from TikTok analytics.
- Row `7` `x.impressions_7d`
  - Enter impressions for the last 7 days.
  - Evidence: Use the last-7-days impressions value from X analytics.

### Priority 3: Release depth metrics
- Status: `needs_values`; waiting: **2**; ready: **0**
- Platforms: `spotify`
- Access: `private_analytics`
- CSV rows: `4, 5`
- Row `4` `spotify.release_streams`
  - Enter lifetime streams for the promoted release.
  - Evidence: Use lifetime streams for the promoted release from Spotify for Artists.
- Row `5` `spotify.saves`
  - Enter lifetime saves for the promoted release.
  - Evidence: Use lifetime saves for the promoted release from Spotify for Artists.

## Worksheet Import Manifest

- Status: **needs_values**
- Ready rows: **0**
- Waiting rows: **6**
- Preview: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
- Apply after review: `blocked until new_value cells are filled`
- Short entry preview: `python3 scripts/update_manual_social_stats.py --from-csv data/manual_metric_entry_template.csv --dry-run`
- Short entry apply after review: `blocked until new_value cells are filled`
- Apply gate: **blocked_until_new_values_filled**
- Guardrail: Import only filled nonnegative numeric new_value cells; leave unknown rows blank.

## Metric Completion Manifest

- Status: **needs_values**
- Waiting fields: **6**
- Ready fields: **0**
- Short entry CSV: `data/manual_metric_entry_template.csv`
- Preview: `python3 scripts/update_manual_social_stats.py --from-csv data/manual_metric_entry_template.csv --dry-run`
- Apply after review: `blocked until new_value cells are filled`
- Apply gate: **blocked_until_new_values_filled**
- Waiting assignments: `facebook.reach_7d=VALUE, instagram.profile_visits_7d=VALUE, spotify.release_streams=VALUE, spotify.saves=VALUE, tiktok.profile_views_7d=VALUE, x.impressions_7d=VALUE`
- Operator checklist:
  - Open the short entry CSV and fill only new_value cells for rows with sourced analytics values.
  - Add an evidence_note for each filled value when the source UI/export can be named briefly.
  - Run the short entry import preview before applying any metric update.
  - Apply only when the preview shows the intended nonnegative numeric values.
  - Refresh Admin and confirm pending_manual_metric_fields decreases or clears.
- Completion evidence:
  - data/manual_metric_collection_packet.json shows fewer waiting fields or ready rows imported.
  - data/manual_social_stats.json contains the imported platform metric values.
  - data/metrics_history.json preserves the imported metrics in the latest snapshot.
  - data/promo_engine_status.json and lilyroo.com/admin show updated pending manual metric counts.
- Guardrails:
  - Do not guess private analytics values.
  - Leave unknown values blank; blank rows are ignored by the import.
  - Import only nonnegative numeric new_value cells from the named analytics source.

### facebook
- Status: `needs_values`; waiting: **1**; ready: **0**
- Open: https://www.facebook.com/903693509504290
- Why: (#100) The value must be a valid insights metric
- CSV row `2` `reach_7d` current `pending` -> `nonnegative_integer e.g. 123`
  - Enter reach for the last 7 days.
  - Evidence: Use the last-7-days reach value from Meta insights.
- Platform command: `python3 scripts/update_manual_social_stats.py facebook.reach_7d=VALUE --refresh-admin`

### instagram
- Status: `needs_values`; waiting: **1**; ready: **0**
- Open: https://www.instagram.com/lilyroo.artist/
- Why: Instagram posting could not resolve instagram_business_account from FB_PAGE_ID; set IG_BUSINESS_ACCOUNT_ID or reconnect the Instagram Business/Creator account to the Facebook Page
- CSV row `3` `profile_visits_7d` current `pending` -> `nonnegative_integer e.g. 12`
  - Enter profile visits for the last 7 days.
  - Evidence: Use the last-7-days profile visits value from the professional dashboard.
- Platform command: `python3 scripts/update_manual_social_stats.py instagram.profile_visits_7d=VALUE --refresh-admin`

### spotify
- Status: `needs_values`; waiting: **2**; ready: **0**
- Open: https://open.spotify.com/artist/4yzWmf64UKLwbAVwnDi49a
- Why: Spotify streams, saves, monthly listeners, and artist followers require Spotify for Artists export or a connected analytics source.
- CSV row `4` `release_streams` current `pending` -> `nonnegative_integer e.g. 1234`
  - Enter lifetime streams for the promoted release.
  - Evidence: Use lifetime streams for the promoted release from Spotify for Artists.
- CSV row `5` `saves` current `pending` -> `nonnegative_integer e.g. 12`
  - Enter lifetime saves for the promoted release.
  - Evidence: Use lifetime saves for the promoted release from Spotify for Artists.
- Platform command: `python3 scripts/update_manual_social_stats.py spotify.release_streams=VALUE spotify.saves=VALUE --refresh-admin`

### tiktok
- Status: `needs_values`; waiting: **1**; ready: **0**
- Open: https://www.tiktok.com/@lilyroo930
- Why: TikTok metrics need TikTok OAuth credentials.
- CSV row `6` `profile_views_7d` current `pending` -> `nonnegative_integer e.g. 12`
  - Enter profile views for the last 7 days.
  - Evidence: Use the last-7-days profile views value from TikTok analytics.
- Platform command: `python3 scripts/update_manual_social_stats.py tiktok.profile_views_7d=VALUE --refresh-admin`

### x
- Status: `needs_values`; waiting: **1**; ready: **0**
- Open: https://x.com/lilyrooartist
- Why: X metrics need X_USER_ACCESS_TOKEN with user lookup access.
- CSV row `7` `impressions_7d` current `pending` -> `nonnegative_integer e.g. 123`
  - Enter impressions for the last 7 days.
  - Evidence: Use the last-7-days impressions value from X analytics.
- Platform command: `python3 scripts/update_manual_social_stats.py x.impressions_7d=VALUE --refresh-admin`

## facebook

Source: Meta Business Suite > Insights
Open: https://www.facebook.com/903693509504290
Why: (#100) The value must be a valid insights metric

- CSV row `2` `reach_7d` current `pending` -> `VALUE` (nonnegative_integer; example `123`)
  - Enter reach for the last 7 days.
  - Import effect: update data/manual_social_stats.json facebook.reach_7d from 'pending' to the filled new_value

Command: `python3 scripts/update_manual_social_stats.py facebook.reach_7d=VALUE --refresh-admin`

## instagram

Source: Instagram Professional Dashboard > Insights
Open: https://www.instagram.com/lilyroo.artist/
Why: Instagram posting could not resolve instagram_business_account from FB_PAGE_ID; set IG_BUSINESS_ACCOUNT_ID or reconnect the Instagram Business/Creator account to the Facebook Page

- CSV row `3` `profile_visits_7d` current `pending` -> `VALUE` (nonnegative_integer; example `12`)
  - Enter profile visits for the last 7 days.
  - Import effect: update data/manual_social_stats.json instagram.profile_visits_7d from 'pending' to the filled new_value

Command: `python3 scripts/update_manual_social_stats.py instagram.profile_visits_7d=VALUE --refresh-admin`

## spotify

Source: Spotify for Artists > Music/Stats export
Open: https://open.spotify.com/artist/4yzWmf64UKLwbAVwnDi49a
Why: Spotify streams, saves, monthly listeners, and artist followers require Spotify for Artists export or a connected analytics source.

- CSV row `4` `release_streams` current `pending` -> `VALUE` (nonnegative_integer; example `1234`)
  - Enter lifetime streams for the promoted release.
  - Import effect: update data/manual_social_stats.json spotify.release_streams from 'pending' to the filled new_value
- CSV row `5` `saves` current `pending` -> `VALUE` (nonnegative_integer; example `12`)
  - Enter lifetime saves for the promoted release.
  - Import effect: update data/manual_social_stats.json spotify.saves from 'pending' to the filled new_value

Command: `python3 scripts/update_manual_social_stats.py spotify.release_streams=VALUE spotify.saves=VALUE --refresh-admin`

## tiktok

Source: TikTok Studio or Creator Center analytics
Open: https://www.tiktok.com/@lilyroo930
Why: TikTok metrics need TikTok OAuth credentials.

- CSV row `6` `profile_views_7d` current `pending` -> `VALUE` (nonnegative_integer; example `12`)
  - Enter profile views for the last 7 days.
  - Import effect: update data/manual_social_stats.json tiktok.profile_views_7d from 'pending' to the filled new_value

Command: `python3 scripts/update_manual_social_stats.py tiktok.profile_views_7d=VALUE --refresh-admin`

## x

Source: X Analytics or account profile metrics
Open: https://x.com/lilyrooartist
Why: X metrics need X_USER_ACCESS_TOKEN with user lookup access.

- CSV row `7` `impressions_7d` current `pending` -> `VALUE` (nonnegative_integer; example `123`)
  - Enter impressions for the last 7 days.
  - Import effect: update data/manual_social_stats.json x.impressions_7d from 'pending' to the filled new_value

Command: `python3 scripts/update_manual_social_stats.py x.impressions_7d=VALUE --refresh-admin`
