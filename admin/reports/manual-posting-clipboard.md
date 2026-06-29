# Manual Posting Clipboard - Lily Roo

Generated: 2026-06-29T12:34:04.279052Z

## Summary
- Status: **ready_to_post**
- Posting surface: **YouTube Studio Community**
- Public Community URL: https://www.youtube.com/@lilyroo.artist/community
- Postable cards: **4**
- Waiting public URLs: **4**
- URL worksheet: `data/manual_distribution_url_template.csv`
- Session file: `data/manual-posting-cards/youtube-community-session.md`
- Paste text files: `data/manual-posting-cards` (4 file(s))
- Batch log preview: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv`
- Batch log apply after posting: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --apply --refresh-admin`
- Partial batch apply after first URL: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --allow-partial --apply --refresh-admin`
- Public URL reconciliation: `python3 scripts/reconcile_youtube_community_urls.py`
- Reconciliation status: **waiting_for_public_posts** (0 match(es))
- Reconciliation apply if matches exist: `not available`
- Result handoff after URL logging: `admin/reports/experiment-result-clipboard.md`
- First measurement due: **24 hours after public URL logging**
- Next action: Post each card in YouTube Community, copy the real public URL, then log it.

## Tracking Lifecycle
- Status: **active**
- Posted: **0/4**
- Public URLs logged: **0/4**
- Results recorded: **0/4**
- Ready for measurement: **0**
- Primary gap: `manual_posting`
- Guardrail: Do not advance a lifecycle stage without the listed completion evidence.
- Lifecycle rows:
  - `FP-AUTO-270` `waiting_for_manual_post` posted `False` logged `False` measured `False` due `after URL logging`
    - Next: Publish the Community card, copy the real public post URL, then log it.
  - `FP-AUTO-275` `waiting_for_manual_post` posted `False` logged `False` measured `False` due `after URL logging`
    - Next: Publish the Community card, copy the real public post URL, then log it.
  - `FP-AUTO-280` `waiting_for_manual_post` posted `False` logged `False` measured `False` due `after URL logging`
    - Next: Publish the Community card, copy the real public post URL, then log it.
  - `FP-AUTO-285` `waiting_for_manual_post` posted `False` logged `False` measured `False` due `after URL logging`
    - Next: Publish the Community card, copy the real public post URL, then log it.

## Post Now
- First card: `FP-AUTO-270` (Brain Rot)
- Surface: https://www.youtube.com/@lilyroo.artist/community
- Copy source: `data/manual-posting-cards/fp-auto-270.txt`
- Asset source: `assets/albums/twelve-dollars/art/01-brain-rot-youtube-thumbnail.jpg`
- Preview URL log: `python3 scripts/log_manual_distribution.py --id FP-AUTO-270 --url 'PUBLIC_URL'`
- Apply URL log: `python3 scripts/log_manual_distribution.py --id FP-AUTO-270 --url 'PUBLIC_URL' --apply --refresh-admin`
- Result handoff: `admin/reports/experiment-result-clipboard.md`
- First measurement due: **24 hours after URL logging**
- Completion evidence:
  - The YouTube Community post is published from the listed text and asset.
  - A real public YouTube Community URL replaces PUBLIC_URL in the logging command.
  - The post appears in Published_Log.csv with this manual distribution ID.

## First Post Runbook
- Status: **ready_to_post_and_log**
- Post: `FP-AUTO-270` (Brain Rot)
- Surface: https://www.youtube.com/@lilyroo.artist/community
- Copy file: `data/manual-posting-cards/fp-auto-270.txt`
- Asset: `assets/albums/twelve-dollars/art/01-brain-rot-youtube-thumbnail.jpg`
- Public URL slot: `PUBLIC_URL`
- URL worksheet: `data/manual_distribution_url_template.csv`
- Worksheet update: Paste the real public URL into data/manual_distribution_url_template.csv public_url for FP-AUTO-270.
- Preview URL log: `python3 scripts/log_manual_distribution.py --id FP-AUTO-270 --url 'PUBLIC_URL'`
- Apply URL log: `python3 scripts/log_manual_distribution.py --id FP-AUTO-270 --url 'PUBLIC_URL' --apply --refresh-admin`
- Partial batch apply: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --allow-partial --apply --refresh-admin`
- Result handoff: `admin/reports/experiment-result-clipboard.md`
- First measurement trigger: **after real public URL is logged**
- First measurement due: **24 hours after URL logging**
- Guardrail: Do not run an apply command with PUBLIC_URL, a blank URL, or a private/non-public post URL.
- Checklist:
  - Open the YouTube Community surface.
  - Paste the copy exactly from copy_source.
  - Attach the listed asset_source or asset_url.
  - Publish the Community post manually.
  - Copy the real public YouTube Community post URL.
  - Run the preview command with the real URL.
  - Run the apply command only after preview confirms the real URL.
  - Confirm Published_Log.csv contains this manual distribution ID.
  - Collect first visible metrics 24 hours after the public URL is logged.
