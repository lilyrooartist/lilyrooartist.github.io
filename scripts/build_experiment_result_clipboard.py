#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PACKET = ROOT / "data" / "experiment_result_collection_packet.json"
MANUAL_POSTING = ROOT / "data" / "manual_posting_clipboard.json"
PLATFORM_REPAIR = ROOT / "data" / "platform_repair_status.json"
OUT = ROOT / "data" / "experiment_result_clipboard.json"
REPORT = ROOT / "admin" / "reports" / "experiment-result-clipboard.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"
RESULT_FIELDS = ["views", "likes", "comments", "shares", "saves", "subs_delta"]
DEFAULT_FIRST_MEASUREMENT_DUE_AFTER_HOURS = 24


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


def evidence_sources(platform: str, post_url: str) -> list[dict]:
    platform_lower = platform.lower()
    sources = []
    if post_url:
        sources.append({
            "label": "Logged public post",
            "url": post_url,
            "instruction": "Open the public post to confirm the URL and visible engagement before entering metrics.",
        })
    if platform_lower == "x":
        sources.append({
            "label": "X Analytics",
            "url": "https://analytics.x.com/",
            "instruction": "Use the logged post URL or post ID to find the post and copy visible analytics values.",
        })
    elif platform_lower == "facebook":
        sources.append({
            "label": "Meta Business Suite",
            "url": "https://business.facebook.com/latest/insights",
            "instruction": "Open post insights for the Lily Roo page post and copy the available result values.",
        })
    elif platform_lower == "instagram":
        sources.append({
            "label": "Instagram Insights",
            "url": "https://business.facebook.com/latest/insights",
            "instruction": "Open Instagram content insights and copy values only for the matching post.",
        })
    elif platform_lower == "tiktok":
        sources.append({
            "label": "TikTok Studio analytics",
            "url": "https://www.tiktok.com/creator-center/analytics",
            "instruction": "Open the post in TikTok Studio analytics and copy values only after the public URL is logged.",
        })
    elif "youtube" in platform_lower:
        sources.append({
            "label": "YouTube Studio analytics",
            "url": "https://studio.youtube.com/",
            "instruction": "Open the matching Community post analytics and copy available public-performance values.",
        })
    return sources


def metric_cards(rows: list[dict], wide_rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row.get("post_id") or "", row.get("source_row") or "")].append(row)
    wide_by_key = {
        (row.get("post_id") or "", row.get("source_row") or ""): row
        for row in wide_rows
    }
    cards = []
    for (post_id, source_row), group_rows in sorted(grouped.items(), key=lambda item: (item[1][0].get("published_date") or "", item[0][0])):
        first = group_rows[0]
        wide_row = wide_by_key.get((post_id, source_row)) or {}
        ready_fields = [
            row.get("field") or ""
            for row in group_rows
            if str(row.get("new_value") or "").strip() and str(row.get("evidence_note") or "").strip()
        ]
        wide_ready_fields = [
            field
            for field in RESULT_FIELDS
            if str(wide_row.get(field) or "").strip() and str(wide_row.get("evidence_note") or "").strip()
        ]
        pending_fields = [
            row.get("field") or ""
            for row in group_rows
            if not (str(row.get("new_value") or "").strip() and str(row.get("evidence_note") or "").strip())
        ]
        cards.append({
            "post_id": post_id,
            "experiment_format": first.get("experiment_format") or "",
            "platform": first.get("platform") or "",
            "song": first.get("song") or "",
            "post_url": first.get("post_url") or "",
            "published_date": first.get("published_date") or "",
            "source_row": source_row,
            "pending_field_count": len(pending_fields),
            "ready_field_count": len(ready_fields),
            "wide_ready_field_count": len(wide_ready_fields),
            "pending_fields": pending_fields,
            "ready_fields": ready_fields,
            "wide_ready_fields": wide_ready_fields,
            "wide_entry_row": {
                "experiment_format": first.get("experiment_format") or "",
                "post_id": post_id,
                "platform": first.get("platform") or "",
                "song": first.get("song") or "",
                "post_url": first.get("post_url") or "",
                "published_date": first.get("published_date") or "",
                "source_row": source_row,
                **{field: str(wide_row.get(field) or next((row.get("new_value") or "" for row in group_rows if row.get("field") == field), "")).strip() for field in RESULT_FIELDS},
                "evidence_note": str(wide_row.get("evidence_note") or next((row.get("evidence_note") or "" for row in group_rows if row.get("evidence_note")), "")).strip(),
            },
            "wide_entry_instruction": "Fill one wide entry CSV row in data/experiment_result_entry_wide_template.csv for this post; keep unknown metrics blank and include one evidence_note.",
            "evidence_sources": evidence_sources(first.get("platform") or "", first.get("post_url") or ""),
            "collection_checklist": [
                "Open the logged public post and confirm it matches this post_id.",
                "Open the platform analytics or insights source listed for this card.",
                "Copy only numeric values that are visible in the source.",
                "Enter values in the wide entry CSV row for this post_id and source_row.",
                "Add an evidence_note with source and collection date before import preview.",
            ],
            "fields": [
                {
                    "field": row.get("field") or "",
                    "new_value": row.get("new_value") or "",
                    "evidence_note": row.get("evidence_note") or "",
                    "collection_hint": row.get("collection_hint") or "",
                }
                for row in group_rows
            ],
        })
    return cards


