#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLOCKER_LEDGER = ROOT / "data" / "promotion_blocker_ledger.json"
HUMAN_HANDOFF = ROOT / "data" / "human_handoff_packet.json"
HANDOFF_PREVIEW = ROOT / "data" / "human_handoff_resolution_preview.json"
PROMO_STATUS = ROOT / "data" / "promo_engine_status.json"
OUT = ROOT / "data" / "promo_unlock_sequence.json"
REPORT = ROOT / "admin" / "reports" / "promo-unlock-sequence.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def by_id(rows: list[dict], key: str) -> dict:
    return {row.get(key): row for row in rows if row.get(key)}


def previews_for_roadmap(roadmap: dict, previews: dict) -> list[dict]:
    step_id = roadmap.get("id") or ""
    if step_id == "unlock-checked-scheduled-approval":
        return [previews.get("approve-checked-scheduled-batch") or {}]
    if step_id == "unlock-manual-distribution":
        return [row for key, row in previews.items() if str(key).startswith("manual-distribution-")]
    if step_id == "unlock-tiktok-platform-repair":
        return [previews.get("platform-setup-FP-AUTO-264") or {}]
    if step_id == "unlock-backlog-reschedule":
        return [previews.get("backlog-reschedule") or {}]
    if step_id == "unlock-manual-metrics":
        return [row for key, row in previews.items() if str(key).startswith("manual-metrics-")]
    return [previews.get(step_id) or {}]


def aggregate_preview_status(preview_rows: list[dict]) -> str:
    statuses = [row.get("preview_status") for row in preview_rows if row.get("preview_status")]
    if not statuses:
        return ""
    if any(status == "input_missing" for status in statuses):
        return "input_missing"
    if any(status == "preview_ok_with_warning" for status in statuses):
        return "preview_ok_with_warning"
    if all(status == "preview_ok" for status in statuses):
        return "preview_ok"
    return statuses[0]


def joined_unique(values: list[str]) -> str:
    seen = []
    for value in values:
        if value and value not in seen:
            seen.append(value)
    return " ".join(seen)


def gate_state(roadmap: dict, preview_rows: list[dict]) -> str:
    preview_status = aggregate_preview_status(preview_rows)
    roadmap_status = roadmap.get("status") or ""
    if roadmap_status in {"completed", "clear"}:
        return roadmap_status
    if preview_status == "preview_ok":
        return "ready_for_human_review"
    if preview_status == "preview_ok_with_warning":
        return "preview_ready_with_blocker_warning"
    if preview_status == "input_missing":
        return "blocked_until_input"
    if roadmap_status.startswith("blocked"):
        return "blocked"
    return roadmap_status or "waiting"


def gate_reason(roadmap: dict, preview_rows: list[dict]) -> str:
    preview_status = aggregate_preview_status(preview_rows)
    roadmap_status = roadmap.get("status") or ""
    if roadmap_status == "completed":
        return "This gate is already applied; it is kept here as evidence, not as a pending task."
    if roadmap_status == "clear":
        return "No action is needed for this gate."
    if preview_status == "input_missing":
        missing = joined_unique([row.get("input_needed") or "" for row in preview_rows if row.get("preview_status") == "input_missing"])
        return missing or "Input is missing before this gate can advance."
    if preview_status == "preview_ok_with_warning":
        return "Preview ran, but the output still names a known blocker."
    if preview_status == "preview_ok":
        return "Preview ran cleanly; this gate is waiting for human review or external completion."
    blocked_by = roadmap.get("blocked_by") or []
    if blocked_by:
        return f"Blocked by: {', '.join(blocked_by)}."
    return roadmap.get("status") or "Waiting for operator action."


def command_sequence(roadmap: dict, preview_rows: list[dict]) -> list[dict]:
    commands = []
    preview_command = preview_rows[0].get("command") if preview_rows else ""
    if roadmap.get("preview_command") or preview_command:
        preview_status = aggregate_preview_status(preview_rows)
        preview_returncodes = [row.get("returncode") for row in preview_rows if row.get("returncode") is not None]
        commands.append({
            "step": "preview",
            "command": roadmap.get("preview_command") or preview_command or "",
            "safe_to_run": True,
            "status": preview_status or "not_previewed",
            "returncodes": preview_returncodes,
        })
    if roadmap.get("apply_command"):
        commands.append({
            "step": "apply_after_review",
            "command": roadmap.get("apply_command") or "",
            "safe_to_run": False,
            "requires": "Human review, required input, or external platform repair must be complete first.",
        })
    return commands


