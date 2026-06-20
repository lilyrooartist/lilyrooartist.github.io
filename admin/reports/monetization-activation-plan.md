# Monetization Activation Plan - Lily Roo

Generated: 2026-06-20T00:27:40.025016Z

## Summary
- Current subscribers: **6 / 1000**
- Runway status: **behind_365_day_pace**
- Ready subscriber CTA approvals: **0**
- Subscriber CTA swaps available: **0**
- Platform fixes: **3**
- Activation actions: **6**

## Activation Sequence
1. **Apply approved plan rows after review**
   - Phase: `Move approved subscriber posts into queue`; status: `blocked_until_approved`
   - Detail: After copy review and approval, apply only approved rows to the live queue; this does not directly post externally.
   - After review: `python3 scripts/apply_promo_queue_plan.py --apply --refresh-admin`
2. **Preview approved backlog reschedule**
   - Phase: `Recover stalled approved backlog`; status: `preview_first`
   - Detail: Preview a new schedule for approved past-due posts. Apply refuses known blocked executor rows unless deliberately overridden.
   - Preview/check: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-21T10:00:00+09:00' --spacing-hours 24`
   - After review: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-21T10:00:00+09:00' --spacing-hours 24 --apply --refresh-admin`
3. **Repair Instagram executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Reconnect the Instagram Business/Creator account to the Facebook Page or set IG_BUSINESS_ACCOUNT_ID, then push the worker secret and recapture readiness.
   - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run IG_BUSINESS_ACCOUNT_ID`
   - After review: `python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py`
4. **Repair Facebook executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
   - Preview/check: `python3 scripts/check_facebook_publishing.py --post-id 'FP-AUTO-265' --check-worker-dry-run`
5. **Repair TikTok executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Missing worker secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. TikTok public posting approval is false. Complete TikTok OAuth/public posting setup, push secrets, then refresh Admin.
   - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
   - After review: `python3 scripts/push_social_worker_secrets.py TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN && python3 scripts/refresh_promo_admin.py`
6. **Current operations next action: Preview reschedule for approved past-due posts**
   - Phase: `Operations packet`; status: `waiting_for_user`
   - Detail: Approved posts are past due; preview a new schedule before any apply step.
   - Preview/check: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-21T10:00:00+09:00' --spacing-hours 24`
   - After review: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-21T10:00:00+09:00' --spacing-hours 24 --apply --refresh-admin`

## Guardrails
- This plan does not approve, apply, publish, or post anything.
- Approval and apply commands are shown as deliberate after-review steps.
- Run preview/check commands first when present.