def missing_log_cards(rows: list[dict]) -> list[dict]:
    return [
        {
            "post_id": row.get("post_id") or "",
            "experiment_format": row.get("experiment_format") or "",
            "platform": row.get("platform") or "",
            "song": row.get("song") or "",
            "status": row.get("status") or "not_in_published_log",
            "next_action": row.get("next_action") or "Publish or log the public URL before metrics can be collected.",
        }
        for row in rows
    ]


def measurement_priority_cards(metric_cards: list[dict], missing_cards: list[dict], manual_posting: dict, platform_repair: dict) -> list[dict]:
    priority = []
    format_counts: dict[str, dict] = defaultdict(lambda: {"measurable": 0, "missing": 0})
    postable_manual_ids = {
        card.get("id") or ""
        for card in manual_posting.get("post_cards") or []
        if card.get("postable_now")
    }
    manual_cards_by_id = {
        card.get("id") or "": card
        for card in manual_posting.get("post_cards") or []
    }
    blocked_ids = {
        row.get("post_id") or ""
        for row in platform_repair.get("rows") or []
        if row.get("post_id")
    }
    for card in metric_cards:
        format_counts[card.get("experiment_format") or "Unknown format"]["measurable"] += 1
    for card in missing_cards:
        format_counts[card.get("experiment_format") or "Unknown format"]["missing"] += 1
    for card in metric_cards:
        fmt = card.get("experiment_format") or "Unknown format"
        counts = format_counts[fmt]
        primary_field = next(iter(card.get("pending_fields") or []), "views")
        primary_arg = primary_field.replace("_", "-")
        base_direct_command = (
            f"python3 scripts/update_experiment_results.py --post-id {card.get('post_id') or 'POST_ID'} "
            f"--source-row {card.get('source_row') or 'SOURCE_ROW'} --{primary_arg} VALUE "
            "--evidence-note 'SOURCE analytics YYYY-MM-DD'"
        )
        direct_preview_command = (
            f"{base_direct_command} --dry-run"
        )
        direct_apply_command = (
            f"{base_direct_command} --apply --refresh-admin"
        )
        priority.append({
            "action": "collect_metrics",
            "priority": 1,
            "post_id": card.get("post_id") or "",
            "platform": card.get("platform") or "",
            "song": card.get("song") or "",
            "experiment_format": fmt,
            "post_url": card.get("post_url") or "",
            "source_row": card.get("source_row") or "",
            "pending_fields": card.get("pending_fields") or [],
            "direct_preview_command_template": direct_preview_command,
            "direct_apply_command_template": direct_apply_command,
            "reason": (
                f"Already published and logged; measuring it reduces the {fmt} evidence gap. "
                f"{counts['measurable']} logged post(s), {counts['missing']} missing URL(s) in this format."
            ),
        })
    for card in missing_cards:
        fmt = card.get("experiment_format") or "Unknown format"
        counts = format_counts[fmt]
        post_id = card.get("post_id") or ""
        platform = card.get("platform") or ""
        if post_id in postable_manual_ids:
            action = "post_and_log_public_url"
            priority_value = 2
            reason_prefix = "Postable now in the Manual Posting Clipboard; publish it and log the public URL so metrics can start."
        elif post_id in blocked_ids or platform.lower() in {"tiktok", "instagram"}:
            action = "clear_platform_blocker"
            priority_value = 4
            reason_prefix = "Platform work is blocked; clear the platform repair gate before URL logging can produce metrics."
        else:
            action = "log_public_url"
            priority_value = 3
            reason_prefix = "Cannot collect metrics until the public URL is logged."
        manual_card = manual_cards_by_id.get(post_id) or {}
        priority.append({
            "action": action,
            "priority": priority_value,
            "post_id": post_id,
            "platform": platform,
            "song": card.get("song") or "",
            "experiment_format": fmt,
            "post_url": "",
            "source_row": "",
            "pending_fields": [],
            "direct_preview_command_template": "",
            "direct_apply_command_template": "",
            "manual_posting_report": "admin/reports/manual-posting-clipboard.md" if manual_card else "",
            "public_community_url": manual_card.get("public_community_url") or "",
            "paste_text_path": manual_card.get("paste_text_path") or "",
            "log_preview_command": manual_card.get("log_preview_command") or "",
            "log_apply_command": manual_card.get("log_apply_command") or "",
            "reason": (
                f"{reason_prefix} "
                f"{counts['measurable']} logged post(s), {counts['missing']} missing URL(s) in this format."
            ),
        })
    priority.sort(key=lambda item: (item["priority"], item["experiment_format"], item["platform"], item["post_id"]))
    selected = []
    selected_keys = set()
    covered_formats = set()
    for item in priority:
        fmt = item.get("experiment_format") or "Unknown format"
        key = (item.get("action"), item.get("post_id"), fmt)
        if fmt in covered_formats:
            continue
        selected.append(item)
        selected_keys.add(key)
        covered_formats.add(fmt)
    for item in priority:
        if len(selected) >= 12:
            break
        key = (item.get("action"), item.get("post_id"), item.get("experiment_format") or "Unknown format")
        if key in selected_keys:
            continue
        selected.append(item)
        selected_keys.add(key)
    selected.sort(key=lambda item: (item["priority"], item["experiment_format"], item["platform"], item["post_id"]))
    return selected


