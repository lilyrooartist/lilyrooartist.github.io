#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data" / "scheduled_posts.csv"
EXECUTIONS = ROOT / "data" / "social_execution_snapshot.json"
EXECUTOR_READINESS = ROOT / "data" / "executor_readiness_snapshot.json"
OUT = ROOT / "data" / "scheduled_approval_packet.json"
REPORT = ROOT / "admin" / "reports" / "scheduled-approval-packet.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"
URL_RE = re.compile(r"https?://[^\s|]+")


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


def approval_batch_command(rows: list[dict], *, dry_run: bool) -> str:
    ids = [row.get("id") or "" for row in rows if row.get("id")]
    if not ids:
        return ""
    suffix = " --dry-run" if dry_run else " --refresh-admin"
    return "python3 scripts/update_scheduled_post_approval.py " + " ".join(ids) + suffix


def approval_effect(row: dict, *, target_value: str = "yes") -> dict:
    previous = row.get("approved") or ""
    changed = previous != target_value
    return {
        "field": "approved",
        "from": previous,
        "to": target_value,
        "changed": changed,
        "summary": f"approved {previous!r} -> {target_value!r}",
    }


def approval_effect_summary(rows: list[dict]) -> dict:
    effects = [
        {
            "id": row.get("id") or "",
            "platform": row.get("platform") or "",
            "execution_mode": row.get("execution_mode") or "",
            "effect": row.get("approval_effect") or approval_effect(row),
        }
        for row in rows
        if row.get("id")
    ]
    return {
        "row_count": len(effects),
        "change_count": sum(1 for item in effects if (item.get("effect") or {}).get("changed")),
        "ids": [item["id"] for item in effects],
        "effects": effects,
    }


def platform_slug(platform: str) -> str:
    value = str(platform or "").strip().lower()
    return {
        "youtube community": "youtube",
        "x": "x",
        "instagram": "instagram",
        "tiktok": "tiktok",
        "facebook": "facebook",
    }.get(value, value)


def links_in_text(value: str) -> list[str]:
    return [match.group(0).rstrip(".,);]") for match in URL_RE.finditer(value or "")]


def local_public_path(url: str) -> Path | None:
    parsed = urlparse(url or "")
    if parsed.netloc not in {"www.lilyroo.com", "lilyroo.com", "lilyrooartist.github.io"}:
        return None
    if not parsed.path:
        return None
    return ROOT / parsed.path.lstrip("/")


def check(name: str, status: str, detail: str) -> dict:
    return {"name": name, "status": status, "detail": detail}


def review_checks(row: dict[str, str], item: dict, readiness: dict) -> list[dict]:
    checks = []
    text = row.get("text") or ""
    reply_text = row.get("reply_text") or ""
    media_url = row.get("clip_url") or row.get("imagery_url") or ""
    links = links_in_text("\n".join([text, reply_text]))
    local_asset = local_public_path(media_url)
    platform = row.get("platform") or item.get("platform") or ""
    platform_ready = ((readiness.get("summary") or {}).get("platforms") or {}).get(platform)
    platform_payload = ((readiness.get("payload") or {}).get("platforms") or {}).get(platform_slug(platform)) or {}
    missing_secrets = ", ".join(platform_payload.get("missing_secrets") or [])

    checks.append(check(
        "copy_present",
        "pass" if text else "fail",
        f"{len(text)} characters of primary copy." if text else "Primary copy is empty.",
    ))
    checks.append(check(
        "destination_links_present",
        "pass" if links else "fail",
        f"{len(links)} link(s): {', '.join(links)}" if links else "No destination links found in copy or reply text.",
    ))
    if media_url and local_asset:
        checks.append(check(
            "asset_file_present",
            "pass" if local_asset.exists() else "fail",
            f"{media_url} maps to {local_asset.relative_to(ROOT)}.",
        ))
    elif media_url:
        checks.append(check("asset_file_present", "review", f"{media_url} is external; review manually."))
    else:
        checks.append(check("asset_file_present", "fail", "No media URL is attached."))
    checks.append(check(
        "executor_blocker_confirmed",
        "pass" if item.get("reason") == "not_approved" else "review",
        f"Current executor state is {item.get('status') or 'unknown'} / {item.get('reason') or 'unknown'}.",
    ))
    if platform_ready is True:
        readiness_detail = "Executor readiness snapshot marks platform ready."
        readiness_status = "pass"
    elif platform_ready is False:
        readiness_detail = "Executor readiness snapshot marks platform blocked."
        if missing_secrets:
            readiness_detail += f" Missing secrets: {missing_secrets}."
        readiness_status = "fail"
    else:
        readiness_detail = "Platform readiness is absent from the snapshot."
        readiness_status = "review"
    checks.append(check("platform_readiness", readiness_status, readiness_detail))
    return checks


