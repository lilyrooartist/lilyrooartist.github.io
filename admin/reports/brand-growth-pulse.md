# Brand Growth Pulse - Lily Roo

Generated: 2026-07-07T18:01:02.225346Z

## Current Pulse
- Status: **campaign_running**
- Primary action: **Let the next automated posts run**
- Why: The active X/Facebook Analog Myth campaign is queued and ready; proof capture starts after the next window.
- Command: `python3 scripts/refresh_promo_admin.py`
- Active campaign ready: **True**
- Posting preflight ready: **True**
- Future queued posts: **56**
- Posted or measured rows: **8**
- Ready for result capture: **6**
- First-party clicks: **0** across **0** post(s)
- Click snapshot: `2026-07-07T18:00:58.414596Z` (covers current due posts)
- Next post at: `2026-07-08T10:15:00-04:00`
- Proof due at: `2026-07-08T15:21:00Z`
- Hours until next post: `20.23`
- Hours until proof due: `21.33`

## Post-Window Learning
- Status: **first_party_click_checked**
- Headline: **First-party clicks checked**
- Note: Fresh click evidence covers 6 public posts. No first-party clicks are recorded yet, so keep the next automatic posts moving and check again after the next result window.
- Question: Which Analog Myth posts are turning attention into album, Echo Thread, or video clicks?
- Measurement due rows: **6**
- Waiting measurement rows: **2**
- Future scheduled rows: **56**
- Next learning due at: `2026-07-08T14:15:31.050000Z`
- Click refresh: `python3 scripts/capture_brand_campaign_clicks.py`
- Pulse refresh: `python3 scripts/build_brand_growth_pulse.py`
- Automation note: No manual posting is required; this loop uses automatic posts, public URL proof, first-party click checks, and optional connected X/Facebook metrics.
- Credential note: X/Facebook result counts need connected analytics credentials, but the campaign can keep posting and checking first-party click response without them.
- Rows:
  - `FP-BRAND-AM-01-13-X` (X): 13 - Ready for post-window comparison
  - `FP-BRAND-AM-01-13-FACEBOOK` (Facebook): 13 - Ready for post-window comparison
  - `FP-BRAND-AM-02-GIRLS-CAMP-X` (X): Girls Camp - Ready for post-window comparison
  - `FP-BRAND-AM-02-GIRLS-CAMP-FACEBOOK` (Facebook): Girls Camp - Ready for post-window comparison
  - `FP-BRAND-AM-04-SPILLING-THE-TEA-X` (X): Spilling The Tea - Waiting for first useful result check
  - `FP-BRAND-AM-04-SPILLING-THE-TEA-FACEBOOK` (Facebook): Spilling The Tea - Waiting for first useful result check
  - `FP-BRAND-AM-05-NO-MORTGAGE-X` (X): No Mortgage - Next queued learning input
  - `FP-BRAND-AM-05-NO-MORTGAGE-FACEBOOK` (Facebook): No Mortgage - Next queued learning input

## Recommendations
- **Let the next automated posts run**: The active X/Facebook Analog Myth campaign is queued and ready; proof capture starts after the next window.
  - Command: `python3 scripts/refresh_promo_admin.py`
- **First-party clicks checked**: Which Analog Myth posts are turning attention into album, Echo Thread, or video clicks? No manual posting is required; this loop uses automatic posts, public URL proof, first-party click checks, and optional connected X/Facebook metrics.
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
