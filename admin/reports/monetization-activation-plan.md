# Monetization Activation Plan - Lily Roo

Generated: 2026-06-23T04:29:19.882430Z

## Summary
- Current subscribers: **6 / 1000**
- Runway status: **behind_365_day_pace**
- Ready subscriber CTA approvals: **6**
- Subscriber CTA swaps available: **0**
- Platform fixes: **5**
- Activation actions: **14**

## Activation Sequence
1. **Review subscriber CTA for Facebook**
   - Phase: `Tighten subscriber CTA`; status: `waiting_for_review`
   - Detail: Selected copy already has a hard subscriber CTA. Recommended copy: Time broke, so Lily Roo made an album out of the pieces. Subscribe on YouTube and help Lily Roo push this signal toward 1,000.
   - Preview/check: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-ANALOG-MYTH-FACEBOOK-ARCHIVE-CTA --dry-run`
   - After review: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-ANALOG-MYTH-FACEBOOK-ARCHIVE-CTA --refresh-admin`
2. **Review subscriber CTA for Facebook**
   - Phase: `Tighten subscriber CTA`; status: `waiting_for_review`
   - Detail: Selected copy already has a hard subscriber CTA. Recommended copy: I Learned It All in Fifteen Seconds is live in the Lily Roo archive. Subscribe on YouTube and help Lily Roo push this signal toward 1,000.
   - Preview/check: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-I-LEARNED-IT-ALL-IN-FIFTEEN-SECONDS-FACEBOOK-ARCHIVE-CTA --dry-run`
   - After review: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-I-LEARNED-IT-ALL-IN-FIFTEEN-SECONDS-FACEBOOK-ARCHIVE-CTA --refresh-admin`
3. **Review subscriber CTA for Facebook**
   - Phase: `Tighten subscriber CTA`; status: `waiting_for_review`
   - Detail: Selected copy already has a hard subscriber CTA. Recommended copy: A small amount of money, a large amount of stage light. Subscribe on YouTube and help Lily Roo push this signal toward 1,000.
   - Preview/check: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-TWELVE-DOLLARS-FACEBOOK-ARCHIVE-CTA --dry-run`
   - After review: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-TWELVE-DOLLARS-FACEBOOK-ARCHIVE-CTA --refresh-admin`
4. **Review subscriber CTA for X**
   - Phase: `Tighten subscriber CTA`; status: `waiting_for_review`
   - Detail: Selected copy already has a hard subscriber CTA. Recommended copy: Time broke, so Lily Roo made an album out of the pieces. Subscribe on YouTube and help Lily Roo push this signal toward 1,000.
   - Preview/check: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-ANALOG-MYTH-X-ARCHIVE-CTA --dry-run`
   - After review: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-ANALOG-MYTH-X-ARCHIVE-CTA --refresh-admin`
5. **Review subscriber CTA for X**
   - Phase: `Tighten subscriber CTA`; status: `waiting_for_review`
   - Detail: Selected copy already has a hard subscriber CTA. Recommended copy: I Learned It All in Fifteen Seconds is live in the Lily Roo archive. Subscribe on YouTube and help Lily Roo push this signal toward 1,000.
   - Preview/check: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-I-LEARNED-IT-ALL-IN-FIFTEEN-SECONDS-X-ARCHIVE-CTA --dry-run`
   - After review: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-I-LEARNED-IT-ALL-IN-FIFTEEN-SECONDS-X-ARCHIVE-CTA --refresh-admin`
6. **Review subscriber CTA for X**
   - Phase: `Tighten subscriber CTA`; status: `waiting_for_review`
   - Detail: Selected copy already has a hard subscriber CTA. Recommended copy: A small amount of money, a large amount of stage light. Subscribe on YouTube and help Lily Roo push this signal toward 1,000.
   - Preview/check: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-TWELVE-DOLLARS-X-ARCHIVE-CTA --dry-run`
   - After review: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-TWELVE-DOLLARS-X-ARCHIVE-CTA --refresh-admin`
7. **Apply approved plan rows after review**
   - Phase: `Move approved subscriber posts into queue`; status: `blocked_until_approved`
   - Detail: After copy review and approval, apply only approved rows to the live queue; this does not directly post externally.
   - After review: `python3 scripts/apply_promo_queue_plan.py --apply --refresh-admin`
8. **Preview approved backlog reschedule**
   - Phase: `Recover stalled approved backlog`; status: `preview_first`
   - Detail: Preview a new schedule for approved past-due posts. Normal apply is hidden until known executor/platform blockers clear.
   - Blocked apply command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-24T10:00:00+00:00' --spacing-hours 24 --apply --refresh-admin`
   - Deliberate override command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-24T10:00:00+00:00' --spacing-hours 24 --allow-blocked --apply --refresh-admin`
   - Preview/check: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-24T10:00:00+00:00' --spacing-hours 24`
9. **Repair Instagram executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Worker cannot resolve instagram_business_account from FB_PAGE_ID. Local secret source is missing: IG_BUSINESS_ACCOUNT_ID. Set IG_BUSINESS_ACCOUNT_ID from Meta Business/Instagram Graph, push it to the Worker, then recapture readiness.
   - Missing locally: `IG_BUSINESS_ACCOUNT_ID`
   - Local source: `secrets/social_api.env`
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-258`
10. **Repair Instagram executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Worker cannot resolve instagram_business_account from FB_PAGE_ID. Local secret source is missing: IG_BUSINESS_ACCOUNT_ID. Set IG_BUSINESS_ACCOUNT_ID from Meta Business/Instagram Graph, push it to the Worker, then recapture readiness.
   - Missing locally: `IG_BUSINESS_ACCOUNT_ID`
   - Local source: `secrets/social_api.env`
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-263`
11. **Repair Instagram executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Worker cannot resolve instagram_business_account from FB_PAGE_ID. Local secret source is missing: IG_BUSINESS_ACCOUNT_ID. Set IG_BUSINESS_ACCOUNT_ID from Meta Business/Instagram Graph, push it to the Worker, then recapture readiness.
   - Missing locally: `IG_BUSINESS_ACCOUNT_ID`
   - Local source: `secrets/social_api.env`
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`
12. **Repair Facebook executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
   - Preview/check: `python3 scripts/check_facebook_publishing.py --post-id 'FP-AUTO-265' --check-worker-dry-run`
13. **Repair TikTok executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Missing worker secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. TikTok direct public posting approval is false, but upload-draft mode can proceed after credentials. Local secret source is also missing: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. Complete TikTok OAuth setup locally, then push upload-mode secrets and refresh Admin.
   - Missing secrets: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
   - Missing locally: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
   - Local source: `secrets/social_api.env`
   - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
14. **Current operations next action: Fix Instagram executor**
   - Phase: `Operations packet`; status: `needs_fix`
   - Detail: Platform executor needs repair before queued auto posts can publish.
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`

## Guardrails
- This plan does not approve, apply, publish, or post anything.
- Approval and apply commands are shown as deliberate after-review steps.
- Run preview/check commands first when present.
