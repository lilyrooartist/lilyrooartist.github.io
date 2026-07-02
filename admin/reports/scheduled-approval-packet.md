# Scheduled Approval Packet - Lily Roo

Generated: 2026-07-02T01:10:11.519885Z

## Summary
- Approval blockers: **0**
- Auto rows: **0**
- Manual rows: **0**
- Review checks passed: **0**
- Review checks blocked: **0**
- Checked batch IDs: none
- Blocked review IDs: none
- Checked-only preview: none
- Checked-only approve after review: none
- Checked-only explicit preview: none
- Checked-only explicit approve after review: none
- Checked-only effect: **0** row(s) would change approval state
- Batch preview: none
- Batch approve after review: none
- Batch effect: **0** row(s) would change approval state

## Approval Docket
- Status: **blocked**
- Ready to approve: **0**
- Held: **0**
- Checked batch preview: `none`
- Checked batch approve after review: `none`
- Checked batch dry-run result: **0** change(s), **0** reviewed row(s), no files written
- Decision manifest: **0** reviewed row(s); ready `none`; held `none`

### Approval Apply Manifest
- Status: **blocked**
- Apply scope: **checked_batch**
- Ready IDs: `none`
- Held IDs: `none`
- Expected changes: **0**
- Preview: `none`
- Apply after review: `none`

#### Pre-Apply Checklist
- Review copy, links, and media for every ready row.
- Run the preview command and confirm it lists only ready_ids.
- Confirm held_ids are excluded from the checked batch.
- Apply only with --checked-batch after human review passes.

#### Post-Apply Evidence
- data/scheduled_posts.csv shows ready_ids changed from approved=no to approved=yes.
- data/scheduled_approval_packet.json reports fewer approval blockers after refresh.
- data/social_scheduler_dry_run.json no longer blocks the approved row on not_approved.

#### Apply Guardrails
- This manifest does not approve, publish, post, or log anything.
- Do not use the full batch command while held_ids are present.
- Do not approve held rows until failed review checks clear.

### Approval Review Runbook
- Status: **blocked**
- Ready IDs: `none`
- Blocked IDs: `none`
- Manual dispatch ready after approval: **0**
- 1. Review ready checked-batch rows - `blocked`
  - Evidence: Review copy_block, destination_links, asset_url, and checklist for each ready row.
- 2. Preview the guarded checked batch - `blocked`
  - Evidence: Dry run must report no file writes and only the checked IDs.
- 3. Apply after human review - `blocked`
  - Evidence: Apply only after human copy/media/link review passes.
- 4. Refresh and validate admin state - `ready_after_apply`; command: `python3 scripts/refresh_promo_admin.py && python3 scripts/validate_content_system.py`
  - Evidence: Admin should show fewer approval blockers and fresh execution state.

### Ready Row Checklist
- None; all currently reviewed rows are held until failed checks clear.

### Ready to Approve
- None

### Held
- None

## Review Queue

## Guardrails
- This packet does not approve, publish, or post anything.
- Use preview commands before approval apply commands.
- Manual rows still require human posting and public URL logging after approval.
