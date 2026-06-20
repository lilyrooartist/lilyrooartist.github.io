#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLOCKER_LEDGER = ROOT / "data" / "promotion_blocker_ledger.json"
SCHEDULED_APPROVAL = ROOT / "data" / "scheduled_approval_packet.json"
MANUAL_DISTRIBUTION = ROOT / "data" / "manual_distribution_packet.json"
APPROVAL_RUNWAY = ROOT / "data" / "approval_runway.json"
MANUAL_METRICS = ROOT / "data" / "manual_metric_collection_packet.json"
PLATFORM_REPAIR = ROOT / "data" / "platform_repair_status.json"
TIKTOK_PREFLIGHT = ROOT / "data" / "tiktok_setup_preflight.json"
BACKLOG_RESCHEDULE = ROOT / "data" / "backlog_reschedule_preview.json"
OUT = ROOT / "data" / "human_handoff_packet.json"
WORKSHEET = ROOT / "data" / "human_handoff_resolution_worksheet.csv"
REPORT = ROOT / "admin" / "reports" / "human-handoff-packet.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"

WORKSHEET_FIELDS = [
    "task_id",
    "phase",
    "owner",
    "urgency",
    "status",
    "title",
    "input_needed",
    "worksheet_reference",
    "source_path",
    "preview_command",
    "apply_after_review_command",
    "completion_evidence",
    "guardrail",
]


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def command_task(
    task_id: str,
    title: str,
    phase: str,
    owner: str,
    urgency: str,
    status: str,
    detail: str,
    preview_command: str = "",
    apply_command: str = "",
    source_path: str = "",
    impact: dict | None = None,
    links: list[dict] | None = None,
    guardrail: str = "",
) -> dict:
    return {
        "id": task_id,
        "title": title,
        "phase": phase,
        "owner": owner,
        "urgency": urgency,
        "status": status,
        "detail": detail,
        "preview_command": preview_command,
        "apply_command": apply_command,
        "source_path": source_path,
        "impact": impact or {},
        "links": links or [],
        "guardrail": guardrail,
    }


def approval_tasks(packet: dict, blocker_summary: dict) -> list[dict]:
    summary = packet.get("summary") or {}
    decision_manifest = packet.get("approval_decision_manifest") or {}
    apply_manifest = packet.get("approval_apply_manifest") or {}
    review_runbook = packet.get("approval_review_runbook") or {}
    checked_ids = summary.get("checked_batch_ids") or []
    if not checked_ids:
        return []
    effect = summary.get("checked_batch_effect") or {}
    rows_by_id = {
        row.get("id"): row
        for row in packet.get("rows") or []
        if row.get("id")
    }
    checked_rows = [rows_by_id.get(post_id) or {} for post_id in checked_ids]
    projection = blocker_summary.get("next_resolution_projection") or {}
    auto_rows_unblocked = projection.get("auto_rows_unblocked")
    manual_rows_unblocked = projection.get("manual_rows_unblocked")
    if auto_rows_unblocked is None:
        auto_rows_unblocked = sum(1 for row in checked_rows if row.get("execution_mode") == "auto")
    if manual_rows_unblocked is None:
        manual_rows_unblocked = sum(1 for row in checked_rows if row.get("execution_mode") == "manual")
    return [
        command_task(
            "approve-checked-scheduled-batch",
            "Review and approve checked scheduled batch",
            "Approval",
            "tod",
            "high",
            "waiting_for_review",
            "Review the checked rows, then apply the guarded batch command. Failed review rows stay excluded.",
            summary.get("checked_batch_preview_command") or "",
            summary.get("checked_batch_apply_command") or "",
            str(SCHEDULED_APPROVAL.relative_to(ROOT)),
            {
                "checked_ids": checked_ids,
                "blocked_ids_retained": summary.get("blocked_review_ids") or [],
                "blockers_resolved": projection.get("blockers_resolved") or len(checked_ids),
                "approval_blockers_before": projection.get("approval_blockers_before") or summary.get("approval_blocker_count") or 0,
                "approval_blockers_after": projection.get("approval_blockers_after") if projection.get("approval_blockers_after") is not None else len(summary.get("blocked_review_ids") or []),
                "change_count": effect.get("change_count") or 0,
                "auto_rows_unblocked": auto_rows_unblocked,
                "manual_rows_unblocked": manual_rows_unblocked,
                "approval_decision_manifest": decision_manifest,
                "approval_apply_manifest": apply_manifest,
                "approval_review_runbook": review_runbook,
                "pre_apply_checklist": apply_manifest.get("pre_apply_checklist") or [],
                "post_apply_evidence": apply_manifest.get("post_apply_evidence") or [],
                "apply_guardrails": apply_manifest.get("guardrails") or [],
                "review_runbook_steps": review_runbook.get("steps") or [],
                "review_checklist": review_runbook.get("review_checklist") or [],
                "decision_ready_ids": decision_manifest.get("ready_ids") or [],
                "decision_held_ids": decision_manifest.get("held_ids") or [],
                "decision_guardrail": decision_manifest.get("guardrail") or "",
            },
            guardrail="Use --checked-batch so only rows that passed review checks are approved.",
        )
    ]


