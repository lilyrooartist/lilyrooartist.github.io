# Lily Roo Social Executor

Cloudflare Worker backing the live `/admin` **Execute now** button.

The public site is static GitHub Pages, so social API credentials must live in a server-side runtime. This Worker exposes:

- `GET /api/social/health`
- `POST /api/social/execute`

Deploy:

```bash
npx wrangler deploy --config workers/social-executor/wrangler.jsonc
```

Required secrets are listed in `admin/content/18_OPS_RUNBOOK_DAILY_WEEKLY.md`.

Facebook publishing uses Meta Graph API `v25.0` by default. Override with the
`META_GRAPH_VERSION` Worker var only when intentionally testing a different
Graph version.
Instagram publishing can use either the Facebook-login Graph path with
`META_LONG_LIVED_TOKEN` plus `IG_BUSINESS_ACCOUNT_ID`, or an Instagram-login
token in `IG_ACCESS_TOKEN`.

The browser admin UI uses the fixed admin password stored in the Worker
`ADMIN_PASSWORD` var. Once the password is entered, the browser remembers it in
localStorage for that computer until **Lock admin** is clicked.
`EXECUTOR_BEARER_TOKEN` remains available for command-line checks.

Notes:

- TikTok and YouTube require a public direct video URL through `clip_url` or `SOCIAL_MEDIA_MAP_JSON`. Do not point video media at `/admin/*`; admin content is intended for signed-in browser use, so upload media must live under a public path such as `/assets/media/*`.
- X can post text/replies with `X_USER_ACCESS_TOKEN`. X media is only attached when a queue row provides an explicit media key; media upload uses OAuth 1.0a or pre-uploaded IDs in `X_MEDIA_MAP_JSON`.
- The Worker route is configured for `www.lilyroo.com/api/social/*`.
- `GET /api/social/health` is public. `POST /api/social/execute` is gated by
  the admin password header or the executor bearer token fallback.
