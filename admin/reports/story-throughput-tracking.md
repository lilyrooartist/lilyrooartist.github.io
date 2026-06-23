# Story Throughput Tracking - Lily Roo

Generated: 2026-06-23T08:58:45.965309Z

## Summary
- Story posts scheduled: **6**
- Queued future: **6**
- Past due without public URL: **0**
- Logged, waiting results: **0**
- Measured: **0**
- Platforms: **Facebook, X**

## Commands
- Preview worker export: `python3 scripts/export_social_executions.py --dry-run`
- Apply worker export after review: `python3 scripts/export_social_executions.py --refresh-admin`
- Result collection handoff: `admin/reports/experiment-result-clipboard.md`

## Rows
- **FP-STORY-TWELVE-DOLLARS-X-ARCHIVE-CTA** - X / Twelve Dollars
  - Status: `queued_future`; scheduled: `2026-06-26T10:15:00-04:00`
  - First measurement due: `2026-06-27T14:15:00+00:00`
  - Next: Wait for the scheduler to publish the row, then export social executions and log the public URL.
- **FP-STORY-TWELVE-DOLLARS-FACEBOOK-ARCHIVE-CTA** - Facebook / Twelve Dollars
  - Status: `queued_future`; scheduled: `2026-06-27T11:20:00-04:00`
  - First measurement due: `2026-06-28T15:20:00+00:00`
  - Next: Wait for the scheduler to publish the row, then export social executions and log the public URL.
- **FP-STORY-ANALOG-MYTH-X-ARCHIVE-CTA** - X / Analog Myth
  - Status: `queued_future`; scheduled: `2026-06-28T10:15:00-04:00`
  - First measurement due: `2026-06-29T14:15:00+00:00`
  - Next: Wait for the scheduler to publish the row, then export social executions and log the public URL.
- **FP-STORY-ANALOG-MYTH-FACEBOOK-ARCHIVE-CTA** - Facebook / Analog Myth
  - Status: `queued_future`; scheduled: `2026-06-29T11:20:00-04:00`
  - First measurement due: `2026-06-30T15:20:00+00:00`
  - Next: Wait for the scheduler to publish the row, then export social executions and log the public URL.
- **FP-STORY-I-LEARNED-IT-ALL-IN-FIFTEEN-SECONDS-X-ARCHIVE-CTA** - X / I Learned It All in Fifteen Seconds
  - Status: `queued_future`; scheduled: `2026-06-30T10:15:00-04:00`
  - First measurement due: `2026-07-01T14:15:00+00:00`
  - Next: Wait for the scheduler to publish the row, then export social executions and log the public URL.
- **FP-STORY-I-LEARNED-IT-ALL-IN-FIFTEEN-SECONDS-FACEBOOK-ARCHIVE-CTA** - Facebook / I Learned It All in Fifteen Seconds
  - Status: `queued_future`; scheduled: `2026-07-01T11:20:00-04:00`
  - First measurement due: `2026-07-02T15:20:00+00:00`
  - Next: Wait for the scheduler to publish the row, then export social executions and log the public URL.

## Guardrails
- This packet is read-only; it does not publish, approve, or log URLs.
- Only real public URLs from successful social executions should enter Published_Log.csv.
- Scheduled volume is not winner evidence until a public URL and measured results exist.