def manual_distribution_tasks(packet: dict) -> list[dict]:
    rows = packet.get("rows") or []
    tasks = []
    for row in rows:
        status = row.get("distribution_status") or ""
        if row.get("logged"):
            continue
        links = []
        if row.get("asset_download_url"):
            links.append({"label": "asset", "url": row.get("asset_download_url")})
        tasks.append(command_task(
            f"manual-distribution-{row.get('id')}",
            f"Post {row.get('release') or 'release'} to {row.get('platform') or 'manual channel'}",
            "Manual distribution",
            "tod",
            "medium",
            status or "waiting_for_review",
            "Review the packaged copy, approve if appropriate, post manually, then log the public URL.",
            row.get("approval_preview_command") or "",
            row.get("approval_command") or "",
            str(MANUAL_DISTRIBUTION.relative_to(ROOT)),
            {
                "post_id": row.get("id") or "",
                "release": row.get("release") or "",
                "log_preview_command": row.get("log_preview_command") or "",
                "log_apply_command": row.get("log_apply_command") or "",
                "requires_public_url": (row.get("log_effect") or {}).get("requires_public_url", True),
            },
            links=links,
            guardrail="Do not log a manual post until a real public URL exists.",
        ))
    return tasks


def manual_metric_tasks(packet: dict) -> list[dict]:
    tasks = []
    summary = packet.get("summary") or {}
    completion_manifest = packet.get("metric_completion_manifest") or {}
    for batch in packet.get("priority_batches") or []:
        fields = batch.get("fields") or []
        priority = int(batch.get("priority") or 4)
        label = batch.get("label") or "manual metrics"
        tasks.append(command_task(
            f"manual-metrics-priority-{priority}",
            f"Fill priority {priority} metrics: {label}",
            "Manual metrics",
            "tod",
            "low",
            batch.get("status") or "waiting_for_manual_values",
            f"Collect {len(fields)} field(s) across {', '.join(batch.get('platforms') or [])}, fill the worksheet rows, preview import, then refresh Admin.",
            batch.get("worksheet_import_preview_command") or summary.get("worksheet_import_preview_command") or "",
            batch.get("worksheet_import_command") or summary.get("worksheet_import_command") or "",
            str(MANUAL_METRICS.relative_to(ROOT)),
            {
                "priority": priority,
                "label": label,
                "field_count": len(fields),
                "waiting_count": batch.get("waiting_count") or 0,
                "ready_to_import_count": batch.get("ready_to_import_count") or 0,
                "platforms": batch.get("platforms") or [],
                "access_levels": batch.get("access_levels") or [],
                "csv_rows": batch.get("csv_rows") or [],
                "pending_assignments": [f"{field.get('platform')}.{field.get('field')}" for field in fields if field.get("platform") and field.get("field")],
                "evidence_hints": [field.get("evidence_hint") for field in fields if field.get("evidence_hint")],
                "metric_completion_manifest": completion_manifest,
                "completion_checklist": completion_manifest.get("operator_checklist") or [],
                "completion_evidence": completion_manifest.get("completion_evidence") or [],
                "completion_guardrails": completion_manifest.get("guardrails") or [],
            },
            guardrail="Only import nonnegative numeric values copied from the named source; leave unknown values blank instead of guessing.",
        ))
    return tasks


