#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMO_STATUS = ROOT / "data" / "promo_engine_status.json"
PROMO_OPERATIONS = ROOT / "data" / "promo_operations_packet.json"
BLOCKER_LEDGER = ROOT / "data" / "promotion_blocker_ledger.json"
HUMAN_HANDOFF = ROOT / "data" / "human_handoff_packet.json"
HUMAN_HANDOFF_RESOLUTION_PREVIEW = ROOT / "data" / "human_handoff_resolution_preview.json"
PROMO_UNLOCK_SEQUENCE = ROOT / "data" / "promo_unlock_sequence.json"
SCHEDULED_APPROVAL = ROOT / "data" / "scheduled_approval_packet.json"
PLATFORM_REPAIR = ROOT / "data" / "platform_repair_status.json"
TIKTOK_PREFLIGHT = ROOT / "data" / "tiktok_setup_preflight.json"
MANUAL_DISTRIBUTION = ROOT / "data" / "manual_distribution_packet.json"
MANUAL_METRICS = ROOT / "data" / "manual_metric_collection_packet.json"
STORE_HISTORY = ROOT / "data" / "store_verification_history.json"
SOCIAL_EXECUTIONS = ROOT / "data" / "social_execution_snapshot.json"
SCHEDULER_DRY_RUN = ROOT / "data" / "social_scheduler_dry_run.json"
REFRESH_RUN = ROOT / "data" / "promo_admin_refresh_run.json"
OUT = ROOT / "data" / "promo_consistency_audit.json"
REPORT = ROOT / "admin" / "reports" / "promo-consistency-audit.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def get_path(payload: dict, path: list[str], default=0):
    current = payload
    for key in path:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    return default if current is None else current


def verdict(name: str, ok: bool, detail: str, expected=None, actual=None, severity: str = "high") -> dict:
    return {
        "name": name,
        "status": "pass" if ok else "fail",
        "severity": "ok" if ok else severity,
        "detail": detail,
        "expected": expected,
        "actual": actual,
    }


def same_value(name: str, expected, actual, detail: str, severity: str = "high") -> dict:
    return verdict(name, expected == actual, detail, expected=expected, actual=actual, severity=severity)


def category_count(ledger: dict, category: str) -> int:
    return int(((ledger.get("summary") or {}).get("category_counts") or {}).get(category) or 0)


def phase_count(handoff: dict, phase: str) -> int:
    return int(((handoff.get("summary") or {}).get("phase_counts") or {}).get(phase) or 0)


def action_count(operations: dict, kind: str) -> int:
    return sum(1 for action in operations.get("actions") or [] if action.get("kind") == kind)


