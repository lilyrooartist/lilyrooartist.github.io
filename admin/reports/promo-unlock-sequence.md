# Promo Unlock Sequence - Lily Roo

Generated: 2026-06-29T15:09:59.630277Z

## Summary
- Steps: **4**
- Ready for human review: **1**
- Blocked or warning: **2**
- Projected resolution units across sequence: **30**
- Current step: `unlock-checked-scheduled-approval` (`ready_for_human_review`)
- Open blockers still tracked: **9**

## Sequence
1. **Approve checked scheduled rows** - `unlock-checked-scheduled-approval`
   - State: `ready_for_human_review`; owner: `tod`
   - Reason: Preview ran cleanly; this gate is waiting for human review or external completion.
   - Unlocks: Instagram executor row can become publish-eligible after approval.
   - preview (preview-safe): `python3 scripts/update_scheduled_post_approval.py --checked-batch --dry-run`
   - apply_after_review (after-review only): `python3 scripts/update_scheduled_post_approval.py --checked-batch --refresh-admin`
   - Completion evidence: data/scheduled_approval_packet.json should show fewer approval blockers, and data/social_scheduler_dry_run.json should no longer block the approved Instagram row on not_approved.
   - Guardrail: Use --checked-batch so only rows that passed review checks are approved.
2. **Repair TikTok executor** - `unlock-tiktok-platform-repair`
   - State: `ready`; owner: `tod`
   - Reason: ready
   - Unlocks: Held TikTok approval rows can pass platform-readiness review.; Approved TikTok backlog can become safe to reschedule into upload-draft creation.
3. **Reschedule approved past-due backlog** - `unlock-backlog-reschedule`
   - State: `preview_ready_with_blocker_warning`; owner: `external_platform`
   - Reason: Preview ran, but the output still names a known blocker.
   - Unlocks: Approved past-due queue rows get a fresh schedule after executor blockers clear.
   - preview (preview-safe): `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-30T10:00:00-04:00' --spacing-hours 24`
   - Completion evidence: data/backlog_reschedule_preview.json should show normal_apply_gate clear before any non-override apply command is exposed.
   - Guardrail: Normal apply stays hidden until known executor/platform blockers clear.
4. **Fill manual metric worksheet** - `unlock-manual-metrics`
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
