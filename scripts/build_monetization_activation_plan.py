#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMO_STATUS = ROOT / "data" / "promo_engine_status.json"
APPROVAL_RUNWAY = ROOT / "data" / "approval_runway.json"
SUBSCRIBER_CTA_AUDIT = ROOT / "data" / "subscriber_cta_audit.json"
PLATFORM_REPAIR = ROOT / "data" / "platform_repair_status.json"
PROMO_OPERATIONS = ROOT / "data" / "promo_operations_packet.json"
OUT = ROOT / "data" / "monetization_activation_plan.json"
REPORT = ROOT / "admin" / "reports" / "monetization-activation-plan.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def by_id(rows: list[dict]) -> dict:
    return {
        row.get("id"): row
        for row in rows
        if row.get("id")
    }


def command_action(label: str, phase: str, status: str, detail: str, command: str = "", after_review: str = "", context: dict | None = None) -> dict:
    return {
        "label": label,
        "phase": phase,
        "status": status,
        "detail": detail,
        "command": command,
        "after_review_command": after_review,
        "context": context or {},
    }


def build_actions(status: dict, runway: dict, cta_audit: dict, platform_repair: dict, operations: dict) -> list[dict]:
    actions = []
    cta_by_id = by_id(cta_audit.get("rows") or [])
    recommended_ids = (runway.get("summary") or {}).get("recommended_ids") or []
    for post_id in recommended_ids:
        cta = cta_by_id.get(post_id) or {}
        if not cta:
            continue
        detail = cta.get("action") or "Review subscriber CTA before approval."
        if cta.get("recommended_text"):
            detail = f"{detail} Recommended copy: {cta['recommended_text']}"
        actions.append(command_action(
            f"Review subscriber CTA for {cta.get('platform') or 'platform'}",
            "Tighten subscriber CTA",
            "waiting_for_review",
            detail,
            cta.get("approval_preview_command") or "",
            cta.get("approval_command") or "",
            {
                "post_id": post_id,
                "release": cta.get("release") or "",
                "selected_strength": cta.get("selected_strength") or "",
                "recommended_strength": cta.get("recommended_strength") or "",
                "readiness_state": cta.get("readiness_state") or "",
            },
        ))

    monetization = (status.get("kpi") or {}).get("monetization") or {}
    if monetization.get("draft_review_posts"):
        actions.append(command_action(
            "Apply approved plan rows after review",
            "Move approved subscriber posts into queue",
            "blocked_until_approved",
            "After copy review and approval, apply only approved rows to the live queue; this does not directly post externally.",
            "",
            "python3 scripts/apply_promo_queue_plan.py --apply --refresh-admin",
            {
                "approved_plan_posts": monetization.get("approved_plan_posts"),
                "ready_to_apply_posts": monetization.get("ready_to_apply_posts"),
            },
        ))

    if monetization.get("approved_backlog_posts") and monetization.get("backlog_reschedule_preview_command"):
        actions.append(command_action(
            "Preview approved backlog reschedule",
            "Recover stalled approved backlog",
            "preview_first",
            "Preview a new schedule for approved past-due posts. Apply refuses known blocked executor rows unless deliberately overridden.",
            monetization.get("backlog_reschedule_preview_command") or "",
            monetization.get("backlog_reschedule_apply_command") or "",
            {
                "approved_backlog_posts": monetization.get("approved_backlog_posts"),
                "approved_upcoming_posts": monetization.get("approved_upcoming_posts"),
            },
        ))

    for row in platform_repair.get("rows") or []:
        actions.append(command_action(
            f"Repair {row.get('platform') or 'platform'} executor",
            "Clear platform blockers",
            "needs_platform_fix",
            row.get("repair_action") or row.get("error_summary") or "Repair platform readiness.",
            row.get("preview_command") or "",
            row.get("apply_command") or "",
            {
                "post_id": row.get("post_id") or "",
                "platform": row.get("platform") or "",
                "reason": row.get("reason") or "",
            },
        ))

    next_action = (operations.get("summary") or {}).get("next_action") or {}
    if next_action.get("label"):
        actions.append(command_action(
            f"Current operations next action: {next_action.get('label')}",
            "Operations packet",
            next_action.get("status") or "waiting_for_user",
            next_action.get("urgency_reason") or "",
            next_action.get("command") or "",
            (next_action.get("context") or {}).get("apply_command") or "",
            {
                "kind": next_action.get("kind") or "",
                "urgency": next_action.get("urgency") or "",
            },
        ))

    return actions


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


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Monetization Activation Plan - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Current subscribers: **{summary['current_subscribers']} / {summary['target_subscribers']}**",
        f"- Runway status: **{summary['runway_status']}**",
        f"- Ready subscriber CTA approvals: **{summary['ready_subscriber_approval_count']}**",
        f"- Subscriber CTA swaps available: **{summary['subscriber_swap_count']}**",
        f"- Platform fixes: **{summary['platform_fix_count']}**",
        f"- Activation actions: **{summary['action_count']}**",
        "",
        "## Activation Sequence",
    ]
    for index, action in enumerate(payload["actions"], start=1):
        lines.append(f"{index}. **{action['label']}**")
        lines.append(f"   - Phase: `{action['phase']}`; status: `{action['status']}`")
        if action.get("detail"):
            lines.append(f"   - Detail: {action['detail']}")
        if action.get("command"):
            lines.append(f"   - Preview/check: `{action['command']}`")
        if action.get("after_review_command"):
            lines.append(f"   - After review: `{action['after_review_command']}`")
    lines.append("")
    lines.append("## Guardrails")
    lines.append("- This plan does not approve, apply, publish, or post anything.")
    lines.append("- Approval and apply commands are shown as deliberate after-review steps.")
    lines.append("- Run preview/check commands first when present.")
    lines.append("")
    return "\n".join(lines)


