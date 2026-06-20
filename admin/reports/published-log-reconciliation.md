# Published Log Reconciliation - Lily Roo

Generated: 2026-06-20T09:00:20.632013Z

## Summary
- Published log status: **gated_manual_pending**
- Published log rows: **17**
- Unlogged Worker posts: **0**
- Unlogged manual posts: **2**
- Reconciliation needed: **True**

## Worker Export
- Posted Worker records: **0**
- Unlogged Worker records: **0**
- Preview/check: `python3 scripts/export_social_executions.py --dry-run`
- Apply after review: `python3 scripts/export_social_executions.py --refresh-admin`

## Manual Logging
- Unlogged manual rows: **2**
- Guardrail: Only log manual distribution after approval, manual posting, and a real public post URL.

### Manual Log Gates
- Approval gate: **ready_for_manual_review**; ready: **2**; blocked: **1**
- Posting gate: **needs_review**; needs review: **2**; postable: **0**
- Ready approval IDs: `FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY, FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY`
- Blocked approval IDs: `FP-PLAN-TWELVE-DOLLARS-TIKTOK`
- Preview approvals: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --dry-run`
- Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --refresh-admin`

### Manual Rows
- **Twelve Dollars YouTube Community** (`FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY`)
  - Status: `waiting_for_review`; log gate: `blocked_until_manual_approval`
  - Next step: Approve the manual row after review, post it in YouTube Studio Community, then log the public URL.
  - Posting surface: https://www.youtube.com/@lilyroo.artist/community
  - Preview approval: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --refresh-admin`
  - Preview URL log: `python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url PUBLIC_URL`
  - Apply URL log after posting: `python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url PUBLIC_URL --apply --refresh-admin`
- **Analog Myth YouTube Community** (`FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY`)
  - Status: `waiting_for_review`; log gate: `blocked_until_manual_approval`
  - Next step: Approve the manual row after review, post it in YouTube Studio Community, then log the public URL.
  - Posting surface: https://www.youtube.com/@lilyroo.artist/community
  - Preview approval: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --dry-run`
  - Approve after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --refresh-admin`
  - Preview URL log: `python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url PUBLIC_URL`
  - Apply URL log after posting: `python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url PUBLIC_URL --apply --refresh-admin`

## Guardrails
- This reconciliation is review-only and does not export, append, post, or publish.
- Worker export apply should run only after the dry run shows posted records with public URLs.
- Manual rows require real public URLs; never replace `PUBLIC_URL` with a placeholder.
