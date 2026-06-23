#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEDULED = ROOT / "data" / "scheduled_posts.csv"
PUBLISHED = ROOT / "admin" / "content" / "Published_Log.csv"
OUT = ROOT / "data" / "story_throughput_tracking.json"
REPORT = ROOT / "admin" / "reports" / "story-throughput-tracking.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"

RESULT_FIELDS = ["views", "likes", "comments", "shares", "saves", "subs_delta"]
FIRST_MEASUREMENT_HOURS = 24


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


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


def story_rows(rows: list[dict]) -> list[dict]:
    return [row for row in rows if str(row.get("id") or "").startswith("FP-STORY-")]


def published_lookup(rows: list[dict]) -> dict[str, dict]:
    lookup = {}
    for index, row in enumerate(rows, start=2):
        candidates = [str(row.get("content_id") or "").strip()]
        notes = str(row.get("notes") or "")
        for part in notes.replace(";", " ").split():
            if part.startswith("queue_id="):
                candidates.append(part.split("=", 1)[1].strip())
        for key in candidates:
            if key.startswith("FP-STORY-"):
                enriched = dict(row)
                enriched["_csv_row"] = index
                lookup[key] = enriched
    return lookup


def result_values(row: dict) -> dict:
    return {
        field: str(row.get(field) or "").strip()
        for field in RESULT_FIELDS
        if str(row.get(field) or "").strip()
    }


def row_status(scheduled: dict, published: dict | None, now: datetime) -> str:
    if published:
        return "measured" if result_values(published) else "logged_waiting_results"
    scheduled_at = parse_datetime(scheduled.get("scheduled_at"))
    if scheduled_at and scheduled_at <= now:
        return "past_due_unlogged"
    return "queued_future"


def next_action(status: str) -> str:
    return {
        "queued_future": "Wait for the scheduler to publish the row, then export social executions and log the public URL.",
        "past_due_unlogged": "Run social execution capture/export to confirm whether the post published and log the public URL.",
        "logged_waiting_results": "Collect first result metrics after the measurement window and import them with evidence notes.",
        "measured": "Keep this row in the measured story-throughput history.",
    }.get(status, "Review this row in the story throughput report.")


def build_packet() -> dict:
    now = datetime.now(timezone.utc)
    scheduled = story_rows(read_csv(SCHEDULED))
    published = published_lookup(read_csv(PUBLISHED))
    rows = []
    for row in scheduled:
        post_id = row.get("id") or ""
        published_row = published.get(post_id)
        status = row_status(row, published_row, now)
        scheduled_at = parse_datetime(row.get("scheduled_at"))
        measurement_due_at = ""
        if published_row:
            published_at = parse_datetime(published_row.get("date"))
            if published_at:
                measurement_due_at = (published_at + timedelta(hours=FIRST_MEASUREMENT_HOURS)).isoformat()
        elif scheduled_at:
            measurement_due_at = (scheduled_at + timedelta(hours=FIRST_MEASUREMENT_HOURS)).isoformat()
        rows.append({
            "id": post_id,
            "platform": row.get("platform") or "",
            "song": row.get("song") or "",
            "scheduled_at": row.get("scheduled_at") or "",
            "post_type": row.get("post_type") or "",
            "status": status,
            "public_url": (published_row or {}).get("post_id_or_url") or "",
            "published_log_row": (published_row or {}).get("_csv_row") or "",
            "measurement_due_at": measurement_due_at,
            "result_values": result_values(published_row or {}),
            "next_action": next_action(status),
            "copy": row.get("text") or "",
        })
    counts = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    summary = {
        "story_post_count": len(rows),
        "queued_future_count": counts.get("queued_future", 0),
        "past_due_unlogged_count": counts.get("past_due_unlogged", 0),
        "logged_waiting_results_count": counts.get("logged_waiting_results", 0),
        "measured_count": counts.get("measured", 0),
        "platforms": sorted({row.get("platform") for row in rows if row.get("platform")}),
        "measurement_window_hours": FIRST_MEASUREMENT_HOURS,
        "export_preview_command": "python3 scripts/export_social_executions.py --dry-run",
        "export_apply_command": "python3 scripts/export_social_executions.py --refresh-admin",
        "result_collection_report": "admin/reports/experiment-result-clipboard.md",
    }
    return {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "scheduled_posts": str(SCHEDULED.relative_to(ROOT)),
            "published_log": str(PUBLISHED.relative_to(ROOT)),
        },
        "summary": summary,
        "rows": rows,
    }


def build_markdown(packet: dict) -> str:
    summary = packet["summary"]
    lines = [
        "# Story Throughput Tracking - Lily Roo",
        "",
        f"Generated: {packet['generated_at']}",
        "",
        "## Summary",
        f"- Story posts scheduled: **{summary['story_post_count']}**",
        f"- Queued future: **{summary['queued_future_count']}**",
        f"- Past due without public URL: **{summary['past_due_unlogged_count']}**",
        f"- Logged, waiting results: **{summary['logged_waiting_results_count']}**",
        f"- Measured: **{summary['measured_count']}**",
        f"- Platforms: **{', '.join(summary['platforms']) or 'none'}**",
        "",
        "## Commands",
        f"- Preview worker export: `{summary['export_preview_command']}`",
        f"- Apply worker export after review: `{summary['export_apply_command']}`",
        f"- Result collection handoff: `{summary['result_collection_report']}`",
        "",
        "## Rows",
    ]
    if not packet["rows"]:
        lines.append("- No story-throughput rows are scheduled.")
    for row in packet["rows"]:
        lines.append(f"- **{row['id']}** - {row['platform']} / {row['song']}")
        lines.append(f"  - Status: `{row['status']}`; scheduled: `{row['scheduled_at']}`")
        if row.get("public_url"):
            lines.append(f"  - Public URL: {row['public_url']}")
        if row.get("measurement_due_at"):
            lines.append(f"  - First measurement due: `{row['measurement_due_at']}`")
        if row.get("result_values"):
            values = ", ".join(f"{key}={value}" for key, value in row["result_values"].items())
            lines.append(f"  - Results: `{values}`")
        lines.append(f"  - Next: {row['next_action']}")
    lines.append("")
    lines.append("## Guardrails")
    lines.append("- This packet is read-only; it does not publish, approve, or log URLs.")
    lines.append("- Only real public URLs from successful social executions should enter Published_Log.csv.")
    lines.append("- Scheduled volume is not winner evidence until a public URL and measured results exist.")
    lines.append("")
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


def sync_admin(packet: dict, markdown: str) -> None:
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    html = replace_json_embed(html, "embedded-story-throughput-tracking", packet)
    html = replace_text_embed(html, "embedded-story-throughput-tracking-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(packet)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(packet, markdown)
    print(json.dumps({
        "output": str(OUT.relative_to(ROOT)),
        "story_post_count": packet["summary"]["story_post_count"],
        "queued_future_count": packet["summary"]["queued_future_count"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