def sync_admin(payload: dict, markdown: str) -> None:
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    html = replace_json_embed(html, "embedded-monetization-activation-plan", payload)
    html = replace_text_embed(html, "embedded-monetization-activation-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    now = datetime.now(timezone.utc)
    status = read_json(PROMO_STATUS, {})
    runway = read_json(APPROVAL_RUNWAY, {})
    cta_audit = read_json(SUBSCRIBER_CTA_AUDIT, {})
    platform_repair = read_json(PLATFORM_REPAIR, {})
    operations = read_json(PROMO_OPERATIONS, {})
    monetization = (status.get("kpi") or {}).get("monetization") or {}
    runway_state = monetization.get("runway") or {}
    actions = build_actions(status, runway, cta_audit, platform_repair, operations)
    summary = {
        "target_subscribers": monetization.get("target"),
        "current_subscribers": monetization.get("current_subscribers"),
        "remaining_subscribers": monetization.get("remaining_subscribers"),
        "runway_status": runway_state.get("status") or "",
        "subscribers_per_week": runway_state.get("subscribers_per_week"),
        "required_subscribers_per_week_365": (runway_state.get("required_subscribers_per_week") or {}).get("365_days"),
        "ready_subscriber_approval_count": len((runway.get("summary") or {}).get("recommended_ids") or []),
        "subscriber_swap_count": (cta_audit.get("summary") or {}).get("subscriber_swap_count", 0),
        "ready_after_approval_swap_count": (cta_audit.get("summary") or {}).get("ready_after_approval_swap_count", 0),
        "platform_fix_count": (platform_repair.get("summary") or {}).get("platform_fix_count", 0),
        "action_count": len(actions),
    }
    payload = {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "promo_engine_status": str(PROMO_STATUS.relative_to(ROOT)),
            "approval_runway": str(APPROVAL_RUNWAY.relative_to(ROOT)),
            "subscriber_cta_audit": str(SUBSCRIBER_CTA_AUDIT.relative_to(ROOT)),
            "platform_repair_status": str(PLATFORM_REPAIR.relative_to(ROOT)),
            "promo_operations_packet": str(PROMO_OPERATIONS.relative_to(ROOT)),
        },
        "summary": summary,
        "actions": actions,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(payload)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(payload, markdown)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), "actions": len(actions)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
