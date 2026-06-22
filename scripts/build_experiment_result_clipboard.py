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


def metric_cards(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row.get("post_id") or "", row.get("source_row") or "")].append(row)
    cards = []
    for (post_id, source_row), group_rows in sorted(grouped.items(), key=lambda item: (item[1][0].get("published_date") or "", item[0][0])):
        first = group_rows[0]
        ready_fields = [
            row.get("field") or ""
            for row in group_rows
            if str(row.get("new_value") or "").strip() and str(row.get("evidence_note") or "").strip()
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
            "pending_fields": pending_fields,
            "ready_fields": ready_fields,
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
            "reason": (
                f"{reason_prefix} "
                f"{counts['measurable']} logged post(s), {counts['missing']} missing URL(s) in this format."
            ),
        })
    priority.sort(key=lambda item: (item["priority"], item["experiment_format"], item["platform"], item["post_id"]))
    return priority[:8]


def build_payload() -> dict:
    packet = read_json(RESULT_PACKET, {})
    manual_posting = read_json(MANUAL_POSTING, {})
    platform_repair = read_json(PLATFORM_REPAIR, {})
    summary = packet.get("summary") or {}
    cards = metric_cards(packet.get("pending_result_rows") or [])
    missing_cards = missing_log_cards(packet.get("missing_published_log_posts") or [])
    priority_cards = measurement_priority_cards(cards, missing_cards, manual_posting, platform_repair)
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
        "operator_steps": [
            "Open each post URL or platform analytics surface.",
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
        ],
    }


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
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
        f"- Pending result fields: **{summary['pending_result_field_count']}**",
        f"- Ready to import: **{summary['ready_to_import_count']}**",
        f"- Entry CSV: `{summary.get('entry_csv_path') or 'not available'}`",
        f"- Wide entry CSV: `{summary.get('wide_entry_csv_path') or 'not available'}`",
        f"- Preview import: `{summary.get('result_import_preview_command') or 'not available'}`",
        f"- Preview wide import: `{summary.get('wide_result_import_preview_command') or 'not available'}`",
        f"- Apply after review: `{summary.get('result_import_apply_command') or 'blocked until values/evidence are filled'}`",
        "",
        "## Metric Cards",
    ]
    if not payload["metric_cards"]:
        lines.append("- No published experiment posts are waiting for metric values.")
    for card in payload["metric_cards"]:
        lines.extend([
            f"### {card['platform']} - {card['song']} (`{card['post_id']}`)",
            f"- Format: {card['experiment_format']}",
            f"- URL: {card['post_url'] or 'not logged'}",
            f"- Published: {card['published_date'] or 'unknown'}; Published_Log row: `{card['source_row']}`",
            f"- Pending fields: `{', '.join(card['pending_fields']) or 'none'}`",
        ])
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
