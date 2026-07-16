# Brand Growth Preflight - Lily Roo

Generated: 2026-07-16T03:38:59.557490Z

## Summary
- Status: **needs_attention**
- Next window: **2026-07-17** at `2026-07-17T18:06:00Z`
- Expected posts: **3**
- Scheduler simulation: HTTP **200**, auth `bearer`, simulated at `2026-07-17T18:06:00Z`, due **5**, satisfied **3**, would post **3**, posted **0**, blocked **2**
- Current scheduler snapshot: checked `2026-07-16T03:38:54.948808Z`, requested `2026-07-16T03:38:54.735387Z`, due **2**, would post **0**, posted **0**, blocked **2**
- Link checks: **5 ok**, **0 failed**, **0 warning**, **0 blocking failed**
- Tracking redirects: **3 / 3 checked ok**
- Redirect targets: **3 / 3 checked**, **2 ok**, **0 warning**, **1 blocking failed**
- Current window proof due: `2026-07-17T18:06:00Z`
- Current window measurement due: `2026-07-18T18:05:00Z`

## Expected Posts
- `FP-GROWTH-RESET-03-SLOW-WALK-VISUAL-STORY-YOUTUBE` YouTube at `2026-07-17T10:15:00-04:00`
- `FP-GROWTH-RESET-03-SLOW-WALK-VISUAL-STORY-FACEBOOK` Facebook at `2026-07-17T11:20:00-04:00`
- `FP-GROWTH-RESET-VOICE-02-X` X at `2026-07-17T14:05:00-04:00`

## Blocked Rows
- `FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-FACEBOOK`
- `FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-FACEBOOK`

## Link Checks
- **ok** `FP-GROWTH-RESET-03-SLOW-WALK-VISUAL-STORY-YOUTUBE clip_url` 200 video/mp4
- **ok** `FP-GROWTH-RESET-03-SLOW-WALK-VISUAL-STORY-YOUTUBE Watch the full track` 200 text/html
- **ok** `FP-GROWTH-RESET-03-SLOW-WALK-VISUAL-STORY-FACEBOOK clip_url` 200 video/mp4
- **ok** `FP-GROWTH-RESET-03-SLOW-WALK-VISUAL-STORY-FACEBOOK Watch the full track` 200 text/html
- **ok** `FP-GROWTH-RESET-VOICE-02-X Watch the full track` 200 text/html

## Redirect Target Checks
- **ok** `FP-GROWTH-RESET-03-SLOW-WALK-VISUAL-STORY-YOUTUBE Watch the full track target video` 200 text/html; charset=utf-8
- **ok** `FP-GROWTH-RESET-03-SLOW-WALK-VISUAL-STORY-FACEBOOK Watch the full track target video` 200 text/html; charset=utf-8
- **failed** `FP-GROWTH-RESET-VOICE-02-X Watch the full track target video` 0 missing target URL

## Guardrails
- Preflight is read-only; it calls the scheduler dry-run endpoint and HEAD-checks public URLs.
- It does not publish, approve, mutate, or import metrics.
- A ready preflight proves only that the next window is executable at the simulated due time.
- Rows already posted by the scheduler count as satisfied for the window; rows not yet sent must still be dry-run eligible.
- The current scheduler dry-run is reported separately so the admin does not imply future posts are due before their scheduled window.
- DistroKid HyperFollow 403/429 checks are non-blocking warnings because GitHub-hosted probes can be bot-filtered while the browser-visible public link remains the intended listening hub.
- YouTube 429 link checks are non-blocking warnings because GitHub-hosted probes can be rate-limited while the scheduler and Lily Roo-hosted links remain ready.
