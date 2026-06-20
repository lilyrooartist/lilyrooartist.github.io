# Scheduled Approval Packet - Lily Roo

Generated: 2026-06-20T00:40:48.632251Z

## Summary
- Approval blockers: **3**
- Auto rows: **2**
- Manual rows: **1**

## Review Queue
- **Instagram - I Learned It All in Fifteen Seconds** (`FP-AUTO-258`)
  - Scheduled: `2026-06-05T15:35:00-04:00`; mode: `auto`; type: `image`
  - Reason: `not_approved`
  - Copy: The first Lily Roo single is live, and the cover art has been remastered into its proper tiny-room glow.
  - Link/reply: Listen on Spotify: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi | Apple Music: https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249 | YouTube Music: https://music.youtube.com/watch?v=vK0mDIW65o4
  - Asset: https://www.lilyroo.com/assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg
  - Preview approval: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-258 --dry-run`
  - Approve after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-258 --refresh-admin`
- **TikTok - I Learned It All in Fifteen Seconds** (`FP-AUTO-259`)
  - Scheduled: `2026-06-05T20:40:00-04:00`; mode: `auto`; type: `video`
  - Reason: `not_approved`
  - Copy: I learned it all in fifteen seconds and somehow still have homework. Streaming now.
  - Link/reply: Listen on Spotify: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi | Apple Music: https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249 | YouTube Music: https://music.youtube.com/watch?v=vK0mDIW65o4
  - Asset: https://www.lilyroo.com/assets/ig/01_i_learned_it_all_60s.mp4
  - Preview approval: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-259 --dry-run`
  - Approve after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-259 --refresh-admin`
- **YouTube Community - I Learned It All in Fifteen Seconds** (`FP-AUTO-261`)
  - Scheduled: `2026-06-06T19:10:00-04:00`; mode: `manual`; type: `community`
  - Reason: `not_approved`
  - Copy: New transmission: I Learned It All in Fifteen Seconds is live. Remastered cover art, same suspicious amount of feeling.
  - Link/reply: Stream: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi | Apple Music: https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249 | YouTube: https://www.youtube.com/@lilyroo.artist | YouTube Music: https://music.youtube.com/watch?v=vK0mDIW65o4
  - Asset: https://www.lilyroo.com/assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg
  - Preview approval: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-261 --dry-run`
  - Approve after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-261 --refresh-admin`

## Guardrails
- This packet does not approve, publish, or post anything.
- Use preview commands before approval apply commands.
- Manual rows still require human posting and public URL logging after approval.
