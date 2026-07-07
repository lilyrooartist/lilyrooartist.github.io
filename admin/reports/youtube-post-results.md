# YouTube Post Results - Lily Roo

Generated: 2026-07-07T01:19:21.564383Z

## Summary
- Status: **skipped_invalid_youtube_oauth**
- Captured posts: **10**
- Fillable posts: **0**
- Fillable result fields: **0**
- Apply command: `python3 scripts/capture_youtube_post_results.py --apply-results --refresh-admin`

## Rows
- **FP-AUTO-212** row `12`
  - URL: https://youtu.be/I5BBi4TDfAM
  - Video ID: `I5BBi4TDfAM`
  - Lookup: `skipped_invalid_youtube_oauth`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube metric capture skipped 2026-07-07: OAuth refresh token is expired or revoked.
- **LR-SONG-023** row `13`
  - URL: https://youtu.be/BkkBE2pXHSY
  - Video ID: `BkkBE2pXHSY`
  - Lookup: `skipped_invalid_youtube_oauth`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube metric capture skipped 2026-07-07: OAuth refresh token is expired or revoked.
- **LR-SONG-024** row `14`
  - URL: https://youtu.be/9rmy2JhBuF4
  - Video ID: `9rmy2JhBuF4`
  - Lookup: `skipped_invalid_youtube_oauth`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube metric capture skipped 2026-07-07: OAuth refresh token is expired or revoked.
- **FP-AUTO-229** row `15`
  - URL: https://youtu.be/IahKaEXEA_0
  - Video ID: `IahKaEXEA_0`
  - Lookup: `skipped_invalid_youtube_oauth`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube metric capture skipped 2026-07-07: OAuth refresh token is expired or revoked.
- **FP-AUTO-261** row `25`
  - URL: https://youtu.be/zY8LQmuf4e4
  - Video ID: `zY8LQmuf4e4`
  - Lookup: `skipped_invalid_youtube_oauth`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube metric capture skipped 2026-07-07: OAuth refresh token is expired or revoked.
- **FP-SHORT-ANALOG-MYTH-YOUTUBE-SHORTS-CTA** row `26`
  - URL: https://youtu.be/lbT4adNE-cE
  - Video ID: `lbT4adNE-cE`
  - Lookup: `skipped_invalid_youtube_oauth`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube metric capture skipped 2026-07-07: OAuth refresh token is expired or revoked.
- **FP-SHORT-TWELVE-DOLLARS-YOUTUBE-SHORTS-CTA** row `27`
  - URL: https://youtu.be/0d0PXb_h4FY
  - Video ID: `0d0PXb_h4FY`
  - Lookup: `skipped_invalid_youtube_oauth`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube metric capture skipped 2026-07-07: OAuth refresh token is expired or revoked.
- **FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY** row `28`
  - URL: https://youtu.be/404PvtuXnqY
  - Video ID: `404PvtuXnqY`
  - Lookup: `skipped_invalid_youtube_oauth`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube metric capture skipped 2026-07-07: OAuth refresh token is expired or revoked.
- **FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY** row `29`
  - URL: https://youtu.be/0GOYOFTMAKw
  - Video ID: `0GOYOFTMAKw`
  - Lookup: `skipped_invalid_youtube_oauth`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube metric capture skipped 2026-07-07: OAuth refresh token is expired or revoked.
- **FP-PODCAST-ANALOG-MYTH-YOUTUBE** row `44`
  - URL: https://youtu.be/xX2-Xf161js
  - Video ID: `xX2-Xf161js`
  - Lookup: `skipped_invalid_youtube_oauth`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube metric capture skipped 2026-07-07: OAuth refresh token is expired or revoked.

## Guardrails
- Metrics come from public YouTube video statistics for already-published Lily Roo videos when OAuth credentials are valid.
- This skipped report does not contain OAuth credentials.
- Only views, likes, and comments are imported; shares, saves, and subscriber deltas stay blank unless another evidence source supplies them.
- Applying results goes through scripts/update_experiment_results.py so Published_Log.csv row IDs are verified.