def post_log_measurement_handoff(manual_posting: dict, summary: dict, missing_cards: list[dict]) -> dict:
    session = manual_posting.get("session_manifest") or {}
    session_rows = session.get("rows") or []
    default_due_after_hours = session.get("first_measurement_due_after_hours") or DEFAULT_FIRST_MEASUREMENT_DUE_AFTER_HOURS
    format_by_post_id = {
        card.get("post_id") or "": card.get("experiment_format") or ""
        for card in missing_cards
        if card.get("post_id")
    }
    handoff_rows = []
    for row in session_rows:
        post_id = row.get("id") or ""
        platform = row.get("platform") or "YouTube Community"
        release = row.get("release") or ""
        experiment_format = format_by_post_id.get(post_id) or "Unknown format"
        due_after_hours = row.get("first_measurement_due_after_hours") or default_due_after_hours
        handoff_rows.append({
            "sequence": row.get("sequence"),
            "post_id": post_id,
            "platform": platform,
            "song": release,
            "experiment_format": experiment_format,
            "status": "waiting_for_public_url",
            "public_url": row.get("public_url") or "PUBLIC_URL",
            "source_row": "after Published_Log.csv append",
            "fields_to_collect": RESULT_FIELDS,
            "first_measurement_due_after_hours": due_after_hours,
            "first_measurement_timing": f"Collect first visible metrics {due_after_hours} hours after the public URL is logged.",
            "wide_entry_template": {
                "experiment_format": experiment_format,
                "post_id": post_id,
                "platform": platform,
                "song": release,
                "post_url": "PUBLIC_URL",
                "published_date": "YYYY-MM-DD",
                "source_row": "PUBLISHED_LOG_ROW",
                **{field: "" for field in RESULT_FIELDS},
                "evidence_note": "YouTube Studio Community analytics YYYY-MM-DD",
            },
            "evidence_sources": evidence_sources(platform, "PUBLIC_URL"),
            "preview_after_logging": summary.get("wide_result_import_preview_command") or "",
            "apply_after_logging": summary.get("wide_result_import_apply_command") or "",
            "manual_posting_report": "admin/reports/manual-posting-clipboard.md",
            "log_preview_command": row.get("preview_command_template") or "",
            "log_apply_command": row.get("apply_command_template") or "",
        })
    return {
        "status": "waiting_for_public_urls" if handoff_rows else "clear",
        "source_session": session.get("session_name") or "",
        "manual_posting_report": "admin/reports/manual-posting-clipboard.md",
        "entry_csv_path": summary.get("entry_csv_path") or "",
        "wide_entry_csv_path": summary.get("wide_entry_csv_path") or "",
        "field_count_per_post": len(RESULT_FIELDS),
        "first_measurement_due_after_hours": default_due_after_hours,
        "handoff_row_count": len(handoff_rows),
        "pending_post_ids": [row.get("post_id") for row in handoff_rows],
        "wide_import_preview_command": summary.get("wide_result_import_preview_command") or "",
        "wide_import_apply_command": summary.get("wide_result_import_apply_command") or "",
        "rows": handoff_rows,
        "handoff_sequence": [
            "Post each manual-session card and log the real public URL.",
            "Refresh Admin so Published_Log.csv rows become experiment result cards.",
            f"Collect first visible metrics from YouTube Studio Community analytics {default_due_after_hours} hours after URL logging.",
            "Fill one wide entry CSV row per logged Community post.",
            "Run the wide result import preview before applying metrics.",
        ],
        "completion_evidence": [
            "Published_Log.csv contains the manual-session post URL.",
            "data/experiment_result_clipboard.json shows the post as a metric card instead of a missing-public-url card.",
            "data/experiment_result_entry_wide_template.csv has first-measurement values plus evidence_note for the post.",
            "The wide import preview reports only the intended metric updates.",
        ],
        "guardrail": "This handoff is a template; do not import metrics until a real public URL and source_row exist.",
    }


