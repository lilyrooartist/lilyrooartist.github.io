# Manual Distribution Packet - Lily Roo

Generated: 2026-07-02T01:10:11.577484Z

## Summary
- Manual-ready posts: **0**
- YouTube Community posts: **0**
- Solicitation-style CTAs: **0**
- Approved manual posts: **0**
- Logged manual posts: **0**
- Unlogged manual posts: **0**
- Public URL logs still needed: **0**

## Manual Posting Docket
- Status: **empty**
- Needs review: **0**
- Postable now: **0**
- Logged: **0**
- Public community surface: https://www.youtube.com/@lilyroo.artist/community

### Approval Gate
- Status: **clear**
- Ready approvals: **0**
- Blocked approvals: **0**
- Guardrail: Manual-only approvals do not auto-post; posting and public URL logging remain separate after review.

### Completion Manifest
- Status: **clear**
- Review queue IDs: `none`
- Postable now IDs: `none`
- Pending log IDs: `none`
- Posting surface: YouTube Studio Community
- Public community URL: https://www.youtube.com/@lilyroo.artist/community
- Public URL worksheet: `data/manual_distribution_url_template.csv`
- Batch URL log preview: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv`
- Batch URL log apply after posting: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --apply --refresh-admin`
- URL worksheet rows waiting: **0**
- Operator checklist:
  - Review the packaged copy, asset, and destination link evidence.
  - Run the approval preview command before applying any manual approval.
  - Post approved rows manually in YouTube Studio Community.
  - Copy the real individual public Community post URL after posting; it should look like https://www.youtube.com/post/...
  - Paste public URLs into data/manual_distribution_url_template.csv for batch logging.
  - Run the log preview command with the real URL, then apply with --apply --refresh-admin.
- Completion evidence:
  - data/manual_distribution_packet.json shows the row as logged or no longer pending.
  - data/published_log_reconciliation.json no longer reports the row as an unlogged manual post.
  - admin/content/Published_Log.csv contains the real public URL and manual_distribution_id note.
  - data/promo_engine_status.json and lilyroo.com/admin reflect the updated manual distribution counts.
- Guardrails:
  - Manual-only approvals do not auto-post.
  - Do not log a placeholder URL.
  - For YouTube Community rows, log an individual https://www.youtube.com/post/... URL, not the channel, playlist, video, or Community tab URL.
  - Do not apply the URL worksheet while any public_url cell is blank.
  - Do not mark manual distribution complete until a real public YouTube Community URL is logged.

### Needs Review
- None

### Postable Now
- None

## Manual Posting Queue

## Guardrails
- This packet does not approve, schedule, publish, or post anything.
- No manual posting checklist is active; manual-only rows have been removed from the plan.
