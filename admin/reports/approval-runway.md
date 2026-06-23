# Approval Runway - Lily Roo

Generated: 2026-06-23T04:31:13.216614Z

## Summary
- Drafts needing review: **7**
- Ready after approval: **6**
- Manual-only drafts: **0**
- Blocked drafts: **1**
- Recommended approvals: **6**
- Recommended manual approvals: **0**
- Monetization runway: **behind_365_day_pace**, 0.5 subs/week observed, 19.06 subs/week needed for 365 days

## Manual Approval Docket
- Status: **clear**
- Ready manual approvals: **0**
- Blocked rows kept out: **1**
- Guardrail: Manual-only approvals do not auto-post; posting and public URL logging remain separate after review.

## Recommended Sequence
- **Facebook - Analog Myth** (`FP-STORY-ANALOG-MYTH-FACEBOOK-ARCHIVE-CTA`)
  - Readiness: `ready_after_approval`; score: `123`
  - Recommendation: Review copy, then approve to unlock an auto-publishable subscriber CTA.
  - Copy: Time broke, so Lily Roo made an album out of the pieces. Subscribe on YouTube and help Lily Roo push this signal toward 1,000.
  - Preview: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-ANALOG-MYTH-FACEBOOK-ARCHIVE-CTA --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-ANALOG-MYTH-FACEBOOK-ARCHIVE-CTA --refresh-admin`
- **Facebook - I Learned It All in Fifteen Seconds** (`FP-STORY-I-LEARNED-IT-ALL-IN-FIFTEEN-SECONDS-FACEBOOK-ARCHIVE-CTA`)
  - Readiness: `ready_after_approval`; score: `123`
  - Recommendation: Review copy, then approve to unlock an auto-publishable subscriber CTA.
  - Copy: I Learned It All in Fifteen Seconds is live in the Lily Roo archive. Subscribe on YouTube and help Lily Roo push this signal toward 1,000.
  - Preview: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-I-LEARNED-IT-ALL-IN-FIFTEEN-SECONDS-FACEBOOK-ARCHIVE-CTA --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-I-LEARNED-IT-ALL-IN-FIFTEEN-SECONDS-FACEBOOK-ARCHIVE-CTA --refresh-admin`
- **Facebook - Twelve Dollars** (`FP-STORY-TWELVE-DOLLARS-FACEBOOK-ARCHIVE-CTA`)
  - Readiness: `ready_after_approval`; score: `123`
  - Recommendation: Review copy, then approve to unlock an auto-publishable subscriber CTA.
  - Copy: A small amount of money, a large amount of stage light. Subscribe on YouTube and help Lily Roo push this signal toward 1,000.
  - Preview: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-TWELVE-DOLLARS-FACEBOOK-ARCHIVE-CTA --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-TWELVE-DOLLARS-FACEBOOK-ARCHIVE-CTA --refresh-admin`
- **X - Analog Myth** (`FP-STORY-ANALOG-MYTH-X-ARCHIVE-CTA`)
  - Readiness: `ready_after_approval`; score: `123`
  - Recommendation: Review copy, then approve to unlock an auto-publishable subscriber CTA.
  - Copy: Time broke, so Lily Roo made an album out of the pieces. Subscribe on YouTube and help Lily Roo push this signal toward 1,000.
  - Preview: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-ANALOG-MYTH-X-ARCHIVE-CTA --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-ANALOG-MYTH-X-ARCHIVE-CTA --refresh-admin`
- **X - I Learned It All in Fifteen Seconds** (`FP-STORY-I-LEARNED-IT-ALL-IN-FIFTEEN-SECONDS-X-ARCHIVE-CTA`)
  - Readiness: `ready_after_approval`; score: `123`
  - Recommendation: Review copy, then approve to unlock an auto-publishable subscriber CTA.
  - Copy: I Learned It All in Fifteen Seconds is live in the Lily Roo archive. Subscribe on YouTube and help Lily Roo push this signal toward 1,000.
  - Preview: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-I-LEARNED-IT-ALL-IN-FIFTEEN-SECONDS-X-ARCHIVE-CTA --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-I-LEARNED-IT-ALL-IN-FIFTEEN-SECONDS-X-ARCHIVE-CTA --refresh-admin`
- **X - Twelve Dollars** (`FP-STORY-TWELVE-DOLLARS-X-ARCHIVE-CTA`)
  - Readiness: `ready_after_approval`; score: `123`
  - Recommendation: Review copy, then approve to unlock an auto-publishable subscriber CTA.
  - Copy: A small amount of money, a large amount of stage light. Subscribe on YouTube and help Lily Roo push this signal toward 1,000.
  - Preview: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-TWELVE-DOLLARS-X-ARCHIVE-CTA --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-STORY-TWELVE-DOLLARS-X-ARCHIVE-CTA --refresh-admin`
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
