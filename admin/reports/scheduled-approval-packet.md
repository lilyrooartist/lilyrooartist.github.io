# Scheduled Approval Packet - Lily Roo

Generated: 2026-06-20T12:28:20.381672Z

## Summary
- Approval blockers: **3**
- Auto rows: **2**
- Manual rows: **1**
- Review checks passed: **2**
- Review checks blocked: **1**
- Checked batch IDs: `FP-AUTO-258, FP-AUTO-261`
- Blocked review IDs: `FP-AUTO-259`
- Checked-only preview: `python3 scripts/update_scheduled_post_approval.py --checked-batch --dry-run`
- Checked-only approve after review: `python3 scripts/update_scheduled_post_approval.py --checked-batch --refresh-admin`
- Checked-only explicit preview: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-258 FP-AUTO-261 --dry-run`
- Checked-only explicit approve after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-258 FP-AUTO-261 --refresh-admin`
- Checked-only effect: **0** row(s) would change approval state
- Batch preview: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-258 FP-AUTO-259 FP-AUTO-261 --dry-run`
- Batch approve after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-258 FP-AUTO-259 FP-AUTO-261 --refresh-admin`
- Batch effect: **1** row(s) would change approval state

## Approval Docket
- Status: **ready_for_review**
- Ready to approve: **2**
- Held: **1**
- Checked batch preview: `python3 scripts/update_scheduled_post_approval.py --checked-batch --dry-run`
- Checked batch approve after review: `python3 scripts/update_scheduled_post_approval.py --checked-batch --refresh-admin`
- Checked batch dry-run result: **0** change(s), **2** reviewed row(s), no files written
- Decision manifest: **3** reviewed row(s); ready `FP-AUTO-258, FP-AUTO-261`; held `FP-AUTO-259`

### Approval Apply Manifest
- Status: **ready_for_human_review**
- Apply scope: **checked_batch**
- Ready IDs: `FP-AUTO-258, FP-AUTO-261`
- Held IDs: `FP-AUTO-259`
- Expected changes: **0**
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
- data/social_scheduler_dry_run.json no longer blocks the approved Instagram row on not_approved.
- Manual-dispatch ready rows remain in the manual posting/logging workflow until a real public URL exists.

#### Apply Guardrails
- This manifest does not approve, publish, post, or log anything.
- Do not use the full batch command while held_ids are present.
- Do not approve held rows until failed review checks clear.
- Manual dispatch remains separate from approval.

### Approval Review Runbook
- Status: **ready_for_review**
- Ready IDs: `FP-AUTO-258, FP-AUTO-261`
- Blocked IDs: `FP-AUTO-259`
- Manual dispatch ready after approval: **1**
- 1. Review ready checked-batch rows - `ready_for_review`
  - Evidence: Review copy_block, destination_links, asset_url, and checklist for each ready row.
- 2. Preview the guarded checked batch - `ready_for_review`; command: `python3 scripts/update_scheduled_post_approval.py --checked-batch --dry-run`
  - Evidence: Dry run must report no file writes and only the checked IDs.
- 3. Apply after human review - `ready_after_review`; command: `python3 scripts/update_scheduled_post_approval.py --checked-batch --refresh-admin`
  - Evidence: Apply only after human copy/media/link review passes.
- 4. Refresh and validate admin state - `ready_after_apply`; command: `python3 scripts/refresh_promo_admin.py && python3 scripts/validate_content_system.py`
  - Evidence: Admin should show fewer approval blockers and fresh execution state.
- 5. Post and log manual rows - `required_after_apply`; command: `python3 scripts/log_manual_distribution.py --dry-run`
  - Evidence: Manual YouTube Community rows need real public post URLs before logging.

### Ready Row Checklist
- **Instagram - I Learned It All in Fifteen Seconds** (`FP-AUTO-258`)
  - `ready_for_human_review` copy: 104 primary-copy character(s)
  - `ready_for_human_review` destination_links: 3/3 link(s) have local evidence
  - `ready_for_human_review` media_asset: assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg
  - `ready_for_human_review` platform_readiness: All automated review checks passed.
  - Next: Approve with the checked batch; executor can retry once approval is visible.
- **YouTube Community - I Learned It All in Fifteen Seconds** (`FP-AUTO-261`)
  - `ready_for_human_review` copy: 119 primary-copy character(s)
  - `ready_for_human_review` destination_links: 4/4 link(s) have local evidence
  - `ready_for_human_review` media_asset: assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg
  - `ready_for_human_review` platform_readiness: All automated review checks passed.
  - `required_after_approval` manual_dispatch: Post manually and log the public URL after the checked approval batch is applied.
  - Next: Approve with the checked batch, then post manually and log the public URL.

