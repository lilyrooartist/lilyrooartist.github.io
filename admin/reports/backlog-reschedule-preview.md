# Backlog Reschedule Preview - Lily Roo

Generated: 2026-07-20T04:06:17.082852+00:00

## Summary
- Approved backlog rows: **5**
- Rows with known blockers: **5**
- Clear to apply without override: **0**
- Manual handoff rows excluded from auto-reschedule: **0**
- Start at: **2026-07-21T10:00:00+00:00**
- Spacing hours: **24**
- Apply allowed without override: **False**
- Normal apply gate: **blocked_until_clearance_steps_complete**

## Proposed Reschedule
- **Facebook - Slow Walk** (`FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-FACEBOOK`)
  - Current: `2026-07-13T11:20:00-04:00`
  - Proposed: `2026-07-21T10:00:00+00:00`
  - Blocker: Facebook Reel hosted upload failed (422): {"debug_info":{"retriable":false,"type":"FileUrlProcessingError","message":"Unable to fetch media from URL, got status code: 403 Restricted by robots.txt"}}
  - Clearance: Clear the executor attention item in data/social_execution_snapshot.json before normal reschedule apply.
- **Facebook - Slow Walk** (`FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-FACEBOOK`)
  - Current: `2026-07-15T11:20:00-04:00`
  - Proposed: `2026-07-22T10:00:00+00:00`
  - Blocker: Facebook Reel hosted upload failed (422): {"debug_info":{"retriable":false,"type":"FileUrlProcessingError","message":"Unable to fetch media from URL, got status code: 403 Restricted by robots.txt"}}
  - Clearance: Clear the executor attention item in data/social_execution_snapshot.json before normal reschedule apply.
- **Facebook - Slow Walk** (`FP-GROWTH-RESET-03-SLOW-WALK-VISUAL-STORY-FACEBOOK`)
  - Current: `2026-07-17T11:20:00-04:00`
  - Proposed: `2026-07-23T10:00:00+00:00`
  - Blocker: Facebook Reel hosted upload failed (422): {"debug_info":{"retriable":false,"type":"FileUrlProcessingError","message":"Unable to fetch media from URL, got status code: 403 Restricted by robots.txt"}}
  - Clearance: Clear the executor attention item in data/social_execution_snapshot.json before normal reschedule apply.
- **YouTube - Slow Walk** (`FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE`)
  - Current: `2026-07-19T10:15:00-04:00`
  - Proposed: `2026-07-24T10:00:00+00:00`
  - Blocker: API request failed (400): {"error":"invalid_grant","error_description":"Token has been expired or revoked."}
  - Clearance: Clear the executor attention item in data/social_execution_snapshot.json before normal reschedule apply.
- **Facebook - Slow Walk** (`FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-FACEBOOK`)
  - Current: `2026-07-19T11:20:00-04:00`
  - Proposed: `2026-07-25T10:00:00+00:00`
  - Blocker: Facebook Reel hosted upload failed (422): {"debug_info":{"retriable":false,"type":"FileUrlProcessingError","message":"Unable to fetch media from URL, got status code: 403 Restricted by robots.txt"}}
  - Clearance: Clear the executor attention item in data/social_execution_snapshot.json before normal reschedule apply.

## Clearance Manifest
- Status: **blocked_until_clearance_steps_complete**
- Blocked IDs: `FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-FACEBOOK, FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-FACEBOOK, FP-GROWTH-RESET-03-SLOW-WALK-VISUAL-STORY-FACEBOOK, FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE, FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-FACEBOOK`
- Safe apply command: `blocked until clearance steps complete`
- Partial clear apply available: **False**
- Partial clear apply count: **0**
- Apply gate: **blocked_until_clearance_steps_complete**

## Partial Clear Apply
- Status: **empty**
- Clear IDs: `none`
- Blocked IDs retained: `FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-FACEBOOK, FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-FACEBOOK, FP-GROWTH-RESET-03-SLOW-WALK-VISUAL-STORY-FACEBOOK, FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE, FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-FACEBOOK`
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
- Preview: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-21T10:00:00+00:00' --spacing-hours 24`
- Partial clear preview: `none`
- Partial clear apply: `none`
- Safe apply: none until blockers clear
- Blocked apply command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-21T10:00:00+00:00' --spacing-hours 24 --apply --refresh-admin`
- Deliberate override command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-21T10:00:00+00:00' --spacing-hours 24 --allow-blocked --apply --refresh-admin`

## Guardrails
- This preview does not write schedule changes, approve posts, publish posts, or push secrets.
- The normal apply command is hidden while rows have known executor blockers.
- The override command includes `--allow-blocked` and is only for deliberate review after accepting the blocker risk.
