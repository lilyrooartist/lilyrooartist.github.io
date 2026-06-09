# Promo Operations Packet - Lily Roo

Generated: 2026-06-09T22:14:45.586671Z

## Summary
- Actions: **20**
- User review: **6**
- Platform fixes: **2**
- Store checks: **7**
- Manual metric updates: **5**
- Safe apply commands ready: **0**

## Top Actions
- **Fix Facebook executor**
  - Detail: Facebook blocked Page publishing until identity is confirmed in the Facebook app.
  - Command: `python3 scripts/check_facebook_publishing.py --post-id 'FP-AUTO-265' --check-worker-dry-run`
- **Fix Instagram executor**
  - Detail: Instagram posting could not resolve instagram_business_account; reconnect or set IG_BUSINESS_ACCOUNT_ID.
  - Command: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
- **Review Facebook draft for Twelve Dollars**
  - Detail: Ready after approval.
  - Command: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-FACEBOOK --refresh-admin`
- **Review Instagram draft for Twelve Dollars**
  - Detail: Ready after approval.
  - Command: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM --refresh-admin`
- **Review X draft for Twelve Dollars**
  - Detail: Ready after approval.
  - Command: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-X --refresh-admin`
- **Review YouTube Community draft for Analog Myth**
  - Detail: YouTube Community posts are copy-ready manual workflow.
  - Command: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --refresh-admin`
- **Review YouTube Community draft for Twelve Dollars**
  - Detail: YouTube Community posts are copy-ready manual workflow.
  - Command: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --refresh-admin`
- **Verify Analog Myth on Apple Music**
  - Command: `python3 scripts/capture_apple_music_release.py --artist 'Lily Roo' --title 'Analog Myth' --out 'data/store-verification/analog-myth/apple_music_release_snapshot.json'`
- **Verify Analog Myth on HyperFollow**
  - Command: `python3 scripts/capture_hyperfollow_store_links.py --url 'https://distrokid.com/hyperfollow/lilyroo/analog-myth' --out 'data/store-verification/analog-myth/hyperfollow_store_links_snapshot.json'`
- **Verify Analog Myth on Spotify**
  - Command: `open 'https://open.spotify.com/search/analog%20myth%20Lily%20Roo/albums' && python3 scripts/capture_spotify_release.py --release-url SPOTIFY_ALBUM_URL --out 'data/store-verification/analog-myth/spotify_release_snapshot.json'`
- **Verify Analog Myth on YouTube Music**
  - Command: `python3 scripts/capture_youtube_music_release.py --url YOUTUBE_MUSIC_URL --title 'Analog Myth' --out 'data/store-verification/analog-myth/youtube_music_release_snapshot.json'`
- **Verify Twelve Dollars on Apple Music**
  - Command: `python3 scripts/capture_apple_music_release.py --artist 'Lily Roo' --title 'Twelve Dollars' --out 'data/store-verification/twelve-dollars/apple_music_release_snapshot.json'`

## Guardrails
- This packet does not publish, approve, apply, or post anything.
- Review copy before running approval commands.
- Apply commands only move already-approved rows into the local/live queue; they do not directly post externally.
