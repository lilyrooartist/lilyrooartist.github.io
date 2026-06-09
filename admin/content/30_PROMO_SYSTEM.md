# Lily Roo Promo System (Backstory-driven)

## Goal
Drive social views + profile visits into YouTube subscribers.
Primary KPI: **reach 1,000 YouTube subscribers**.

## Funnel
1. **Hook** (quips/anecdotes on X, IG, FB, TikTok)
2. **Emotion** (micro-story from backstory canon)
3. **Action** (watch full song + subscribe on YouTube)
4. **Archive** (log every post + URL + performance note)

## Current Release Links and Status

Source of truth: `data/distrokid_release_status.json`

Admin promo-health snapshot: `data/promo_engine_status.json`

Refresh with:
`python3 scripts/update_promo_engine_status.py`

This snapshot combines release links, store verification history, queued posts, published posts, social execution history, platform coverage, live metric availability, and manual metric gaps into the Promo Health card on `/admin`.

It also audits source freshness so `/admin` shows when release status, the queue, promo plan, published log, manual metrics, live metrics, executor readiness, store verification history, or social execution history need refresh. Live metrics, promo plans, executor readiness, store verification history, and social execution history are expected to be refreshed daily; release status, queue, and manual metrics every 72 hours; the published log weekly.

When live APIs cannot provide a metric, the snapshot includes `pending_manual_by_platform` so `/admin` names the exact manual fields still needed for reporting.

Update known manual values without hand-editing JSON:
`python3 scripts/update_manual_social_stats.py tiktok.followers=0 spotify.release_streams=0 --refresh-admin`

Draft next queue rows from those gaps with:
`python3 scripts/generate_promo_queue_plan.py`

This writes `data/promo_queue_plan.json`, embeds it into `/admin`, and keeps the output in draft-plan mode. Plan row ids are stable by release/platform, and approved rows stay approved across refreshes when the same release/platform gap still exists.

For a full refresh where Promo Health should account for the latest draft plan, run:
`python3 scripts/update_promo_engine_status.py && python3 scripts/generate_promo_queue_plan.py && python3 scripts/update_promo_engine_status.py`

Safe apply workflow:
`python3 scripts/apply_promo_queue_plan.py`

The apply script is dry-run by default and only selects plan rows where `approved` is `yes`. To preview a specific draft without writing:
`python3 scripts/apply_promo_queue_plan.py --include-unapproved --id FP-PLAN-TWELVE-DOLLARS-X`

Approve selected rows without hand-editing JSON:
`python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-X --refresh-admin`

After approving selected rows, append them to the live queue with:
`python3 scripts/apply_promo_queue_plan.py --apply`

Approve or unapprove rows that are already in the live scheduled queue:
`python3 scripts/update_scheduled_post_approval.py FP-AUTO-259 --refresh-admin`

Then refresh the admin queue:
`python3 scripts/sync_future_posts.py`

### I Learned It All in Fifteen Seconds
- Spotify: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi
- Apple Music: https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249
- YouTube Music: https://music.youtube.com/watch?v=vK0mDIW65o4
- YouTube playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXWKTqgIs2N6dCU3BfS_9J2C
- HyperFollow fallback: https://distrokid.com/hyperfollow/lilyroo/i-learned-it-all-in-fifteen-seconds
- Use Spotify as the primary website/social CTA. Use Apple Music and YouTube Music as secondary streaming links; keep HyperFollow only when one cross-platform landing page is useful.

### Twelve Dollars
- YouTube playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n
- YouTube Music title track: https://music.youtube.com/watch?v=G2RlCwZKOsk
- Spotify, Apple Music, and HyperFollow public links are pending verification when DistroKid exposes them.
- Until store links are verified, use the YouTube playlist as the primary CTA.

### Analog Myth
- YouTube playlist: https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0
- DistroKid target release date: July 1, 2026
- Spotify, Apple Music, YouTube Music release, and HyperFollow public links are pending verification on or after July 1, 2026.
- Until store links are verified, use the YouTube playlist as the primary CTA.

### Copy Anchors
- I Learned It All in Fifteen Seconds: "live now. i learned it all in fifteen seconds and somehow still have homework."
- Twelve Dollars: "a small amount of money, a large amount of stage light."
- Analog Myth: "time broke, so Lily Roo made an album out of the pieces."

## Platform behavior
- **X:** short, sharp, quotable lines; 1-2/day.
- **Instagram:** visual + lore caption; 4-6/week.
- **Facebook:** slightly longer anecdote format; 3-4/week.
- **TikTok:** short clips + one line hook text; 4-7/week.
- **YouTube:** shorts + song anchors + explicit subscribe CTA every time.

## Posting formula (quick)
- Hook: 1 sentence from `20_QUIPS_BANK.csv`
- Context: 1 sentence from `10_ANECDOTE_BANK.md`
- CTA: "full signal on YouTube — help us hit 1,000 subs"

## Randomized artist-style cadence (not robotic)
- Use windows, not strict times:
  - Morning: 8:30–11:30
  - Afternoon: 1:00–4:30
  - Night: 7:00–11:00
- Post 0-2 times/day/platform based on energy and new assets.
- Keep one "quiet day" each week (only story/reply/comment energy).
- Use "cluster days": two posts close together if momentum is high.

## Weekly skeleton (loose, human)
- 2 heavy days (clip + lore + follow-up reply)
- 3 medium days (single post)
- 1 experiment day (new format / weird quip)
- 1 low-output day (engage comments, prep backlog)

## Conversion policy
Every 2-3 posts, include one explicit subscribe ask:
"If you're into this signal, subscribe on YouTube — we're building to 1,000."

## New song introduction pattern
For fresh song launches, use this three-post sequence by default:

1. **Post 1 — Teaser**
   - short mysterious clip
2. **Post 2 — Full Video (Release Day)**
   - upload full video to YouTube, X, and Facebook
3. **Post 3 — Alternate Teaser**
   - second short clip with a different emotional angle or visual moment

Use this as the default release arc unless the user asks for a different rollout.

## Asset storage policy
All new assets/drafts/logs live in:
`/Users/lilyroo/Library/Mobile Documents/com~apple~CloudDocs/Lily Roo`

## Next build steps
1. Expand canon to v0.2 (3 more origin paragraphs + 10 place details)
2. Add 30 more quips grouped by song era
3. Start `Published_Log.csv` immediately for all new posts
