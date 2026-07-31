# Promo Unlock Sequence - Lily Roo

Generated: 2026-07-31T09:17:40.999557Z

## Summary
- Steps: **5**
- Ready for human review: **0**
- Blocked or warning: **1**
- Projected resolution units across sequence: **13**
- Current step: `unlock-backlog-reschedule` (`preview_ready_with_blocker_warning`)
- Open blockers still tracked: **14**

## Sequence
1. **Approve checked scheduled rows** - `unlock-checked-scheduled-approval`
   - State: `clear`; owner: `tod`
   - Reason: No action is needed for this gate.
   - Unlocks: Instagram executor row can become publish-eligible after approval.
2. **Manual distribution lane clear** - `unlock-manual-distribution`
   - State: `clear`; owner: `tod`
   - Reason: No action is needed for this gate.
   - Unlocks: No manual-only posting lane is active; growth work stays in automated or review-only surfaces.
   - Guardrail: Manual-only approvals do not auto-post; posting and public URL logging remain separate after review.
3. **Prepare TikTok direct-public API lane** - `unlock-tiktok-platform-repair`
   - State: `deferred`; owner: `tod`
   - Reason: Do not queue TikTok upload-draft rows as active promotion; only direct public API publishing can enter the active plan.
   - Unlocks: TikTok can become an automated expansion lane only after direct public posting approval is explicit.; Upload-draft/manual-finish TikTok posting stays out of the active plan.
   - preview (preview-safe): `python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --mode direct --dry-run`
   - Completion evidence: data/tiktok_setup_preflight.json should report direct public posting approval before TikTok backlog work is allowed.
   - Guardrail: Do not queue TikTok upload-draft rows as active promotion; only direct public API publishing can enter the active plan.
4. **Reschedule approved past-due backlog** - `unlock-backlog-reschedule`
   - State: `preview_ready_with_blocker_warning`; owner: `external_platform`
   - Reason: Preview ran, but the output still names a known blocker.
   - Unlocks: Approved past-due queue rows get a fresh schedule after executor blockers clear.
   - preview (preview-safe): `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-08-01T10:00:00+00:00' --spacing-hours 24`
   - Completion evidence: data/backlog_reschedule_preview.json should show normal_apply_gate clear before any non-override apply command is exposed.
   - Guardrail: Normal apply stays hidden until known executor/platform blockers clear.
5. **Optional: fill private metric worksheet** - `unlock-manual-metrics`
   - State: `optional_input`; owner: `tod`
   - Reason: Private analytics are optional measurement inputs, not blockers for automated promotion.
   - Unlocks: Admin health and weekly reporting get sharper private-analytics context.; Automated Analog Myth posting, proof export, and click learning continue without these values.
   - preview (preview-safe): `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
   - Completion evidence: data/manual_metric_collection_packet.json should reduce pending_field_count, and data/metrics_history.json should preserve the imported metrics in the latest snapshot.
   - Guardrail: Private analytics are optional measurement inputs, not blockers for automated promotion.

## Guardrails
- This sequence does not approve, post, publish, push secrets, log URLs, import metrics, or mutate promotion state.
- Apply commands are shown only as after-review instructions; preview commands remain the safe first action.
