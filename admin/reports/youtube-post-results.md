# YouTube Post Results - Lily Roo

Generated: 2026-07-06T16:58:34.007863Z

## Summary
- Status: **no_open_youtube_result_fields**
- Captured posts: **10**
- Fillable posts: **0**
- Fillable result fields: **0**
- Apply command: `python3 scripts/capture_youtube_post_results.py --apply-results --refresh-admin`

## Rows
- **FP-AUTO-212** row `12`
  - URL: https://youtu.be/I5BBi4TDfAM
  - Video ID: `I5BBi4TDfAM`
  - Lookup: `ok`
  - Views: `36`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube Data API public statistics 2026-07-06; video_id=I5BBi4TDfAM
- **LR-SONG-023** row `13`
  - URL: https://youtu.be/BkkBE2pXHSY
  - Video ID: `BkkBE2pXHSY`
  - Lookup: `ok`
  - Views: `55`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube Data API public statistics 2026-07-06; video_id=BkkBE2pXHSY
- **LR-SONG-024** row `14`
  - URL: https://youtu.be/9rmy2JhBuF4
  - Video ID: `9rmy2JhBuF4`
  - Lookup: `ok`
  - Views: `68`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube Data API public statistics 2026-07-06; video_id=9rmy2JhBuF4
- **FP-AUTO-229** row `15`
  - URL: https://youtu.be/IahKaEXEA_0
  - Video ID: `IahKaEXEA_0`
  - Lookup: `ok`
  - Views: `71`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube Data API public statistics 2026-07-06; video_id=IahKaEXEA_0
- **FP-AUTO-261** row `25`
  - URL: https://youtu.be/zY8LQmuf4e4
  - Video ID: `zY8LQmuf4e4`
  - Lookup: `ok`
  - Views: `2`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube Data API public statistics 2026-07-06; video_id=zY8LQmuf4e4
- **FP-SHORT-ANALOG-MYTH-YOUTUBE-SHORTS-CTA** row `26`
  - URL: https://youtu.be/lbT4adNE-cE
  - Video ID: `lbT4adNE-cE`
  - Lookup: `ok`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube Data API public statistics 2026-07-06; video_id=lbT4adNE-cE
- **FP-SHORT-TWELVE-DOLLARS-YOUTUBE-SHORTS-CTA** row `27`
  - URL: https://youtu.be/0d0PXb_h4FY
  - Video ID: `0d0PXb_h4FY`
  - Lookup: `ok`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube Data API public statistics 2026-07-06; video_id=0d0PXb_h4FY
- **FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY** row `28`
  - URL: https://youtu.be/404PvtuXnqY
  - Video ID: `404PvtuXnqY`
  - Lookup: `ok`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube Data API public statistics 2026-07-06; video_id=404PvtuXnqY
- **FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY** row `29`
  - URL: https://youtu.be/0GOYOFTMAKw
  - Video ID: `0GOYOFTMAKw`
  - Lookup: `ok`
  - Views: `0`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube Data API public statistics 2026-07-06; video_id=0GOYOFTMAKw
- **FP-PODCAST-ANALOG-MYTH-YOUTUBE** row `44`
  - URL: https://youtu.be/xX2-Xf161js
  - Video ID: `xX2-Xf161js`
  - Lookup: `ok`
  - Views: `1`; likes: `0`; comments: `0`
  - Fillable fields: `none`
  - Evidence: YouTube Data API public statistics 2026-07-06; video_id=xX2-Xf161js

## Guardrails
- Metrics come from public YouTube video statistics for already-published Lily Roo videos.
- This report does not contain OAuth credentials.
- Only views, likes, and comments are imported; shares, saves, and subscriber deltas stay blank unless another evidence source supplies them.
- Applying results goes through scripts/update_experiment_results.py so Published_Log.csv row IDs are verified.
