# Promo Consistency Audit - Lily Roo

Generated: 2026-06-22T05:32:18.871071Z

## Summary
- Status: **pass**
- Checks: **30 / 30** passed
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
- **scheduler_blocked_ids_present_in_executor_attention**: `pass`
  - Scheduler dry-run blockers should be represented in executor attention; executor history may include stale rows that are now would-post.
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
- **handoff_preview_task_alignment**: `pass`
  - Human handoff preview should include one preview row for every handoff task.
- **handoff_preview_worksheet_row_count_matches_handoff**: `pass`
  - Human handoff preview worksheet row count should match the handoff packet worksheet summary.
- **handoff_preview_status_matches_status_kpi**: `pass`
  - Promo status handoff preview KPI should mirror preview status counts.
- **handoff_preview_counts_match_status_kpi**: `pass`
  - Promo status handoff preview KPI should mirror preview summary counts.
- **handoff_preview_next_action_matches_status**: `pass`
  - Promo status next actions should expose the handoff preview health summary.
- **unlock_sequence_step_count_matches_roadmap**: `pass`
  - Promo unlock sequence should include one step for every blocker roadmap phase.
- **unlock_sequence_order_matches_roadmap**: `pass`
  - Promo unlock sequence order should mirror the blocker ledger roadmap order.
- **unlock_sequence_open_blockers_match_ledger**: `pass`
  - Promo unlock sequence should mirror the blocker ledger open blocker count.
- **unlock_sequence_current_step_is_preview_ready**: `pass`
  - Promo unlock sequence should lead with the first currently actionable gate, skipping any completed evidence-only gate.
- **unlock_sequence_matches_status_kpi**: `pass`
  - Promo status should mirror the unlock sequence summary.
- **unlock_sequence_next_action_matches_status**: `pass`
  - Promo status next actions should expose the current unlock sequence gate.
- **refresh_run_required_steps_successful**: `pass`
  - Latest promo admin refresh should have no required failures; tolerated optional capture failures stay visible in the refresh run summary.

## Guardrails
- This audit does not mutate promotion, posting, approval, metrics, or secrets state.
- A failed check means generated admin surfaces disagree and should be inspected before acting on commands.
