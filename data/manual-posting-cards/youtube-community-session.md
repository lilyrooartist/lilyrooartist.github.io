# YouTube Community Manual Posting Session

Generated: 2026-06-29T12:34:04.279052Z
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
- Status: ready_to_post_and_log
- Post: FP-AUTO-270
- Copy file: data/manual-posting-cards/fp-auto-270.txt
- Asset: assets/albums/twelve-dollars/art/01-brain-rot-youtube-thumbnail.jpg
- URL worksheet: data/manual_distribution_url_template.csv
- Worksheet update: Paste the real public URL into data/manual_distribution_url_template.csv public_url for FP-AUTO-270.
- Preview: python3 scripts/log_manual_distribution.py --id FP-AUTO-270 --url 'PUBLIC_URL'
- Apply: python3 scripts/log_manual_distribution.py --id FP-AUTO-270 --url 'PUBLIC_URL' --apply --refresh-admin
- Partial apply: python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --allow-partial --apply --refresh-admin
- Measurement trigger: after real public URL is logged

## First URL Acceleration
- Status: ready_after_first_public_url
- First post: FP-AUTO-270
- Why: Logging the first public URL immediately lets that post enter the 24-hour result-collection queue without waiting for the full batch.
- Preview: python3 scripts/log_manual_distribution.py --id FP-AUTO-270 --url 'PUBLIC_URL'
- Partial apply: python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --allow-partial --apply --refresh-admin
- Measurement report: admin/reports/experiment-result-clipboard.md

## Tracking Lifecycle
- Status: active
- Posted: 0/4
- Public URLs logged: 0/4
- Results recorded: 0/4
- Primary gap: manual_posting
- FP-AUTO-270: waiting_for_manual_post -> Publish the Community card, copy the real public post URL, then log it.
- FP-AUTO-275: waiting_for_manual_post -> Publish the Community card, copy the real public post URL, then log it.
- FP-AUTO-280: waiting_for_manual_post -> Publish the Community card, copy the real public post URL, then log it.
- FP-AUTO-285: waiting_for_manual_post -> Publish the Community card, copy the real public post URL, then log it.

## Posts
### 1. FP-AUTO-270 - Brain Rot
- Copy file: data/manual-posting-cards/fp-auto-270.txt
- Asset: assets/albums/twelve-dollars/art/01-brain-rot-youtube-thumbnail.jpg
- Preview after public URL exists: python3 scripts/log_manual_distribution.py --id FP-AUTO-270 --url 'PUBLIC_URL'
- Apply after preview passes: python3 scripts/log_manual_distribution.py --id FP-AUTO-270 --url 'PUBLIC_URL' --apply --refresh-admin

```text
The phone is melting politely. Brain Rot is tonight's Twelve Dollars signal. Watch the remastered video. Full Twelve Dollars playlist is live.

Watch Brain Rot: https://youtu.be/U7aczBSruAY | Full Twelve Dollars playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
```

Public URL:

### 2. FP-AUTO-275 - Every Pearl in Carmel
- Copy file: data/manual-posting-cards/fp-auto-275.txt
- Asset: assets/albums/twelve-dollars/art/02-every-pearl-in-carmel-youtube-thumbnail.jpg
- Preview after public URL exists: python3 scripts/log_manual_distribution.py --id FP-AUTO-275 --url 'PUBLIC_URL'
- Apply after preview passes: python3 scripts/log_manual_distribution.py --id FP-AUTO-275 --url 'PUBLIC_URL' --apply --refresh-admin

```text
Every Pearl in Carmel is the pretty souvenir that still knows what it cost. Watch the remastered video. Full Twelve Dollars playlist is live.

Watch Every Pearl in Carmel: https://youtu.be/QodRYnvTVZc | Full Twelve Dollars playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
```

Public URL:

### 3. FP-AUTO-280 - The Other One's Charging
- Copy file: data/manual-posting-cards/fp-auto-280.txt
- Asset: assets/albums/twelve-dollars/art/03-the-other-ones-charging-youtube-thumbnail.jpg
- Preview after public URL exists: python3 scripts/log_manual_distribution.py --id FP-AUTO-280 --url 'PUBLIC_URL'
- Apply after preview passes: python3 scripts/log_manual_distribution.py --id FP-AUTO-280 --url 'PUBLIC_URL' --apply --refresh-admin

```text
The Other One's Charging is domestic chaos with a battery icon. Watch the remastered video. Full Twelve Dollars playlist is live.

Watch The Other One's Charging: https://youtu.be/EprgLKHp-lE | Full Twelve Dollars playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
```

Public URL:

### 4. FP-AUTO-285 - Twelve Dollars
- Copy file: data/manual-posting-cards/fp-auto-285.txt
- Asset: assets/albums/twelve-dollars/art/04-twelve-dollars-youtube-thumbnail.jpg
- Preview after public URL exists: python3 scripts/log_manual_distribution.py --id FP-AUTO-285 --url 'PUBLIC_URL'
- Apply after preview passes: python3 scripts/log_manual_distribution.py --id FP-AUTO-285 --url 'PUBLIC_URL' --apply --refresh-admin

```text
Twelve Dollars is the stage light, the joke, and the receipt. Watch the remastered video. Full Twelve Dollars playlist is live.

Watch Twelve Dollars: https://youtu.be/G2RlCwZKOsk | Full Twelve Dollars playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
```

Public URL:

## Completion Evidence
- Each session row has a real public YouTube Community URL.
- The URL worksheet has no remaining blank public_url cells for these IDs.
- Published_Log.csv contains each session ID with a manual_distribution_id note.
- The experiment result clipboard lists the logged posts for first 24-hour measurement collection.
