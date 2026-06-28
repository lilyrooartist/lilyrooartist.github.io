# Manual Distribution Packet - Lily Roo

Generated: 2026-06-28T00:52:27.142201Z

## Summary
- Manual-ready posts: **4**
- YouTube Community posts: **4**
- Hard subscriber CTAs: **0**
- Approved manual posts: **4**
- Logged manual posts: **0**
- Unlogged manual posts: **4**
- Public URL logs still needed: **4**

## Manual Posting Docket
- Status: **postable_now**
- Needs review: **0**
- Postable now: **4**
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
- Postable now IDs: `FP-AUTO-270, FP-AUTO-275, FP-AUTO-280, FP-AUTO-285`
- Pending log IDs: `FP-AUTO-270, FP-AUTO-275, FP-AUTO-280, FP-AUTO-285`
- Posting surface: YouTube Studio Community
- Public community URL: https://www.youtube.com/@lilyroo.artist/community
- Public URL worksheet: `data/manual_distribution_url_template.csv`
- Batch URL log preview: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv`
- Batch URL log apply after posting: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --apply --refresh-admin`
- URL worksheet rows waiting: **4**
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
- **YouTube Community - Brain Rot** (`FP-AUTO-270`)
  - Paste text: The phone is melting politely. Brain Rot is tonight's Twelve Dollars signal. Watch the remastered video and help push Lily Roo toward 1,000 YouTube subscribers.

Watch Brain Rot: https://youtu.be/U7aczBSruAY | Full Twelve Dollars playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
  - Asset: https://www.lilyroo.com/assets/albums/twelve-dollars/art/01-brain-rot-youtube-thumbnail.jpg
  - Log preview after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-270 --url 'PUBLIC_URL'`
  - Log apply after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-270 --url 'PUBLIC_URL' --apply --refresh-admin`
- **YouTube Community - Every Pearl in Carmel** (`FP-AUTO-275`)
  - Paste text: Every Pearl in Carmel is the pretty souvenir that still knows what it cost. Watch the remastered video and help push Lily Roo toward 1,000 YouTube subscribers.

Watch Every Pearl in Carmel: https://youtu.be/QodRYnvTVZc | Full Twelve Dollars playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
  - Asset: https://www.lilyroo.com/assets/albums/twelve-dollars/art/02-every-pearl-in-carmel-youtube-thumbnail.jpg
  - Log preview after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-275 --url 'PUBLIC_URL'`
  - Log apply after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-275 --url 'PUBLIC_URL' --apply --refresh-admin`
- **YouTube Community - The Other One's Charging** (`FP-AUTO-280`)
  - Paste text: The Other One's Charging is domestic chaos with a battery icon. Watch the remastered video and help push Lily Roo toward 1,000 YouTube subscribers.

Watch The Other One's Charging: https://youtu.be/EprgLKHp-lE | Full Twelve Dollars playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
  - Asset: https://www.lilyroo.com/assets/albums/twelve-dollars/art/03-the-other-ones-charging-youtube-thumbnail.jpg
  - Log preview after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-280 --url 'PUBLIC_URL'`
  - Log apply after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-280 --url 'PUBLIC_URL' --apply --refresh-admin`
- **YouTube Community - Twelve Dollars** (`FP-AUTO-285`)
  - Paste text: Twelve Dollars is the stage light, the joke, and the receipt. Watch the remastered video and help push Lily Roo toward 1,000 YouTube subscribers.

Watch Twelve Dollars: https://youtu.be/G2RlCwZKOsk | Full Twelve Dollars playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
  - Asset: https://www.lilyroo.com/assets/albums/twelve-dollars/art/04-twelve-dollars-youtube-thumbnail.jpg
  - Log preview after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-285 --url 'PUBLIC_URL'`
  - Log apply after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-285 --url 'PUBLIC_URL' --apply --refresh-admin`