def build_payload() -> dict:
    ledger = read_json(BLOCKER_LEDGER, {})
    handoff = read_json(HUMAN_HANDOFF, {})
    preview = read_json(HANDOFF_PREVIEW, {})
    status = read_json(PROMO_STATUS, {})
    roadmap = ((ledger.get("summary") or {}).get("blocker_unlock_roadmap") or [])
    previews = by_id(preview.get("previews") or [], "task_id")
    handoff_tasks = by_id(handoff.get("tasks") or [], "id")
    steps = []
    for index, item in enumerate(roadmap, 1):
        preview_rows = previews_for_roadmap(item, previews)
        task = handoff_tasks.get(item.get("id")) or {}
        state = gate_state(item, preview_rows)
        steps.append({
            "order": index,
            "id": item.get("id") or "",
            "phase": item.get("phase") or task.get("phase") or "",
            "owner": item.get("owner") or task.get("owner") or "",
            "gate_state": state,
            "reason": gate_reason(item, preview_rows),
            "blockers_resolved": int(item.get("blockers_resolved") or 0),
            "blocked_by": item.get("blocked_by") or [],
            "unlocks": item.get("unlocks") or [],
            "source_path": item.get("source_path") or task.get("source_path") or "",
            "preview_status": aggregate_preview_status(preview_rows),
            "preview_task_ids": [row.get("task_id") for row in preview_rows if row.get("task_id")],
            "input_needed": joined_unique([row.get("input_needed") or "" for row in preview_rows]),
            "completion_evidence": joined_unique([row.get("completion_evidence") or "" for row in preview_rows]),
            "guardrail": item.get("guardrail") or task.get("guardrail") or joined_unique([row.get("guardrail") or "" for row in preview_rows]),
            "commands": command_sequence(item, preview_rows),
            "next_after_apply": (task.get("impact") or {}).get("next_step_after_apply") or "",
        })

    ready = [step for step in steps if step.get("gate_state") == "ready_for_human_review"]
    blocked = [step for step in steps if step.get("gate_state") in {"blocked", "blocked_until_input", "preview_ready_with_blocker_warning"}]
    current = ready[0] if ready else (blocked[0] if blocked else (steps[0] if steps else {}))
    summary = {
        "step_count": len(steps),
        "ready_for_human_review_count": len(ready),
        "blocked_or_warning_count": len(blocked),
        "total_projected_resolution_units": sum(int(step.get("blockers_resolved") or 0) for step in steps),
        "current_step_id": current.get("id") or "",
        "current_gate_state": current.get("gate_state") or "",
        "open_blocker_count": int(((ledger.get("summary") or {}).get("open_blocker_count")) or 0),
    }
    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "summary": summary,
        "operator_contract": {
            "review_only": True,
            "does_not_apply": True,
            "does_not_post": True,
            "does_not_push_secrets": True,
            "does_not_import_metrics": True,
            "rule": "Run preview commands first; run apply commands only after the named human, platform, URL, secret, or metric input is complete.",
        },
        "current_next_actions": status.get("next_actions") or [],
        "steps": steps,
        "source": {
            "promotion_blocker_ledger": str(BLOCKER_LEDGER.relative_to(ROOT)),
            "human_handoff_packet": str(HUMAN_HANDOFF.relative_to(ROOT)),
            "human_handoff_resolution_preview": str(HANDOFF_PREVIEW.relative_to(ROOT)),
            "promo_engine_status": str(PROMO_STATUS.relative_to(ROOT)),
        },
    }


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Promo Unlock Sequence - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Steps: **{summary['step_count']}**",
        f"- Ready for human review: **{summary['ready_for_human_review_count']}**",
        f"- Blocked or warning: **{summary['blocked_or_warning_count']}**",
        f"- Projected resolution units across sequence: **{summary['total_projected_resolution_units']}**",
        f"- Current step: `{summary['current_step_id']}` (`{summary['current_gate_state']}`)",
        f"- Open blockers still tracked: **{summary['open_blocker_count']}**",
        "",
        "## Sequence",
    ]
    for step in payload["steps"]:
        lines.append(f"{step['order']}. **{step['phase']}** - `{step['id']}`")
        lines.append(f"   - State: `{step['gate_state']}`; owner: `{step['owner']}`")
        lines.append(f"   - Reason: {step['reason']}")
        if step.get("unlocks"):
            lines.append(f"   - Unlocks: {'; '.join(step['unlocks'])}")
        for command in step.get("commands") or []:
            safety = "preview-safe" if command.get("safe_to_run") else "after-review only"
            lines.append(f"   - {command['step']} ({safety}): `{command['command']}`")
        if step.get("completion_evidence"):
            lines.append(f"   - Completion evidence: {step['completion_evidence']}")
        if step.get("guardrail"):
            lines.append(f"   - Guardrail: {step['guardrail']}")
    lines.extend([
        "",
        "## Guardrails",
        "- This sequence does not approve, post, publish, push secrets, log URLs, import metrics, or mutate promotion state.",
        "- Apply commands are shown only as after-review instructions; preview commands remain the safe first action.",
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
    html = replace_json_embed(html, "embedded-promo-unlock-sequence", payload)
    html = replace_text_embed(html, "embedded-promo-unlock-sequence-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    payload = build_payload()
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(payload)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(payload, markdown)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), **payload["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
