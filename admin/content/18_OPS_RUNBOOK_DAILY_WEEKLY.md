# Lily Roo Ops Runbook (Daily + Weekly)

## Purpose
Keep promo momentum compounding with a lightweight routine:
1) keep queue moving,
2) keep backstory quality improving,
3) keep metrics current.

---

## Daily Checklist (Top 3 Must-Do)

### 1) Execute top 2 queued posts
- Open `/admin` → **Promo** tab
- In **Upcoming 7-Day Posts**, choose top 2 by nearest schedule/priority
- Click **Execute now** for each
- Post on target platform
- Paste final published URL when prompted

**Definition of done:**
- 2 posts published
- each marked `posted`
- each has captured URL

---

### 2) Canonize 1 song pack
- Open `/admin` → **Backstory** tab
- Use preset/filter for draft/needs-work songs
- Select one song and upgrade its backstory pack from draft → canonical:
  - clear emotional thesis
  - 2–3 concrete anecdote anchors
  - lyric excerpt linkage
  - CTA line

**Definition of done:**
- 1 song pack updated with canonical narrative quality
- lyric/backstory link is explicit in pack or index

---

### 3) Queue hygiene pass (5 minutes)
- Confirm next 7-day queue has complete entries:
  - platform
  - time
  - text + redo variants
  - imagery + preview
- Fix weak/empty slots immediately

**Definition of done:**
- no empty slots in next 48h
- all queued items have usable copy + imagery

---

## Weekly Checklist (Saturday)

### A) Refresh report
Run:
```bash
python3 scripts/update_weekly_report.py
```
Then review:
- `/admin/reports/weekly-social-report.md`

**Definition of done:**
- report regenerated this week
- period + last updated fields current
- KPI section reflects latest known numbers

---

### B) Canonization review (Top 10)
- Open `admin/content/17_TOP10_CANON_PACKS.md`
- Review all top songs for quality status
- Promote any ready packs to "canonical" quality
- Identify next 3 songs for upcoming week

**Definition of done:**
- top-10 list reviewed
- at least 2 packs improved in the week
- next-week canon targets selected

---

### C) Queue strategy reset
- Rebalance upcoming 7-day queue:
  - mix of current songs + older callbacks (e.g., Brain Rot)
  - varied platform spread
  - conversion CTA cadence (hard CTA every 2–3 posts)

**Definition of done:**
- 7-day queue refreshed
- no platform neglected
- CTA cadence intentional and visible

---

## “If Blocked” Playbook

### 1) Login/Auth block
Symptoms: sign-in wall, invalid session, OTP/captcha loop.
Actions:
1. Pause automation attempts
2. Manual login in browser session
3. Resume from current step
4. Note blocker in report/log if persistent

**Done when:** account session restored and flow can continue.

### 2) Upload/File picker block
Symptoms: media won’t attach, native dialog fails.
Actions:
1. Copy media to `/tmp/openclaw/uploads/`
2. Retry upload from that path
3. If site still blocks picker, do one manual picker step then continue automation

**Done when:** media is attached and preview visible on compose screen.

### 3) Post publish fails/rejected
Symptoms: spinner, silent fail, policy hold, review delay.
Actions:
1. Save draft text locally
2. Retry once with same asset
3. If still blocked, switch to fallback platform post
4. Record failure note + keep URL blank/queued status

**Done when:** either post is published with URL, or fallback post is published with URL.

### 4) Metrics unavailable
Symptoms: API/data unavailable, platform stats missing.
Actions:
1. Update what is known
2. Put missing values in `data/manual_social_stats.json` as `pending`
3. Regenerate report anyway

**Done when:** weekly report updated with explicit pending markers (no silent gaps).

---

## Quick Commands

Check website posting executor health:
```bash
curl https://www.lilyroo.com/api/social/health
```

Check Facebook publishing readiness without posting:
```bash
python3 scripts/check_facebook_publishing.py --post-id FP-AUTO-210 --check-worker-secrets
```

Check X publishing readiness without posting:
```bash
python3 scripts/check_x_publishing.py --post-id FP-AUTO-213 --check-worker-secrets
```

Local development fallback only:
```bash
python3 scripts/social_execute_bridge.py
```

Local fallback health check:
```bash
curl http://127.0.0.1:8765/health
```

Regenerate weekly report:
```bash
python3 scripts/update_weekly_report.py
```

(If schedule/feed changed) regenerate future post feed:
```bash
python3 scripts/sync_future_posts.py
```

## Execute Now Setup

The live `/admin` Execute now button calls the website API route:

`https://www.lilyroo.com/api/social/execute`

That route is served by the Cloudflare Worker in `workers/social-executor`. It exists because GitHub Pages is static and cannot safely hold social API credentials in browser JavaScript.

The health endpoint is public. The execute endpoint accepts either the logged-in Cloudflare Access session from `/admin` or `EXECUTOR_BEARER_TOKEN` for command-line checks. The browser admin page should not ask for or store the executor token.

Deploy/update the Worker:

```bash
npx wrangler deploy --config workers/social-executor/wrangler.jsonc
```

Set Worker secrets:

