# Human Handoff Packet - Lily Roo

Generated: 2026-06-22T10:02:54.923602Z

## Summary
- Open handoff tasks: **9**
- Tod-owned tasks: **9**
- External/platform-gated tasks: **0**
- High urgency tasks: **4**
- Low urgency tasks: **2**

## Action Docket
- Ready steps: **2**
- Blocked steps: **1**
- Manual posts packaged: **3**
- Manual metric fields: **6**
- Resolution worksheet: `data/human_handoff_resolution_worksheet.csv` (9 row(s))

- **Review checked approval batch** (`not_available`)
  - Owner: `tod`; tasks: **0**; blockers resolved: **0**
  - Review runbook: **0** step(s), **0** checklist row(s)
  - Sequence verify: `python3 scripts/refresh_promo_admin.py`
  - Completion evidence: data/scheduled_approval_packet.json should show fewer approval blockers, and data/social_scheduler_dry_run.json should no longer block the approved Instagram row on not_approved.
  - Next after apply: Run the safe admin refresh, then manually post/log any newly approved YouTube Community row before treating the published log as current.
  - Guardrail: Human review is still required; blocked review IDs stay excluded from the checked batch.
- **Review and post manual distribution rows** (`ready_for_manual_post`)
  - Owner: `tod`; tasks: **3**; blockers resolved: **3**
  - Blocked IDs: `FP-PLAN-TWELVE-DOLLARS-TIKTOK`
  - Sequence verify: `python3 scripts/refresh_promo_admin.py`
  - Completion evidence: data/manual_distribution_packet.json should move approved rows from review_queue toward postable manual distribution, and data/published_log_reconciliation.json should remain gated until public URLs are logged.
  - Next after apply: Post each approved YouTube Community row manually, then log its public URL with scripts/log_manual_distribution.py.
  - Guardrail: Manual-only approvals do not auto-post; posting and public URL logging remain separate after review. Post manually first, then log only real public URLs.
- **Repair blocked platform executor setup** (`blocked`)
  - Owner: `tod`; tasks: **4**; blockers resolved: **1**
  - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-263`
  - Sequence preview: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-263`
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
- **Reschedule approved backlog after blockers clear** (`clear`)
  - Owner: `tod`; tasks: **0**; blockers resolved: **0**
  - Sequence verify: `python3 scripts/refresh_promo_admin.py`
  - Completion evidence: data/backlog_reschedule_preview.json should show normal_apply_gate clear before any non-override apply command is exposed.
  - Next after apply: Refresh admin and confirm approved past-due posts have future scheduled_at values before relying on the scheduler.
  - Guardrail: Do not apply blocked backlog reschedules without clearing platform readiness.

## Tasks
- **Repair Instagram executor** (`platform-setup-FP-AUTO-263`)
  - Phase: `Platform setup`; owner: `tod`; status: `failed`; urgency: `high`
  - Detail: Worker cannot resolve instagram_business_account from FB_PAGE_ID. Local secret source is missing: IG_BUSINESS_ACCOUNT_ID. Set IG_BUSINESS_ACCOUNT_ID from Meta Business/Instagram Graph, push it to the Worker, then recapture readiness.
  - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-263`
  - Guardrail: Push worker secrets only after local platform setup is complete.
- **Repair TikTok executor** (`platform-setup-FP-AUTO-264`)
  - Phase: `Platform setup`; owner: `tod`; status: `blocked`; urgency: `high`
  - Detail: Missing worker secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. TikTok direct public posting approval is false, but upload-draft mode can proceed after credentials. Local secret source is also missing: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. Complete TikTok OAuth setup locally, then push upload-mode secrets and refresh Admin.
  - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - Guardrail: Run the TikTok preflight before pushing secrets; push upload-mode secrets only after local OAuth setup is complete. Keep direct public posting blocked until approval is confirmed.
- **Repair Facebook executor** (`platform-setup-FP-AUTO-265`)
  - Phase: `Platform setup`; owner: `tod`; status: `failed`; urgency: `high`
  - Detail: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
  - Preview/check: `python3 scripts/check_facebook_publishing.py --post-id 'FP-AUTO-265' --check-worker-dry-run`
  - Guardrail: Push worker secrets only after local platform setup is complete.
- **Repair Instagram executor** (`platform-setup-FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`)
  - Phase: `Platform setup`; owner: `tod`; status: `failed`; urgency: `high`
  - Detail: Worker cannot resolve instagram_business_account from FB_PAGE_ID. Local secret source is missing: IG_BUSINESS_ACCOUNT_ID. Set IG_BUSINESS_ACCOUNT_ID from Meta Business/Instagram Graph, push it to the Worker, then recapture readiness.
  - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`
  - Guardrail: Push worker secrets only after local platform setup is complete.
- **Post I Learned It All in Fifteen Seconds to YouTube Community** (`manual-distribution-FP-AUTO-261`)
  - Phase: `Manual distribution`; owner: `tod`; status: `ready_for_manual_post`; urgency: `medium`
  - Detail: Post manually in YouTube Studio Community, then log the real public URL before marking distribution complete.
  - Preview/check: `python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url PUBLIC_URL`
  - asset: https://www.lilyroo.com/assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg
  - Guardrail: Do not log a manual post until a real public URL exists.
- **Post Analog Myth to YouTube Community** (`manual-distribution-FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY`)
  - Phase: `Manual distribution`; owner: `tod`; status: `ready_for_manual_post`; urgency: `medium`
  - Detail: Post manually in YouTube Studio Community, then log the real public URL before marking distribution complete.
  - Preview/check: `python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url PUBLIC_URL`
  - asset: https://www.lilyroo.com/assets/albums/analog-myth/art/03-analog-myth.jpg
  - Guardrail: Do not log a manual post until a real public URL exists.
- **Post Twelve Dollars to YouTube Community** (`manual-distribution-FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY`)
  - Phase: `Manual distribution`; owner: `tod`; status: `ready_for_manual_post`; urgency: `medium`
  - Detail: Post manually in YouTube Studio Community, then log the real public URL before marking distribution complete.
  - Preview/check: `python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url PUBLIC_URL`
  - asset: https://www.lilyroo.com/assets/albums/twelve-dollars/art/04-twelve-dollars.jpg
  - Guardrail: Do not log a manual post until a real public URL exists.
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
