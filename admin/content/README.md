# Lily Roo Content System

This folder is the working content brain for Lily Roo admin operations. Keep the public site simple, but keep the source material here explicit, indexed, and easy to refresh.

## Source of truth

| Area | File | Purpose |
| --- | --- | --- |
| Canon and voice | `00_CANON.md`, `01_VOICE_SYSTEM.md` | Durable identity, themes, posting voice, and do/don't rules. |
| Anecdotes | `10_ANECDOTE_BANK.md` | Reusable story seeds for captions, intros, pinned comments, and longer posts. |
| Lyrics and backstory map | `11_LYRIC_BACKSTORY_INDEX.csv` | Links lyric excerpts to story anchors. |
| Song packs | `packs/*_backstory.md`, `packs/*_visuals.md` | Per-song narrative and asset guidance. Every song should have both. |
| Quips | `20_QUIPS_BANK.csv` | Short reusable hooks with theme, tone, platform fit, and CTA. |
| Promo operations | `30_PROMO_SYSTEM.md`, `40_RANDOM_RHYTHM_PLAYBOOK.md` | Posting strategy, cadence, and conversion rules. |
| Account operations | `19_AOL_ACCOUNT_HANDOFF.md`, `21_AOL_GMAIL_BRIDGE.md` | AOL account handoff plus the local AOL-to-Gmail bridge runbook. |
| Queue | `../../data/scheduled_posts.csv` | Source of truth for upcoming scheduled posts. |
| Published log | `Published_Log.csv` | Source of truth for completed posts and report latest-post links. |
| Release status | `../../data/distrokid_release_status.json` | Source of truth for DistroKid/store rollout status and current release CTAs. |
| Generated index | `CONTENT_INDEX.md`, `content_index.json` | Generated inventory of songs, packs, quips, queue state, and drift warnings. |

## Operating rules

- Write queued posts as Lily posting directly unless the platform or page is explicitly editorial.
- Keep each song's backstory pack paired with a visual pack.
- Add one concrete object, scene, or lyric anchor before adding abstract brand language.
- Every 2-3 queued posts should include a real conversion ask: stream, watch, subscribe, or visit the archive.
- Regenerate generated artifacts after content changes:

```bash
python3 scripts/build_content_index.py
python3 scripts/sync_future_posts.py
python3 scripts/update_weekly_report.py
python3 scripts/validate_content_system.py
```

## Generated artifacts

Do not hand-edit `CONTENT_INDEX.md`, `content_index.json`, or `admin/future-posts.json` unless you are intentionally debugging a generated output. Update source files, then rerun the generator.
