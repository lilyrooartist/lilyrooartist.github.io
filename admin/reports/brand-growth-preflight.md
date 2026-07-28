# Brand Growth Preflight - Lily Roo

Generated: 2026-07-28T09:05:29.710096Z

## Summary
- Status: **needs_attention**
- Next window: **2026-07-29** at `2026-07-29T15:21:00Z`
- Expected posts: **2**
- Scheduler simulation: HTTP **200**, auth `bearer`, simulated at `2026-07-29T15:21:00Z`, due **14**, satisfied **2**, would post **2**, posted **0**, blocked **12**
- Current scheduler snapshot: checked `2026-07-28T09:05:23.765636Z`, requested `2026-07-28T09:05:23.504751Z`, due **12**, would post **0**, posted **0**, blocked **12**
- Link checks: **4 ok**, **0 failed**, **0 warning**, **0 blocking failed**
- Tracking redirects: **2 / 2 checked ok**
- Redirect targets: **2 / 2 checked**, **2 ok**, **0 warning**, **0 blocking failed**
- Current window proof due: `2026-07-29T15:21:00Z`
- Current window measurement due: `2026-07-30T15:20:00Z`

## Expected Posts
- `FP-GROWTH-RESET-09-NO-MORTGAGE-LYRIC-PUNCH-LINE-YOUTUBE` YouTube at `2026-07-29T10:15:00-04:00`
- `FP-GROWTH-RESET-09-NO-MORTGAGE-LYRIC-PUNCH-LINE-FACEBOOK` Facebook at `2026-07-29T11:20:00-04:00`

## Blocked Rows
- `FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-FACEBOOK`
- `FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-FACEBOOK`
- `FP-GROWTH-RESET-03-SLOW-WALK-VISUAL-STORY-FACEBOOK`
- `FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE`
- `FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-FACEBOOK`
- `FP-GROWTH-RESET-05-SPILLING-THE-TEA-LYRIC-PUNCH-LINE-YOUTUBE`
- `FP-GROWTH-RESET-05-SPILLING-THE-TEA-LYRIC-PUNCH-LINE-FACEBOOK`
- `FP-GROWTH-RESET-06-SPILLING-THE-TEA-RELATABLE-SITUATION-YOUTUBE`
- `FP-GROWTH-RESET-06-SPILLING-THE-TEA-RELATABLE-SITUATION-FACEBOOK`
- `FP-GROWTH-RESET-07-SPILLING-THE-TEA-VISUAL-STORY-YOUTUBE`
- `FP-GROWTH-RESET-07-SPILLING-THE-TEA-VISUAL-STORY-FACEBOOK`
- `FP-GROWTH-RESET-08-SPILLING-THE-TEA-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE`

## Link Checks
- **ok** `FP-GROWTH-RESET-09-NO-MORTGAGE-LYRIC-PUNCH-LINE-YOUTUBE clip_url` 200 video/mp4
- **ok** `FP-GROWTH-RESET-09-NO-MORTGAGE-LYRIC-PUNCH-LINE-YOUTUBE Hear the song` 200 text/html
- **ok** `FP-GROWTH-RESET-09-NO-MORTGAGE-LYRIC-PUNCH-LINE-FACEBOOK clip_url` 200 video/mp4
- **ok** `FP-GROWTH-RESET-09-NO-MORTGAGE-LYRIC-PUNCH-LINE-FACEBOOK Hear the song` 200 text/html

## Redirect Target Checks
- **ok** `FP-GROWTH-RESET-09-NO-MORTGAGE-LYRIC-PUNCH-LINE-YOUTUBE Hear the song target spotify` 200 text/html; charset=utf-8
- **ok** `FP-GROWTH-RESET-09-NO-MORTGAGE-LYRIC-PUNCH-LINE-FACEBOOK Hear the song target spotify` 200 text/html; charset=utf-8

## Guardrails
- Preflight is read-only; it calls the scheduler dry-run endpoint and HEAD-checks public URLs.
- It does not publish, approve, mutate, or import metrics.
- A ready preflight proves only that the next window is executable at the simulated due time.
- Rows already posted by the scheduler count as satisfied for the window; rows not yet sent must still be dry-run eligible.
- The current scheduler dry-run is reported separately so the admin does not imply future posts are due before their scheduled window.
- DistroKid HyperFollow 403/429 checks are non-blocking warnings because GitHub-hosted probes can be bot-filtered while the browser-visible public link remains the intended listening hub.
- YouTube 429 link checks are non-blocking warnings because GitHub-hosted probes can be rate-limited while the scheduler and Lily Roo-hosted links remain ready.