## Manual Posting Queue
- **YouTube Community - Brain Rot** (`FP-AUTO-270`)
  - Scheduled target: `2026-06-27T22:35:00-04:00`
  - Distribution status: `ready_for_manual_post`
  - Readiness: ``; CTA: ``
  - Copy: The phone is melting politely. Brain Rot is tonight's Twelve Dollars signal. Watch the remastered video and help push Lily Roo toward 1,000 YouTube subscribers.
  - Link/reply: Watch Brain Rot: https://youtu.be/U7aczBSruAY | Full Twelve Dollars playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
  - Paste block:
    The phone is melting politely. Brain Rot is tonight's Twelve Dollars signal. Watch the remastered video and help push Lily Roo toward 1,000 YouTube subscribers.

    Watch Brain Rot: https://youtu.be/U7aczBSruAY | Full Twelve Dollars playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
  - Asset: https://www.lilyroo.com/assets/albums/twelve-dollars/art/01-brain-rot-youtube-thumbnail.jpg
  - Asset evidence: `local_asset_present` assets/albums/twelve-dollars/art/01-brain-rot-youtube-thumbnail.jpg
  - Destination link evidence:
    - `needs_manual_review` https://youtu.be/U7aczBSruAY: no local evidence
    - `verified_local_evidence` https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n: Twelve Dollars YouTube playlist URL (data/distrokid_release_status.json); Twelve Dollars YouTube playlist URL (data/distrokid_release_status.json); Twelve Dollars verified items: 8 (data/youtube_twelve_dollars_playlist.json)
  - Next manual action: `post_manually_then_log_url`
  - Postable now: `True`; approval required: `False`; logging required: `True`
  - Public community surface: https://www.youtube.com/@lilyroo.artist/community
  - Next command: `python3 scripts/log_manual_distribution.py --id FP-AUTO-270 --url 'PUBLIC_URL'`
  - Log effect: append Published_Log.csv content_id=FP-AUTO-270 after public URL is available
  - Preview public URL log: `python3 scripts/log_manual_distribution.py --id FP-AUTO-270 --url 'PUBLIC_URL'`
  - Apply public URL log after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-270 --url 'PUBLIC_URL' --apply --refresh-admin`
- **YouTube Community - Every Pearl in Carmel** (`FP-AUTO-275`)
  - Scheduled target: `2026-06-28T22:35:00-04:00`
  - Distribution status: `ready_for_manual_post`
  - Readiness: ``; CTA: ``
  - Copy: Every Pearl in Carmel is the pretty souvenir that still knows what it cost. Watch the remastered video and help push Lily Roo toward 1,000 YouTube subscribers.
  - Link/reply: Watch Every Pearl in Carmel: https://youtu.be/QodRYnvTVZc | Full Twelve Dollars playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
  - Paste block:
    Every Pearl in Carmel is the pretty souvenir that still knows what it cost. Watch the remastered video and help push Lily Roo toward 1,000 YouTube subscribers.

    Watch Every Pearl in Carmel: https://youtu.be/QodRYnvTVZc | Full Twelve Dollars playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
  - Asset: https://www.lilyroo.com/assets/albums/twelve-dollars/art/02-every-pearl-in-carmel-youtube-thumbnail.jpg
  - Asset evidence: `local_asset_present` assets/albums/twelve-dollars/art/02-every-pearl-in-carmel-youtube-thumbnail.jpg
  - Destination link evidence:
    - `needs_manual_review` https://youtu.be/QodRYnvTVZc: no local evidence
    - `verified_local_evidence` https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n: Twelve Dollars YouTube playlist URL (data/distrokid_release_status.json); Twelve Dollars YouTube playlist URL (data/distrokid_release_status.json); Twelve Dollars verified items: 8 (data/youtube_twelve_dollars_playlist.json)
  - Next manual action: `post_manually_then_log_url`
  - Postable now: `True`; approval required: `False`; logging required: `True`
  - Public community surface: https://www.youtube.com/@lilyroo.artist/community
  - Next command: `python3 scripts/log_manual_distribution.py --id FP-AUTO-275 --url 'PUBLIC_URL'`
  - Log effect: append Published_Log.csv content_id=FP-AUTO-275 after public URL is available
  - Preview public URL log: `python3 scripts/log_manual_distribution.py --id FP-AUTO-275 --url 'PUBLIC_URL'`
  - Apply public URL log after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-275 --url 'PUBLIC_URL' --apply --refresh-admin`
