#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "promo-admin-refresh.yml"
REFRESH_RUN = ROOT / "data" / "promo_admin_refresh_run.json"
WORKFLOW_STATUS = ROOT / "data" / "promo_refresh_workflow_status.json"
SCHEDULER = ROOT / "data" / "social_scheduler_dry_run.json"
EXECUTIONS = ROOT / "data" / "social_execution_snapshot.json"
READINESS = ROOT / "data" / "executor_readiness_snapshot.json"
TIKTOK_PREFLIGHT = ROOT / "data" / "tiktok_setup_preflight.json"
STORY_TRACKING = ROOT / "data" / "story_throughput_tracking.json"
PLATFORM_REPAIR = ROOT / "data" / "platform_repair_status.json"
SOCIAL_INPUTS = ROOT / "data" / "social_blocker_input_status.json"
OUT = ROOT / "data" / "posting_automation_status.json"
REPORT = ROOT / "admin" / "reports" / "posting-automation-status.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def workflow_config() -> dict:
    text = WORKFLOW.read_text(encoding="utf-8") if WORKFLOW.exists() else ""
    crons = re.findall(r'cron:\s*["\']([^"\']+)["\']', text)
    return {
        "path": str(WORKFLOW.relative_to(ROOT)),
        "exists": WORKFLOW.exists(),
        "scheduled": bool(crons),
        "crons": crons,
        "manual_dispatch": "workflow_dispatch:" in text,
        "refresh_command_present": "python3 scripts/refresh_promo_admin.py" in text,
        "validate_command_present": "python3 scripts/validate_content_system.py" in text,
        "commits_refreshed_data": "git commit -m \"Refresh promo admin snapshots\"" in text,
    }


def step_map(refresh: dict) -> dict:
    steps = {}
    for item in refresh.get("steps") or []:
        name = item.get("name")
        if name:
            steps[name] = item
    return steps


def lane_status(label: str, status: str, detail: str, evidence: str = "", next_action: str = "") -> dict:
    return {
        "label": label,
        "status": status,
        "detail": detail,
        "evidence": evidence,
        "next_action": next_action,
    }


