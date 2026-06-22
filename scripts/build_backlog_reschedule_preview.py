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
EXECUTOR_READINESS = ROOT / "data" / "executor_readiness_snapshot.json"
PROMO_STATUS = ROOT / "data" / "promo_engine_status.json"
MANUAL_POSTING = ROOT / "data" / "manual_posting_clipboard.json"
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
    for key in ("platform_fix_needed", "approval_needed", "manual_handoff_needed", "latest_attention"):
        for row in summary.get(key) or []:
            post_id = row.get("post_id")
            if post_id and post_id not in blockers:
                blockers[post_id] = row
    return blockers


def clearance_steps(blocker: dict, readiness: dict) -> list[str]:
    platform = str(blocker.get("platform") or "").strip().lower()
    reason = str(blocker.get("reason") or "").strip()
    platform_payload = ((readiness.get("payload") or {}).get("platforms") or {}).get(platform) or {}
    missing = platform_payload.get("missing_secrets") or blocker.get("missing_secrets") or []
    steps = []
    if reason == "tiktok_credentials_missing" or platform == "tiktok":
        if missing:
            steps.append("Add local TikTok OAuth credentials, then push upload-mode worker secrets: " + ", ".join(missing) + ".")
        if platform_payload.get("public_posting_approved") is False:
            steps.append("Keep direct public posting blocked until TikTok public-posting approval is confirmed; upload mode can still create inbox drafts after credentials.")
        steps.append("Run `python3 scripts/build_tiktok_setup_preflight.py` and `python3 scripts/refresh_promo_admin.py` after repair.")
    elif blocker:
        steps.append("Clear the executor attention item in data/social_execution_snapshot.json before normal reschedule apply.")
    return steps


def preview_command(status: dict) -> str:
    monetization = (status.get("kpi") or {}).get("monetization") or {}
    command = monetization.get("backlog_reschedule_preview_command") or ""
    if command:
        return command
    return "python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at '2026-06-14T10:00:00-04:00' --spacing-hours 24"


def apply_command(status: dict) -> str:
    monetization = (status.get("kpi") or {}).get("monetization") or {}
    return monetization.get("backlog_reschedule_apply_command") or ""


def override_apply_command(status: dict) -> str:
    command = apply_command(status)
    if not command:
        return ""
    if " --allow-blocked" in command:
        return command
    if " --apply" in command:
        return command.replace(" --apply", " --allow-blocked --apply", 1)
    return command + " --allow-blocked"


