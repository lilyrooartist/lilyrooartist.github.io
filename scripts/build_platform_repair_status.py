#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OPERATIONS = ROOT / "data" / "promo_operations_packet.json"
EXECUTIONS = ROOT / "data" / "social_execution_snapshot.json"
READINESS = ROOT / "data" / "executor_readiness_snapshot.json"
TIKTOK_PREFLIGHT = ROOT / "data" / "tiktok_setup_preflight.json"
OUT = ROOT / "data" / "platform_repair_status.json"
REPORT = ROOT / "admin" / "reports" / "platform-repair-status.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def platform_slug(platform: str) -> str:
    value = str(platform or "").strip().lower()
    return {
        "youtube community": "youtube",
        "x": "x",
        "instagram": "instagram",
        "tiktok": "tiktok",
        "facebook": "facebook",
    }.get(value, value)


def execution_rows(snapshot: dict) -> dict[str, dict]:
    summary = snapshot.get("summary") or {}
    rows = {}
    for key in ("platform_fix_needed", "approval_needed", "latest_attention"):
        for row in summary.get(key) or []:
            post_id = row.get("post_id")
            if post_id and post_id not in rows:
                rows[post_id] = row
    return rows


def readiness_for(readiness: dict, platform: str) -> dict:
    payload = readiness.get("payload") or {}
    platforms = payload.get("platforms") or {}
    return platforms.get(platform_slug(platform)) or {}


def replace_json_embed(html: str, block_id: str, payload) -> str:
    marker = f'<script type="application/json" id="{block_id}">'
    end_marker = "</script>"
    encoded = json.dumps(payload, indent=2, ensure_ascii=False)
    start = html.find(marker)
    if start == -1:
        insert = f"\n{marker}{encoded}{end_marker}\n"
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
        insert = f"\n{marker}{content.rstrip()}{end_marker}\n"
        return html.replace("<script>", insert + "\n<script>", 1)
    start_content = start + len(marker)
    end = html.find(end_marker, start_content)
    if end == -1:
        raise RuntimeError(f"Could not find end marker for {block_id}")
    return html[:start_content] + content.rstrip() + html[end:]


def repair_priority(row: dict) -> int:
    platform = platform_slug(row.get("platform") or "")
    if platform == "instagram":
        return 1
    if platform == "facebook":
        return 2
    if platform == "tiktok":
        return 3
    return 9


