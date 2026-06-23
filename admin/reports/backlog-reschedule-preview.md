# Backlog Reschedule Preview - Lily Roo

Generated: 2026-06-23T14:03:53.987272+08:00

## Summary
- Approved backlog rows: **2**
- Rows with known blockers: **2**
- Clear to apply without override: **0**
- Manual handoff rows excluded from auto-reschedule: **0**
- Start at: **2026-06-24T10:00:00+08:00**
- Spacing hours: **24**
- Apply allowed without override: **False**
- Normal apply gate: **blocked_until_clearance_steps_complete**

## Proposed Reschedule
- **Instagram - I Learned It All in Fifteen Seconds** (`FP-AUTO-258`)
  - Current: `2026-06-23T10:00:00+08:00`
  - Proposed: `2026-06-24T10:00:00+08:00`
  - Blocker: Instagram posting could not resolve instagram_business_account; reconnect or set IG_BUSINESS_ACCOUNT_ID.
  - Clearance: Clear the executor attention item in data/social_execution_snapshot.json before normal reschedule apply.
- **TikTok - I Learned It All in Fifteen Seconds** (`FP-AUTO-264`)
  - Current: `2026-06-23T10:00:00+08:00`
  - Proposed: `2026-06-25T10:00:00+08:00`
  - Blocker: tiktok_credentials_missing
  - Clearance: Add local TikTok OAuth credentials, then push upload-mode worker secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN.
  - Clearance: Keep direct public posting blocked until TikTok public-posting approval is confirmed; upload mode can still create inbox drafts after credentials.
  - Clearance: Run `python3 scripts/build_tiktok_setup_preflight.py` and `python3 scripts/refresh_promo_admin.py` after repair.

## Clearance Manifest
- Status: **blocked_until_clearance_steps_complete**
- Blocked IDs: `FP-AUTO-258, FP-AUTO-264`
- Safe apply command: `blocked until clearance steps complete`
- Partial clear apply available: **False**
- Partial clear apply count: **0**
- Apply gate: **blocked_until_clearance_steps_complete**

## Partial Clear Apply
- Status: **empty**
- Clear IDs: `none`
- Blocked IDs retained: `FP-AUTO-258, FP-AUTO-264`
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
- Preview: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-24T10:00:00+08:00' --spacing-hours 24`
- Partial clear preview: `none`
- Partial clear apply: `none`
- Safe apply: none until blockers clear
- Blocked apply command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-24T10:00:00+08:00' --spacing-hours 24 --apply --refresh-admin`
- Deliberate override command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-24T10:00:00+08:00' --spacing-hours 24 --allow-blocked --apply --refresh-admin`

## Guardrails
- This preview does not write schedule changes, approve posts, publish posts, or push secrets.
- The normal apply command is hidden while rows have known executor blockers.
- The override command includes `--allow-blocked` and is only for deliberate review after accepting the blocker risk.
