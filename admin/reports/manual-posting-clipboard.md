# Manual Posting Clipboard - Lily Roo

Generated: 2026-06-29T21:20:06.190324Z

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
- Status: **not_active**
- Session: **No manual posting session**
- Surface: not set
- Postable rows: **0**
- Waiting public URLs: **0**
- Logged rows: **0**
- URL worksheet: `not available`
- Batch preview: `not available`
- Batch apply: `not available`
- Partial apply: `not available`
- URL reconciliation: `not available`
- Result handoff: `not available`
- First measurement due: **24 hours after URL logging**
- Guardrail: No manual posting rows are active.

- Session rows: none; API automation has replaced the manual posting lane.

## Cards
- No approved manual posts are currently waiting.
- Posting bundle: not applicable while the manual lane is empty.
- Paste text: not applicable while the manual lane is empty.
- Log preview after posting: not applicable while the manual lane is empty.
- Bundle result trigger: not applicable while the manual lane is empty.
- After posting checklist: no manual posting checklist is active.

## Operator Steps

## Guardrails
- This clipboard does not approve, schedule, publish, or log posts.
- Do not use PUBLIC_URL in an apply command.
- Use --allow-partial only after at least one worksheet row has a real public_url; blank rows remain waiting.
- Do not mark a row complete until a real public YouTube Community URL is logged.
