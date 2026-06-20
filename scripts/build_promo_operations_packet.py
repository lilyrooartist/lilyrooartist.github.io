#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMO_STATUS = ROOT / "data" / "promo_engine_status.json"
PROMO_PLAN = ROOT / "data" / "promo_queue_plan.json"
SOCIAL_EXECUTIONS = ROOT / "data" / "social_execution_snapshot.json"
EXECUTOR_READINESS = ROOT / "data" / "executor_readiness_snapshot.json"
SCHEDULED_APPROVAL = ROOT / "data" / "scheduled_approval_packet.json"
OUT = ROOT / "data" / "promo_operations_packet.json"
REPORT = ROOT / "admin" / "reports" / "promo-operations-packet.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def command_row(label: str, command: str, kind: str, priority: int, context: dict | None = None) -> dict:
    return {
        "label": label,
        "kind": kind,
        "priority": priority,
        "command": command,
        "context": context or {},
    }


def parse_datetime(value: str | None):
    raw = str(value or "").strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def phase_for(action: dict) -> str:
    kind = action.get("kind")
    if kind == "backlog_reschedule":
        return "Reschedule approved backlog"
    if kind == "scheduled_approval_batch":
        return "Review scheduled approvals"
    if kind == "platform_fix":
        return "Repair executor"
    if kind == "apply_approved":
        return "Apply approved"
    if kind == "approval_review":
        state = (action.get("context") or {}).get("readiness_state")
        if state == "blocked":
            return "Review blocked drafts"
        return "Review draft posts"
    if kind == "store_verification":
        return "Verify music sites"
    if kind == "manual_metrics":
        return "Fill manual metrics"
    return "Other"


def urgency_for(action: dict, now: datetime) -> tuple[str, str]:
    kind = action.get("kind")
    context = action.get("context") or {}
    if kind == "backlog_reschedule":
        return "high", "Approved posts are past due; preview a new schedule before any apply step."
    if kind == "scheduled_approval_batch":
        return "high", "Scheduled executor records are blocked until reviewed approval is applied."
    if kind == "platform_fix":
        return "high", "Platform executor needs repair before queued auto posts can publish."
    if kind == "apply_approved":
        return "high", "Approved rows are ready to move into the live queue."
    if kind == "approval_review":
        state = context.get("readiness_state")
        if state == "blocked":
            return "blocked", "Executor setup is not ready for this draft."
        scheduled = parse_datetime(context.get("scheduled_at"))
        if scheduled:
            hours = (scheduled - now).total_seconds() / 3600
            if hours <= 24:
                return "high", "Draft is scheduled within 24 hours."
            if hours <= 72:
                return "medium", "Draft is scheduled within 72 hours."
        if state == "manual_only":
            return "medium", "Manual copy is ready for human posting workflow."
        return "medium", "Auto draft is ready once reviewed and approved."
    if kind == "store_verification":
        release = context.get("release", "")
        if release == "Analog Myth":
            return "medium", "Public store links should be checked as the July 1 release approaches."
        return "medium", "Public store links should be checked until DistroKid exposes them."
    if kind == "manual_metrics":
        return "low", "Manual metric gaps affect reporting, not publishing."
    return "low", ""


def enrich_actions(actions: list[dict], now: datetime) -> list[dict]:
    enriched = []
    urgency_order = {"blocked": 0, "high": 1, "medium": 2, "low": 3}
    for index, action in enumerate(actions):
        urgency, reason = urgency_for(action, now)
        phase = phase_for(action)
        item = dict(action)
        item["phase"] = phase
        item["urgency"] = urgency
        item["urgency_reason"] = reason
        if urgency == "blocked":
            item["status"] = "blocked"
        elif action.get("kind") in {"approval_review", "manual_metrics", "backlog_reschedule", "scheduled_approval_batch"}:
            item["status"] = "waiting_for_user"
        elif action.get("kind") == "platform_fix":
            item["status"] = "needs_fix"
        else:
            item["status"] = "ready"
        item["sort_key"] = [
            urgency_order.get(urgency, 9),
            int(action["priority"]) if action.get("priority") is not None else 999,
            index,
        ]
        enriched.append(item)
    return sorted(enriched, key=lambda action: (action["sort_key"], action["label"]))


