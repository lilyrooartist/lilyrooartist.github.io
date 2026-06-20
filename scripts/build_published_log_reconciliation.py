#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLISHED_LOG = ROOT / "admin" / "content" / "Published_Log.csv"
SOCIAL_EXECUTIONS = ROOT / "data" / "social_execution_snapshot.json"
MANUAL_DISTRIBUTION = ROOT / "data" / "manual_distribution_packet.json"
PROMO_ENGINE_STATUS = ROOT / "data" / "promo_engine_status.json"
OUT = ROOT / "data" / "published_log_reconciliation.json"
REPORT = ROOT / "admin" / "reports" / "published-log-reconciliation.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def published_source(status: dict) -> dict:
    for source in ((status.get("freshness") or {}).get("sources") or []):
        if source.get("name") == "published_log":
            return source
    return {}


def logged_ids(rows: list[dict]) -> set[str]:
    ids = set()
    for row in rows:
        content_id = (row.get("content_id") or "").strip()
        if content_id:
            ids.add(content_id)
        notes = row.get("notes") or ""
        marker = "manual_distribution_id="
        if marker in notes:
            ids.add(notes.split(marker, 1)[1].split(";", 1)[0].strip())
    return ids


def worker_export_packet(executions: dict, existing_ids: set[str]) -> dict:
    rows = []
    for item in executions.get("rows") or []:
        post_id = (item.get("post_id") or "").strip()
        if item.get("status") != "posted" or not post_id:
            continue
        rows.append({
            "post_id": post_id,
            "platform": item.get("platform") or "",
            "post_url": item.get("post_url") or "",
            "logged": post_id in existing_ids,
        })
    return {
        "posted_worker_count": len(rows),
        "unlogged_worker_count": len([row for row in rows if not row["logged"]]),
        "rows": rows,
        "preview_command": "python3 scripts/export_social_executions.py --dry-run",
        "apply_command": "python3 scripts/export_social_executions.py --refresh-admin",
    }


def manual_log_packet(packet: dict, existing_ids: set[str]) -> dict:
    rows = []
    for item in packet.get("rows") or []:
        post_id = item.get("id") or ""
        logged = bool(item.get("logged")) or post_id in existing_ids
        if logged:
            continue
        rows.append({
            "id": post_id,
            "release": item.get("release") or "",
            "platform": item.get("platform") or "",
            "status": item.get("distribution_status") or "",
            "requires_public_url": (item.get("log_effect") or {}).get("requires_public_url", True),
            "log_preview_command": item.get("log_preview_command") or "",
            "log_apply_command": item.get("log_apply_command") or "",
            "public_community_url": (packet.get("summary") or {}).get("public_community_url") or "",
        })
    return {
        "unlogged_manual_count": len(rows),
        "rows": rows,
        "guardrail": "Only log manual distribution after the public post URL exists.",
    }


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    worker = payload["worker_export"]
    manual = payload["manual_logging"]
    lines = [
        "# Published Log Reconciliation - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Published log status: **{summary['published_log_status']}**",
        f"- Published log rows: **{summary['published_log_rows']}**",
        f"- Unlogged Worker posts: **{summary['unlogged_worker_posts']}**",
        f"- Unlogged manual posts: **{summary['unlogged_manual_posts']}**",
        f"- Reconciliation needed: **{summary['reconciliation_needed']}**",
        "",
        "## Worker Export",
        f"- Posted Worker records: **{worker['posted_worker_count']}**",
        f"- Unlogged Worker records: **{worker['unlogged_worker_count']}**",
        f"- Preview/check: `{worker['preview_command']}`",
        f"- Apply after review: `{worker['apply_command']}`",
        "",
        "## Manual Logging",
        f"- Unlogged manual rows: **{manual['unlogged_manual_count']}**",
        f"- Guardrail: {manual['guardrail']}",
    ]
    for row in manual["rows"]:
        lines.append(f"- **{row['release']} {row['platform']}** (`{row['id']}`)")
        lines.append(f"  - Status: `{row['status']}`")
        if row.get("public_community_url"):
            lines.append(f"  - Posting surface: {row['public_community_url']}")
        if row.get("log_preview_command"):
            lines.append(f"  - Preview URL log: `{row['log_preview_command']}`")
        if row.get("log_apply_command"):
            lines.append(f"  - Apply URL log after posting: `{row['log_apply_command']}`")
    lines.extend([
        "",
        "## Guardrails",
        "- This reconciliation is review-only and does not export, append, post, or publish.",
        "- Worker export apply should run only after the dry run shows posted records with public URLs.",
        "- Manual rows require real public URLs; never replace `PUBLIC_URL` with a placeholder.",
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
    html = replace_json_embed(html, "embedded-published-log-reconciliation", payload)
    html = replace_text_embed(html, "embedded-published-log-reconciliation-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    published_rows = read_csv(PUBLISHED_LOG)
    existing_ids = logged_ids(published_rows)
    status = read_json(PROMO_ENGINE_STATUS, {})
    source = published_source(status)
    worker = worker_export_packet(read_json(SOCIAL_EXECUTIONS, {}), existing_ids)
    manual = manual_log_packet(read_json(MANUAL_DISTRIBUTION, {}), existing_ids)
    latest = published_rows[-1] if published_rows else {}
    reconciliation_needed = bool(worker["unlogged_worker_count"] or manual["unlogged_manual_count"] or source.get("status") == "stale")
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "published_log": str(PUBLISHED_LOG.relative_to(ROOT)),
            "promo_engine_status": str(PROMO_ENGINE_STATUS.relative_to(ROOT)),
            "social_execution_snapshot": str(SOCIAL_EXECUTIONS.relative_to(ROOT)),
            "manual_distribution_packet": str(MANUAL_DISTRIBUTION.relative_to(ROOT)),
        },
        "summary": {
            "published_log_status": source.get("status") or "unknown",
            "published_log_rows": len(published_rows),
            "latest_entry_date": latest.get("date") or "",
            "latest_entry_platform": latest.get("platform") or "",
            "latest_entry_content_id": latest.get("content_id") or "",
            "latest_entry_url": latest.get("post_id_or_url") or "",
            "unlogged_worker_posts": worker["unlogged_worker_count"],
            "unlogged_manual_posts": manual["unlogged_manual_count"],
            "reconciliation_needed": reconciliation_needed,
            "next_preview_command": worker["preview_command"],
            "next_apply_command": worker["apply_command"] if worker["unlogged_worker_count"] else "",
        },
        "worker_export": worker,
        "manual_logging": manual,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(payload)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(payload, markdown)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), "reconciliation_needed": reconciliation_needed}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