### Ready to Approve
- **Instagram - I Learned It All in Fifteen Seconds** (`FP-AUTO-258`)
  - Scheduled: `2026-06-05T15:35:00-04:00`; mode: `auto`; type: `image`
  - Paste text: The first Lily Roo single is live, and the cover art has been remastered into its proper tiny-room glow.

Listen on Spotify: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi | Apple Music: https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249 | YouTube Music: https://music.youtube.com/watch?v=vK0mDIW65o4
  - Asset: https://www.lilyroo.com/assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg
  - Destination links: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi, https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249, https://music.youtube.com/watch?v=vK0mDIW65o4
  - Destination link evidence:
    - `verified_local_evidence` https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi: HyperFollow spotify link (data/hyperfollow_store_links_snapshot.json); spotify alignment check: ok (data/first_single_alignment_audit.json)
    - `verified_local_evidence` https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249: HyperFollow applemusic link (data/hyperfollow_store_links_snapshot.json); HyperFollow itunes link (data/hyperfollow_store_links_snapshot.json); apple_music alignment check: ok (data/first_single_alignment_audit.json); Apple Music release snapshot: I Learned It All in Fifteen Seconds - Single (data/apple_music_release_snapshot.json)
    - `verified_local_evidence` https://music.youtube.com/watch?v=vK0mDIW65o4: youtube_music alignment check: ok (data/first_single_alignment_audit.json); YouTube Music release snapshot: I Learned It All in Fifteen Seconds - Lily Roo (data/youtube_music_release_snapshot.json)
  - Preview: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-258 --dry-run`
  - Apply after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-258 --refresh-admin`
- **YouTube Community - I Learned It All in Fifteen Seconds** (`FP-AUTO-261`)
  - Scheduled: `2026-06-06T19:10:00-04:00`; mode: `manual`; type: `community`
  - Paste text: New transmission: I Learned It All in Fifteen Seconds is live. Remastered cover art, same suspicious amount of feeling.

Stream: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi | Apple Music: https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249 | YouTube: https://www.youtube.com/@lilyroo.artist | YouTube Music: https://music.youtube.com/watch?v=vK0mDIW65o4
  - Asset: https://www.lilyroo.com/assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg
  - Destination links: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi, https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249, https://www.youtube.com/@lilyroo.artist, https://music.youtube.com/watch?v=vK0mDIW65o4
  - Destination link evidence:
    - `verified_local_evidence` https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi: HyperFollow spotify link (data/hyperfollow_store_links_snapshot.json); spotify alignment check: ok (data/first_single_alignment_audit.json)
    - `verified_local_evidence` https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249: HyperFollow applemusic link (data/hyperfollow_store_links_snapshot.json); HyperFollow itunes link (data/hyperfollow_store_links_snapshot.json); apple_music alignment check: ok (data/first_single_alignment_audit.json); Apple Music release snapshot: I Learned It All in Fifteen Seconds - Single (data/apple_music_release_snapshot.json)
    - `verified_local_evidence` https://www.youtube.com/@lilyroo.artist: YouTube artist channel snapshot: Lily Roo (data/youtube_title_track_snapshot.json)
    - `verified_local_evidence` https://music.youtube.com/watch?v=vK0mDIW65o4: youtube_music alignment check: ok (data/first_single_alignment_audit.json); YouTube Music release snapshot: I Learned It All in Fifteen Seconds - Lily Roo (data/youtube_music_release_snapshot.json)
  - Manual dispatch required after approval.
  - Preview: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-261 --dry-run`
  - Apply after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-261 --refresh-admin`

### Held
- **TikTok - I Learned It All in Fifteen Seconds** (`FP-AUTO-259`)
  - Held by `platform_readiness`: Executor readiness snapshot marks platform blocked. Missing secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN.

