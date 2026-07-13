# Brand Growth Preflight - Lily Roo

Generated: 2026-07-13T19:51:48.947845Z

## Summary
- Status: **needs_attention**
- Next window: **2026-07-15** at `2026-07-15T15:21:00Z`
- Expected posts: **2**
- Scheduler simulation: HTTP **200**, auth `bearer`, simulated at `2026-07-15T15:21:00Z`, due **4**, satisfied **2**, would post **2**, posted **1**, blocked **1**
- Current scheduler snapshot: checked `2026-07-13T19:51:44.560635Z`, requested `2026-07-13T19:51:44.416006Z`, due **2**, would post **0**, posted **1**, blocked **1**
- Link checks: **4 ok**, **0 failed**, **0 warning**, **0 blocking failed**
- Tracking redirects: **2 / 2 checked ok**
- Redirect targets: **2 / 2 checked**, **2 ok**, **0 warning**, **0 blocking failed**
- Current window proof due: `2026-07-15T15:21:00Z`
- Current window measurement due: `2026-07-16T15:20:00Z`

## Expected Posts
- `FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-YOUTUBE` YouTube at `2026-07-15T10:15:00-04:00`
- `FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-FACEBOOK` Facebook at `2026-07-15T11:20:00-04:00`

## Blocked Rows
- `FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-FACEBOOK`

## Link Checks
- **ok** `FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-YOUTUBE clip_url` 200 video/mp4
- **ok** `FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-YOUTUBE Enter the album room` 200 text/html
- **ok** `FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-FACEBOOK clip_url` 200 video/mp4
- **ok** `FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-FACEBOOK Enter the album room` 200 text/html

## Redirect Target Checks
- **ok** `FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-YOUTUBE Enter the album room target album` 200 text/html
- **ok** `FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-FACEBOOK Enter the album room target album` 200 text/html

## Guardrails
- Preflight is read-only; it calls the scheduler dry-run endpoint and HEAD-checks public URLs.
- It does not publish, approve, mutate, or import metrics.
- A ready preflight proves only that the next window is executable at the simulated due time.
- Rows already posted by the scheduler count as satisfied for the window; rows not yet sent must still be dry-run eligible.
- The current scheduler dry-run is reported separately so the admin does not imply future posts are due before their scheduled window.
- DistroKid HyperFollow 403/429 checks are non-blocking warnings because GitHub-hosted probes can be bot-filtered while the browser-visible public link remains the intended listening hub.
- YouTube 429 link checks are non-blocking warnings because GitHub-hosted probes can be rate-limited while the scheduler and Lily Roo-hosted links remain ready.