- Completion evidence:
  - A real public YouTube Community post URL exists.
  - The URL has replaced PUBLIC_URL in the preview/apply command or worksheet.
  - Published_Log.csv contains this manual_distribution_id.
  - The experiment result clipboard lists this post for its 24-hour measurement.

## First URL Acceleration
- Status: **ready_after_first_public_url**
- First post: `FP-AUTO-270` (Brain Rot)
- Copy file: `data/manual-posting-cards/fp-auto-270.txt`
- Asset: `assets/albums/twelve-dollars/art/01-brain-rot-youtube-thumbnail.jpg`
- Preview first URL: `python3 scripts/log_manual_distribution.py --id FP-AUTO-270 --url 'PUBLIC_URL'`
- Apply first URL with partial batch: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --allow-partial --apply --refresh-admin`
- Measurement report: `admin/reports/experiment-result-clipboard.md`
- Measurement preview: `python3 scripts/update_experiment_results.py --from-wide-csv data/experiment_result_entry_wide_template.csv --dry-run`
- First measurement due: **24 hours after URL logging**
- Why: Logging the first public URL immediately lets that post enter the 24-hour result-collection queue without waiting for the full batch.
- Guardrail: Use only a real public YouTube Community post URL; never apply PUBLIC_URL or blank worksheet rows.

## Session Manifest
- Status: **ready_to_post**
- Session: **YouTube Community manual posting batch**
- Surface: https://www.youtube.com/@lilyroo.artist/community
- Postable rows: **4**
- Waiting public URLs: **4**
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
- Session rows:
  - `1` `FP-AUTO-270` `waiting_for_post_and_public_url` first measurement `24h` copy `data/manual-posting-cards/fp-auto-270.txt` asset `assets/albums/twelve-dollars/art/01-brain-rot-youtube-thumbnail.jpg`
  - `2` `FP-AUTO-275` `waiting_for_post_and_public_url` first measurement `24h` copy `data/manual-posting-cards/fp-auto-275.txt` asset `assets/albums/twelve-dollars/art/02-every-pearl-in-carmel-youtube-thumbnail.jpg`
  - `3` `FP-AUTO-280` `waiting_for_post_and_public_url` first measurement `24h` copy `data/manual-posting-cards/fp-auto-280.txt` asset `assets/albums/twelve-dollars/art/03-the-other-ones-charging-youtube-thumbnail.jpg`
  - `4` `FP-AUTO-285` `waiting_for_post_and_public_url` first measurement `24h` copy `data/manual-posting-cards/fp-auto-285.txt` asset `assets/albums/twelve-dollars/art/04-twelve-dollars-youtube-thumbnail.jpg`

## Cards
### 1. Brain Rot - YouTube Community
- ID: `FP-AUTO-270`
- Status: `ready_for_manual_post`
- Open: https://www.youtube.com/@lilyroo.artist/community
- Paste file: `data/manual-posting-cards/fp-auto-270.txt`
- Posting bundle: copy `data/manual-posting-cards/fp-auto-270.txt`, asset `assets/albums/twelve-dollars/art/01-brain-rot-youtube-thumbnail.jpg`
- Paste text:
```text
The phone is melting politely. Brain Rot is tonight's Twelve Dollars signal. Watch the remastered video. Full Twelve Dollars playlist is live.

