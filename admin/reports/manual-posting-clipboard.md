# Manual Posting Clipboard - Lily Roo

Generated: 2026-06-23T07:12:16.617557Z

## Summary
- Status: **empty**
- Posting surface: **YouTube Studio Community**
- Public Community URL: https://www.youtube.com/@lilyroo.artist/community
- Postable cards: **0**
- Waiting public URLs: **0**
- URL worksheet: `data/manual_distribution_url_template.csv`
- Session file: `data/manual-posting-cards/youtube-community-session.md`
- Paste text files: `data/manual-posting-cards` (0 file(s))
- Batch log preview: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv`
- Batch log apply after posting: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --apply --refresh-admin`
- Partial batch apply after first URL: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --allow-partial --apply --refresh-admin`
- Public URL reconciliation: `python3 scripts/reconcile_youtube_community_urls.py`
- Reconciliation status: **waiting_for_public_posts** (0 match(es))
- Reconciliation apply if matches exist: `not available`
- Result handoff after URL logging: `admin/reports/experiment-result-clipboard.md`
- First measurement due: **24 hours after public URL logging**
- Next action: No approved manual posts are currently waiting.

## Tracking Lifecycle
- Status: **active**
- Posted: **0/0**
- Public URLs logged: **0/0**
- Results recorded: **0/0**
- Ready for measurement: **0**
- Primary gap: `complete`
- Guardrail: Do not advance a lifecycle stage without the listed completion evidence.

## Post Now
- No manual post is waiting; API automation has replaced the manual posting lane.

## First Post Runbook
- Status: **clear**
- Post: `not available` (unknown release)
- Surface: not set
- Copy file: `not available`
- Asset: `not available`
- Public URL slot: `PUBLIC_URL`
- URL worksheet: `not available`
- Worksheet update: not available
- Preview URL log: `not available`
- Apply URL log: `not available`
- Partial batch apply: `not available`
- Result handoff: `not available`
- First measurement trigger: **after URL logging**
- First measurement due: **24 hours after URL logging**
- Guardrail: No placeholder URLs are accepted.

## First URL Acceleration
- Status: **clear**
- First post: `not available` (unknown release)
- Copy file: `not available`
- Asset: `not available`
- Preview first URL: `not available`
- Apply first URL with partial batch: `not available`
- Measurement report: `not available`
- Measurement preview: `not available`
- First measurement due: **24 hours after URL logging**
- Why: not available
- Guardrail: No placeholder URLs are accepted.

## Session Manifest
- Status: **complete**
- Session: **YouTube Community manual posting batch**
- Surface: https://www.youtube.com/@lilyroo.artist/community
- Postable rows: **0**
- Waiting public URLs: **0**
- Logged rows: **0**
- URL worksheet: `data/manual_distribution_url_template.csv`
- Batch preview: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv`
- Batch apply: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --apply --refresh-admin`
- Partial apply: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --allow-partial --apply --refresh-admin`
- URL reconciliation: `python3 scripts/reconcile_youtube_community_urls.py`
- Result handoff: `admin/reports/experiment-result-clipboard.md`
- First measurement due: **24 hours after URL logging**
- Guardrail: Do not mark the session complete until every row has a real public URL logged.

- Posting sequence:
  - Open the YouTube Community surface once.
  - Post each session row in sequence using its copy_source and asset_source.
  - After each publish, copy the real public URL into the URL worksheet.
  - Run the batch preview command; use partial apply if only some rows have public URLs.
  - After logging, collect the first 24-hour metrics from the result handoff report.
- Completion evidence:
  - Each session row has a real public YouTube Community URL.
  - The URL worksheet has no remaining blank public_url cells for these IDs.
  - Published_Log.csv contains each session ID with a manual_distribution_id note.
  - The experiment result clipboard lists the logged posts for first 24-hour measurement collection.
- Session rows: none; API automation has replaced the manual posting lane.

## Cards
- No approved manual posts are currently waiting.
- Posting bundle: not applicable while the manual lane is empty.
- Paste text: not applicable while the manual lane is empty.
- Log preview after posting: not applicable while the manual lane is empty.
- Bundle result trigger: not applicable while the manual lane is empty.
- After posting checklist: no manual posting checklist is active.

## Operator Steps
- Open the YouTube Community surface.
- For each card, paste the text exactly as shown.
- Attach the listed asset URL or download/open the local asset path if needed.
- Publish manually in YouTube Studio Community.
- Copy the real public post URL.
- Use the first-post runbook to preview and apply the first real public URL.
- Run the preview logging command with the real URL, then run the apply command.
- After the first public URL exists, use the first-url acceleration command so that post can enter result collection immediately.
- Or rerun the public URL reconciliation command after posting to auto-detect confident public URLs.
- If only one public URL is ready, use the partial batch apply command so that post can start accumulating measurable evidence immediately.

## Guardrails
- This clipboard does not approve, schedule, publish, or log posts.
- Do not use PUBLIC_URL in an apply command.
- Use --allow-partial only after at least one worksheet row has a real public_url; blank rows remain waiting.
- Do not mark a row complete until a real public YouTube Community URL is logged.
