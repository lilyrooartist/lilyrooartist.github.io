# Lily Roo Social Executor

Cloudflare Worker backing the live `/admin` **Execute now** button.

The public site is static GitHub Pages, so social API credentials must live in a server-side runtime. This Worker exposes:

- `GET /api/social/health`
- `GET /api/social/readiness`
- `GET /api/social/metrics`
- `GET /api/social/executions`
- `GET /api/social/tiktok/status?publish_id=...`
- `POST /api/social/execute`
- `POST /api/social/scheduler/dry-run`

Deploy:

```bash
npx wrangler deploy --config workers/social-executor/wrangler.jsonc
```

If deploy returns Cloudflare API authentication code `10000` for account
`d7557073a09c5995e004a1839f0f4f70`, re-authenticate Wrangler with the
Cloudflare account that owns the existing `lilyroo-social-executor` service and
`lilyroo.com` zone, then rerun the same deploy command.

Required secrets are listed in `admin/content/18_OPS_RUNBOOK_DAILY_WEEKLY.md`.
`ADMIN_PASSWORD` must be set as a Worker secret; it is intentionally not stored
in `wrangler.jsonc`.

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

- `/api/social/metrics` is read-only and authenticated. It returns live metrics
  where the current tokens/scopes support them, and an explicit unavailable or
  API-limited status where a platform token only supports posting.
- Spotify is included in the metrics payload with public oEmbed release
  verification when the Worker source is deployed. Release streams, saves,
  monthly listeners, and artist followers should still be entered in
  `data/manual_social_stats.json` until Spotify for Artists export or another
  analytics source is connected.
- The cron trigger runs every 15 minutes, but scheduled posting is disabled
  until a KV namespace binding named `SOCIAL_EXECUTOR_STATE` exists. That state
  is used for idempotency, attempts, success URLs, skip reasons, and errors.
- TikTok and YouTube require a public direct video URL through `clip_url` or `SOCIAL_MEDIA_MAP_JSON`. Do not point video media at `/admin/*`; admin content is intended for signed-in browser use, so upload media must live under a public path such as `/assets/media/*`.
- TikTok supports `TIKTOK_POSTING_MODE=upload` for inbox draft uploads using
  `video.upload`; the creator must finish the post in TikTok and then log the
  public URL.
- TikTok direct auto-posting requires `TIKTOK_POSTING_MODE=direct`,
  `TIKTOK_PUBLIC_POSTING_APPROVED=true`, and a creator privacy option of
  `PUBLIC_TO_EVERYONE`.
- TikTok auth may use either a current `TIKTOK_ACCESS_TOKEN` or refresh credentials
  `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, and `TIKTOK_REFRESH_TOKEN`.
- TikTok posts return a `publish_id`; use `GET /api/social/tiktok/status?publish_id=...` to fetch follow-up processing status.
- X can post text/replies with `X_USER_ACCESS_TOKEN`. X media is only attached when a queue row provides an explicit media key; media upload uses OAuth 1.0a or pre-uploaded IDs in `X_MEDIA_MAP_JSON`.
- The Worker route is configured for `www.lilyroo.com/api/social/*`.
- `GET /api/social/health` is public. `GET /api/social/readiness`,
  `GET /api/social/metrics`, and `POST /api/social/execute` are gated by the
  admin password header or the executor bearer token fallback.