```bash
npx wrangler secret put EXECUTOR_BEARER_TOKEN --config workers/social-executor/wrangler.jsonc
npx wrangler secret put META_LONG_LIVED_TOKEN --config workers/social-executor/wrangler.jsonc
npx wrangler secret put FB_PAGE_ID --config workers/social-executor/wrangler.jsonc
npx wrangler secret put IG_BUSINESS_ACCOUNT_ID --config workers/social-executor/wrangler.jsonc
npx wrangler secret put TIKTOK_ACCESS_TOKEN --config workers/social-executor/wrangler.jsonc
npx wrangler secret put GOOGLE_CLIENT_ID --config workers/social-executor/wrangler.jsonc
npx wrangler secret put GOOGLE_CLIENT_SECRET --config workers/social-executor/wrangler.jsonc
npx wrangler secret put YOUTUBE_REFRESH_TOKEN --config workers/social-executor/wrangler.jsonc
npx wrangler secret put X_USER_ACCESS_TOKEN --config workers/social-executor/wrangler.jsonc
npx wrangler secret put SOCIAL_MEDIA_MAP_JSON --config workers/social-executor/wrangler.jsonc
```

Or push selected values from the local gitignored secret files:

```bash
python3 scripts/push_social_worker_secrets.py X_USER_ACCESS_TOKEN
```

For X image upload fallback, also set OAuth 1.0a credentials:

```bash
npx wrangler secret put X_API_KEY --config workers/social-executor/wrangler.jsonc
npx wrangler secret put X_API_SECRET --config workers/social-executor/wrangler.jsonc
npx wrangler secret put X_ACCESS_TOKEN --config workers/social-executor/wrangler.jsonc
npx wrangler secret put X_ACCESS_TOKEN_SECRET --config workers/social-executor/wrangler.jsonc
```

Optional X pre-uploaded media mapping:

```bash
npx wrangler secret put X_MEDIA_MAP_JSON --config workers/social-executor/wrangler.jsonc
```

Example value:

```json
{"slow-walk-cover":"1234567890123456789"}
```

Example `SOCIAL_MEDIA_MAP_JSON` value for website-hosted media:

```json
{"slow-walk-video":"https://www.lilyroo.com/admin/media/slow-walk-22s.mp4","slow-walk-cover":"https://i.ytimg.com/vi/R7evPASi8vM/maxresdefault.jpg"}
```

TikTok and YouTube need a public direct video URL, either in the queue `clip_url` column or in `SOCIAL_MEDIA_MAP_JSON`.

### X publishing

The X queue path publishes text posts and optional reply posts through `POST https://api.x.com/2/tweets`.

Required Cloudflare secrets for text/reply posting:
- `EXECUTOR_BEARER_TOKEN`: random posting token used by command-line checks and emergency fallback
- `X_USER_ACCESS_TOKEN`: OAuth 2 user access token with post/write access

OAuth 1.0a credentials are only required for direct X media upload:
- `X_API_KEY`
- `X_API_SECRET`
- `X_ACCESS_TOKEN`
- `X_ACCESS_TOKEN_SECRET`

Queued X posts are text-only unless `x_media_key` or `media_key` is populated. If an X row has an explicit media key, either map it to pre-uploaded X media IDs with `X_MEDIA_MAP_JSON`, or provide the OAuth 1.0a credentials for image upload.

Current queued X smoke test:
```bash
python3 scripts/post_x_from_queue.py --post-id FP-AUTO-213 --dry-run
```

Live execute smoke test after secrets are set:
```bash
python3 scripts/check_x_publishing.py --post-id FP-AUTO-213 --check-worker-secrets --check-worker-readiness --check-worker-dry-run --executor-token "$EXECUTOR_BEARER_TOKEN"
```

### Facebook publishing

The Facebook queue path publishes Page posts through Meta Graph API `v25.0`.

Required Cloudflare secrets:
- `EXECUTOR_BEARER_TOKEN`: random posting token used by command-line checks and emergency fallback
- `META_LONG_LIVED_TOKEN`: Page access token for the Lily Roo Facebook Page
- `FB_PAGE_ID`: Lily Roo Facebook Page ID

The Meta token must be able to create Page posts. In Meta's current Pages API docs, Page publishing uses a Page access token with `pages_manage_posts`, and the publish endpoints are `/{page_id}/feed` for text/link posts and `/{page_id}/photos` for image URL posts.

Current queued Facebook smoke test:
```bash
python3 scripts/post_meta_from_queue.py --post-id FP-AUTO-210 --dry-run
```

Live execute smoke test after secrets are set:
```bash
python3 scripts/check_facebook_publishing.py --post-id FP-AUTO-210 --check-worker-secrets --check-worker-dry-run --executor-token "$EXECUTOR_BEARER_TOKEN"
```

Security rule: protect `/admin/*` with Cloudflare Access. The Worker validates the Cloudflare Access JWT/cookie for browser execute calls and also keeps `EXECUTOR_BEARER_TOKEN` as a non-browser fallback for scripts.

Local-only Python bridge files are still useful for testing from a laptop. They are not used by the live website button.

Required local files are gitignored and live under the workspace-level `secrets/` directory:

- `secrets/social_api.env`
  - Executor: `EXECUTOR_BEARER_TOKEN` for live dry-run checks
  - X: `X_USER_ACCESS_TOKEN` for OAuth 2 user context, or `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET` for OAuth 1.0a
  - Meta: `META_LONG_LIVED_TOKEN`, `FB_PAGE_ID`, `IG_BUSINESS_ACCOUNT_ID`, optional `META_GRAPH_VERSION`
  - TikTok: `TIKTOK_ACCESS_TOKEN`, optional `TIKTOK_IS_AIGC=true|false`
- `secrets/youtube-api.env`
  - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`
- `secrets/social-media-map.json`
  - maps queue `media_key` values like `slow-walk-video` to local video files for TikTok/YouTube
  - maps image keys like `slow-walk-cover` to local image files when a platform needs uploadable local media
- `secrets/x-media-map.json`
  - optional: maps X `x_media_key` values to pre-uploaded numeric media IDs, or local image files for simple image upload

---

## Operating Rule
Consistency beats intensity: 2 posts/day + 1 canonized song/day + weekly report discipline.
