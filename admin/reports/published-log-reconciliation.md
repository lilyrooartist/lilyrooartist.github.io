# Published Log Reconciliation - Lily Roo

Generated: 2026-06-20T04:17:55.532274Z

## Summary
- Published log status: **stale**
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
- Guardrail: Only log manual distribution after the public post URL exists.
- **Twelve Dollars YouTube Community** (`FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY`)
  - Status: `waiting_for_review`
  - Posting surface: https://www.youtube.com/@lilyroo.artist/community
  - Preview URL log: `python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url PUBLIC_URL`
  - Apply URL log after posting: `python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url PUBLIC_URL --apply --refresh-admin`
- **Analog Myth YouTube Community** (`FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY`)
  - Status: `waiting_for_review`
  - Posting surface: https://www.youtube.com/@lilyroo.artist/community
  - Preview URL log: `python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url PUBLIC_URL`
  - Apply URL log after posting: `python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url PUBLIC_URL --apply --refresh-admin`

## Guardrails
- This reconciliation is review-only and does not export, append, post, or publish.
- Worker export apply should run only after the dry run shows posted records with public URLs.
- Manual rows require real public URLs; never replace `PUBLIC_URL` with a placeholder.
