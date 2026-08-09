# Brand Growth Preflight - Lily Roo

Generated: 2026-08-09T02:30:21.133282Z

## Summary
- Status: **needs_attention**
- Next window: **n/a** at `n/a`
- Expected posts: **0**
- Scheduler simulation: HTTP **0**, auth `bearer`, simulated at `n/a`, due **0**, satisfied **0**, would post **0**, posted **0**, blocked **0**
- Current scheduler snapshot: checked `2026-08-09T02:30:13.356643Z`, requested `2026-08-09T02:30:12.738842Z`, due **16**, would post **0**, posted **0**, blocked **16**
- Link checks: **0 ok**, **0 failed**, **0 warning**, **0 blocking failed**
- Tracking redirects: **0 / 0 checked ok**
- Redirect targets: **0 / 0 checked**, **0 ok**, **0 warning**, **0 blocking failed**
- Current window proof due: `n/a`
- Current window measurement due: `n/a`

## Expected Posts

## Link Checks

## Redirect Target Checks

## Guardrails
- Preflight is read-only; it calls the scheduler dry-run endpoint and HEAD-checks public URLs.
- It does not publish, approve, mutate, or import metrics.
- A ready preflight proves only that the next window is executable at the simulated due time.
- Rows already posted by the scheduler count as satisfied for the window; rows not yet sent must still be dry-run eligible.
- The current scheduler dry-run is reported separately so the admin does not imply future posts are due before their scheduled window.
- DistroKid HyperFollow 403/429 checks are non-blocking warnings because GitHub-hosted probes can be bot-filtered while the browser-visible public link remains the intended listening hub.
- YouTube 429 link checks are non-blocking warnings because GitHub-hosted probes can be rate-limited while the scheduler and Lily Roo-hosted links remain ready.
