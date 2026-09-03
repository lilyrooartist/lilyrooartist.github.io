# Brand Post Visibility - Lily Roo

Generated: 2026-09-03T19:10:10.773054Z

## Summary
- Status: **verified**
- Checked posts: **8**
- Public visibility OK: **8**
- Attention: **0**
- X copy confirmed: **4**
- Facebook pages loaded: **4**

## Rows
- **FP-BRAND-AM-05-NO-MORTGAGE-X** X - `visible_copy_confirmed`
  - Logged URL: https://x.com/i/web/status/2074859954704441417
  - Checked URL: https://publish.twitter.com/oembed?url=https%3A%2F%2Ftwitter.com%2Flilyrooartist%2Fstatus%2F2074859954704441417
  - HTTP: `200`; copy matched: `True`
  - Note: X public oEmbed returned Lily Roo post copy.
- **FP-BRAND-AM-05-NO-MORTGAGE-FACEBOOK** Facebook - `page_loaded_no_unavailable_marker`
  - Logged URL: https://www.facebook.com/lilyrooartist/posts/122121305865249470
  - Checked URL: https://www.facebook.com/lilyrooartist/posts/122121305865249470
  - HTTP: `200`; copy matched: `False`
  - Note: Facebook public page loaded without the common unavailable-content marker.
- **FP-BRAND-AM-06-GUARDS-DOWN-FACEBOOK** Facebook - `page_loaded_no_unavailable_marker`
  - Logged URL: https://www.facebook.com/lilyrooartist/posts/122121402309249470
  - Checked URL: https://www.facebook.com/lilyrooartist/posts/122121402309249470
  - HTTP: `200`; copy matched: `False`
  - Note: Facebook public page loaded without the common unavailable-content marker.
- **FP-BRAND-AM-06-GUARDS-DOWN-X** X - `visible_copy_confirmed`
  - Logged URL: https://x.com/i/web/status/2075222310240535024
  - Checked URL: https://publish.twitter.com/oembed?url=https%3A%2F%2Ftwitter.com%2Flilyrooartist%2Fstatus%2F2075222310240535024
  - HTTP: `200`; copy matched: `True`
  - Note: X public oEmbed returned Lily Roo post copy.
- **FP-BRAND-AM-07-SLOW-WALK-X** X - `visible_copy_confirmed`
  - Logged URL: https://x.com/i/web/status/2075584699003740283
  - Checked URL: https://publish.twitter.com/oembed?url=https%3A%2F%2Ftwitter.com%2Flilyrooartist%2Fstatus%2F2075584699003740283
  - HTTP: `200`; copy matched: `True`
  - Note: X public oEmbed returned Lily Roo post copy.
- **FP-BRAND-AM-07-SLOW-WALK-FACEBOOK** Facebook - `page_loaded_no_unavailable_marker`
  - Logged URL: https://www.facebook.com/lilyrooartist/posts/122121496545249470
  - Checked URL: https://www.facebook.com/lilyrooartist/posts/122121496545249470
  - HTTP: `200`; copy matched: `False`
  - Note: Facebook public page loaded without the common unavailable-content marker.
- **FP-BRAND-AM-08-THE-POWER-OF-LIGHT-FACEBOOK** Facebook - `page_loaded_no_unavailable_marker`
  - Logged URL: https://www.facebook.com/lilyrooartist/posts/122121593013249470
  - Checked URL: https://www.facebook.com/lilyrooartist/posts/122121593013249470
  - HTTP: `200`; copy matched: `True`
  - Note: Facebook public page loaded without the common unavailable-content marker.
- **FP-BRAND-AM-08-THE-POWER-OF-LIGHT-X** X - `visible_copy_confirmed`
  - Logged URL: https://x.com/i/web/status/2075947147338391981
  - Checked URL: https://publish.twitter.com/oembed?url=https%3A%2F%2Ftwitter.com%2Flilyrooartist%2Fstatus%2F2075947147338391981
  - HTTP: `200`; copy matched: `True`
  - Note: X public oEmbed returned Lily Roo post copy.

## Guardrails
- Read-only public URL probe; it does not publish, edit, or collect private analytics.
- X visibility is confirmed through public oEmbed post copy.
- Facebook visibility is limited to public page load checks because unauthenticated Facebook pages do not reliably expose post copy.
- A Facebook page load without an unavailable-content marker is treated as a visibility pass; metric capture still requires Meta API credentials.
