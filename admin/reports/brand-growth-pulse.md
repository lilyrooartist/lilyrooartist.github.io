# Brand Growth Pulse - Lily Roo

Generated: 2026-07-06T11:04:32.432543Z

## Current Pulse
- Status: **campaign_running**
- Primary action: **Let the next automated posts run**
- Why: The active X/Facebook Analog Myth campaign is queued and ready; proof capture starts after the next window.
- Command: `python3 scripts/refresh_promo_admin.py`
- Active campaign ready: **True**
- Posting preflight ready: **True**
- Future queued posts: **60**
- Posted or measured rows: **4**
- Ready for result capture: **2**
- First-party clicks: **0** across **0** post(s)
- Next post at: `2026-07-06T10:15:00-04:00`
- Proof due at: `2026-07-06T15:21:00Z`
- Hours until next post: `3.17`
- Hours until proof due: `4.27`

## Recommendations
- **Let the next automated posts run**: The active X/Facebook Analog Myth campaign is queued and ready; proof capture starts after the next window.
  - Command: `python3 scripts/refresh_promo_admin.py`
- **Preserve the no-manual-posting lane**: Keep Analog Myth promotion on API-backed X/Facebook rows until another platform has a real automated path.
  - Command: `python3 scripts/build_posting_automation_status.py`
- **Use click data before changing creative direction**: First-party link telemetry is ready and privacy-safe; wait for real clicks before ranking tracks by response.
  - Command: `python3 scripts/capture_brand_campaign_clicks.py`
- **Optional: connect X/Meta result capture**: This is the only current measurement setup needing help; do it only after explicit approval for secret handling.
  - Command: `python3 scripts/push_github_actions_secrets.py --name FB_PAGE_ID --name META_LONG_LIVED_TOKEN --name X_ACCESS_TOKEN --name X_ACCESS_TOKEN_SECRET --name X_API_KEY --name X_API_SECRET`

## Blockers
- No active posting blockers.

## Guardrails
- No manual posting is introduced by this pulse.
- Do not solicit subscribers or use audience-target copy in public Lily Roo posts.
- Do not transmit social API secrets without explicit approval for the destination.
- Click telemetry is first-party, aggregate, and does not store IP addresses.