Watch Brain Rot: https://youtu.be/U7aczBSruAY | Full Twelve Dollars playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
```
- Asset: https://www.lilyroo.com/assets/albums/twelve-dollars/art/01-brain-rot-youtube-thumbnail.jpg
- Asset evidence: `local_asset_present` assets/albums/twelve-dollars/art/01-brain-rot-youtube-thumbnail.jpg
- Destination links: https://youtu.be/U7aczBSruAY, https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
- Destination evidence:
  - `needs_manual_review` https://youtu.be/U7aczBSruAY: no local evidence
  - `verified_local_evidence` https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n: Twelve Dollars YouTube playlist URL (data/distrokid_release_status.json); Twelve Dollars YouTube playlist URL (data/distrokid_release_status.json); Twelve Dollars verified items: 8 (data/youtube_twelve_dollars_playlist.json)
- Public URL slot: `PUBLIC_URL`
- Log preview after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-270 --url 'PUBLIC_URL'`
- Log apply after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-270 --url 'PUBLIC_URL' --apply --refresh-admin`
- Log notes: `manual_distribution_id=FP-AUTO-270; source=data/manual_distribution_packet.json`
- Bundle preview command template: `python3 scripts/log_manual_distribution.py --id FP-AUTO-270 --url 'PUBLIC_URL'`
- Bundle apply command template: `python3 scripts/log_manual_distribution.py --id FP-AUTO-270 --url 'PUBLIC_URL' --apply --refresh-admin`
- Bundle result trigger: Log the public URL, then use admin/reports/experiment-result-clipboard.md for the first 24-hour measurement.
- Result handoff: `blocked_until_public_url_logged` via `admin/reports/experiment-result-clipboard.md`
- Result handoff reason: Experiment result collection starts after the real public URL is logged in Published_Log.csv.
- First measurement due: **24 hours after URL logging**
- After posting checklist:
  - Copy the real public YouTube Community post URL.
  - Run the log preview command: python3 scripts/log_manual_distribution.py --id FP-AUTO-270 --url 'PUBLIC_URL'
  - Run the log apply command after preview passes: python3 scripts/log_manual_distribution.py --id FP-AUTO-270 --url 'PUBLIC_URL' --apply --refresh-admin
  - Refresh Admin and confirm this card moves out of the manual posting queue.
  - Open the experiment result clipboard 24 hours after URL logging for the first measurement.
### 2. Every Pearl in Carmel - YouTube Community
- ID: `FP-AUTO-275`
- Status: `ready_for_manual_post`
- Open: https://www.youtube.com/@lilyroo.artist/community
- Paste file: `data/manual-posting-cards/fp-auto-275.txt`
- Posting bundle: copy `data/manual-posting-cards/fp-auto-275.txt`, asset `assets/albums/twelve-dollars/art/02-every-pearl-in-carmel-youtube-thumbnail.jpg`
- Paste text:
```text
Every Pearl in Carmel is the pretty souvenir that still knows what it cost. Watch the remastered video. Full Twelve Dollars playlist is live.