def repair_checklist(context: dict, platform_readiness: dict, preview_command: str, apply_command: str) -> list[dict]:
    missing = context.get("missing_secrets") or platform_readiness.get("missing_secrets") or []
    local_missing = context.get("local_missing_secrets") or []
    local_source = context.get("local_secret_source") or ""
    public_posting = context.get("public_posting_approved", platform_readiness.get("public_posting_approved"))
    checklist = []
    if missing:
        checklist.append({
            "id": "remote_worker_secrets",
            "label": "Worker secrets",
            "status": "blocked",
            "detail": f"Missing remote worker secret(s): {', '.join(missing)}.",
            "command": preview_command,
        })
    else:
        checklist.append({
            "id": "remote_worker_secrets",
            "label": "Worker secrets",
            "status": "pass",
            "detail": "Worker readiness snapshot reports required secrets present.",
            "command": "",
        })
    if local_missing:
        checklist.append({
            "id": "local_secret_source",
            "label": "Local secret source",
            "status": "blocked",
            "detail": f"{local_source or 'local secret source'} is missing: {', '.join(local_missing)}.",
            "command": "",
        })
    elif local_source:
        checklist.append({
            "id": "local_secret_source",
            "label": "Local secret source",
            "status": "pass",
            "detail": f"{local_source} has the required local value(s).",
            "command": "",
        })
    if public_posting is False:
        checklist.append({
            "id": "public_posting_approval",
            "label": "Direct public posting approval",
            "status": "blocked",
            "detail": "Direct public posting approval is false; TikTok upload-draft mode can still proceed after credentials.",
            "command": "",
        })
    elif public_posting is True:
        checklist.append({
            "id": "public_posting_approval",
            "label": "Direct public posting approval",
            "status": "pass",
            "detail": "Direct public posting approval is true.",
            "command": "",
        })
    checklist.append({
        "id": "refresh_verification",
        "label": "Refresh verification",
        "status": "waiting" if apply_command else "review",
        "detail": "After repair, refresh admin so readiness, scheduler, blocker, and backlog state update together.",
        "command": apply_command or "python3 scripts/refresh_promo_admin.py",
    })
    return checklist


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Platform Repair Status - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Platform fixes: **{summary['platform_fix_count']}**",
        f"- Blocked rows: **{summary['blocked_count']}**",
        f"- Preview commands: **{summary['preview_command_count']}**",
        f"- Apply commands: **{summary['apply_command_count']}**",
        f"- Checklist items: **{summary['checklist_item_count']}**",
        f"- Checklist blocked: **{summary['checklist_blocked_count']}**",
        f"- Platforms: **{', '.join(summary['platforms']) or 'none'}**",
        "",
        "## Repair Checklist",
    ]
    for row in payload["rows"]:
        lines.append(f"- **{row['platform']}** (`{row['post_id']}`)")
        lines.append(f"  - Status: `{row['status']}`; reason: `{row['reason']}`")
        if row.get("error_summary"):
            lines.append(f"  - Error: {row['error_summary']}")
        if row.get("repair_action"):
            lines.append(f"  - Repair: {row['repair_action']}")
        if row.get("missing_secrets"):
            lines.append(f"  - Missing secrets: {', '.join(row['missing_secrets'])}")
        if row.get("local_missing_secrets"):
            lines.append(f"  - Missing locally: {', '.join(row['local_missing_secrets'])}")
        if row.get("local_secret_source"):
            lines.append(f"  - Local source: `{row['local_secret_source']}`")
        if row.get("preflight_status"):
            lines.append(f"  - Setup preflight: `{row['preflight_status']}`; blocked checks: `{row.get('preflight_blocked_count')}`")
        if row.get("preflight_command"):
            lines.append(f"  - Rebuild setup preflight: `{row['preflight_command']}`")
        if row.get("preflight_report"):
            lines.append(f"  - Preflight report: `{row['preflight_report']}`")
        if row.get("repair_checklist"):
            lines.append("  - Checklist:")
            for item in row["repair_checklist"]:
                command = f" Command: `{item['command']}`" if item.get("command") else ""
                lines.append(f"    - `{item['status']}` {item['label']}: {item['detail']}{command}")
        if row.get("preview_command"):
            lines.append(f"  - Preview/check: `{row['preview_command']}`")
        if row.get("apply_command"):
            lines.append(f"  - Apply after review: `{row['apply_command']}`")
        if row.get("blocked_apply_command"):
            lines.append(f"  - Blocked apply command: `{row['blocked_apply_command']}`")
        if row.get("blocked_apply_reasons"):
            lines.append(f"  - Apply blocked by: {', '.join(row['blocked_apply_reasons'])}")
        if row.get("retry_reset_verification_command"):
            lines.append(f"  - Verify before retry reset: `{row['retry_reset_verification_command']}`")
        if row.get("retry_reset_preview_command"):
            lines.append(f"  - Preview retry reset after platform repair: `{row['retry_reset_preview_command']}`")
        if row.get("retry_reset_apply_command"):
            lines.append(f"  - Apply retry reset after platform repair: `{row['retry_reset_apply_command']}`")
        if row.get("retry_reset_note"):
            lines.append(f"  - Retry reset note: {row['retry_reset_note']}")
    lines.extend([
        "",
        "## Guardrails",
        "- This report does not push secrets, reconnect accounts, approve posts, or publish posts.",
        "- Run preview/check commands before any repair apply command.",
        "- Re-run the safe admin refresh after repairs so backlog and readiness state update together.",
        "",
    ])
    return "\n".join(lines)


