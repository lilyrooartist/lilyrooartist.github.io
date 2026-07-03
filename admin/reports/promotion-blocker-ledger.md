# Promotion Blocker Ledger - Lily Roo

Generated: 2026-07-03T07:30:10.193041Z

## Summary
- Open blockers: **2**
- User-owned: **2**
- External platform-owned: **0**
- Codex-actionable: **0**
- High or critical: **0**

## Unlock Roadmap
- **Approve checked scheduled rows** (`blocked`)
  - Owner: `tod`; projected blockers resolved: **0**
  - Unlocks: Instagram executor row can become publish-eligible after approval.
- **Manual distribution lane clear** (`clear`)
  - Owner: `tod`; projected blockers resolved: **0**
  - Unlocks: No manual-only posting lane is active; growth work stays in automated or review-only surfaces.
  - Guardrail: Manual-only approvals do not auto-post; posting and public URL logging remain separate after review.
- **Repair TikTok executor** (`ready`)
  - Owner: `tod`; projected blockers resolved: **0**
  - Unlocks: Held TikTok approval rows can pass platform-readiness review.; Approved TikTok backlog can become safe to reschedule into upload-draft creation.
- **Reschedule approved past-due backlog** (`clear`)
  - Owner: `tod`; projected blockers resolved: **0**
  - Unlocks: Approved past-due queue rows get a fresh schedule after executor blockers clear.
  - Preview/check: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-04T10:00:00-04:00' --spacing-hours 24`
  - Apply after review: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-04T10:00:00-04:00' --spacing-hours 24 --apply --refresh-admin`
- **Fill manual metric worksheet** (`needs_values`)
  - Owner: `tod`; projected blockers resolved: **6**
  - Unlocks: Admin health and weekly reporting can use fresh cross-platform metrics.; Manual metric blockers clear once worksheet values are imported.
  - Blocked by: P2 Recent discovery and traffic:4, P3 Release depth metrics:2
  - Preview/check: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Apply after review: `python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`

## Ledger
- **[low] Fill priority 2 metrics: Recent discovery and traffic** (`metrics-priority-2`)
  - Owner: `tod`; status: `needs_values`; category: `manual_metrics`
  - Evidence: 4 pending field(s): facebook.reach_7d, instagram.profile_visits_7d, tiktok.profile_views_7d, x.impressions_7d.
  - Next step: Collect this priority batch, fill the CSV worksheet rows, preview import, then refresh admin.
  - Preview/check: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Apply/log after review: `python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`
  - Guardrail: Do not guess analytics values; import only values copied from the platform source.
  - Impact: priority 2; fields: 4; access: private_analytics; csv rows: 2, 3, 6, 7
- **[low] Fill priority 3 metrics: Release depth metrics** (`metrics-priority-3`)
  - Owner: `tod`; status: `needs_values`; category: `manual_metrics`
  - Evidence: 2 pending field(s): spotify.release_streams, spotify.saves.
  - Next step: Collect this priority batch, fill the CSV worksheet rows, preview import, then refresh admin.
  - Preview/check: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Apply/log after review: `python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`
  - Guardrail: Do not guess analytics values; import only values copied from the platform source.
  - Impact: priority 3; fields: 2; access: private_analytics; csv rows: 4, 5

## Guardrails
- This ledger does not approve posts, post externally, push secrets, or invent metric values.
- Treat external platform repairs and manual values as blockers until fresh admin evidence proves they cleared.
