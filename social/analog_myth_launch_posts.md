# Analog Myth Launch Promo Pack

Release: Analog Myth  
Launch date: July 1, 2026  
Album page: https://www.lilyroo.com/analog-myth.html  
Podcast episode: https://www.lilyroo.com/podcasts/analog-myth.html  
Podcast RSS: https://www.lilyroo.com/podcasts/feed.xml  
Playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0  
Release hub: https://distrokid.com/hyperfollow/lilyroo/analog-myth  
Primary streaming CTA: add verified Spotify album URL after `python3 scripts/run_analog_myth_launch.py --apply --live` succeeds.

## Launch Gate

Do not publish a Spotify-specific CTA until the launch runner reports `launch_ready: true` and the public site has been updated with the verified store link.

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
- Instagram: Analog Myth is an eight-song room of clocks, camp smoke, tea, tiny-house freedom, and light that keeps coming back.
- TikTok: Time broke. The songs kept moving.
- Facebook: Analog Myth goes live July 1, with the Echo Thread podcast episode ready for the track-by-track walk-through.
- YouTube Community: New transmission: Analog Myth arrives July 1. The remastered playlist and podcast episode are live on lilyroo.com.

## Launch-Day Posts

### X

Analog Myth is live.

Eight songs, one broken clock, and a podcast episode for the track-by-track walk-through.

Album: https://www.lilyroo.com/analog-myth.html
Podcast: https://www.lilyroo.com/podcasts/analog-myth.html

### Instagram

Analog Myth is live July 1.

Eight songs from the room where time keeps trying to explain itself and failing: 13, Girls Camp, Analog Myth, Spilling the Tea, No Mortgage, Guards Down, Slow Walk, and The Power of Light.

The Echo Thread podcast episode is also live for the track-by-track conversation.

Album page: lilyroo.com/analog-myth.html
Podcast: lilyroo.com/podcasts/analog-myth.html

### TikTok

Analog Myth is live July 1.

The clock cannot explain this.

Album + podcast: lilyroo.com

### Facebook

Analog Myth, the eight-song Lily Roo album, goes live July 1.

The launch page includes the album, the remastered playlist, cover art, and the new Echo Thread podcast episode: The Clock Cannot Explain This.

Album page: https://www.lilyroo.com/analog-myth.html
Podcast: https://www.lilyroo.com/podcasts/analog-myth.html

### YouTube Community

Analog Myth arrives July 1.

The full remastered playlist is ready, and the Echo Thread podcast episode is live for the track-by-track conversation.

Playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0
Album page: https://www.lilyroo.com/analog-myth.html

## Post-Store-Link Variants

Use these only after the verified Spotify URL replaces `TBD_VERIFIED_SPOTIFY_ALBUM_URL`.

### X

Analog Myth is live on Spotify.

Listen: TBD_VERIFIED_SPOTIFY_ALBUM_URL
Podcast: https://www.lilyroo.com/podcasts/analog-myth.html

### Instagram

Analog Myth is live on Spotify.

Listen there, then open the Echo Thread episode for the track-by-track story behind the album.

Spotify: TBD_VERIFIED_SPOTIFY_ALBUM_URL
Podcast: lilyroo.com/podcasts/analog-myth.html

### TikTok

Analog Myth is live on Spotify.

Eight songs. One suspicious clock.

TBD_VERIFIED_SPOTIFY_ALBUM_URL

## Hashtags

#LilyRoo #AnalogMyth #NewAlbum #NewMusic #IndieArtist #SingerSongwriter #Podcast #MusicPodcast #AlbumRelease #IndieMusic #EchoThread

## Assets

- Album cover: https://www.lilyroo.com/assets/albums/analog-myth/art/03-analog-myth.jpg
- Podcast poster: https://www.lilyroo.com/assets/podcasts/analog-myth/analog-myth-podcast-poster.jpg
- Podcast directory art: https://www.lilyroo.com/assets/podcasts/analog-myth/analog-myth-podcast-directory-art-3000.jpg
- Podcast audio: https://www.lilyroo.com/assets/podcasts/analog-myth/analog-myth-the-clock-cannot-explain-this.m4a

## Launch-Day Operator Checklist

1. Run `python3 scripts/run_analog_myth_launch.py --live`.
2. If store links verify, run `python3 scripts/run_analog_myth_launch.py --apply --live`.
3. Confirm the runner reports `launch_ready: true`, `local_launch_ready: true`, `public_launch_ready: false`, and prints `post_deploy_live_check`.
4. Commit and push the launch-link changes.
5. After GitHub Pages deploys, run `python3 scripts/check_analog_myth_launch_readiness.py --require-store-links --live`.
6. Confirm the post-deploy live check returns zero failures; that is the public launch-ready proof.
7. Publish Spotify-specific captions only after the post-deploy live check passes.
8. Replace `TBD_VERIFIED_SPOTIFY_ALBUM_URL` in any copied captions before using Spotify-specific variants.
