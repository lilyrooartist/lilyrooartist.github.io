# Brand Post Visibility - Lily Roo

Generated: 2026-07-07T17:31:41.889657Z

## Summary
- Status: **verified**
- Checked posts: **8**
- Public visibility OK: **8**
- Attention: **0**
- X copy confirmed: **4**
- Facebook pages loaded: **4**

## Rows
- **FP-BRAND-AM-01-13-FACEBOOK** Facebook - `page_loaded_no_unavailable_marker`
  - Logged URL: https://www.facebook.com/lilyrooartist/posts/122120959905249470
  - Checked URL: https://www.facebook.com/lilyrooartist/posts/122120959905249470
  - HTTP: `200`; copy matched: `True`
  - Note: Facebook public page loaded without the common unavailable-content marker.
- **FP-BRAND-AM-01-13-X** X - `visible_copy_confirmed`
  - Logged URL: https://x.com/i/web/status/2073410401006751908
  - Checked URL: https://publish.twitter.com/oembed?url=https%3A%2F%2Ftwitter.com%2Flilyrooartist%2Fstatus%2F2073410401006751908
  - HTTP: `200`; copy matched: `True`
  - Note: X public oEmbed returned Lily Roo post copy.
- **FP-BRAND-AM-02-GIRLS-CAMP-FACEBOOK** Facebook - `page_loaded_no_unavailable_marker`
  - Logged URL: https://www.facebook.com/lilyrooartist/posts/122121048123249470
  - Checked URL: https://www.facebook.com/lilyrooartist/posts/122121048123249470
  - HTTP: `200`; copy matched: `False`
  - Note: Facebook public page loaded without the common unavailable-content marker.
- **FP-BRAND-AM-02-GIRLS-CAMP-X** X - `visible_copy_confirmed`
  - Logged URL: https://x.com/i/web/status/2073772787177861205
  - Checked URL: https://publish.twitter.com/oembed?url=https%3A%2F%2Ftwitter.com%2Flilyrooartist%2Fstatus%2F2073772787177861205
  - HTTP: `200`; copy matched: `True`
  - Note: X public oEmbed returned Lily Roo post copy.
- **FP-BRAND-AM-03-ANALOG-MYTH-X** X - `visible_copy_confirmed`
  - Logged URL: https://x.com/i/web/status/2074135149185266159
  - Checked URL: https://publish.twitter.com/oembed?url=https%3A%2F%2Ftwitter.com%2Flilyrooartist%2Fstatus%2F2074135149185266159
  - HTTP: `200`; copy matched: `True`
  - Note: X public oEmbed returned Lily Roo post copy.
- **FP-BRAND-AM-03-ANALOG-MYTH-FACEBOOK** Facebook - `page_loaded_no_unavailable_marker`
  - Logged URL: https://www.facebook.com/lilyrooartist/posts/122121136809249470
  - Checked URL: https://www.facebook.com/lilyrooartist/posts/122121136809249470
  - HTTP: `200`; copy matched: `True`
  - Note: Facebook public page loaded without the common unavailable-content marker.
- **FP-BRAND-AM-04-SPILLING-THE-TEA-X** X - `visible_copy_confirmed`
  - Logged URL: https://x.com/i/web/status/2074497538409779510
  - Checked URL: https://publish.twitter.com/oembed?url=https%3A%2F%2Ftwitter.com%2Flilyrooartist%2Fstatus%2F2074497538409779510
  - HTTP: `200`; copy matched: `True`
  - Note: X public oEmbed returned Lily Roo post copy.
- **FP-BRAND-AM-04-SPILLING-THE-TEA-FACEBOOK** Facebook - `page_loaded_no_unavailable_marker`
  - Logged URL: https://www.facebook.com/lilyrooartist/posts/122121211923249470
  - Checked URL: https://www.facebook.com/lilyrooartist/posts/122121211923249470
  - HTTP: `200`; copy matched: `False`
  - Note: Facebook public page loaded without the common unavailable-content marker.

## Guardrails
- Read-only public URL probe; it does not publish, edit, or collect private analytics.
- X visibility is confirmed through public oEmbed post copy.
- Facebook visibility is limited to public page load checks because unauthenticated Facebook pages do not reliably expose post copy.
- A Facebook page load without an unavailable-content marker is treated as a visibility pass; metric capture still requires Meta API credentials.