def build_checks() -> dict:
    status = read_json(PROMO_STATUS, {})
    operations = read_json(PROMO_OPERATIONS, {})
    ledger = read_json(BLOCKER_LEDGER, {})
    handoff = read_json(HUMAN_HANDOFF, {})
    handoff_preview = read_json(HUMAN_HANDOFF_RESOLUTION_PREVIEW, {})
    unlock_sequence = read_json(PROMO_UNLOCK_SEQUENCE, {})
    scheduled = read_json(SCHEDULED_APPROVAL, {})
    platform = read_json(PLATFORM_REPAIR, {})
    tiktok_preflight = read_json(TIKTOK_PREFLIGHT, {})
    manual_distribution = read_json(MANUAL_DISTRIBUTION, {})
    manual_metrics = read_json(MANUAL_METRICS, {})
    store = read_json(STORE_HISTORY, {})
    executions = read_json(SOCIAL_EXECUTIONS, {})
    scheduler = read_json(SCHEDULER_DRY_RUN, {})
    refresh = read_json(REFRESH_RUN, {})

    ledger_rows = ledger.get("rows") or []
    ledger_summary = ledger.get("summary") or {}
    handoff_summary = handoff.get("summary") or {}
    handoff_preview_summary = handoff_preview.get("summary") or {}
    operations_summary = operations.get("summary") or {}
    status_health = status.get("health") or {}
    status_preview = (status.get("kpi") or {}).get("handoff_resolution_preview") or {}
    status_unlock_sequence = (status.get("kpi") or {}).get("promo_unlock_sequence") or {}
    unlock_summary = unlock_sequence.get("summary") or {}
    execution_summary = executions.get("summary") or {}
    scheduler_summary = scheduler.get("summary") or {}
    preflight_summary = tiktok_preflight.get("summary") or {}
    tiktok_repair = next(
        (row for row in platform.get("rows") or [] if str(row.get("platform") or "").lower() == "tiktok"),
        {},
    )
    checks = []

    ledger_category_total = sum(int(value or 0) for value in (ledger_summary.get("category_counts") or {}).values())
    checks.append(same_value(
        "ledger_open_count_matches_rows",
        len(ledger_rows),
        int(ledger_summary.get("open_blocker_count") or 0),
        "Blocker ledger summary should match row count.",
    ))
    checks.append(same_value(
        "ledger_category_total_matches_rows",
        len(ledger_rows),
        ledger_category_total,
        "Blocker category counts should account for every blocker row.",
    ))
    checks.append(same_value(
        "status_open_actions_match_operations",
        int(operations_summary.get("action_count") or 0),
        int(status_health.get("open_action_count") or 0),
        "Promo status open action count should mirror the operations packet.",
    ))
    checks.append(same_value(
        "approval_counts_match",
        int((scheduled.get("summary") or {}).get("approval_blocker_count") or 0),
        category_count(ledger, "approval"),
        "Scheduled approval packet should match approval blockers in the ledger.",
    ))
    checks.append(same_value(
        "executor_approval_count_matches_scheduled_packet",
        int(execution_summary.get("approval_needed_count") or 0),
        int((scheduled.get("summary") or {}).get("approval_blocker_count") or 0),
        "Executor approval-needed count should match the scheduled approval packet.",
    ))
    checks.append(same_value(
        "platform_repair_count_matches_ledger",
        int((platform.get("summary") or {}).get("platform_fix_count") or 0),
        category_count(ledger, "platform_repair"),
        "Platform repair packet should match platform repair blockers in the ledger.",
    ))
    checks.append(same_value(
        "executor_platform_fix_count_matches_platform_packet",
        int(execution_summary.get("platform_fix_needed_count") or 0),
        int((platform.get("summary") or {}).get("platform_fix_count") or 0),
        "Executor platform-fix count should match the platform repair packet.",
    ))
    checks.append(same_value(
        "tiktok_preflight_status_matches_platform_repair",
        tiktok_repair.get("preflight_status") or "",
        preflight_summary.get("status") or "",
        "TikTok platform repair row should mirror the setup preflight status.",
    ))
    checks.append(same_value(
        "tiktok_preflight_local_missing_matches_platform_repair",
        sorted(tiktok_repair.get("local_missing_secrets") or []),
        sorted(preflight_summary.get("local_missing_secrets") or []),
        "TikTok preflight local missing secrets should match the platform repair row.",
    ))
    checks.append(same_value(
        "tiktok_preflight_worker_missing_matches_platform_repair",
        sorted(tiktok_repair.get("missing_secrets") or []),
        sorted(preflight_summary.get("worker_missing_secrets") or []),
        "TikTok preflight worker missing secrets should match the platform repair row.",
    ))
    checks.append(same_value(
        "scheduler_blocked_matches_executor_attention",
        int(scheduler_summary.get("blocked_count") or 0),
        int(execution_summary.get("attention_count") or 0),
        "Scheduler dry-run blocked count should match executor attention count.",
    ))
    checks.append(same_value(
        "manual_distribution_count_matches_ledger",
        int((manual_distribution.get("summary") or {}).get("unlogged_manual_count") or 0),
        category_count(ledger, "manual_distribution"),
        "Manual distribution packet should match manual distribution blockers in the ledger.",
        severity="medium",
    ))
    checks.append(same_value(
        "manual_distribution_handoff_count_matches_packet",
        int((manual_distribution.get("summary") or {}).get("unlogged_manual_count") or 0),
        phase_count(handoff, "Manual distribution"),
        "Human handoff should include every unlogged manual distribution row.",
        severity="medium",
    ))
    checks.append(same_value(
        "manual_metric_batch_count_matches_ledger",
        int((manual_metrics.get("summary") or {}).get("priority_batch_count") or 0),
        category_count(ledger, "manual_metrics"),
        "Manual metric priority batch count should match manual metric blockers.",
        severity="medium",
    ))
    checks.append(same_value(
        "manual_metric_handoff_batch_count_matches_packet",
        int((manual_metrics.get("summary") or {}).get("priority_batch_count") or 0),
        phase_count(handoff, "Manual metrics"),
        "Human handoff should include every manual metric priority batch.",
        severity="medium",
    ))
    checks.append(same_value(
        "store_checks_match_checked_pending_services",
        int((store.get("summary") or {}).get("checked_pending") or 0),
        action_count(operations, "store_verification"),
        "Operations store checks should match checked-pending store services.",
        severity="medium",
    ))
    checks.append(same_value(
        "handoff_blocker_summary_matches_ledger",
        ledger_summary.get("open_blocker_count"),
        (handoff_summary.get("blocker_summary") or {}).get("open_blocker_count"),
        "Human handoff blocker summary should be copied from the blocker ledger.",
    ))
    ledger_projection = ledger_summary.get("next_resolution_projection") or {}
    handoff_projection = (handoff_summary.get("blocker_summary") or {}).get("next_resolution_projection") or {}
    checks.append(same_value(
        "handoff_projection_matches_ledger_projection",
        ledger_projection,
        handoff_projection,
        "Human handoff next-resolution projection should match the blocker ledger projection.",
    ))
    handoff_task_ids = sorted(task.get("id") for task in handoff.get("tasks") or [] if task.get("id"))
    handoff_preview_task_ids = sorted(preview.get("task_id") for preview in handoff_preview.get("previews") or [] if preview.get("task_id"))
    checks.append(same_value(
        "handoff_preview_task_alignment",
        handoff_task_ids,
        handoff_preview_task_ids,
        "Human handoff preview should include one preview row for every handoff task.",
    ))
    checks.append(same_value(
        "handoff_preview_worksheet_row_count_matches_handoff",
        int(((handoff.get("resolution_worksheet") or {}).get("row_count")) or 0),
        int(handoff_preview_summary.get("worksheet_row_count") or 0),
        "Human handoff preview worksheet row count should match the handoff packet worksheet summary.",
    ))
    checks.append(same_value(
        "handoff_preview_status_matches_status_kpi",
        handoff_preview_summary.get("status_counts") or {},
        status_preview.get("status_counts") or {},
        "Promo status handoff preview KPI should mirror preview status counts.",
    ))
    checks.append(same_value(
        "handoff_preview_counts_match_status_kpi",
        {
            "worksheet_row_count": int(handoff_preview_summary.get("worksheet_row_count") or 0),
            "preview_count": int(handoff_preview_summary.get("preview_count") or 0),
            "executed_preview_count": int(handoff_preview_summary.get("executed_preview_count") or 0),
            "skipped_preview_count": int(handoff_preview_summary.get("skipped_preview_count") or 0),
        },
        {
            "worksheet_row_count": int(status_preview.get("worksheet_row_count") or 0),
            "preview_count": int(status_preview.get("preview_count") or 0),
            "executed_preview_count": int(status_preview.get("executed_preview_count") or 0),
            "skipped_preview_count": int(status_preview.get("skipped_preview_count") or 0),
        },
        "Promo status handoff preview KPI should mirror preview summary counts.",
    ))
    preview_next_action = (
        "Review handoff preview health: "
        f"{int(status_preview.get('ready_preview_count') or 0)} preview-clean, "
        f"{int(status_preview.get('input_missing_count') or 0)} missing input, "
        f"{int(status_preview.get('warning_preview_count') or 0)} warning; "
        "see data/human_handoff_resolution_preview.json."
    )
    checks.append(verdict(
        "handoff_preview_next_action_matches_status",
        preview_next_action in (status.get("next_actions") or []),
        "Promo status next actions should expose the handoff preview health summary.",
        expected=preview_next_action,
        actual=status.get("next_actions") or [],
        severity="medium",
    ))
    roadmap = ledger_summary.get("blocker_unlock_roadmap") or []
    unlock_steps = unlock_sequence.get("steps") or []
    checks.append(same_value(
        "unlock_sequence_step_count_matches_roadmap",
        len(roadmap),
        int(unlock_summary.get("step_count") or 0),
        "Promo unlock sequence should include one step for every blocker roadmap phase.",
    ))
    checks.append(same_value(
        "unlock_sequence_order_matches_roadmap",
        [item.get("id") for item in roadmap],
        [step.get("id") for step in unlock_steps],
        "Promo unlock sequence order should mirror the blocker ledger roadmap order.",
    ))
    checks.append(same_value(
        "unlock_sequence_open_blockers_match_ledger",
        int(ledger_summary.get("open_blocker_count") or 0),
        int(unlock_summary.get("open_blocker_count") or 0),
        "Promo unlock sequence should mirror the blocker ledger open blocker count.",
    ))
    checks.append(verdict(
        "unlock_sequence_current_step_is_preview_ready",
        (unlock_summary.get("current_step_id") == "unlock-checked-scheduled-approval"
         and unlock_summary.get("current_gate_state") == "ready_for_human_review"),
        "Promo unlock sequence should lead with the checked scheduled approval batch while it is the highest-leverage safe review step.",
        expected={"current_step_id": "unlock-checked-scheduled-approval", "current_gate_state": "ready_for_human_review"},
        actual={"current_step_id": unlock_summary.get("current_step_id"), "current_gate_state": unlock_summary.get("current_gate_state")},
        severity="medium",
    ))
    checks.append(same_value(
        "unlock_sequence_matches_status_kpi",
        {
            "step_count": int(unlock_summary.get("step_count") or 0),
            "ready_for_human_review_count": int(unlock_summary.get("ready_for_human_review_count") or 0),
            "blocked_or_warning_count": int(unlock_summary.get("blocked_or_warning_count") or 0),
            "current_step_id": unlock_summary.get("current_step_id") or "",
            "current_gate_state": unlock_summary.get("current_gate_state") or "",
            "open_blocker_count": int(unlock_summary.get("open_blocker_count") or 0),
        },
        {
            "step_count": int(status_unlock_sequence.get("step_count") or 0),
            "ready_for_human_review_count": int(status_unlock_sequence.get("ready_for_human_review_count") or 0),
            "blocked_or_warning_count": int(status_unlock_sequence.get("blocked_or_warning_count") or 0),
            "current_step_id": status_unlock_sequence.get("current_step_id") or "",
            "current_gate_state": status_unlock_sequence.get("current_gate_state") or "",
            "open_blocker_count": int(status_unlock_sequence.get("open_blocker_count") or 0),
        },
        "Promo status should mirror the unlock sequence summary.",
    ))
    checks.append(verdict(
        "unlock_sequence_next_action_matches_status",
        any(action.startswith("Current unlock gate:") and status_unlock_sequence.get("source_path") in action for action in status.get("next_actions") or []),
        "Promo status next actions should expose the current unlock sequence gate.",
        expected="Current unlock gate action includes data/promo_unlock_sequence.json",
        actual=status.get("next_actions") or [],
        severity="medium",
    ))
    refresh_summary = refresh.get("summary") or {}
    required_failed = int(refresh_summary.get("required_failed") or 0)
    optional_failed = int(refresh_summary.get("optional_failed") or 0)
    allowed_failures = int(refresh_summary.get("allowed_failures") or 0)
    checks.append(verdict(
        "refresh_run_required_steps_successful",
        required_failed == 0 and optional_failed <= allowed_failures,
        "Latest promo admin refresh should have no required failures; tolerated optional capture failures stay visible in the refresh run summary.",
        expected={"required_failed": 0, "optional_failed_lte_allowed_failures": True},
        actual={"required_failed": required_failed, "optional_failed": optional_failed, "allowed_failures": allowed_failures},
    ))

    failed = [check for check in checks if check.get("status") != "pass"]
    summary = {
        "check_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "high_failed": sum(1 for check in failed if check.get("severity") == "high"),
        "medium_failed": sum(1 for check in failed if check.get("severity") == "medium"),
        "status": "pass" if not failed else "fail",
    }
    return {
        "summary": summary,
        "checks": checks,
        "source": {
            "promo_engine_status": str(PROMO_STATUS.relative_to(ROOT)),
            "promo_operations_packet": str(PROMO_OPERATIONS.relative_to(ROOT)),
            "promotion_blocker_ledger": str(BLOCKER_LEDGER.relative_to(ROOT)),
            "human_handoff_packet": str(HUMAN_HANDOFF.relative_to(ROOT)),
            "human_handoff_resolution_preview": str(HUMAN_HANDOFF_RESOLUTION_PREVIEW.relative_to(ROOT)),
            "promo_unlock_sequence": str(PROMO_UNLOCK_SEQUENCE.relative_to(ROOT)),
            "scheduled_approval_packet": str(SCHEDULED_APPROVAL.relative_to(ROOT)),
            "platform_repair_status": str(PLATFORM_REPAIR.relative_to(ROOT)),
            "tiktok_setup_preflight": str(TIKTOK_PREFLIGHT.relative_to(ROOT)),
            "manual_distribution_packet": str(MANUAL_DISTRIBUTION.relative_to(ROOT)),
            "manual_metric_collection_packet": str(MANUAL_METRICS.relative_to(ROOT)),
            "store_verification_history": str(STORE_HISTORY.relative_to(ROOT)),
            "social_execution_snapshot": str(SOCIAL_EXECUTIONS.relative_to(ROOT)),
            "social_scheduler_dry_run": str(SCHEDULER_DRY_RUN.relative_to(ROOT)),
            "promo_admin_refresh_run": str(REFRESH_RUN.relative_to(ROOT)),
        },
    }


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Promo Consistency Audit - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Status: **{summary['status']}**",
        f"- Checks: **{summary['passed']} / {summary['check_count']}** passed",
        f"- Failed checks: **{summary['failed']}**",
        f"- High severity failures: **{summary['high_failed']}**",
        f"- Medium severity failures: **{summary['medium_failed']}**",
        "",
        "## Checks",
    ]
    for check in payload["checks"]:
        lines.append(f"- **{check['name']}**: `{check['status']}`")
        lines.append(f"  - {check['detail']}")
        if check.get("status") != "pass":
            lines.append(f"  - Expected: `{check.get('expected')}`")
            lines.append(f"  - Actual: `{check.get('actual')}`")
    lines.extend([
        "",
        "## Guardrails",
        "- This audit does not mutate promotion, posting, approval, metrics, or secrets state.",
        "- A failed check means generated admin surfaces disagree and should be inspected before acting on commands.",
        "",
    ])
    return "\n".join(lines)


