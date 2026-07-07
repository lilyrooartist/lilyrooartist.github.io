# Brand Growth Preflight - Lily Roo

Generated: 2026-07-07T01:47:56.034779Z

## Summary
- Status: **ready**
- Next window: **2026-07-07** at `2026-07-07T15:21:00Z`
- Expected posts: **2**
- Scheduler simulation: HTTP **200**, auth `bearer`, simulated at `2026-07-07T15:21:00Z`, due **2**, would post **2**, blocked **0**
- Current scheduler snapshot: checked `2026-07-07T01:47:52.078952Z`, requested `2026-07-07T01:47:51.571310Z`, due **0**, would post **0**, blocked **0**
- Link checks: **8 ok**, **0 failed**, **0 warning**, **0 blocking failed**
- Tracking redirects: **6 / 6 checked ok**
- Redirect targets: **6 / 6 checked**, **6 ok**, **0 warning**, **0 blocking failed**
- Current window proof due: `2026-07-07T15:21:00Z`
- Current window measurement due: `2026-07-08T15:20:00Z`

## Expected Posts
- `FP-BRAND-AM-04-SPILLING-THE-TEA-X` X at `2026-07-07T10:15:00-04:00`
- `FP-BRAND-AM-04-SPILLING-THE-TEA-FACEBOOK` Facebook at `2026-07-07T11:20:00-04:00`

## Link Checks
- **ok** `FP-BRAND-AM-04-SPILLING-THE-TEA-X imagery_url` 200 image/jpeg
- **ok** `FP-BRAND-AM-04-SPILLING-THE-TEA-X Album` 200 text/html
- **ok** `FP-BRAND-AM-04-SPILLING-THE-TEA-X Echo` 200 text/html
- **ok** `FP-BRAND-AM-04-SPILLING-THE-TEA-X Video` 200 text/html
- **ok** `FP-BRAND-AM-04-SPILLING-THE-TEA-FACEBOOK imagery_url` 200 image/jpeg
- **ok** `FP-BRAND-AM-04-SPILLING-THE-TEA-FACEBOOK Analog Myth` 200 text/html
- **ok** `FP-BRAND-AM-04-SPILLING-THE-TEA-FACEBOOK Echo Thread` 200 text/html
- **ok** `FP-BRAND-AM-04-SPILLING-THE-TEA-FACEBOOK Track video` 200 text/html

## Redirect Target Checks
- **ok** `FP-BRAND-AM-04-SPILLING-THE-TEA-X Album target album` 200 text/html
- **ok** `FP-BRAND-AM-04-SPILLING-THE-TEA-X Echo target echo` 200 text/html
- **ok** `FP-BRAND-AM-04-SPILLING-THE-TEA-X Video target video` 200 text/html; charset=utf-8
- **ok** `FP-BRAND-AM-04-SPILLING-THE-TEA-FACEBOOK Analog Myth target album` 200 text/html
- **ok** `FP-BRAND-AM-04-SPILLING-THE-TEA-FACEBOOK Echo Thread target echo` 200 text/html
- **ok** `FP-BRAND-AM-04-SPILLING-THE-TEA-FACEBOOK Track video target video` 200 text/html; charset=utf-8

## Guardrails
- Preflight is read-only; it calls the scheduler dry-run endpoint and HEAD-checks public URLs.
- It does not publish, approve, mutate, or import metrics.
- A ready preflight proves only that the next window is executable at the simulated due time.
- The current scheduler dry-run is reported separately so the admin does not imply future posts are due before their scheduled window.
- DistroKid HyperFollow 403/429 checks are non-blocking warnings because GitHub-hosted probes can be bot-filtered while the browser-visible public link remains the intended listening hub.
- YouTube 429 link checks are non-blocking warnings because GitHub-hosted probes can be rate-limited while the scheduler and Lily Roo-hosted links remain ready.
