# Manual Metric Collection - Lily Roo

Generated: 2026-06-15T12:44:07.774655Z

Pending fields: **11**

Fill `new_value` in `data/manual_metric_collection_template.csv`, then run:

`python3 scripts/update_manual_social_stats.py --from-csv --dry-run`

If the preview looks right, run:

`python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`

You can still run a platform update command directly if you only collect one platform.

## facebook

Source: Meta Business Suite > Insights
Open: https://www.facebook.com/903693509504290
Why: Facebook reach requires Page insights access or manual Meta Business Suite export.

- `reach_7d` current `pending` -> `VALUE`

Command: `python3 scripts/update_manual_social_stats.py facebook.reach_7d=VALUE --refresh-admin`

## instagram

Source: Instagram Professional Dashboard > Insights
Open: https://www.instagram.com/professional_dashboard/
Why: Instagram posting could not resolve instagram_business_account from FB_PAGE_ID; set IG_BUSINESS_ACCOUNT_ID or reconnect the Instagram Business/Creator account to the Facebook Page

- `followers` current `pending` -> `VALUE`
- `profile_visits_7d` current `pending` -> `VALUE`

Command: `python3 scripts/update_manual_social_stats.py instagram.followers=VALUE instagram.profile_visits_7d=VALUE --refresh-admin`

## spotify

Source: Spotify for Artists > Music/Stats export
Open: https://open.spotify.com/artist/4yzWmf64UKLwbAVwnDi49a
Why: Spotify streams, saves, monthly listeners, and artist followers require Spotify for Artists export or a connected analytics source.

- `artist_followers` current `pending` -> `VALUE`
- `monthly_listeners` current `pending` -> `VALUE`
- `release_streams` current `pending` -> `VALUE`
- `saves` current `pending` -> `VALUE`

Command: `python3 scripts/update_manual_social_stats.py spotify.artist_followers=VALUE spotify.monthly_listeners=VALUE spotify.release_streams=VALUE spotify.saves=VALUE --refresh-admin`

## tiktok

Source: TikTok Studio or Creator Center analytics
Open: https://www.tiktok.com/creator-center/analytics
Why: TikTok metrics need TikTok OAuth credentials.

- `followers` current `pending` -> `VALUE`
- `profile_views_7d` current `pending` -> `VALUE`

Command: `python3 scripts/update_manual_social_stats.py tiktok.followers=VALUE tiktok.profile_views_7d=VALUE --refresh-admin`

## x

Source: X Analytics or account profile metrics
Open: https://analytics.x.com/
Why: X metrics need X_USER_ACCESS_TOKEN with user lookup access.

- `followers` current `pending` -> `VALUE`
- `impressions_7d` current `pending` -> `VALUE`

Command: `python3 scripts/update_manual_social_stats.py x.followers=VALUE x.impressions_7d=VALUE --refresh-admin`