Watch Every Pearl in Carmel: https://youtu.be/QodRYnvTVZc | Full Twelve Dollars playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
```
- Asset: https://www.lilyroo.com/assets/albums/twelve-dollars/art/02-every-pearl-in-carmel-youtube-thumbnail.jpg
- Asset evidence: `local_asset_present` assets/albums/twelve-dollars/art/02-every-pearl-in-carmel-youtube-thumbnail.jpg
- Destination links: https://youtu.be/QodRYnvTVZc, https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
- Destination evidence:
  - `needs_manual_review` https://youtu.be/QodRYnvTVZc: no local evidence
  - `verified_local_evidence` https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n: Twelve Dollars YouTube playlist URL (data/distrokid_release_status.json); Twelve Dollars YouTube playlist URL (data/distrokid_release_status.json); Twelve Dollars verified items: 8 (data/youtube_twelve_dollars_playlist.json)
- Public URL slot: `PUBLIC_URL`
- Log preview after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-275 --url 'PUBLIC_URL'`
- Log apply after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-275 --url 'PUBLIC_URL' --apply --refresh-admin`
- Log notes: `manual_distribution_id=FP-AUTO-275; source=data/manual_distribution_packet.json`
- Bundle preview command template: `python3 scripts/log_manual_distribution.py --id FP-AUTO-275 --url 'PUBLIC_URL'`
- Bundle apply command template: `python3 scripts/log_manual_distribution.py --id FP-AUTO-275 --url 'PUBLIC_URL' --apply --refresh-admin`
- Bundle result trigger: Log the public URL, then use admin/reports/experiment-result-clipboard.md for the first 24-hour measurement.
- Result handoff: `blocked_until_public_url_logged` via `admin/reports/experiment-result-clipboard.md`
- Result handoff reason: Experiment result collection starts after the real public URL is logged in Published_Log.csv.
- First measurement due: **24 hours after URL logging**
- After posting checklist:
  - Copy the real public YouTube Community post URL.
  - Run the log preview command: python3 scripts/log_manual_distribution.py --id FP-AUTO-275 --url 'PUBLIC_URL'
  - Run the log apply command after preview passes: python3 scripts/log_manual_distribution.py --id FP-AUTO-275 --url 'PUBLIC_URL' --apply --refresh-admin
  - Refresh Admin and confirm this card moves out of the manual posting queue.
  - Open the experiment result clipboard 24 hours after URL logging for the first measurement.
### 3. The Other One's Charging - YouTube Community
- ID: `FP-AUTO-280`
- Status: `ready_for_manual_post`
- Open: https://www.youtube.com/@lilyroo.artist/community
- Paste file: `data/manual-posting-cards/fp-auto-280.txt`
- Posting bundle: copy `data/manual-posting-cards/fp-auto-280.txt`, asset `assets/albums/twelve-dollars/art/03-the-other-ones-charging-youtube-thumbnail.jpg`
- Paste text:
```text
The Other One's Charging is domestic chaos with a battery icon. Watch the remastered video. Full Twelve Dollars playlist is live.

