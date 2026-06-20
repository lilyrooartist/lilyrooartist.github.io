# Manual Metric Collection - Lily Roo

Generated: 2026-06-20T06:40:00.287982Z

Pending fields: **8**

Live-importable fields: **0**
Manual collection required: **8**

Fill `new_value` in `data/manual_metric_collection_template.csv`, then run:

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
- Waiting fields: **8**
- Ready to import: **0**
- CSV: `data/manual_metric_collection_template.csv`
- Preview worksheet import: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
- Apply worksheet import after review: `python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`

## Public Metric Capture Backlog

- Fields: **2**
- Status: **needs_capture_adapter**
- Engine work: Add safe public profile capture adapters for these public fields, then route them through data/live_social_metrics.json and scripts/update_manual_social_stats.py --from-live.
- Guardrail: Do not treat private analytics fields as public-capture candidates.

- CSV row `3` `instagram.followers`
  - Public/source URL: https://www.instagram.com/lilyroo.artist/
  - Evidence: Capture the public follower count from the profile page or account dashboard.
- CSV row `8` `x.followers`
  - Public/source URL: https://x.com/lilyrooartist
  - Evidence: Capture the public follower count from the profile page or account dashboard.

### Priority 1: Audience size snapshot
- Status: `needs_values`; waiting: **2**; ready: **0**
- Platforms: `instagram, x`
- Access: `public_profile`
- CSV rows: `3, 8`
- Row `3` `instagram.followers`
  - Enter the current public follower count.
  - Evidence: Capture the public follower count from the profile page or account dashboard.
- Row `8` `x.followers`
  - Enter the current public follower count.
  - Evidence: Capture the public follower count from the profile page or account dashboard.

### Priority 2: Recent discovery and traffic
- Status: `needs_values`; waiting: **4**; ready: **0**
- Platforms: `facebook, instagram, tiktok, x`
- Access: `private_analytics`
- CSV rows: `2, 4, 7, 9`
- Row `2` `facebook.reach_7d`
  - Enter reach for the last 7 days.
  - Evidence: Use the last-7-days reach value from Meta insights.
- Row `4` `instagram.profile_visits_7d`
  - Enter profile visits for the last 7 days.
  - Evidence: Use the last-7-days profile visits value from the professional dashboard.
- Row `7` `tiktok.profile_views_7d`
  - Enter profile views for the last 7 days.
  - Evidence: Use the last-7-days profile views value from TikTok analytics.
- Row `9` `x.impressions_7d`
  - Enter impressions for the last 7 days.
  - Evidence: Use the last-7-days impressions value from X analytics.

### Priority 3: Release depth metrics
- Status: `needs_values`; waiting: **2**; ready: **0**
- Platforms: `spotify`
- Access: `private_analytics`
- CSV rows: `5, 6`
- Row `5` `spotify.release_streams`
  - Enter lifetime streams for the promoted release.
  - Evidence: Use lifetime streams for the promoted release from Spotify for Artists.
- Row `6` `spotify.saves`
  - Enter lifetime saves for the promoted release.
  - Evidence: Use lifetime saves for the promoted release from Spotify for Artists.

## Worksheet Import Manifest

- Status: **needs_values**
- Ready rows: **0**
- Waiting rows: **8**
- Preview: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
- Apply after review: `blocked until new_value cells are filled`
- Apply gate: **blocked_until_new_values_filled**
- Guardrail: Import only filled nonnegative numeric new_value cells; leave unknown rows blank.

