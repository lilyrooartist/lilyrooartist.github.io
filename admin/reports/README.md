# Reports Automation

## Weekly update command

```bash
python3 scripts/capture_spotify_release.py
python3 scripts/capture_live_metrics.py
python3 scripts/update_weekly_report.py
```

## Manual stat overrides
Edit:
`data/manual_social_stats.json`

Spotify public release metadata is captured into:
`data/spotify_release_snapshot.json`

Then re-run the update command to regenerate:
`admin/reports/weekly-social-report.md`
