# Promo Unlock Sequence - Lily Roo

Generated: 2026-07-03T09:48:16.894623Z

## Summary
- Steps: **5**
- Ready for human review: **1**
- Blocked or warning: **2**
- Projected resolution units across sequence: **6**
- Current step: `unlock-tiktok-platform-repair` (`ready_for_human_review`)
- Open blockers still tracked: **2**

## Sequence
1. **Approve checked scheduled rows** - `unlock-checked-scheduled-approval`
   - State: `blocked`; owner: `tod`
   - Reason: blocked
   - Unlocks: Instagram executor row can become publish-eligible after approval.
2. **Manual distribution lane clear** - `unlock-manual-distribution`
   - State: `clear`; owner: `tod`
   - Reason: No action is needed for this gate.
   - Unlocks: No manual-only posting lane is active; growth work stays in automated or review-only surfaces.
   - Guardrail: Manual-only approvals do not auto-post; posting and public URL logging remain separate after review.
3. **Repair TikTok executor** - `unlock-tiktok-platform-repair`
   - State: `ready_for_human_review`; owner: `tod`
   - Reason: Preview ran cleanly; this gate is waiting for human review or external completion.
   - Unlocks: Held TikTok approval rows can pass platform-readiness review.; Approved TikTok backlog can become safe to reschedule into upload-draft creation.
   - preview (preview-safe): `python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --mode upload --dry-run`
   - Completion evidence: data/tiktok_setup_preflight.json should report ready_to_push_worker_secrets and ready_to_upload_drafts before TikTok upload-mode backlog work is allowed.
   - Guardrail: Keep TikTok upload-draft mode separate from direct public posting; do not require manual-only community posting.
4. **Reschedule approved past-due backlog** - `unlock-backlog-reschedule`
   - State: `clear`; owner: `tod`
   - Reason: No action is needed for this gate.
   - Unlocks: Approved past-due queue rows get a fresh schedule after executor blockers clear.
   - preview (preview-safe): `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-04T10:00:00-04:00' --spacing-hours 24`
   - apply_after_review (after-review only): `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-04T10:00:00-04:00' --spacing-hours 24 --apply --refresh-admin`
5. **Fill manual metric worksheet** - `unlock-manual-metrics`
   - State: `blocked_until_input`; owner: `tod`
   - Reason: private_metric_values
   - Unlocks: Admin health and weekly reporting can use fresh cross-platform metrics.; Manual metric blockers clear once worksheet values are imported.
   - preview (preview-safe): `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
   - apply_after_review (after-review only): `python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`
   - Completion evidence: data/manual_metric_collection_packet.json should reduce pending_field_count, and data/metrics_history.json should preserve the imported metrics in the latest snapshot.
   - Guardrail: Only import nonnegative numeric values copied from the named source; leave unknown values blank instead of guessing.

## Guardrails
- This sequence does not approve, post, publish, push secrets, log URLs, import metrics, or mutate promotion state.
- Apply commands are shown only as after-review instructions; preview commands remain the safe first action.
