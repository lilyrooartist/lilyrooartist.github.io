# Promo Operations Packet - Lily Roo

Generated: 2026-07-03T08:56:01.777327Z

## Summary
- Actions: **10**
- User review: **0**
- Platform fixes: **1**
- Scheduled approval batches: **0**
- Manual distribution actions: **0**
- Experiment result actions: **1**
- Store checks: **6**
- Manual metric updates: **2**
- Safe apply commands ready: **0**
- Urgency: **high: 2, low: 2, medium: 6**

## Phase Counts
- Collect experiment results: **1**
- Fill manual metrics: **2**
- Repair executor: **1**
- Verify music sites: **6**

## Top Actions

### Repair executor
- **[high] Fix TikTok upload-mode credentials**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Local upload-mode OAuth credentials missing: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. Complete TikTok OAuth setup locally, then push upload-mode secrets and refresh Admin.
  - Missing secrets: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
  - Missing locally: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
  - Local source: `secrets/social_api.env`
  - Public posting approved: `False`
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - Apply repair after preview: `python3 scripts/push_social_worker_secrets.py TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN && python3 scripts/refresh_promo_admin.py`

### Collect experiment results
- **[high] Collect experiment result metrics**
  - Why: 15 logged experiment post(s) have 81 result field(s) waiting; these results rank repeatable formats.
  - Detail: Fill measured result values with evidence notes, preview the import, then apply only after review.
  - Command: `python3 scripts/update_experiment_results.py --from-wide-csv data/experiment_result_entry_wide_template.csv --dry-run`
  - Packet: `admin/reports/experiment-result-clipboard.md`
  - Metric cards: **15**; pending fields: **81**
  - Measurement priorities: **12**
  - Wide entry CSV: `data/experiment_result_entry_wide_template.csv`
  - Preview result import: `python3 scripts/update_experiment_results.py --from-wide-csv data/experiment_result_entry_wide_template.csv --dry-run`

### Verify music sites
- **[medium] Re-check Twelve Dollars on Spotify**
  - Why: Public store links should be checked until DistroKid exposes them.
  - Detail: Searches public web results for Spotify album URLs, then validates exact-title candidates with Spotify oEmbed. Latest snapshot found no public URL; next recommended re-check after 2026-07-04T08:55:46.019701+00:00. Status: waiting_for_release_propagation.
  - Latest snapshot checked: `2026-07-03T08:55:46.019701+00:00`
  - Command: `python3 scripts/search_spotify_release.py --artist 'Lily Roo' --title 'Twelve Dollars' --out 'data/store-verification/twelve-dollars/spotify_release_snapshot.json'`
- **[medium] Re-check Twelve Dollars on Apple Music**
  - Why: Public store links should be checked until DistroKid exposes them.
  - Detail: Uses the public iTunes Search API; if it finds the release, copy release_url into data/distrokid_release_status.json. Latest snapshot found no public URL; next recommended re-check after 2026-07-04T08:55:48.370132+00:00. Status: waiting_for_release_propagation.
  - Latest snapshot checked: `2026-07-03T08:55:48.370132+00:00`
  - Command: `python3 scripts/capture_apple_music_release.py --artist 'Lily Roo' --title 'Twelve Dollars' --out 'data/store-verification/twelve-dollars/apple_music_release_snapshot.json'`
- **[medium] Re-check Twelve Dollars on HyperFollow**
  - Why: Public store links should be checked until DistroKid exposes them.
  - Detail: Captures the public HyperFollow store buttons; confirm the guessed URL if DistroKid used a different slug. Latest snapshot found no public URL; next recommended re-check after 2026-07-04T08:55:48.578797+00:00. Status: waiting_for_release_propagation.
  - Latest snapshot checked: `2026-07-03T08:55:48.578797+00:00`
  - Command: `python3 scripts/capture_hyperfollow_store_links.py --url 'https://distrokid.com/hyperfollow/lilyroo/twelve-dollars' --out 'data/store-verification/twelve-dollars/hyperfollow_store_links_snapshot.json'`
- **[medium] Re-check Analog Myth on Spotify**
  - Why: Public store links should be checked as the July 1 release approaches.
  - Detail: Searches public web results for Spotify album URLs, then validates exact-title candidates with Spotify oEmbed. Latest snapshot found no public URL; next recommended re-check after 2026-07-04T08:55:48.637762+00:00. Status: waiting_for_release_propagation.
  - Latest snapshot checked: `2026-07-03T08:55:48.637762+00:00`
  - Command: `python3 scripts/search_spotify_release.py --artist 'Lily Roo' --title 'Analog Myth' --out 'data/store-verification/analog-myth/spotify_release_snapshot.json'`
- **[medium] Re-check Analog Myth on YouTube Music**
  - Why: Public store links should be checked as the July 1 release approaches.
  - Detail: Searches public web results for YouTube Music watch URLs, then validates the public title. Latest snapshot found no public URL; next recommended re-check after 2026-07-04T08:55:49.333408+00:00. Status: waiting_for_release_propagation.
  - Latest snapshot checked: `2026-07-03T08:55:49.333408+00:00`
  - Command: `python3 scripts/search_youtube_music_release.py --artist 'Lily Roo' --title 'Analog Myth' --out 'data/store-verification/analog-myth/youtube_music_release_snapshot.json'`
- **[medium] Re-check Analog Myth on HyperFollow**
  - Why: Public store links should be checked as the July 1 release approaches.
  - Detail: Captures the public HyperFollow store buttons; confirm the guessed URL if DistroKid used a different slug. Latest snapshot found no public URL; next recommended re-check after 2026-07-04T08:55:50.075048+00:00. Status: waiting_for_release_propagation.
  - Latest snapshot checked: `2026-07-03T08:55:50.075048+00:00`
  - Command: `python3 scripts/capture_hyperfollow_store_links.py --url 'https://distrokid.com/hyperfollow/lilyroo/analog-myth' --out 'data/store-verification/analog-myth/hyperfollow_store_links_snapshot.json'`

### Fill manual metrics
- **[low] Fill priority 2 metrics: Recent discovery and traffic**
  - Why: Manual metric gaps affect reporting, not publishing.
  - Detail: facebook.reach_7d, instagram.profile_visits_7d, tiktok.profile_views_7d, x.impressions_7d
  - Command: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Packet: `admin/reports/manual-metric-collection.md`
  - Access: `private_analytics`
  - CSV rows: `2, 3, 6, 7`
  - Import filled worksheet: `python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`
- **[low] Fill priority 3 metrics: Release depth metrics**
  - Why: Manual metric gaps affect reporting, not publishing.
  - Detail: spotify.release_streams, spotify.saves
  - Command: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Packet: `admin/reports/manual-metric-collection.md`
  - Access: `private_analytics`
  - CSV rows: `4, 5`
  - Import filled worksheet: `python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`

## Guardrails
- This packet does not publish, approve, apply, or post anything.
- Review copy before running approval commands.
- Apply commands only move already-approved rows into the local/live queue; they do not directly post externally.
