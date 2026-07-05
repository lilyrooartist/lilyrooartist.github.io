# Brand Post Visibility - Lily Roo

Generated: 2026-07-05T23:09:59.946563Z

## Summary
- Status: **attention**
- Checked posts: **4**
- Public visibility OK: **2**
- Attention: **2**
- X copy confirmed: **2**
- Facebook pages loaded: **0**

## Rows
- **FP-BRAND-AM-01-13-FACEBOOK** Facebook - `unavailable_marker_found`
  - Logged URL: https://www.facebook.com/122119767927249470/posts/122120959905249470
  - Checked URL: https://www.facebook.com/122119767927249470/posts/122120959905249470
  - HTTP: `200`; copy matched: `False`
  - Note: Facebook returned an unavailable-content marker for this post.
- **FP-BRAND-AM-01-13-X** X - `visible_copy_confirmed`
  - Logged URL: https://x.com/i/web/status/2073410401006751908
  - Checked URL: https://publish.twitter.com/oembed?url=https%3A%2F%2Ftwitter.com%2Flilyrooartist%2Fstatus%2F2073410401006751908
  - HTTP: `200`; copy matched: `True`
  - Note: X public oEmbed returned Lily Roo post copy.
- **FP-BRAND-AM-02-GIRLS-CAMP-FACEBOOK** Facebook - `unavailable_marker_found`
  - Logged URL: https://www.facebook.com/122119767927249470/posts/122121048123249470
  - Checked URL: https://www.facebook.com/122119767927249470/posts/122121048123249470
  - HTTP: `200`; copy matched: `False`
  - Note: Facebook returned an unavailable-content marker for this post.
- **FP-BRAND-AM-02-GIRLS-CAMP-X** X - `visible_copy_confirmed`
  - Logged URL: https://x.com/i/web/status/2073772787177861205
  - Checked URL: https://publish.twitter.com/oembed?url=https%3A%2F%2Ftwitter.com%2Flilyrooartist%2Fstatus%2F2073772787177861205
  - HTTP: `200`; copy matched: `True`
  - Note: X public oEmbed returned Lily Roo post copy.

## Guardrails
- Read-only public URL probe; it does not publish, edit, or collect private analytics.
- X visibility is confirmed through public oEmbed post copy.
- Facebook visibility is limited to public page load checks because unauthenticated Facebook pages do not reliably expose post copy.
- A Facebook page load without an unavailable-content marker is treated as a visibility pass; metric capture still requires Meta API credentials.