def grouped_counts(actions: list[dict], field: str) -> dict:
    counts = {}
    for action in actions:
        key = action.get(field) or "unknown"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def pending_store_actions(status):
    actions = []
    for release in status.get("releases") or []:
        title = release.get("title") or "Untitled release"
        for item in release.get("store_verification_commands") or []:
            latest = item.get("latest_snapshot") or {}
            checked_at = latest.get("checked_at") or latest.get("updated_at") or latest.get("generated_at") or latest.get("captured_at") or ""
            label_prefix = "Re-check" if latest else "Verify"
            note = item.get("note") or ""
            if latest:
                note = f"{note} Latest snapshot found no public URL; keep this pending until DistroKid exposes the release.".strip()
            actions.append(command_row(
                f"{label_prefix} {title} on {item.get('service') or 'store'}",
                item.get("command") or "",
                "store_verification",
                20,
                {
                    "release": title,
                    "service": item.get("service") or "",
                    "checked_at": checked_at,
                    "latest_snapshot": latest,
                    "note": note,
                },
            ))
    return actions


def platform_slug(platform: str) -> str:
    value = str(platform or "").strip().lower()
    return {
        "youtube community": "youtube",
        "x": "x",
        "instagram": "instagram",
        "tiktok": "tiktok",
        "facebook": "facebook",
    }.get(value, value)


def readiness_diagnostics(readiness: dict, platform: str) -> dict:
    payload = readiness.get("payload") if isinstance(readiness, dict) else {}
    platform_data = ((payload or {}).get("platforms") or {}).get(platform_slug(platform)) or {}
    missing_secrets = platform_data.get("missing_secrets") or []
    diagnostics = {
        "readiness": platform_data,
        "missing_secrets": missing_secrets,
        "public_posting_approved": platform_data.get("public_posting_approved"),
        "refresh_config_present": platform_data.get("refresh_config_present"),
        "access_token_present": platform_data.get("access_token_present"),
        "default_privacy": platform_data.get("default_privacy"),
    }
    return {key: value for key, value in diagnostics.items() if value not in (None, "", [])}


def repair_command_for(platform: str, fallback: str) -> str:
    if platform_slug(platform) == "tiktok":
        return "python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN"
    if platform_slug(platform) == "instagram":
        return "python3 scripts/push_social_worker_secrets.py --dry-run IG_BUSINESS_ACCOUNT_ID"
    return fallback


def repair_apply_command_for(platform: str, fallback: str) -> str:
    if platform_slug(platform) == "tiktok":
        return "python3 scripts/push_social_worker_secrets.py TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN && python3 scripts/refresh_promo_admin.py"
    if platform_slug(platform) == "instagram":
        return "python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py"
    return ""


def repair_action_for(platform: str, fallback: str, diagnostics: dict) -> str:
    if platform_slug(platform) == "tiktok":
        missing = ", ".join(diagnostics.get("missing_secrets") or [])
        approval = diagnostics.get("public_posting_approved")
        pieces = []
        if missing:
            pieces.append(f"Missing worker secrets: {missing}.")
        if approval is False:
            pieces.append("TikTok public posting approval is false.")
        pieces.append("Complete TikTok OAuth/public posting setup, push secrets, then refresh Admin.")
        return " ".join(pieces)
    return fallback


def retry_reset_context(row: dict) -> dict:
    post_id = row.get("post_id") or ""
    if row.get("reason") != "max_attempts_exceeded" or not post_id:
        return {}
    base = f"python3 scripts/reset_social_execution_state.py {post_id}"
    return {
        "retry_reset_preview_command": base,
        "retry_reset_apply_command": base + " --apply",
        "retry_reset_note": "Run only after the external platform repair is verified; this clears the retry cap so cron can attempt the row again.",
    }


