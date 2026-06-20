# Manual Metric Collection - Lily Roo

Generated: 2026-06-20T04:41:31.182929Z

Pending fields: **11**

Live-importable fields: **0**
Manual collection required: **11**

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
- Waiting fields: **11**
- Ready to import: **0**
- CSV: `data/manual_metric_collection_template.csv`
- Preview worksheet import: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
- Apply worksheet import after review: `python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`

### facebook
- Status: `needs_values`; waiting: **1**; ready: **0**
- Open: https://www.facebook.com/903693509504290
- Why: (#100) The value must be a valid insights metric
- CSV row `2` `reach_7d` current `pending` -> `nonnegative_integer e.g. 123`
  - Enter reach for the last 7 days.
- Platform command: `python3 scripts/update_manual_social_stats.py facebook.reach_7d=VALUE --refresh-admin`

### instagram
- Status: `needs_values`; waiting: **2**; ready: **0**
- Open: https://www.instagram.com/professional_dashboard/
- Why: Instagram posting could not resolve instagram_business_account from FB_PAGE_ID; set IG_BUSINESS_ACCOUNT_ID or reconnect the Instagram Business/Creator account to the Facebook Page
- CSV row `3` `followers` current `pending` -> `nonnegative_integer e.g. 123`
  - Enter the current public follower count.
- CSV row `4` `profile_visits_7d` current `pending` -> `nonnegative_integer e.g. 12`
  - Enter profile visits for the last 7 days.
- Platform command: `python3 scripts/update_manual_social_stats.py instagram.followers=VALUE instagram.profile_visits_7d=VALUE --refresh-admin`

### spotify
- Status: `needs_values`; waiting: **4**; ready: **0**
- Open: https://open.spotify.com/artist/4yzWmf64UKLwbAVwnDi49a
- Why: Spotify streams, saves, monthly listeners, and artist followers require Spotify for Artists export or a connected analytics source.
- CSV row `5` `artist_followers` current `pending` -> `nonnegative_integer e.g. 123`
  - Enter the current Spotify artist follower count.
- CSV row `6` `monthly_listeners` current `pending` -> `nonnegative_integer e.g. 123`
  - Enter the current Spotify monthly listener count.
- CSV row `7` `release_streams` current `pending` -> `nonnegative_integer e.g. 1234`
  - Enter lifetime streams for the promoted release.
- CSV row `8` `saves` current `pending` -> `nonnegative_integer e.g. 12`
  - Enter lifetime saves for the promoted release.
- Platform command: `python3 scripts/update_manual_social_stats.py spotify.artist_followers=VALUE spotify.monthly_listeners=VALUE spotify.release_streams=VALUE spotify.saves=VALUE --refresh-admin`

### tiktok
- Status: `needs_values`; waiting: **2**; ready: **0**
- Open: https://www.tiktok.com/creator-center/analytics
- Why: TikTok metrics need TikTok OAuth credentials.
- CSV row `9` `followers` current `pending` -> `nonnegative_integer e.g. 123`
  - Enter the current public follower count.
- CSV row `10` `profile_views_7d` current `pending` -> `nonnegative_integer e.g. 12`
  - Enter profile views for the last 7 days.
- Platform command: `python3 scripts/update_manual_social_stats.py tiktok.followers=VALUE tiktok.profile_views_7d=VALUE --refresh-admin`

### x
- Status: `needs_values`; waiting: **2**; ready: **0**
- Open: https://analytics.x.com/
- Why: X metrics need X_USER_ACCESS_TOKEN with user lookup access.
- CSV row `11` `followers` current `pending` -> `nonnegative_integer e.g. 123`
  - Enter the current public follower count.
- CSV row `12` `impressions_7d` current `pending` -> `nonnegative_integer e.g. 123`
  - Enter impressions for the last 7 days.
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
Open: https://www.instagram.com/professional_dashboard/
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

- CSV row `5` `artist_followers` current `pending` -> `VALUE` (nonnegative_integer; example `123`)
  - Enter the current Spotify artist follower count.
  - Import effect: update data/manual_social_stats.json spotify.artist_followers from 'pending' to the filled new_value
- CSV row `6` `monthly_listeners` current `pending` -> `VALUE` (nonnegative_integer; example `123`)
  - Enter the current Spotify monthly listener count.
  - Import effect: update data/manual_social_stats.json spotify.monthly_listeners from 'pending' to the filled new_value
- CSV row `7` `release_streams` current `pending` -> `VALUE` (nonnegative_integer; example `1234`)
  - Enter lifetime streams for the promoted release.
  - Import effect: update data/manual_social_stats.json spotify.release_streams from 'pending' to the filled new_value
- CSV row `8` `saves` current `pending` -> `VALUE` (nonnegative_integer; example `12`)
  - Enter lifetime saves for the promoted release.
  - Import effect: update data/manual_social_stats.json spotify.saves from 'pending' to the filled new_value

Command: `python3 scripts/update_manual_social_stats.py spotify.artist_followers=VALUE spotify.monthly_listeners=VALUE spotify.release_streams=VALUE spotify.saves=VALUE --refresh-admin`

## tiktok

Source: TikTok Studio or Creator Center analytics
Open: https://www.tiktok.com/creator-center/analytics
Why: TikTok metrics need TikTok OAuth credentials.

- CSV row `9` `followers` current `pending` -> `VALUE` (nonnegative_integer; example `123`)
  - Enter the current public follower count.
  - Import effect: update data/manual_social_stats.json tiktok.followers from 'pending' to the filled new_value
- CSV row `10` `profile_views_7d` current `pending` -> `VALUE` (nonnegative_integer; example `12`)
  - Enter profile views for the last 7 days.
  - Import effect: update data/manual_social_stats.json tiktok.profile_views_7d from 'pending' to the filled new_value

Command: `python3 scripts/update_manual_social_stats.py tiktok.followers=VALUE tiktok.profile_views_7d=VALUE --refresh-admin`

## x

Source: X Analytics or account profile metrics
Open: https://analytics.x.com/
Why: X metrics need X_USER_ACCESS_TOKEN with user lookup access.

- CSV row `11` `followers` current `pending` -> `VALUE` (nonnegative_integer; example `123`)
  - Enter the current public follower count.
  - Import effect: update data/manual_social_stats.json x.followers from 'pending' to the filled new_value
- CSV row `12` `impressions_7d` current `pending` -> `VALUE` (nonnegative_integer; example `123`)
  - Enter impressions for the last 7 days.
  - Import effect: update data/manual_social_stats.json x.impressions_7d from 'pending' to the filled new_value

Command: `python3 scripts/update_manual_social_stats.py x.followers=VALUE x.impressions_7d=VALUE --refresh-admin`
