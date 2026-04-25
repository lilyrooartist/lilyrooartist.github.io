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

Notes:

- TikTok and YouTube require a public direct video URL through `clip_url` or `SOCIAL_MEDIA_MAP_JSON`.
- X can post text with `X_USER_ACCESS_TOKEN`; media upload uses OAuth 1.0a or pre-uploaded IDs in `X_MEDIA_MAP_JSON`.
- The Worker route is configured for `www.lilyroo.com/api/social/*`.
