# Brand Activation Plan - Lily Roo

Generated: 2026-07-29T03:42:22.530614Z

## Summary
- Brand growth goal: **release_forward_brand_growth**
- Runway status: **moving**
- Ready release-forward approvals: **0**
- Solicitation rewrites available: **0**
- Platform fixes: **12**
- Activation actions: **14**

## Activation Sequence
1. **Preview approved backlog reschedule**
   - Phase: `Recover stalled approved backlog`; status: `preview_first`
   - Detail: Preview a new schedule for approved past-due posts. Normal apply is hidden until known executor/platform blockers clear.
   - Blocked apply command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-30T10:00:00+00:00' --spacing-hours 24 --apply --refresh-admin`
   - Deliberate override command: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-30T10:00:00+00:00' --spacing-hours 24 --allow-blocked --apply --refresh-admin`
   - Preview/check: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-30T10:00:00+00:00' --spacing-hours 24`
2. **Repair Facebook executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-FACEBOOK`
3. **Repair Facebook executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-FACEBOOK`
4. **Repair Facebook executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-03-SLOW-WALK-VISUAL-STORY-FACEBOOK`
5. **Repair Facebook executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-FACEBOOK`
6. **Repair Facebook executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-05-SPILLING-THE-TEA-LYRIC-PUNCH-LINE-FACEBOOK`
7. **Repair Facebook executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-06-SPILLING-THE-TEA-RELATABLE-SITUATION-FACEBOOK`
8. **Repair Facebook executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-07-SPILLING-THE-TEA-VISUAL-STORY-FACEBOOK`
9. **Repair YouTube executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Review platform credentials/readiness, then rerun the social execution capture.
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE`
10. **Repair YouTube executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Review platform credentials/readiness, then rerun the social execution capture.
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-05-SPILLING-THE-TEA-LYRIC-PUNCH-LINE-YOUTUBE`
11. **Repair YouTube executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Review platform credentials/readiness, then rerun the social execution capture.
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-06-SPILLING-THE-TEA-RELATABLE-SITUATION-YOUTUBE`
12. **Repair YouTube executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Review platform credentials/readiness, then rerun the social execution capture.
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-07-SPILLING-THE-TEA-VISUAL-STORY-YOUTUBE`
13. **Repair YouTube executor**
   - Phase: `Clear platform blockers`; status: `needs_platform_fix`
   - Detail: Review platform credentials/readiness, then rerun the social execution capture.
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-08-SPILLING-THE-TEA-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE`
14. **Current operations next action: Fix YouTube executor**
   - Phase: `Operations packet`; status: `needs_fix`
   - Detail: Platform executor needs repair before queued auto posts can publish.
   - Preview/check: `python3 scripts/check_social_executor_dry_run.py --post-id FP-GROWTH-RESET-08-SPILLING-THE-TEA-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE`

## Guardrails
- This plan does not approve, apply, publish, or post anything.
- Approval and apply commands are shown as deliberate after-review steps.
- Run preview/check commands first when present.
