# Monetization Activation Plan - Lily Roo

Generated: 2026-07-03T06:33:28.512308Z

## Summary
- Current YouTube audience metric: **5 subscribers**
- Runway status: **stalled**
- Ready song-forward approvals: **0**
- Solicitation rewrites available: **0**
- Platform fixes: **4**
- Activation actions: **5**

## Activation Sequence
1. **Repair Instagram executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Worker cannot resolve instagram_business_account from FB_PAGE_ID. Local secret source is missing: IG_BUSINESS_ACCOUNT_ID. Set IG_BUSINESS_ACCOUNT_ID from Meta Business/Instagram Graph, push it to the Worker, then recapture readiness.
   - Missing locally: `IG_BUSINESS_ACCOUNT_ID`
   - Local source: `secrets/social_api.env`
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-258`
2. **Repair Instagram executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Worker cannot resolve instagram_business_account from FB_PAGE_ID. Local secret source is missing: IG_BUSINESS_ACCOUNT_ID. Set IG_BUSINESS_ACCOUNT_ID from Meta Business/Instagram Graph, push it to the Worker, then recapture readiness.
   - Missing locally: `IG_BUSINESS_ACCOUNT_ID`
   - Local source: `secrets/social_api.env`
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-263`
3. **Repair Instagram executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Worker cannot resolve instagram_business_account from FB_PAGE_ID. Local secret source is missing: IG_BUSINESS_ACCOUNT_ID. Set IG_BUSINESS_ACCOUNT_ID from Meta Business/Instagram Graph, push it to the Worker, then recapture readiness.
   - Missing locally: `IG_BUSINESS_ACCOUNT_ID`
   - Local source: `secrets/social_api.env`
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`
4. **Repair TikTok executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Local upload-mode OAuth credentials missing: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. Complete TikTok OAuth setup locally, then push upload-mode secrets and refresh Admin.
   - Missing locally: `TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN`
   - Local source: `secrets/social_api.env`
   - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
5. **Current operations next action: Fix Instagram executor**
   - Phase: `Operations packet`; status: `needs_fix`
   - Detail: Platform executor needs repair before queued auto posts can publish.
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`

## Guardrails
- This plan does not approve, apply, publish, or post anything.
- Approval and apply commands are shown as deliberate after-review steps.
- Run preview/check commands first when present.
