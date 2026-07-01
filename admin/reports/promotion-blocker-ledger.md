# Promotion Blocker Ledger - Lily Roo

Generated: 2026-07-01T06:31:43.645621Z

## Summary
- Open blockers: **9**
- User-owned: **5**
- External platform-owned: **4**
- Codex-actionable: **0**
- High or critical: **7**

## Unlock Roadmap
- **Approve checked scheduled rows** (`blocked`)
  - Owner: `tod`; projected blockers resolved: **0**
  - Unlocks: Instagram executor row can become publish-eligible after approval.
  - Blocked by: FP-AUTO-259
- **Repair TikTok executor** (`blocked`)
  - Owner: `tod`; projected blockers resolved: **2**
  - Unlocks: Held TikTok approval rows can pass platform-readiness review.; Approved TikTok backlog can become safe to reschedule into upload-draft creation.
  - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
- **Reschedule approved past-due backlog** (`blocked_until_clearance_steps_complete`)
  - Owner: `external_platform`; projected blockers resolved: **27**
  - Unlocks: Approved past-due queue rows get a fresh schedule after executor blockers clear.
  - Blocked by: FP-AUTO-272, FP-AUTO-277, FP-AUTO-279, FP-AUTO-282, FP-AUTO-284
  - Preview/check: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-02T10:00:00-04:00' --spacing-hours 24`
- **Fill manual metric worksheet** (`needs_values`)
  - Owner: `tod`; projected blockers resolved: **6**
  - Unlocks: Admin health and weekly reporting can use fresh cross-platform metrics.; Manual metric blockers clear once worksheet values are imported.
  - Blocked by: P2 Recent discovery and traffic:4, P3 Release depth metrics:2
  - Preview/check: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Apply after review: `python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`

## Ledger
- **[high] Approve scheduled TikTok row** (`approval-FP-AUTO-259`)
  - Owner: `tod`; status: `blocked_by_review_checks`; category: `approval`
  - Evidence: FP-AUTO-259 is blocked by not_approved in executor state. Failed review checks: platform_readiness: Executor readiness snapshot marks platform blocked.
  - Next step: Resolve failed review checks before approving this scheduled row.
  - Open: https://www.lilyroo.com/assets/ig/01_i_learned_it_all_60s.mp4
  - Preview/check: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-259 --dry-run`
  - Apply/log after review: `python3 scripts/update_scheduled_post_approval.py FP-AUTO-259 --refresh-admin`
  - Guardrail: Approval does not guarantee posting if the platform executor is still blocked.
  - Impact: resolves blocker: False
- **[high] Repair TikTok executor** (`platform-FP-AUTO-279`)
  - Owner: `tod`; status: `blocked`; category: `platform_repair`
  - Evidence: tiktok_public_posting_not_approved
  - Next step: TikTok direct public posting approval is false, but upload-draft mode can proceed after credentials. Complete TikTok OAuth setup, push upload-mode secrets, then refresh Admin.
  - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - Guardrail: Run retry resets only after the external platform repair is verified.
  - Blocked apply command: `python3 scripts/push_social_worker_secrets.py TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN && python3 scripts/refresh_promo_admin.py`
  - Impact: apply blocked by: public_posting_approval_not_confirmed_for_direct_posting
- **[high] Repair TikTok executor** (`platform-FP-AUTO-284`)
  - Owner: `tod`; status: `blocked`; category: `platform_repair`
  - Evidence: tiktok_public_posting_not_approved
  - Next step: TikTok direct public posting approval is false, but upload-draft mode can proceed after credentials. Complete TikTok OAuth setup, push upload-mode secrets, then refresh Admin.
  - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - Guardrail: Run retry resets only after the external platform repair is verified.
  - Blocked apply command: `python3 scripts/push_social_worker_secrets.py TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN && python3 scripts/refresh_promo_admin.py`
  - Impact: apply blocked by: public_posting_approval_not_confirmed_for_direct_posting
- **[high] Reschedule approved past-due backlog** (`backlog-reschedule`)
  - Owner: `external_platform`; status: `blocked`; category: `backlog_reschedule`
  - Evidence: 27 approved backlog row(s); 5 still have executor blockers.
  - Next step: Preview a new schedule. Safe apply becomes available after known executor blockers clear.
  - Preview/check: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-02T10:00:00-04:00' --spacing-hours 24`
  - Guardrail: Normal apply is hidden while rows have known executor blockers.
  - Blocked apply command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-02T10:00:00-04:00' --spacing-hours 24 --apply --refresh-admin`
