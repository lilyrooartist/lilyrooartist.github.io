# Promo Unlock Sequence - Lily Roo

Generated: 2026-06-21T14:33:48.135314Z

## Summary
- Steps: **5**
- Ready for human review: **1**
- Blocked or warning: **3**
- Projected resolution units across sequence: **14**
- Current step: `unlock-manual-distribution` (`ready_for_human_review`)
- Open blockers still tracked: **9**

## Sequence
1. **Approve checked scheduled rows** - `unlock-checked-scheduled-approval`
   - State: `completed`; owner: `tod`
   - Reason: This gate is already applied; it is kept here as evidence, not as a pending task.
   - Unlocks: Instagram executor row can become publish-eligible after approval.; One scheduled YouTube Community row can move into manual distribution after approval.
   - preview (preview-safe): `python3 scripts/update_scheduled_post_approval.py --checked-batch --dry-run`
   - apply_after_review (after-review only): `python3 scripts/update_scheduled_post_approval.py --checked-batch --refresh-admin`
   - Completion evidence: data/scheduled_approval_packet.json should show fewer approval blockers, and data/social_scheduler_dry_run.json should no longer block the approved Instagram row on not_approved.
   - Guardrail: Use --checked-batch so only rows that passed review checks are approved.
2. **Review and post manual YouTube Community rows** - `unlock-manual-distribution`
   - State: `ready_for_human_review`; owner: `tod`
   - Reason: Preview ran cleanly; this gate is waiting for human review or external completion.
   - Unlocks: Manual YouTube Community promotion can publish without waiting for broken auto executors.; Published_Log.csv can be updated after public URLs exist.
   - preview (preview-safe): `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --dry-run`
   - apply_after_review (after-review only): `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --refresh-admin`
   - Completion evidence: data/manual_distribution_packet.json should move approved rows from review_queue toward postable manual distribution, and data/published_log_reconciliation.json should remain gated until public URLs are logged.
   - Guardrail: Manual-only approvals do not auto-post; posting and public URL logging remain separate after review.
3. **Repair TikTok executor** - `unlock-tiktok-platform-repair`
   - State: `blocked_until_input`; owner: `tod`
   - Reason: local_secret_presence_and_public_posting_approval
   - Unlocks: Held TikTok approval rows can pass platform-readiness review.; Approved TikTok backlog can become safe to reschedule and publish.
   - preview (preview-safe): `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
   - Completion evidence: data/tiktok_setup_preflight.json should report ready_to_push_worker_secrets and ready_to_post_publicly before TikTok backlog work is allowed.
   - Guardrail: Run the TikTok preflight before pushing secrets; push worker secrets only after local OAuth/public posting setup is complete.
4. **Reschedule approved past-due backlog** - `unlock-backlog-reschedule`
   - State: `preview_ready_with_blocker_warning`; owner: `external_platform`
   - Reason: Preview ran, but the output still names a known blocker.
   - Unlocks: Approved past-due queue rows get a fresh schedule after executor blockers clear.
   - preview (preview-safe): `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-22T10:00:00+00:00' --spacing-hours 24`
   - Completion evidence: data/backlog_reschedule_preview.json should show normal_apply_gate clear before any non-override apply command is exposed.
   - Guardrail: Normal apply stays hidden until known executor/platform blockers clear.
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
