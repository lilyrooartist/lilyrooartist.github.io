# Brand Growth Preflight - Lily Roo

Generated: 2026-07-20T09:34:47.969883Z

## Summary
- Status: **needs_attention**
- Next window: **2026-07-20** at `2026-07-20T18:06:00Z`
- Expected posts: **1**
- Scheduler simulation: HTTP **200**, auth `bearer`, simulated at `2026-07-20T18:06:00Z`, due **6**, satisfied **1**, would post **1**, posted **0**, blocked **5**
- Current scheduler snapshot: checked `2026-07-20T09:34:42.804670Z`, requested `2026-07-20T09:34:42.617016Z`, due **5**, would post **0**, posted **0**, blocked **5**
- Link checks: **1 ok**, **0 failed**, **0 warning**, **0 blocking failed**
- Tracking redirects: **1 / 1 checked ok**
- Redirect targets: **1 / 1 checked**, **1 ok**, **0 warning**, **0 blocking failed**
- Current window proof due: `2026-07-20T18:06:00Z`
- Current window measurement due: `2026-07-21T18:05:00Z`

## Expected Posts
- `FP-GROWTH-RESET-VOICE-03-X` X at `2026-07-20T14:05:00-04:00`

## Blocked Rows
- `FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-FACEBOOK`
- `FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-FACEBOOK`
- `FP-GROWTH-RESET-03-SLOW-WALK-VISUAL-STORY-FACEBOOK`
- `FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE`
- `FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-FACEBOOK`

## Link Checks
- **ok** `FP-GROWTH-RESET-VOICE-03-X Hear the song` 200 text/html

## Redirect Target Checks
- **ok** `FP-GROWTH-RESET-VOICE-03-X Hear the song target spotify` 200 text/html; charset=utf-8

## Guardrails
- Preflight is read-only; it calls the scheduler dry-run endpoint and HEAD-checks public URLs.
- It does not publish, approve, mutate, or import metrics.
- A ready preflight proves only that the next window is executable at the simulated due time.
- Rows already posted by the scheduler count as satisfied for the window; rows not yet sent must still be dry-run eligible.
- The current scheduler dry-run is reported separately so the admin does not imply future posts are due before their scheduled window.
- DistroKid HyperFollow 403/429 checks are non-blocking warnings because GitHub-hosted probes can be bot-filtered while the browser-visible public link remains the intended listening hub.
- YouTube 429 link checks are non-blocking warnings because GitHub-hosted probes can be rate-limited while the scheduler and Lily Roo-hosted links remain ready.
