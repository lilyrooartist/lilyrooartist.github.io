# Brand Growth Preflight - Lily Roo

Generated: 2026-07-26T17:02:30.843273Z

## Summary
- Status: **needs_attention**
- Next window: **2026-07-27** at `2026-07-27T18:06:00Z`
- Expected posts: **3**
- Scheduler simulation: HTTP **200**, auth `bearer`, simulated at `2026-07-27T18:06:00Z`, due **14**, satisfied **3**, would post **3**, posted **0**, blocked **11**
- Current scheduler snapshot: checked `2026-07-26T17:02:26.729079Z`, requested `2026-07-26T17:02:26.346414Z`, due **11**, would post **0**, posted **0**, blocked **11**
- Link checks: **5 ok**, **0 failed**, **0 warning**, **0 blocking failed**
- Tracking redirects: **3 / 3 checked ok**
- Redirect targets: **3 / 3 checked**, **3 ok**, **0 warning**, **0 blocking failed**
- Current window proof due: `2026-07-27T18:06:00Z`
- Current window measurement due: `2026-07-28T18:05:00Z`

## Expected Posts
- `FP-GROWTH-RESET-08-SPILLING-THE-TEA-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE` YouTube at `2026-07-27T10:15:00-04:00`
- `FP-GROWTH-RESET-08-SPILLING-THE-TEA-ECHO-THREAD-SETUP-SONG-PAYOFF-FACEBOOK` Facebook at `2026-07-27T11:20:00-04:00`
- `FP-GROWTH-RESET-VOICE-05-X` X at `2026-07-27T14:05:00-04:00`

## Blocked Rows
- `FP-GROWTH-RESET-01-SLOW-WALK-LYRIC-PUNCH-LINE-FACEBOOK`
- `FP-GROWTH-RESET-02-SLOW-WALK-RELATABLE-SITUATION-FACEBOOK`
- `FP-GROWTH-RESET-03-SLOW-WALK-VISUAL-STORY-FACEBOOK`
- `FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE`
- `FP-GROWTH-RESET-04-SLOW-WALK-ECHO-THREAD-SETUP-SONG-PAYOFF-FACEBOOK`
- `FP-GROWTH-RESET-05-SPILLING-THE-TEA-LYRIC-PUNCH-LINE-YOUTUBE`
- `FP-GROWTH-RESET-05-SPILLING-THE-TEA-LYRIC-PUNCH-LINE-FACEBOOK`
- `FP-GROWTH-RESET-06-SPILLING-THE-TEA-RELATABLE-SITUATION-YOUTUBE`
- `FP-GROWTH-RESET-06-SPILLING-THE-TEA-RELATABLE-SITUATION-FACEBOOK`
- `FP-GROWTH-RESET-07-SPILLING-THE-TEA-VISUAL-STORY-YOUTUBE`
- `FP-GROWTH-RESET-07-SPILLING-THE-TEA-VISUAL-STORY-FACEBOOK`

## Link Checks
- **ok** `FP-GROWTH-RESET-08-SPILLING-THE-TEA-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE clip_url` 200 video/mp4
- **ok** `FP-GROWTH-RESET-08-SPILLING-THE-TEA-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE Hear the Echo Thread` 200 text/html
- **ok** `FP-GROWTH-RESET-08-SPILLING-THE-TEA-ECHO-THREAD-SETUP-SONG-PAYOFF-FACEBOOK clip_url` 200 video/mp4
- **ok** `FP-GROWTH-RESET-08-SPILLING-THE-TEA-ECHO-THREAD-SETUP-SONG-PAYOFF-FACEBOOK Hear the Echo Thread` 200 text/html
- **ok** `FP-GROWTH-RESET-VOICE-05-X Enter the album room` 200 text/html

## Redirect Target Checks
- **ok** `FP-GROWTH-RESET-08-SPILLING-THE-TEA-ECHO-THREAD-SETUP-SONG-PAYOFF-YOUTUBE Hear the Echo Thread target echo` 200 text/html
- **ok** `FP-GROWTH-RESET-08-SPILLING-THE-TEA-ECHO-THREAD-SETUP-SONG-PAYOFF-FACEBOOK Hear the Echo Thread target echo` 200 text/html
- **ok** `FP-GROWTH-RESET-VOICE-05-X Enter the album room target album` 200 text/html

## Guardrails
- Preflight is read-only; it calls the scheduler dry-run endpoint and HEAD-checks public URLs.
- It does not publish, approve, mutate, or import metrics.
- A ready preflight proves only that the next window is executable at the simulated due time.
- Rows already posted by the scheduler count as satisfied for the window; rows not yet sent must still be dry-run eligible.
- The current scheduler dry-run is reported separately so the admin does not imply future posts are due before their scheduled window.
- DistroKid HyperFollow 403/429 checks are non-blocking warnings because GitHub-hosted probes can be bot-filtered while the browser-visible public link remains the intended listening hub.
- YouTube 429 link checks are non-blocking warnings because GitHub-hosted probes can be rate-limited while the scheduler and Lily Roo-hosted links remain ready.
