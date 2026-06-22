# Backlog Reschedule Preview - Lily Roo

Generated: 2026-06-22T12:38:12.605333+00:00

## Summary
- Approved backlog rows: **0**
- Rows with known blockers: **0**
- Clear to apply without override: **0**
- Manual handoff rows excluded from auto-reschedule: **1**
- Start at: **2026-06-23T10:00:00+00:00**
- Spacing hours: **24**
- Apply allowed without override: **True**
- Normal apply gate: **clear**

## Manual Handoff Rows
- **YouTube Community - I Learned It All in Fifteen Seconds** (`FP-AUTO-261`)
  - Current: `2026-06-06T19:10:00-04:00`
  - Handoff: `admin/reports/manual-posting-clipboard.md`
  - Reason: Manual/community row is ready for manual posting and public URL logging; it is excluded from auto-reschedule commands.

## Proposed Reschedule

## Clearance Manifest
- Status: **clear**
- Blocked IDs: `none`
- Safe apply command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-23T10:00:00+00:00' --spacing-hours 24 --apply --refresh-admin`
- Partial clear apply available: **False**
- Partial clear apply count: **0**
- Apply gate: **clear**

## Partial Clear Apply
- Status: **empty**
- Clear IDs: `none`
- Blocked IDs retained: `none`
- Recommended preview: `none`
- Recommended apply: `none`

### Operator Checklist
- Preview each clear row before applying it.
- Apply only rows listed in clear_ids; do not use --allow-blocked for this partial-clear path.
- Refresh Admin after each apply command, then rebuild this preview before applying the next clear row.
- Leave blocked_ids_retained unchanged until their platform or executor clearance steps are complete.
- Run the preview command and confirm it proposes only approved unpublished backlog rows.
- If partial_clear_apply_available is true, use the scoped partial-clear commands for unblocked rows while blocked rows are repaired.
- Complete every listed platform/executor clearance step before normal apply.
- Refresh Admin and confirm the normal apply gate is clear.
- Apply only when safe_apply_command is populated without --allow-blocked.
- After apply, refresh Admin and confirm the backlog rows have future scheduled_at values.

### Completion Evidence
- The applied clear row has a future scheduled_at value in data/scheduled_posts.csv.
- data/backlog_reschedule_preview.json shows one fewer clear-to-apply past-due row after refresh.
- Blocked rows remain listed in blocked_ids_retained until their clearance steps are complete.
- data/backlog_reschedule_preview.json shows normal_apply_gate clear.
- data/platform_repair_status.json shows the affected platform repair gate clear.
- data/social_execution_snapshot.json no longer reports the row as blocked by executor/platform repair.
- data/promo_engine_status.json and lilyroo.com/admin expose a safe apply command or no approved past-due backlog.

### Clearance Guardrails
- Partial clear commands are scoped with --id and never include --allow-blocked.
- This path reschedules only unblocked approved rows; it does not approve, publish, or repair executors.
- Normal apply stays hidden while blocked_ids are present.
- Do not use the override command unless accepting the blocked executor risk deliberately.
- A reschedule does not publish, approve, or repair platform credentials by itself.

## Commands
- Preview: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-23T10:00:00+00:00' --spacing-hours 24`
- Partial clear preview: `none`
- Partial clear apply: `none`
- Safe apply: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-23T10:00:00+00:00' --spacing-hours 24 --apply --refresh-admin`
- Blocked apply command: none
- Deliberate override command: none

## Guardrails
- This preview does not write schedule changes, approve posts, publish posts, or push secrets.
- The normal apply command is hidden while rows have known executor blockers.
- The override command includes `--allow-blocked` and is only for deliberate review after accepting the blocker risk.
