# Backlog Reschedule Preview - Lily Roo

Generated: 2026-06-20T09:49:26.687995+09:00

## Summary
- Approved backlog rows: **3**
- Rows with known blockers: **3**
- Clear to apply without override: **0**
- Start at: **2026-06-21T10:00:00+09:00**
- Spacing hours: **24**
- Apply allowed without override: **False**

## Proposed Reschedule
- **Instagram - I Learned It All in Fifteen Seconds** (`FP-AUTO-263`)
  - Current: `2026-06-08T14:05:00-04:00`
  - Proposed: `2026-06-21T10:00:00+09:00`
  - Blocker: Instagram retry cap reached; verify instagram_business_account repair before resetting execution state.
- **TikTok - I Learned It All in Fifteen Seconds** (`FP-AUTO-264`)
  - Current: `2026-06-09T21:25:00-04:00`
  - Proposed: `2026-06-22T10:00:00+09:00`
  - Blocker: tiktok_credentials_missing
- **Facebook - I Learned It All in Fifteen Seconds** (`FP-AUTO-265`)
  - Current: `2026-06-10T12:30:00-04:00`
  - Proposed: `2026-06-23T10:00:00+09:00`
  - Blocker: Facebook retry cap reached; rerun the Facebook dry-run check after identity confirmation.

## Commands
- Preview: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-21T10:00:00+09:00' --spacing-hours 24`
- Apply after blockers are cleared: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-21T10:00:00+09:00' --spacing-hours 24 --apply --refresh-admin`

## Guardrails
- This preview does not write schedule changes, approve posts, publish posts, or push secrets.
- Apply refuses known blocked rows unless `--allow-blocked` is used after deliberate review.