def first_measurement_runbook(priority_cards: list[dict], cards: list[dict], summary: dict) -> dict:
    first_priority = next((item for item in priority_cards if item.get("action") == "collect_metrics"), {})
    if not first_priority:
        return {
            "status": "clear",
            "post_id": "",
            "next_action": "No published experiment result card is waiting for values.",
            "guardrail": "Do not invent metric values.",
        }
    card_by_id = {card.get("post_id") or "": card for card in cards}
    card = card_by_id.get(first_priority.get("post_id") or "") or {}
    pending_fields = card.get("pending_fields") or first_priority.get("pending_fields") or []
    return {
        "status": "ready_to_collect_metrics",
        "post_id": first_priority.get("post_id") or "",
        "platform": first_priority.get("platform") or "",
        "song": first_priority.get("song") or card.get("song") or "",
        "experiment_format": first_priority.get("experiment_format") or card.get("experiment_format") or "",
        "post_url": first_priority.get("post_url") or card.get("post_url") or "",
        "source_row": first_priority.get("source_row") or card.get("source_row") or "",
        "pending_fields": pending_fields,
        "wide_entry_csv_path": summary.get("wide_entry_csv_path") or "data/experiment_result_entry_wide_template.csv",
        "entry_csv_path": summary.get("entry_csv_path") or "data/experiment_result_entry_template.csv",
        "direct_preview_command_template": first_priority.get("direct_preview_command_template") or "",
        "direct_apply_command_template": first_priority.get("direct_apply_command_template") or "",
        "wide_import_preview_command": summary.get("wide_result_import_preview_command") or "",
        "wide_import_apply_command": summary.get("wide_result_import_apply_command") or "",
        "evidence_note_template": f"{first_priority.get('platform') or card.get('platform') or 'Platform'} analytics YYYY-MM-DD",
        "wide_entry_instruction": (
            "Fill only visible numeric values for this post in the wide entry CSV; "
            "leave unknown fields blank and include one evidence_note."
        ),
        "evidence_sources": card.get("evidence_sources") or evidence_sources(first_priority.get("platform") or "", first_priority.get("post_url") or ""),
        "collection_checklist": [
            "Open the logged public post and confirm it matches this post_id.",
            "Open the listed platform analytics or insights source.",
            "Copy only visible numeric values for pending_fields.",
            "Enter the values and evidence_note in the wide entry CSV row for this post_id and source_row.",
            "Run the direct preview command for the first filled field, or the wide import preview for the filled worksheet.",
            "Apply only after preview shows the intended Published_Log.csv update.",
        ],
        "completion_evidence": [
            "The wide entry CSV has at least one numeric value for this post_id plus an evidence_note.",
            "The dry-run preview reports only this post/source_row or the intended worksheet rows.",
            "Published_Log.csv contains the imported result values and result_evidence notes after apply.",
            "The growth dashboard refreshes with a lower pending_result_field_count.",
        ],
        "why": first_priority.get("reason") or "This is the top published/logged post that can improve repeatable-format evidence.",
        "guardrail": "Do not guess metrics; leave unknown values blank and never apply without an evidence_note.",
    }


