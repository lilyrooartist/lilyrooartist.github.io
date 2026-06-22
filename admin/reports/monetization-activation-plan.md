# Monetization Activation Plan - Lily Roo

Generated: 2026-06-22T06:02:36.358106Z

## Summary
- Current subscribers: **6 / 1000**
- Runway status: **behind_365_day_pace**
- Ready subscriber CTA approvals: **2**
- Subscriber CTA swaps available: **0**
- Platform fixes: **4**
- Activation actions: **8**

## Activation Sequence
1. **Approve manual YouTube Community subscriber rows**
   - Phase: `Approve manual subscriber rows`; status: `ready_for_manual_review`
   - Detail: Review and approve 2 manual subscriber-growth YouTube Community row(s) for Analog Myth, Twelve Dollars. Approval only moves them into the manual distribution docket; it does not publish externally. Blocked rows stay excluded: FP-PLAN-TWELVE-DOLLARS-TIKTOK.
   - Ready IDs: `FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY, FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY`
   - Blocked IDs: `FP-PLAN-TWELVE-DOLLARS-TIKTOK`
   - Guardrail: Manual-only approvals do not auto-post; posting and public URL logging remain separate after review.
   - Preview/check: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --dry-run`
   - After review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --refresh-admin`
2. **Apply approved plan rows after review**
   - Phase: `Move approved subscriber posts into queue`; status: `blocked_until_approved`
   - Detail: After copy review and approval, apply only approved rows to the live queue; this does not directly post externally.
   - After review: `python3 scripts/apply_promo_queue_plan.py --apply --refresh-admin`
3. **Preview approved backlog reschedule**
   - Phase: `Recover stalled approved backlog`; status: `preview_first`
   - Detail: Preview a new schedule for approved past-due posts. Normal apply is hidden until known executor/platform blockers clear.
   - Blocked apply command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-23T10:00:00+08:00' --spacing-hours 24 --apply --refresh-admin`
   - Deliberate override command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-23T10:00:00+08:00' --spacing-hours 24 --allow-blocked --apply --refresh-admin`
   - Preview/check: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-23T10:00:00+08:00' --spacing-hours 24`
4. **Repair Instagram executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Reconnect the Instagram Business/Creator account to the Facebook Page or set IG_BUSINESS_ACCOUNT_ID, then push the worker secret and recapture readiness.
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-263`
   - After review: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
5. **Repair Instagram executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Reconnect the Instagram Business/Creator account to the Facebook Page or set IG_BUSINESS_ACCOUNT_ID, then push the worker secret and recapture readiness.
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`
   - After review: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
6. **Repair Facebook executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
   - Preview/check: `python3 scripts/check_facebook_publishing.py --post-id 'FP-AUTO-265' --check-worker-dry-run`
7. **Repair TikTok executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Missing worker secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. TikTok public posting approval is false. Local secret source is also missing: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. Complete TikTok OAuth/public posting setup locally, then push secrets and refresh Admin.
   - Missing secrets: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
   - Missing locally: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
   - Local source: `secrets/social_api.env`
   - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
8. **Current operations next action: Preview clear approved backlog row**
   - Phase: `Operations packet`; status: `waiting_for_user`
   - Detail: Approved posts are past due; preview a new schedule before any apply step.
   - Preview/check: `python3 scripts/reschedule_scheduled_posts.py --id FP-AUTO-258 --start-at '2026-06-23T10:00:00+08:00' --spacing-hours 24`

## Guardrails
- This plan does not approve, apply, publish, or post anything.
- Approval and apply commands are shown as deliberate after-review steps.
- Run preview/check commands first when present.
