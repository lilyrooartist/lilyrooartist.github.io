# Scheduled Approval Packet - Lily Roo

Generated: 2026-06-22T07:37:16.127104Z

## Summary
- Approval blockers: **1**
- Auto rows: **1**
- Manual rows: **0**
- Review checks passed: **0**
- Review checks blocked: **1**
- Checked batch IDs: none
- Blocked review IDs: `FP-AUTO-259`
- Checked-only preview: none
- Checked-only approve after review: none
- Checked-only explicit preview: none
- Checked-only explicit approve after review: none
- Checked-only effect: **0** row(s) would change approval state
- Batch preview: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-259 --dry-run`
- Batch approve after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-259 --refresh-admin`
- Batch effect: **1** row(s) would change approval state

## Approval Docket
- Status: **blocked**
- Ready to approve: **0**
- Held: **1**
- Checked batch preview: `none`
- Checked batch approve after review: `none`
- Checked batch dry-run result: **0** change(s), **0** reviewed row(s), no files written
- Decision manifest: **1** reviewed row(s); ready `none`; held `FP-AUTO-259`

### Approval Apply Manifest
- Status: **blocked**
- Apply scope: **checked_batch**
- Ready IDs: `none`
- Held IDs: `FP-AUTO-259`
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
- data/social_scheduler_dry_run.json no longer blocks the approved Instagram row on not_approved.
- Manual-dispatch ready rows remain in the manual posting/logging workflow until a real public URL exists.

#### Apply Guardrails
- This manifest does not approve, publish, post, or log anything.
- Do not use the full batch command while held_ids are present.
- Do not approve held rows until failed review checks clear.
- Manual dispatch remains separate from approval.

### Approval Review Runbook
- Status: **blocked**
- Ready IDs: `none`
- Blocked IDs: `FP-AUTO-259`
- Manual dispatch ready after approval: **0**
- 1. Review ready checked-batch rows - `blocked`
  - Evidence: Review copy_block, destination_links, asset_url, and checklist for each ready row.
- 2. Preview the guarded checked batch - `blocked`
  - Evidence: Dry run must report no file writes and only the checked IDs.
- 3. Apply after human review - `blocked`
  - Evidence: Apply only after human copy/media/link review passes.
- 4. Refresh and validate admin state - `ready_after_apply`; command: `python3 scripts/refresh_promo_admin.py && python3 scripts/validate_content_system.py`
  - Evidence: Admin should show fewer approval blockers and fresh execution state.
- 5. Post and log manual rows - `not_applicable`; command: `python3 scripts/log_manual_distribution.py --dry-run`
  - Evidence: Manual YouTube Community rows need real public post URLs before logging.

### Ready Row Checklist
- None; all currently reviewed rows are held until failed checks clear.

### Ready to Approve
- None

### Held
- **TikTok - I Learned It All in Fifteen Seconds** (`FP-AUTO-259`)
  - Held by `platform_readiness`: Executor readiness snapshot marks platform blocked. Missing secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN.
    - Repair next step: Complete the TikTok setup preflight before approving this row; approval alone would not make the executor publishable.
    - Repair report: `admin/reports/tiktok-setup-preflight.md`
    - Repair runbook: `admin/reports/tiktok-repair-runbook.md`
    - Repair command: `python3 scripts/tiktok_oauth_handoff.py`

## Review Queue
- **TikTok - I Learned It All in Fifteen Seconds** (`FP-AUTO-259`)
  - Scheduled: `2026-06-05T20:40:00-04:00`; mode: `auto`; type: `video`
  - Reason: `not_approved`
  - Copy: I learned it all in fifteen seconds and somehow still have homework. Streaming now.
  - Link/reply: Listen on Spotify: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi | Apple Music: https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249 | YouTube Music: https://music.youtube.com/watch?v=vK0mDIW65o4
  - Asset: https://www.lilyroo.com/assets/ig/01_i_learned_it_all_60s.mp4
  - Review checks:
    - `pass` copy_present: 83 characters of primary copy.
    - `pass` destination_links_present: 3 link(s): https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi, https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249, https://music.youtube.com/watch?v=vK0mDIW65o4
    - `pass` asset_file_present: https://www.lilyroo.com/assets/ig/01_i_learned_it_all_60s.mp4 maps to assets/ig/01_i_learned_it_all_60s.mp4.
    - `pass` executor_blocker_confirmed: Current executor state is blocked / not_approved.
    - `fail` platform_readiness: Executor readiness snapshot marks platform blocked. Missing secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN.
  - Destination link evidence:
    - `verified_local_evidence` https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi: HyperFollow spotify link (data/hyperfollow_store_links_snapshot.json); spotify alignment check: ok (data/first_single_alignment_audit.json)
    - `verified_local_evidence` https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249: HyperFollow applemusic link (data/hyperfollow_store_links_snapshot.json); HyperFollow itunes link (data/hyperfollow_store_links_snapshot.json); apple_music alignment check: ok (data/first_single_alignment_audit.json); Apple Music release snapshot: I Learned It All in Fifteen Seconds - Single (data/apple_music_release_snapshot.json)
    - `verified_local_evidence` https://music.youtube.com/watch?v=vK0mDIW65o4: youtube_music alignment check: ok (data/first_single_alignment_audit.json); YouTube Music release snapshot: I Learned It All in Fifteen Seconds - Lily Roo (data/youtube_music_release_snapshot.json)
  - Approval review status: `held_by_failed_checks`
  - Checked batch member: `False`
  - Failed checks holding this row:
    - `platform_readiness`: Executor readiness snapshot marks platform blocked. Missing secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN.
      - Repair next step: Complete the TikTok setup preflight before approving this row; approval alone would not make the executor publishable.
      - Repair report: `admin/reports/tiktok-setup-preflight.md`
      - Repair runbook: `admin/reports/tiktok-repair-runbook.md`
      - Repair command: `python3 scripts/tiktok_oauth_handoff.py`
  - Batch reason: Held outside checked batch until failed/review checks clear.
  - Approval effect: `approved 'no' -> 'yes'`
  - Preview approval: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-259 --dry-run`
  - Approve after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-259 --refresh-admin`

## Guardrails
- This packet does not approve, publish, or post anything.
- Use preview commands before approval apply commands.
- Manual rows still require human posting and public URL logging after approval.