def build_payload() -> dict:
    packet = read_json(RESULT_PACKET, {})
    manual_posting = read_json(MANUAL_POSTING, {})
    platform_repair = read_json(PLATFORM_REPAIR, {})
    summary = packet.get("summary") or {}
    cards = metric_cards(packet.get("pending_result_rows") or [], packet.get("wide_entry_rows") or [])
    missing_cards = missing_log_cards(packet.get("missing_published_log_posts") or [])
    priority_cards = measurement_priority_cards(cards, missing_cards, manual_posting, platform_repair)
    handoff = post_log_measurement_handoff(manual_posting, summary, missing_cards)
    runbook = first_measurement_runbook(priority_cards, cards, summary)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "experiment_result_collection_packet": str(RESULT_PACKET.relative_to(ROOT)),
            "manual_posting_clipboard": str(MANUAL_POSTING.relative_to(ROOT)),
            "platform_repair_status": str(PLATFORM_REPAIR.relative_to(ROOT)),
            "entry_csv_path": summary.get("entry_csv_path") or "",
            "wide_entry_csv_path": summary.get("wide_entry_csv_path") or "",
        },
        "summary": {
            "status": "needs_values" if cards else ("needs_public_urls" if missing_cards else "clear"),
            "metric_card_count": len(cards),
            "missing_public_url_count": len(missing_cards),
            "measurement_priority_count": len(priority_cards),
            "post_log_measurement_handoff_count": handoff.get("handoff_row_count") or 0,
            "pending_result_field_count": summary.get("pending_result_field_count") or 0,
            "ready_to_import_count": summary.get("ready_to_import_count") or 0,
            "wide_ready_to_import_count": summary.get("wide_ready_to_import_count") or 0,
            "entry_csv_path": summary.get("entry_csv_path") or "",
            "wide_entry_csv_path": summary.get("wide_entry_csv_path") or "",
            "report_path": str(REPORT.relative_to(ROOT)),
            "result_import_preview_command": summary.get("result_import_preview_command") or "",
            "wide_result_import_preview_command": summary.get("wide_result_import_preview_command") or "",
            "result_import_apply_command": summary.get("result_import_apply_command") or "",
            "wide_result_import_apply_command": summary.get("wide_result_import_apply_command") or "",
            "apply_gate": summary.get("apply_gate") or "",
        },
        "metric_cards": cards,
        "missing_public_url_cards": missing_cards,
        "measurement_priority_cards": priority_cards,
        "first_measurement_runbook": runbook,
        "post_log_measurement_handoff": handoff,
        "operator_steps": [
            "Open each post URL or platform analytics surface.",
            "Start with the first-measurement runbook when it is ready.",
            "Start with measurement_priority_cards; they are ordered to unlock repeatable-format evidence fastest.",
            "Preferred: fill one row per post in the wide entry CSV, including evidence_note.",
            "Alternative: fill new_value and evidence_note for every pending field in the long entry CSV.",
            "Leave unknown values blank; do not guess metrics.",
            "Run the result import preview command.",
            "Apply only after preview confirms the intended rows.",
        ],
        "guardrails": [
            "This clipboard does not fetch private analytics or write metrics.",
            "Do not use guessed result values.",
            "Posts without public URLs must be published or logged before result metrics can be collected.",
            "The post-log measurement handoff is only usable after real public URLs are logged.",
        ],
    }


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    runbook = payload.get("first_measurement_runbook") or {}
    lines = [
        "# Experiment Result Clipboard - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Status: **{summary['status']}**",
        f"- Metric cards: **{summary['metric_card_count']}**",
        f"- Missing public URLs: **{summary['missing_public_url_count']}**",
        f"- Measurement priorities: **{summary.get('measurement_priority_count') or 0}**",
        f"- Post-log handoff rows: **{summary.get('post_log_measurement_handoff_count') or 0}**",
        f"- Pending result fields: **{summary['pending_result_field_count']}**",
        f"- Ready to import: **{summary['ready_to_import_count']}**",
        f"- Wide rows ready to import: **{summary.get('wide_ready_to_import_count') or 0}**",
        f"- Entry CSV: `{summary.get('entry_csv_path') or 'not available'}`",
        f"- Wide entry CSV: `{summary.get('wide_entry_csv_path') or 'not available'}`",
        f"- Preview import: `{summary.get('result_import_preview_command') or 'not available'}`",
        f"- Preview wide import: `{summary.get('wide_result_import_preview_command') or 'not available'}`",
        f"- Apply after review: `{summary.get('result_import_apply_command') or 'blocked until values/evidence are filled'}`",
        "",
        "## First Measurement Runbook",
        f"- Status: **{runbook.get('status', 'unknown')}**",
        f"- Post: `{runbook.get('post_id') or 'not available'}` {runbook.get('platform') or ''} / {runbook.get('experiment_format') or 'unknown format'}",
        f"- URL: {runbook.get('post_url') or 'not logged'}",
        f"- Published_Log row: `{runbook.get('source_row') or 'not available'}`",
        f"- Pending fields: `{', '.join(runbook.get('pending_fields') or []) or 'none'}`",
        f"- Wide entry CSV: `{runbook.get('wide_entry_csv_path') or 'not available'}`",
        f"- Evidence note template: `{runbook.get('evidence_note_template') or 'SOURCE analytics YYYY-MM-DD'}`",
        f"- Direct preview template: `{runbook.get('direct_preview_command_template') or 'not available'}`",
        f"- Direct apply template: `{runbook.get('direct_apply_command_template') or 'not available'}`",
        f"- Wide import preview: `{runbook.get('wide_import_preview_command') or 'not available'}`",
        f"- Why: {runbook.get('why') or 'not available'}",
        f"- Guardrail: {runbook.get('guardrail') or 'Do not guess metrics.'}",
    ]
    if runbook.get("evidence_sources"):
        lines.append("- Evidence sources:")
        for source in runbook["evidence_sources"]:
            lines.append(f"  - {source.get('label')}: {source.get('url')} - {source.get('instruction')}")
    if runbook.get("collection_checklist"):
        lines.append("- Checklist:")
        for item in runbook["collection_checklist"]:
            lines.append(f"  - {item}")
    if runbook.get("completion_evidence"):
        lines.append("- Completion evidence:")
        for item in runbook["completion_evidence"]:
            lines.append(f"  - {item}")
    lines.extend([
        "",
        "## Metric Cards",
    ])
    if not payload["metric_cards"]:
        lines.append("- No published experiment posts are waiting for metric values.")
    for card in payload["metric_cards"]:
        lines.extend([
            f"### {card['platform']} - {card['song']} (`{card['post_id']}`)",
            f"- Format: {card['experiment_format']}",
            f"- URL: {card['post_url'] or 'not logged'}",
            f"- Published: {card['published_date'] or 'unknown'}; Published_Log row: `{card['source_row']}`",
            f"- Pending fields: `{', '.join(card['pending_fields']) or 'none'}`",
            f"- Wide-ready fields: `{', '.join(card.get('wide_ready_fields') or []) or 'none'}`",
            f"- Wide entry instruction: {card.get('wide_entry_instruction')}",
        ])
        wide_entry = card.get("wide_entry_row") or {}
        if wide_entry:
            fillable = ", ".join(field for field in RESULT_FIELDS if field in card.get("pending_fields", []))
            lines.append(f"- Wide CSV target: post_id `{wide_entry.get('post_id')}`, source_row `{wide_entry.get('source_row')}`, fill `{fillable or 'none'}`.")
        if card.get("evidence_sources"):
            lines.append("- Evidence sources:")
            for source in card["evidence_sources"]:
                lines.append(f"  - {source.get('label')}: {source.get('url')} - {source.get('instruction')}")
        if card.get("collection_checklist"):
            lines.append("- Collection checklist:")
            for item in card["collection_checklist"]:
                lines.append(f"  - {item}")
        for field in card["fields"]:
            lines.append(f"  - `{field['field']}`: {field['collection_hint']}")
    lines.extend(["", "## Measurement Priorities"])
    if not payload["measurement_priority_cards"]:
        lines.append("- None.")
    for item in payload["measurement_priority_cards"]:
        action_labels = {
            "collect_metrics": "Collect metrics",
            "post_and_log_public_url": "Post and log public URL",
            "log_public_url": "Log public URL",
            "clear_platform_blocker": "Clear platform blocker",
        }
        action = action_labels.get(item["action"], item["action"])
        lines.append(f"- **{action}** `{item['post_id']}` {item['platform']} / {item['experiment_format']}: {item['reason']}")
        if item.get("direct_preview_command_template"):
            lines.append(f"  - Direct preview template: `{item['direct_preview_command_template']}`")
        if item.get("direct_apply_command_template"):
            lines.append(f"  - Direct apply template: `{item['direct_apply_command_template']}`")
        if item.get("paste_text_path"):
            lines.append(f"  - Paste file: `{item['paste_text_path']}`")
        if item.get("public_community_url"):
            lines.append(f"  - Community surface: {item['public_community_url']}")
        if item.get("log_preview_command"):
            lines.append(f"  - Log preview after posting: `{item['log_preview_command']}`")
        if item.get("log_apply_command"):
            lines.append(f"  - Log apply after posting: `{item['log_apply_command']}`")
    handoff = payload.get("post_log_measurement_handoff") or {}
    lines.extend(["", "## Post-Log Measurement Handoff"])
    lines.append(f"- Status: **{handoff.get('status', 'unknown')}**")
    lines.append(f"- Source session: {handoff.get('source_session') or 'not available'}")
    lines.append(f"- Manual posting report: `{handoff.get('manual_posting_report') or 'not available'}`")
    lines.append(f"- Wide entry CSV after URL logging: `{handoff.get('wide_entry_csv_path') or 'not available'}`")
    lines.append(f"- Wide import preview after logging: `{handoff.get('wide_import_preview_command') or 'not available'}`")
    lines.append(f"- First measurement due: **{handoff.get('first_measurement_due_after_hours') or DEFAULT_FIRST_MEASUREMENT_DUE_AFTER_HOURS} hours after URL logging**")
    lines.append(f"- Guardrail: {handoff.get('guardrail') or 'Wait for real public URLs.'}")
    if handoff.get("handoff_sequence"):
        lines.append("- Handoff sequence:")
        for item in handoff["handoff_sequence"]:
            lines.append(f"  - {item}")
    lines.append("- Handoff rows:")
    if not handoff.get("rows"):
        lines.append("  - None.")
    for row in handoff.get("rows") or []:
        lines.append(f"  - `{row.get('sequence')}` `{row.get('post_id')}` {row.get('platform')} - collect `{', '.join(row.get('fields_to_collect') or [])}` {row.get('first_measurement_due_after_hours')}h after `{row.get('public_url')}` is real.")
        if row.get("first_measurement_timing"):
            lines.append(f"    - Timing: {row['first_measurement_timing']}")
        if row.get("log_preview_command"):
            lines.append(f"    - Log preview: `{row['log_preview_command']}`")
    if handoff.get("completion_evidence"):
        lines.append("- Completion evidence:")
        for item in handoff["completion_evidence"]:
            lines.append(f"  - {item}")
    lines.extend(["", "## Missing Public URLs"])
    if not payload["missing_public_url_cards"]:
        lines.append("- None.")
    for card in payload["missing_public_url_cards"]:
        lines.append(f"- `{card['post_id']}` {card['platform']} / {card['experiment_format']}: {card['next_action']}")
    lines.extend(["", "## Guardrails"])
    lines.extend(f"- {item}" for item in payload["guardrails"])
    lines.append("")
    return "\n".join(lines)


def sync_admin(payload: dict, markdown: str) -> None:
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    html = replace_json_embed(html, "embedded-experiment-result-clipboard", payload)
    html = replace_text_embed(html, "embedded-experiment-result-clipboard-report", markdown)
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
