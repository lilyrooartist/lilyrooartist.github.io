#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
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
BRAND_GROWTH_READOUT = ROOT / "data" / "brand_growth_readout.json"
BRAND_GROWTH_PREFLIGHT = ROOT / "data" / "brand_growth_preflight.json"
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


def parse_iso(value: str | None):
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
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def fixed_daily_cron(cron: str):
    match = re.fullmatch(r"\s*(\d{1,2})\s+(\d{1,2})\s+\*\s+\*\s+\*\s*", cron or "")
    if not match:
        return None
    minute = int(match.group(1))
    hour = int(match.group(2))
    if minute > 59 or hour > 23:
        return None
    return hour, minute


def proof_refresh_alignment(crons: list[str], proof_due_at: str) -> dict:
    due = parse_iso(proof_due_at)
    if not due:
        return {
            "status": "unknown",
            "proof_due_at": proof_due_at or "",
            "next_refresh_at": "",
            "lag_minutes": None,
            "cron": "",
            "detail": "No proof due time is available yet.",
        }
    candidates = []
    for cron in crons:
        fixed = fixed_daily_cron(cron)
        if not fixed:
            continue
        hour, minute = fixed
        candidate = due.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if candidate < due:
            candidate += timedelta(days=1)
        candidates.append((candidate, cron))
    if not candidates:
        return {
            "status": "unknown",
            "proof_due_at": due.isoformat().replace("+00:00", "Z"),
            "next_refresh_at": "",
            "lag_minutes": None,
            "cron": "",
            "detail": "No fixed daily proof-refresh cron was found.",
        }
    refresh_at, cron = min(candidates, key=lambda item: item[0])
    lag_minutes = int(round((refresh_at - due).total_seconds() / 60))
    status = "ready" if 0 <= lag_minutes <= 15 else "slow"
    return {
        "status": status,
        "proof_due_at": due.isoformat().replace("+00:00", "Z"),
        "next_refresh_at": refresh_at.isoformat().replace("+00:00", "Z"),
        "lag_minutes": lag_minutes,
        "cron": cron,
        "detail": (
            f"next fixed refresh {lag_minutes} minute(s) after proof due"
            if status == "ready"
            else f"next fixed refresh is {lag_minutes} minute(s) after proof due"
        ),
    }


def step_map(refresh: dict) -> dict:
    steps = {}
    for item in refresh.get("steps") or []:
        name = item.get("name")
        if name:
            steps[name] = item
    return steps


def step_stdout_json(step: dict) -> dict:
    raw = str(step.get("stdout_tail") or "").strip()
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def lane_status(label: str, status: str, detail: str, evidence: str = "", next_action: str = "") -> dict:
    return {
        "label": label,
        "status": status,
        "detail": detail,
        "evidence": evidence,
        "next_action": next_action,
    }