def quote_datetime(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def scoped_reschedule_command(item: dict, apply: bool = False) -> str:
    command = (
        "python3 scripts/reschedule_scheduled_posts.py "
        f"--id {item.get('id') or ''} "
        f"--start-at {quote_datetime(item.get('proposed_scheduled_at') or '')} "
        "--spacing-hours 24"
    )
    if apply:
        command += " --apply --refresh-admin"
    return command


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
    readiness = read_json(EXECUTOR_READINESS, {})
    manual_posting = read_json(MANUAL_POSTING, {})
    manual_handoff_ids = {
        card.get("id") or ""
        for card in manual_posting.get("post_cards") or []
        if card.get("postable_now")
    }
    published_ids = load_published_ids()
    blockers = load_execution_blockers()
    rows = []
    manual_handoff_items = []
    for row in read_csv(QUEUE):
        row_id = row.get("id") or ""
        scheduled_at = parse_datetime(row.get("scheduled_at") or "")
        if not row_id or row_id in published_ids or not scheduled_at:
            continue
        if str(row.get("approved") or "").strip().lower() == "yes" and scheduled_at < now:
            if row_id in manual_handoff_ids:
                manual_handoff_items.append({
                    "id": row_id,
                    "platform": row.get("platform") or "",
                    "song": row.get("song") or "",
                    "current_scheduled_at": row.get("scheduled_at") or "",
                    "handoff_status": "manual_posting_clipboard",
                    "handoff_report": "admin/reports/manual-posting-clipboard.md",
                    "reason": "Manual/community row is ready for manual posting and public URL logging; it is excluded from auto-reschedule commands.",
                })
                continue
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
        steps = clearance_steps(blocker, readiness)
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
            "blocker_kind": blocker.get("reason") or blocker.get("status") or "",
            "blocks_normal_apply": bool(blocker),
            "safe_apply_available": not bool(blocker),
            "clearance_steps": steps,
        })

    blocked_items = [item for item in items if item["blocked"]]
    clearance_summary = []
    for item in blocked_items:
        for step in item.get("clearance_steps") or []:
            if step not in clearance_summary:
                clearance_summary.append(step)
    safe_apply_command = apply_command(status) if not blocked_items else ""
    blocked_apply_command = apply_command(status) if blocked_items else ""
    clear_items = [item for item in items if not item["blocked"]]
    clear_subset = partial_clear_apply_manifest(clear_items, blocked_items)
    summary = {
        "approved_backlog_count": len(items),
        "blocked_backlog_count": len(blocked_items),
        "clear_to_apply_count": len(items) - len(blocked_items),
        "partial_clear_apply_available": bool(clear_items),
        "partial_clear_apply_count": len(clear_items),
        "start_at": start_at.isoformat(),
        "spacing_hours": spacing_hours,
        "preview_command": preview_command(status),
        "apply_command": safe_apply_command,
        "blocked_apply_command": blocked_apply_command,
        "override_apply_command": override_apply_command(status) if blocked_items else "",
        "apply_blocked_reason": "Known executor/platform blockers must clear before normal apply." if blocked_items else "",
        "apply_allowed_without_override": len(blocked_items) == 0,
        "blocked_ids": [item["id"] for item in blocked_items],
        "normal_apply_gate": "blocked_until_clearance_steps_complete" if blocked_items else "clear",
        "clearance_steps": clearance_summary,
        "partial_clear_preview_commands": clear_subset["preview_commands"],
        "partial_clear_apply_commands": clear_subset["apply_commands"],
        "manual_handoff_count": len(manual_handoff_items),
        "manual_handoff_ids": [item["id"] for item in manual_handoff_items],
    }
    return {
        "generated_at": datetime.now().astimezone().isoformat(),
        "safe_mode": True,
        "source": {
            "scheduled_posts": str(QUEUE.relative_to(ROOT)),
            "published_log": str(PUBLISHED_LOG.relative_to(ROOT)),
            "social_execution_snapshot": str(SOCIAL_EXECUTIONS.relative_to(ROOT)),
            "executor_readiness": str(EXECUTOR_READINESS.relative_to(ROOT)),
            "promo_engine_status": str(PROMO_STATUS.relative_to(ROOT)),
            "manual_posting_clipboard": str(MANUAL_POSTING.relative_to(ROOT)),
        },
        "summary": summary,
        "backlog_clearance_manifest": backlog_clearance_manifest(summary, items),
        "partial_clear_apply_manifest": clear_subset,
        "manual_handoff_items": manual_handoff_items,
        "items": items,
    }


def partial_clear_apply_manifest(clear_items: list[dict], blocked_items: list[dict]) -> dict:
    preview_commands = [scoped_reschedule_command(item, apply=False) for item in clear_items]
    apply_commands = [scoped_reschedule_command(item, apply=True) for item in clear_items]
    return {
        "status": "ready" if clear_items else "empty",
        "clear_to_apply_count": len(clear_items),
        "blocked_backlog_count": len(blocked_items),
        "clear_ids": [item.get("id") or "" for item in clear_items],
        "blocked_ids_retained": [item.get("id") or "" for item in blocked_items],
        "preview_commands": preview_commands,
        "apply_commands": apply_commands,
        "recommended_next_command": preview_commands[0] if preview_commands else "",
        "recommended_apply_command": apply_commands[0] if apply_commands else "",
        "operator_checklist": [
            "Preview each clear row before applying it.",
            "Apply only rows listed in clear_ids; do not use --allow-blocked for this partial-clear path.",
            "Refresh Admin after each apply command, then rebuild this preview before applying the next clear row.",
            "Leave blocked_ids_retained unchanged until their platform or executor clearance steps are complete.",
        ],
        "completion_evidence": [
            "The applied clear row has a future scheduled_at value in data/scheduled_posts.csv.",
            "data/backlog_reschedule_preview.json shows one fewer clear-to-apply past-due row after refresh.",
            "Blocked rows remain listed in blocked_ids_retained until their clearance steps are complete.",
        ],
        "guardrails": [
            "Partial clear commands are scoped with --id and never include --allow-blocked.",
            "This path reschedules only unblocked approved rows; it does not approve, publish, or repair executors.",
        ],
    }


