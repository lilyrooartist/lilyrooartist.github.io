# Approval Runway - Lily Roo

Generated: 2026-06-22T12:06:39.950747Z

## Summary
- Drafts needing review: **1**
- Ready after approval: **0**
- Manual-only drafts: **0**
- Blocked drafts: **1**
- Recommended approvals: **0**
- Recommended manual approvals: **0**
- Monetization runway: **behind_365_day_pace**, 0.54 subs/week observed, 19.06 subs/week needed for 365 days

## Manual Approval Docket
- Status: **clear**
- Ready manual approvals: **0**
- Blocked rows kept out: **1**
- Guardrail: Manual-only approvals do not auto-post; posting and public URL logging remain separate after review.

## Recommended Sequence
- **TikTok - Twelve Dollars** (`FP-PLAN-TWELVE-DOLLARS-TIKTOK`)
  - Readiness: `blocked`; score: `18`
  - Recommendation: Repair platform readiness before approval can create reliable distribution.
  - Copy: Twelve Dollars is part of the Lily Roo archive now. Help us build the signal to 1,000 subscribers.
  - Preview: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-TIKTOK --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-TIKTOK --refresh-admin`

## Guardrails
- This runway does not approve, apply, publish, or post anything.
- Run preview commands first, then approval commands only after copy review.
- Applying approved rows to the live queue remains a separate deliberate step.
