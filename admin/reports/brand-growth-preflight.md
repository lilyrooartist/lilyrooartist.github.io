# Brand Growth Preflight - Lily Roo

Generated: 2026-07-09T17:29:49.362335Z

## Summary
- Status: **ready**
- Next window: **2026-07-10** at `2026-07-10T15:21:00Z`
- Expected posts: **2**
- Scheduler simulation: HTTP **200**, auth `bearer`, simulated at `2026-07-10T15:21:00Z`, due **2**, satisfied **2**, would post **2**, posted **0**, blocked **0**
- Current scheduler snapshot: checked `2026-07-09T17:29:43.656680Z`, requested `2026-07-09T17:29:43.508495Z`, due **0**, would post **0**, posted **0**, blocked **0**
- Link checks: **8 ok**, **0 failed**, **0 warning**, **0 blocking failed**
- Tracking redirects: **6 / 6 checked ok**
- Redirect targets: **6 / 6 checked**, **4 ok**, **2 warning**, **0 blocking failed**
- Current window proof due: `2026-07-10T15:21:00Z`
- Current window measurement due: `2026-07-11T15:20:00Z`

## Expected Posts
- `FP-BRAND-AM-07-SLOW-WALK-X` X at `2026-07-10T10:15:00-04:00`
- `FP-BRAND-AM-07-SLOW-WALK-FACEBOOK` Facebook at `2026-07-10T11:20:00-04:00`

## Link Checks
- **ok** `FP-BRAND-AM-07-SLOW-WALK-X imagery_url` 200 image/jpeg
- **ok** `FP-BRAND-AM-07-SLOW-WALK-X Album` 200 text/html
- **ok** `FP-BRAND-AM-07-SLOW-WALK-X Echo` 200 text/html
- **ok** `FP-BRAND-AM-07-SLOW-WALK-X Video` 200 text/html
- **ok** `FP-BRAND-AM-07-SLOW-WALK-FACEBOOK imagery_url` 200 image/jpeg
- **ok** `FP-BRAND-AM-07-SLOW-WALK-FACEBOOK Analog Myth` 200 text/html
- **ok** `FP-BRAND-AM-07-SLOW-WALK-FACEBOOK Echo Thread` 200 text/html
- **ok** `FP-BRAND-AM-07-SLOW-WALK-FACEBOOK Track video` 200 text/html

## Redirect Target Checks
- **ok** `FP-BRAND-AM-07-SLOW-WALK-X Album target album` 200 text/html
- **ok** `FP-BRAND-AM-07-SLOW-WALK-X Echo target echo` 200 text/html
- **warning** `FP-BRAND-AM-07-SLOW-WALK-X Video target video` 429 HTTP 429: Too Many Requests
- **ok** `FP-BRAND-AM-07-SLOW-WALK-FACEBOOK Analog Myth target album` 200 text/html
- **ok** `FP-BRAND-AM-07-SLOW-WALK-FACEBOOK Echo Thread target echo` 200 text/html
- **warning** `FP-BRAND-AM-07-SLOW-WALK-FACEBOOK Track video target video` 429 HTTP 429: Too Many Requests

## Guardrails
- Preflight is read-only; it calls the scheduler dry-run endpoint and HEAD-checks public URLs.
- It does not publish, approve, mutate, or import metrics.
- A ready preflight proves only that the next window is executable at the simulated due time.
- Rows already posted by the scheduler count as satisfied for the window; rows not yet sent must still be dry-run eligible.
- The current scheduler dry-run is reported separately so the admin does not imply future posts are due before their scheduled window.
- DistroKid HyperFollow 403/429 checks are non-blocking warnings because GitHub-hosted probes can be bot-filtered while the browser-visible public link remains the intended listening hub.
- YouTube 429 link checks are non-blocking warnings because GitHub-hosted probes can be rate-limited while the scheduler and Lily Roo-hosted links remain ready.