def replace_json_embed(html: str, block_id: str, payload) -> str:
    marker = f'<script type="application/json" id="{block_id}">'
    end_marker = "</script>"
    encoded = json.dumps(payload, indent=2, ensure_ascii=False)
    start = html.find(marker)
    if start == -1:
        return html.replace("<script>", f"\n{marker}{encoded}{end_marker}\n\n<script>", 1)
    start_content = start + len(marker)
    end = html.find(end_marker, start_content)
    if end == -1:
        raise RuntimeError(f"Could not find end marker for {block_id}")
    return html[:start_content] + encoded + html[end:]


def replace_text_embed(html: str, block_id: str, content: str) -> str:
    marker = f'<script type="text/plain" id="{block_id}">'
    end_marker = "</script>"
    start = html.find(marker)
    if start == -1:
        return html.replace("<script>", f"\n{marker}{content.rstrip()}{end_marker}\n\n<script>", 1)
    start_content = start + len(marker)
    end = html.find(end_marker, start_content)
    if end == -1:
        raise RuntimeError(f"Could not find end marker for {block_id}")
    return html[:start_content] + content.rstrip() + html[end:]


def sync_admin(payload: dict, markdown: str) -> None:
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    html = replace_json_embed(html, "embedded-promo-consistency-audit", payload)
    html = replace_text_embed(html, "embedded-promo-consistency-audit-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        **build_checks(),
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(payload)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(payload, markdown)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), **payload["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
