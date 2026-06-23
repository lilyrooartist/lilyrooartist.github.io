# Promo Operations Packet - Lily Roo

Generated: 2026-06-23T04:29:19.549011Z

## Summary
- Actions: **23**
- User review: **7**
- Platform fixes: **5**
- Scheduled approval batches: **0**
- Manual distribution actions: **0**
- Experiment result actions: **1**
- Store checks: **7**
- Manual metric updates: **2**
- Safe apply commands ready: **0**
- Urgency: **blocked: 2, high: 6, low: 2, medium: 13**

## Phase Counts
- Collect experiment results: **1**
- Fill manual metrics: **2**
- Repair executor: **5**
- Reschedule approved backlog: **1**
- Review blocked drafts: **1**
- Review draft posts: **6**
- Verify music sites: **7**

## Top Actions

### Reschedule approved backlog
- **[blocked] Preview reschedule for approved past-due posts**
  - Why: All approved past-due posts are behind executor/platform repair gates; fix those before rescheduling.
  - Detail: Preview first. Normal apply is hidden until known executor/platform blockers clear; override requires deliberate review.
  - Command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-24T10:00:00+00:00' --spacing-hours 24`

### Review blocked drafts
- **[blocked] Review TikTok draft for Twelve Dollars**
  - Why: Executor setup is not ready for this draft.
  - Detail: Executor credentials or platform setup are not ready.
  - Missing secrets: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
  - Public posting approved: `False`
  - Command: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-TIKTOK --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-TIKTOK --refresh-admin`

### Repair executor
- **[high] Fix Instagram executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Instagram posting could not resolve instagram_business_account; reconnect or set IG_BUSINESS_ACCOUNT_ID.
  - Missing locally: `IG_BUSINESS_ACCOUNT_ID`
  - Local source: `secrets/social_api.env`
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`
  - Apply repair after preview: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-PLAN-TWELVE-DOLLARS-INSTAGRAM --apply`
- **[high] Fix Instagram executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Instagram posting could not resolve instagram_business_account; reconnect or set IG_BUSINESS_ACCOUNT_ID.
  - Missing locally: `IG_BUSINESS_ACCOUNT_ID`
  - Local source: `secrets/social_api.env`
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-263`
  - Apply repair after preview: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-263`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-263 --apply`
- **[high] Fix TikTok executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Missing worker secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. TikTok direct public posting approval is false, but upload-draft mode can proceed after credentials. Local secret source is also missing: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. Complete TikTok OAuth setup locally, then push upload-mode secrets and refresh Admin.
  - Missing secrets: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
  - Missing locally: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
  - Local source: `secrets/social_api.env`
  - Public posting approved: `False`
  - Command: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - Apply repair after preview: `python3 scripts/push_social_worker_secrets.py TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN && python3 scripts/refresh_promo_admin.py`
- **[high] Fix Facebook executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Facebook blocked Page publishing until identity is confirmed in the Facebook app.
  - Command: `python3 scripts/check_facebook_publishing.py --post-id 'FP-AUTO-265' --check-worker-dry-run`
- **[high] Fix Instagram executor**
  - Why: Platform executor needs repair before queued auto posts can publish.
  - Detail: Instagram posting could not resolve instagram_business_account; reconnect or set IG_BUSINESS_ACCOUNT_ID.
  - Missing locally: `IG_BUSINESS_ACCOUNT_ID`
  - Local source: `secrets/social_api.env`
  - Command: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-258`
  - Apply repair after preview: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
  - Preview retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-258`
  - Apply retry reset after repair: `python3 scripts/reset_social_execution_state.py FP-AUTO-258 --apply`

### Collect experiment results
- **[high] Collect experiment result metrics**
  - Why: 3 logged experiment post(s) have 5 result field(s) waiting; these results rank repeatable formats.
  - Detail: Fill measured result values with evidence notes, preview the import, then apply only after review.
  - Command: `python3 scripts/update_experiment_results.py --from-wide-csv data/experiment_result_entry_wide_template.csv --dry-run`
  - Packet: `admin/reports/experiment-result-clipboard.md`
  - Metric cards: **3**; pending fields: **5**
  - Measurement priorities: **12**
  - Wide entry CSV: `data/experiment_result_entry_wide_template.csv`
  - Preview result import: `python3 scripts/update_experiment_results.py --from-wide-csv data/experiment_result_entry_wide_template.csv --dry-run`

### Review draft posts
- **[medium] Review X draft for Twelve Dollars**
  - Why: Auto draft is ready once reviewed and approved.
  - Detail: Ready after approval.
  - Command: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-TWELVE-DOLLARS-X-ARCHIVE-CTA --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-TWELVE-DOLLARS-X-ARCHIVE-CTA --refresh-admin`
- **[medium] Review Facebook draft for Twelve Dollars**
  - Why: Auto draft is ready once reviewed and approved.
  - Detail: Ready after approval.
  - Command: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-TWELVE-DOLLARS-FACEBOOK-ARCHIVE-CTA --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-TWELVE-DOLLARS-FACEBOOK-ARCHIVE-CTA --refresh-admin`
- **[medium] Review X draft for Analog Myth**
  - Why: Auto draft is ready once reviewed and approved.
  - Detail: Ready after approval.
  - Command: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-ANALOG-MYTH-X-ARCHIVE-CTA --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-ANALOG-MYTH-X-ARCHIVE-CTA --refresh-admin`
- **[medium] Review Facebook draft for Analog Myth**
  - Why: Auto draft is ready once reviewed and approved.
  - Detail: Ready after approval.
  - Command: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-ANALOG-MYTH-FACEBOOK-ARCHIVE-CTA --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-ANALOG-MYTH-FACEBOOK-ARCHIVE-CTA --refresh-admin`

## Guardrails
- This packet does not publish, approve, apply, or post anything.
- Review copy before running approval commands.
- Apply commands only move already-approved rows into the local/live queue; they do not directly post externally.
