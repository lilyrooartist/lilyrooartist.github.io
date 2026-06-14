#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data" / "scheduled_posts.csv"
PUBLISHED_LOG = ROOT / "admin" / "content" / "Published_Log.csv"
SOCIAL_EXECUTIONS = ROOT / "data" / "social_execution_snapshot.json"
PROMO_STATUS = ROOT / "data" / "promo_engine_status.json"
OUT = ROOT / "data" / "backlog_reschedule_preview.json"
REPORT = ROOT / "admin" / "reports" / "backlog-reschedule-preview.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_datetime(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value or "").strip())
    except ValueError:
        return None
    return parsed.astimezone() if parsed.tzinfo is None else parsed


def load_published_ids() -> set[str]:
    ids = set()
    for row in read_csv(PUBLISHED_LOG):
        content_id = (row.get("content_id") or "").strip()
        if content_id.startswith("FP-AUTO-"):
            ids.add(content_id)
        for match in re.findall(r"\bqueue_id=(FP-AUTO-\d+)\b", row.get("notes") or ""):
            ids.add(match)
    return ids


def load_execution_blockers() -> dict[str, dict]:
    snapshot = read_json(SOCIAL_EXECUTIONS, {})
    summary = snapshot.get("summary") or {}
    blockers = {}
    for key in ("platform_fix_needed", "approval_needed", "latest_attention"):
        for row in summary.get(key) or []:
            post_id = row.get("post_id")
            if post_id and post_id not in blockers:
                blockers[post_id] = row
    return blockers


def preview_command(status: dict) -> str:
    monetization = (status.get("kpi") or {}).get("monetization") or {}
    command = monetization.get("backlog_reschedule_preview_command") or ""
    if command:
        return command
    return "python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-14T10:00:00-04:00' --spacing-hours 24"


def apply_command(status: dict) -> str:
    monetization = (status.get("kpi") or {}).get("monetization") or {}
    return monetization.get("backlog_reschedule_apply_command") or ""


def start_at_from_status(status: dict) -> datetime:
    command = preview_command(status)
    match = re.search(r"--start-at\s+'([^']+)'", command)
    if match:
        parsed = parse_datetime(match.group(1))
        if parsed:
            return parsed
    return datetime.now().astimezone().replace(hour=10, minute=0, second=0, microsecond=0)


def spacing_from_status(status: dict) -> int:
    command = preview_command(status)
    match = re.search(r"--spacing-hours\s+(\d+)", command)
    if match:
        return max(int(match.group(1)), 1)
    return 24


def build_preview() -> dict:
    now = datetime.now().astimezone()
    status = read_json(PROMO_STATUS, {})
    published_ids = load_published_ids()
    blockers = load_execution_blockers()
    rows = []
    for row in read_csv(QUEUE):
        row_id = row.get("id") or ""
        scheduled_at = parse_datetime(row.get("scheduled_at") or "")
        if not row_id or row_id in published_ids or not scheduled_at:
            continue
        if str(row.get("approved") or "").strip().lower() == "yes" and scheduled_at < now:
            rows.append(row)
    rows.sort(key=lambda row: row.get("scheduled_at", ""))

    start_at = start_at_from_status(status)
    spacing_hours = spacing_from_status(status)
    items = []
    for index, row in enumerate(rows):
        row_id = row.get("id") or ""
        blocker = blockers.get(row_id) or {}
        proposed = start_at + timedelta(hours=spacing_hours * index)
        blocker_detail = blocker.get("error_summary") or blocker.get("reason") or blocker.get("status") or ""
        items.append({
            "id": row_id,
            "platform": row.get("platform") or "",
            "song": row.get("song") or "",
            "current_scheduled_at": row.get("scheduled_at") or "",
            "proposed_scheduled_at": proposed.isoformat(),
            "blocked": bool(blocker),
            "blocker_reason": blocker_detail,
            "blocker_status": blocker.get("status") or "",
            "blocker_source": blocker.get("source") or "",
        })

    blocked_items = [item for item in items if item["blocked"]]
    return {
        "generated_at": datetime.now().astimezone().isoformat(),
        "safe_mode": True,
        "source": {
            "scheduled_posts": str(QUEUE.relative_to(ROOT)),
            "published_log": str(PUBLISHED_LOG.relative_to(ROOT)),
            "social_execution_snapshot": str(SOCIAL_EXECUTIONS.relative_to(ROOT)),
            "promo_engine_status": str(PROMO_STATUS.relative_to(ROOT)),
        },
        "summary": {
            "approved_backlog_count": len(items),
            "blocked_backlog_count": len(blocked_items),
            "clear_to_apply_count": len(items) - len(blocked_items),
            "start_at": start_at.isoformat(),
            "spacing_hours": spacing_hours,
            "preview_command": preview_command(status),
            "apply_command": apply_command(status),
            "apply_allowed_without_override": len(blocked_items) == 0,
        },
        "items": items,
    }


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


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Backlog Reschedule Preview - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Approved backlog rows: **{summary['approved_backlog_count']}**",
        f"- Rows with known blockers: **{summary['blocked_backlog_count']}**",
        f"- Clear to apply without override: **{summary['clear_to_apply_count']}**",
        f"- Start at: **{summary['start_at']}**",
        f"- Spacing hours: **{summary['spacing_hours']}**",
        f"- Apply allowed without override: **{summary['apply_allowed_without_override']}**",
        "",
        "## Proposed Reschedule",
    ]
    for item in payload["items"]:
        lines.append(f"- **{item['platform']} - {item['song']}** (`{item['id']}`)")
        lines.append(f"  - Current: `{item['current_scheduled_at']}`")
        lines.append(f"  - Proposed: `{item['proposed_scheduled_at']}`")
        if item["blocked"]:
            lines.append(f"  - Blocker: {item['blocker_reason'] or item['blocker_status'] or 'executor attention required'}")
    lines.extend([
        "",
        "## Commands",
        f"- Preview: `{summary['preview_command']}`",
        f"- Apply after blockers are cleared: `{summary['apply_command']}`",
        "",
        "## Guardrails",
        "- This preview does not write schedule changes, approve posts, publish posts, or push secrets.",
        "- Apply refuses known blocked rows unless `--allow-blocked` is used after deliberate review.",
        "",
    ])
    return "\n".join(lines)


def sync_admin(payload: dict, markdown: str) -> None:
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    html = replace_json_embed(html, "embedded-backlog-reschedule-preview", payload)
    html = replace_text_embed(html, "embedded-backlog-reschedule-preview-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    payload = build_preview()
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(payload)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(payload, markdown)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), "approved_backlog": payload["summary"]["approved_backlog_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