def checks_passed(checks: list[dict]) -> bool:
    return bool(checks) and all(item.get("status") == "pass" for item in checks)


def build_rows(queue: dict[str, dict[str, str]], executions: dict, readiness: dict) -> list[dict]:
    rows = []
    for item in (executions.get("summary") or {}).get("approval_needed") or []:
        post_id = item.get("post_id") or ""
        row = queue.get(post_id) or {}
        if not row:
            continue
        media_url = row.get("clip_url") or row.get("imagery_url") or ""
        checks = review_checks(row, item, readiness)
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
            "review_checks": checks,
            "review_check_passed": checks_passed(checks),
            "approval_effect": approval_effect(row),
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
        f"- Review checks passed: **{summary['review_check_passed_count']}**",
        f"- Review checks blocked: **{summary['review_check_blocked_count']}**",
        f"- Checked batch IDs: `{', '.join(summary['checked_batch_ids'])}`" if summary.get("checked_batch_ids") else "- Checked batch IDs: none",
        f"- Blocked review IDs: `{', '.join(summary['blocked_review_ids'])}`" if summary.get("blocked_review_ids") else "- Blocked review IDs: none",
        f"- Checked-only preview: `{summary['checked_batch_preview_command']}`" if summary.get("checked_batch_preview_command") else "- Checked-only preview: none",
        f"- Checked-only approve after review: `{summary['checked_batch_apply_command']}`" if summary.get("checked_batch_apply_command") else "- Checked-only approve after review: none",
        f"- Checked-only effect: **{summary['checked_batch_effect']['change_count']}** row(s) would change approval state" if summary.get("checked_batch_effect") else "- Checked-only effect: none",
        f"- Batch preview: `{summary['batch_preview_command']}`" if summary.get("batch_preview_command") else "- Batch preview: none",
        f"- Batch approve after review: `{summary['batch_apply_command']}`" if summary.get("batch_apply_command") else "- Batch approve after review: none",
        f"- Batch effect: **{summary['batch_effect']['change_count']}** row(s) would change approval state" if summary.get("batch_effect") else "- Batch effect: none",
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
        if row.get("review_checks"):
            lines.append("  - Review checks:")
            for item in row["review_checks"]:
                lines.append(f"    - `{item['status']}` {item['name']}: {item['detail']}")
        if row.get("approval_effect"):
            effect = row["approval_effect"]
            lines.append(f"  - Approval effect: `{effect['summary']}`")
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
    readiness = read_json(EXECUTOR_READINESS, {})
    rows = build_rows(queue, executions, readiness)
    checked_rows = [row for row in rows if row.get("review_check_passed")]
    blocked_rows = [row for row in rows if not row.get("review_check_passed")]
    review_check_status_counts = {}
    for row in rows:
        for item in row.get("review_checks") or []:
            status = item.get("status") or "unknown"
            review_check_status_counts[status] = review_check_status_counts.get(status, 0) + 1
    batch_preview_command = approval_batch_command(rows, dry_run=True)
    batch_apply_command = approval_batch_command(rows, dry_run=False)
    checked_batch_preview_command = approval_batch_command(checked_rows, dry_run=True)
    checked_batch_apply_command = approval_batch_command(checked_rows, dry_run=False)
    checked_batch_effect = approval_effect_summary(checked_rows)
    batch_effect = approval_effect_summary(rows)
    payload = {
        "generated_at": now,
        "safe_mode": True,
        "source": {
            "scheduled_posts": str(QUEUE.relative_to(ROOT)),
            "social_execution_snapshot": str(EXECUTIONS.relative_to(ROOT)),
            "executor_readiness": str(EXECUTOR_READINESS.relative_to(ROOT)),
        },
        "summary": {
            "approval_blocker_count": len(rows),
            "auto_count": sum(1 for row in rows if row.get("execution_mode") == "auto"),
            "manual_count": sum(1 for row in rows if row.get("execution_mode") == "manual"),
            "review_check_passed_count": sum(1 for row in rows if row.get("review_check_passed")),
            "review_check_blocked_count": sum(1 for row in rows if not row.get("review_check_passed")),
            "checked_batch_ids": [row.get("id") for row in checked_rows if row.get("id")],
            "blocked_review_ids": [row.get("id") for row in blocked_rows if row.get("id")],
            "review_check_status_counts": dict(sorted(review_check_status_counts.items())),
            "checked_batch_preview_command": checked_batch_preview_command,
            "checked_batch_apply_command": checked_batch_apply_command,
            "checked_batch_effect": checked_batch_effect,
            "preview_command_count": sum(1 for row in rows if row.get("approval_preview_command")),
            "apply_command_count": sum(1 for row in rows if row.get("approval_apply_command")),
            "batch_preview_command": batch_preview_command,
            "batch_apply_command": batch_apply_command,
            "batch_effect": batch_effect,
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
