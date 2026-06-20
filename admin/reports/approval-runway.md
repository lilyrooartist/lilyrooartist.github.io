# Approval Runway - Lily Roo

Generated: 2026-06-20T08:51:29.103892Z

## Summary
- Drafts needing review: **3**
- Ready after approval: **0**
- Manual-only drafts: **2**
- Blocked drafts: **1**
- Recommended approvals: **2**
- Recommended manual approvals: **2**
- Monetization runway: **behind_365_day_pace**, 0.64 subs/week observed, 19.06 subs/week needed for 365 days

## Manual Approval Docket
- Status: **ready_for_manual_review**
- Ready manual approvals: **2**
- Blocked rows kept out: **1**
- Preview manual approvals: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --dry-run`
- Approve manual rows after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --refresh-admin`
- Guardrail: Manual-only approvals do not auto-post; posting and public URL logging remain separate after review.

## Recommended Sequence
- **YouTube Community - Analog Myth** (`FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY`)
  - Readiness: `manual_only`; score: `116`
  - Recommendation: Review copy and use the manual posting workflow; approval will not auto-post this row.
  - Copy: Analog Myth is part of the Lily Roo archive now. Help us build the signal to 1,000 subscribers.
  - Preview: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --refresh-admin`
- **YouTube Community - Twelve Dollars** (`FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY`)
  - Readiness: `manual_only`; score: `116`
  - Recommendation: Review copy and use the manual posting workflow; approval will not auto-post this row.
  - Copy: Twelve Dollars is part of the Lily Roo archive now. Help us build the signal to 1,000 subscribers.
  - Preview: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --refresh-admin`
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
