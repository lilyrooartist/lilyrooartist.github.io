#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMO_STATUS = ROOT / "data" / "promo_engine_status.json"
PROMO_PLAN = ROOT / "data" / "promo_queue_plan.json"
SOCIAL_EXECUTIONS = ROOT / "data" / "social_execution_snapshot.json"
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


def pending_store_actions(status):
    actions = []
    for release in status.get("releases") or []:
        title = release.get("title") or "Untitled release"
        for item in release.get("store_verification_commands") or []:
            actions.append(command_row(
                f"Verify {title} on {item.get('service') or 'store'}",
                item.get("command") or "",
                "store_verification",
                20,
                {
                    "release": title,
                    "service": item.get("service") or "",
                    "latest_snapshot": item.get("latest_snapshot") or {},
                },
            ))
    return actions


def approval_actions(plan):
    actions = []
    readiness_by_id = {
        row.get("id"): row
        for row in ((plan.get("readiness_audit") or {}).get("rows") or [])
        if row.get("id")
    }
    for post in plan.get("posts") or []:
        if post.get("approved") == "yes":
            continue
        readiness = readiness_by_id.get(post.get("id")) or {}
        state = readiness.get("state") or "unknown"
        priority = 10
        if state == "blocked":
            priority = 40
        elif state == "manual_only":
            priority = 15
        actions.append(command_row(
            f"Review {post.get('platform') or 'platform'} draft for {post.get('song') or 'release'}",
            post.get("approval_command") or "",
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
                "readiness_message": readiness.get("message") or "",
                "text": post.get("text") or "",
                "reply_text": post.get("reply_text") or "",
                "media_key": post.get("media_key") or "",
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


def manual_metric_actions(status):
    kpi = status.get("kpi") or {}
    actions = []
    for platform, command in sorted((kpi.get("pending_manual_update_by_platform") or {}).items()):
        actions.append(command_row(
            f"Fill manual metrics for {platform}",
            command,
            "manual_metrics",
            30,
            {
                "platform": platform,
                "fields": (kpi.get("pending_manual_by_platform") or {}).get(platform) or [],
            },
        ))
    return actions


def platform_fix_actions(status, executions):
    summary = status.get("kpi", {}).get("social_execution_summary") or {}
    rows = summary.get("platform_fix_needed") or (executions.get("summary") or {}).get("platform_fix_needed") or []
    actions = []
    for row in rows:
        actions.append(command_row(
            f"Fix {row.get('platform') or 'social'} executor",
            row.get("repair_command") or "python3 scripts/refresh_promo_admin.py",
            "platform_fix",
            1,
            {
                "post_id": row.get("post_id") or "",
                "platform": row.get("platform") or "",
                "reason": row.get("reason") or "",
                "error_summary": row.get("error_summary") or "",
                "repair_action": row.get("repair_action") or "",
            },
        ))
    return actions


def build_markdown(packet):
    lines = [
        "# Promo Operations Packet - Lily Roo",
        "",
        f"Generated: {packet['generated_at']}",
        "",
        "## Summary",
        f"- Actions: **{packet['summary']['action_count']}**",
        f"- User review: **{packet['summary']['user_review']}**",
        f"- Platform fixes: **{packet['summary']['platform_fixes']}**",
        f"- Store checks: **{packet['summary']['store_checks']}**",
        f"- Manual metric updates: **{packet['summary']['manual_metric_updates']}**",
        f"- Safe apply commands ready: **{packet['summary']['safe_apply_commands']}**",
        "",
        "## Top Actions",
    ]
    for action in packet["actions"][:12]:
        context = action.get("context") or {}
        detail = context.get("error_summary") or context.get("readiness_message") or ", ".join(context.get("fields") or [])
        lines.append(f"- **{action['label']}**")
        if detail:
            lines.append(f"  - Detail: {detail}")
        if action.get("command"):
            lines.append(f"  - Command: `{action['command']}`")
    if not packet["actions"]:
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
    status = read_json(PROMO_STATUS, {})
    plan = read_json(PROMO_PLAN, {})
    executions = read_json(SOCIAL_EXECUTIONS, {})
    actions = (
        platform_fix_actions(status, executions)
        + apply_actions(plan)
        + approval_actions(plan)
        + pending_store_actions(status)
        + manual_metric_actions(status)
    )
    actions = sorted(actions, key=lambda action: (action["priority"], action["label"]))
    summary = {
        "action_count": len(actions),
        "user_review": sum(1 for action in actions if action["kind"] == "approval_review"),
        "platform_fixes": sum(1 for action in actions if action["kind"] == "platform_fix"),
        "store_checks": sum(1 for action in actions if action["kind"] == "store_verification"),
        "manual_metric_updates": sum(1 for action in actions if action["kind"] == "manual_metrics"),
        "safe_apply_commands": sum(1 for action in actions if action["kind"] == "apply_approved"),
        "blocked_review_items": sum(1 for action in actions if action["context"].get("readiness_state") == "blocked"),
        "manual_only_review_items": sum(1 for action in actions if action["context"].get("readiness_state") == "manual_only"),
    }
    packet = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "promo_engine_status": str(PROMO_STATUS.relative_to(ROOT)),
            "promo_queue_plan": str(PROMO_PLAN.relative_to(ROOT)),
            "social_executions": str(SOCIAL_EXECUTIONS.relative_to(ROOT)),
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
