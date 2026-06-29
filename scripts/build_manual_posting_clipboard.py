#!/usr/bin/env python3
from __future__ import annotations

import json
import csv
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUAL_DISTRIBUTION = ROOT / "data" / "manual_distribution_packet.json"
YOUTUBE_RECONCILIATION = ROOT / "data" / "youtube_community_url_reconciliation.json"
PASTE_CARD_DIR = ROOT / "data" / "manual-posting-cards"
SESSION_FILE = PASTE_CARD_DIR / "youtube-community-session.md"
OUT = ROOT / "data" / "manual_posting_clipboard.json"
REPORT = ROOT / "admin" / "reports" / "manual-posting-clipboard.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"
PUBLISHED_LOG = ROOT / "admin" / "content" / "Published_Log.csv"
FIRST_MEASUREMENT_DUE_AFTER_HOURS = 24


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def read_published_log() -> list[dict]:
    if not PUBLISHED_LOG.exists():
        return []
    with PUBLISHED_LOG.open(newline="", encoding="utf-8") as handle:
        return [
            {key: (value or "").strip() for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def parse_log_date(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def note_value(notes: str, key: str) -> str:
    marker = f"{key}="
    for part in (notes or "").split(";"):
        part = part.strip()
        if part.startswith(marker):
            return part[len(marker):].strip()
    return ""


def parse_iso_timestamp(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def manual_logged_at(row: dict) -> datetime | None:
    notes = row.get("notes") or ""
    return parse_iso_timestamp(note_value(notes, "manual_logged_at")) or parse_log_date(row.get("date") or "")


def first_measurement_due_at(row: dict) -> datetime | None:
    notes = row.get("notes") or ""
    explicit = parse_iso_timestamp(note_value(notes, "first_measurement_due_at"))
    if explicit:
        return explicit
    logged_at = manual_logged_at(row)
    if logged_at:
        return logged_at + timedelta(hours=FIRST_MEASUREMENT_DUE_AFTER_HOURS)
    return None


def iso_z(value: datetime | None) -> str:
    if not value:
        return ""
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def has_result_values(row: dict) -> bool:
    metric_fields = ["views", "likes", "comments", "shares", "saves", "subs_delta"]
    has_metric = any((row.get(field) or "").strip() for field in metric_fields)
    notes = row.get("notes") or ""
    return has_metric and "result_evidence:" in notes


def published_log_by_id(rows: list[dict]) -> dict[str, dict]:
    result = {}
    for row in rows:
        content_id = (row.get("content_id") or "").strip()
        notes = row.get("notes") or ""
        ids = [content_id]
        match = re.search(r"manual_distribution_id=([^;]+)", notes)
        if match:
            ids.append(match.group(1).strip())
        for post_id in ids:
            if post_id:
                result[post_id] = row
    return result


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


def slug(value: str) -> str:
    slugged = re.sub(r"[^A-Za-z0-9_-]+", "-", value.strip()).strip("-").lower()
    return slugged or "manual-post"


def post_card(row: dict) -> dict:
    posting = row.get("manual_posting_packet") or {}
    log_effect = row.get("log_effect") or {}
    post_id = row.get("id") or ""
    paste_text_path = PASTE_CARD_DIR / f"{slug(post_id)}.txt"
    log_preview_command = row.get("log_preview_command") or ""
    log_apply_command = row.get("log_apply_command") or ""
    result_handoff = {
        "status": "blocked_until_public_url_logged",
        "source_report": "admin/reports/experiment-result-clipboard.md",
        "reason": "Experiment result collection starts after the real public URL is logged in Published_Log.csv.",
        "first_measurement_due_after_hours": FIRST_MEASUREMENT_DUE_AFTER_HOURS,
        "first_measurement_window": "Collect first public performance values 24 hours after the public URL is logged.",
    }
    paste_text = posting.get("paste_text") or row.get("copy_block") or ""
    asset_url = posting.get("asset_url") or row.get("asset_download_url") or ""
    asset_local_path = (row.get("asset_audit") or {}).get("local_path") or ""
    return {
        "id": post_id,
        "release": row.get("release") or "",
        "platform": row.get("platform") or "",
        "status": row.get("distribution_status") or "",
        "posting_surface": posting.get("posting_surface") or "YouTube Studio Community",
        "public_community_url": posting.get("public_community_url") or "",
        "paste_text": paste_text,
        "paste_text_path": str(paste_text_path.relative_to(ROOT)),
        "asset_url": asset_url,
        "asset_status": (row.get("asset_audit") or {}).get("status") or "",
        "asset_local_path": asset_local_path,
        "destination_links": row.get("destination_links") or [],
        "destination_link_audit": row.get("destination_link_audit") or [],
        "selected_cta_strength": row.get("selected_cta_strength") or "",
        "postable_now": bool(posting.get("postable_now")),
        "logging_required": bool(posting.get("logging_required")),
        "public_url": row.get("published_url") or "",
        "public_url_placeholder": log_effect.get("url_placeholder") or "PUBLIC_URL",
        "log_preview_command": log_preview_command,
        "log_apply_command": log_apply_command,
        "log_notes": log_effect.get("notes") or "",
        "result_handoff": result_handoff,
        "posting_bundle": {
            "surface_url": posting.get("public_community_url") or "",
            "copy_source": str(paste_text_path.relative_to(ROOT)),
            "asset_source": asset_local_path or asset_url,
            "asset_url": asset_url,
            "public_url_required": True,
            "url_placeholder": log_effect.get("url_placeholder") or "PUBLIC_URL",
            "preview_command_template": log_preview_command,
            "apply_command_template": log_apply_command,
            "result_collection_trigger": "Log the public URL, then use admin/reports/experiment-result-clipboard.md for the first 24-hour measurement.",
            "first_measurement_due_after_hours": FIRST_MEASUREMENT_DUE_AFTER_HOURS,
            "operator_sequence": [
                "Open the YouTube Community surface.",
                "Paste the copy from copy_source.",
                "Attach the asset from asset_source.",
                "Publish the Community post.",
                "Copy the real public Community post URL.",
                "Run the preview command with the real URL.",
                "Run the apply command after the preview passes.",
            ],
        },
        "after_posting_checklist": [
            "Copy the real public YouTube Community post URL.",
            f"Run the log preview command: {log_preview_command}",
            f"Run the log apply command after preview passes: {log_apply_command}",
            "Refresh Admin and confirm this card moves out of the manual posting queue.",
            "Open the experiment result clipboard 24 hours after URL logging for the first measurement.",
        ],
        "completion_evidence": [
            "A real public YouTube Community post URL exists.",
            "The URL is logged with scripts/log_manual_distribution.py.",
            "admin/content/Published_Log.csv contains this manual_distribution_id.",
            "The experiment result clipboard can request first measurement values at the 24-hour readout for this post.",
        ],
    }


def build_session_manifest(cards: list[dict], summary: dict) -> dict:
    if not cards:
        return {
            "status": "not_active",
            "session_name": "No manual posting session",
            "surface_url": "",
            "postable_count": 0,
            "waiting_public_url_count": 0,
            "logged_count": 0,
            "sequence_ids": [],
            "copy_sources": [],
            "asset_sources": [],
            "url_template_path": "",
            "batch_log_preview_command": "",
            "batch_log_apply_command": "",
            "batch_log_partial_apply_command": "",
            "public_url_reconciliation_command": "",
            "result_handoff_report": "",
            "first_measurement_due_after_hours": FIRST_MEASUREMENT_DUE_AFTER_HOURS,
            "rows": [],
            "posting_sequence": [],
            "completion_evidence": [],
            "guardrail": "No manual posting rows are active.",
        }
    rows = []
    for index, card in enumerate(cards, start=1):
        public_url = (card.get("public_url") or "").strip()
        posted = bool(public_url)
        rows.append({
            "sequence": index,
            "id": card.get("id") or "",
            "release": card.get("release") or "",
            "platform": card.get("platform") or "",
            "status": "logged" if posted else "waiting_for_post_and_public_url",
            "copy_source": card.get("paste_text_path") or "",
            "asset_source": (card.get("posting_bundle") or {}).get("asset_source") or "",
            "surface_url": card.get("public_community_url") or "",
            "public_url": public_url,
            "public_url_required": not posted,
            "preview_command_template": card.get("log_preview_command") or "",
            "apply_command_template": card.get("log_apply_command") or "",
            "result_collection_trigger": (card.get("posting_bundle") or {}).get("result_collection_trigger") or "",
            "first_measurement_due_after_hours": (card.get("posting_bundle") or {}).get("first_measurement_due_after_hours") or FIRST_MEASUREMENT_DUE_AFTER_HOURS,
            "completion_evidence": card.get("completion_evidence") or [],
        })
    waiting = [row for row in rows if row.get("public_url_required")]
    return {
        "status": "ready_to_post" if waiting else "complete",
        "session_name": "YouTube Community manual posting batch",
        "surface_url": summary.get("public_community_url") or "",
        "postable_count": len(cards),
        "waiting_public_url_count": len(waiting),
        "logged_count": len(rows) - len(waiting),
        "sequence_ids": [row.get("id") for row in rows],
        "copy_sources": [row.get("copy_source") for row in rows if row.get("copy_source")],
        "asset_sources": [row.get("asset_source") for row in rows if row.get("asset_source")],
        "url_template_path": summary.get("url_template_path") or "",
        "batch_log_preview_command": summary.get("batch_log_preview_command") or "",
        "batch_log_apply_command": summary.get("batch_log_apply_command") or "",
        "batch_log_partial_apply_command": summary.get("batch_log_partial_apply_command") or "",
        "public_url_reconciliation_command": summary.get("public_url_reconciliation_command") or "",
        "result_handoff_report": summary.get("result_handoff_report") or "admin/reports/experiment-result-clipboard.md",
        "first_measurement_due_after_hours": FIRST_MEASUREMENT_DUE_AFTER_HOURS,
        "rows": rows,
        "posting_sequence": [
            "Open the YouTube Community surface once.",
            "Post each session row in sequence using its copy_source and asset_source.",
            "After each publish, copy the real public URL into the URL worksheet.",
            "Run the batch preview command; use partial apply if only some rows have public URLs.",
            "After logging, collect the first 24-hour metrics from the result handoff report.",
        ],
        "completion_evidence": [
            "Each session row has a real public YouTube Community URL.",
            "The URL worksheet has no remaining blank public_url cells for these IDs.",
            "Published_Log.csv contains each session ID with a manual_distribution_id note.",
            "The experiment result clipboard lists the logged posts for first 24-hour measurement collection.",
        ],
        "guardrail": "Do not mark the session complete until every row has a real public URL logged.",
    }


def first_url_acceleration(cards: list[dict], summary: dict) -> dict:
    waiting = [card for card in cards if not (card.get("public_url") or "").strip()]
    if not waiting:
        return {
            "status": "clear",
            "first_post_id": "",
            "next_action": "All manual post URLs are already logged.",
            "guardrail": "No placeholder URLs are accepted.",
        }
    first = waiting[0]
    return {
        "status": "ready_after_first_public_url",
        "first_post_id": first.get("id") or "",
        "first_release": first.get("release") or "",
        "surface_url": first.get("public_community_url") or summary.get("public_community_url") or "",
        "copy_source": first.get("paste_text_path") or "",
        "asset_source": (first.get("posting_bundle") or {}).get("asset_source") or first.get("asset_url") or "",
        "single_preview_command": first.get("log_preview_command") or "",
        "single_apply_command": first.get("log_apply_command") or "",
        "partial_batch_apply_command": summary.get("batch_log_partial_apply_command") or "",
        "measurement_report": summary.get("result_handoff_report") or "admin/reports/experiment-result-clipboard.md",
        "measurement_preview_command": "python3 scripts/update_experiment_results.py --from-wide-csv data/experiment_result_entry_wide_template.csv --dry-run",
        "first_measurement_due_after_hours": FIRST_MEASUREMENT_DUE_AFTER_HOURS,
        "why": "Logging the first public URL immediately lets that post enter the 24-hour result-collection queue without waiting for the full batch.",
        "next_action": "Post the first card, paste its real public URL into the worksheet, run the preview, then apply with --allow-partial.",
        "guardrail": "Use only a real public YouTube Community post URL; never apply PUBLIC_URL or blank worksheet rows.",
    }


def first_post_runbook(cards: list[dict], summary: dict) -> dict:
    waiting = [card for card in cards if not (card.get("public_url") or "").strip()]
    if not waiting:
        return {
            "status": "clear",
            "post_id": "",
            "next_action": "All manual post URLs are already logged.",
            "guardrail": "No placeholder URLs are accepted.",
        }
    first = waiting[0]
    bundle = first.get("posting_bundle") or {}
    worksheet_path = summary.get("url_template_path") or "data/manual_distribution_url_template.csv"
    return {
        "status": "ready_to_post_and_log",
        "post_id": first.get("id") or "",
        "release": first.get("release") or "",
        "platform": first.get("platform") or "",
        "posting_surface": first.get("posting_surface") or summary.get("posting_surface") or "YouTube Studio Community",
        "surface_url": first.get("public_community_url") or summary.get("public_community_url") or "",
        "copy_source": first.get("paste_text_path") or "",
        "asset_source": bundle.get("asset_source") or first.get("asset_local_path") or first.get("asset_url") or "",
        "asset_url": first.get("asset_url") or "",
        "paste_text": first.get("paste_text") or "",
        "public_url_slot": "PUBLIC_URL",
        "url_worksheet_path": worksheet_path,
        "worksheet_update_instruction": f"Paste the real public URL into {worksheet_path} public_url for {first.get('id') or 'the first manual post'}.",
        "log_preview_command_template": first.get("log_preview_command") or "",
        "log_apply_command_template": first.get("log_apply_command") or "",
        "partial_batch_apply_command": summary.get("batch_log_partial_apply_command") or "",
        "result_handoff_report": summary.get("result_handoff_report") or "admin/reports/experiment-result-clipboard.md",
        "first_measurement_due_after_hours": FIRST_MEASUREMENT_DUE_AFTER_HOURS,
        "first_measurement_trigger": "after real public URL is logged",
        "post_completion_checklist": [
            "Open the YouTube Community surface.",
            "Paste the copy exactly from copy_source.",
            "Attach the listed asset_source or asset_url.",
            "Publish the Community post manually.",
            "Copy the real public YouTube Community post URL.",
            "Run the preview command with the real URL.",
            "Run the apply command only after preview confirms the real URL.",
            "Confirm Published_Log.csv contains this manual distribution ID.",
            "Collect first visible metrics 24 hours after the public URL is logged.",
        ],
        "completion_evidence": [
            "A real public YouTube Community post URL exists.",
            "The URL has replaced PUBLIC_URL in the preview/apply command or worksheet.",
            "Published_Log.csv contains this manual_distribution_id.",
            "The experiment result clipboard lists this post for its 24-hour measurement.",
        ],
        "guardrail": "Do not run an apply command with PUBLIC_URL, a blank URL, or a private/non-public post URL.",
    }


def lifecycle_stage(row: dict, log_row: dict | None) -> str:
    if log_row and has_result_values(log_row):
        return "result_recorded"
    if log_row:
        due_at = first_measurement_due_at(log_row)
        if due_at and datetime.now(timezone.utc) >= due_at:
            return "ready_for_first_measurement"
        return "measurement_waiting_24h"
    if row.get("published_url"):
        return "public_url_ready_to_log"
    return "waiting_for_manual_post"


def lifecycle_next_action(stage: str, row: dict, log_row: dict | None) -> str:
    post_id = row.get("id") or ""
    if stage == "result_recorded":
        return "Result values and evidence are already recorded in Published_Log.csv."
    if stage == "ready_for_first_measurement":
        return f"Collect first 24-hour metrics for {post_id} in admin/reports/experiment-result-clipboard.md."
    if stage == "measurement_waiting_24h":
        return "Wait until the first 24-hour measurement window, then collect visible metrics."
    if stage == "public_url_ready_to_log":
        return f"Preview and apply URL logging for {post_id} with scripts/log_manual_distribution.py."
    return "Publish the Community card, copy the real public post URL, then log it."


def build_tracking_lifecycle(manual_rows: list[dict]) -> dict:
    published_rows = read_published_log()
    log_by_id = published_log_by_id(published_rows)
    stages = []
    rows = []
    now = datetime.now(timezone.utc)
    for row in manual_rows:
        post_id = row.get("id") or ""
        log_row = log_by_id.get(post_id)
        logged_at = manual_logged_at(log_row or {})
        due_at = first_measurement_due_at(log_row or {})
        stage = lifecycle_stage(row, log_row)
        stages.append(stage)
        rows.append({
            "id": post_id,
            "release": row.get("release") or "",
            "platform": row.get("platform") or "",
            "stage": stage,
            "posted": bool(row.get("published_url") or log_row),
            "public_url_logged": bool(log_row),
            "result_recorded": bool(log_row and has_result_values(log_row)),
            "public_url": (log_row or {}).get("post_id_or_url") or row.get("published_url") or "",
            "logged_at": iso_z(logged_at),
            "logged_date": (log_row or {}).get("date") or "",
            "measurement_due_at": iso_z(due_at),
            "measurement_due": bool(due_at and now >= due_at),
            "measurement_due_source": (
                "first_measurement_due_at_note"
                if note_value((log_row or {}).get("notes") or "", "first_measurement_due_at")
                else "manual_logged_at_note"
                if note_value((log_row or {}).get("notes") or "", "manual_logged_at")
                else "published_log_date_fallback"
                if log_row
                else "after_url_logging"
            ),
            "result_handoff_report": "admin/reports/experiment-result-clipboard.md",
            "next_action": lifecycle_next_action(stage, row, log_row),
            "completion_evidence": [
                "A real public YouTube Community post URL exists.",
                "Published_Log.csv contains this manual_distribution_id or content_id.",
                "The first measurement has at least one numeric value plus a result_evidence note.",
            ],
        })
    counts = {stage: stages.count(stage) for stage in sorted(set(stages))}
    return {
        "status": "complete" if rows and all(row["result_recorded"] for row in rows) else "active",
        "total_count": len(rows),
        "posted_count": sum(1 for row in rows if row["posted"]),
        "public_url_logged_count": sum(1 for row in rows if row["public_url_logged"]),
        "result_recorded_count": sum(1 for row in rows if row["result_recorded"]),
        "waiting_manual_post_count": counts.get("waiting_for_manual_post", 0),
        "ready_for_measurement_count": counts.get("ready_for_first_measurement", 0),
        "stage_counts": counts,
        "primary_gap": (
            "manual_posting"
            if counts.get("waiting_for_manual_post", 0)
            else "result_measurement"
            if any(stage in {"measurement_waiting_24h", "ready_for_first_measurement"} for stage in stages)
            else "complete"
        ),
        "rows": rows,
        "guardrail": "Do not advance a lifecycle stage without the listed completion evidence.",
    }


def build_payload() -> dict:
    packet = read_json(MANUAL_DISTRIBUTION, {})
    reconciliation = read_json(YOUTUBE_RECONCILIATION, {})
    reconciliation_summary = reconciliation.get("summary") or {}
    distribution = packet.get("manual_distribution_docket") or {}
    completion = packet.get("manual_completion_manifest") or {}
    manual_rows = [
        row
        for row in packet.get("rows") or []
        if (row.get("manual_posting_packet") or {}).get("postable_now") or row.get("logged")
    ]
    postable_rows = [
        row
        for row in manual_rows
        if (row.get("manual_posting_packet") or {}).get("postable_now") and not row.get("logged")
    ]
    cards = [post_card(row) for row in postable_rows]
    paste_text_files = [card.get("paste_text_path") for card in cards if card.get("paste_text_path")]
    url_template_path = completion.get("url_template_path") or ""
    partial_apply_command = (
        f"python3 scripts/log_manual_distribution.py --from-csv {url_template_path} --allow-partial --apply --refresh-admin"
        if url_template_path
        else ""
    )
    summary = {
        "status": "ready_to_post" if cards else "empty",
        "posting_surface": completion.get("posting_surface") or "YouTube Studio Community",
        "public_community_url": completion.get("public_community_url") or distribution.get("public_community_url") or "",
        "postable_count": len(cards),
        "waiting_public_url_count": completion.get("waiting_public_url_count") or len(cards),
        "pending_log_ids": completion.get("pending_log_ids") or [card["id"] for card in cards],
        "posting_bundle_count": sum(1 for card in cards if card.get("posting_bundle")),
        "url_template_path": completion.get("url_template_path") or "",
        "paste_text_dir": str(PASTE_CARD_DIR.relative_to(ROOT)),
        "session_file_path": str(SESSION_FILE.relative_to(ROOT)),
        "paste_text_file_count": len(paste_text_files),
        "paste_text_files": paste_text_files,
        "batch_log_preview_command": completion.get("batch_log_preview_command") or "",
        "batch_log_apply_command": completion.get("batch_log_apply_command") or "",
        "batch_log_partial_apply_command": partial_apply_command,
        "public_url_reconciliation_status": reconciliation_summary.get("status") or "not_run",
        "public_url_reconciliation_match_count": reconciliation_summary.get("match_count") or 0,
        "public_url_reconciliation_command": "python3 scripts/reconcile_youtube_community_urls.py",
        "public_url_reconciliation_apply_command": reconciliation_summary.get("apply_command") or "",
        "result_handoff_report": "admin/reports/experiment-result-clipboard.md",
        "first_measurement_due_after_hours": FIRST_MEASUREMENT_DUE_AFTER_HOURS,
        "next_action": (
            "Post each card in YouTube Community, copy the real public URL, then log it."
            if cards
            else "No approved manual posts are currently waiting."
        ),
    }
    if cards:
        first_card = cards[0]
        first_bundle = first_card.get("posting_bundle") or {}
        summary["next_post_now"] = {
            "id": first_card.get("id") or "",
            "release": first_card.get("release") or "",
            "platform": first_card.get("platform") or "",
            "surface_url": first_card.get("public_community_url") or summary.get("public_community_url") or "",
            "copy_source": first_card.get("paste_text_path") or "",
            "asset_source": first_bundle.get("asset_source") or first_card.get("asset_local_path") or first_card.get("asset_url") or "",
            "asset_url": first_card.get("asset_url") or "",
            "paste_text": first_card.get("paste_text") or "",
            "log_preview_command": first_card.get("log_preview_command") or "",
            "log_apply_command": first_card.get("log_apply_command") or "",
            "result_handoff_report": "admin/reports/experiment-result-clipboard.md",
            "completion_evidence": [
                "The YouTube Community post is published from the listed text and asset.",
                "A real public YouTube Community URL replaces PUBLIC_URL in the logging command.",
                "The post appears in Published_Log.csv with this manual distribution ID.",
            ],
        }
    acceleration = first_url_acceleration(cards, summary)
    runbook = first_post_runbook(cards, summary)
    tracking_lifecycle = build_tracking_lifecycle(manual_rows)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "manual_distribution_packet": str(MANUAL_DISTRIBUTION.relative_to(ROOT)),
            "manual_distribution_url_template": completion.get("url_template_path") or "",
            "youtube_community_url_reconciliation": str(YOUTUBE_RECONCILIATION.relative_to(ROOT)) if YOUTUBE_RECONCILIATION.exists() else "",
            "published_log_target": "admin/content/Published_Log.csv",
        },
        "summary": summary,
        "first_post_runbook": runbook,
        "first_url_acceleration": acceleration,
        "tracking_lifecycle": tracking_lifecycle,
        "session_manifest": build_session_manifest(cards, summary),
        "post_cards": cards,
        "operator_steps": [
            "Open the YouTube Community surface.",
            "For each card, paste the text exactly as shown.",
            "Attach the listed asset URL or download/open the local asset path if needed.",
            "Publish manually in YouTube Studio Community.",
            "Copy the real public post URL.",
            "Use the first-post runbook to preview and apply the first real public URL.",
            "Run the preview logging command with the real URL, then run the apply command.",
            "After the first public URL exists, use the first-url acceleration command so that post can enter result collection immediately.",
            "Or rerun the public URL reconciliation command after posting to auto-detect confident public URLs.",
            "If only one public URL is ready, use the partial batch apply command so that post can start accumulating measurable evidence immediately.",
        ] if cards else [],
        "guardrails": [
            "This clipboard does not approve, schedule, publish, or log posts.",
            "Do not use PUBLIC_URL in an apply command.",
            "Use --allow-partial only after at least one worksheet row has a real public_url; blank rows remain waiting.",
            "Do not mark a row complete until a real public YouTube Community URL is logged.",
        ],
    }


def audit_sources_line(audit: dict) -> str:
    evidence = audit.get("evidence") or []
    if not evidence:
        return "no local evidence"
    return "; ".join(f"{item.get('label')} ({item.get('source')})" for item in evidence)


def write_paste_files(cards: list[dict]) -> None:
    PASTE_CARD_DIR.mkdir(parents=True, exist_ok=True)
    wanted = {card.get("paste_text_path") for card in cards if card.get("paste_text_path")}
    for existing in PASTE_CARD_DIR.glob("*.txt"):
        relative = str(existing.relative_to(ROOT))
        if relative not in wanted:
            existing.unlink()
    for card in cards:
        relative_path = card.get("paste_text_path") or ""
        if not relative_path:
            continue
        path = ROOT / relative_path
        path.write_text((card.get("paste_text") or "").rstrip() + "\n", encoding="utf-8")


def write_session_file(payload: dict) -> None:
    summary = payload.get("summary") or {}
    session = payload.get("session_manifest") or {}
    runbook = payload.get("first_post_runbook") or {}
    acceleration = payload.get("first_url_acceleration") or {}
    lifecycle = payload.get("tracking_lifecycle") or {}
    if not payload.get("post_cards"):
        lines = [
            "# No Manual Posting Session",
            "",
            f"Generated: {payload.get('generated_at')}",
            "",
            "No manual posts are currently waiting. API automation has replaced the manual posting lane.",
            "",
        ]
        SESSION_FILE.write_text("\n".join(lines), encoding="utf-8")
        return
    lines = [
        "# YouTube Community Manual Posting Session",
        "",
        f"Generated: {payload.get('generated_at')}",
        f"Surface: {summary.get('public_community_url') or session.get('surface_url') or 'not set'}",
        f"URL worksheet: {summary.get('url_template_path') or 'not available'}",
        f"Partial apply: {summary.get('batch_log_partial_apply_command') or 'not available'}",
        "",
        "## Steps",
    ]
    for step in session.get("posting_sequence") or []:
        lines.append(f"- {step}")
    lines.extend([
        "",
        "## First Post Runbook",
        f"- Status: {runbook.get('status') or 'unknown'}",
        f"- Post: {runbook.get('post_id') or 'not available'}",
        f"- Copy file: {runbook.get('copy_source') or 'not available'}",
        f"- Asset: {runbook.get('asset_source') or 'not available'}",
        f"- URL worksheet: {runbook.get('url_worksheet_path') or 'not available'}",
        f"- Worksheet update: {runbook.get('worksheet_update_instruction') or 'not available'}",
        f"- Preview: {runbook.get('log_preview_command_template') or 'not available'}",
        f"- Apply: {runbook.get('log_apply_command_template') or 'not available'}",
        f"- Partial apply: {runbook.get('partial_batch_apply_command') or 'not available'}",
        f"- Measurement trigger: {runbook.get('first_measurement_trigger') or 'not available'}",
        "",
        "## First URL Acceleration",
        f"- Status: {acceleration.get('status') or 'unknown'}",
        f"- First post: {acceleration.get('first_post_id') or 'not available'}",
        f"- Why: {acceleration.get('why') or 'not available'}",
        f"- Preview: {acceleration.get('single_preview_command') or 'not available'}",
        f"- Partial apply: {acceleration.get('partial_batch_apply_command') or 'not available'}",
        f"- Measurement report: {acceleration.get('measurement_report') or 'not available'}",
    ])
    lines.extend([
        "",
        "## Tracking Lifecycle",
        f"- Status: {lifecycle.get('status') or 'unknown'}",
        f"- Posted: {lifecycle.get('posted_count', 0)}/{lifecycle.get('total_count', 0)}",
        f"- Public URLs logged: {lifecycle.get('public_url_logged_count', 0)}/{lifecycle.get('total_count', 0)}",
        f"- Results recorded: {lifecycle.get('result_recorded_count', 0)}/{lifecycle.get('total_count', 0)}",
        f"- Primary gap: {lifecycle.get('primary_gap') or 'unknown'}",
    ])
    for row in lifecycle.get("rows") or []:
        lines.append(f"- {row.get('id')}: {row.get('stage')} -> {row.get('next_action')}")
    lines.extend([
        "",
        "## Posts",
    ])
    if not payload.get("post_cards"):
        lines.append("- No manual posts are currently waiting.")
    for index, card in enumerate(payload.get("post_cards") or [], start=1):
        bundle = card.get("posting_bundle") or {}
        lines.extend([
            f"### {index}. {card.get('id')} - {card.get('release')}",
            f"- Copy file: {card.get('paste_text_path') or 'not available'}",
            f"- Asset: {bundle.get('asset_source') or card.get('asset_url') or 'not available'}",
            f"- Preview after public URL exists: {card.get('log_preview_command') or 'not available'}",
            f"- Apply after preview passes: {card.get('log_apply_command') or 'not available'}",
            "",
            "```text",
            (card.get("paste_text") or "").rstrip(),
            "```",
            "",
            "Public URL:",
            "",
        ])
    lines.extend([
        "## Completion Evidence",
    ])
    for item in session.get("completion_evidence") or []:
        lines.append(f"- {item}")
    lines.append("")
    SESSION_FILE.write_text("\n".join(lines), encoding="utf-8")


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    runbook = payload.get("first_post_runbook") or {}
    acceleration = payload.get("first_url_acceleration") or {}
    lifecycle = payload.get("tracking_lifecycle") or {}
    lines = [
        "# Manual Posting Clipboard - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Status: **{summary['status']}**",
        f"- Posting surface: **{summary['posting_surface']}**",
        f"- Public Community URL: {summary.get('public_community_url') or 'not set'}",
        f"- Postable cards: **{summary['postable_count']}**",
        f"- Waiting public URLs: **{summary['waiting_public_url_count']}**",
        f"- URL worksheet: `{summary.get('url_template_path') or 'not available'}`",
        f"- Session file: `{summary.get('session_file_path') or 'not available'}`",
        f"- Paste text files: `{summary.get('paste_text_dir') or 'not available'}` ({summary.get('paste_text_file_count', 0)} file(s))",
        f"- Batch log preview: `{summary.get('batch_log_preview_command') or 'not available'}`",
        f"- Batch log apply after posting: `{summary.get('batch_log_apply_command') or 'not available'}`",
        f"- Partial batch apply after first URL: `{summary.get('batch_log_partial_apply_command') or 'not available'}`",
        f"- Public URL reconciliation: `{summary.get('public_url_reconciliation_command') or 'not available'}`",
        f"- Reconciliation status: **{summary.get('public_url_reconciliation_status')}** ({summary.get('public_url_reconciliation_match_count')} match(es))",
        f"- Reconciliation apply if matches exist: `{summary.get('public_url_reconciliation_apply_command') or 'not available'}`",
        f"- Result handoff after URL logging: `{summary.get('result_handoff_report') or 'not available'}`",
        f"- First measurement due: **{summary.get('first_measurement_due_after_hours')} hours after public URL logging**",
        f"- Next action: {summary['next_action']}",
    ]
    if lifecycle:
        lines.extend([
            "",
            "## Tracking Lifecycle",
            f"- Status: **{lifecycle.get('status', 'unknown')}**",
            f"- Posted: **{lifecycle.get('posted_count', 0)}/{lifecycle.get('total_count', 0)}**",
            f"- Public URLs logged: **{lifecycle.get('public_url_logged_count', 0)}/{lifecycle.get('total_count', 0)}**",
            f"- Results recorded: **{lifecycle.get('result_recorded_count', 0)}/{lifecycle.get('total_count', 0)}**",
            f"- Ready for measurement: **{lifecycle.get('ready_for_measurement_count', 0)}**",
            f"- Primary gap: `{lifecycle.get('primary_gap', 'unknown')}`",
            f"- Guardrail: {lifecycle.get('guardrail') or 'Do not advance without evidence.'}",
        ])
        if lifecycle.get("rows"):
            lines.append("- Lifecycle rows:")
            for row in lifecycle["rows"]:
                lines.append(
                    f"  - `{row.get('id')}` `{row.get('stage')}` posted `{row.get('posted')}` "
                    f"logged `{row.get('public_url_logged')}` measured `{row.get('result_recorded')}` "
                    f"due `{row.get('measurement_due_at') or 'after URL logging'}`"
                )
                lines.append(f"    - Next: {row.get('next_action')}")
    next_post = summary.get("next_post_now") or {}
    lines.extend([
        "",
        "## Post Now",
    ])
    if next_post:
        lines.extend([
            f"- First card: `{next_post.get('id')}` ({next_post.get('release')})",
            f"- Surface: {next_post.get('surface_url') or 'not set'}",
            f"- Copy source: `{next_post.get('copy_source') or 'not available'}`",
            f"- Asset source: `{next_post.get('asset_source') or 'not available'}`",
            f"- Preview URL log: `{next_post.get('log_preview_command') or 'not available'}`",
            f"- Apply URL log: `{next_post.get('log_apply_command') or 'not available'}`",
            f"- Result handoff: `{next_post.get('result_handoff_report') or 'not available'}`",
            f"- First measurement due: **{summary.get('first_measurement_due_after_hours')} hours after URL logging**",
        ])
        if next_post.get("completion_evidence"):
            lines.append("- Completion evidence:")
            for item in next_post["completion_evidence"]:
                lines.append(f"  - {item}")
    else:
        lines.append("- No manual post is waiting; API automation has replaced the manual posting lane.")
    if runbook:
        lines.extend([
            "",
            "## First Post Runbook",
            f"- Status: **{runbook.get('status', 'unknown')}**",
            f"- Post: `{runbook.get('post_id') or 'not available'}` ({runbook.get('release') or 'unknown release'})",
            f"- Surface: {runbook.get('surface_url') or 'not set'}",
            f"- Copy file: `{runbook.get('copy_source') or 'not available'}`",
            f"- Asset: `{runbook.get('asset_source') or 'not available'}`",
            f"- Public URL slot: `{runbook.get('public_url_slot') or 'PUBLIC_URL'}`",
            f"- URL worksheet: `{runbook.get('url_worksheet_path') or 'not available'}`",
            f"- Worksheet update: {runbook.get('worksheet_update_instruction') or 'not available'}",
            f"- Preview URL log: `{runbook.get('log_preview_command_template') or 'not available'}`",
            f"- Apply URL log: `{runbook.get('log_apply_command_template') or 'not available'}`",
            f"- Partial batch apply: `{runbook.get('partial_batch_apply_command') or 'not available'}`",
            f"- Result handoff: `{runbook.get('result_handoff_report') or 'not available'}`",
            f"- First measurement trigger: **{runbook.get('first_measurement_trigger') or 'after URL logging'}**",
            f"- First measurement due: **{runbook.get('first_measurement_due_after_hours') or summary.get('first_measurement_due_after_hours')} hours after URL logging**",
            f"- Guardrail: {runbook.get('guardrail') or 'Use only real public URLs.'}",
        ])
        if runbook.get("post_completion_checklist"):
            lines.append("- Checklist:")
            for item in runbook["post_completion_checklist"]:
                lines.append(f"  - {item}")
        if runbook.get("completion_evidence"):
            lines.append("- Completion evidence:")
            for item in runbook["completion_evidence"]:
                lines.append(f"  - {item}")
    lines.extend([
        "",
        "## First URL Acceleration",
        f"- Status: **{acceleration.get('status', 'unknown')}**",
        f"- First post: `{acceleration.get('first_post_id') or 'not available'}` ({acceleration.get('first_release') or 'unknown release'})",
        f"- Copy file: `{acceleration.get('copy_source') or 'not available'}`",
        f"- Asset: `{acceleration.get('asset_source') or 'not available'}`",
        f"- Preview first URL: `{acceleration.get('single_preview_command') or 'not available'}`",
        f"- Apply first URL with partial batch: `{acceleration.get('partial_batch_apply_command') or 'not available'}`",
        f"- Measurement report: `{acceleration.get('measurement_report') or 'not available'}`",
        f"- Measurement preview: `{acceleration.get('measurement_preview_command') or 'not available'}`",
        f"- First measurement due: **{acceleration.get('first_measurement_due_after_hours') or summary.get('first_measurement_due_after_hours')} hours after URL logging**",
        f"- Why: {acceleration.get('why') or 'not available'}",
        f"- Guardrail: {acceleration.get('guardrail') or 'Use only real public URLs.'}",
        "",
        "## Session Manifest",
    ])
    session = payload.get("session_manifest") or {}
    lines.extend([
        f"- Status: **{session.get('status', 'unknown')}**",
        f"- Session: **{session.get('session_name', 'manual posting session')}**",
        f"- Surface: {session.get('surface_url') or 'not set'}",
        f"- Postable rows: **{session.get('postable_count', 0)}**",
        f"- Waiting public URLs: **{session.get('waiting_public_url_count', 0)}**",
        f"- Logged rows: **{session.get('logged_count', 0)}**",
        f"- URL worksheet: `{session.get('url_template_path') or 'not available'}`",
        f"- Batch preview: `{session.get('batch_log_preview_command') or 'not available'}`",
        f"- Batch apply: `{session.get('batch_log_apply_command') or 'not available'}`",
        f"- Partial apply: `{session.get('batch_log_partial_apply_command') or 'not available'}`",
        f"- URL reconciliation: `{session.get('public_url_reconciliation_command') or 'not available'}`",
        f"- Result handoff: `{session.get('result_handoff_report') or 'not available'}`",
        f"- First measurement due: **{session.get('first_measurement_due_after_hours') or summary.get('first_measurement_due_after_hours')} hours after URL logging**",
        f"- Guardrail: {session.get('guardrail') or 'Do not complete without public URLs.'}",
        "",
    ])
    if session.get("posting_sequence"):
        lines.append("- Posting sequence:")
        for item in session["posting_sequence"]:
            lines.append(f"  - {item}")
    if session.get("completion_evidence"):
        lines.append("- Completion evidence:")
        for item in session["completion_evidence"]:
            lines.append(f"  - {item}")
    if session.get("rows"):
        lines.append("- Session rows:")
        for row in session["rows"]:
            lines.append(f"  - `{row.get('sequence')}` `{row.get('id')}` `{row.get('status')}` first measurement `{row.get('first_measurement_due_after_hours')}h` copy `{row.get('copy_source')}` asset `{row.get('asset_source')}`")
    else:
        lines.append("- Session rows: none; API automation has replaced the manual posting lane.")
    lines.extend([
        "",
        "## Cards",
    ])
    if not payload["post_cards"]:
        lines.append("- No approved manual posts are currently waiting.")
        lines.extend([
            "- Posting bundle: not applicable while the manual lane is empty.",
            "- Paste text: not applicable while the manual lane is empty.",
            "- Log preview after posting: not applicable while the manual lane is empty.",
            "- Bundle result trigger: not applicable while the manual lane is empty.",
            "- After posting checklist: no manual posting checklist is active.",
        ])
    for index, card in enumerate(payload["post_cards"], start=1):
        lines.extend([
            f"### {index}. {card['release']} - {card['platform']}",
            f"- ID: `{card['id']}`",
            f"- Status: `{card['status']}`",
            f"- Open: {card.get('public_community_url') or 'not set'}",
            f"- Paste file: `{card.get('paste_text_path') or 'not available'}`",
            f"- Posting bundle: copy `{(card.get('posting_bundle') or {}).get('copy_source') or 'not available'}`, asset `{(card.get('posting_bundle') or {}).get('asset_source') or 'not available'}`",
            "- Paste text:",
            "```text",
            card.get("paste_text") or "",
            "```",
            f"- Asset: {card.get('asset_url') or 'not set'}",
            f"- Asset evidence: `{card.get('asset_status') or 'unknown'}` {card.get('asset_local_path') or ''}".rstrip(),
        ])
        if card.get("destination_links"):
            lines.append(f"- Destination links: {', '.join(card['destination_links'])}")
        if card.get("destination_link_audit"):
            lines.append("- Destination evidence:")
            for audit in card["destination_link_audit"]:
                lines.append(f"  - `{audit.get('status')}` {audit.get('url')}: {audit_sources_line(audit)}")
        lines.extend([
            f"- Public URL slot: `{card.get('public_url') or card.get('public_url_placeholder') or 'PUBLIC_URL'}`",
            f"- Log preview after posting: `{card.get('log_preview_command') or 'not available'}`",
            f"- Log apply after posting: `{card.get('log_apply_command') or 'not available'}`",
            f"- Log notes: `{card.get('log_notes') or 'not available'}`",
        ])
        bundle = card.get("posting_bundle") or {}
        if bundle:
            lines.extend([
                f"- Bundle preview command template: `{bundle.get('preview_command_template') or 'not available'}`",
                f"- Bundle apply command template: `{bundle.get('apply_command_template') or 'not available'}`",
                f"- Bundle result trigger: {bundle.get('result_collection_trigger')}",
            ])
        result_handoff = card.get("result_handoff") or {}
        if result_handoff:
            lines.extend([
                f"- Result handoff: `{result_handoff.get('status')}` via `{result_handoff.get('source_report')}`",
                f"- Result handoff reason: {result_handoff.get('reason')}",
                f"- First measurement due: **{result_handoff.get('first_measurement_due_after_hours')} hours after URL logging**",
            ])
        if card.get("after_posting_checklist"):
            lines.append("- After posting checklist:")
            for item in card["after_posting_checklist"]:
                lines.append(f"  - {item}")
    lines.extend([
        "",
        "## Operator Steps",
    ])
    lines.extend(f"- {item}" for item in payload["operator_steps"])
    lines.extend([
        "",
        "## Guardrails",
    ])
    lines.extend(f"- {item}" for item in payload["guardrails"])
    lines.append("")
    return "\n".join(lines)


def sync_admin(payload: dict, markdown: str) -> None:
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    html = replace_json_embed(html, "embedded-manual-posting-clipboard", payload)
    html = replace_text_embed(html, "embedded-manual-posting-clipboard-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    payload = build_payload()
    write_paste_files(payload["post_cards"])
    write_session_file(payload)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(payload)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(payload, markdown)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), **payload["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
