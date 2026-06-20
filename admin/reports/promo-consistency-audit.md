# Promo Consistency Audit - Lily Roo

Generated: 2026-06-20T06:03:18.030348Z

## Summary
- Status: **pass**
- Checks: **19 / 19** passed
- Failed checks: **0**
- High severity failures: **0**
- Medium severity failures: **0**

## Checks
- **ledger_open_count_matches_rows**: `pass`
  - Blocker ledger summary should match row count.
- **ledger_category_total_matches_rows**: `pass`
  - Blocker category counts should account for every blocker row.
- **status_open_actions_match_operations**: `pass`
  - Promo status open action count should mirror the operations packet.
- **approval_counts_match**: `pass`
  - Scheduled approval packet should match approval blockers in the ledger.
- **executor_approval_count_matches_scheduled_packet**: `pass`
  - Executor approval-needed count should match the scheduled approval packet.
- **platform_repair_count_matches_ledger**: `pass`
  - Platform repair packet should match platform repair blockers in the ledger.
- **executor_platform_fix_count_matches_platform_packet**: `pass`
  - Executor platform-fix count should match the platform repair packet.
- **tiktok_preflight_status_matches_platform_repair**: `pass`
  - TikTok platform repair row should mirror the setup preflight status.
- **tiktok_preflight_local_missing_matches_platform_repair**: `pass`
  - TikTok preflight local missing secrets should match the platform repair row.
- **tiktok_preflight_worker_missing_matches_platform_repair**: `pass`
  - TikTok preflight worker missing secrets should match the platform repair row.
- **scheduler_blocked_matches_executor_attention**: `pass`
  - Scheduler dry-run blocked count should match executor attention count.
- **manual_distribution_count_matches_ledger**: `pass`
  - Manual distribution packet should match manual distribution blockers in the ledger.
- **manual_distribution_handoff_count_matches_packet**: `pass`
  - Human handoff should include every unlogged manual distribution row.
- **manual_metric_batch_count_matches_ledger**: `pass`
  - Manual metric priority batch count should match manual metric blockers.
- **manual_metric_handoff_batch_count_matches_packet**: `pass`
  - Human handoff should include every manual metric priority batch.
- **store_checks_match_checked_pending_services**: `pass`
  - Operations store checks should match checked-pending store services.
- **handoff_blocker_summary_matches_ledger**: `pass`
  - Human handoff blocker summary should be copied from the blocker ledger.
- **handoff_projection_matches_ledger_projection**: `pass`
  - Human handoff next-resolution projection should match the blocker ledger projection.
- **refresh_run_required_steps_successful**: `pass`
  - Latest promo admin refresh should have no required failures; tolerated optional capture failures stay visible in the refresh run summary.

## Guardrails
- This audit does not mutate promotion, posting, approval, metrics, or secrets state.
- A failed check means generated admin surfaces disagree and should be inspected before acting on commands.