def approval_actions(plan, readiness):
    actions = []
    readiness_by_id = {
        row.get("id"): row
        for row in ((plan.get("readiness_audit") or {}).get("rows") or [])
        if row.get("id")
    }
    for post in plan.get("posts") or []:
        if post.get("approved") == "yes":
            continue
        post_readiness = readiness_by_id.get(post.get("id")) or {}
        state = post_readiness.get("state") or "unknown"
        priority = 10
        if state == "blocked":
            priority = 40
        elif state == "manual_only":
            priority = 15
        approval_command = post.get("approval_command") or ""
        preview_command = approval_command.replace("--refresh-admin", "--dry-run").strip()
        if preview_command == approval_command and approval_command:
            preview_command = approval_command + " --dry-run"
        actions.append(command_row(
            f"Review {post.get('platform') or 'platform'} draft for {post.get('song') or 'release'}",
            preview_command,
            "approval_review",
            priority,
            {
                "id": post.get("id") or "",
                "release": post.get("song") or "",
                "platform": post.get("platform") or "",
                "scheduled_at": post.get("scheduled_at") or "",
                "execution_mode": post.get("execution_mode") or "",
                "post_type": post.get("post_type") or "",
                "readiness_state": state,
                "readiness_message": post_readiness.get("message") or "",
                "text": post.get("text") or "",
                "reply_text": post.get("reply_text") or "",
                "media_key": post.get("media_key") or "",
                "approval_command": approval_command,
                "preview_command": preview_command,
                **readiness_diagnostics(readiness, post.get("platform") or ""),
            },
        ))
    return actions


def apply_actions(plan):
    preview = plan.get("apply_preview") or {}
    if not preview.get("ready_to_apply_posts"):
        return []
    return [
        command_row(
            "Apply approved promo plan rows to the live queue",
            plan.get("apply_command") or "python3 scripts/apply_promo_queue_plan.py --apply --refresh-admin",
            "apply_approved",
            5,
            {"ready_ids": preview.get("ready_ids") or []},
        )
    ]


def scheduled_approval_batch_actions(packet):
    summary = packet.get("summary") or {}
    preview_command = summary.get("checked_batch_preview_command") or summary.get("batch_preview_command") or ""
    apply_command = summary.get("checked_batch_apply_command") or summary.get("batch_apply_command") or ""
    blocker_count = int(summary.get("approval_blocker_count") or 0)
    if not blocker_count or not preview_command:
        return []
    checked_count = int(summary.get("review_check_passed_count") or 0)
    blocked_count = int(summary.get("review_check_blocked_count") or 0)
    label = "Preview checked scheduled approval batch" if checked_count else "Preview scheduled approval batch"
    note = "Review all passing rows first. The checked batch excludes rows with failed review checks."
    if not checked_count:
        note = "Review all copy, assets, links, and platform readiness first. Apply only after human approval."
    return [
        command_row(
            label,
            preview_command,
            "scheduled_approval_batch",
            -1,
            {
                "approval_blocker_count": blocker_count,
                "review_check_passed_count": checked_count,
                "review_check_blocked_count": blocked_count,
                "auto_count": int(summary.get("auto_count") or 0),
                "manual_count": int(summary.get("manual_count") or 0),
                "apply_command": apply_command,
                "note": note,
            },
        )
    ]


def backlog_reschedule_actions(status):
    monetization = (status.get("kpi") or {}).get("monetization") or {}
    approved_backlog = int(monetization.get("approved_backlog_posts") or 0)
    preview_command = monetization.get("backlog_reschedule_preview_command") or ""
    if not approved_backlog or not preview_command:
        return []
    return [
        command_row(
            "Preview reschedule for approved past-due posts",
            preview_command,
            "backlog_reschedule",
            0,
            {
                "approved_backlog_posts": approved_backlog,
                "approved_upcoming_posts": int(monetization.get("approved_upcoming_posts") or 0),
                "apply_command": monetization.get("backlog_reschedule_apply_command") or "",
                "note": "Preview first. Apply refuses rows with known executor blockers unless blockers are fixed or --allow-blocked is used after deliberate review.",
            },
        )
    ]


def manual_metric_actions(status):
    kpi = status.get("kpi") or {}
    steps = {
        step.get("platform"): step
        for step in (kpi.get("manual_metric_collection_steps") or [])
        if step.get("platform")
    }
    actions = []
    for platform, command in sorted((kpi.get("pending_manual_update_by_platform") or {}).items()):
        step = steps.get(platform) or {}
        actions.append(command_row(
            f"Fill manual metrics for {platform}",
            step.get("worksheet_import_preview_command") or "python3 scripts/update_manual_social_stats.py --from-csv --dry-run",
            "manual_metrics",
            30,
            {
                "platform": platform,
                "fields": (kpi.get("pending_manual_by_platform") or {}).get(platform) or [],
                "collection_url": step.get("collection_url") or "",
                "csv_path": step.get("csv_path") or "data/manual_metric_collection_template.csv",
                "report_path": step.get("report_path") or "admin/reports/manual-metric-collection.md",
                "direct_update_command": command,
                "worksheet_import_preview_command": step.get("worksheet_import_preview_command") or "python3 scripts/update_manual_social_stats.py --from-csv --dry-run",
                "worksheet_import_command": step.get("worksheet_import_command") or "python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin",
            },
        ))
    return actions


