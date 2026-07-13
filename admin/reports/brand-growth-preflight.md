# Brand Growth Preflight - Lily Roo

Generated: 2026-07-13T15:13:00.312604Z

## Summary
- Status: **ready**
- Next window: **2026-07-13** at `2026-07-13T18:06:00Z`
- Expected posts: **3**
- Scheduler simulation: HTTP **200**, auth `bearer`, simulated at `2026-07-13T18:06:00Z`, due **3**, satisfied **3**, would post **2**, posted **1**, blocked **0**
- Current scheduler snapshot: checked `2026-07-13T15:12:53.677724Z`, requested `2026-07-13T15:12:53.097440Z`, due **1**, would post **0**, posted **1**, blocked **0**
- Link checks: **5 ok**, **0 failed**, **0 warning**, **0 blocking failed**
- Tracking redirects: **3 / 3 checked ok**
- Redirect targets: **3 / 3 checked**, **3 ok**, **0 warning**, **0 blocking failed**
- Current window proof due: `2026-07-13T18:06:00Z`
- Current window measurement due: `2026-07-14T18:05:00Z`

## Expected Posts
- `FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-YOUTUBE` YouTube at `2026-07-13T10:15:00-04:00`
- `FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-FACEBOOK` Facebook at `2026-07-13T11:20:00-04:00`
- `FP-GROWTH-RESET-VOICE-01-X` X at `2026-07-13T14:05:00-04:00`

## Link Checks
- **ok** `FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-YOUTUBE clip_url` 200 video/mp4
- **ok** `FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-YOUTUBE Hear the song` 200 text/html
- **ok** `FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-FACEBOOK clip_url` 200 video/mp4
- **ok** `FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-FACEBOOK Hear the song` 200 text/html
- **ok** `FP-GROWTH-RESET-VOICE-01-X Enter the album room` 200 text/html

## Redirect Target Checks
- **ok** `FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-YOUTUBE Hear the song target spotify` 200 text/html; charset=utf-8
- **ok** `FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-FACEBOOK Hear the song target spotify` 200 text/html; charset=utf-8
- **ok** `FP-GROWTH-RESET-VOICE-01-X Enter the album room target album` 200 text/html

## Guardrails
- Preflight is read-only; it calls the scheduler dry-run endpoint and HEAD-checks public URLs.
- It does not publish, approve, mutate, or import metrics.
- A ready preflight proves only that the next window is executable at the simulated due time.
- Rows already posted by the scheduler count as satisfied for the window; rows not yet sent must still be dry-run eligible.
- The current scheduler dry-run is reported separately so the admin does not imply future posts are due before their scheduled window.
- DistroKid HyperFollow 403/429 checks are non-blocking warnings because GitHub-hosted probes can be bot-filtered while the browser-visible public link remains the intended listening hub.
- YouTube 429 link checks are non-blocking warnings because GitHub-hosted probes can be rate-limited while the scheduler and Lily Roo-hosted links remain ready.
