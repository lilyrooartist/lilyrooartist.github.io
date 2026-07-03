# YouTube Experiment Public Metrics - Lily Roo

Generated: 2026-07-03T08:30:34Z

## Summary
- Status: **ready_to_import**
- YouTube template rows: **3**
- Importable posts: **3**
- Importable fields: **9**
- Output CSV: `data/youtube_experiment_public_metrics.csv`
- Preview: `python3 scripts/update_experiment_results.py --from-wide-csv data/youtube_experiment_public_metrics.csv --dry-run`
- Apply after review: `python3 scripts/update_experiment_results.py --from-wide-csv data/youtube_experiment_public_metrics.csv --apply --refresh-admin`

## Measurements
- `FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY` `404PvtuXnqY` views=0, likes=0, comments=0
- `FP-SHORT-ANALOG-MYTH-YOUTUBE-SHORTS-CTA` `lbT4adNE-cE` views=0, likes=0, comments=0
- `FP-SHORT-TWELVE-DOLLARS-YOUTUBE-SHORTS-CTA` `0d0PXb_h4FY` views=0, likes=0, comments=0

## Guardrails
- This prefill reads public YouTube video statistics only.
- It writes a review CSV; it does not update Published_Log.csv or refresh admin state.
- The normal update_experiment_results.py dry-run/apply gate remains required before import.
- Secret values are never written to generated files.
