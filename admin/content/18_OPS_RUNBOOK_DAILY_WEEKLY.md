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

Regenerate weekly report:
```bash
python3 scripts/update_weekly_report.py
```

(If schedule/feed changed) regenerate future post feed:
```bash
python3 scripts/sync_future_posts.py
```

---

## Operating Rule
Consistency beats intensity: 2 posts/day + 1 canonized song/day + weekly report discipline.