## Review Queue
- **Instagram - I Learned It All in Fifteen Seconds** (`FP-AUTO-258`)
  - Scheduled: `2026-06-05T15:35:00-04:00`; mode: `auto`; type: `image`
  - Reason: `not_approved`
  - Copy: The first Lily Roo single is live, and the cover art has been remastered into its proper tiny-room glow.
  - Link/reply: Listen on Spotify: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi | Apple Music: https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249 | YouTube Music: https://music.youtube.com/watch?v=vK0mDIW65o4
  - Asset: https://www.lilyroo.com/assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg
  - Review checks:
    - `pass` copy_present: 104 characters of primary copy.
    - `pass` destination_links_present: 3 link(s): https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi, https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249, https://music.youtube.com/watch?v=vK0mDIW65o4
    - `pass` asset_file_present: https://www.lilyroo.com/assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg maps to assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg.
    - `pass` executor_blocker_confirmed: Current executor state is blocked / not_approved.
    - `pass` platform_readiness: Executor readiness snapshot marks platform ready.
  - Destination link evidence:
    - `verified_local_evidence` https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi: HyperFollow spotify link (data/hyperfollow_store_links_snapshot.json); spotify alignment check: ok (data/first_single_alignment_audit.json)
    - `verified_local_evidence` https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249: HyperFollow applemusic link (data/hyperfollow_store_links_snapshot.json); HyperFollow itunes link (data/hyperfollow_store_links_snapshot.json); apple_music alignment check: ok (data/first_single_alignment_audit.json); Apple Music release snapshot: I Learned It All in Fifteen Seconds - Single (data/apple_music_release_snapshot.json)
    - `verified_local_evidence` https://music.youtube.com/watch?v=vK0mDIW65o4: youtube_music alignment check: ok (data/first_single_alignment_audit.json); YouTube Music release snapshot: I Learned It All in Fifteen Seconds - Lily Roo (data/youtube_music_release_snapshot.json)
  - Approval review status: `checked_batch_ready`
  - Checked batch member: `True`
  - Batch reason: All automated review checks passed.
  - Approval effect: `approved 'yes' -> 'yes'`
  - Preview approval: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-258 --dry-run`
  - Approve after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-258 --refresh-admin`
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
  - Batch reason: Held outside checked batch until failed/review checks clear.
  - Approval effect: `approved 'no' -> 'yes'`
  - Preview approval: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-259 --dry-run`
  - Approve after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-259 --refresh-admin`
- **YouTube Community - I Learned It All in Fifteen Seconds** (`FP-AUTO-261`)
  - Scheduled: `2026-06-06T19:10:00-04:00`; mode: `manual`; type: `community`
  - Reason: `not_approved`
  - Copy: New transmission: I Learned It All in Fifteen Seconds is live. Remastered cover art, same suspicious amount of feeling.
  - Link/reply: Stream: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi | Apple Music: https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249 | YouTube: https://www.youtube.com/@lilyroo.artist | YouTube Music: https://music.youtube.com/watch?v=vK0mDIW65o4
  - Asset: https://www.lilyroo.com/assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg
  - Review checks:
    - `pass` copy_present: 119 characters of primary copy.
    - `pass` destination_links_present: 4 link(s): https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi, https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249, https://www.youtube.com/@lilyroo.artist, https://music.youtube.com/watch?v=vK0mDIW65o4
    - `pass` asset_file_present: https://www.lilyroo.com/assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg maps to assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg.
    - `pass` executor_blocker_confirmed: Current executor state is blocked / not_approved.
    - `pass` platform_readiness: Executor readiness snapshot marks platform ready.
  - Destination link evidence:
    - `verified_local_evidence` https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi: HyperFollow spotify link (data/hyperfollow_store_links_snapshot.json); spotify alignment check: ok (data/first_single_alignment_audit.json)
    - `verified_local_evidence` https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249: HyperFollow applemusic link (data/hyperfollow_store_links_snapshot.json); HyperFollow itunes link (data/hyperfollow_store_links_snapshot.json); apple_music alignment check: ok (data/first_single_alignment_audit.json); Apple Music release snapshot: I Learned It All in Fifteen Seconds - Single (data/apple_music_release_snapshot.json)
    - `verified_local_evidence` https://www.youtube.com/@lilyroo.artist: YouTube artist channel snapshot: Lily Roo (data/youtube_title_track_snapshot.json)
    - `verified_local_evidence` https://music.youtube.com/watch?v=vK0mDIW65o4: youtube_music alignment check: ok (data/first_single_alignment_audit.json); YouTube Music release snapshot: I Learned It All in Fifteen Seconds - Lily Roo (data/youtube_music_release_snapshot.json)
  - Approval review status: `checked_batch_ready`
  - Checked batch member: `True`
  - Batch reason: All automated review checks passed.
  - Approval effect: `approved 'yes' -> 'yes'`
  - Preview approval: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-261 --dry-run`
  - Approve after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-261 --refresh-admin`

## Guardrails
- This packet does not approve, publish, or post anything.
- Use preview commands before approval apply commands.
- Manual rows still require human posting and public URL logging after approval.
