# Backlog Reschedule Preview - Lily Roo

Generated: 2026-06-20T11:08:18.983693+09:00

## Summary
- Approved backlog rows: **1**
- Rows with known blockers: **1**
- Clear to apply without override: **0**
- Start at: **2026-06-21T10:00:00+09:00**
- Spacing hours: **24**
- Apply allowed without override: **False**

## Proposed Reschedule
- **TikTok - I Learned It All in Fifteen Seconds** (`FP-AUTO-264`)
  - Current: `2026-06-09T21:25:00-04:00`
  - Proposed: `2026-06-21T10:00:00+09:00`
  - Blocker: tiktok_credentials_missing

## Commands
- Preview: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-21T10:00:00+09:00' --spacing-hours 24`
- Apply after blockers are cleared: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-21T10:00:00+09:00' --spacing-hours 24 --apply --refresh-admin`

## Guardrails
- This preview does not write schedule changes, approve posts, publish posts, or push secrets.
- Apply refuses known blocked rows unless `--allow-blocked` is used after deliberate review.