def platform_fix_actions(status, executions, readiness):
    summary = status.get("kpi", {}).get("social_execution_summary") or {}
    rows = summary.get("platform_fix_needed") or (executions.get("summary") or {}).get("platform_fix_needed") or []
    actions = []
    for row in rows:
        platform = row.get("platform") or ""
        diagnostics = readiness_diagnostics(readiness, platform)
        fallback_action = row.get("repair_action") or ""
        fallback_command = row.get("repair_command") or "python3 scripts/refresh_promo_admin.py"
        command = repair_command_for(platform, fallback_command)
        actions.append(command_row(
            f"Fix {platform or 'social'} executor",
            command,
            "platform_fix",
            1,
            {
                "post_id": row.get("post_id") or "",
                "platform": platform,
                "reason": row.get("reason") or "",
                "error_summary": row.get("error_summary") or "",
                "repair_action": repair_action_for(platform, fallback_action, diagnostics),
                "repair_apply_command": repair_apply_command_for(platform, fallback_command),
                **retry_reset_context(row),
                **diagnostics,
            },
        ))
    return actions


def build_markdown(packet):
    phases = packet["summary"].get("phases") or {}
    urgencies = packet["summary"].get("urgencies") or {}
    lines = [
        "# Promo Operations Packet - Lily Roo",
        "",
        f"Generated: {packet['generated_at']}",
        "",
        "## Summary",
        f"- Actions: **{packet['summary']['action_count']}**",
        f"- User review: **{packet['summary']['user_review']}**",
        f"- Platform fixes: **{packet['summary']['platform_fixes']}**",
        f"- Scheduled approval batches: **{packet['summary']['scheduled_approval_batches']}**",
        f"- Store checks: **{packet['summary']['store_checks']}**",
        f"- Manual metric updates: **{packet['summary']['manual_metric_updates']}**",
        f"- Safe apply commands ready: **{packet['summary']['safe_apply_commands']}**",
        f"- Urgency: **{', '.join(f'{key}: {value}' for key, value in urgencies.items()) or 'none'}**",
        "",
        "## Phase Counts",
    ]
    for phase, count in phases.items():
        lines.append(f"- {phase}: **{count}**")
    lines.append("")
    lines.append("## Top Actions")
    if packet["actions"]:
        current_phase = ""
        for action in packet["actions"][:12]:
            phase = action.get("phase") or "Other"
            if phase != current_phase:
                lines.append("")
                lines.append(f"### {phase}")
                current_phase = phase
            context = action.get("context") or {}
            detail = context.get("error_summary") or context.get("repair_action") or context.get("readiness_message") or context.get("note") or ", ".join(context.get("fields") or [])
            missing_secrets = ", ".join(context.get("missing_secrets") or [])
            lines.append(f"- **[{action.get('urgency', 'low')}] {action['label']}**")
            if action.get("urgency_reason"):
                lines.append(f"  - Why: {action['urgency_reason']}")
            if detail:
                lines.append(f"  - Detail: {detail}")
            if missing_secrets:
                lines.append(f"  - Missing secrets: `{missing_secrets}`")
            if context.get("checked_at"):
                lines.append(f"  - Latest snapshot checked: `{context['checked_at']}`")
            if "public_posting_approved" in context:
                lines.append(f"  - Public posting approved: `{context.get('public_posting_approved')}`")
            if action.get("command"):
                lines.append(f"  - Command: `{action['command']}`")
            if context.get("repair_apply_command"):
                lines.append(f"  - Apply repair after preview: `{context['repair_apply_command']}`")
            if context.get("retry_reset_preview_command"):
                lines.append(f"  - Preview retry reset after repair: `{context['retry_reset_preview_command']}`")
            if context.get("retry_reset_apply_command"):
                lines.append(f"  - Apply retry reset after repair: `{context['retry_reset_apply_command']}`")
            if context.get("approval_command"):
                lines.append(f"  - Approve after review: `{context['approval_command']}`")
            if context.get("collection_url"):
                lines.append(f"  - Open: {context['collection_url']}")
            if context.get("worksheet_import_command"):
                lines.append(f"  - Import filled worksheet: `{context['worksheet_import_command']}`")
            if context.get("direct_update_command"):
                lines.append(f"  - Direct update fallback: `{context['direct_update_command']}`")
            if context.get("apply_command"):
                lines.append(f"  - Apply after review: `{context['apply_command']}`")
    else:
        lines.append("- No open promo operations.")
    lines.append("")
    lines.append("## Guardrails")
    lines.append("- This packet does not publish, approve, apply, or post anything.")
    lines.append("- Review copy before running approval commands.")
    lines.append("- Apply commands only move already-approved rows into the local/live queue; they do not directly post externally.")
    lines.append("")
    return "\n".join(lines)