def sync_admin(payload: dict, markdown: str) -> None:
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    html = replace_json_embed(html, "embedded-platform-repair-status", payload)
    html = replace_text_embed(html, "embedded-platform-repair-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def build_status() -> dict:
    now = datetime.now(timezone.utc)
    operations = read_json(OPERATIONS, {})
    executions = read_json(EXECUTIONS, {})
    readiness = read_json(READINESS, {})
    tiktok_preflight = read_json(TIKTOK_PREFLIGHT, {})
    execution_by_id = execution_rows(executions)
    rows = []
    for action in operations.get("actions") or []:
        if action.get("kind") != "platform_fix":
            continue
        context = action.get("context") or {}
        post_id = context.get("post_id") or ""
        platform = context.get("platform") or ""
        execution = execution_by_id.get(post_id) or {}
        platform_readiness = readiness_for(readiness, platform)
        preview_command = action.get("command") or ""
        preflight = tiktok_preflight if platform_slug(platform) == "tiktok" else {}
        preflight_summary = preflight.get("summary") or {}
        raw_apply_command = context.get("repair_apply_command") or ""
        local_missing = context.get("local_missing_secrets") or []
        public_posting_approved = context.get("public_posting_approved", platform_readiness.get("public_posting_approved"))
        blocked_apply_reasons = []
        if local_missing:
            blocked_apply_reasons.append(f"local_secret_source_missing:{','.join(local_missing)}")
        if platform_slug(platform) == "tiktok" and public_posting_approved is not True:
            direct_mode = str(preflight_summary.get("worker_posting_mode") or "").lower() == "direct"
            if direct_mode:
                blocked_apply_reasons.append("public_posting_approval_not_confirmed_for_direct_posting")
        apply_command = "" if blocked_apply_reasons else raw_apply_command
        checklist = repair_checklist(context, platform_readiness, preview_command, apply_command)
        rows.append({
            "post_id": post_id,
            "platform": platform,
            "priority": repair_priority({"platform": platform}),
            "status": execution.get("status") or "needs_fix",
            "reason": execution.get("reason") or context.get("reason") or "",
            "attempts": execution.get("attempts"),
            "updated_at": execution.get("updated_at") or "",
            "error_summary": execution.get("error_summary") or context.get("error_summary") or "",
            "repair_action": context.get("repair_action") or "",
            "preview_command": preview_command,
            "apply_command": apply_command,
            "blocked_apply_command": raw_apply_command if blocked_apply_reasons else "",
            "blocked_apply_reasons": blocked_apply_reasons,
            "retry_reset_verification_command": context.get("retry_reset_verification_command") or "",
            "retry_reset_preview_command": context.get("retry_reset_preview_command") or "",
            "retry_reset_apply_command": context.get("retry_reset_apply_command") or "",
            "retry_reset_note": context.get("retry_reset_note") or "",
            "readiness": platform_readiness,
            "missing_secrets": context.get("missing_secrets") or platform_readiness.get("missing_secrets") or [],
            "local_missing_secrets": local_missing,
            "local_secret_presence": context.get("local_secret_presence") or {},
            "local_secret_ready": context.get("local_secret_ready"),
            "local_secret_source": context.get("local_secret_source") or "",
            "public_posting_approved": public_posting_approved,
            "preflight_status": preflight_summary.get("status") or "",
            "preflight_blocked_count": preflight_summary.get("blocked_count"),
            "preflight_command": "python3 scripts/build_tiktok_setup_preflight.py" if platform_slug(platform) == "tiktok" else "",
            "preflight_report": str((ROOT / "admin" / "reports" / "tiktok-setup-preflight.md").relative_to(ROOT)) if platform_slug(platform) == "tiktok" else "",
            "repair_checklist": checklist,
            "repair_checklist_blocked_count": sum(1 for item in checklist if item.get("status") == "blocked"),
            "blocked": True,
        })
    rows.sort(key=lambda row: (row.get("priority") or 9, row.get("platform") or "", row.get("post_id") or ""))
    summary = {
        "platform_fix_count": len(rows),
        "blocked_count": sum(1 for row in rows if row.get("blocked")),
        "preview_command_count": sum(1 for row in rows if row.get("preview_command")),
        "apply_command_count": sum(1 for row in rows if row.get("apply_command")),
        "retry_reset_count": sum(1 for row in rows if row.get("retry_reset_preview_command")),
        "checklist_item_count": sum(len(row.get("repair_checklist") or []) for row in rows),
        "checklist_blocked_count": sum(int(row.get("repair_checklist_blocked_count") or 0) for row in rows),
        "platforms": sorted({row.get("platform") for row in rows if row.get("platform")}),
    }
    return {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "promo_operations_packet": str(OPERATIONS.relative_to(ROOT)),
            "social_executions": str(EXECUTIONS.relative_to(ROOT)),
            "executor_readiness": str(READINESS.relative_to(ROOT)),
            "tiktok_setup_preflight": str(TIKTOK_PREFLIGHT.relative_to(ROOT)),
        },
        "summary": summary,
        "rows": rows,
    }


def main() -> int:
    status = build_status()
    OUT.write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(status)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(status, markdown)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), "platform_fix_count": status["summary"]["platform_fix_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
