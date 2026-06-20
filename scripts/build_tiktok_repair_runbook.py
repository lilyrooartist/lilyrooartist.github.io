#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "data" / "tiktok_setup_preflight.json"
PLATFORM_REPAIR = ROOT / "data" / "platform_repair_status.json"
READINESS = ROOT / "data" / "executor_readiness_snapshot.json"
BACKLOG_RESCHEDULE = ROOT / "data" / "backlog_reschedule_preview.json"
WRANGLER_CONFIG = ROOT / "workers" / "social-executor" / "wrangler.jsonc"
OUT = ROOT / "data" / "tiktok_repair_runbook.json"
REPORT = ROOT / "admin" / "reports" / "tiktok-repair-runbook.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"

REQUIRED_SECRETS = ["TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REFRESH_TOKEN"]


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


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


def runbook_step(step_id: str, phase: str, status: str, title: str, detail: str, command: str = "", blocked_by=None) -> dict:
    return {
        "id": step_id,
        "phase": phase,
        "status": status,
        "title": title,
        "detail": detail,
        "command": command,
        "blocked_by": blocked_by or [],
    }


def build_payload() -> dict:
    preflight = read_json(PREFLIGHT, {})
    repair = read_json(PLATFORM_REPAIR, {})
    readiness = read_json(READINESS, {})
    backlog = read_json(BACKLOG_RESCHEDULE, {})
    preflight_summary = preflight.get("summary") or {}
    credential_handoff = preflight.get("credential_handoff") or {}
    api_strategy = preflight.get("api_strategy") or {}
    posting_mode = preflight_summary.get("posting_mode") or api_strategy.get("posting_mode") or "api"
    backlog_summary = backlog.get("summary") or {}
    local_missing = preflight_summary.get("local_missing_secrets") or []
    worker_missing = preflight_summary.get("worker_missing_secrets") or []
    public_posting = preflight_summary.get("public_posting_approved")
    push_preview = preflight_summary.get("push_preview_command") or "python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN"
    push_apply = preflight_summary.get("push_apply_command") or ""
    repair_rows = [
        row for row in repair.get("rows") or []
        if str(row.get("platform") or "").lower() == "tiktok"
    ]
    repair_row = repair_rows[0] if repair_rows else {}
    local_ready = not local_missing
    public_ready = public_posting is True
    worker_ready = not worker_missing
    apply_ready = local_ready and public_ready
    verify_ready = worker_ready and public_ready
    backlog_preview = backlog_summary.get("preview_command") or "python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-21T10:00:00+09:00' --spacing-hours 24"
    backlog_apply = backlog_summary.get("apply_command") or ""
    blocked_ids: list[str] = []
    steps = [
        runbook_step(
            "collect_local_oauth_credentials",
            "Collect credentials",
            "pass" if local_ready else "blocked",
            "Add TikTok OAuth credentials locally",
            "Use the redacted TikTok handoff template to populate the local social API env file with the required TikTok refresh credential names. Values stay local and are never written to generated reports.",
            "",
            local_missing,
        ),
        runbook_step(
            "confirm_public_posting_approval",
            "Confirm approval",
            "pass" if public_ready else "blocked",
            "Confirm public posting approval",
            "Set TikTok public posting approval only after Lily Roo is approved for public TikTok posting and PUBLIC_TO_EVERYONE is intentionally allowed.",
            "",
            [] if public_ready else ["TIKTOK_PUBLIC_POSTING_APPROVED"],
        ),
        runbook_step(
            "preview_worker_secret_push",
            "Preview push",
            "ready" if local_ready else "blocked",
            "Dry-run worker secret push",
            "Preview the exact secret names that would be pushed to the worker before any apply command is available.",
            push_preview,
            local_missing,
        ),
        runbook_step(
            "apply_worker_secret_push",
            "Apply push",
            "ready" if apply_ready else "blocked",
            "Push worker secrets after review",
            "Run the apply command only after local credentials exist and public posting approval is confirmed.",
            push_apply if apply_ready else "",
            ([] if apply_ready else local_missing + ([] if public_ready else ["TIKTOK_PUBLIC_POSTING_APPROVED"])),
        ),
        runbook_step(
            "recapture_readiness",
            "Verify repair",
            "waiting" if apply_ready else "blocked",
            "Recapture executor readiness",
            "After applying secrets, recapture worker readiness and rebuild the admin packets so platform repair, blocker, handoff, and backlog state agree.",
            "python3 scripts/capture_executor_readiness.py && python3 scripts/refresh_promo_admin.py" if apply_ready else "python3 scripts/refresh_promo_admin.py",
            [] if apply_ready else ["apply_worker_secret_push"],
        ),
        runbook_step(
            "clear_backlog_gate",
            "Clear gate",
            "ready" if verify_ready else "blocked",
            "Clear TikTok backlog gate",
            "Once readiness is clean, rerun the backlog reschedule preview and apply the approved row only if the gate reports safe apply available.",
            f"python3 scripts/build_backlog_reschedule_preview.py && {backlog_preview}" if verify_ready else "",
            [] if verify_ready else ["worker_refresh_credentials", "public_posting_approval"],
        ),
    ]
    for step in steps:
        if step["status"] == "blocked":
            blocked_ids.append(step["id"])
    status = "ready_for_apply" if apply_ready else "blocked"
    if verify_ready:
        status = "ready_for_backlog_clearance"
    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "status": status,
        "source": {
            "tiktok_setup_preflight": str(PREFLIGHT.relative_to(ROOT)),
            "platform_repair_status": str(PLATFORM_REPAIR.relative_to(ROOT)),
            "executor_readiness": str(READINESS.relative_to(ROOT)),
            "backlog_reschedule_preview": str(BACKLOG_RESCHEDULE.relative_to(ROOT)),
            "wrangler_config": str(WRANGLER_CONFIG.relative_to(ROOT)),
        },
        "summary": {
            "posting_mode": posting_mode,
            "api_strategy_confirmed": posting_mode == "api",
            "phase_count": len({step["phase"] for step in steps}),
            "step_count": len(steps),
            "blocked_step_count": len(blocked_ids),
            "blocked_step_ids": blocked_ids,
            "required_secret_names": REQUIRED_SECRETS,
            "handoff_template_path": credential_handoff.get("handoff_template_path") or "",
            "local_missing_secrets": local_missing,
            "worker_missing_secrets": worker_missing,
            "public_posting_approved": public_posting,
            "ready_to_apply_worker_secrets": apply_ready,
            "ready_to_clear_backlog_gate": verify_ready,
            "repair_row_count": len(repair_rows),
            "repair_post_id": repair_row.get("post_id") or "",
            "blocked_apply_command": "" if apply_ready else "python3 scripts/push_social_worker_secrets.py TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN && python3 scripts/refresh_promo_admin.py",
            "apply_command": push_apply if apply_ready else "",
            "backlog_preview_command": backlog_preview,
            "backlog_apply_command": backlog_apply,
            "backlog_normal_apply_gate": backlog_summary.get("normal_apply_gate") or "unknown",
        },
        "steps": steps,
        "redaction": "Secret values are never written to this runbook; only required names, missing names, and presence-derived readiness are recorded.",
        "guardrails": [
            "This runbook does not push secrets, approve public posting, publish posts, or clear backlog rows.",
            "Use the dry-run secret push before any apply command.",
            "Do not run a TikTok backlog apply until fresh admin evidence shows TikTok readiness is clean.",
        ],
    }


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# TikTok Repair Runbook - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Status: **{payload['status']}**",
        f"- Posting mode: **{summary['posting_mode']}**",
        f"- API strategy confirmed: **{summary['api_strategy_confirmed']}**",
        f"- Phases: **{summary['phase_count']}**",
        f"- Steps: **{summary['step_count']}**",
        f"- Blocked steps: **{summary['blocked_step_count']}**",
        f"- Public posting approved: **{summary['public_posting_approved']}**",
        f"- Handoff template: `{summary.get('handoff_template_path') or 'none'}`",
        f"- Ready to apply worker secrets: **{summary['ready_to_apply_worker_secrets']}**",
        f"- Ready to clear backlog gate: **{summary['ready_to_clear_backlog_gate']}**",
        "",
        "## Sequence",
    ]
    for step in payload["steps"]:
        lines.append(f"- **{step['phase']} - {step['title']}**: `{step['status']}`")
        lines.append(f"  - {step['detail']}")
        if step.get("blocked_by"):
            lines.append(f"  - Blocked by: {', '.join(step['blocked_by'])}")
        if step.get("command"):
            lines.append(f"  - Command: `{step['command']}`")
    lines.extend([
        "",
        "## Guardrails",
    ])
    lines.extend(f"- {item}" for item in payload["guardrails"])
    lines.extend([
        f"- {payload['redaction']}",
        "",
    ])
    return "\n".join(lines)


def sync_admin(payload: dict, markdown: str) -> None:
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    html = replace_json_embed(html, "embedded-tiktok-repair-runbook", payload)
    html = replace_text_embed(html, "embedded-tiktok-repair-runbook-report", markdown)
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
