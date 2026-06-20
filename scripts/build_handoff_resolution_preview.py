#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSHEET = ROOT / "data" / "human_handoff_resolution_worksheet.csv"
HANDOFF = ROOT / "data" / "human_handoff_packet.json"
OUT = ROOT / "data" / "human_handoff_resolution_preview.json"
REPORT = ROOT / "admin" / "reports" / "human-handoff-resolution-preview.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"

FORBIDDEN_TOKENS = {"--apply", "--refresh-admin"}
MAX_OUTPUT_CHARS = 2000


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def read_rows() -> list[dict]:
    if not WORKSHEET.exists():
        return []
    with WORKSHEET.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def command_tokens(command: str) -> list[str]:
    try:
        return shlex.split(command)
    except ValueError:
        return []


def is_safe_preview(command: str) -> tuple[bool, str]:
    if not command:
        return False, "missing_preview_command"
    if "PUBLIC_URL" in command:
        return False, "placeholder_public_url"
    tokens = command_tokens(command)
    if len(tokens) < 2:
        return False, "unparseable_command"
    if tokens[0] != "python3" or not tokens[1].startswith("scripts/"):
        return False, "unsupported_command"
    if any(token in FORBIDDEN_TOKENS for token in tokens):
        return False, "apply_or_refresh_token_present"
    if "--dry-run" in tokens:
        return True, "dry_run_command"
    if tokens[1] == "scripts/reschedule_scheduled_posts.py" and "--apply" not in tokens:
        return True, "reschedule_preview_command"
    return False, "not_marked_preview_safe"


def classify_result(returncode: int, output: str) -> str:
    text = output.lower()
    if "error:" in text or "missing from" in text or "no metric assignments supplied" in text:
        return "input_missing"
    if returncode != 0:
        return "preview_failed"
    if "warning:" in text or "known blocker" in text:
        return "preview_ok_with_warning"
    return "preview_ok"


def sanitize_output(output: str) -> str:
    sanitized = output
    for path in (ROOT, ROOT.parent):
        prefix = str(path)
        sanitized = sanitized.replace(prefix + "/", "")
        sanitized = sanitized.replace(prefix, ".")
    return sanitized


def run_preview(row: dict) -> dict:
    command = row.get("preview_command") or ""
    safe, safety_reason = is_safe_preview(command)
    result = {
        "task_id": row.get("task_id") or "",
        "phase": row.get("phase") or "",
        "status": row.get("status") or "",
        "input_needed": row.get("input_needed") or "",
        "command": command,
        "safety": "safe_preview" if safe else "skipped",
        "safety_reason": safety_reason,
        "returncode": None,
        "preview_status": "skipped" if not safe else "",
        "output_excerpt": "",
        "completion_evidence": row.get("completion_evidence") or "",
        "guardrail": row.get("guardrail") or "",
    }
    if not safe:
        return result
    completed = subprocess.run(
        command_tokens(command),
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=60,
        check=False,
    )
    output = sanitize_output((completed.stdout or "").strip())
    result.update({
        "returncode": completed.returncode,
        "preview_status": classify_result(completed.returncode, output),
        "output_excerpt": output[:MAX_OUTPUT_CHARS],
    })
    return result


def build_payload() -> dict:
    rows = read_rows()
    previews = [run_preview(row) for row in rows]
    status_counts: dict[str, int] = {}
    phase_counts: dict[str, int] = {}
    for item in previews:
        status_counts[item["preview_status"]] = status_counts.get(item["preview_status"], 0) + 1
        phase_counts[item["phase"]] = phase_counts.get(item["phase"], 0) + 1
    executed = [item for item in previews if item.get("safety") == "safe_preview"]
    skipped = [item for item in previews if item.get("safety") != "safe_preview"]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "resolution_worksheet": str(WORKSHEET.relative_to(ROOT)),
            "human_handoff_packet": str(HANDOFF.relative_to(ROOT)),
        },
        "summary": {
            "worksheet_row_count": len(rows),
            "preview_count": len(previews),
            "executed_preview_count": len(executed),
            "skipped_preview_count": len(skipped),
            "status_counts": dict(sorted(status_counts.items())),
            "phase_counts": dict(sorted(phase_counts.items())),
            "safe_command_policy": "Only python3 scripts/* commands with --dry-run, or reschedule previews without --apply, are executed.",
            "mutation_guardrail": "This preview runner never executes apply, refresh-admin, PUBLIC_URL placeholder, non-python, or unsupported commands.",
        },
        "previews": previews,
        "handoff_resolution_summary": (read_json(HANDOFF, {}).get("resolution_worksheet") or {}),
    }


def build_markdown(payload: dict) -> str:
    summary = payload.get("summary") or {}
    lines = [
        "# Human Handoff Resolution Preview - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Worksheet rows: **{summary.get('worksheet_row_count', 0)}**",
        f"- Executed previews: **{summary.get('executed_preview_count', 0)}**",
        f"- Skipped previews: **{summary.get('skipped_preview_count', 0)}**",
        f"- Status counts: `{json.dumps(summary.get('status_counts') or {}, sort_keys=True)}`",
        f"- Policy: {summary.get('safe_command_policy')}",
        f"- Guardrail: {summary.get('mutation_guardrail')}",
        "",
        "## Previews",
    ]
    for item in payload.get("previews") or []:
        lines.append(f"- **{item.get('task_id')}** (`{item.get('preview_status')}`)")
        lines.append(f"  - Phase: `{item.get('phase')}`; input needed: `{item.get('input_needed')}`")
        lines.append(f"  - Safety: `{item.get('safety')}` ({item.get('safety_reason')})")
        if item.get("command"):
            lines.append(f"  - Command: `{item.get('command')}`")
        if item.get("output_excerpt"):
            excerpt = item["output_excerpt"].replace("\n", " | ")
            lines.append(f"  - Output: {excerpt}")
        if item.get("guardrail"):
            lines.append(f"  - Guardrail: {item.get('guardrail')}")
    lines.extend([
        "",
        "## Guardrails",
        "- This preview does not approve, post, publish, push secrets, log URLs, import metrics, or refresh admin state.",
        "- Missing values and blocked platform setup are reported as input_missing, not repaired automatically.",
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
    html = replace_json_embed(html, "embedded-human-handoff-resolution-preview", payload)
    html = replace_text_embed(html, "embedded-human-handoff-resolution-preview-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    payload = build_payload()
    markdown = build_markdown(payload)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(payload, markdown)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), "previews": len(payload["previews"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