Watch The Other One's Charging: https://youtu.be/EprgLKHp-lE | Full Twelve Dollars playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
```
- Asset: https://www.lilyroo.com/assets/albums/twelve-dollars/art/03-the-other-ones-charging-youtube-thumbnail.jpg
- Asset evidence: `local_asset_present` assets/albums/twelve-dollars/art/03-the-other-ones-charging-youtube-thumbnail.jpg
- Destination links: https://youtu.be/EprgLKHp-lE, https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
- Destination evidence:
  - `needs_manual_review` https://youtu.be/EprgLKHp-lE: no local evidence
  - `verified_local_evidence` https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n: Twelve Dollars YouTube playlist URL (data/distrokid_release_status.json); Twelve Dollars YouTube playlist URL (data/distrokid_release_status.json); Twelve Dollars verified items: 8 (data/youtube_twelve_dollars_playlist.json)
- Public URL slot: `PUBLIC_URL`
- Log preview after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-280 --url 'PUBLIC_URL'`
- Log apply after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-280 --url 'PUBLIC_URL' --apply --refresh-admin`
- Log notes: `manual_distribution_id=FP-AUTO-280; source=data/manual_distribution_packet.json`
- Bundle preview command template: `python3 scripts/log_manual_distribution.py --id FP-AUTO-280 --url 'PUBLIC_URL'`
- Bundle apply command template: `python3 scripts/log_manual_distribution.py --id FP-AUTO-280 --url 'PUBLIC_URL' --apply --refresh-admin`
- Bundle result trigger: Log the public URL, then use admin/reports/experiment-result-clipboard.md for the first 24-hour measurement.
- Result handoff: `blocked_until_public_url_logged` via `admin/reports/experiment-result-clipboard.md`
- Result handoff reason: Experiment result collection starts after the real public URL is logged in Published_Log.csv.
- First measurement due: **24 hours after URL logging**
- After posting checklist:
  - Copy the real public YouTube Community post URL.
  - Run the log preview command: python3 scripts/log_manual_distribution.py --id FP-AUTO-280 --url 'PUBLIC_URL'
  - Run the log apply command after preview passes: python3 scripts/log_manual_distribution.py --id FP-AUTO-280 --url 'PUBLIC_URL' --apply --refresh-admin
  - Refresh Admin and confirm this card moves out of the manual posting queue.
  - Open the experiment result clipboard 24 hours after URL logging for the first measurement.
### 4. Twelve Dollars - YouTube Community
- ID: `FP-AUTO-285`
- Status: `ready_for_manual_post`
- Open: https://www.youtube.com/@lilyroo.artist/community
- Paste file: `data/manual-posting-cards/fp-auto-285.txt`
- Posting bundle: copy `data/manual-posting-cards/fp-auto-285.txt`, asset `assets/albums/twelve-dollars/art/04-twelve-dollars-youtube-thumbnail.jpg`
- Paste text:
```text
Twelve Dollars is the stage light, the joke, and the receipt. Watch the remastered video. Full Twelve Dollars playlist is live.

Watch Twelve Dollars: https://youtu.be/G2RlCwZKOsk | Full Twelve Dollars playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
```
- Asset: https://www.lilyroo.com/assets/albums/twelve-dollars/art/04-twelve-dollars-youtube-thumbnail.jpg
- Asset evidence: `local_asset_present` assets/albums/twelve-dollars/art/04-twelve-dollars-youtube-thumbnail.jpg
- Destination links: https://youtu.be/G2RlCwZKOsk, https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
- Destination evidence:
  - `needs_manual_review` https://youtu.be/G2RlCwZKOsk: no local evidence
  - `verified_local_evidence` https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n: Twelve Dollars YouTube playlist URL (data/distrokid_release_status.json); Twelve Dollars YouTube playlist URL (data/distrokid_release_status.json); Twelve Dollars verified items: 8 (data/youtube_twelve_dollars_playlist.json)
- Public URL slot: `PUBLIC_URL`
- Log preview after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-285 --url 'PUBLIC_URL'`
- Log apply after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-285 --url 'PUBLIC_URL' --apply --refresh-admin`
- Log notes: `manual_distribution_id=FP-AUTO-285; source=data/manual_distribution_packet.json`
- Bundle preview command template: `python3 scripts/log_manual_distribution.py --id FP-AUTO-285 --url 'PUBLIC_URL'`
- Bundle apply command template: `python3 scripts/log_manual_distribution.py --id FP-AUTO-285 --url 'PUBLIC_URL' --apply --refresh-admin`
- Bundle result trigger: Log the public URL, then use admin/reports/experiment-result-clipboard.md for the first 24-hour measurement.
- Result handoff: `blocked_until_public_url_logged` via `admin/reports/experiment-result-clipboard.md`
- Result handoff reason: Experiment result collection starts after the real public URL is logged in Published_Log.csv.
- First measurement due: **24 hours after URL logging**
- After posting checklist:
  - Copy the real public YouTube Community post URL.
  - Run the log preview command: python3 scripts/log_manual_distribution.py --id FP-AUTO-285 --url 'PUBLIC_URL'
  - Run the log apply command after preview passes: python3 scripts/log_manual_distribution.py --id FP-AUTO-285 --url 'PUBLIC_URL' --apply --refresh-admin
  - Refresh Admin and confirm this card moves out of the manual posting queue.
  - Open the experiment result clipboard 24 hours after URL logging for the first measurement.

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
