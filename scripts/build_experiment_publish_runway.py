#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMO_STATUS = ROOT / "data" / "promo_engine_status.json"
APPROVAL_RUNWAY = ROOT / "data" / "approval_runway.json"
MANUAL_DISTRIBUTION = ROOT / "data" / "manual_distribution_packet.json"
BACKLOG_RESCHEDULE = ROOT / "data" / "backlog_reschedule_preview.json"
PLATFORM_REPAIR = ROOT / "data" / "platform_repair_status.json"
OUT = ROOT / "data" / "experiment_publish_runway.json"
REPORT = ROOT / "admin" / "reports" / "experiment-publish-runway.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def command_for_ids(script: str, ids: list[str], suffix: str) -> str:
    if not ids:
        return ""
    return f"python3 {script} " + " ".join(f"--id {post_id}" for post_id in ids) + f" {suffix}"


def manual_rows(manual_packet: dict) -> tuple[list[dict], list[dict], list[dict]]:
    rows = manual_packet.get("rows") or []
    review_ready = [
        row for row in rows
        if row.get("distribution_status") == "waiting_for_review" and row.get("readiness_state") == "manual_only"
    ]
    postable_now = [
        row for row in rows
        if row.get("manual_posting_packet", {}).get("postable_now") and not row.get("logged")
    ]
    needs_logging = [
        row for row in rows
        if row.get("approved") == "yes" and not row.get("logged")
    ]
    return review_ready, postable_now, needs_logging


def blocked_platform_rows(platform_packet: dict) -> list[dict]:
    rows = []
    for row in platform_packet.get("rows") or []:
        rows.append({
            "post_id": row.get("post_id") or "",
            "platform": row.get("platform") or "",
            "reason": row.get("reason") or "",
            "status": row.get("status") or "",
            "repair_action": row.get("repair_action") or "",
            "preview_command": row.get("preview_command") or "",
            "blocked_apply_reasons": row.get("blocked_apply_reasons") or [],
        })
    return rows


def build_packet() -> dict:
    status = read_json(PROMO_STATUS, {})
    approval = read_json(APPROVAL_RUNWAY, {})
    manual = read_json(MANUAL_DISTRIBUTION, {})
    backlog = read_json(BACKLOG_RESCHEDULE, {})
    platform = read_json(PLATFORM_REPAIR, {})
    growth = ((status.get("kpi") or {}).get("growth_goal") or {})
    readiness = growth.get("format_winner_readiness") or {}
    review_ready, postable_now, needs_logging = manual_rows(manual)
    review_ids = [row.get("id") for row in review_ready if row.get("id")]
    postable_ids = [row.get("id") for row in postable_now if row.get("id")]
    logging_ids = [row.get("id") for row in needs_logging if row.get("id")]
    manual_docket = approval.get("manual_approval_docket") or {}
    blocked_platform = blocked_platform_rows(platform)
    approved_backlog = (backlog.get("summary") or {}).get("approved_backlog_count") or 0
    blocked_backlog = (backlog.get("summary") or {}).get("blocked_backlog_count") or 0
    steps = [
        {
            "id": "review_manual_youtube_community",
            "status": "ready_for_review" if review_ids else "clear",
            "post_ids": review_ids,
            "preview_command": manual_docket.get("preview_command") or command_for_ids("scripts/approve_promo_queue_plan.py", review_ids, "--dry-run"),
            "apply_after_review_command": manual_docket.get("apply_command") or command_for_ids("scripts/approve_promo_queue_plan.py", review_ids, "--refresh-admin"),
            "guardrail": "Manual-only approvals do not auto-post; posting and public URL logging remain separate.",
            "completion_evidence": "data/manual_distribution_packet.json should move rows from waiting_for_review toward postable manual distribution.",
        },
        {
            "id": "queue_approved_manual_rows",
            "status": "ready_after_approval" if review_ids else "waiting_for_approval",
            "post_ids": review_ids,
            "preview_command": command_for_ids("scripts/apply_promo_queue_plan.py", review_ids, ""),
            "apply_after_review_command": command_for_ids("scripts/apply_promo_queue_plan.py", review_ids, "--apply --refresh-admin"),
            "guardrail": "Apply only after the matching promo plan rows have approved=yes.",
            "completion_evidence": "data/scheduled_posts.csv contains the approved manual YouTube Community row ids.",
        },
        {
            "id": "post_manual_youtube_community",
            "status": "postable_now" if postable_ids else "waiting_for_review_or_queue",
            "post_ids": postable_ids or review_ids,
            "surface": "YouTube Studio Community",
            "public_community_url": (manual.get("summary") or {}).get("public_community_url") or "",
            "guardrail": "Post manually using the reviewed copy and local asset evidence; do not log placeholder URLs.",
            "completion_evidence": "A real public YouTube Community URL exists for each posted row.",
        },
        {
            "id": "log_public_urls",
            "status": "ready_after_manual_post" if logging_ids else "waiting_for_public_urls",
            "post_ids": logging_ids or review_ids,
            "preview_command": "python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv",
            "apply_after_review_command": "python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --apply --refresh-admin",
            "guardrail": "Every CSV row must contain a real public_url before apply.",
            "completion_evidence": "admin/content/Published_Log.csv contains real public URLs for the manual community rows.",
        },
        {
            "id": "collect_results",
            "status": "waiting_for_measurement_window",
            "post_ids": review_ids,
            "preview_command": "python3 scripts/update_experiment_results.py --from-csv data/experiment_result_entry_template.csv --dry-run",
            "apply_after_review_command": "",
            "guardrail": "Fill only visible platform analytics values with evidence notes.",
            "completion_evidence": "data/promo_engine_status.json shows fewer pending result fields and more measured posts per candidate format.",
        },
    ]
    packet = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "promo_engine_status": str(PROMO_STATUS.relative_to(ROOT)),
            "approval_runway": str(APPROVAL_RUNWAY.relative_to(ROOT)),
            "manual_distribution_packet": str(MANUAL_DISTRIBUTION.relative_to(ROOT)),
            "backlog_reschedule_preview": str(BACKLOG_RESCHEDULE.relative_to(ROOT)),
            "platform_repair_status": str(PLATFORM_REPAIR.relative_to(ROOT)),
        },
        "summary": {
            "review_ready_manual_count": len(review_ready),
            "postable_now_count": len(postable_now),
            "public_url_log_needed_count": int((manual.get("summary") or {}).get("public_url_log_needed_count") or 0),
            "pending_result_field_count": int(readiness.get("pending_result_field_count") or 0),
            "winner_ready_candidate_count": int(readiness.get("ready_candidate_count") or 0),
            "winner_count_target": int(readiness.get("winner_count_target") or 3),
            "blocked_platform_count": len(blocked_platform),
            "approved_backlog_count": int(approved_backlog or 0),
            "blocked_backlog_count": int(blocked_backlog or 0),
            "next_publish_action": "Review and approve manual YouTube Community experiment rows." if review_ids else "Log public URLs and collect experiment results.",
        },
        "manual_review_rows": [
            {
                "id": row.get("id") or "",
                "release": row.get("release") or "",
                "platform": row.get("platform") or "",
                "scheduled_at": row.get("scheduled_at") or "",
                "copy_block": row.get("copy_block") or "",
                "asset_download_url": row.get("asset_download_url") or "",
                "destination_links": row.get("destination_links") or [],
                "approval_preview_command": row.get("approval_preview_command") or "",
                "approval_command": row.get("approval_command") or "",
                "log_preview_command": row.get("log_preview_command") or "",
            }
            for row in review_ready
        ],
        "blocked_platform_rows": blocked_platform,
        "steps": steps,
        "guardrails": [
            "Review-only packet; it does not approve, schedule, post, or log URLs.",
            "Manual YouTube Community rows must be reviewed before approval.",
            "TikTok stays blocked until OAuth credentials and public-posting approval are present.",
            "Do not declare winning formats until the winner-readiness gate is satisfied.",
        ],
    }
    return packet


