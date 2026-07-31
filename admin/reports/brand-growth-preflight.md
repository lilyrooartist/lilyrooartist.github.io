# Brand Growth Preflight - Lily Roo

Generated: 2026-07-31T17:39:26.871370Z

## Summary
- Status: **needs_attention**
- Next window: **2026-07-31** at `2026-07-31T18:06:00Z`
- Expected posts: **2**
- Scheduler simulation: HTTP **200**, auth `bearer`, simulated at `2026-07-31T18:06:00Z`, due **16**, satisfied **1**, would post **1**, posted **1**, blocked **14**
- Current scheduler snapshot: checked `2026-07-31T17:39:20.436020Z`, requested `2026-07-31T17:39:20.029714Z`, due **15**, would post **0**, posted **1**, blocked **14**
- Link checks: **3 ok**, **0 failed**, **0 warning**, **0 blocking failed**
- Tracking redirects: **2 / 2 checked ok**
- Redirect targets: **2 / 2 checked**, **1 ok**, **0 warning**, **1 blocking failed**
- Current window proof due: `2026-07-31T18:06:00Z`
- Current window measurement due: `2026-08-01T18:05:00Z`

## Expected Posts
- `FP-GROWTH-RESET-10-NO-MORTGAGE-RELATABLE-SITUATION-YOUTUBE` YouTube at `2026-07-31T10:15:00-04:00`
- `FP-GROWTH-RESET-VOICE-06-X` X at `2026-07-31T14:05:00-04:00`

## Missing From Dry Run
- `FP-GROWTH-RESET-10-NO-MORTGAGE-RELATABLE-SITUATION-YOUTUBE`

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

## Link Checks
- **ok** `FP-GROWTH-RESET-10-NO-MORTGAGE-RELATABLE-SITUATION-YOUTUBE clip_url` 200 video/mp4
- **ok** `FP-GROWTH-RESET-10-NO-MORTGAGE-RELATABLE-SITUATION-YOUTUBE Enter the album room` 200 text/html
- **ok** `FP-GROWTH-RESET-VOICE-06-X Watch the full track` 200 text/html

## Redirect Target Checks
- **ok** `FP-GROWTH-RESET-10-NO-MORTGAGE-RELATABLE-SITUATION-YOUTUBE Enter the album room target album` 200 text/html
- **failed** `FP-GROWTH-RESET-VOICE-06-X Watch the full track target video` 0 missing target URL

## Guardrails
- Preflight is read-only; it calls the scheduler dry-run endpoint and HEAD-checks public URLs.
- It does not publish, approve, mutate, or import metrics.
- A ready preflight proves only that the next window is executable at the simulated due time.
- Rows already posted by the scheduler count as satisfied for the window; rows not yet sent must still be dry-run eligible.
- The current scheduler dry-run is reported separately so the admin does not imply future posts are due before their scheduled window.
- DistroKid HyperFollow 403/429 checks are non-blocking warnings because GitHub-hosted probes can be bot-filtered while the browser-visible public link remains the intended listening hub.
- YouTube 429 link checks are non-blocking warnings because GitHub-hosted probes can be rate-limited while the scheduler and Lily Roo-hosted links remain ready.
