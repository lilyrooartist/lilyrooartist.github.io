# Promotion Blocker Ledger - Lily Roo

Generated: 2026-07-02T01:10:12.434805Z

## Summary
- Open blockers: **8**
- User-owned: **4**
- External platform-owned: **3**
- Codex-actionable: **1**
- High or critical: **6**

## Unlock Roadmap
- **Approve checked scheduled rows** (`blocked`)
  - Owner: `tod`; projected blockers resolved: **0**
  - Unlocks: Instagram executor row can become publish-eligible after approval.
- **Repair TikTok executor** (`blocked`)
  - Owner: `tod`; projected blockers resolved: **2**
  - Unlocks: Held TikTok approval rows can pass platform-readiness review.; Approved TikTok backlog can become safe to reschedule into upload-draft creation.
  - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
- **Reschedule approved past-due backlog** (`clear`)
  - Owner: `tod`; projected blockers resolved: **11**
  - Unlocks: Approved past-due queue rows get a fresh schedule after executor blockers clear.
  - Preview/check: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-02T10:00:00-04:00' --spacing-hours 24`
  - Apply after review: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-02T10:00:00-04:00' --spacing-hours 24 --apply --refresh-admin`
- **Fill manual metric worksheet** (`needs_values`)
  - Owner: `tod`; projected blockers resolved: **6**
  - Unlocks: Admin health and weekly reporting can use fresh cross-platform metrics.; Manual metric blockers clear once worksheet values are imported.
  - Blocked by: P2 Recent discovery and traffic:4, P3 Release depth metrics:2
  - Preview/check: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Apply after review: `python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`

## Ledger
- **[high] Reschedule approved past-due backlog** (`backlog-reschedule`)
  - Owner: `codex`; status: `ready_to_preview`; category: `backlog_reschedule`
  - Evidence: 11 approved backlog row(s); 0 still have executor blockers.
  - Next step: Preview the new schedule, then apply the safe reschedule command.
  - Preview/check: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-02T10:00:00-04:00' --spacing-hours 24`
  - Apply/log after review: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-02T10:00:00-04:00' --spacing-hours 24 --apply --refresh-admin`
  - Guardrail: The apply command remains dry-run-first through the preview artifact.
- **[high] Repair TikTok executor** (`platform-FP-AUTO-279`)
  - Owner: `tod`; status: `blocked`; category: `platform_repair`
  - Evidence: analog_myth_launch_day
  - Next step: TikTok direct public posting approval is false, but upload-draft mode can proceed after credentials. Complete TikTok OAuth setup, push upload-mode secrets, then refresh Admin.
  - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - Guardrail: Run retry resets only after the external platform repair is verified.
  - Blocked apply command: `python3 scripts/push_social_worker_secrets.py TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN && python3 scripts/refresh_promo_admin.py`
  - Impact: apply blocked by: public_posting_approval_not_confirmed_for_direct_posting
- **[high] Repair TikTok executor** (`platform-FP-AUTO-284`)
  - Owner: `tod`; status: `blocked`; category: `platform_repair`
  - Evidence: analog_myth_launch_day
  - Next step: TikTok direct public posting approval is false, but upload-draft mode can proceed after credentials. Complete TikTok OAuth setup, push upload-mode secrets, then refresh Admin.
  - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - Guardrail: Run retry resets only after the external platform repair is verified.
  - Blocked apply command: `python3 scripts/push_social_worker_secrets.py TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN && python3 scripts/refresh_promo_admin.py`
  - Impact: apply blocked by: public_posting_approval_not_confirmed_for_direct_posting
- **[high] Repair Instagram executor** (`platform-FP-AUTO-272`)
  - Owner: `external_platform`; status: `blocked`; category: `platform_repair`
  - Evidence: analog_myth_launch_day Local secret source is missing: IG_BUSINESS_ACCOUNT_ID.
  - Next step: Worker cannot resolve instagram_business_account from FB_PAGE_ID. Local secret source is missing: IG_BUSINESS_ACCOUNT_ID. Set IG_BUSINESS_ACCOUNT_ID from Meta Business/Instagram Graph, push it to the Worker, then recapture readiness.
  - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run IG_BUSINESS_ACCOUNT_ID`
  - Guardrail: Run retry resets only after the external platform repair is verified.
  - Blocked apply command: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
  - Impact: apply blocked by: local_secret_source_missing:IG_BUSINESS_ACCOUNT_ID
- **[high] Repair Instagram executor** (`platform-FP-AUTO-277`)
  - Owner: `external_platform`; status: `blocked`; category: `platform_repair`
  - Evidence: analog_myth_launch_day Local secret source is missing: IG_BUSINESS_ACCOUNT_ID.
  - Next step: Worker cannot resolve instagram_business_account from FB_PAGE_ID. Local secret source is missing: IG_BUSINESS_ACCOUNT_ID. Set IG_BUSINESS_ACCOUNT_ID from Meta Business/Instagram Graph, push it to the Worker, then recapture readiness.
  - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run IG_BUSINESS_ACCOUNT_ID`
  - Guardrail: Run retry resets only after the external platform repair is verified.
  - Blocked apply command: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
  - Impact: apply blocked by: local_secret_source_missing:IG_BUSINESS_ACCOUNT_ID
- **[high] Repair Instagram executor** (`platform-FP-AUTO-282`)
  - Owner: `external_platform`; status: `blocked`; category: `platform_repair`
  - Evidence: analog_myth_launch_day Local secret source is missing: IG_BUSINESS_ACCOUNT_ID.
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
