# Manual Distribution Packet - Lily Roo

Generated: 2026-06-20T08:04:28.388688Z

## Summary
- Manual-ready posts: **2**
- YouTube Community posts: **2**
- Hard subscriber CTAs: **2**
- Approved manual posts: **0**
- Logged manual posts: **0**
- Unlogged manual posts: **2**
- Public URL logs still needed: **2**

## Manual Posting Docket
- Status: **needs_review**
- Needs review: **2**
- Postable now: **0**
- Logged: **0**
- Public community surface: https://www.youtube.com/@lilyroo.artist/community

### Approval Gate
- Status: **ready_for_manual_review**
- Ready approvals: **2**
- Blocked approvals: **1**
- Ready IDs: `FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY, FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY`
- Blocked IDs: `FP-PLAN-TWELVE-DOLLARS-TIKTOK`
- Preview approvals: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --dry-run`
- Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --refresh-admin`
- Guardrail: Manual-only approvals do not auto-post; posting and public URL logging remain separate after review.

### Needs Review
- **YouTube Community - Twelve Dollars** (`FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY`)
  - Paste text: Twelve Dollars is part of the Lily Roo archive now. Help us build the signal to 1,000 subscribers.

Full playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
  - Asset: https://www.lilyroo.com/assets/albums/twelve-dollars/art/04-twelve-dollars.jpg
  - Asset evidence: `local_asset_present` assets/albums/twelve-dollars/art/04-twelve-dollars.jpg
  - Destination links: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
  - Destination link evidence:
    - `verified_local_evidence` https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n: Twelve Dollars YouTube playlist URL (data/distrokid_release_status.json); Twelve Dollars verified items: 8 (data/youtube_twelve_dollars_playlist.json)
  - Preview approval: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --refresh-admin`
- **YouTube Community - Analog Myth** (`FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY`)
  - Paste text: Analog Myth is part of the Lily Roo archive now. Help us build the signal to 1,000 subscribers.

Full playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0
  - Asset: https://www.lilyroo.com/assets/albums/analog-myth/art/03-analog-myth.jpg
  - Asset evidence: `local_asset_present` assets/albums/analog-myth/art/03-analog-myth.jpg
  - Destination links: https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0
  - Destination link evidence:
    - `verified_local_evidence` https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0: Analog Myth YouTube playlist URL (data/distrokid_release_status.json); Analog Myth - Lily Roo verified items: 8 (data/youtube_analog_myth_playlist.json)
  - Preview approval: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --refresh-admin`

### Postable Now
- None

## Manual Posting Queue
- **YouTube Community - Twelve Dollars** (`FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY`)
  - Scheduled target: `2026-06-22T18:30:00-04:00`
  - Distribution status: `waiting_for_review`
  - Readiness: `manual_only`; CTA: `hard_goal`
  - Copy: Twelve Dollars is part of the Lily Roo archive now. Help us build the signal to 1,000 subscribers.
  - Link/reply: Full playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
  - Paste block:
    Twelve Dollars is part of the Lily Roo archive now. Help us build the signal to 1,000 subscribers.
    
    Full playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
  - Asset: https://www.lilyroo.com/assets/albums/twelve-dollars/art/04-twelve-dollars.jpg
  - Asset evidence: `local_asset_present` assets/albums/twelve-dollars/art/04-twelve-dollars.jpg
  - Destination link evidence:
    - `verified_local_evidence` https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n: Twelve Dollars YouTube playlist URL (data/distrokid_release_status.json); Twelve Dollars verified items: 8 (data/youtube_twelve_dollars_playlist.json)
  - Next manual action: `review_and_approve`
  - Postable now: `False`; approval required: `True`; logging required: `True`
  - Public community surface: https://www.youtube.com/@lilyroo.artist/community
  - Next command: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --refresh-admin`
  - Log effect: append Published_Log.csv content_id=FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY after public URL is available
  - Preview approval: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --refresh-admin`
  - Preview public URL log: `python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url PUBLIC_URL`
  - Apply public URL log after posting: `python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url PUBLIC_URL --apply --refresh-admin`
- **YouTube Community - Analog Myth** (`FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY`)
  - Scheduled target: `2026-06-23T18:30:00-04:00`
  - Distribution status: `waiting_for_review`
  - Readiness: `manual_only`; CTA: `hard_goal`
  - Copy: Analog Myth is part of the Lily Roo archive now. Help us build the signal to 1,000 subscribers.
  - Link/reply: Full playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0
  - Paste block:
    Analog Myth is part of the Lily Roo archive now. Help us build the signal to 1,000 subscribers.
    
    Full playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0
  - Asset: https://www.lilyroo.com/assets/albums/analog-myth/art/03-analog-myth.jpg
  - Asset evidence: `local_asset_present` assets/albums/analog-myth/art/03-analog-myth.jpg
  - Destination link evidence:
    - `verified_local_evidence` https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0: Analog Myth YouTube playlist URL (data/distrokid_release_status.json); Analog Myth - Lily Roo verified items: 8 (data/youtube_analog_myth_playlist.json)
  - Next manual action: `review_and_approve`
  - Postable now: `False`; approval required: `True`; logging required: `True`
  - Public community surface: https://www.youtube.com/@lilyroo.artist/community
  - Next command: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --refresh-admin`
  - Log effect: append Published_Log.csv content_id=FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY after public URL is available
  - Preview approval: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --refresh-admin`
  - Preview public URL log: `python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url PUBLIC_URL`
  - Apply public URL log after posting: `python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url PUBLIC_URL --apply --refresh-admin`

## Guardrails
- This packet does not approve, schedule, publish, or post anything.
- Use it as a human posting checklist for manual YouTube Community distribution.
- Log the public post URL after manual posting so metrics and admin state stay accurate.
