# YouTube Community Manual Posting Session

Generated: 2026-06-22T09:43:31.070663Z
Surface: https://www.youtube.com/@lilyroo.artist/community
URL worksheet: data/manual_distribution_url_template.csv
Partial apply: python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --allow-partial --apply --refresh-admin

## Steps
- Open the YouTube Community surface once.
- Post each session row in sequence using its copy_source and asset_source.
- After each publish, copy the real public URL into the URL worksheet.
- Run the batch preview command; use partial apply if only some rows have public URLs.
- After logging, collect first metrics from the result handoff report.

## First URL Acceleration
- Status: ready_after_first_public_url
- First post: FP-AUTO-261
- Why: Logging the first public URL immediately lets that post enter the result-collection queue without waiting for the full batch.
- Preview: python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url PUBLIC_URL
- Partial apply: python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --allow-partial --apply --refresh-admin
- Measurement report: admin/reports/experiment-result-clipboard.md

## Posts
### 1. FP-AUTO-261 - I Learned It All in Fifteen Seconds
- Copy file: data/manual-posting-cards/fp-auto-261.txt
- Asset: assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg
- Preview after public URL exists: python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url PUBLIC_URL
- Apply after preview passes: python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url PUBLIC_URL --apply --refresh-admin

```text
New transmission: I Learned It All in Fifteen Seconds is live. Remastered cover art, same suspicious amount of feeling.

Stream: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi | Apple Music: https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249 | YouTube: https://www.youtube.com/@lilyroo.artist | YouTube Music: https://music.youtube.com/watch?v=vK0mDIW65o4
```

Public URL:

### 2. FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY - Twelve Dollars
- Copy file: data/manual-posting-cards/fp-plan-twelve-dollars-youtube-community.txt
- Asset: assets/albums/twelve-dollars/art/04-twelve-dollars.jpg
- Preview after public URL exists: python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url PUBLIC_URL
- Apply after preview passes: python3 scripts/log_manual_distribution.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --url PUBLIC_URL --apply --refresh-admin

```text
Twelve Dollars is part of the Lily Roo archive now. Help us build the signal to 1,000 subscribers.

Full playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
```

Public URL:

### 3. FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY - Analog Myth
- Copy file: data/manual-posting-cards/fp-plan-analog-myth-youtube-community.txt
- Asset: assets/albums/analog-myth/art/03-analog-myth.jpg
- Preview after public URL exists: python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url PUBLIC_URL
- Apply after preview passes: python3 scripts/log_manual_distribution.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --url PUBLIC_URL --apply --refresh-admin

```text
Analog Myth is part of the Lily Roo archive now. Help us build the signal to 1,000 subscribers.

Full playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0
```

Public URL:

## Completion Evidence
- Each session row has a real public YouTube Community URL.
- The URL worksheet has no remaining blank public_url cells for these IDs.
- Published_Log.csv contains each session ID with a manual_distribution_id note.
- The experiment result clipboard lists the logged posts for first measurement collection.
