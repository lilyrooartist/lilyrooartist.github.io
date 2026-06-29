# Scheduled Approval Packet - Lily Roo

Generated: 2026-06-29T15:09:58.604044Z

## Summary
- Approval blockers: **1**
- Auto rows: **1**
- Manual rows: **0**
- Review checks passed: **1**
- Review checks blocked: **0**
- Checked batch IDs: `FP-AUTO-259`
- Blocked review IDs: none
- Checked-only preview: `python3 scripts/update_scheduled_post_approval.py --checked-batch --dry-run`
- Checked-only approve after review: `python3 scripts/update_scheduled_post_approval.py --checked-batch --refresh-admin`
- Checked-only explicit preview: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-259 --dry-run`
- Checked-only explicit approve after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-259 --refresh-admin`
- Checked-only effect: **1** row(s) would change approval state
- Batch preview: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-259 --dry-run`
- Batch approve after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-259 --refresh-admin`
- Batch effect: **1** row(s) would change approval state

## Approval Docket
- Status: **ready_for_review**
- Ready to approve: **1**
- Held: **0**
- Checked batch preview: `python3 scripts/update_scheduled_post_approval.py --checked-batch --dry-run`
- Checked batch approve after review: `python3 scripts/update_scheduled_post_approval.py --checked-batch --refresh-admin`
- Checked batch dry-run result: **1** change(s), **1** reviewed row(s), no files written
- Decision manifest: **1** reviewed row(s); ready `FP-AUTO-259`; held `none`

### Approval Apply Manifest
- Status: **ready_for_human_review**
- Apply scope: **checked_batch**
- Ready IDs: `FP-AUTO-259`
- Held IDs: `none`
- Expected changes: **1**
- Preview: `python3 scripts/update_scheduled_post_approval.py --checked-batch --dry-run`
- Apply after review: `python3 scripts/update_scheduled_post_approval.py --checked-batch --refresh-admin`

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
- Status: **ready_for_review**
- Ready IDs: `FP-AUTO-259`
- Blocked IDs: `none`
- Manual dispatch ready after approval: **0**
- 1. Review ready checked-batch rows - `ready_for_review`
  - Evidence: Review copy_block, destination_links, asset_url, and checklist for each ready row.
- 2. Preview the guarded checked batch - `ready_for_review`; command: `python3 scripts/update_scheduled_post_approval.py --checked-batch --dry-run`
  - Evidence: Dry run must report no file writes and only the checked IDs.
- 3. Apply after human review - `ready_after_review`; command: `python3 scripts/update_scheduled_post_approval.py --checked-batch --refresh-admin`
  - Evidence: Apply only after human copy/media/link review passes.
- 4. Refresh and validate admin state - `ready_after_apply`; command: `python3 scripts/refresh_promo_admin.py && python3 scripts/validate_content_system.py`
  - Evidence: Admin should show fewer approval blockers and fresh execution state.

### Ready Row Checklist
- **TikTok - I Learned It All in Fifteen Seconds** (`FP-AUTO-259`)
  - `ready_for_human_review` copy: 83 primary-copy character(s)
  - `ready_for_human_review` destination_links: 3/3 link(s) have local evidence
  - `ready_for_human_review` media_asset: assets/ig/01_i_learned_it_all_60s.mp4
  - `ready_for_human_review` platform_readiness: All automated review checks passed.
  - Next: Approve with the checked batch; executor can retry once approval is visible.

### Ready to Approve
- **TikTok - I Learned It All in Fifteen Seconds** (`FP-AUTO-259`)
  - Scheduled: `2026-06-05T20:40:00-04:00`; mode: `auto`; type: `video`
  - Paste text: I learned it all in fifteen seconds and somehow still have homework. Streaming now.

Listen on Spotify: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi | Apple Music: https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249 | YouTube Music: https://music.youtube.com/watch?v=vK0mDIW65o4
  - Asset: https://www.lilyroo.com/assets/ig/01_i_learned_it_all_60s.mp4
  - Destination links: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi, https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249, https://music.youtube.com/watch?v=vK0mDIW65o4
  - Destination link evidence:
    - `verified_local_evidence` https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi: HyperFollow spotify link (data/hyperfollow_store_links_snapshot.json); spotify alignment check: ok (data/first_single_alignment_audit.json)
    - `verified_local_evidence` https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249: HyperFollow applemusic link (data/hyperfollow_store_links_snapshot.json); HyperFollow itunes link (data/hyperfollow_store_links_snapshot.json); apple_music alignment check: ok (data/first_single_alignment_audit.json); Apple Music release snapshot: I Learned It All in Fifteen Seconds - Single (data/apple_music_release_snapshot.json)
    - `verified_local_evidence` https://music.youtube.com/watch?v=vK0mDIW65o4: youtube_music alignment check: ok (data/first_single_alignment_audit.json); YouTube Music release snapshot: I Learned It All in Fifteen Seconds - Lily Roo (data/youtube_music_release_snapshot.json)
  - Preview: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-259 --dry-run`
  - Apply after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-259 --refresh-admin`

### Held
- None

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
    - `pass` platform_readiness: Executor readiness snapshot marks platform ready.
  - Destination link evidence:
    - `verified_local_evidence` https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi: HyperFollow spotify link (data/hyperfollow_store_links_snapshot.json); spotify alignment check: ok (data/first_single_alignment_audit.json)
    - `verified_local_evidence` https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249: HyperFollow applemusic link (data/hyperfollow_store_links_snapshot.json); HyperFollow itunes link (data/hyperfollow_store_links_snapshot.json); apple_music alignment check: ok (data/first_single_alignment_audit.json); Apple Music release snapshot: I Learned It All in Fifteen Seconds - Single (data/apple_music_release_snapshot.json)
    - `verified_local_evidence` https://music.youtube.com/watch?v=vK0mDIW65o4: youtube_music alignment check: ok (data/first_single_alignment_audit.json); YouTube Music release snapshot: I Learned It All in Fifteen Seconds - Lily Roo (data/youtube_music_release_snapshot.json)
  - Approval review status: `checked_batch_ready`
  - Checked batch member: `True`
  - Batch reason: All automated review checks passed.
  - Approval effect: `approved 'no' -> 'yes'`
  - Preview approval: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-259 --dry-run`
  - Approve after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-259 --refresh-admin`

## Guardrails
- This packet does not approve, publish, or post anything.
- Use preview commands before approval apply commands.
- Manual rows still require human posting and public URL logging after approval.
