# Manual Posting Clipboard - Lily Roo

Generated: 2026-06-22T12:34:23.866222Z

## Summary
- Status: **ready_to_post**
- Posting surface: **YouTube Studio Community**
- Public Community URL: https://www.youtube.com/@lilyroo.artist/community
- Postable cards: **3**
- Waiting public URLs: **3**
- URL worksheet: `data/manual_distribution_url_template.csv`
- Session file: `data/manual-posting-cards/youtube-community-session.md`
- Paste text files: `data/manual-posting-cards` (3 file(s))
- Batch log preview: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv`
- Batch log apply after posting: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --apply --refresh-admin`
- Partial batch apply after first URL: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --allow-partial --apply --refresh-admin`
- Public URL reconciliation: `python3 scripts/reconcile_youtube_community_urls.py`
- Reconciliation status: **waiting_for_public_posts** (0 match(es))
- Reconciliation apply if matches exist: `not available`
- Result handoff after URL logging: `admin/reports/experiment-result-clipboard.md`
- First measurement due: **24 hours after public URL logging**
- Next action: Post each card in YouTube Community, copy the real public URL, then log it.

## Post Now
- First card: `FP-AUTO-261` (I Learned It All in Fifteen Seconds)
- Surface: https://www.youtube.com/@lilyroo.artist/community
- Copy source: `data/manual-posting-cards/fp-auto-261.txt`
- Asset source: `assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg`
- Preview URL log: `python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url 'PUBLIC_URL'`
- Apply URL log: `python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url 'PUBLIC_URL' --apply --refresh-admin`
- Result handoff: `admin/reports/experiment-result-clipboard.md`
- First measurement due: **24 hours after URL logging**
- Completion evidence:
  - The YouTube Community post is published from the listed text and asset.
  - A real public YouTube Community URL replaces PUBLIC_URL in the logging command.
  - The post appears in Published_Log.csv with this manual distribution ID.

## First Post Runbook
- Status: **ready_to_post_and_log**
- Post: `FP-AUTO-261` (I Learned It All in Fifteen Seconds)
- Surface: https://www.youtube.com/@lilyroo.artist/community
- Copy file: `data/manual-posting-cards/fp-auto-261.txt`
- Asset: `assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg`
- Public URL slot: `PUBLIC_URL`
- URL worksheet: `data/manual_distribution_url_template.csv`
- Worksheet update: Paste the real public URL into data/manual_distribution_url_template.csv public_url for FP-AUTO-261.
- Preview URL log: `python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url 'PUBLIC_URL'`
- Apply URL log: `python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url 'PUBLIC_URL' --apply --refresh-admin`
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
- First post: `FP-AUTO-261` (I Learned It All in Fifteen Seconds)
- Copy file: `data/manual-posting-cards/fp-auto-261.txt`
- Asset: `assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg`
- Preview first URL: `python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url 'PUBLIC_URL'`
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
- Postable rows: **3**
- Waiting public URLs: **3**
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
  - `1` `FP-AUTO-261` `waiting_for_post_and_public_url` first measurement `24h` copy `data/manual-posting-cards/fp-auto-261.txt` asset `assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg`
  - `2` `FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY` `waiting_for_post_and_public_url` first measurement `24h` copy `data/manual-posting-cards/fp-plan-twelve-dollars-youtube-community.txt` asset `assets/albums/twelve-dollars/art/04-twelve-dollars.jpg`
  - `3` `FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY` `waiting_for_post_and_public_url` first measurement `24h` copy `data/manual-posting-cards/fp-plan-analog-myth-youtube-community.txt` asset `assets/albums/analog-myth/art/03-analog-myth.jpg`

## Cards
### 1. I Learned It All in Fifteen Seconds - YouTube Community
- ID: `FP-AUTO-261`
- Status: `ready_for_manual_post`
- Open: https://www.youtube.com/@lilyroo.artist/community
- Paste file: `data/manual-posting-cards/fp-auto-261.txt`
- Posting bundle: copy `data/manual-posting-cards/fp-auto-261.txt`, asset `assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg`
- Paste text:
```text
New transmission: I Learned It All in Fifteen Seconds is live. Remastered cover art, same suspicious amount of feeling.