### facebook
- Status: `needs_values`; waiting: **1**; ready: **0**
- Open: https://www.facebook.com/903693509504290
- Why: (#100) The value must be a valid insights metric
- CSV row `2` `reach_7d` current `pending` -> `nonnegative_integer e.g. 123`
  - Enter reach for the last 7 days.
  - Evidence: Use the last-7-days reach value from Meta insights.
- Platform command: `python3 scripts/update_manual_social_stats.py facebook.reach_7d=VALUE --refresh-admin`

### instagram
- Status: `needs_values`; waiting: **2**; ready: **0**
- Open: https://www.instagram.com/lilyroo.artist/
- Why: Instagram posting could not resolve instagram_business_account from FB_PAGE_ID; set IG_BUSINESS_ACCOUNT_ID or reconnect the Instagram Business/Creator account to the Facebook Page
- CSV row `3` `followers` current `pending` -> `nonnegative_integer e.g. 123`
  - Enter the current public follower count.
  - Evidence: Capture the public follower count from the profile page or account dashboard.
- CSV row `4` `profile_visits_7d` current `pending` -> `nonnegative_integer e.g. 12`
  - Enter profile visits for the last 7 days.
  - Evidence: Use the last-7-days profile visits value from the professional dashboard.
- Platform command: `python3 scripts/update_manual_social_stats.py instagram.followers=VALUE instagram.profile_visits_7d=VALUE --refresh-admin`

### spotify
- Status: `needs_values`; waiting: **2**; ready: **0**
- Open: https://open.spotify.com/artist/4yzWmf64UKLwbAVwnDi49a
- Why: Spotify streams, saves, monthly listeners, and artist followers require Spotify for Artists export or a connected analytics source.
- CSV row `5` `release_streams` current `pending` -> `nonnegative_integer e.g. 1234`
  - Enter lifetime streams for the promoted release.
  - Evidence: Use lifetime streams for the promoted release from Spotify for Artists.
- CSV row `6` `saves` current `pending` -> `nonnegative_integer e.g. 12`
  - Enter lifetime saves for the promoted release.
  - Evidence: Use lifetime saves for the promoted release from Spotify for Artists.
- Platform command: `python3 scripts/update_manual_social_stats.py spotify.release_streams=VALUE spotify.saves=VALUE --refresh-admin`

### tiktok
- Status: `needs_values`; waiting: **1**; ready: **0**
- Open: https://www.tiktok.com/@lilyroo930
- Why: TikTok metrics need TikTok OAuth credentials.
- CSV row `7` `profile_views_7d` current `pending` -> `nonnegative_integer e.g. 12`
  - Enter profile views for the last 7 days.
  - Evidence: Use the last-7-days profile views value from TikTok analytics.
- Platform command: `python3 scripts/update_manual_social_stats.py tiktok.profile_views_7d=VALUE --refresh-admin`

### x
- Status: `needs_values`; waiting: **2**; ready: **0**
- Open: https://x.com/lilyrooartist
- Why: X metrics need X_USER_ACCESS_TOKEN with user lookup access.
- CSV row `8` `followers` current `pending` -> `nonnegative_integer e.g. 123`
  - Enter the current public follower count.
  - Evidence: Capture the public follower count from the profile page or account dashboard.
- CSV row `9` `impressions_7d` current `pending` -> `nonnegative_integer e.g. 123`
  - Enter impressions for the last 7 days.
  - Evidence: Use the last-7-days impressions value from X analytics.
- Platform command: `python3 scripts/update_manual_social_stats.py x.followers=VALUE x.impressions_7d=VALUE --refresh-admin`

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

- CSV row `3` `followers` current `pending` -> `VALUE` (nonnegative_integer; example `123`)
  - Enter the current public follower count.
  - Import effect: update data/manual_social_stats.json instagram.followers from 'pending' to the filled new_value
- CSV row `4` `profile_visits_7d` current `pending` -> `VALUE` (nonnegative_integer; example `12`)
  - Enter profile visits for the last 7 days.
  - Import effect: update data/manual_social_stats.json instagram.profile_visits_7d from 'pending' to the filled new_value

Command: `python3 scripts/update_manual_social_stats.py instagram.followers=VALUE instagram.profile_visits_7d=VALUE --refresh-admin`

## spotify

Source: Spotify for Artists > Music/Stats export
Open: https://open.spotify.com/artist/4yzWmf64UKLwbAVwnDi49a
Why: Spotify streams, saves, monthly listeners, and artist followers require Spotify for Artists export or a connected analytics source.

- CSV row `5` `release_streams` current `pending` -> `VALUE` (nonnegative_integer; example `1234`)
  - Enter lifetime streams for the promoted release.
  - Import effect: update data/manual_social_stats.json spotify.release_streams from 'pending' to the filled new_value
- CSV row `6` `saves` current `pending` -> `VALUE` (nonnegative_integer; example `12`)
  - Enter lifetime saves for the promoted release.
  - Import effect: update data/manual_social_stats.json spotify.saves from 'pending' to the filled new_value

Command: `python3 scripts/update_manual_social_stats.py spotify.release_streams=VALUE spotify.saves=VALUE --refresh-admin`

## tiktok

Source: TikTok Studio or Creator Center analytics
Open: https://www.tiktok.com/@lilyroo930
Why: TikTok metrics need TikTok OAuth credentials.

- CSV row `7` `profile_views_7d` current `pending` -> `VALUE` (nonnegative_integer; example `12`)
  - Enter profile views for the last 7 days.
  - Import effect: update data/manual_social_stats.json tiktok.profile_views_7d from 'pending' to the filled new_value

Command: `python3 scripts/update_manual_social_stats.py tiktok.profile_views_7d=VALUE --refresh-admin`

## x

Source: X Analytics or account profile metrics
Open: https://x.com/lilyrooartist
Why: X metrics need X_USER_ACCESS_TOKEN with user lookup access.

- CSV row `8` `followers` current `pending` -> `VALUE` (nonnegative_integer; example `123`)
  - Enter the current public follower count.
  - Import effect: update data/manual_social_stats.json x.followers from 'pending' to the filled new_value
- CSV row `9` `impressions_7d` current `pending` -> `VALUE` (nonnegative_integer; example `123`)
  - Enter impressions for the last 7 days.
  - Import effect: update data/manual_social_stats.json x.impressions_7d from 'pending' to the filled new_value

Command: `python3 scripts/update_manual_social_stats.py x.followers=VALUE x.impressions_7d=VALUE --refresh-admin`
