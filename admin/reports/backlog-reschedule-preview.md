# Backlog Reschedule Preview - Lily Roo

Generated: 2026-06-20T17:50:34.445295+09:00

## Summary
- Approved backlog rows: **1**
- Rows with known blockers: **1**
- Clear to apply without override: **0**
- Start at: **2026-06-21T10:00:00+09:00**
- Spacing hours: **24**
- Apply allowed without override: **False**
- Normal apply gate: **blocked_until_clearance_steps_complete**

## Proposed Reschedule
- **TikTok - I Learned It All in Fifteen Seconds** (`FP-AUTO-264`)
  - Current: `2026-06-09T21:25:00-04:00`
  - Proposed: `2026-06-21T10:00:00+09:00`
  - Blocker: tiktok_credentials_missing
  - Clearance: Add local TikTok OAuth credentials, then push worker secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN.
  - Clearance: Confirm TikTok public posting approval before treating auto-posting as ready.
  - Clearance: Run `python3 scripts/build_tiktok_setup_preflight.py` and `python3 scripts/refresh_promo_admin.py` after repair.

## Clearance Manifest
- Status: **blocked_until_clearance_steps_complete**
- Blocked IDs: `FP-AUTO-264`
- Safe apply command: `blocked until clearance steps complete`
- Apply gate: **blocked_until_clearance_steps_complete**

### Operator Checklist
- Run the preview command and confirm it proposes only approved unpublished backlog rows.
- Complete every listed platform/executor clearance step before normal apply.
- Refresh Admin and confirm the normal apply gate is clear.
- Apply only when safe_apply_command is populated without --allow-blocked.
- After apply, refresh Admin and confirm the backlog rows have future scheduled_at values.

### Completion Evidence
- data/backlog_reschedule_preview.json shows normal_apply_gate clear.
- data/platform_repair_status.json shows the affected platform repair gate clear.
- data/social_execution_snapshot.json no longer reports the row as blocked by executor/platform repair.
- data/promo_engine_status.json and lilyroo.com/admin expose a safe apply command or no approved past-due backlog.

### Clearance Guardrails
- Normal apply stays hidden while blocked_ids are present.
- Do not use the override command unless accepting the blocked executor risk deliberately.
- A reschedule does not publish, approve, or repair platform credentials by itself.

## Commands
- Preview: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-21T10:00:00+09:00' --spacing-hours 24`
- Safe apply: none until blockers clear
- Blocked apply command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-21T10:00:00+09:00' --spacing-hours 24 --apply --refresh-admin`
- Deliberate override command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-21T10:00:00+09:00' --spacing-hours 24 --allow-blocked --apply --refresh-admin`

## Guardrails
- This preview does not write schedule changes, approve posts, publish posts, or push secrets.
- The normal apply command is hidden while rows have known executor blockers.
- The override command includes `--allow-blocked` and is only for deliberate review after accepting the blocker risk.
