# YouTube Post Results - Lily Roo

Generated: 2026-07-13T09:48:45.770527Z

## Summary
- Status: **skipped_missing_secrets**
- Captured posts: **10**
- Fillable posts: **0**
- Fillable result fields: **0**
- Apply command: `python3 scripts/capture_youtube_post_results.py --apply-results --refresh-admin`
- Missing credential names: `GOOGLE_CLIENT_ID, YOUTUBE_REFRESH_TOKEN`
- Next action: Add the missing YouTube OAuth credential names locally or in GitHub Actions, then rerun capture.

## Rows
- **FP-AUTO-212** row `12`
  - URL: https://youtu.be/I5BBi4TDfAM
  - Video ID: `I5BBi4TDfAM`
  - Lookup: `skipped_missing_secrets`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube metric capture skipped 2026-07-13: missing credential name(s) GOOGLE_CLIENT_ID, YOUTUBE_REFRESH_TOKEN
- **LR-SONG-023** row `13`
  - URL: https://youtu.be/BkkBE2pXHSY
  - Video ID: `BkkBE2pXHSY`
  - Lookup: `skipped_missing_secrets`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube metric capture skipped 2026-07-13: missing credential name(s) GOOGLE_CLIENT_ID, YOUTUBE_REFRESH_TOKEN
- **LR-SONG-024** row `14`
  - URL: https://youtu.be/9rmy2JhBuF4
  - Video ID: `9rmy2JhBuF4`
  - Lookup: `skipped_missing_secrets`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube metric capture skipped 2026-07-13: missing credential name(s) GOOGLE_CLIENT_ID, YOUTUBE_REFRESH_TOKEN
- **FP-AUTO-229** row `15`
  - URL: https://youtu.be/IahKaEXEA_0
  - Video ID: `IahKaEXEA_0`
  - Lookup: `skipped_missing_secrets`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube metric capture skipped 2026-07-13: missing credential name(s) GOOGLE_CLIENT_ID, YOUTUBE_REFRESH_TOKEN
- **FP-AUTO-261** row `25`
  - URL: https://youtu.be/zY8LQmuf4e4
  - Video ID: `zY8LQmuf4e4`
  - Lookup: `skipped_missing_secrets`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube metric capture skipped 2026-07-13: missing credential name(s) GOOGLE_CLIENT_ID, YOUTUBE_REFRESH_TOKEN
- **FP-SHORT-ANALOG-MYTH-YOUTUBE-SHORTS-CTA** row `26`
  - URL: https://youtu.be/lbT4adNE-cE
  - Video ID: `lbT4adNE-cE`
  - Lookup: `skipped_missing_secrets`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube metric capture skipped 2026-07-13: missing credential name(s) GOOGLE_CLIENT_ID, YOUTUBE_REFRESH_TOKEN
- **FP-SHORT-TWELVE-DOLLARS-YOUTUBE-SHORTS-CTA** row `27`
  - URL: https://youtu.be/0d0PXb_h4FY
  - Video ID: `0d0PXb_h4FY`
  - Lookup: `skipped_missing_secrets`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube metric capture skipped 2026-07-13: missing credential name(s) GOOGLE_CLIENT_ID, YOUTUBE_REFRESH_TOKEN
- **FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY** row `28`
  - URL: https://youtu.be/404PvtuXnqY
  - Video ID: `404PvtuXnqY`
  - Lookup: `skipped_missing_secrets`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube metric capture skipped 2026-07-13: missing credential name(s) GOOGLE_CLIENT_ID, YOUTUBE_REFRESH_TOKEN
- **FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY** row `29`
  - URL: https://youtu.be/0GOYOFTMAKw
  - Video ID: `0GOYOFTMAKw`
  - Lookup: `skipped_missing_secrets`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube metric capture skipped 2026-07-13: missing credential name(s) GOOGLE_CLIENT_ID, YOUTUBE_REFRESH_TOKEN
- **FP-PODCAST-ANALOG-MYTH-YOUTUBE** row `44`
  - URL: https://youtu.be/xX2-Xf161js
  - Video ID: `xX2-Xf161js`
  - Lookup: `skipped_missing_secrets`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube metric capture skipped 2026-07-13: missing credential name(s) GOOGLE_CLIENT_ID, YOUTUBE_REFRESH_TOKEN

## Guardrails
- Metrics come from public YouTube video statistics for already-published Lily Roo videos when OAuth credentials are present.
- This skipped report does not contain OAuth credentials.
- Only views, likes, and comments are imported; shares, saves, and subscriber deltas stay blank unless another evidence source supplies them.
- Applying results goes through scripts/update_experiment_results.py so Published_Log.csv row IDs are verified.
