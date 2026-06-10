#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMO_STATUS = ROOT / "data" / "promo_engine_status.json"
MANUAL_STATS = ROOT / "data" / "manual_social_stats.json"
OUT_CSV = ROOT / "data" / "manual_metric_collection_template.csv"
OUT_MD = ROOT / "admin" / "reports" / "manual-metric-collection.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"


SOURCE_HINTS = {
    "facebook": "Meta Business Suite > Insights",
    "instagram": "Instagram Professional Dashboard > Insights",
    "spotify": "Spotify for Artists > Music/Stats export",
    "tiktok": "TikTok Studio or Creator Center analytics",
    "x": "X Analytics or account profile metrics",
}


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def current_value(manual: dict, platform: str, field: str) -> str:
    return str(((manual.get(platform) or {}).get(field)) or "")


def build_rows(status: dict, manual: dict) -> list[dict]:
    kpi = status.get("kpi") or {}
    pending = kpi.get("pending_manual_by_platform") or {}
    commands = kpi.get("pending_manual_update_by_platform") or {}
    steps = {
        step.get("platform"): step
        for step in (kpi.get("manual_metric_collection_steps") or [])
        if step.get("platform")
    }
    rows = []
    for platform, fields in sorted(pending.items()):
        step = steps.get(platform) or {}
        for field in fields:
            rows.append({
                "platform": platform,
                "field": field,
                "current_value": current_value(manual, platform, field),
                "new_value": "",
                "source_hint": SOURCE_HINTS.get(platform, "Manual platform export"),
                "reason": step.get("reason") or "",
                "update_assignment": f"{platform}.{field}=VALUE",
                "platform_update_command": commands.get(platform, ""),
            })
    return rows


def write_csv(rows: list[dict]) -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "platform",
        "field",
        "current_value",
        "new_value",
        "source_hint",
        "reason",
        "update_assignment",
        "platform_update_command",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_markdown(rows: list[dict], generated_at: str) -> str:
    lines = [
        "# Manual Metric Collection - Lily Roo",
        "",
        f"Generated: {generated_at}",
        "",
        f"Pending fields: **{len(rows)}**",
        "",
        "Fill `new_value` in `data/manual_metric_collection_template.csv`, then run the platform update command with real values.",
        "",
    ]
    by_platform = {}
    for row in rows:
        by_platform.setdefault(row["platform"], []).append(row)
    for platform, platform_rows in by_platform.items():
        lines.append(f"## {platform}")
        lines.append("")
        lines.append(f"Source: {SOURCE_HINTS.get(platform, 'Manual platform export')}")
        reason = platform_rows[0].get("reason")
        if reason:
            lines.append(f"Why: {reason}")
        lines.append("")
        for row in platform_rows:
            lines.append(f"- `{row['field']}` current `{row['current_value']}` -> `VALUE`")
        command = platform_rows[0].get("platform_update_command")
        if command:
            lines.append("")
            lines.append(f"Command: `{command}`")
        lines.append("")
    if not rows:
        lines.append("No pending manual metric fields.")
        lines.append("")
    return "\n".join(lines)


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


def sync_admin(markdown: str) -> None:
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    html = replace_text_embed(html, "embedded-manual-metric-collection", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    status = read_json(PROMO_STATUS, {})
    manual = read_json(MANUAL_STATS, {})
    rows = build_rows(status, manual)
    write_csv(rows)
    markdown = build_markdown(rows, generated_at)
    OUT_MD.write_text(markdown, encoding="utf-8")
    sync_admin(markdown)
    print(json.dumps({
        "csv": str(OUT_CSV.relative_to(ROOT)),
        "report": str(OUT_MD.relative_to(ROOT)),
        "pending_fields": len(rows),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
