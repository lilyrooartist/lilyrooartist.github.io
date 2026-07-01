# Story Throughput Tracking - Lily Roo

Generated: 2026-07-01T22:21:51.944841Z

## Summary
- Story posts scheduled: **6**
- Queued future: **0**
- Past due without public URL: **0**
- Logged, waiting results: **6**
- Measured: **0**
- Platforms: **Facebook, X**

## Commands
- Preview worker export: `python3 scripts/export_social_executions.py --dry-run`
- Apply worker export after review: `python3 scripts/export_social_executions.py --refresh-admin`
- Result collection handoff: `admin/reports/experiment-result-clipboard.md`

## Rows
- **FP-STORY-TWELVE-DOLLARS-X-ARCHIVE-CTA** - X / Twelve Dollars
  - Status: `logged_waiting_results`; scheduled: `2026-06-26T10:15:00-04:00`
  - Public URL: https://x.com/i/web/status/2070511391048405318
  - First measurement due: `2026-06-30T00:00:00+00:00`
  - Next: Collect first result metrics after the measurement window and import them with evidence notes.
- **FP-STORY-TWELVE-DOLLARS-FACEBOOK-ARCHIVE-CTA** - Facebook / Twelve Dollars
  - Status: `logged_waiting_results`; scheduled: `2026-06-27T11:20:00-04:00`
  - Public URL: https://www.facebook.com/903693509504290_122120594331249470
  - First measurement due: `2026-07-01T00:00:00+00:00`
  - Next: Collect first result metrics after the measurement window and import them with evidence notes.
- **FP-STORY-ANALOG-MYTH-X-ARCHIVE-CTA** - X / Analog Myth
  - Status: `logged_waiting_results`; scheduled: `2026-06-28T10:15:00-04:00`
  - Public URL: https://x.com/i/web/status/2071236124497080380
  - First measurement due: `2026-06-30T00:00:00+00:00`
  - Next: Collect first result metrics after the measurement window and import them with evidence notes.
- **FP-STORY-ANALOG-MYTH-FACEBOOK-ARCHIVE-CTA** - Facebook / Analog Myth
  - Status: `logged_waiting_results`; scheduled: `2026-06-29T11:20:00-04:00`
  - Public URL: https://www.facebook.com/903693509504290_122120594589249470
  - First measurement due: `2026-07-01T00:00:00+00:00`
  - Next: Collect first result metrics after the measurement window and import them with evidence notes.
- **FP-STORY-I-LEARNED-IT-ALL-IN-FIFTEEN-SECONDS-X-ARCHIVE-CTA** - X / I Learned It All in Fifteen Seconds
  - Status: `logged_waiting_results`; scheduled: `2026-06-30T10:15:00-04:00`
  - Public URL: https://x.com/i/web/status/2071960909967442193
  - First measurement due: `2026-07-02T00:00:00+00:00`
  - Next: Collect first result metrics after the measurement window and import them with evidence notes.
- **FP-STORY-I-LEARNED-IT-ALL-IN-FIFTEEN-SECONDS-FACEBOOK-ARCHIVE-CTA** - Facebook / I Learned It All in Fifteen Seconds
  - Status: `logged_waiting_results`; scheduled: `2026-07-01T11:20:00-04:00`
  - Public URL: https://www.facebook.com/903693509504290_122120699235249470
  - First measurement due: `2026-07-02T00:00:00+00:00`
  - Next: Collect first result metrics after the measurement window and import them with evidence notes.

## Guardrails
- This packet is read-only; it does not publish, approve, or log URLs.
- Only real public URLs from successful social executions should enter Published_Log.csv.
- Scheduled volume is not winner evidence until a public URL and measured results exist.
