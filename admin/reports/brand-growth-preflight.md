# Brand Growth Preflight - Lily Roo

Generated: 2026-07-05T21:36:15.198219Z

## Summary
- Status: **needs_attention**
- Next window: **2026-07-06** at `2026-07-06T15:21:00Z`
- Expected posts: **2**
- Scheduler: HTTP **200**, auth `bearer`, due **2**, would post **2**, blocked **0**
- Link checks: **8 ok**, **2 failed**, **0 warning**, **2 blocking failed**
- Next proof due: `2026-07-04T16:05:00Z`
- First measurement due: `2026-07-05T15:20:00Z`

## Expected Posts
- `FP-BRAND-AM-03-ANALOG-MYTH-X` X at `2026-07-06T10:15:00-04:00`
- `FP-BRAND-AM-03-ANALOG-MYTH-FACEBOOK` Facebook at `2026-07-06T11:20:00-04:00`

## Link Checks
- **ok** `FP-BRAND-AM-03-ANALOG-MYTH-X imagery_url` 200 image/jpeg
- **failed** `FP-BRAND-AM-03-ANALOG-MYTH-X Listen` 403 HTTP 403: Forbidden
- **ok** `FP-BRAND-AM-03-ANALOG-MYTH-X Album page` 200 text/html; charset=utf-8
- **ok** `FP-BRAND-AM-03-ANALOG-MYTH-X Echo Thread` 200 text/html; charset=utf-8
- **ok** `FP-BRAND-AM-03-ANALOG-MYTH-X Track video` 200 text/html; charset=utf-8
- **ok** `FP-BRAND-AM-03-ANALOG-MYTH-FACEBOOK imagery_url` 200 image/jpeg
- **failed** `FP-BRAND-AM-03-ANALOG-MYTH-FACEBOOK Listen` 403 HTTP 403: Forbidden
- **ok** `FP-BRAND-AM-03-ANALOG-MYTH-FACEBOOK Album page` 200 text/html; charset=utf-8
- **ok** `FP-BRAND-AM-03-ANALOG-MYTH-FACEBOOK Echo Thread` 200 text/html; charset=utf-8
- **ok** `FP-BRAND-AM-03-ANALOG-MYTH-FACEBOOK Track video` 200 text/html; charset=utf-8

## Guardrails
- Preflight is read-only; it calls the scheduler dry-run endpoint and HEAD-checks public URLs.
- It does not publish, approve, mutate, or import metrics.
- A ready preflight proves only that the next window is executable at the simulated due time.
- YouTube 429 link checks are non-blocking warnings because GitHub-hosted probes can be rate-limited while the scheduler and Lily Roo-hosted links remain ready.
