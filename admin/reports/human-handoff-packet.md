# Human Handoff Packet - Lily Roo

Generated: 2026-06-29T21:10:05.835871Z

## Summary
- Open handoff tasks: **8**
- Tod-owned tasks: **7**
- External/platform-gated tasks: **1**
- High urgency tasks: **6**
- Low urgency tasks: **2**

## Action Docket
- Ready steps: **1**
- Blocked steps: **2**
- Manual posts packaged: **0**
- Manual metric fields: **6**
- Resolution worksheet: `data/human_handoff_resolution_worksheet.csv` (8 row(s))

- **Review checked approval batch** (`not_available`)
  - Owner: `tod`; tasks: **0**; blockers resolved: **0**
  - Review runbook: **0** step(s), **0** checklist row(s)
  - Sequence verify: `python3 scripts/refresh_promo_admin.py`
  - Completion evidence: data/scheduled_approval_packet.json should show fewer approval blockers, and data/social_scheduler_dry_run.json should no longer block the approved Instagram row on not_approved.
  - Next after apply: Run the safe admin refresh, then manually post/log any newly approved YouTube Community row before treating the published log as current.
  - Guardrail: Human review is still required; blocked review IDs stay excluded from the checked batch.
- **Review and post manual distribution rows** (`clear`)
  - Owner: `tod`; tasks: **0**; blockers resolved: **0**
  - Sequence verify: `python3 scripts/refresh_promo_admin.py`
  - Completion evidence: data/manual_distribution_packet.json should move approved rows from review_queue toward postable manual distribution, and data/published_log_reconciliation.json should remain gated until public URLs are logged.
  - Next after apply: Post each approved YouTube Community row manually, then log its public URL with scripts/log_manual_distribution.py.
  - Guardrail: Manual-only approvals do not auto-post; posting and public URL logging remain separate after review. Post manually first, then log only real public URLs.
- **Repair blocked platform executor setup** (`blocked`)
  - Owner: `tod`; tasks: **5**; blockers resolved: **1**
  - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-265`
  - Sequence preview: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-265`
  - Sequence verify: `python3 scripts/refresh_promo_admin.py`
  - Completion evidence: data/tiktok_setup_preflight.json should report ready_to_push_worker_secrets and ready_to_upload_drafts before TikTok upload-mode backlog work is allowed.
  - Next after apply: Recapture admin state and only then revisit TikTok approval or backlog reschedule rows.
  - Guardrail: Run preflight and confirm local OAuth setup before pushing upload-mode secrets; direct public posting remains separately approval-gated.
- **Fill and import manual metric worksheet** (`needs_values`)
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
  - Next after apply: Rebuild the weekly report and confirm lilyroo.com/admin shows fewer pending manual metric fields.
  - Guardrail: Import only collected numeric values; leave unknown cells blank.
- **Reschedule approved backlog after blockers clear** (`blocked`)
  - Owner: `external_platform`; tasks: **1**; blockers resolved: **23**
  - Preview/check: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-30T10:00:00-04:00' --spacing-hours 24`
  - Sequence preview: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-30T10:00:00-04:00' --spacing-hours 24`
  - Sequence verify: `python3 scripts/refresh_promo_admin.py`
  - Completion evidence: data/backlog_reschedule_preview.json should show normal_apply_gate clear before any non-override apply command is exposed.
  - Next after apply: Refresh admin and confirm approved past-due posts have future scheduled_at values before relying on the scheduler.
  - Guardrail: Normal apply stays hidden until known executor/platform blockers clear.

## Tasks
- **Repair Facebook executor** (`platform-setup-FP-AUTO-265`)
  - Phase: `Platform setup`; owner: `tod`; status: `failed`; urgency: `high`
  - Detail: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
  - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-265`
  - Guardrail: Push worker secrets only after local platform setup is complete.
- **Repair Facebook executor** (`platform-setup-FP-AUTO-268`)
  - Phase: `Platform setup`; owner: `tod`; status: `failed`; urgency: `high`
  - Detail: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
  - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-268`
  - Guardrail: Push worker secrets only after local platform setup is complete.
- **Repair Instagram executor** (`platform-setup-FP-AUTO-272`)
  - Phase: `Platform setup`; owner: `tod`; status: `blocked`; urgency: `high`
  - Detail: Worker cannot resolve instagram_business_account from FB_PAGE_ID. Local secret source is missing: IG_BUSINESS_ACCOUNT_ID. Set IG_BUSINESS_ACCOUNT_ID from Meta Business/Instagram Graph, push it to the Worker, then recapture readiness.
  - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run IG_BUSINESS_ACCOUNT_ID`
  - Guardrail: Push worker secrets only after local platform setup is complete.
- **Repair Facebook executor** (`platform-setup-FP-AUTO-273`)
  - Phase: `Platform setup`; owner: `tod`; status: `failed`; urgency: `high`
  - Detail: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
  - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-273`
  - Guardrail: Push worker secrets only after local platform setup is complete.
- **Repair Facebook executor** (`platform-setup-FP-STORY-ANALOG-MYTH-FACEBOOK-ARCHIVE-CTA`)
  - Phase: `Platform setup`; owner: `tod`; status: `failed`; urgency: `high`
  - Detail: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
  - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-STORY-ANALOG-MYTH-FACEBOOK-ARCHIVE-CTA`
  - Guardrail: Push worker secrets only after local platform setup is complete.
- **Preview approved backlog reschedule** (`backlog-reschedule`)
  - Phase: `Backlog recovery`; owner: `external_platform`; status: `blocked`; urgency: `high`
  - Detail: Known executor/platform blockers must clear before normal apply.
  - Preview/check: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-30T10:00:00-04:00' --spacing-hours 24`
  - Guardrail: Normal apply stays hidden until known executor/platform blockers clear.
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
