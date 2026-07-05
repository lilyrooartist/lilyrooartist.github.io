# Brand Growth Preflight - Lily Roo

Generated: 2026-07-05T09:23:24.216113Z

## Summary
- Status: **ready**
- Next window: **2026-07-05** at `2026-07-05T15:21:00Z`
- Expected posts: **2**
- Scheduler: HTTP **200**, auth `bearer`, due **2**, would post **2**, blocked **0**
- Link checks: **10 ok**, **0 failed**, **0 warning**, **0 blocking failed**
- Next proof due: `2026-07-04T16:05:00Z`
- First measurement due: `2026-07-05T15:20:00Z`

## Expected Posts
- `FP-BRAND-AM-02-GIRLS-CAMP-X` X at `2026-07-05T10:15:00-04:00`
- `FP-BRAND-AM-02-GIRLS-CAMP-FACEBOOK` Facebook at `2026-07-05T11:20:00-04:00`

## Link Checks
- **ok** `FP-BRAND-AM-02-GIRLS-CAMP-X imagery_url` 200 image/jpeg
- **ok** `FP-BRAND-AM-02-GIRLS-CAMP-X Analog Myth` 200 text/html; charset=utf-8
- **ok** `FP-BRAND-AM-02-GIRLS-CAMP-X Echo Thread` 200 text/html; charset=utf-8
- **ok** `FP-BRAND-AM-02-GIRLS-CAMP-X Track` 200 text/html; charset=utf-8
- **ok** `FP-BRAND-AM-02-GIRLS-CAMP-X Playlist` 200 text/html; charset=utf-8
- **ok** `FP-BRAND-AM-02-GIRLS-CAMP-FACEBOOK imagery_url` 200 image/jpeg
- **ok** `FP-BRAND-AM-02-GIRLS-CAMP-FACEBOOK Analog Myth` 200 text/html; charset=utf-8
- **ok** `FP-BRAND-AM-02-GIRLS-CAMP-FACEBOOK Echo Thread` 200 text/html; charset=utf-8
- **ok** `FP-BRAND-AM-02-GIRLS-CAMP-FACEBOOK Track` 200 text/html; charset=utf-8
- **ok** `FP-BRAND-AM-02-GIRLS-CAMP-FACEBOOK Playlist` 200 text/html; charset=utf-8

## Guardrails
- Preflight is read-only; it calls the scheduler dry-run endpoint and HEAD-checks public URLs.
- It does not publish, approve, mutate, or import metrics.
- A ready preflight proves only that the next window is executable at the simulated due time.
- YouTube 429 link checks are non-blocking warnings because GitHub-hosted probes can be rate-limited while the scheduler and Lily Roo-hosted links remain ready.
