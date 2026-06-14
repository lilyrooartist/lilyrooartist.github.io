# Approval Runway - Lily Roo

Generated: 2026-06-14T01:32:28.062358Z

## Summary
- Drafts needing review: **6**
- Ready after approval: **3**
- Manual-only drafts: **2**
- Blocked drafts: **1**
- Recommended approvals: **3**
- Monetization runway: **stalled**, 0.0 subs/week observed, 19.08 subs/week needed for 365 days

## Recommended Sequence
- **Facebook - Twelve Dollars** (`FP-PLAN-TWELVE-DOLLARS-FACEBOOK`)
  - Readiness: `ready_after_approval`; score: `108`
  - Recommendation: Review copy, then approve to unlock an auto-publishable subscriber CTA.
  - Copy: Twelve Dollars is live in the Lily Roo archive. The remastered videos are up, the playlist is public, and the stage finally has the right kind of trouble on it.
  - Preview: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-FACEBOOK --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-FACEBOOK --refresh-admin`
- **Instagram - Twelve Dollars** (`FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`)
  - Readiness: `ready_after_approval`; score: `108`
  - Recommendation: Review copy, then approve to unlock an auto-publishable subscriber CTA.
  - Copy: Twelve Dollars is live on YouTube: stage lights, scattered bills, impossible shoes, and one very stubborn little signal.
  - Preview: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM --refresh-admin`
- **X - Twelve Dollars** (`FP-PLAN-TWELVE-DOLLARS-X`)
  - Readiness: `ready_after_approval`; score: `108`
  - Recommendation: Review copy, then approve to unlock an auto-publishable subscriber CTA.
  - Copy: Twelve Dollars is the part where the stage gets too bright and the joke gets honest. Full album playlist is live.
  - Preview: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-X --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-X --refresh-admin`
- **YouTube Community - Analog Myth** (`FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY`)
  - Readiness: `manual_only`; score: `101`
  - Recommendation: Review copy and use the manual posting workflow; approval will not auto-post this row.
  - Copy: Analog Myth transmission is live: 13, Girls Camp, Analog Myth, Spilling the Tea, No Mortgage, Guards Down, Slow Walk, The Power of Light.
  - Preview: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --refresh-admin`
- **YouTube Community - Twelve Dollars** (`FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY`)
  - Readiness: `manual_only`; score: `101`
  - Recommendation: Review copy and use the manual posting workflow; approval will not auto-post this row.
  - Copy: New album transmission: Twelve Dollars. Remastered videos, updated art, full playlist live now.
  - Preview: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --refresh-admin`
- **TikTok - Twelve Dollars** (`FP-PLAN-TWELVE-DOLLARS-TIKTOK`)
  - Readiness: `blocked`; score: `3`
  - Recommendation: Repair platform readiness before approval can create reliable distribution.
  - Copy: Twelve Dollars is what happens when the joke walks on stage wearing impossible shoes. Full album playlist is live.
  - Preview: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-TIKTOK --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-TIKTOK --refresh-admin`

## Guardrails
- This runway does not approve, apply, publish, or post anything.
- Run preview commands first, then approval commands only after copy review.
- Applying approved rows to the live queue remains a separate deliberate step.