def replace_json_embed(html: str, block_id: str, payload) -> str:
    marker = f'<script type="application/json" id="{block_id}">'
    end_marker = "</script>"
    encoded = json.dumps(payload, indent=2, ensure_ascii=False)
    start = html.find(marker)
    if start == -1:
        insert = f'\n{marker}{encoded}{end_marker}\n'
        return html.replace("<script>", insert + "\n<script>", 1)
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
        insert = f'\n{marker}{content.rstrip()}{end_marker}\n'
        return html.replace("<script>", insert + "\n<script>", 1)
    start_content = start + len(marker)
    end = html.find(end_marker, start_content)
    if end == -1:
        raise RuntimeError(f"Could not find end marker for {block_id}")
    return html[:start_content] + content.rstrip() + html[end:]


def sync_admin(packet, markdown):
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    html = replace_json_embed(html, "embedded-promo-operations-packet", packet)
    html = replace_text_embed(html, "embedded-promo-operations-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    now = datetime.now(timezone.utc)
    status = read_json(PROMO_STATUS, {})
    plan = read_json(PROMO_PLAN, {})
    executions = read_json(SOCIAL_EXECUTIONS, {})
    readiness = read_json(EXECUTOR_READINESS, {})
    scheduled_approval = read_json(SCHEDULED_APPROVAL, {})
    actions = (
        scheduled_approval_batch_actions(scheduled_approval)
        + backlog_reschedule_actions(status)
        + platform_fix_actions(status, executions, readiness)
        + apply_actions(plan)
        + approval_actions(plan, readiness)
        + pending_store_actions(status)
        + manual_metric_actions(status)
    )
    actions = enrich_actions(actions, now)
    summary = {
        "action_count": len(actions),
        "user_review": sum(1 for action in actions if action["kind"] == "approval_review"),
        "platform_fixes": sum(1 for action in actions if action["kind"] == "platform_fix"),
        "scheduled_approval_batches": sum(1 for action in actions if action["kind"] == "scheduled_approval_batch"),
        "store_checks": sum(1 for action in actions if action["kind"] == "store_verification"),
        "manual_metric_updates": sum(1 for action in actions if action["kind"] == "manual_metrics"),
        "backlog_reschedules": sum(1 for action in actions if action["kind"] == "backlog_reschedule"),
        "safe_apply_commands": sum(1 for action in actions if action["kind"] == "apply_approved"),
        "blocked_review_items": sum(1 for action in actions if action["context"].get("readiness_state") == "blocked"),
        "manual_only_review_items": sum(1 for action in actions if action["context"].get("readiness_state") == "manual_only"),
        "phases": grouped_counts(actions, "phase"),
        "urgencies": grouped_counts(actions, "urgency"),
        "next_action": next((action for action in actions if action.get("status") != "blocked"), actions[0] if actions else {}),
    }
    packet = {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "promo_engine_status": str(PROMO_STATUS.relative_to(ROOT)),
            "promo_queue_plan": str(PROMO_PLAN.relative_to(ROOT)),
            "social_executions": str(SOCIAL_EXECUTIONS.relative_to(ROOT)),
            "executor_readiness": str(EXECUTOR_READINESS.relative_to(ROOT)),
            "scheduled_approval": str(SCHEDULED_APPROVAL.relative_to(ROOT)),
        },
        "summary": summary,
        "actions": actions,
    }
    OUT.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(packet)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(packet, markdown)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), "actions": len(actions)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
