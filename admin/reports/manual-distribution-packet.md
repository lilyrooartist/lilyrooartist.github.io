# Manual Distribution Packet - Lily Roo

Generated: 2026-06-22T11:48:31.357930Z

## Summary
- Manual-ready posts: **3**
- YouTube Community posts: **3**
- Hard subscriber CTAs: **0**
- Approved manual posts: **3**
- Logged manual posts: **0**
- Unlogged manual posts: **3**
- Public URL logs still needed: **3**

## Manual Posting Docket
- Status: **postable_now**
- Needs review: **0**
- Postable now: **3**
- Logged: **0**
- Public community surface: https://www.youtube.com/@lilyroo.artist/community

### Approval Gate
- Status: **clear**
- Ready approvals: **0**
- Blocked approvals: **1**
- Blocked IDs: `FP-PLAN-TWELVE-DOLLARS-TIKTOK`
- Guardrail: Manual-only approvals do not auto-post; posting and public URL logging remain separate after review.

### Completion Manifest
- Status: **ready_to_post_and_log**
- Review queue IDs: `none`
- Postable now IDs: `FP-AUTO-261, FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY, FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY`
- Pending log IDs: `FP-AUTO-261, FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY, FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY`
- Posting surface: YouTube Studio Community
- Public community URL: https://www.youtube.com/@lilyroo.artist/community
- Public URL worksheet: `data/manual_distribution_url_template.csv`
- Batch URL log preview: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv`
- Batch URL log apply after posting: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --apply --refresh-admin`
- URL worksheet rows waiting: **3**
- Operator checklist:
  - Review the packaged copy, asset, destination link evidence, and subscriber CTA.
  - Run the approval preview command before applying any manual approval.
  - Post approved rows manually in YouTube Studio Community.
  - Copy the real individual public Community post URL after posting; it should look like https://www.youtube.com/post/...
  - Paste public URLs into data/manual_distribution_url_template.csv for batch logging.
  - Run the log preview command with the real URL, then apply with --apply --refresh-admin.
- Completion evidence:
  - data/manual_distribution_packet.json shows the row as logged or no longer pending.
  - data/published_log_reconciliation.json no longer reports the row as an unlogged manual post.
  - admin/content/Published_Log.csv contains the real public URL and manual_distribution_id note.
  - data/promo_engine_status.json and lilyroo.com/admin reflect the updated manual distribution counts.
- Guardrails:
  - Manual-only approvals do not auto-post.
  - Do not log a placeholder URL.
  - For YouTube Community rows, log an individual https://www.youtube.com/post/... URL, not the channel, playlist, video, or Community tab URL.
  - Do not apply the URL worksheet while any public_url cell is blank.
  - Do not mark manual distribution complete until a real public YouTube Community URL is logged.

### Needs Review
- None

### Postable Now
- **YouTube Community - I Learned It All in Fifteen Seconds** (`FP-AUTO-261`)
  - Paste text: New transmission: I Learned It All in Fifteen Seconds is live. Remastered cover art, same suspicious amount of feeling.

Stream: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi | Apple Music: https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249 | YouTube: https://www.youtube.com/@lilyroo.artist | YouTube Music: https://music.youtube.com/watch?v=vK0mDIW65o4
  - Asset: https://www.lilyroo.com/assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg
  - Log preview after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url 'PUBLIC_URL'`
  - Log apply after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url 'PUBLIC_URL' --apply --refresh-admin`
- **YouTube Community - Twelve Dollars** (`FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY`)
  - Paste text: Twelve Dollars is part of the Lily Roo archive now. Help us build the signal to 1,000 subscribers.

Full playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
  - Asset: https://www.lilyroo.com/assets/albums/twelve-dollars/art/04-twelve-dollars.jpg
  - Log preview after posting: `python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url 'PUBLIC_URL'`
  - Log apply after posting: `python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url 'PUBLIC_URL' --apply --refresh-admin`
- **YouTube Community - Analog Myth** (`FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY`)
  - Paste text: Analog Myth is part of the Lily Roo archive now. Help us build the signal to 1,000 subscribers.

Full playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0
  - Asset: https://www.lilyroo.com/assets/albums/analog-myth/art/03-analog-myth.jpg
  - Log preview after posting: `python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url 'PUBLIC_URL'`
  - Log apply after posting: `python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url 'PUBLIC_URL' --apply --refresh-admin`