def platform_setup_tasks(packet: dict, tiktok_preflight: dict) -> list[dict]:
    tasks = []
    preflight_summary = tiktok_preflight.get("summary") or {}
    for row in packet.get("rows") or []:
        is_tiktok = str(row.get("platform") or "").lower() == "tiktok"
        impact = {
            "platform": row.get("platform") or "",
            "missing_secrets": row.get("missing_secrets") or [],
            "local_missing_secrets": row.get("local_missing_secrets") or [],
            "public_posting_approved": row.get("public_posting_approved"),
            "repair_checklist_blocked_count": row.get("repair_checklist_blocked_count") or 0,
        }
        if is_tiktok:
            impact.update({
                "preflight_status": preflight_summary.get("status") or row.get("preflight_status") or "",
                "preflight_blocked_count": preflight_summary.get("blocked_count") if preflight_summary.get("blocked_count") is not None else row.get("preflight_blocked_count"),
                "ready_to_push_worker_secrets": preflight_summary.get("ready_to_push_worker_secrets"),
                "ready_to_post_publicly": preflight_summary.get("ready_to_post_publicly"),
                "preflight_report": str((ROOT / "admin" / "reports" / "tiktok-setup-preflight.md").relative_to(ROOT)),
                "preflight_command": "python3 scripts/build_tiktok_setup_preflight.py",
            })
        tasks.append(command_task(
            f"platform-setup-{row.get('post_id') or row.get('platform')}",
            f"Repair {row.get('platform') or 'platform'} executor",
            "Platform setup",
            "tod",
            "high",
            row.get("status") or "blocked",
            row.get("repair_action") or row.get("error_summary") or "Complete platform repair, then refresh Admin.",
            row.get("preview_command") or "",
            row.get("apply_command") or "",
            str(PLATFORM_REPAIR.relative_to(ROOT)),
            impact,
            guardrail="Run the TikTok preflight before pushing secrets; push worker secrets only after local OAuth/public posting setup is complete." if is_tiktok else "Push worker secrets only after local OAuth/public posting setup is complete.",
        ))
    return tasks


def backlog_tasks(packet: dict) -> list[dict]:
    summary = packet.get("summary") or {}
    clearance_manifest = packet.get("backlog_clearance_manifest") or {}
    if not int(summary.get("approved_backlog_count") or 0):
        return []
    return [
        command_task(
            "backlog-reschedule",
            "Preview approved backlog reschedule",
            "Backlog recovery",
            "tod" if summary.get("apply_allowed_without_override") else "external_platform",
            "high",
            "blocked" if not summary.get("apply_allowed_without_override") else "ready_to_preview",
            summary.get("apply_blocked_reason") or "Preview a new schedule for approved past-due posts.",
            summary.get("preview_command") or "",
            summary.get("apply_command") or "",
            str(BACKLOG_RESCHEDULE.relative_to(ROOT)),
            {
                "approved_backlog_count": summary.get("approved_backlog_count") or 0,
                "blocked_backlog_count": summary.get("blocked_backlog_count") or 0,
                "blocked_apply_command": summary.get("blocked_apply_command") or "",
                "override_apply_command": summary.get("override_apply_command") or "",
                "backlog_clearance_manifest": clearance_manifest,
                "clearance_checklist": clearance_manifest.get("operator_checklist") or [],
                "completion_evidence": clearance_manifest.get("completion_evidence") or [],
                "clearance_guardrails": clearance_manifest.get("guardrails") or [],
            },
            guardrail="Normal apply stays hidden until known executor/platform blockers clear.",
        )
    ]


def first_task(tasks: list[dict], phase: str) -> dict:
    return next((task for task in tasks if task.get("phase") == phase), {})


def tasks_for_phase(tasks: list[dict], phase: str) -> list[dict]:
    return [task for task in tasks if task.get("phase") == phase]


