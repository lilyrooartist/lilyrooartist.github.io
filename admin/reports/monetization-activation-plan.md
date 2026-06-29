# Monetization Activation Plan - Lily Roo

Generated: 2026-06-29T15:09:59.197138Z

## Summary
- Current subscribers: **6 / 1000**
- Runway status: **behind_365_day_pace**
- Ready song-forward approvals: **0**
- Solicitation rewrites available: **0**
- Platform fixes: **5**
- Activation actions: **7**

## Activation Sequence
1. **Preview approved backlog reschedule**
   - Phase: `Recover stalled approved backlog`; status: `preview_first`
   - Detail: Preview a new schedule for approved past-due posts. Normal apply is hidden until known executor/platform blockers clear.
   - Blocked apply command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-30T10:00:00-04:00' --spacing-hours 24 --apply --refresh-admin`
   - Deliberate override command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-30T10:00:00-04:00' --spacing-hours 24 --allow-blocked --apply --refresh-admin`
   - Preview/check: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-30T10:00:00-04:00' --spacing-hours 24`
2. **Repair Instagram executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Worker cannot resolve instagram_business_account from FB_PAGE_ID. Local secret source is missing: IG_BUSINESS_ACCOUNT_ID. Set IG_BUSINESS_ACCOUNT_ID from Meta Business/Instagram Graph, push it to the Worker, then recapture readiness.
   - Missing locally: `IG_BUSINESS_ACCOUNT_ID`
   - Local source: `secrets/social_api.env`
   - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run IG_BUSINESS_ACCOUNT_ID`
3. **Repair Facebook executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-265`
4. **Repair Facebook executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-268`
5. **Repair Facebook executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-AUTO-273`
6. **Repair YouTube executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Review platform credentials/readiness, then rerun the social execution capture.
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-SHORT-ANALOG-MYTH-YOUTUBE-SHORTS-CTA`
7. **Current operations next action: Preview checked scheduled approval batch**
   - Phase: `Operations packet`; status: `waiting_for_user`
   - Detail: Scheduled executor records are blocked until reviewed approval is applied.
   - Preview/check: `python3 scripts/update_scheduled_post_approval.py --checked-batch --dry-run`
   - After review: `python3 scripts/update_scheduled_post_approval.py --checked-batch --refresh-admin`

## Guardrails
- This plan does not approve, apply, publish, or post anything.
- Approval and apply commands are shown as deliberate after-review steps.
- Run preview/check commands first when present.
