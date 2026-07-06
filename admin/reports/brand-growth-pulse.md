# Brand Growth Pulse - Lily Roo

Generated: 2026-07-06T18:57:46.675825Z

## Current Pulse
- Status: **first_party_click_check_ready**
- Primary action: **Refresh first-party click learning**
- Why: 4 recent posts are public and ready for a click-response check; X/Meta result metrics can join after credentials are connected.
- Command: `python3 scripts/capture_brand_campaign_clicks.py && python3 scripts/build_brand_growth_pulse.py`
- Active campaign ready: **True**
- Posting preflight ready: **True**
- Future queued posts: **58**
- Posted or measured rows: **6**
- Ready for result capture: **4**
- First-party clicks: **0** across **0** post(s)
- Next post at: `2026-07-07T10:15:00-04:00`
- Proof due at: `2026-07-07T15:21:00Z`
- Hours until next post: `19.29`
- Hours until proof due: `20.39`

## Post-Window Learning
- Status: **first_party_click_check_ready**
- Headline: **First-party click check is ready**
- Note: Public proof is saved; refresh first-party click evidence now, then add private X/Facebook result counts after analytics credentials are connected.
- Question: Which Analog Myth posts are turning attention into album, Echo Thread, or video clicks?
- Measurement due rows: **4**
- Waiting measurement rows: **2**
- Future scheduled rows: **58**
- Next learning due at: `2026-07-06T18:57:46.675825Z`
- Click refresh: `python3 scripts/capture_brand_campaign_clicks.py`
- Pulse refresh: `python3 scripts/build_brand_growth_pulse.py`
- Automation note: No manual posting is required; this loop uses automatic posts, public URL proof, first-party click checks, and optional connected X/Facebook metrics.
- Credential note: X/Facebook result counts need connected analytics credentials, but the campaign can keep posting and checking first-party click response without them.
- Rows:
  - `FP-BRAND-AM-01-13-X` (X): 13 - Ready for post-window comparison
  - `FP-BRAND-AM-01-13-FACEBOOK` (Facebook): 13 - Ready for post-window comparison
  - `FP-BRAND-AM-02-GIRLS-CAMP-X` (X): Girls Camp - Ready for post-window comparison
  - `FP-BRAND-AM-02-GIRLS-CAMP-FACEBOOK` (Facebook): Girls Camp - Ready for post-window comparison
  - `FP-BRAND-AM-03-ANALOG-MYTH-X` (X): Analog Myth - Waiting for first useful result check
  - `FP-BRAND-AM-03-ANALOG-MYTH-FACEBOOK` (Facebook): Analog Myth - Waiting for first useful result check
  - `FP-BRAND-AM-04-SPILLING-THE-TEA-X` (X): Spilling The Tea - Next queued learning input
  - `FP-BRAND-AM-04-SPILLING-THE-TEA-FACEBOOK` (Facebook): Spilling The Tea - Next queued learning input

## Recommendations
- **Refresh first-party click learning**: 4 recent posts are public and ready for a click-response check; X/Meta result metrics can join after credentials are connected.
  - Command: `python3 scripts/capture_brand_campaign_clicks.py && python3 scripts/build_brand_growth_pulse.py`
- **First-party click check is ready**: Which Analog Myth posts are turning attention into album, Echo Thread, or video clicks? No manual posting is required; this loop uses automatic posts, public URL proof, first-party click checks, and optional connected X/Facebook metrics.
  - Command: `python3 scripts/capture_brand_campaign_clicks.py && python3 scripts/build_brand_growth_pulse.py`
- **Preserve the no-manual-posting lane**: Keep Analog Myth promotion on API-backed X/Facebook rows until another platform has a real automated path.
  - Command: `python3 scripts/build_posting_automation_status.py`
- **Optional: connect X/Meta result capture**: This is the only current measurement setup needing help; do it only after explicit approval for secret handling.
  - Command: `python3 scripts/push_github_actions_secrets.py --name FB_PAGE_ID --name META_LONG_LIVED_TOKEN --name X_ACCESS_TOKEN --name X_ACCESS_TOKEN_SECRET --name X_API_KEY --name X_API_SECRET`

## Blockers
- No active posting blockers.

## Guardrails
- No manual posting is introduced by this pulse.
- Do not solicit subscribers or use audience-target copy in public Lily Roo posts.
- Do not transmit social API secrets without explicit approval for the destination.
- Click telemetry is first-party, aggregate, and does not store IP addresses.