def command_sequence(preview_command: str = "", apply_command: str = "", verify_command: str = "") -> list[dict]:
    sequence = []
    if preview_command:
        sequence.append({
            "step": "preview",
            "command": preview_command,
            "required_before_apply": True,
        })
    if apply_command:
        sequence.append({
            "step": "apply_after_review",
            "command": apply_command,
            "required_before_apply": False,
        })
    if verify_command:
        sequence.append({
            "step": "verify",
            "command": verify_command,
            "required_before_apply": False,
        })
    return sequence


def task_input_needed(task: dict) -> tuple[str, str]:
    phase = task.get("phase") or ""
    impact = task.get("impact") or {}
    if phase == "Approval":
        ids = impact.get("checked_ids") or []
        return (
            "human_review_decision",
            f"review checked scheduled ids: {', '.join(ids)}" if ids else "review checked scheduled batch",
        )
    if phase == "Manual distribution":
        post_id = impact.get("post_id") or task.get("id") or ""
        if task.get("status") == "ready_for_manual_post":
            return ("public_post_url", f"paste public URL for {post_id} into data/manual_distribution_url_template.csv")
        return (
            "manual_post_review_and_public_url",
            f"approve/post {post_id}, then paste public URL into data/manual_distribution_url_template.csv",
        )
    if phase == "Manual metrics":
        rows = impact.get("csv_rows") or []
        row_text = ", ".join(str(row) for row in rows)
        return (
            "private_metric_values",
            f"fill data/manual_metric_entry_template.csv rows: {row_text}" if row_text else "fill data/manual_metric_entry_template.csv",
        )
    if phase == "Platform setup":
        missing = impact.get("missing_secrets") or impact.get("local_missing_secrets") or []
        secret_names = ", ".join(missing)
        return (
            "local_secret_presence_and_public_posting_approval",
            f"populate local env from data/tiktok_secret_handoff_template.env for names: {secret_names}" if secret_names else "complete platform setup preflight",
        )
    if phase == "Backlog recovery":
        return (
            "clearance_confirmation",
            "complete backlog clearance checklist in data/backlog_reschedule_preview.json",
        )
    return ("operator_review", task.get("source_path") or "")


def build_resolution_rows(tasks: list[dict], action_docket: dict) -> list[dict]:
    evidence_by_task: dict[str, str] = {}
    for item in action_docket.get("checklist") or []:
        evidence = item.get("completion_evidence") or ""
        for task_id in item.get("task_ids") or []:
            if task_id:
                evidence_by_task[task_id] = evidence
    rows = []
    for task in tasks:
        input_needed, worksheet_reference = task_input_needed(task)
        task_id = task.get("id") or ""
        rows.append({
            "task_id": task_id,
            "phase": task.get("phase") or "",
            "owner": task.get("owner") or "",
            "urgency": task.get("urgency") or "",
            "status": task.get("status") or "",
            "title": task.get("title") or "",
            "input_needed": input_needed,
            "worksheet_reference": worksheet_reference,
            "source_path": task.get("source_path") or "",
            "preview_command": task.get("preview_command") or "",
            "apply_after_review_command": task.get("apply_command") or "",
            "completion_evidence": evidence_by_task.get(task_id) or "",
            "guardrail": task.get("guardrail") or "",
        })
    return rows


