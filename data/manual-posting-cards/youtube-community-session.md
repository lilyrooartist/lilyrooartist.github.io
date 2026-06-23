# YouTube Community Manual Posting Session

Generated: 2026-06-23T08:49:09.279284Z
Surface: https://www.youtube.com/@lilyroo.artist/community
URL worksheet: data/manual_distribution_url_template.csv
Partial apply: python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --allow-partial --apply --refresh-admin

## Steps
- Open the YouTube Community surface once.
- Post each session row in sequence using its copy_source and asset_source.
- After each publish, copy the real public URL into the URL worksheet.
- Run the batch preview command; use partial apply if only some rows have public URLs.
- After logging, collect the first 24-hour metrics from the result handoff report.

## First Post Runbook
- Status: clear
- Post: not available
- Copy file: not available
- Asset: not available
- URL worksheet: not available
- Worksheet update: not available
- Preview: not available
- Apply: not available
- Partial apply: not available
- Measurement trigger: not available

## First URL Acceleration
- Status: clear
- First post: not available
- Why: not available
- Preview: not available
- Partial apply: not available
- Measurement report: not available

## Tracking Lifecycle
- Status: active
- Posted: 0/0
- Public URLs logged: 0/0
- Results recorded: 0/0
- Primary gap: complete

## Posts
- No manual posts are currently waiting.
## Completion Evidence
- Each session row has a real public YouTube Community URL.
- The URL worksheet has no remaining blank public_url cells for these IDs.
- Published_Log.csv contains each session ID with a manual_distribution_id note.
- The experiment result clipboard lists the logged posts for first 24-hour measurement collection.
