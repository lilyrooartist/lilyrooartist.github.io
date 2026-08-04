# Brand Growth Preflight - Lily Roo

Generated: 2026-08-04T14:40:29.856448Z

## Summary
- Status: **needs_attention**
- Next window: **2026-08-04** at `2026-08-04T15:21:00Z`
- Expected posts: **2**
- Scheduler simulation: HTTP **200**, auth `bearer`, simulated at `2026-08-04T15:21:00Z`, due **17**, satisfied **2**, would post **2**, posted **0**, blocked **15**
- Current scheduler snapshot: checked `2026-08-04T14:40:22.766726Z`, requested `2026-08-04T14:40:22.499064Z`, due **16**, would post **1**, posted **0**, blocked **15**
- Link checks: **4 ok**, **0 failed**, **0 warning**, **0 blocking failed**
- Tracking redirects: **2 / 2 checked ok**
- Redirect targets: **2 / 2 checked**, **2 ok**, **0 warning**, **0 blocking failed**
- Current window proof due: `2026-08-04T15:21:00Z`
- Current window measurement due: `2026-08-05T15:20:00Z`

## Expected Posts
- `FP-GROWTH-RESET-12-NO-MORTGAGE-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE` YouTube at `2026-08-04T10:15:00-04:00`
- `FP-GROWTH-RESET-12-NO-MORTGAGE-ECHO-THREAD-SETUP-SONG-PAYOFF-FACEBOOK` Facebook at `2026-08-04T11:20:00-04:00`

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
- `FP-GROWTH-RESET-09-NO-MORTGAGE-LYRIC-PUNCH-LINE-YOUTUBE`
- `FP-GROWTH-RESET-10-NO-MORTGAGE-RELATABLE-SITUATION-YOUTUBE`
- `FP-GROWTH-RESET-11-NO-MORTGAGE-VISUAL-STORY-YOUTUBE`

## Link Checks
- **ok** `FP-GROWTH-RESET-12-NO-MORTGAGE-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE clip_url` 200 video/mp4
- **ok** `FP-GROWTH-RESET-12-NO-MORTGAGE-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE Hear the Echo Thread` 200 text/html
- **ok** `FP-GROWTH-RESET-12-NO-MORTGAGE-ECHO-THREAD-SETUP-SONG-PAYOFF-FACEBOOK clip_url` 200 video/mp4
- **ok** `FP-GROWTH-RESET-12-NO-MORTGAGE-ECHO-THREAD-SETUP-SONG-PAYOFF-FACEBOOK Hear the Echo Thread` 200 text/html

## Redirect Target Checks
- **ok** `FP-GROWTH-RESET-12-NO-MORTGAGE-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE Hear the Echo Thread target echo` 200 text/html
- **ok** `FP-GROWTH-RESET-12-NO-MORTGAGE-ECHO-THREAD-SETUP-SONG-PAYOFF-FACEBOOK Hear the Echo Thread target echo` 200 text/html

## Guardrails
- Preflight is read-only; it calls the scheduler dry-run endpoint and HEAD-checks public URLs.
- It does not publish, approve, mutate, or import metrics.
- A ready preflight proves only that the next window is executable at the simulated due time.
- Rows already posted by the scheduler count as satisfied for the window; rows not yet sent must still be dry-run eligible.
- The current scheduler dry-run is reported separately so the admin does not imply future posts are due before their scheduled window.
- DistroKid HyperFollow 403/429 checks are non-blocking warnings because GitHub-hosted probes can be bot-filtered while the browser-visible public link remains the intended listening hub.
- YouTube 429 link checks are non-blocking warnings because GitHub-hosted probes can be rate-limited while the scheduler and Lily Roo-hosted links remain ready.
