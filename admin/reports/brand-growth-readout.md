# Brand Growth Readout - Lily Roo

Generated: 2026-07-03T06:13:37.014039Z

## Summary
- Campaign rows: **16**
- Approved auto rows: **16**
- Visible in future queue: **16**
- Posted or measured rows: **0**
- Measured rows: **0**
- Ready for metric capture: **0**
- Status counts: **scheduled_future: 16**
- Next scheduled: `FP-BRAND-AM-01-13-X` at `2026-07-04T10:15:00-04:00`
- YouTube total views: **462**
- Spotify monthly listeners: **2**

## Commands
- Refresh state: `python3 scripts/refresh_promo_admin.py`
- Export posted URLs: `python3 scripts/export_social_executions.py --refresh-admin`
- Capture X metrics: `waiting for logged X campaign posts`
- Capture Facebook metrics: `waiting for logged Facebook campaign posts`

## Next Actions
- Next campaign post is FP-BRAND-AM-01-13-X at 2026-07-04T10:15:00-04:00.

## Rows
- `FP-BRAND-AM-01-13-X` X 2026-07-04T10:15:00-04:00 - **scheduled_future**
  - Next: Wait for the scheduled social executor, then refresh admin and export executions.
- `FP-BRAND-AM-01-13-FACEBOOK` Facebook 2026-07-04T11:20:00-04:00 - **scheduled_future**
  - Next: Wait for the scheduled social executor, then refresh admin and export executions.
- `FP-BRAND-AM-02-GIRLS-CAMP-X` X 2026-07-05T10:15:00-04:00 - **scheduled_future**
  - Next: Wait for the scheduled social executor, then refresh admin and export executions.
- `FP-BRAND-AM-02-GIRLS-CAMP-FACEBOOK` Facebook 2026-07-05T11:20:00-04:00 - **scheduled_future**
  - Next: Wait for the scheduled social executor, then refresh admin and export executions.
- `FP-BRAND-AM-03-ANALOG-MYTH-X` X 2026-07-06T10:15:00-04:00 - **scheduled_future**
  - Next: Wait for the scheduled social executor, then refresh admin and export executions.
- `FP-BRAND-AM-03-ANALOG-MYTH-FACEBOOK` Facebook 2026-07-06T11:20:00-04:00 - **scheduled_future**
  - Next: Wait for the scheduled social executor, then refresh admin and export executions.
- `FP-BRAND-AM-04-SPILLING-THE-TEA-X` X 2026-07-07T10:15:00-04:00 - **scheduled_future**
  - Next: Wait for the scheduled social executor, then refresh admin and export executions.
- `FP-BRAND-AM-04-SPILLING-THE-TEA-FACEBOOK` Facebook 2026-07-07T11:20:00-04:00 - **scheduled_future**
  - Next: Wait for the scheduled social executor, then refresh admin and export executions.
- `FP-BRAND-AM-05-NO-MORTGAGE-X` X 2026-07-08T10:15:00-04:00 - **scheduled_future**
  - Next: Wait for the scheduled social executor, then refresh admin and export executions.
- `FP-BRAND-AM-05-NO-MORTGAGE-FACEBOOK` Facebook 2026-07-08T11:20:00-04:00 - **scheduled_future**
  - Next: Wait for the scheduled social executor, then refresh admin and export executions.
- `FP-BRAND-AM-06-GUARDS-DOWN-X` X 2026-07-09T10:15:00-04:00 - **scheduled_future**
  - Next: Wait for the scheduled social executor, then refresh admin and export executions.
- `FP-BRAND-AM-06-GUARDS-DOWN-FACEBOOK` Facebook 2026-07-09T11:20:00-04:00 - **scheduled_future**
  - Next: Wait for the scheduled social executor, then refresh admin and export executions.
- `FP-BRAND-AM-07-SLOW-WALK-X` X 2026-07-10T10:15:00-04:00 - **scheduled_future**
  - Next: Wait for the scheduled social executor, then refresh admin and export executions.
- `FP-BRAND-AM-07-SLOW-WALK-FACEBOOK` Facebook 2026-07-10T11:20:00-04:00 - **scheduled_future**
  - Next: Wait for the scheduled social executor, then refresh admin and export executions.
- `FP-BRAND-AM-08-THE-POWER-OF-LIGHT-X` X 2026-07-11T10:15:00-04:00 - **scheduled_future**
  - Next: Wait for the scheduled social executor, then refresh admin and export executions.
- `FP-BRAND-AM-08-THE-POWER-OF-LIGHT-FACEBOOK` Facebook 2026-07-11T11:20:00-04:00 - **scheduled_future**
  - Next: Wait for the scheduled social executor, then refresh admin and export executions.

## Guardrails
- Readout only; it does not post or import metrics.
- Published_Log.csv is the source of truth for public URLs.
- Metric capture commands only target logged X/Facebook campaign post IDs.
- Unknown metrics remain blank until an API capture or visible analytics source proves them.