def campaign_packet(readout: dict, preflight: dict) -> dict:
    readout_summary = readout.get("summary") or {}
    preflight_summary = preflight.get("summary") or {}
    expected_ids = preflight_summary.get("expected_post_ids") or readout_summary.get("next_proof_post_ids") or []
    status = "ready" if (
        preflight_summary.get("status") == "ready"
        and int(preflight_summary.get("scheduler_blocked_count") or 0) == 0
        and int(preflight_summary.get("link_blocking_failed_count") or 0) == 0
        and int(readout_summary.get("approved_auto_rows") or 0) > 0
    ) else "needs_attention"
    next_proof = (
        preflight_summary.get("scheduled_time")
        if status == "ready"
        else preflight_summary.get("next_proof_due_at") or readout_summary.get("next_proof_due_at") or ""
    )
    next_action = (
        f"Watch {', '.join(expected_ids)} after {next_proof}, then export posted URLs."
        if status == "ready" and expected_ids and next_proof
        else preflight_summary.get("error") or readout_summary.get("next_actions", ["Refresh brand growth readout and preflight."])[0]
    )
    return {
        "status": status,
        "platforms": sorted((readout_summary.get("active_platform_counts") or readout_summary.get("platform_counts") or {}).keys()),
        "detail": (
            f"{int(readout_summary.get('approved_auto_rows') or 0)} approved auto posts; "
            f"next={readout_summary.get('next_scheduled_post_id') or 'none'} at "
            f"{readout_summary.get('next_scheduled_at') or 'n/a'}; "
            f"preflight={preflight_summary.get('status') or 'unknown'}"
        ),
        "next_action": next_action,
        "next_proof_due_at": next_proof,
        "next_measurement_due_at": preflight_summary.get("next_measurement_due_at") or readout_summary.get("next_measurement_due_at") or "",
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
    brand_readout = read_json(BRAND_GROWTH_READOUT)
    brand_preflight = read_json(BRAND_GROWTH_PREFLIGHT)
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
    campaign = campaign_packet(brand_readout, brand_preflight)
    proof_refresh = proof_refresh_alignment(workflow["crons"], campaign.get("next_proof_due_at") or "")
    active_campaign_ready = campaign["status"] == "ready"
    proof_refresh_ready = (not active_campaign_ready) or proof_refresh.get("status") == "ready"
    export_step = refresh_steps.get("export_social_executions") or {}
    export_payload = step_stdout_json(export_step)
    export_step_command = str(export_step.get("command") or "")
    proof_export_ready = bool(
        active_campaign_ready
        and proof_refresh_ready
        and export_step.get("ok") is True
        and "export_social_executions.py" in export_step_command
        and "--dry-run" not in export_step_command
        and export_payload.get("dry_run") is False
        and export_payload.get("ok") is True
    )
    proof_export_next_action = (
        f"Automatic proof/export is scheduled at {proof_refresh.get('next_refresh_at')}; "
        f"verify {', '.join(campaign.get('expected_post_ids') or []) or 'the active posts'} in Published_Log after that run."
        if proof_export_ready
        else campaign["next_action"]
    )
    active_platforms = {str(platform).strip().lower() for platform in campaign.get("platforms") or []}
    blocked_platforms = [str(platform) for platform in readiness_summary.get("blocked_platforms") or []]
    blocked_platforms_in_active_campaign = [
        platform for platform in blocked_platforms
        if platform.strip().lower() in active_platforms
    ]
    optional_platform_status = "blocked" if blocked_platforms_in_active_campaign else "deferred"
    input_status = input_summary.get("status")
    blocker_input_lane_status = "ready" if input_status == "ready" else ("deferred" if active_campaign_ready else "blocked")

    lanes = [
        lane_status(
            "Active Analog Myth brand campaign",
            "ready" if active_campaign_ready else "needs_attention",
            campaign["detail"],
            "data/brand_growth_preflight.json",
            proof_export_next_action,
        ),
        lane_status(
            "Scheduled refresh workflow",
            "ready" if workflow_ready and workflow_ok and proof_refresh_ready else "needs_attention",
            f"{', '.join(workflow['crons']) or 'no cron'}; latest run {workflow_latest.get('status') or 'unknown'} / {workflow_latest.get('conclusion') or 'pending'}; proof refresh {proof_refresh.get('detail')}",
            workflow_latest.get("html_url") or workflow_status.get("actions_url") or "",
            (
                ""
                if workflow_ready and workflow_ok and proof_refresh_ready
                else "Add or repair a fixed daily refresh cron within 15 minutes after the active campaign proof window."
            ),
        ),
        lane_status(
            "Published URL export",
            "ready" if proof_export_ready else "needs_attention",
            f"safe refresh runs {export_step_command or 'missing export step'}; latest export added={export_payload.get('added', 'unknown')} dry_run={export_payload.get('dry_run', 'unknown')}; next proof refresh={proof_refresh.get('next_refresh_at') or 'n/a'}",
            "data/promo_admin_refresh_run.json",
            "" if proof_export_ready else "Ensure refresh_promo_admin.py runs export_social_executions.py without --dry-run during the scheduled proof refresh.",
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
            optional_platform_status if blocked_platforms else "ready",
            f"ready={', '.join(readiness_summary.get('ready_platforms') or []) or 'none'}; blocked={', '.join(readiness_summary.get('blocked_platforms') or []) or 'none'}",
            "data/executor_readiness_snapshot.json",
            (
                "Repair the active campaign platform before the next scheduled slot."
                if blocked_platforms_in_active_campaign
                else "Optional expansion only; unsupported platforms stay inactive until their automated lane is ready."
            ) if blocked_platforms else "",
        ),
        lane_status(
            "TikTok API lane",
            "ready" if tiktok_summary.get("ready_to_post_publicly") else ("deferred" if active_campaign_ready else "blocked"),
            f"{tiktok_summary.get('status') or 'unknown'}; upload_ready={bool(tiktok_summary.get('ready_to_upload_drafts'))}; public_ready={bool(tiktok_summary.get('ready_to_post_publicly'))}",
            "data/tiktok_setup_preflight.json",
            (
                "Direct TikTok public posting is not in the active plan until platform approval is explicit; upload-draft/manual-finish posting is excluded."
                if not tiktok_summary.get("ready_to_post_publicly")
                else ""
            ),
        ),
        lane_status(
            "Blocker input readiness",
            blocker_input_lane_status,
            f"{input_summary.get('ready_count', 0)} ready; {input_summary.get('missing_local_input_count', 0)} missing local input; {input_summary.get('external_action_needed_count', 0)} external action needed",
            "data/social_blocker_input_status.json",
            (
                "Optional expansion inputs can wait; the active brand campaign is already preflight-ready."
                if blocker_input_lane_status == "deferred"
                else input_summary.get("next_action") or "Fill missing local inputs, then rerun the verification commands."
            ),
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
    deferred = [lane for lane in lanes if lane["status"] == "deferred"]
    ready = [lane for lane in lanes if lane["status"] == "ready"]
    help_needed = []
    if not scheduler_ok:
        help_needed.append({
            "label": "Scheduler and executor auth",
            "need": "Confirm LILYROO_EXECUTOR_BEARER_TOKEN or LILYROO_ADMIN_PASSWORD is available locally and as a GitHub Actions secret.",
            "unblocks": "Scheduler dry-run, executor readiness capture, and execution history capture.",
            "verification_command": "python3 scripts/capture_scheduler_dry_run.py && python3 scripts/capture_social_executions.py",
        })
    optional_inputs = [
        {
            "label": "Instagram business account ID",
            "need": "Provide Meta Page credentials so the resolver can write IG_BUSINESS_ACCOUNT_ID for the Instagram account connected to the Lily Roo Facebook Page.",
            "unblocks": "Optional automated Instagram expansion after the secret is pushed and readiness is recaptured.",
            "verification_command": "python3 scripts/check_social_executor_dry_run.py --post-id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM",
        },
        {
            "label": "TikTok public-posting approval",
            "need": "Confirm whether TikTok has approved direct public posting for Lily Roo.",
            "unblocks": "Optional direct public TikTok posting; inbox-draft upload is not part of the active no-manual-posting plan.",
            "verification_command": "python3 scripts/set_tiktok_public_posting_approval.py --approved",
        },
    ]
    next_action = ""
    if active_campaign_ready:
        next_action = proof_export_next_action
    elif blocked:
        next_action = blocked[0]["next_action"] or blocked[0]["detail"]
    elif attention:
        next_action = attention[0]["next_action"] or attention[0]["detail"]
    else:
        next_action = "Monitor scheduled posts and import results after their measurement windows."

    capture_step = refresh_steps.get("capture_scheduler_dry_run") or {}
    summary = {
        "status": "ready_active_campaign" if active_campaign_ready and not blocked else "blocked" if blocked else "needs_attention" if attention else "ready",
        "active_campaign_ready": active_campaign_ready,
        "active_campaign_platforms": campaign.get("platforms") or [],
        "active_campaign_next_proof_due_at": campaign.get("next_proof_due_at") or "",
        "active_campaign_next_measurement_due_at": campaign.get("next_measurement_due_at") or "",
        "ready_lane_count": len(ready),
        "blocked_lane_count": len(blocked),
        "deferred_lane_count": len(deferred),
        "attention_lane_count": len(attention),
        "lane_count": len(lanes),
        "workflow_crons": workflow["crons"],
        "active_campaign_proof_refresh_status": proof_refresh.get("status"),
        "active_campaign_next_proof_refresh_at": proof_refresh.get("next_refresh_at"),
        "active_campaign_proof_refresh_lag_minutes": proof_refresh.get("lag_minutes"),
        "active_campaign_proof_refresh_cron": proof_refresh.get("cron"),
        "active_campaign_proof_export_status": "ready" if proof_export_ready else "needs_attention",
        "active_campaign_proof_export_mode": "scheduled_refresh",
        "active_campaign_proof_export_command": "python3 scripts/refresh_promo_admin.py",
        "active_campaign_proof_export_step_command": export_step_command,
        "active_campaign_proof_export_added_last_run": export_payload.get("added"),
        "active_campaign_proof_export_dry_run_last_run": export_payload.get("dry_run"),
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
            "brand_growth_readout": str(BRAND_GROWTH_READOUT.relative_to(ROOT)),
            "brand_growth_preflight": str(BRAND_GROWTH_PREFLIGHT.relative_to(ROOT)),
        },
        "summary": summary,
        "proof_refresh": proof_refresh,
        "lanes": lanes,
        "help_needed": help_needed,
        "optional_inputs": optional_inputs,
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
        f"- Active campaign ready: **{summary['active_campaign_ready']}**",
        f"- Lanes ready: **{summary['ready_lane_count']} / {summary['lane_count']}**",
        f"- Blocked lanes: **{summary['blocked_lane_count']}**",
        f"- Deferred optional lanes: **{summary['deferred_lane_count']}**",
        f"- Needs attention: **{summary['attention_lane_count']}**",
        f"- Story posts tracked: **{summary['story_post_count']}**",
        f"- Help-needed items: **{summary['help_needed_count']}**",
        f"- Proof refresh: **{summary.get('active_campaign_proof_refresh_status') or 'unknown'}** at `{summary.get('active_campaign_next_proof_refresh_at') or 'n/a'}` ({summary.get('active_campaign_proof_refresh_lag_minutes')} min)",
        f"- Proof export: **{summary.get('active_campaign_proof_export_status') or 'unknown'}** via `{summary.get('active_campaign_proof_export_step_command') or 'n/a'}`",
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
    if not packet.get("help_needed"):
        lines.append("- No active campaign help needed.")
    lines.append("")
    lines.append("## Optional Expansion Inputs")
    for item in packet.get("optional_inputs") or []:
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
