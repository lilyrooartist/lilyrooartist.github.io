#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data" / "scheduled_posts.csv"
EXECUTIONS = ROOT / "data" / "social_execution_snapshot.json"
OUT = ROOT / "data" / "scheduled_approval_packet.json"
REPORT = ROOT / "admin" / "reports" / "scheduled-approval-packet.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def read_queue() -> dict[str, dict[str, str]]:
    with QUEUE.open(newline="", encoding="utf-8") as handle:
        return {
            row.get("id", ""): {key: (value or "").strip() for key, value in row.items()}
            for row in csv.DictReader(handle)
            if row.get("id")
        }


def copy_block(row: dict[str, str]) -> str:
    return "\n\n".join(part for part in [row.get("text") or "", row.get("reply_text") or ""] if part)


def approval_preview_command(post_id: str) -> str:
    return f"python3 scripts/update_scheduled_post_approval.py {post_id} --dry-run"


def approval_apply_command(post_id: str) -> str:
    return f"python3 scripts/update_scheduled_post_approval.py {post_id} --refresh-admin"


def build_rows(queue: dict[str, dict[str, str]], executions: dict) -> list[dict]:
    rows = []
    for item in (executions.get("summary") or {}).get("approval_needed") or []:
        post_id = item.get("post_id") or ""
        row = queue.get(post_id) or {}
        if not row:
            continue
        media_url = row.get("clip_url") or row.get("imagery_url") or ""
        rows.append({
            "id": post_id,
            "platform": row.get("platform") or item.get("platform") or "",
            "song": row.get("song") or "",
            "scheduled_at": row.get("scheduled_at") or "",
            "execution_mode": row.get("execution_mode") or "",
            "post_type": row.get("post_type") or "",
            "approved": row.get("approved") or "",
            "status": item.get("status") or "",
            "reason": item.get("reason") or "",
            "attempts": item.get("attempts") or 0,
            "text": row.get("text") or "",
            "reply_text": row.get("reply_text") or "",
            "copy_block": copy_block(row),
            "imagery_url": row.get("imagery_url") or "",
            "clip_url": row.get("clip_url") or "",
            "asset_url": media_url,
            "media_key": row.get("media_key") or "",
            "desired_privacy": row.get("desired_privacy") or "",
            "approval_preview_command": approval_preview_command(post_id),
            "approval_apply_command": approval_apply_command(post_id),
            "recommendation": "Review copy, media, destination links, and platform readiness before approval.",
            "manual_dispatch": row.get("execution_mode") == "manual",
        })
    return sorted(rows, key=lambda row: (row.get("scheduled_at") or "", row.get("platform") or "", row.get("id") or ""))


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Scheduled Approval Packet - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Approval blockers: **{summary['approval_blocker_count']}**",
        f"- Auto rows: **{summary['auto_count']}**",
        f"- Manual rows: **{summary['manual_count']}**",
        "",
        "## Review Queue",
    ]
    for row in payload["rows"]:
        lines.append(f"- **{row['platform']} - {row['song']}** (`{row['id']}`)")
        lines.append(f"  - Scheduled: `{row['scheduled_at']}`; mode: `{row['execution_mode']}`; type: `{row['post_type']}`")
        lines.append(f"  - Reason: `{row['reason']}`")
        lines.append(f"  - Copy: {row['text']}")
        if row.get("reply_text"):
            lines.append(f"  - Link/reply: {row['reply_text']}")
        if row.get("asset_url"):
            lines.append(f"  - Asset: {row['asset_url']}")
        lines.append(f"  - Preview approval: `{row['approval_preview_command']}`")
        lines.append(f"  - Approve after review: `{row['approval_apply_command']}`")
    lines.extend([
        "",
        "## Guardrails",
        "- This packet does not approve, publish, or post anything.",
        "- Use preview commands before approval apply commands.",
        "- Manual rows still require human posting and public URL logging after approval.",
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
    html = replace_json_embed(html, "embedded-scheduled-approval-packet", payload)
    html = replace_text_embed(html, "embedded-scheduled-approval-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    queue = read_queue()
    executions = read_json(EXECUTIONS, {})
    rows = build_rows(queue, executions)
    payload = {
        "generated_at": now,
        "safe_mode": True,
        "source": {
            "scheduled_posts": str(QUEUE.relative_to(ROOT)),
            "social_execution_snapshot": str(EXECUTIONS.relative_to(ROOT)),
        },
        "summary": {
            "approval_blocker_count": len(rows),
            "auto_count": sum(1 for row in rows if row.get("execution_mode") == "auto"),
            "manual_count": sum(1 for row in rows if row.get("execution_mode") == "manual"),
            "preview_command_count": sum(1 for row in rows if row.get("approval_preview_command")),
            "apply_command_count": sum(1 for row in rows if row.get("approval_apply_command")),
        },
        "rows": rows,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(payload)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(payload, markdown)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), "approval_blockers": len(rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
