# /admin — Lily Roo 8-week progress tracker

- `index.html` renders `progress.json` (targets with progress bars, this week's tasks, blockers waiting on Tod, all weeks, metrics history, log).
- Password gate: client-side SHA-256 check against the same digest the old admin used, so the existing password works.
  This is **not security**. Everything in this folder (including progress.json) is publicly downloadable. Don't put secrets or private data here.
  For real protection, put /admin behind Cloudflare Access.
- `noindex` meta tag + `Disallow: /admin/` in robots.txt keep it out of search.

## Updating (weekly, one commit — no bots)
Edit `progress.json` and commit to `main`:
1. Set `"updated"` to today.
2. Append one row to `metrics` (use `null` for unknown):
   `{"date":"2026-10-19","yt_subs":9,"yt_videos":40,"spotify_monthly":12,"spotify_followers":null,"email_subs":3,"x_followers":40,"site_sessions":null}`
   The cards show the latest non-null value of each metric against `targets`.
3. Change task `status` (`todo` | `doing` | `done` | `blocked`), set `done_on`, add `notes`. `owner` is `Tod` or `LR`.
   Tod-owned tasks that are blocked, or due in the current week or earlier and not done, show under "Blockers needing Tod".
4. Add a line to `log`.
The current week is computed from `plan_start` (2026-10-12), capped at 8.

Spotify/Apple numbers come from Spotify for Artists / Apple Music for Artists by hand (no public API).
To change the password: put the new SHA-256 hex digest in `ADMIN_PASSWORD_DIGEST` in index.html
(`printf %s 'newpass' | sha256sum`).