def build_markdown(packet: dict) -> str:
    summary = packet["summary"]
    lines = [
        "# Experiment Publish Runway - Lily Roo",
        "",
        f"Generated: {packet['generated_at']}",
        "",
        "## Summary",
        f"- Manual rows ready for review: **{summary['review_ready_manual_count']}**",
        f"- Postable now: **{summary['postable_now_count']}**",
        f"- Public URLs needed: **{summary['public_url_log_needed_count']}**",
        f"- Pending result fields: **{summary['pending_result_field_count']}**",
        f"- Winner-ready formats: **{summary['winner_ready_candidate_count']} / {summary['winner_count_target']}**",
        f"- Blocked platform rows: **{summary['blocked_platform_count']}**",
        "",
        "## Next Publish Action",
        f"- {summary['next_publish_action']}",
        "",
        "## Manual Review Rows",
    ]
    rows = packet.get("manual_review_rows") or []
    if rows:
        for row in rows:
            lines.append(f"- `{row['id']}` {row['release']} on {row['platform']}")
            lines.append(f"  - Preview: `{row['approval_preview_command']}`")
            lines.append(f"  - Apply after review: `{row['approval_command']}`")
    else:
        lines.append("- None.")
    lines.extend(["", "## Runway Steps"])
    for step in packet.get("steps") or []:
        lines.append(f"- **{step['id']}** - `{step['status']}`")
        if step.get("preview_command"):
            lines.append(f"  - Preview: `{step['preview_command']}`")
        if step.get("apply_after_review_command"):
            lines.append(f"  - Apply after review: `{step['apply_after_review_command']}`")
        lines.append(f"  - Guardrail: {step['guardrail']}")
    lines.extend(["", "## Blocked Platform Rows"])
    blocked = packet.get("blocked_platform_rows") or []
    if blocked:
        for row in blocked:
            lines.append(f"- `{row['post_id']}` {row['platform']} - {row['reason'] or row['status']}")
    else:
        lines.append("- None.")
    lines.append("")
    return "\n".join(lines)


def replace_json_embed(html: str, block_id: str, payload) -> str:
    marker = f'<script type="application/json" id="{block_id}">'
    end_marker = "</script>"
    encoded = json.dumps(payload, indent=2, ensure_ascii=False)
    start = html.find(marker)
    if start == -1:
        return html.replace("<script>", f"\n{marker}{encoded}{end_marker}\n\n<script>", 1)
    content_start = start + len(marker)
    content_end = html.find(end_marker, content_start)
    if content_end == -1:
        raise RuntimeError(f"Could not find end marker for {block_id}")
    return html[:content_start] + encoded + html[content_end:]


def replace_text_embed(html: str, block_id: str, content: str) -> str:
    marker = f'<script type="text/plain" id="{block_id}">'
    end_marker = "</script>"
    start = html.find(marker)
    if start == -1:
        return html.replace("<script>", f"\n{marker}{content.rstrip()}{end_marker}\n\n<script>", 1)
    content_start = start + len(marker)
    content_end = html.find(end_marker, content_start)
    if content_end == -1:
        raise RuntimeError(f"Could not find end marker for {block_id}")
    return html[:content_start] + content.rstrip() + html[content_end:]


def sync_admin(packet: dict, markdown: str) -> None:
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    html = replace_json_embed(html, "embedded-experiment-publish-runway", packet)
    html = replace_text_embed(html, "embedded-experiment-publish-runway-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(packet)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(packet, markdown)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), **packet["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
