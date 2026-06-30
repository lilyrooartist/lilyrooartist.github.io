# Analog Myth Launch Promo Pack

Release: Analog Myth  
Launch date: July 1, 2026  
Album page: https://www.lilyroo.com/analog-myth.html  
Podcast episode: https://www.lilyroo.com/podcasts/analog-myth.html  
Podcast RSS: https://www.lilyroo.com/podcasts/feed.xml  
Playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0  
Release hub: https://distrokid.com/hyperfollow/lilyroo/analog-myth  
Primary streaming CTA: add the verified Spotify album URL with `python3 scripts/run_analog_myth_launch.py --apply --live`; publish Spotify-specific copy only after the post-deploy live check passes.

## Launch Gate

Do not publish a Spotify-specific CTA until `python3 scripts/check_analog_myth_launch_readiness.py --require-store-links --live` returns zero failures after the launch-link deploy.

Pre-store-link CTA:

- Open the Analog Myth launch page: https://www.lilyroo.com/analog-myth.html
- Hear the Echo Thread podcast episode: https://www.lilyroo.com/podcasts/analog-myth.html
- Watch the remastered album playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0

Post-store-link CTA:

- Listen on Spotify: `TBD_VERIFIED_SPOTIFY_ALBUM_URL`
- Album page: https://www.lilyroo.com/analog-myth.html
- Podcast episode: https://www.lilyroo.com/podcasts/analog-myth.html

## Platform Hooks

- X: Analog Myth is the clock lying politely while the songs keep receipts.
- Facebook: Analog Myth goes live July 1, with the Echo Thread podcast episode ready for the track-by-track walk-through.

## Automated Launch-Day Posts

These rows are queued in `data/scheduled_posts.csv` and generated into `admin/future-posts.json`.

- `FP-LAUNCH-ANALOG-MYTH-X` at 2026-07-01T00:45:00-04:00
- `FP-LAUNCH-ANALOG-MYTH-FACEBOOK` at 2026-07-01T00:55:00-04:00

### X

Analog Myth is live.

Eight songs, one broken clock, and a podcast episode for the track-by-track walk-through.

Album: https://www.lilyroo.com/analog-myth.html
Podcast: https://www.lilyroo.com/podcasts/analog-myth.html

### Facebook

Analog Myth, the eight-song Lily Roo album, goes live July 1.

The launch page includes the album, the remastered playlist, cover art, and the new Echo Thread podcast episode: The Clock Cannot Explain This.

Album page: https://www.lilyroo.com/analog-myth.html
Podcast: https://www.lilyroo.com/podcasts/analog-myth.html

## Post-Store-Link Variants

Use these only after the verified Spotify URL replaces `TBD_VERIFIED_SPOTIFY_ALBUM_URL`.

### X

Analog Myth is live on Spotify.

Listen: TBD_VERIFIED_SPOTIFY_ALBUM_URL
Podcast: https://www.lilyroo.com/podcasts/analog-myth.html

## Hashtags

#LilyRoo #AnalogMyth #NewAlbum #NewMusic #IndieArtist #SingerSongwriter #Podcast #MusicPodcast #AlbumRelease #IndieMusic #EchoThread

## Assets

- Album cover: https://www.lilyroo.com/assets/albums/analog-myth/art/03-analog-myth.jpg
- Podcast poster: https://www.lilyroo.com/assets/podcasts/analog-myth/analog-myth-podcast-poster.jpg
- Podcast directory art: https://www.lilyroo.com/assets/podcasts/analog-myth/analog-myth-podcast-directory-art-3000.jpg
- Podcast audio: https://www.lilyroo.com/assets/podcasts/analog-myth/analog-myth-the-clock-cannot-explain-this.m4a

## Launch-Day Operator Checklist

1. Run `python3 scripts/run_analog_myth_launch.py --live`.
2. Follow the runner's `next_commands`; if store links verify, it should point to `python3 scripts/run_analog_myth_launch.py --apply --live`.
   If the store search lags but a real public Spotify album URL is visible, run `python3 scripts/run_analog_myth_launch.py --live --spotify-url VERIFIED_SPOTIFY_ALBUM_URL`; the runner will preserve that URL in its apply command.
   The manual URL check must validate Spotify title `Analog Myth` and artist `Lily Roo`; do not use the apply command if it reports any title or artist mismatch.
   If adding optional Apple Music or YouTube Music URLs manually, include `--apple-music-url` or `--youtube-music-url` in the same runner command and require those links to be validated as `Analog Myth` by `Lily Roo`.
   When optional store URLs are supplied, use the runner's printed `next_commands` apply command so those optional URL arguments are preserved.
   If that manual-URL check reports `launch_ready: true`, the direct apply command is `python3 scripts/run_analog_myth_launch.py --apply --live --spotify-url VERIFIED_SPOTIFY_ALBUM_URL`.
3. Confirm the apply runner reports `launch_ready: true`, `local_launch_ready: true`, `public_launch_ready: false`, and prints both `next_commands` and `post_deploy_live_check`. Treat any apply run as local-only until the post-deploy live check passes.
4. Commit and push the launch-link changes.
5. After GitHub Pages deploys, run `python3 scripts/check_analog_myth_launch_readiness.py --require-store-links --live`.
6. Confirm the post-deploy live check returns zero failures; that is the public launch-ready proof.
7. Publish Spotify-specific captions only after the post-deploy live check passes.
8. Replace `TBD_VERIFIED_SPOTIFY_ALBUM_URL` in any copied captions before using Spotify-specific variants.
