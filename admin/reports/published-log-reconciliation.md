# Published Log Reconciliation - Lily Roo

Generated: 2026-07-02T01:22:31.096493Z

## Summary
- Published log status: **fresh**
- Published log rows: **48**
- Unlogged Worker posts: **0**
- Unlogged manual posts: **0**
- Reconciliation needed: **False**

## Worker Export
- Posted Worker records: **0**
- Unlogged Worker records: **0**
- Preview/check: `python3 scripts/export_social_executions.py --dry-run`
- Apply after review: `python3 scripts/export_social_executions.py --refresh-admin`

## Manual Logging
- Unlogged manual rows: **0**
- Guardrail: Only log manual distribution after approval, manual posting, and a real public post URL.

### Manual Log Gates
- Approval gate: **clear**; ready: **0**; blocked: **0**
- Posting gate: **empty**; needs review: **0**; postable: **0**
- URL logging gate: **clear**
- Posting session: `data/manual-posting-cards/youtube-community-session.md`
- URL worksheet: `data/manual_distribution_url_template.csv`
- Partial URL apply: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --allow-partial --apply --refresh-admin`

### Manual Rows

## Guardrails
- This reconciliation is review-only and does not export, append, post, or publish.
- Worker export apply should run only after the dry run shows posted records with public URLs.
- Manual rows require real public URLs; never replace `PUBLIC_URL` with a placeholder.
