# YouTube Experiment Public Metrics - Lily Roo

Generated: 2026-07-27T17:43:41Z

## Summary
- Status: **blocked**
- YouTube template rows: **3**
- Importable posts: **0**
- Importable fields: **0**
- Output CSV: `data/youtube_experiment_public_metrics.csv`
- Preview: `python3 scripts/update_experiment_results.py --from-wide-csv data/youtube_experiment_public_metrics.csv --dry-run`
- Error: `Missing YouTube OAuth key(s): GOOGLE_CLIENT_ID, YOUTUBE_REFRESH_TOKEN`

## Measurements
- No importable YouTube public metrics were found.

## Guardrails
- This prefill reads public YouTube video statistics only.
- It writes a review CSV; it does not update Published_Log.csv or refresh admin state.
- The normal update_experiment_results.py dry-run/apply gate remains required before import.
- Secret values are never written to generated files.
