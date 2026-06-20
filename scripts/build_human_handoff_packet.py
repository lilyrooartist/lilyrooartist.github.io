#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLOCKER_LEDGER = ROOT / "data" / "promotion_blocker_ledger.json"
SCHEDULED_APPROVAL = ROOT / "data" / "scheduled_approval_packet.json"
MANUAL_DISTRIBUTION = ROOT / "data" / "manual_distribution_packet.json"
MANUAL_METRICS = ROOT / "data" / "manual_metric_collection_packet.json"
PLATFORM_REPAIR = ROOT / "data" / "platform_repair_status.json"
BACKLOG_RESCHEDULE = ROOT / "data" / "backlog_reschedule_preview.json"
OUT = ROOT / "data" / "human_handoff_packet.json"
REPORT = ROOT / "admin" / "reports" / "human-handoff-packet.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"


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


def approval_tasks(packet: dict) -> list[dict]:
    summary = packet.get("summary") or {}
    checked_ids = summary.get("checked_batch_ids") or []
    if not checked_ids:
        return []
    effect = summary.get("checked_batch_effect") or {}
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
                "blockers_resolved": len(checked_ids),
                "change_count": effect.get("change_count") or 0,
                "auto_count": summary.get("auto_count") or 0,
                "manual_count": summary.get("manual_count") or 0,
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
    for platform in packet.get("platforms") or []:
        fields = platform.get("fields") or []
        tasks.append(command_task(
            f"manual-metrics-{platform.get('platform')}",
            f"Fill {platform.get('platform')} manual metrics",
            "Manual metrics",
            "tod",
            "low",
            "waiting_for_manual_values",
            f"Collect {len(fields)} field(s), fill the worksheet, preview import, then refresh Admin.",
            platform.get("worksheet_import_preview_command") or "",
            platform.get("worksheet_import_command") or "",
            str(MANUAL_METRICS.relative_to(ROOT)),
            {
                "platform": platform.get("platform") or "",
                "field_count": len(fields),
                "pending_assignments": platform.get("pending_assignments") or [],
                "platform_update_command": platform.get("platform_update_command") or "",
            },
            links=[{"label": "metric source", "url": platform.get("collection_url") or ""}] if platform.get("collection_url") else [],
            guardrail="Only import nonnegative numeric values; leave unknown values blank instead of guessing.",
        ))
    return tasks


def platform_setup_tasks(packet: dict) -> list[dict]:
    tasks = []
    for row in packet.get("rows") or []:
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
            {
                "platform": row.get("platform") or "",
                "missing_secrets": row.get("missing_secrets") or [],
                "local_missing_secrets": row.get("local_missing_secrets") or [],
                "public_posting_approved": row.get("public_posting_approved"),
                "repair_checklist_blocked_count": row.get("repair_checklist_blocked_count") or 0,
            },
            guardrail="Push worker secrets only after local OAuth/public posting setup is complete.",
        ))
    return tasks


def backlog_tasks(packet: dict) -> list[dict]:
    summary = packet.get("summary") or {}
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
            },
            guardrail="Normal apply stays hidden until known executor/platform blockers clear.",
        )
    ]


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
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
        "## Tasks",
    ]
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
    tasks = []
    tasks.extend(approval_tasks(read_json(SCHEDULED_APPROVAL, {})))
    tasks.extend(manual_distribution_tasks(read_json(MANUAL_DISTRIBUTION, {})))
    tasks.extend(platform_setup_tasks(read_json(PLATFORM_REPAIR, {})))
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
    blocker_summary = (read_json(BLOCKER_LEDGER, {}).get("summary") or {})
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "promotion_blocker_ledger": str(BLOCKER_LEDGER.relative_to(ROOT)),
            "scheduled_approval": str(SCHEDULED_APPROVAL.relative_to(ROOT)),
            "manual_distribution": str(MANUAL_DISTRIBUTION.relative_to(ROOT)),
            "manual_metrics": str(MANUAL_METRICS.relative_to(ROOT)),
            "platform_repair": str(PLATFORM_REPAIR.relative_to(ROOT)),
            "backlog_reschedule": str(BACKLOG_RESCHEDULE.relative_to(ROOT)),
        },
        "summary": {
            "task_count": len(tasks),
            "owner_counts": dict(sorted(owner_counts.items())),
            "urgency_counts": dict(sorted(urgency_counts.items())),
            "phase_counts": dict(sorted(phase_counts.items())),
            "blocker_summary": blocker_summary,
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
