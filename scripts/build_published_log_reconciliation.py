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
    approval_docket = packet.get("manual_approval_docket") or {}
    distribution_docket = packet.get("manual_distribution_docket") or {}
    for item in packet.get("rows") or []:
        post_id = item.get("id") or ""
        logged = bool(item.get("logged")) or post_id in existing_ids
        if logged:
            continue
        posting = item.get("manual_posting_packet") or {}
        approval_required = bool(posting.get("approval_required"))
        postable_now = bool(posting.get("postable_now"))
        if approval_required:
            log_gate = "blocked_until_manual_approval"
            next_step = "Approve the manual row after review, post it in YouTube Studio Community, then log the public URL."
        elif postable_now:
            log_gate = "blocked_until_public_url"
            next_step = "Post manually in YouTube Studio Community, then replace PUBLIC_URL with the real public URL."
        else:
            log_gate = "ready_to_log" if item.get("published_url") else "blocked_until_public_url"
            next_step = "Use the log preview command with the real public URL before applying."
        rows.append({
            "id": post_id,
            "release": item.get("release") or "",
            "platform": item.get("platform") or "",
            "status": item.get("distribution_status") or "",
            "log_gate": log_gate,
            "approval_required": approval_required,
            "postable_now": postable_now,
            "requires_public_url": (item.get("log_effect") or {}).get("requires_public_url", True),
            "next_step": next_step,
            "approval_preview_command": item.get("approval_preview_command") or "",
            "approval_command": item.get("approval_command") or "",
            "log_preview_command": item.get("log_preview_command") or "",
            "log_apply_command": item.get("log_apply_command") or "",
            "public_community_url": (packet.get("summary") or {}).get("public_community_url") or "",
        })
    gate_counts = {}
    for row in rows:
        gate = row.get("log_gate") or "unknown"
        gate_counts[gate] = gate_counts.get(gate, 0) + 1
    return {
        "unlogged_manual_count": len(rows),
        "approval_gate": {
            "status": approval_docket.get("status") or "unknown",
            "ready_count": approval_docket.get("ready_count") or 0,
            "blocked_count": approval_docket.get("blocked_count") or 0,
            "ready_ids": approval_docket.get("ready_ids") or [],
            "blocked_ids": approval_docket.get("blocked_ids") or [],
            "preview_command": approval_docket.get("preview_command") or "",
            "apply_command": approval_docket.get("apply_command") or "",
            "guardrail": approval_docket.get("guardrail") or "",
        },
        "posting_gate": {
            "status": distribution_docket.get("status") or "unknown",
            "review_count": distribution_docket.get("review_count") or 0,
            "postable_count": distribution_docket.get("postable_count") or 0,
            "logged_count": distribution_docket.get("logged_count") or 0,
            "public_community_url": distribution_docket.get("public_community_url") or "",
        },
        "gate_counts": dict(sorted(gate_counts.items())),
        "rows": rows,
        "url_logging": {
            "status": "waiting_for_public_urls" if any(row.get("log_gate") == "blocked_until_public_url" for row in rows) else "clear",
            "worksheet_path": (packet.get("manual_completion_manifest") or {}).get("url_template_path") or "",
            "session_file_path": "data/manual-posting-cards/youtube-community-session.md",
            "batch_preview_command": (packet.get("manual_completion_manifest") or {}).get("batch_log_preview_command") or "",
            "batch_apply_command": (packet.get("manual_completion_manifest") or {}).get("batch_log_apply_command") or "",
            "partial_apply_command": (
                f"python3 scripts/log_manual_distribution.py --from-csv {(packet.get('manual_completion_manifest') or {}).get('url_template_path')} --allow-partial --apply --refresh-admin"
                if (packet.get("manual_completion_manifest") or {}).get("url_template_path")
                else ""
            ),
            "pending_ids": [row.get("id") for row in rows if row.get("log_gate") == "blocked_until_public_url"],
            "guardrail": "Use only real public YouTube Community URLs; never apply rows containing PUBLIC_URL or blanks.",
        },
        "guardrail": "Only log manual distribution after approval, manual posting, and a real public post URL.",
    }


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    worker = payload["worker_export"]
    manual = payload["manual_logging"]
    url_logging = manual.get("url_logging") or {}
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
        "",
        "### Manual Log Gates",
        f"- Approval gate: **{(manual.get('approval_gate') or {}).get('status', 'unknown')}**; ready: **{(manual.get('approval_gate') or {}).get('ready_count', 0)}**; blocked: **{(manual.get('approval_gate') or {}).get('blocked_count', 0)}**",
        f"- Posting gate: **{(manual.get('posting_gate') or {}).get('status', 'unknown')}**; needs review: **{(manual.get('posting_gate') or {}).get('review_count', 0)}**; postable: **{(manual.get('posting_gate') or {}).get('postable_count', 0)}**",
        f"- URL logging gate: **{url_logging.get('status', 'unknown')}**",
    ]
    if url_logging.get("session_file_path"):
        lines.append(f"- Posting session: `{url_logging['session_file_path']}`")
    if url_logging.get("worksheet_path"):
        lines.append(f"- URL worksheet: `{url_logging['worksheet_path']}`")
    if url_logging.get("partial_apply_command"):
        lines.append(f"- Partial URL apply: `{url_logging['partial_apply_command']}`")
    approval_gate = manual.get("approval_gate") or {}
    if approval_gate.get("ready_ids"):
        lines.append(f"- Ready approval IDs: `{', '.join(approval_gate['ready_ids'])}`")
    if approval_gate.get("blocked_ids"):
        lines.append(f"- Blocked approval IDs: `{', '.join(approval_gate['blocked_ids'])}`")
    if approval_gate.get("preview_command"):
        lines.append(f"- Preview approvals: `{approval_gate['preview_command']}`")
    if approval_gate.get("apply_command"):
        lines.append(f"- Approve after review: `{approval_gate['apply_command']}`")
    lines.append("")
    lines.append("### Manual Rows")
    for row in manual["rows"]:
        lines.append(f"- **{row['release']} {row['platform']}** (`{row['id']}`)")
        lines.append(f"  - Status: `{row['status']}`; log gate: `{row.get('log_gate', 'unknown')}`")
        if row.get("next_step"):
            lines.append(f"  - Next step: {row['next_step']}")
        if row.get("public_community_url"):
            lines.append(f"  - Posting surface: {row['public_community_url']}")
        if row.get("approval_preview_command"):
            lines.append(f"  - Preview approval: `{row['approval_preview_command']}`")
        if row.get("approval_command"):
            lines.append(f"  - Approve after review: `{row['approval_command']}`")
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


