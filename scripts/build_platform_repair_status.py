#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OPERATIONS = ROOT / "data" / "promo_operations_packet.json"
EXECUTIONS = ROOT / "data" / "social_execution_snapshot.json"
READINESS = ROOT / "data" / "executor_readiness_snapshot.json"
OUT = ROOT / "data" / "platform_repair_status.json"
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


def sync_admin(payload: dict) -> None:
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    html = replace_json_embed(html, "embedded-platform-repair-status", payload)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def build_status() -> dict:
    now = datetime.now(timezone.utc)
    operations = read_json(OPERATIONS, {})
    executions = read_json(EXECUTIONS, {})
    readiness = read_json(READINESS, {})
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
        apply_command = context.get("repair_apply_command") or ""
        rows.append({
            "post_id": post_id,
            "platform": platform,
            "status": execution.get("status") or "needs_fix",
            "reason": execution.get("reason") or context.get("reason") or "",
            "attempts": execution.get("attempts"),
            "updated_at": execution.get("updated_at") or "",
            "error_summary": execution.get("error_summary") or context.get("error_summary") or "",
            "repair_action": context.get("repair_action") or "",
            "preview_command": preview_command,
            "apply_command": apply_command,
            "readiness": platform_readiness,
            "missing_secrets": context.get("missing_secrets") or platform_readiness.get("missing_secrets") or [],
            "public_posting_approved": context.get("public_posting_approved", platform_readiness.get("public_posting_approved")),
            "blocked": True,
        })
    summary = {
        "platform_fix_count": len(rows),
        "blocked_count": sum(1 for row in rows if row.get("blocked")),
        "preview_command_count": sum(1 for row in rows if row.get("preview_command")),
        "apply_command_count": sum(1 for row in rows if row.get("apply_command")),
        "platforms": sorted({row.get("platform") for row in rows if row.get("platform")}),
    }
    return {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "promo_operations_packet": str(OPERATIONS.relative_to(ROOT)),
            "social_executions": str(EXECUTIONS.relative_to(ROOT)),
            "executor_readiness": str(READINESS.relative_to(ROOT)),
        },
        "summary": summary,
        "rows": rows,
    }


def main() -> int:
    status = build_status()
    OUT.write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    sync_admin(status)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), "platform_fix_count": status["summary"]["platform_fix_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
