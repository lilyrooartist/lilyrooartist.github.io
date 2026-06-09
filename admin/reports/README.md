# Reports Automation

## Weekly update command

```bash
python3 scripts/refresh_promo_admin.py
```

This safe refresh updates read-only store checks, live metrics, executor readiness, social execution history, metrics history, the weekly report, and the Admin embedded promo snapshot. It writes the run log to `data/promo_admin_refresh_run.json`.

The executor capture scripts use `LILYROO_EXECUTOR_BEARER_TOKEN` when available and fall back to `LILYROO_ADMIN_PASSWORD`.

Approve a reviewed live queue row with:
`python3 scripts/update_scheduled_post_approval.py FP-AUTO-259 --refresh-admin`

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

Safe refresh run history is captured into:
`data/promo_admin_refresh_run.json`

Then re-run the update command to regenerate:
`admin/reports/weekly-social-report.md`
