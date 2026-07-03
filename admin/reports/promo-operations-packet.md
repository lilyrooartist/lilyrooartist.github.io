# Promo Operations Packet - Lily Roo

Generated: 2026-07-03T06:24:08.711665Z

## Summary
- Actions: **20**
- User review: **7**
- Platform fixes: **4**
- Scheduled approval batches: **0**
- Manual distribution actions: **0**
- Experiment result actions: **1**
- Store checks: **6**
- Manual metric updates: **2**
- Safe apply commands ready: **0**
- Urgency: **blocked: 7, high: 5, low: 2, medium: 6**

## Phase Counts
- Collect experiment results: **1**
- Fill manual metrics: **2**
- Repair executor: **4**
- Review blocked drafts: **7**
- Verify music sites: **6**

## Top Actions

### Review blocked drafts
- **[blocked] Review scheduled TikTok approval FP-AUTO-259**
  - Why: Executor setup is not ready for this draft.
  - Detail: not_approved
  - Command: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-259 --dry-run`
  - Approve after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-259 --refresh-admin`
- **[blocked] Review scheduled Instagram approval FP-AUTO-267**
  - Why: Executor setup is not ready for this draft.
  - Detail: not_approved
  - Command: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-267 --dry-run`
  - Approve after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-267 --refresh-admin`
- **[blocked] Review scheduled Instagram approval FP-AUTO-272**
  - Why: Executor setup is not ready for this draft.
  - Detail: not_approved
  - Command: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-272 --dry-run`
  - Approve after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-272 --refresh-admin`
- **[blocked] Review scheduled Instagram approval FP-AUTO-277**
  - Why: Executor setup is not ready for this draft.
  - Detail: not_approved
  - Command: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-277 --dry-run`
  - Approve after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-277 --refresh-admin`
- **[blocked] Review scheduled TikTok approval FP-AUTO-279**
  - Why: Executor setup is not ready for this draft.
  - Detail: not_approved
  - Command: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-279 --dry-run`
  - Approve after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-279 --refresh-admin`
- **[blocked] Review scheduled Instagram approval FP-AUTO-282**
  - Why: Executor setup is not ready for this draft.
  - Detail: not_approved
  - Command: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-282 --dry-run`
  - Approve after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-282 --refresh-admin`
- **[blocked] Review scheduled TikTok approval FP-AUTO-284**
  - Why: Executor setup is not ready for this draft.
  - Detail: not_approved
  - Command: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-284 --dry-run`
  - Approve after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-284 --refresh-admin`

### Repair executor
- **[high] Fix Instagram executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Instagram retry cap reached; verify instagram_business_account repair before resetting execution state.
  - Missing locally: `IG_BUSINESS_ACCOUNT_ID`
  - Local source: `secrets/social_api.env`
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`
  - Apply repair after preview: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-PLAN-TWELVE-DOLLARS-INSTAGRAM --apply`
- **[high] Fix Instagram executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Instagram retry cap reached; verify instagram_business_account repair before resetting execution state.
  - Missing locally: `IG_BUSINESS_ACCOUNT_ID`
  - Local source: `secrets/social_api.env`
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-263`
  - Apply repair after preview: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-263`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-263 --apply`
- **[high] Fix Instagram executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Instagram retry cap reached; verify instagram_business_account repair before resetting execution state.
  - Missing locally: `IG_BUSINESS_ACCOUNT_ID`
  - Local source: `secrets/social_api.env`
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-258`
  - Apply repair after preview: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-258`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-258 --apply`
- **[high] Fix TikTok upload-mode credentials**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Local upload-mode OAuth credentials missing: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. Complete TikTok OAuth setup locally, then push upload-mode secrets and refresh Admin.
  - Missing secrets: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
  - Missing locally: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
  - Local source: `secrets/social_api.env`
  - Public posting approved: `False`
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - Apply repair after preview: `python3 scripts/push_social_worker_secrets.py TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN && python3 scripts/refresh_promo_admin.py`

### Collect experiment results
- **[high] Collect experiment result metrics**
  - Why: 15 logged experiment post(s) have 90 result field(s) waiting; these results rank repeatable formats.
  - Detail: Fill measured result values with evidence notes, preview the import, then apply only after review.
  - Command: `python3 scripts/update_experiment_results.py --from-wide-csv data/experiment_result_entry_wide_template.csv --dry-run`
  - Packet: `admin/reports/experiment-result-clipboard.md`
  - Metric cards: **15**; pending fields: **90**
  - Measurement priorities: **12**
  - Wide entry CSV: `data/experiment_result_entry_wide_template.csv`
  - Preview result import: `python3 scripts/update_experiment_results.py --from-wide-csv data/experiment_result_entry_wide_template.csv --dry-run`

## Guardrails
- This packet does not publish, approve, apply, or post anything.
- Review copy before running approval commands.
- Apply commands only move already-approved rows into the local/live queue; they do not directly post externally.