## Manual Posting Queue
- **YouTube Community - I Learned It All in Fifteen Seconds** (`FP-AUTO-261`)
  - Scheduled target: `2026-06-06T19:10:00-04:00`
  - Distribution status: `ready_for_manual_post`
  - Readiness: ``; CTA: ``
  - Copy: New transmission: I Learned It All in Fifteen Seconds is live. Remastered cover art, same suspicious amount of feeling.
  - Link/reply: Stream: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi | Apple Music: https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249 | YouTube: https://www.youtube.com/@lilyroo.artist | YouTube Music: https://music.youtube.com/watch?v=vK0mDIW65o4
  - Paste block:
    New transmission: I Learned It All in Fifteen Seconds is live. Remastered cover art, same suspicious amount of feeling.
    
    Stream: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi | Apple Music: https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249 | YouTube: https://www.youtube.com/@lilyroo.artist | YouTube Music: https://music.youtube.com/watch?v=vK0mDIW65o4
  - Asset: https://www.lilyroo.com/assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg
  - Asset evidence: `local_asset_present` assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg
  - Destination link evidence:
    - `verified_local_evidence` https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi: HyperFollow public store link: spotify (data/hyperfollow_store_links_snapshot.json)
    - `verified_local_evidence` https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249: Apple Music public snapshot: release (data/apple_music_release_snapshot.json)
    - `verified_local_evidence` https://www.youtube.com/@lilyroo.artist: YouTube channel author URL (data/youtube_title_track_snapshot.json)
    - `verified_local_evidence` https://music.youtube.com/watch?v=vK0mDIW65o4: I Learned It All in Fifteen Seconds YouTube Music URL (data/distrokid_release_status.json); YouTube Music public snapshot: release (data/youtube_music_release_snapshot.json)
  - Next manual action: `post_manually_then_log_url`
  - Postable now: `True`; approval required: `False`; logging required: `True`
  - Public community surface: https://www.youtube.com/@lilyroo.artist/community
  - Next command: `python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url 'PUBLIC_URL'`
  - Log effect: append Published_Log.csv content_id=FP-AUTO-261 after public URL is available
  - Preview public URL log: `python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url 'PUBLIC_URL'`
  - Apply public URL log after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url 'PUBLIC_URL' --apply --refresh-admin`
- **YouTube Community - Twelve Dollars** (`FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY`)
  - Scheduled target: `2026-06-24T18:30:00-04:00`
  - Distribution status: `ready_for_manual_post`
  - Readiness: ``; CTA: ``
  - Copy: Twelve Dollars is part of the Lily Roo archive now. Help us build the signal to 1,000 subscribers.
  - Link/reply: Full playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
  - Paste block:
    Twelve Dollars is part of the Lily Roo archive now. Help us build the signal to 1,000 subscribers.
    
    Full playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
  - Asset: https://www.lilyroo.com/assets/albums/twelve-dollars/art/04-twelve-dollars.jpg
  - Asset evidence: `local_asset_present` assets/albums/twelve-dollars/art/04-twelve-dollars.jpg
  - Destination link evidence:
    - `verified_local_evidence` https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n: Twelve Dollars YouTube playlist URL (data/distrokid_release_status.json); Twelve Dollars YouTube playlist URL (data/distrokid_release_status.json); Twelve Dollars verified items: 8 (data/youtube_twelve_dollars_playlist.json)
  - Next manual action: `post_manually_then_log_url`
  - Postable now: `True`; approval required: `False`; logging required: `True`
  - Public community surface: https://www.youtube.com/@lilyroo.artist/community
  - Next command: `python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url 'PUBLIC_URL'`
  - Log effect: append Published_Log.csv content_id=FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY after public URL is available
  - Preview public URL log: `python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url 'PUBLIC_URL'`
  - Apply public URL log after posting: `python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url 'PUBLIC_URL' --apply --refresh-admin`
- **YouTube Community - Analog Myth** (`FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY`)
  - Scheduled target: `2026-06-25T18:30:00-04:00`
  - Distribution status: `ready_for_manual_post`
  - Readiness: ``; CTA: ``
  - Copy: Analog Myth is part of the Lily Roo archive now. Help us build the signal to 1,000 subscribers.
  - Link/reply: Full playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0
  - Paste block:
    Analog Myth is part of the Lily Roo archive now. Help us build the signal to 1,000 subscribers.
    
    Full playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0
  - Asset: https://www.lilyroo.com/assets/albums/analog-myth/art/03-analog-myth.jpg
  - Asset evidence: `local_asset_present` assets/albums/analog-myth/art/03-analog-myth.jpg
  - Destination link evidence:
    - `verified_local_evidence` https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0: Analog Myth YouTube playlist URL (data/distrokid_release_status.json); Analog Myth YouTube playlist URL (data/distrokid_release_status.json); Analog Myth - Lily Roo verified items: 8 (data/youtube_analog_myth_playlist.json)
  - Next manual action: `post_manually_then_log_url`
  - Postable now: `True`; approval required: `False`; logging required: `True`
  - Public community surface: https://www.youtube.com/@lilyroo.artist/community
  - Next command: `python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url 'PUBLIC_URL'`
  - Log effect: append Published_Log.csv content_id=FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY after public URL is available
  - Preview public URL log: `python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url 'PUBLIC_URL'`
  - Apply public URL log after posting: `python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url 'PUBLIC_URL' --apply --refresh-admin`

## Guardrails
- This packet does not approve, schedule, publish, or post anything.
- Use it as a human posting checklist for manual YouTube Community distribution.
- Log the public post URL after manual posting so metrics and admin state stay accurate.
