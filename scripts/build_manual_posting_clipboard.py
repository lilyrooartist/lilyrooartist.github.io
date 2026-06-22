#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUAL_DISTRIBUTION = ROOT / "data" / "manual_distribution_packet.json"
YOUTUBE_RECONCILIATION = ROOT / "data" / "youtube_community_url_reconciliation.json"
PASTE_CARD_DIR = ROOT / "data" / "manual-posting-cards"
OUT = ROOT / "data" / "manual_posting_clipboard.json"
REPORT = ROOT / "admin" / "reports" / "manual-posting-clipboard.md"
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


def slug(value: str) -> str:
    slugged = re.sub(r"[^A-Za-z0-9_-]+", "-", value.strip()).strip("-").lower()
    return slugged or "manual-post"


def post_card(row: dict) -> dict:
    posting = row.get("manual_posting_packet") or {}
    log_effect = row.get("log_effect") or {}
    post_id = row.get("id") or ""
    paste_text_path = PASTE_CARD_DIR / f"{slug(post_id)}.txt"
    return {
        "id": post_id,
        "release": row.get("release") or "",
        "platform": row.get("platform") or "",
        "status": row.get("distribution_status") or "",
        "posting_surface": posting.get("posting_surface") or "YouTube Studio Community",
        "public_community_url": posting.get("public_community_url") or "",
        "paste_text": posting.get("paste_text") or row.get("copy_block") or "",
        "paste_text_path": str(paste_text_path.relative_to(ROOT)),
        "asset_url": posting.get("asset_url") or row.get("asset_download_url") or "",
        "asset_status": (row.get("asset_audit") or {}).get("status") or "",
        "asset_local_path": (row.get("asset_audit") or {}).get("local_path") or "",
        "destination_links": row.get("destination_links") or [],
        "destination_link_audit": row.get("destination_link_audit") or [],
        "selected_cta_strength": row.get("selected_cta_strength") or "",
        "postable_now": bool(posting.get("postable_now")),
        "logging_required": bool(posting.get("logging_required")),
        "public_url": row.get("published_url") or "",
        "public_url_placeholder": log_effect.get("url_placeholder") or "PUBLIC_URL",
        "log_preview_command": row.get("log_preview_command") or "",
        "log_apply_command": row.get("log_apply_command") or "",
        "log_notes": log_effect.get("notes") or "",
        "completion_evidence": [
            "A real public YouTube Community post URL exists.",
            "The URL is logged with scripts/log_manual_distribution.py.",
            "admin/content/Published_Log.csv contains this manual_distribution_id.",
        ],
    }


def build_payload() -> dict:
    packet = read_json(MANUAL_DISTRIBUTION, {})
    reconciliation = read_json(YOUTUBE_RECONCILIATION, {})
    reconciliation_summary = reconciliation.get("summary") or {}
    distribution = packet.get("manual_distribution_docket") or {}
    completion = packet.get("manual_completion_manifest") or {}
    postable_rows = [
        row
        for row in packet.get("rows") or []
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
    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "manual_distribution_packet": str(MANUAL_DISTRIBUTION.relative_to(ROOT)),
            "manual_distribution_url_template": completion.get("url_template_path") or "",
            "youtube_community_url_reconciliation": str(YOUTUBE_RECONCILIATION.relative_to(ROOT)) if YOUTUBE_RECONCILIATION.exists() else "",
            "published_log_target": "admin/content/Published_Log.csv",
        },
        "summary": {
            "status": "ready_to_post" if cards else "empty",
            "posting_surface": completion.get("posting_surface") or "YouTube Studio Community",
            "public_community_url": completion.get("public_community_url") or distribution.get("public_community_url") or "",
            "postable_count": len(cards),
            "waiting_public_url_count": completion.get("waiting_public_url_count") or len(cards),
            "pending_log_ids": completion.get("pending_log_ids") or [card["id"] for card in cards],
            "url_template_path": completion.get("url_template_path") or "",
            "paste_text_dir": str(PASTE_CARD_DIR.relative_to(ROOT)),
            "paste_text_file_count": len(paste_text_files),
            "paste_text_files": paste_text_files,
            "batch_log_preview_command": completion.get("batch_log_preview_command") or "",
            "batch_log_apply_command": completion.get("batch_log_apply_command") or "",
            "batch_log_partial_apply_command": partial_apply_command,
            "public_url_reconciliation_status": reconciliation_summary.get("status") or "not_run",
            "public_url_reconciliation_match_count": reconciliation_summary.get("match_count") or 0,
            "public_url_reconciliation_command": "python3 scripts/reconcile_youtube_community_urls.py",
            "public_url_reconciliation_apply_command": reconciliation_summary.get("apply_command") or "",
            "next_action": (
                "Post each card in YouTube Community, copy the real public URL, then log it."
                if cards
                else "No approved manual posts are currently waiting."
            ),
        },
        "post_cards": cards,
        "operator_steps": [
            "Open the YouTube Community surface.",
            "For each card, paste the text exactly as shown.",
            "Attach the listed asset URL or download/open the local asset path if needed.",
            "Publish manually in YouTube Studio Community.",
            "Copy the real public post URL.",
            "Run the preview logging command with the real URL, then run the apply command.",
            "Or rerun the public URL reconciliation command after posting to auto-detect confident public URLs.",
            "If only one public URL is ready, use the partial batch apply command so that post can start accumulating measurable evidence immediately.",
        ],
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


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
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
        f"- Paste text files: `{summary.get('paste_text_dir') or 'not available'}` ({summary.get('paste_text_file_count', 0)} file(s))",
        f"- Batch log preview: `{summary.get('batch_log_preview_command') or 'not available'}`",
        f"- Batch log apply after posting: `{summary.get('batch_log_apply_command') or 'not available'}`",
        f"- Partial batch apply after first URL: `{summary.get('batch_log_partial_apply_command') or 'not available'}`",
        f"- Public URL reconciliation: `{summary.get('public_url_reconciliation_command') or 'not available'}`",
        f"- Reconciliation status: **{summary.get('public_url_reconciliation_status')}** ({summary.get('public_url_reconciliation_match_count')} match(es))",
        f"- Reconciliation apply if matches exist: `{summary.get('public_url_reconciliation_apply_command') or 'not available'}`",
        f"- Next action: {summary['next_action']}",
        "",
        "## Cards",
    ]
    if not payload["post_cards"]:
        lines.append("- No approved manual posts are currently waiting.")
    for index, card in enumerate(payload["post_cards"], start=1):
        lines.extend([
            f"### {index}. {card['release']} - {card['platform']}",
            f"- ID: `{card['id']}`",
            f"- Status: `{card['status']}`",
            f"- Open: {card.get('public_community_url') or 'not set'}",
            f"- Paste file: `{card.get('paste_text_path') or 'not available'}`",
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
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(payload)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(payload, markdown)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), **payload["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
