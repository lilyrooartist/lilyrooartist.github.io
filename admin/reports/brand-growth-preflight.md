# Brand Growth Preflight - Lily Roo

Generated: 2026-07-06T00:37:19.469261Z

## Summary
- Status: **ready**
- Next window: **2026-07-06** at `2026-07-06T15:21:00Z`
- Expected posts: **2**
- Scheduler: HTTP **200**, auth `bearer`, due **2**, would post **2**, blocked **0**
- Link checks: **7 ok**, **0 failed**, **0 warning**, **0 blocking failed**
- Next proof due: `2026-07-04T16:05:00Z`
- First measurement due: `2026-07-05T15:20:00Z`

## Expected Posts
- `FP-BRAND-AM-03-ANALOG-MYTH-X` X at `2026-07-06T10:15:00-04:00`
- `FP-BRAND-AM-03-ANALOG-MYTH-FACEBOOK` Facebook at `2026-07-06T11:20:00-04:00`

## Link Checks
- **ok** `FP-BRAND-AM-03-ANALOG-MYTH-X imagery_url` 200 image/jpeg
- **ok** `FP-BRAND-AM-03-ANALOG-MYTH-X Analog Myth` 200 text/html
- **ok** `FP-BRAND-AM-03-ANALOG-MYTH-X Track video` 200 text/html
- **ok** `FP-BRAND-AM-03-ANALOG-MYTH-FACEBOOK imagery_url` 200 image/jpeg
- **ok** `FP-BRAND-AM-03-ANALOG-MYTH-FACEBOOK Analog Myth` 200 text/html
- **ok** `FP-BRAND-AM-03-ANALOG-MYTH-FACEBOOK Echo Thread` 200 text/html
- **ok** `FP-BRAND-AM-03-ANALOG-MYTH-FACEBOOK Track video` 200 text/html

## Guardrails
- Preflight is read-only; it calls the scheduler dry-run endpoint and HEAD-checks public URLs.
- It does not publish, approve, mutate, or import metrics.
- A ready preflight proves only that the next window is executable at the simulated due time.
- DistroKid HyperFollow 403/429 checks are non-blocking warnings because GitHub-hosted probes can be bot-filtered while the browser-visible public link remains the intended listening hub.
- YouTube 429 link checks are non-blocking warnings because GitHub-hosted probes can be rate-limited while the scheduler and Lily Roo-hosted links remain ready.
