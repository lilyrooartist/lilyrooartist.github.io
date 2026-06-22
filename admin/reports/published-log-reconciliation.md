# Published Log Reconciliation - Lily Roo

Generated: 2026-06-22T10:20:30.416189Z

## Summary
- Published log status: **fresh**
- Published log rows: **17**
- Unlogged Worker posts: **0**
- Unlogged manual posts: **3**
- Reconciliation needed: **True**

## Worker Export
- Posted Worker records: **0**
- Unlogged Worker records: **0**
- Preview/check: `python3 scripts/export_social_executions.py --dry-run`
- Apply after review: `python3 scripts/export_social_executions.py --refresh-admin`

## Manual Logging
- Unlogged manual rows: **3**
- Guardrail: Only log manual distribution after approval, manual posting, and a real public post URL.

### Manual Log Gates
- Approval gate: **clear**; ready: **0**; blocked: **1**
- Posting gate: **postable_now**; needs review: **0**; postable: **3**
- URL logging gate: **waiting_for_public_urls**
- Posting session: `data/manual-posting-cards/youtube-community-session.md`
- URL worksheet: `data/manual_distribution_url_template.csv`
- Partial URL apply: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --allow-partial --apply --refresh-admin`
- Blocked approval IDs: `FP-PLAN-TWELVE-DOLLARS-TIKTOK`

### Manual Rows
- **I Learned It All in Fifteen Seconds YouTube Community** (`FP-AUTO-261`)
  - Status: `ready_for_manual_post`; log gate: `blocked_until_public_url`
  - Next step: Post manually in YouTube Studio Community, then replace PUBLIC_URL with the real public URL.
  - Posting surface: https://www.youtube.com/@lilyroo.artist/community
  - Preview URL log: `python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url PUBLIC_URL`
  - Apply URL log after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url PUBLIC_URL --apply --refresh-admin`
- **Twelve Dollars YouTube Community** (`FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY`)
  - Status: `ready_for_manual_post`; log gate: `blocked_until_public_url`
  - Next step: Post manually in YouTube Studio Community, then replace PUBLIC_URL with the real public URL.
  - Posting surface: https://www.youtube.com/@lilyroo.artist/community
  - Preview URL log: `python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url PUBLIC_URL`
  - Apply URL log after posting: `python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url PUBLIC_URL --apply --refresh-admin`
- **Analog Myth YouTube Community** (`FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY`)
  - Status: `ready_for_manual_post`; log gate: `blocked_until_public_url`
  - Next step: Post manually in YouTube Studio Community, then replace PUBLIC_URL with the real public URL.
  - Posting surface: https://www.youtube.com/@lilyroo.artist/community
  - Preview URL log: `python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url PUBLIC_URL`
  - Apply URL log after posting: `python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url PUBLIC_URL --apply --refresh-admin`

## Guardrails
- This reconciliation is review-only and does not export, append, post, or publish.
- Worker export apply should run only after the dry run shows posted records with public URLs.
- Manual rows require real public URLs; never replace `PUBLIC_URL` with a placeholder.
