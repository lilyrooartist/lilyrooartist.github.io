# Promotion Blocker Ledger - Lily Roo

Generated: 2026-07-11T03:44:02.068393Z

## Summary
- Open blockers: **0**
- User-owned: **0**
- External platform-owned: **0**
- Codex-actionable: **0**
- High or critical: **0**

## Unlock Roadmap
- **Approve checked scheduled rows** (`clear`)
  - Owner: `tod`; projected blockers resolved: **0**
  - Unlocks: Instagram executor row can become publish-eligible after approval.
- **Manual distribution lane clear** (`clear`)
  - Owner: `tod`; projected blockers resolved: **0**
  - Unlocks: No manual-only posting lane is active; growth work stays in automated or review-only surfaces.
  - Guardrail: Manual-only approvals do not auto-post; posting and public URL logging remain separate after review.
- **Prepare TikTok direct-public API lane** (`deferred`)
  - Owner: `tod`; projected blockers resolved: **0**
  - Unlocks: TikTok can become an automated expansion lane only after direct public posting approval is explicit.; Upload-draft/manual-finish TikTok posting stays out of the active plan.
  - Guardrail: Do not queue TikTok upload-draft rows as active promotion; only direct public API publishing can enter the active plan.
- **Reschedule approved past-due backlog** (`clear`)
  - Owner: `tod`; projected blockers resolved: **0**
  - Unlocks: Approved past-due queue rows get a fresh schedule after executor blockers clear.
  - Preview/check: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-12T10:00:00+00:00' --spacing-hours 24`
  - Apply after review: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-07-12T10:00:00+00:00' --spacing-hours 24 --apply --refresh-admin`
- **Optional: fill private metric worksheet** (`optional_input`)
  - Owner: `tod`; projected blockers resolved: **0**
  - Optional measurement fields: **6**
  - Unlocks: Admin health and weekly reporting get sharper private-analytics context.; Automated Analog Myth posting, proof export, and click learning continue without these values.
  - Blocked by: P2 Recent discovery and traffic:4, P3 Release depth metrics:2
  - Guardrail: Private analytics are optional measurement inputs, not blockers for automated promotion.

## Ledger

## Optional Measurement Inputs
- **Fill priority 2 metrics: Recent discovery and traffic** (`needs_values`)
  - Fields: 4; source: `data/manual_metric_collection_packet.json`
  - Preview/check after filling values: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Guardrail: Private analytics improve reporting but do not block automated promotion.
- **Fill priority 3 metrics: Release depth metrics** (`needs_values`)
  - Fields: 2; source: `data/manual_metric_collection_packet.json`
  - Preview/check after filling values: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Guardrail: Private analytics improve reporting but do not block automated promotion.

## Guardrails
- This ledger does not approve posts, post externally, push secrets, or invent metric values.
- Treat external platform repairs as blockers until fresh admin evidence proves they cleared.
- Treat private manual metric values as optional measurement inputs; do not guess or import them without source evidence.