def build_packet() -> dict:
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    workflow = workflow_config()
    refresh = read_json(REFRESH_RUN)
    workflow_status = read_json(WORKFLOW_STATUS)
    scheduler = read_json(SCHEDULER)
    executions = read_json(EXECUTIONS)
    readiness = read_json(READINESS)
    tiktok = read_json(TIKTOK_PREFLIGHT)
    stories = read_json(STORY_TRACKING)
    repairs = read_json(PLATFORM_REPAIR)
    social_inputs = read_json(SOCIAL_INPUTS)
    refresh_steps = step_map(refresh)

    workflow_latest = workflow_status.get("latest_run") or {}
    workflow_ready = workflow["scheduled"] and workflow["manual_dispatch"] and workflow["refresh_command_present"]
    workflow_ok = bool(workflow_status.get("ok")) and workflow_latest.get("conclusion") in {"success", ""} and workflow_latest.get("status") in {"completed", "in_progress"}

    scheduler_ok = bool(scheduler.get("ok"))
    scheduler_summary = scheduler.get("summary") or {}
    execution_ok = bool(executions.get("ok"))
    execution_summary = executions.get("summary") or {}
    readiness_summary = readiness.get("summary") or {}
    tiktok_summary = tiktok.get("summary") or {}
    story_summary = stories.get("summary") or {}
    repair_summary = repairs.get("summary") or {}
    input_summary = social_inputs.get("summary") or {}
    refresh_summary = refresh.get("summary") or {}

    lanes = [
        lane_status(
            "Scheduled refresh workflow",
            "ready" if workflow_ready and workflow_ok else "needs_attention",
            f"{', '.join(workflow['crons']) or 'no cron'}; latest run {workflow_latest.get('status') or 'unknown'} / {workflow_latest.get('conclusion') or 'pending'}",
            workflow_latest.get("html_url") or workflow_status.get("actions_url") or "",
            "" if workflow_ready and workflow_ok else "Confirm the GitHub Actions workflow is enabled and has a successful run.",
        ),
        lane_status(
            "Safe admin refresh",
            "ready" if refresh.get("ok") else "needs_attention",
            f"{refresh_summary.get('command_count', len(refresh.get('steps') or []))} refresh commands captured at {refresh.get('finished_at') or refresh.get('started_at') or refresh.get('updated_at') or 'unknown time'}",
            "data/promo_admin_refresh_run.json",
            "" if refresh.get("ok") else "Run python3 scripts/refresh_promo_admin.py and inspect failed required steps.",
        ),
        lane_status(
            "Scheduler dry-run authentication",
            "ready" if scheduler_ok else "blocked",
            f"HTTP {scheduler.get('http_status', 'unknown')} using {scheduler.get('auth_method') or 'unknown'} auth; due={scheduler_summary.get('due_count', 0)} would_post={scheduler_summary.get('would_post_count', 0)}",
            "data/social_scheduler_dry_run.json",
            scheduler.get("action_needed") or "",
        ),
        lane_status(
            "Execution capture",
            "ready" if execution_ok else "blocked",
            f"posted={execution_summary.get('posted_count', 0)} attention={execution_summary.get('attention_count', 0)} platform_fix_needed={execution_summary.get('platform_fix_needed_count', 0)}",
            "data/social_execution_snapshot.json",
            executions.get("action_needed") or "",
        ),
        lane_status(
            "Platform readiness",
            "blocked" if readiness_summary.get("blocked_platforms") else "ready",
            f"ready={', '.join(readiness_summary.get('ready_platforms') or []) or 'none'}; blocked={', '.join(readiness_summary.get('blocked_platforms') or []) or 'none'}",
            "data/executor_readiness_snapshot.json",
            "Resolve the platform repair checklist before expecting full auto-post coverage." if readiness_summary.get("blocked_platforms") else "",
        ),
        lane_status(
            "TikTok API lane",
            "blocked" if not tiktok_summary.get("ready_to_upload_drafts") else "ready",
            f"{tiktok_summary.get('status') or 'unknown'}; upload_ready={bool(tiktok_summary.get('ready_to_upload_drafts'))}; public_ready={bool(tiktok_summary.get('ready_to_post_publicly'))}",
            "data/tiktok_setup_preflight.json",
            "Add TikTok OAuth credentials and rerun the upload-mode dry run." if not tiktok_summary.get("ready_to_upload_drafts") else "",
        ),
        lane_status(
            "Blocker input readiness",
            "ready" if input_summary.get("status") == "ready" else "blocked",
            f"{input_summary.get('ready_count', 0)} ready; {input_summary.get('missing_local_input_count', 0)} missing local input; {input_summary.get('external_action_needed_count', 0)} external action needed",
            "data/social_blocker_input_status.json",
            input_summary.get("next_action") or "Fill missing local inputs, then rerun the verification commands.",
        ),
        lane_status(
            "Story throughput",
            "ready" if story_summary.get("story_post_count") else "needs_attention",
            f"{story_summary.get('story_post_count', 0)} tracked; {story_summary.get('queued_future_count', 0)} queued; {story_summary.get('past_due_unlogged_count', 0)} past due without URL",
            "data/story_throughput_tracking.json",
            "Export social executions after scheduled post times, then log public URLs and results." if story_summary.get("story_post_count") else "Schedule approved story posts.",
        ),
    ]

    blocked = [lane for lane in lanes if lane["status"] == "blocked"]
    attention = [lane for lane in lanes if lane["status"] == "needs_attention"]
    ready = [lane for lane in lanes if lane["status"] == "ready"]
    help_needed = [
        {
            "label": "Scheduler and executor auth",
            "need": "Confirm LILYROO_EXECUTOR_BEARER_TOKEN or LILYROO_ADMIN_PASSWORD is available locally and as a GitHub Actions secret.",
            "unblocks": "Scheduler dry-run, executor readiness capture, and execution history capture.",
            "verification_command": "python3 scripts/capture_scheduler_dry_run.py && python3 scripts/capture_social_executions.py",
        },
        {
            "label": "Instagram business account ID",
            "need": "Provide IG_BUSINESS_ACCOUNT_ID for the Instagram account connected to the Lily Roo Facebook Page.",
            "unblocks": "Instagram executor rows after the secret is pushed and readiness is recaptured.",
            "verification_command": "python3 scripts/check_social_executor_dry_run.py --post-id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM",
        },
        {
            "label": "TikTok OAuth app values",
            "need": "Provide TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, and TIKTOK_REDIRECT_URI, then authorize the generated TikTok OAuth URL so TIKTOK_REFRESH_TOKEN can be created.",
            "unblocks": "TikTok upload-draft automation for the first ready TikTok asset.",
            "verification_command": "python3 scripts/tiktok_oauth_handoff.py --print-auth-url --posting-mode upload",
        },
        {
            "label": "TikTok public-posting approval",
            "need": "Confirm whether TikTok has approved direct public posting for Lily Roo.",
            "unblocks": "Direct public TikTok posting; without approval, upload-draft mode remains the safest automated path.",
            "verification_command": "python3 scripts/set_tiktok_public_posting_approval.py --approved",
        },
        {
            "label": "Facebook identity confirmation",
            "need": "Confirm identity in Facebook/Meta for Page publishing if Meta still shows the Page publishing checkpoint.",
            "unblocks": "The blocked Facebook executor row that hit the identity confirmation checkpoint.",
            "verification_command": "python3 scripts/check_facebook_publishing.py --post-id 'FP-AUTO-265' --check-worker-dry-run",
        },
    ]
    next_action = ""
    if blocked:
        next_action = blocked[0]["next_action"] or blocked[0]["detail"]
    elif attention:
        next_action = attention[0]["next_action"] or attention[0]["detail"]
    else:
        next_action = "Monitor scheduled posts and import results after their measurement windows."

    capture_step = refresh_steps.get("capture_scheduler_dry_run") or {}
    summary = {
        "status": "blocked" if blocked else "needs_attention" if attention else "ready",
        "ready_lane_count": len(ready),
        "blocked_lane_count": len(blocked),
        "attention_lane_count": len(attention),
        "lane_count": len(lanes),
        "workflow_crons": workflow["crons"],
        "scheduler_http_status": scheduler.get("http_status"),
        "scheduler_auth_method": scheduler.get("auth_method"),
        "scheduler_refresh_step_ok": bool(capture_step.get("ok")),
        "posted_count": execution_summary.get("posted_count", 0),
        "attention_count": execution_summary.get("attention_count", 0),
        "platform_fix_needed_count": execution_summary.get("platform_fix_needed_count", 0),
        "story_post_count": story_summary.get("story_post_count", 0),
        "story_queued_future_count": story_summary.get("queued_future_count", 0),
        "platform_repair_blocked_count": repair_summary.get("blocked_count", 0),
        "blocker_input_status": input_summary.get("status", "unknown"),
        "blocker_input_missing_count": input_summary.get("missing_local_input_count", 0),
        "blocker_input_external_action_count": input_summary.get("external_action_needed_count", 0),
        "help_needed_count": len(help_needed),
        "next_action": next_action,
    }
    return {
        "generated_at": generated_at,
        "safe_mode": True,
        "source": {
            "workflow": str(WORKFLOW.relative_to(ROOT)),
            "refresh_run": str(REFRESH_RUN.relative_to(ROOT)),
            "workflow_status": str(WORKFLOW_STATUS.relative_to(ROOT)),
            "scheduler": str(SCHEDULER.relative_to(ROOT)),
            "executions": str(EXECUTIONS.relative_to(ROOT)),
            "readiness": str(READINESS.relative_to(ROOT)),
            "tiktok_preflight": str(TIKTOK_PREFLIGHT.relative_to(ROOT)),
            "story_tracking": str(STORY_TRACKING.relative_to(ROOT)),
            "platform_repair": str(PLATFORM_REPAIR.relative_to(ROOT)),
            "social_inputs": str(SOCIAL_INPUTS.relative_to(ROOT)),
        },
        "summary": summary,
        "lanes": lanes,
        "help_needed": help_needed,
    }