def write_resolution_worksheet(rows: list[dict]) -> None:
    with WORKSHEET.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=WORKSHEET_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_action_docket(tasks: list[dict], blocker_summary: dict, approval_runway: dict) -> dict:
    projection = blocker_summary.get("next_resolution_projection") or {}
    roadmap = blocker_summary.get("blocker_unlock_roadmap") or []
    manual_approval_docket = approval_runway.get("manual_approval_docket") or {}
    manual_distribution = tasks_for_phase(tasks, "Manual distribution")
    manual_metrics = tasks_for_phase(tasks, "Manual metrics")
    platform_setup = tasks_for_phase(tasks, "Platform setup")
    backlog = first_task(tasks, "Backlog recovery")
    approval = first_task(tasks, "Approval")
    metric_field_count = sum(int((task.get("impact") or {}).get("field_count") or 0) for task in manual_metrics)
    manual_post_count = len(manual_distribution)
    blocked_platform_count = len([task for task in platform_setup if task.get("status") == "blocked"])
    manual_preview_command = manual_approval_docket.get("preview_command") or (manual_distribution[0].get("preview_command") if manual_distribution else "")
    manual_apply_command = manual_approval_docket.get("apply_command") or (manual_distribution[0].get("apply_command") if manual_distribution else "")
    manual_guardrail = manual_approval_docket.get("guardrail") or "Post manually first, then log only real public URLs."
    approval_preview_command = approval.get("preview_command") or projection.get("preview_command") or ""
    approval_apply_command = approval.get("apply_command") or projection.get("apply_command") or ""
    approval_impact = approval.get("impact") or {}
    platform_preview_command = platform_setup[0].get("preview_command") if platform_setup else ""
    platform_apply_command = platform_setup[0].get("apply_command") if platform_setup else ""
    metric_preview_command = manual_metrics[0].get("preview_command") if manual_metrics else ""
    metric_apply_command = manual_metrics[0].get("apply_command") if manual_metrics else ""
    metric_manifest = (manual_metrics[0].get("impact") or {}).get("metric_completion_manifest") if manual_metrics else {}
    backlog_preview_command = backlog.get("preview_command") if backlog else ""
    backlog_apply_command = backlog.get("apply_command") if backlog else ""
    backlog_manifest = (backlog.get("impact") or {}).get("backlog_clearance_manifest") if backlog else {}
    checklist = [
        {
            "id": "review-checked-approval-batch",
            "label": "Review checked approval batch",
            "state": "ready_for_review" if approval else "not_available",
            "owner": "tod",
            "task_ids": [approval.get("id")] if approval else [],
            "blockers_resolved": projection.get("blockers_resolved") or 0,
            "decision_ready_ids": approval_impact.get("decision_ready_ids") or [],
            "decision_held_ids": approval_impact.get("decision_held_ids") or [],
            "approval_decision_manifest": approval_impact.get("approval_decision_manifest") or {},
            "approval_apply_manifest": approval_impact.get("approval_apply_manifest") or {},
            "approval_review_runbook": approval_impact.get("approval_review_runbook") or {},
            "pre_apply_checklist": approval_impact.get("pre_apply_checklist") or [],
            "post_apply_evidence": approval_impact.get("post_apply_evidence") or [],
            "apply_guardrails": approval_impact.get("apply_guardrails") or [],
            "review_runbook_steps": approval_impact.get("review_runbook_steps") or [],
            "review_checklist": approval_impact.get("review_checklist") or [],
            "preview_command": approval_preview_command,
            "apply_command": approval_apply_command,
            "command_sequence": command_sequence(approval_preview_command, approval_apply_command, "python3 scripts/refresh_promo_admin.py"),
            "completion_evidence": "data/scheduled_approval_packet.json should show fewer approval blockers, and data/social_scheduler_dry_run.json should no longer block the approved Instagram row on not_approved.",
            "next_step_after_apply": "Run the safe admin refresh, then manually post/log any newly approved YouTube Community row before treating the published log as current.",
            "guardrail": approval.get("guardrail") or projection.get("guardrail") or "",
        },
        {
            "id": "manual-posting-review",
            "label": "Review and post manual distribution rows",
            "state": "needs_review" if manual_distribution else "clear",
            "owner": "tod",
            "task_ids": [task["id"] for task in manual_distribution],
            "blockers_resolved": manual_post_count,
            "ready_ids": manual_approval_docket.get("ready_ids") or [],
            "blocked_ids": manual_approval_docket.get("blocked_ids") or [],
            "preview_command": manual_preview_command,
            "apply_command": manual_apply_command,
            "command_sequence": command_sequence(manual_preview_command, manual_apply_command, "python3 scripts/refresh_promo_admin.py"),
            "completion_evidence": "data/manual_distribution_packet.json should move approved rows from review_queue toward postable manual distribution, and data/published_log_reconciliation.json should remain gated until public URLs are logged.",
            "next_step_after_apply": "Post each approved YouTube Community row manually, then log its public URL with scripts/log_manual_distribution.py.",
            "guardrail": f"{manual_guardrail} Post manually first, then log only real public URLs.",
        },
        {
            "id": "platform-repair-gate",
            "label": "Repair blocked platform executor setup",
            "state": "blocked" if blocked_platform_count else "clear",
            "owner": "tod",
            "task_ids": [task["id"] for task in platform_setup],
            "blockers_resolved": blocked_platform_count,
            "preview_command": platform_preview_command,
            "apply_command": platform_apply_command,
            "command_sequence": command_sequence(platform_preview_command, platform_apply_command, "python3 scripts/refresh_promo_admin.py"),
            "completion_evidence": "data/tiktok_setup_preflight.json should report ready_to_push_worker_secrets and ready_to_post_publicly before TikTok backlog work is allowed.",
            "next_step_after_apply": "Recapture admin state and only then revisit TikTok approval or backlog reschedule rows.",
            "guardrail": "Run preflight and confirm local OAuth/public-posting setup before pushing secrets.",
        },
        {
            "id": "manual-metric-worksheet",
            "label": "Fill and import manual metric worksheet",
            "state": "needs_values" if metric_field_count else "clear",
            "owner": "tod",
            "task_ids": [task["id"] for task in manual_metrics],
            "blockers_resolved": metric_field_count,
            "field_count": metric_field_count,
            "batch_count": len(manual_metrics),
            "metric_completion_manifest": metric_manifest or {},
            "completion_checklist": (metric_manifest or {}).get("operator_checklist") or [],
            "completion_guardrails": (metric_manifest or {}).get("guardrails") or [],
            "batches": [
                {
                    "priority": (task.get("impact") or {}).get("priority"),
                    "label": (task.get("impact") or {}).get("label"),
                    "field_count": (task.get("impact") or {}).get("field_count"),
                    "access_levels": (task.get("impact") or {}).get("access_levels") or [],
                    "csv_rows": (task.get("impact") or {}).get("csv_rows") or [],
                }
                for task in manual_metrics
            ],
            "preview_command": metric_preview_command,
            "apply_command": metric_apply_command,
            "command_sequence": command_sequence(metric_preview_command, metric_apply_command, "python3 scripts/refresh_promo_admin.py"),
            "completion_evidence": "data/manual_metric_collection_packet.json should reduce pending_field_count, and data/metrics_history.json should preserve the imported metrics in the latest snapshot.",
            "next_step_after_apply": "Rebuild the weekly report and confirm lilyroo.com/admin shows fewer pending manual metric fields.",
            "guardrail": "Import only collected numeric values; leave unknown cells blank.",
        },
        {
            "id": "backlog-reschedule-gate",
            "label": "Reschedule approved backlog after blockers clear",
            "state": "blocked" if backlog and backlog.get("owner") == "external_platform" else ("ready" if backlog else "clear"),
            "owner": backlog.get("owner") or "tod",
            "task_ids": [backlog.get("id")] if backlog else [],
            "blockers_resolved": (backlog.get("impact") or {}).get("approved_backlog_count") or 0,
            "backlog_clearance_manifest": backlog_manifest or {},
            "clearance_checklist": (backlog_manifest or {}).get("operator_checklist") or [],
            "clearance_guardrails": (backlog_manifest or {}).get("guardrails") or [],
            "preview_command": backlog_preview_command,
            "apply_command": backlog_apply_command,
            "command_sequence": command_sequence(backlog_preview_command, backlog_apply_command, "python3 scripts/refresh_promo_admin.py"),
            "completion_evidence": "data/backlog_reschedule_preview.json should show normal_apply_gate clear before any non-override apply command is exposed.",
            "next_step_after_apply": "Refresh admin and confirm approved past-due posts have future scheduled_at values before relying on the scheduler.",
            "guardrail": backlog.get("guardrail") or "Do not apply blocked backlog reschedules without clearing platform readiness.",
        },
    ]
    ready = [item for item in checklist if item["state"] in {"ready", "ready_for_review", "needs_review", "needs_values"}]
    blocked = [item for item in checklist if item["state"] == "blocked"]
    return {
        "source": "data/human_handoff_packet.json",
        "roadmap_step_count": len(roadmap),
        "task_count": len(tasks),
        "ready_step_count": len(ready),
        "blocked_step_count": len(blocked),
        "manual_post_count": manual_post_count,
        "manual_metric_field_count": metric_field_count,
        "first_ready_step": ready[0] if ready else {},
        "blocked_steps": blocked,
        "checklist": checklist,
    }


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    docket = payload.get("action_docket") or {}
    worksheet = payload.get("resolution_worksheet") or {}
    lines = [
        "# Human Handoff Packet - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Open handoff tasks: **{summary['task_count']}**",
        f"- Tod-owned tasks: **{summary['owner_counts'].get('tod', 0)}**",
        f"- External/platform-gated tasks: **{summary['owner_counts'].get('external_platform', 0)}**",
        f"- High urgency tasks: **{summary['urgency_counts'].get('high', 0)}**",
        f"- Low urgency tasks: **{summary['urgency_counts'].get('low', 0)}**",
        "",
        "## Action Docket",
        f"- Ready steps: **{docket.get('ready_step_count', 0)}**",
        f"- Blocked steps: **{docket.get('blocked_step_count', 0)}**",
        f"- Manual posts packaged: **{docket.get('manual_post_count', 0)}**",
        f"- Manual metric fields: **{docket.get('manual_metric_field_count', 0)}**",
        f"- Resolution worksheet: `{worksheet.get('path') or str(WORKSHEET.relative_to(ROOT))}` ({worksheet.get('row_count', 0)} row(s))",
        "",
    ]
    for item in docket.get("checklist") or []:
        lines.append(f"- **{item['label']}** (`{item['state']}`)")
        lines.append(f"  - Owner: `{item['owner']}`; tasks: **{len(item.get('task_ids') or [])}**; blockers resolved: **{item.get('blockers_resolved', 0)}**")
        if item.get("field_count"):
            lines.append(f"  - Fields: **{item['field_count']}**")
        if item.get("batch_count"):
            lines.append(f"  - Batches: **{item['batch_count']}**")
        for batch in item.get("batches") or []:
            bits = []
            if batch.get("access_levels"):
                bits.append(f"access: {', '.join(batch['access_levels'])}")
            if batch.get("csv_rows"):
                bits.append(f"rows: {', '.join(str(value) for value in batch['csv_rows'])}")
            suffix = f" ({'; '.join(bits)})" if bits else ""
            lines.append(f"  - Priority {batch.get('priority')}: {batch.get('label')} - **{batch.get('field_count', 0)}** field(s){suffix}")
        if item.get("ready_ids"):
            lines.append(f"  - Ready IDs: `{', '.join(item['ready_ids'])}`")
        if item.get("blocked_ids"):
            lines.append(f"  - Blocked IDs: `{', '.join(item['blocked_ids'])}`")
        if item.get("decision_ready_ids") or item.get("decision_held_ids"):
            ready_ids = ", ".join(item.get("decision_ready_ids") or []) or "none"
            held_ids = ", ".join(item.get("decision_held_ids") or []) or "none"
            lines.append(f"  - Decision manifest: ready `{ready_ids}`; held `{held_ids}`")
        if item.get("review_runbook_steps") is not None:
            lines.append(
                f"  - Review runbook: **{len(item.get('review_runbook_steps') or [])}** step(s), "
                f"**{len(item.get('review_checklist') or [])}** checklist row(s)"
            )
        if item.get("preview_command"):
            lines.append(f"  - Preview/check: `{item['preview_command']}`")
        if item.get("apply_command"):
            lines.append(f"  - Apply after review: `{item['apply_command']}`")
        for sequence_item in item.get("command_sequence") or []:
            if sequence_item.get("command"):
                lines.append(f"  - Sequence {sequence_item.get('step')}: `{sequence_item['command']}`")
        if item.get("completion_evidence"):
            lines.append(f"  - Completion evidence: {item['completion_evidence']}")
        if item.get("next_step_after_apply"):
            lines.append(f"  - Next after apply: {item['next_step_after_apply']}")
        if item.get("guardrail"):
            lines.append(f"  - Guardrail: {item['guardrail']}")
    lines.extend([
        "",
        "## Tasks",
    ])
    for task in payload["tasks"]:
        lines.append(f"- **{task['title']}** (`{task['id']}`)")
        lines.append(f"  - Phase: `{task['phase']}`; owner: `{task['owner']}`; status: `{task['status']}`; urgency: `{task['urgency']}`")
        if task.get("detail"):
            lines.append(f"  - Detail: {task['detail']}")
        if task.get("preview_command"):
            lines.append(f"  - Preview/check: `{task['preview_command']}`")
        if task.get("apply_command"):
            lines.append(f"  - Apply after review: `{task['apply_command']}`")
        for link in task.get("links") or []:
            if link.get("url"):
                lines.append(f"  - {link.get('label') or 'Link'}: {link['url']}")
        if task.get("guardrail"):
            lines.append(f"  - Guardrail: {task['guardrail']}")
    lines.extend([
        "",
        "## Guardrails",
        "- This packet is review-only and does not approve, post, publish, push secrets, or import metrics.",
        "- Preview commands should run before any apply command.",
        "- Manual metrics and public post URLs should come from real platform surfaces, not estimates.",
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
    html = replace_json_embed(html, "embedded-human-handoff-packet", payload)
    html = replace_text_embed(html, "embedded-human-handoff-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    blocker_summary = (read_json(BLOCKER_LEDGER, {}).get("summary") or {})
    approval_runway = read_json(APPROVAL_RUNWAY, {})
    tasks = []
    tasks.extend(approval_tasks(read_json(SCHEDULED_APPROVAL, {}), blocker_summary))
    tasks.extend(manual_distribution_tasks(read_json(MANUAL_DISTRIBUTION, {})))
    tasks.extend(platform_setup_tasks(read_json(PLATFORM_REPAIR, {}), read_json(TIKTOK_PREFLIGHT, {})))
    tasks.extend(backlog_tasks(read_json(BACKLOG_RESCHEDULE, {})))
    tasks.extend(manual_metric_tasks(read_json(MANUAL_METRICS, {})))
    urgency_order = {"high": 0, "medium": 1, "low": 2}
    owner_order = {"tod": 0, "external_platform": 1, "codex": 2}
    tasks.sort(key=lambda item: (urgency_order.get(item["urgency"], 9), owner_order.get(item["owner"], 9), item["phase"], item["id"]))
    owner_counts = {}
    urgency_counts = {}
    phase_counts = {}
    for task in tasks:
        owner_counts[task["owner"]] = owner_counts.get(task["owner"], 0) + 1
        urgency_counts[task["urgency"]] = urgency_counts.get(task["urgency"], 0) + 1
        phase_counts[task["phase"]] = phase_counts.get(task["phase"], 0) + 1
    action_docket = build_action_docket(tasks, blocker_summary, approval_runway)
    resolution_rows = build_resolution_rows(tasks, action_docket)
    write_resolution_worksheet(resolution_rows)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "promotion_blocker_ledger": str(BLOCKER_LEDGER.relative_to(ROOT)),
            "scheduled_approval": str(SCHEDULED_APPROVAL.relative_to(ROOT)),
            "manual_distribution": str(MANUAL_DISTRIBUTION.relative_to(ROOT)),
            "approval_runway": str(APPROVAL_RUNWAY.relative_to(ROOT)),
            "manual_metrics": str(MANUAL_METRICS.relative_to(ROOT)),
            "platform_repair": str(PLATFORM_REPAIR.relative_to(ROOT)),
            "tiktok_setup_preflight": str(TIKTOK_PREFLIGHT.relative_to(ROOT)),
            "backlog_reschedule": str(BACKLOG_RESCHEDULE.relative_to(ROOT)),
            "resolution_worksheet": str(WORKSHEET.relative_to(ROOT)),
        },
        "summary": {
            "task_count": len(tasks),
            "owner_counts": dict(sorted(owner_counts.items())),
            "urgency_counts": dict(sorted(urgency_counts.items())),
            "phase_counts": dict(sorted(phase_counts.items())),
            "blocker_summary": blocker_summary,
        },
        "action_docket": action_docket,
        "resolution_worksheet": {
            "path": str(WORKSHEET.relative_to(ROOT)),
            "row_count": len(resolution_rows),
            "fieldnames": WORKSHEET_FIELDS,
            "safe_mode": True,
            "redaction": "Worksheet rows collect prompts, commands, and evidence targets only; private metric values, public URLs, approval decisions, and secret values stay out of generated reports.",
        },
        "tasks": tasks,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(payload)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(payload, markdown)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), "tasks": len(tasks)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
