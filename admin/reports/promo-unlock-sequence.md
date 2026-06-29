# Promo Unlock Sequence - Lily Roo

Generated: 2026-06-29T21:10:06.027233Z

## Summary
- Steps: **4**
- Ready for human review: **0**
- Blocked or warning: **3**
- Projected resolution units across sequence: **29**
- Current step: `unlock-manual-metrics` (`blocked_until_input`)
- Open blockers still tracked: **9**

## Sequence
1. **Approve checked scheduled rows** - `unlock-checked-scheduled-approval`
   - State: `blocked`; owner: `tod`
   - Reason: Blocked by: FP-AUTO-259.
   - Unlocks: Instagram executor row can become publish-eligible after approval.
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
