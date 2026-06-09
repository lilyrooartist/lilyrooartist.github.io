# Reports Automation

## Weekly update command

```bash
python3 scripts/capture_youtube_public.py
python3 scripts/capture_spotify_release.py
python3 scripts/capture_live_metrics.py
python3 scripts/update_metrics_history.py --refresh-admin
python3 scripts/verify_pending_store_links.py --refresh-admin
LILYROO_ADMIN_PASSWORD="$LILYROO_ADMIN_PASSWORD" python3 scripts/capture_executor_readiness.py
LILYROO_ADMIN_PASSWORD="$LILYROO_ADMIN_PASSWORD" python3 scripts/capture_social_executions.py
python3 scripts/update_weekly_report.py
```

## Manual stat overrides
Edit:
`data/manual_social_stats.json`

Spotify public release metadata is captured into:
`data/spotify_release_snapshot.json`

YouTube public video-view metadata is captured into:
`data/youtube_public_snapshot.json`

Daily trend snapshots are captured into:
`data/metrics_history.json`

Executor readiness is captured into:
`data/executor_readiness_snapshot.json`

All-release store verification history is captured into:
`data/store_verification_history.json`

Social execution history is captured into:
`data/social_execution_snapshot.json`

Then re-run the update command to regenerate:
`admin/reports/weekly-social-report.md`