Stream: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi | Apple Music: https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249 | YouTube: https://www.youtube.com/@lilyroo.artist | YouTube Music: https://music.youtube.com/watch?v=vK0mDIW65o4
```
- Asset: https://www.lilyroo.com/assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg
- Asset evidence: `local_asset_present` assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg
- Destination links: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi, https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249, https://www.youtube.com/@lilyroo.artist, https://music.youtube.com/watch?v=vK0mDIW65o4
- Destination evidence:
  - `verified_local_evidence` https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi: HyperFollow public store link: spotify (data/hyperfollow_store_links_snapshot.json)
  - `verified_local_evidence` https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249: Apple Music public snapshot: release (data/apple_music_release_snapshot.json)
  - `verified_local_evidence` https://www.youtube.com/@lilyroo.artist: YouTube channel author URL (data/youtube_title_track_snapshot.json)
  - `verified_local_evidence` https://music.youtube.com/watch?v=vK0mDIW65o4: I Learned It All in Fifteen Seconds YouTube Music URL (data/distrokid_release_status.json); YouTube Music public snapshot: release (data/youtube_music_release_snapshot.json)
- Public URL slot: `PUBLIC_URL`
- Log preview after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url 'PUBLIC_URL'`
- Log apply after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url 'PUBLIC_URL' --apply --refresh-admin`
- Log notes: `manual_distribution_id=FP-AUTO-261; source=data/manual_distribution_packet.json`
- Bundle preview command template: `python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url 'PUBLIC_URL'`
- Bundle apply command template: `python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url 'PUBLIC_URL' --apply --refresh-admin`
- Bundle result trigger: Log the public URL, then use admin/reports/experiment-result-clipboard.md for the first 24-hour measurement.
- Result handoff: `blocked_until_public_url_logged` via `admin/reports/experiment-result-clipboard.md`
- Result handoff reason: Experiment result collection starts after the real public URL is logged in Published_Log.csv.
- First measurement due: **24 hours after URL logging**
- After posting checklist:
  - Copy the real public YouTube Community post URL.
  - Run the log preview command: python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url 'PUBLIC_URL'
  - Run the log apply command after preview passes: python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url 'PUBLIC_URL' --apply --refresh-admin
  - Refresh Admin and confirm this card moves out of the manual posting queue.
  - Open the experiment result clipboard 24 hours after URL logging for the first measurement.
### 2. Twelve Dollars - YouTube Community
- ID: `FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY`
- Status: `ready_for_manual_post`
- Open: https://www.youtube.com/@lilyroo.artist/community
- Paste file: `data/manual-posting-cards/fp-plan-twelve-dollars-youtube-community.txt`
- Posting bundle: copy `data/manual-posting-cards/fp-plan-twelve-dollars-youtube-community.txt`, asset `assets/albums/twelve-dollars/art/04-twelve-dollars.jpg`
- Paste text:
```text
Twelve Dollars is part of the Lily Roo archive now. Help us build the signal to 1,000 subscribers.

Full playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
```
- Asset: https://www.lilyroo.com/assets/albums/twelve-dollars/art/04-twelve-dollars.jpg
- Asset evidence: `local_asset_present` assets/albums/twelve-dollars/art/04-twelve-dollars.jpg
- Destination links: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
- Destination evidence:
  - `verified_local_evidence` https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n: Twelve Dollars YouTube playlist URL (data/distrokid_release_status.json); Twelve Dollars YouTube playlist URL (data/distrokid_release_status.json); Twelve Dollars verified items: 8 (data/youtube_twelve_dollars_playlist.json)
- Public URL slot: `PUBLIC_URL`
- Log preview after posting: `python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url 'PUBLIC_URL'`
- Log apply after posting: `python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url 'PUBLIC_URL' --apply --refresh-admin`
- Log notes: `manual_distribution_id=FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY; source=data/manual_distribution_packet.json`
- Bundle preview command template: `python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url 'PUBLIC_URL'`
- Bundle apply command template: `python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url 'PUBLIC_URL' --apply --refresh-admin`
- Bundle result trigger: Log the public URL, then use admin/reports/experiment-result-clipboard.md for the first 24-hour measurement.
- Result handoff: `blocked_until_public_url_logged` via `admin/reports/experiment-result-clipboard.md`
- Result handoff reason: Experiment result collection starts after the real public URL is logged in Published_Log.csv.
- First measurement due: **24 hours after URL logging**
- After posting checklist:
  - Copy the real public YouTube Community post URL.
  - Run the log preview command: python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url 'PUBLIC_URL'
  - Run the log apply command after preview passes: python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url 'PUBLIC_URL' --apply --refresh-admin
  - Refresh Admin and confirm this card moves out of the manual posting queue.
  - Open the experiment result clipboard 24 hours after URL logging for the first measurement.
### 3. Analog Myth - YouTube Community
- ID: `FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY`
- Status: `ready_for_manual_post`
- Open: https://www.youtube.com/@lilyroo.artist/community
- Paste file: `data/manual-posting-cards/fp-plan-analog-myth-youtube-community.txt`
- Posting bundle: copy `data/manual-posting-cards/fp-plan-analog-myth-youtube-community.txt`, asset `assets/albums/analog-myth/art/03-analog-myth.jpg`
- Paste text:
```text
Analog Myth is part of the Lily Roo archive now. Help us build the signal to 1,000 subscribers.

Full playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0
```
- Asset: https://www.lilyroo.com/assets/albums/analog-myth/art/03-analog-myth.jpg
- Asset evidence: `local_asset_present` assets/albums/analog-myth/art/03-analog-myth.jpg
- Destination links: https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0
- Destination evidence:
  - `verified_local_evidence` https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0: Analog Myth YouTube playlist URL (data/distrokid_release_status.json); Analog Myth YouTube playlist URL (data/distrokid_release_status.json); Analog Myth - Lily Roo verified items: 8 (data/youtube_analog_myth_playlist.json)
- Public URL slot: `PUBLIC_URL`
- Log preview after posting: `python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url 'PUBLIC_URL'`
- Log apply after posting: `python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url 'PUBLIC_URL' --apply --refresh-admin`
- Log notes: `manual_distribution_id=FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY; source=data/manual_distribution_packet.json`
- Bundle preview command template: `python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url 'PUBLIC_URL'`
- Bundle apply command template: `python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url 'PUBLIC_URL' --apply --refresh-admin`
- Bundle result trigger: Log the public URL, then use admin/reports/experiment-result-clipboard.md for the first 24-hour measurement.
- Result handoff: `blocked_until_public_url_logged` via `admin/reports/experiment-result-clipboard.md`
- Result handoff reason: Experiment result collection starts after the real public URL is logged in Published_Log.csv.
- First measurement due: **24 hours after URL logging**
- After posting checklist:
  - Copy the real public YouTube Community post URL.
  - Run the log preview command: python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url 'PUBLIC_URL'
  - Run the log apply command after preview passes: python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url 'PUBLIC_URL' --apply --refresh-admin
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