def backlog_clearance_manifest(summary: dict, items: list[dict]) -> dict:
    blocked_items = [item for item in items if item.get("blocked")]
    return {
        "status": summary.get("normal_apply_gate") or "unknown",
        "approved_backlog_count": summary.get("approved_backlog_count") or 0,
        "blocked_backlog_count": summary.get("blocked_backlog_count") or 0,
        "clear_to_apply_count": summary.get("clear_to_apply_count") or 0,
        "partial_clear_apply_available": bool(summary.get("partial_clear_apply_available")),
        "partial_clear_apply_count": summary.get("partial_clear_apply_count") or 0,
        "blocked_ids": summary.get("blocked_ids") or [],
        "preview_command": summary.get("preview_command") or "",
        "safe_apply_command": summary.get("apply_command") or "",
        "blocked_apply_command": summary.get("blocked_apply_command") or "",
        "override_apply_command": summary.get("override_apply_command") or "",
        "apply_allowed_without_override": bool(summary.get("apply_allowed_without_override")),
        "apply_gate": summary.get("normal_apply_gate") or "unknown",
        "clearance_steps": summary.get("clearance_steps") or [],
        "blocked_items": [
            {
                "id": item.get("id") or "",
                "platform": item.get("platform") or "",
                "song": item.get("song") or "",
                "blocker_kind": item.get("blocker_kind") or "",
                "blocker_reason": item.get("blocker_reason") or "",
                "proposed_scheduled_at": item.get("proposed_scheduled_at") or "",
                "clearance_steps": item.get("clearance_steps") or [],
            }
            for item in blocked_items
        ],
        "operator_checklist": [
            "Run the preview command and confirm it proposes only approved unpublished backlog rows.",
            "If partial_clear_apply_available is true, use the scoped partial-clear commands for unblocked rows while blocked rows are repaired.",
            "Complete every listed platform/executor clearance step before normal apply.",
            "Refresh Admin and confirm the normal apply gate is clear.",
            "Apply only when safe_apply_command is populated without --allow-blocked.",
            "After apply, refresh Admin and confirm the backlog rows have future scheduled_at values.",
        ],
        "completion_evidence": [
            "data/backlog_reschedule_preview.json shows normal_apply_gate clear.",
            "data/platform_repair_status.json shows the affected platform repair gate clear.",
            "data/social_execution_snapshot.json no longer reports the row as blocked by executor/platform repair.",
            "data/promo_engine_status.json and lilyroo.com/admin expose a safe apply command or no approved past-due backlog.",
        ],
        "guardrails": [
            "Normal apply stays hidden while blocked_ids are present.",
            "Do not use the override command unless accepting the blocked executor risk deliberately.",
            "A reschedule does not publish, approve, or repair platform credentials by itself.",
        ],
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
    manifest = payload.get("backlog_clearance_manifest") or {}
    lines = [
        "# Backlog Reschedule Preview - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Approved backlog rows: **{summary['approved_backlog_count']}**",
        f"- Rows with known blockers: **{summary['blocked_backlog_count']}**",
        f"- Clear to apply without override: **{summary['clear_to_apply_count']}**",
        f"- Manual handoff rows excluded from auto-reschedule: **{summary.get('manual_handoff_count', 0)}**",
        f"- Start at: **{summary['start_at']}**",
        f"- Spacing hours: **{summary['spacing_hours']}**",
        f"- Apply allowed without override: **{summary['apply_allowed_without_override']}**",
        f"- Normal apply gate: **{summary.get('normal_apply_gate', 'unknown')}**",
    ]
    if payload.get("manual_handoff_items"):
        lines.extend([
            "",
            "## Manual Handoff Rows",
        ])
        for item in payload["manual_handoff_items"]:
            lines.append(f"- **{item['platform']} - {item['song']}** (`{item['id']}`)")
            lines.append(f"  - Current: `{item['current_scheduled_at']}`")
            lines.append(f"  - Handoff: `{item['handoff_report']}`")
            lines.append(f"  - Reason: {item['reason']}")
    lines.extend(["", "## Proposed Reschedule"])
    for item in payload["items"]:
        lines.append(f"- **{item['platform']} - {item['song']}** (`{item['id']}`)")
        lines.append(f"  - Current: `{item['current_scheduled_at']}`")
        lines.append(f"  - Proposed: `{item['proposed_scheduled_at']}`")
        if item["blocked"]:
            lines.append(f"  - Blocker: {item['blocker_reason'] or item['blocker_status'] or 'executor attention required'}")
            for step in item.get("clearance_steps") or []:
                lines.append(f"  - Clearance: {step}")
    lines.extend([
        "",
        "## Clearance Manifest",
        f"- Status: **{manifest.get('status', 'unknown')}**",
        f"- Blocked IDs: `{', '.join(manifest.get('blocked_ids') or []) or 'none'}`",
        f"- Safe apply command: `{manifest.get('safe_apply_command') or 'blocked until clearance steps complete'}`",
        f"- Partial clear apply available: **{manifest.get('partial_clear_apply_available', False)}**",
        f"- Partial clear apply count: **{manifest.get('partial_clear_apply_count', 0)}**",
        f"- Apply gate: **{manifest.get('apply_gate', 'unknown')}**",
        "",
        "## Partial Clear Apply",
    ])
    partial = payload.get("partial_clear_apply_manifest") or {}
    lines.extend([
        f"- Status: **{partial.get('status', 'unknown')}**",
        f"- Clear IDs: `{', '.join(partial.get('clear_ids') or []) or 'none'}`",
        f"- Blocked IDs retained: `{', '.join(partial.get('blocked_ids_retained') or []) or 'none'}`",
        f"- Recommended preview: `{partial.get('recommended_next_command') or 'none'}`",
        f"- Recommended apply: `{partial.get('recommended_apply_command') or 'none'}`",
    ])
    for command in partial.get("preview_commands") or []:
        lines.append(f"- Preview clear row: `{command}`")
    lines.extend([
        "",
        "### Operator Checklist",
    ])
    for item in (partial.get("operator_checklist") or []) + (manifest.get("operator_checklist") or []):
        lines.append(f"- {item}")
    lines.extend([
        "",
        "### Completion Evidence",
    ])
    for item in (partial.get("completion_evidence") or []) + (manifest.get("completion_evidence") or []):
        lines.append(f"- {item}")
    lines.extend([
        "",
        "### Clearance Guardrails",
    ])
    for item in (partial.get("guardrails") or []) + (manifest.get("guardrails") or []):
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Commands",
        f"- Preview: `{summary['preview_command']}`",
        f"- Partial clear preview: `{(payload.get('partial_clear_apply_manifest') or {}).get('recommended_next_command') or 'none'}`",
        f"- Partial clear apply: `{(payload.get('partial_clear_apply_manifest') or {}).get('recommended_apply_command') or 'none'}`",
        f"- Safe apply: `{summary['apply_command']}`" if summary.get("apply_command") else "- Safe apply: none until blockers clear",
        f"- Blocked apply command: `{summary['blocked_apply_command']}`" if summary.get("blocked_apply_command") else "- Blocked apply command: none",
        f"- Deliberate override command: `{summary['override_apply_command']}`" if summary.get("override_apply_command") else "- Deliberate override command: none",
        "",
        "## Guardrails",
        "- This preview does not write schedule changes, approve posts, publish posts, or push secrets.",
        "- The normal apply command is hidden while rows have known executor blockers.",
        "- The override command includes `--allow-blocked` and is only for deliberate review after accepting the blocker risk.",
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
