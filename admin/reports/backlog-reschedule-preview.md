# Backlog Reschedule Preview - Lily Roo

Generated: 2026-06-19T10:57:59.754630+00:00

## Summary
- Approved backlog rows: **3**
- Rows with known blockers: **3**
- Clear to apply without override: **0**
- Start at: **2026-06-20T10:00:00+00:00**
- Spacing hours: **24**
- Apply allowed without override: **False**

## Proposed Reschedule
- **Instagram - I Learned It All in Fifteen Seconds** (`FP-AUTO-263`)
  - Current: `2026-06-08T14:05:00-04:00`
  - Proposed: `2026-06-20T10:00:00+00:00`
  - Blocker: Instagram posting could not resolve instagram_business_account; reconnect or set IG_BUSINESS_ACCOUNT_ID.
- **TikTok - I Learned It All in Fifteen Seconds** (`FP-AUTO-264`)
  - Current: `2026-06-09T21:25:00-04:00`
  - Proposed: `2026-06-21T10:00:00+00:00`
  - Blocker: tiktok_credentials_missing
- **Facebook - I Learned It All in Fifteen Seconds** (`FP-AUTO-265`)
  - Current: `2026-06-10T12:30:00-04:00`
  - Proposed: `2026-06-22T10:00:00+00:00`
  - Blocker: Facebook blocked Page publishing until identity is confirmed in the Facebook app.

## Commands
- Preview: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-20T10:00:00+00:00' --spacing-hours 24`
- Apply after blockers are cleared: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-20T10:00:00+00:00' --spacing-hours 24 --apply --refresh-admin`

## Guardrails
- This preview does not write schedule changes, approve posts, publish posts, or push secrets.
- Apply refuses known blocked rows unless `--allow-blocked` is used after deliberate review.
