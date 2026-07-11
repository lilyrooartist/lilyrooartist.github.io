# Brand Growth Pulse - Lily Roo

Generated: 2026-07-11T08:15:21.378581Z

## Current Pulse
- Status: **learn_from_clicks**
- Primary action: **Review first-party click response**
- Why: Fresh click evidence is available for recent public posts, so the next content pass can favor the strongest tracks and destinations.
- Command: `python3 scripts/capture_brand_campaign_clicks.py && python3 scripts/build_brand_growth_pulse.py`
- Active campaign ready: **True**
- Posting preflight ready: **True**
- Future queued posts: **34**
- Posted or measured rows: **14**
- Ready for result capture: **12**
- First-party clicks: **3** across **1** post(s)
- Click snapshot: `2026-07-11T08:15:18.098735Z` (covers current due posts)
- Next post at: `2026-07-11T10:15:00-04:00`
- Proof due at: `2026-07-11T15:21:00Z`
- Hours until next post: `5.99`
- Hours until proof due: `7.09`

## Post-Window Learning
- Status: **learn_from_clicks**
- Headline: **Click response is ready to review**
- Note: Fresh first-party click evidence is saved; use it to shape the next copy, while private X/Facebook result counts can join after analytics credentials are connected.
- Question: Which Analog Myth posts are turning attention into album, Echo Thread, or video clicks?
- Measurement due rows: **12**
- Waiting measurement rows: **2**
- Future scheduled rows: **34**
- Next learning due at: `2026-07-11T14:15:30.211000Z`
- Click refresh: `python3 scripts/capture_brand_campaign_clicks.py`
- Pulse refresh: `python3 scripts/build_brand_growth_pulse.py`
- Automation note: No manual posting is required; this loop uses automatic native-video posts, public URL proof, first-party click checks, and connected platform metrics when available.
- Credential note: X/Facebook result counts need connected analytics credentials, but the campaign can keep posting and checking first-party click response without them.
- Rows:
  - `FP-BRAND-AM-01-13-X` (X): 13 - Ready for post-window comparison
  - `FP-BRAND-AM-01-13-FACEBOOK` (Facebook): 13 - Ready for post-window comparison
  - `FP-BRAND-AM-02-GIRLS-CAMP-X` (X): Girls Camp - Ready for post-window comparison
  - `FP-BRAND-AM-02-GIRLS-CAMP-FACEBOOK` (Facebook): Girls Camp - Ready for post-window comparison
  - `FP-BRAND-AM-07-SLOW-WALK-X` (X): Slow Walk - Waiting for first useful result check
  - `FP-BRAND-AM-07-SLOW-WALK-FACEBOOK` (Facebook): Slow Walk - Waiting for first useful result check
  - `FP-BRAND-AM-08-THE-POWER-OF-LIGHT-X` (X): The Power Of Light - Next queued learning input
  - `FP-BRAND-AM-08-THE-POWER-OF-LIGHT-FACEBOOK` (Facebook): The Power Of Light - Next queued learning input

## Recommendations
- **Review first-party click response**: Fresh click evidence is available for recent public posts, so the next content pass can favor the strongest tracks and destinations.
  - Command: `python3 scripts/capture_brand_campaign_clicks.py && python3 scripts/build_brand_growth_pulse.py`
- **Click response is ready to review**: Which Analog Myth posts are turning attention into album, Echo Thread, or video clicks? No manual posting is required; this loop uses automatic native-video posts, public URL proof, first-party click checks, and connected platform metrics when available.
  - Command: `python3 scripts/capture_brand_campaign_clicks.py && python3 scripts/build_brand_growth_pulse.py`
- **Preserve the no-manual-posting lane**: Keep only API-backed platforms active; unsupported surfaces stay unapproved until their automated path is verified.
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