- **[high] Repair Instagram executor** (`platform-FP-AUTO-272`)
  - Owner: `external_platform`; status: `blocked`; category: `platform_repair`
  - Evidence: instagram_business_account_unresolved Local secret source is missing: IG_BUSINESS_ACCOUNT_ID.
  - Next step: Worker cannot resolve instagram_business_account from FB_PAGE_ID. Local secret source is missing: IG_BUSINESS_ACCOUNT_ID. Set IG_BUSINESS_ACCOUNT_ID from Meta Business/Instagram Graph, push it to the Worker, then recapture readiness.
  - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run IG_BUSINESS_ACCOUNT_ID`
  - Guardrail: Run retry resets only after the external platform repair is verified.
  - Blocked apply command: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
  - Impact: apply blocked by: local_secret_source_missing:IG_BUSINESS_ACCOUNT_ID
- **[high] Repair Instagram executor** (`platform-FP-AUTO-277`)
  - Owner: `external_platform`; status: `blocked`; category: `platform_repair`
  - Evidence: instagram_business_account_unresolved Local secret source is missing: IG_BUSINESS_ACCOUNT_ID.
  - Next step: Worker cannot resolve instagram_business_account from FB_PAGE_ID. Local secret source is missing: IG_BUSINESS_ACCOUNT_ID. Set IG_BUSINESS_ACCOUNT_ID from Meta Business/Instagram Graph, push it to the Worker, then recapture readiness.
  - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run IG_BUSINESS_ACCOUNT_ID`
  - Guardrail: Run retry resets only after the external platform repair is verified.
  - Blocked apply command: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
  - Impact: apply blocked by: local_secret_source_missing:IG_BUSINESS_ACCOUNT_ID
- **[high] Repair Instagram executor** (`platform-FP-AUTO-282`)
  - Owner: `external_platform`; status: `blocked`; category: `platform_repair`
  - Evidence: instagram_business_account_unresolved Local secret source is missing: IG_BUSINESS_ACCOUNT_ID.
  - Next step: Worker cannot resolve instagram_business_account from FB_PAGE_ID. Local secret source is missing: IG_BUSINESS_ACCOUNT_ID. Set IG_BUSINESS_ACCOUNT_ID from Meta Business/Instagram Graph, push it to the Worker, then recapture readiness.
  - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run IG_BUSINESS_ACCOUNT_ID`
  - Guardrail: Run retry resets only after the external platform repair is verified.
  - Blocked apply command: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
  - Impact: apply blocked by: local_secret_source_missing:IG_BUSINESS_ACCOUNT_ID
- **[low] Fill priority 2 metrics: Recent discovery and traffic** (`metrics-priority-2`)
  - Owner: `tod`; status: `needs_values`; category: `manual_metrics`
  - Evidence: 4 pending field(s): facebook.reach_7d, instagram.profile_visits_7d, tiktok.profile_views_7d, x.impressions_7d.
  - Next step: Collect this priority batch, fill the CSV worksheet rows, preview import, then refresh admin.
  - Preview/check: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Apply/log after review: `python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`
  - Guardrail: Do not guess analytics values; import only values copied from the platform source.
  - Impact: priority 2; fields: 4; access: private_analytics; csv rows: 2, 3, 6, 7
- **[low] Fill priority 3 metrics: Release depth metrics** (`metrics-priority-3`)
  - Owner: `tod`; status: `needs_values`; category: `manual_metrics`
  - Evidence: 2 pending field(s): spotify.release_streams, spotify.saves.
  - Next step: Collect this priority batch, fill the CSV worksheet rows, preview import, then refresh admin.
  - Preview/check: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Apply/log after review: `python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`
  - Guardrail: Do not guess analytics values; import only values copied from the platform source.
  - Impact: priority 3; fields: 2; access: private_analytics; csv rows: 4, 5

## Guardrails
- This ledger does not approve posts, post externally, push secrets, or invent metric values.
- Treat external platform repairs and manual values as blockers until fresh admin evidence proves they cleared.