- **YouTube Community - The Other One's Charging** (`FP-AUTO-280`)
  - Scheduled target: `2026-06-29T22:35:00-04:00`
  - Distribution status: `ready_for_manual_post`
  - Readiness: ``; CTA: ``
  - Copy: The Other One's Charging is domestic chaos with a battery icon. Watch the remastered video and help push Lily Roo toward 1,000 YouTube subscribers.
  - Link/reply: Watch The Other One's Charging: https://youtu.be/EprgLKHp-lE | Full Twelve Dollars playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
  - Paste block:
    The Other One's Charging is domestic chaos with a battery icon. Watch the remastered video and help push Lily Roo toward 1,000 YouTube subscribers.

    Watch The Other One's Charging: https://youtu.be/EprgLKHp-lE | Full Twelve Dollars playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
  - Asset: https://www.lilyroo.com/assets/albums/twelve-dollars/art/03-the-other-ones-charging-youtube-thumbnail.jpg
  - Asset evidence: `local_asset_present` assets/albums/twelve-dollars/art/03-the-other-ones-charging-youtube-thumbnail.jpg
  - Destination link evidence:
    - `needs_manual_review` https://youtu.be/EprgLKHp-lE: no local evidence
    - `verified_local_evidence` https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n: Twelve Dollars YouTube playlist URL (data/distrokid_release_status.json); Twelve Dollars YouTube playlist URL (data/distrokid_release_status.json); Twelve Dollars verified items: 8 (data/youtube_twelve_dollars_playlist.json)
  - Next manual action: `post_manually_then_log_url`
  - Postable now: `True`; approval required: `False`; logging required: `True`
  - Public community surface: https://www.youtube.com/@lilyroo.artist/community
  - Next command: `python3 scripts/log_manual_distribution.py --id FP-AUTO-280 --url 'PUBLIC_URL'`
  - Log effect: append Published_Log.csv content_id=FP-AUTO-280 after public URL is available
  - Preview public URL log: `python3 scripts/log_manual_distribution.py --id FP-AUTO-280 --url 'PUBLIC_URL'`
  - Apply public URL log after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-280 --url 'PUBLIC_URL' --apply --refresh-admin`
- **YouTube Community - Twelve Dollars** (`FP-AUTO-285`)
  - Scheduled target: `2026-06-30T22:35:00-04:00`
  - Distribution status: `ready_for_manual_post`
  - Readiness: ``; CTA: ``
  - Copy: Twelve Dollars is the stage light, the joke, and the receipt. Watch the remastered video and help push Lily Roo toward 1,000 YouTube subscribers.
  - Link/reply: Watch Twelve Dollars: https://youtu.be/G2RlCwZKOsk | Full Twelve Dollars playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
  - Paste block:
    Twelve Dollars is the stage light, the joke, and the receipt. Watch the remastered video and help push Lily Roo toward 1,000 YouTube subscribers.

    Watch Twelve Dollars: https://youtu.be/G2RlCwZKOsk | Full Twelve Dollars playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
  - Asset: https://www.lilyroo.com/assets/albums/twelve-dollars/art/04-twelve-dollars-youtube-thumbnail.jpg
  - Asset evidence: `local_asset_present` assets/albums/twelve-dollars/art/04-twelve-dollars-youtube-thumbnail.jpg
  - Destination link evidence:
    - `needs_manual_review` https://youtu.be/G2RlCwZKOsk: no local evidence
    - `verified_local_evidence` https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n: Twelve Dollars YouTube playlist URL (data/distrokid_release_status.json); Twelve Dollars YouTube playlist URL (data/distrokid_release_status.json); Twelve Dollars verified items: 8 (data/youtube_twelve_dollars_playlist.json)
  - Next manual action: `post_manually_then_log_url`
  - Postable now: `True`; approval required: `False`; logging required: `True`
  - Public community surface: https://www.youtube.com/@lilyroo.artist/community
  - Next command: `python3 scripts/log_manual_distribution.py --id FP-AUTO-285 --url 'PUBLIC_URL'`
  - Log effect: append Published_Log.csv content_id=FP-AUTO-285 after public URL is available
  - Preview public URL log: `python3 scripts/log_manual_distribution.py --id FP-AUTO-285 --url 'PUBLIC_URL'`
  - Apply public URL log after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-285 --url 'PUBLIC_URL' --apply --refresh-admin`

## Guardrails
- This packet does not approve, schedule, publish, or post anything.
- Use it as a human posting checklist for manual YouTube Community distribution.
- Log the public post URL after manual posting so metrics and admin state stay accurate.