def next_reconciliation_gate(worker: dict, manual: dict) -> str:
    if worker["unlogged_worker_count"]:
        return "worker_export"
    if not manual["unlogged_manual_count"]:
        return "clear"
    url_logging = manual.get("url_logging") or {}
    posting_gate = manual.get("posting_gate") or {}
    if url_logging.get("status") == "waiting_for_public_urls" and posting_gate.get("postable_count", 0) > 0:
        return "manual_public_url_logging"
    return "manual_approval"


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
    approval_gate = manual.get("approval_gate") or {}
    posting_gate = manual.get("posting_gate") or {}
    next_preview_command = worker["preview_command"] if worker["unlogged_worker_count"] else (approval_gate.get("preview_command") or "")
    next_apply_command = ""
    if worker["unlogged_worker_count"]:
        next_apply_command = worker["apply_command"]
    elif manual["unlogged_manual_count"]:
        next_apply_command = approval_gate.get("apply_command") or ""
    url_logging = manual.get("url_logging") or {}
    next_manual_gate = (
        "public_url_logging"
        if manual["unlogged_manual_count"] and url_logging.get("status") == "waiting_for_public_urls"
        else "manual_approval"
        if manual["unlogged_manual_count"]
        else "clear"
    )
    next_gate = next_reconciliation_gate(worker, manual)
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
            "manual_log_gate_counts": manual.get("gate_counts") or {},
            "manual_logging_gate_status": (manual.get("posting_gate") or {}).get("status") or "unknown",
            "reconciliation_needed": reconciliation_needed,
            "next_preview_command": next_preview_command,
            "next_apply_command": next_apply_command,
            "next_gate": next_gate,
            "next_manual_gate": next_manual_gate,
            "url_logging_status": url_logging.get("status") or "unknown",
            "url_logging_session_file": url_logging.get("session_file_path") or "",
            "url_logging_worksheet": url_logging.get("worksheet_path") or "",
            "url_logging_partial_apply_command": url_logging.get("partial_apply_command") or "",
            "posting_gate_status": posting_gate.get("status") or "unknown",
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
