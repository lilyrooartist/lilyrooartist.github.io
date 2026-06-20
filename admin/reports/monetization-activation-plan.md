# Monetization Activation Plan - Lily Roo

Generated: 2026-06-20T07:58:51.905222Z

## Summary
- Current subscribers: **6 / 1000**
- Runway status: **behind_365_day_pace**
- Ready subscriber CTA approvals: **2**
- Subscriber CTA swaps available: **0**
- Platform fixes: **1**
- Activation actions: **5**

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
   - Blocked apply command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-21T10:00:00+00:00' --spacing-hours 24 --apply --refresh-admin`
   - Deliberate override command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-21T10:00:00+00:00' --spacing-hours 24 --allow-blocked --apply --refresh-admin`
   - Preview/check: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-21T10:00:00+00:00' --spacing-hours 24`
4. **Repair TikTok executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Missing worker secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. TikTok public posting approval is false. Local secret source is also missing: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. Complete TikTok OAuth/public posting setup locally, then push secrets and refresh Admin.
   - Missing secrets: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
   - Missing locally: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
   - Local source: `secrets/social_api.env`
   - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
5. **Current operations next action: Preview checked scheduled approval batch**
   - Phase: `Operations packet`; status: `waiting_for_user`
   - Detail: Scheduled executor records are blocked until reviewed approval is applied.
   - Preview/check: `python3 scripts/update_scheduled_post_approval.py --checked-batch --dry-run`
   - After review: `python3 scripts/update_scheduled_post_approval.py --checked-batch --refresh-admin`

## Guardrails
- This plan does not approve, apply, publish, or post anything.
- Approval and apply commands are shown as deliberate after-review steps.
- Run preview/check commands first when present.