def build_markdown(packet: dict) -> str:
    summary = packet["summary"]
    lines = [
        "# Posting Automation Status - Lily Roo",
        "",
        f"Generated: {packet['generated_at']}",
        "",
        "## Summary",
        f"- Status: **{summary['status']}**",
        f"- Lanes ready: **{summary['ready_lane_count']} / {summary['lane_count']}**",
        f"- Blocked lanes: **{summary['blocked_lane_count']}**",
        f"- Needs attention: **{summary['attention_lane_count']}**",
        f"- Story posts tracked: **{summary['story_post_count']}**",
        f"- Help-needed items: **{summary['help_needed_count']}**",
        f"- Next action: {summary['next_action']}",
        "",
        "## Automation Lanes",
    ]
    for lane in packet["lanes"]:
        lines.append(f"- **{lane['label']}** - `{lane['status']}`")
        lines.append(f"  - Detail: {lane['detail']}")
        if lane.get("evidence"):
            lines.append(f"  - Evidence: {lane['evidence']}")
        if lane.get("next_action"):
            lines.append(f"  - Next: {lane['next_action']}")
    lines.append("")
    lines.append("## Help Needed")
    for item in packet.get("help_needed") or []:
        lines.append(f"- **{item['label']}**")
        lines.append(f"  - Need: {item['need']}")
        lines.append(f"  - Unblocks: {item['unblocks']}")
        lines.append(f"  - Verify: `{item['verification_command']}`")
    lines.extend([
        "",
        "## Guardrails",
        "- This packet is read-only; it does not publish posts, approve posts, or push secrets.",
        "- A scheduled workflow is not full automation unless scheduler auth, execution capture, platform readiness, and URL/result logging are also healthy.",
        "- TikTok direct public posting remains blocked until credentials and public-posting approval are explicit.",
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


def sync_admin(packet: dict, markdown: str) -> None:
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    html = replace_json_embed(html, "embedded-posting-automation-status", packet)
    html = replace_text_embed(html, "embedded-posting-automation-status-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(packet)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(packet, markdown)
    print(json.dumps({
        "output": str(OUT.relative_to(ROOT)),
        "status": packet["summary"]["status"],
        "ready_lane_count": packet["summary"]["ready_lane_count"],
        "blocked_lane_count": packet["summary"]["blocked_lane_count"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
