# Human Handoff Packet - Lily Roo

Generated: 2026-07-07T04:17:40.011595Z

## Summary
- Open handoff tasks: **3**
- Tod-owned tasks: **3**
- External/platform-gated tasks: **0**
- High urgency tasks: **1**
- Low urgency tasks: **2**

## Action Docket
- Ready steps: **0**
- Blocked steps: **1**
- Manual posts packaged: **0**
- Manual metric fields: **6**
- Resolution worksheet: `data/human_handoff_resolution_worksheet.csv` (3 row(s))

- **Review checked approval batch** (`not_available`)
  - Owner: `tod`; tasks: **0**; blockers resolved: **0**
  - Review runbook: **0** step(s), **0** checklist row(s)
  - Sequence verify: `python3 scripts/refresh_promo_admin.py`
  - Completion evidence: data/scheduled_approval_packet.json should show fewer approval blockers, and data/social_scheduler_dry_run.json should no longer block the approved Instagram row on not_approved.
  - Next after apply: Run the safe admin refresh, then remove or convert any newly approved manual-only YouTube Community row before treating the published log as current.
  - Guardrail: Human review is still required; blocked review IDs stay excluded from the checked batch.
- **Review and post manual distribution rows** (`clear`)
  - Owner: `tod`; tasks: **0**; blockers resolved: **0**
  - Sequence verify: `python3 scripts/refresh_promo_admin.py`
  - Completion evidence: data/manual_distribution_packet.json should move approved rows from review_queue toward postable manual distribution, and data/published_log_reconciliation.json should remain gated until public URLs are logged.
  - Next after apply: Remove or convert each approved manual-only YouTube Community row; only log URLs for historical rows that already have real public post URLs.
  - Guardrail: Manual-only approvals do not auto-post; posting and public URL logging remain separate after review. Manual posting is not in the active plan; log only real historical public URLs.
- **Repair blocked platform executor setup** (`blocked`)
  - Owner: `tod`; tasks: **1**; blockers resolved: **1**
  - Preview/check: `python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --mode direct --dry-run`
  - Sequence preview: `python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --mode direct --dry-run`
  - Sequence verify: `python3 scripts/refresh_promo_admin.py`
  - Completion evidence: data/tiktok_setup_preflight.json should report direct public posting approval before TikTok backlog work is allowed.
  - Next after apply: Recapture admin state and only then revisit TikTok approval or backlog reschedule rows that can publish automatically.
  - Guardrail: Run preflight and confirm local OAuth setup before pushing secrets; upload-draft/manual-finish TikTok posting remains excluded from the active plan.
- **Optional private metric worksheet** (`optional_values`)
  - Owner: `tod`; tasks: **2**; blockers resolved: **6**
  - Fields: **6**
  - Batches: **2**
  - Priority 2: Recent discovery and traffic - **4** field(s) (access: private_analytics; rows: 2, 3, 6, 7)
  - Priority 3: Release depth metrics - **2** field(s) (access: private_analytics; rows: 4, 5)
  - Preview/check: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Apply after review: `python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`
  - Sequence preview: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Sequence apply_after_review: `python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`
  - Sequence verify: `python3 scripts/refresh_promo_admin.py`
  - Completion evidence: data/manual_metric_collection_packet.json should reduce pending_field_count, and data/metrics_history.json should preserve the imported metrics in the latest snapshot.
  - Next after apply: Rebuild the weekly report and confirm lilyroo.com/admin shows the optional metric count decreased.
  - Guardrail: Optional reporting input only; automated promotion is not blocked. Import only collected numeric values and leave unknown cells blank.
- **Reschedule approved backlog after blockers clear** (`clear`)
  - Owner: `tod`; tasks: **0**; blockers resolved: **0**
  - Sequence verify: `python3 scripts/refresh_promo_admin.py`
  - Completion evidence: data/backlog_reschedule_preview.json should show normal_apply_gate clear before any non-override apply command is exposed.
  - Next after apply: Refresh admin and confirm approved past-due posts have future scheduled_at values before relying on the scheduler.
  - Guardrail: Do not apply blocked backlog reschedules without clearing platform readiness.

## Tasks
- **Review TikTok upload-mode preflight** (`platform-setup-tiktok-preflight`)
  - Phase: `Platform setup`; owner: `tod`; status: `blocked`; urgency: `high`
  - Detail: Review the TikTok upload-mode/direct-public split before treating TikTok as ready.
  - Preview/check: `python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --mode direct --dry-run`
  - Guardrail: Keep TikTok upload-draft/manual-finish posting out of the active plan; only direct public API publishing can become an automated TikTok lane.
- **Fill priority 2 metrics: Recent discovery and traffic** (`manual-metrics-priority-2`)
  - Phase: `Manual metrics`; owner: `tod`; status: `needs_values`; urgency: `low`
  - Detail: Collect 4 field(s) across facebook, instagram, tiktok, x, fill the worksheet rows, preview import, then refresh Admin.
  - Preview/check: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Apply after review: `python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`
  - Guardrail: Only import nonnegative numeric values copied from the named source; leave unknown values blank instead of guessing.
- **Fill priority 3 metrics: Release depth metrics** (`manual-metrics-priority-3`)
  - Phase: `Manual metrics`; owner: `tod`; status: `needs_values`; urgency: `low`
  - Detail: Collect 2 field(s) across spotify, fill the worksheet rows, preview import, then refresh Admin.
  - Preview/check: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Apply after review: `python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`
  - Guardrail: Only import nonnegative numeric values copied from the named source; leave unknown values blank instead of guessing.

## Guardrails
- This packet is review-only and does not approve, post, publish, push secrets, or import metrics.
- Preview commands should run before any apply command.
- Manual metrics and public post URLs should come from real platform surfaces, not estimates.
