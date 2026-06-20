# Backlog Reschedule Preview - Lily Roo

Generated: 2026-06-20T08:27:13.127046+00:00

## Summary
- Approved backlog rows: **1**
- Rows with known blockers: **1**
- Clear to apply without override: **0**
- Start at: **2026-06-21T10:00:00+00:00**
- Spacing hours: **24**
- Apply allowed without override: **False**
- Normal apply gate: **blocked_until_clearance_steps_complete**

## Proposed Reschedule
- **TikTok - I Learned It All in Fifteen Seconds** (`FP-AUTO-264`)
  - Current: `2026-06-09T21:25:00-04:00`
  - Proposed: `2026-06-21T10:00:00+00:00`
  - Blocker: tiktok_credentials_missing
  - Clearance: Add local TikTok OAuth credentials, then push worker secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN.
  - Clearance: Confirm TikTok public posting approval before treating auto-posting as ready.
  - Clearance: Run `python3 scripts/build_tiktok_setup_preflight.py` and `python3 scripts/refresh_promo_admin.py` after repair.

## Commands
- Preview: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-21T10:00:00+00:00' --spacing-hours 24`
- Safe apply: none until blockers clear
- Blocked apply command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-21T10:00:00+00:00' --spacing-hours 24 --apply --refresh-admin`
- Deliberate override command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-21T10:00:00+00:00' --spacing-hours 24 --allow-blocked --apply --refresh-admin`

## Guardrails
- This preview does not write schedule changes, approve posts, publish posts, or push secrets.
- The normal apply command is hidden while rows have known executor blockers.
- The override command includes `--allow-blocked` and is only for deliberate review after accepting the blocker risk.
