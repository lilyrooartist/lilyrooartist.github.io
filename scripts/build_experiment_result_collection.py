#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMO_STATUS = ROOT / "data" / "promo_engine_status.json"
PUBLISHED_LOG = ROOT / "admin" / "content" / "Published_Log.csv"
OUT_JSON = ROOT / "data" / "experiment_result_collection_packet.json"
OUT_CSV = ROOT / "data" / "experiment_result_entry_template.csv"
OUT_WIDE_CSV = ROOT / "data" / "experiment_result_entry_wide_template.csv"
OUT_MD = ROOT / "admin" / "reports" / "experiment-result-collection.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"

RESULT_FIELDS = ["views", "likes", "comments", "shares", "saves", "subs_delta"]


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def existing_entries() -> dict[tuple[str, str, str], dict]:
    entries = {}
    for row in read_csv(OUT_CSV):
        post_id = str(row.get("post_id") or "").strip()
        field = str(row.get("field") or "").strip()
        source_row = str(row.get("source_row") or "").strip()
        if post_id and field and source_row:
            entries[(post_id, field, source_row)] = {
                "new_value": str(row.get("new_value") or "").strip(),
                "evidence_note": str(row.get("evidence_note") or "").strip(),
            }
    return entries


def existing_wide_entries() -> dict[tuple[str, str], dict]:
    entries = {}
    for row in read_csv(OUT_WIDE_CSV):
        post_id = str(row.get("post_id") or "").strip()
        source_row = str(row.get("source_row") or "").strip()
        if post_id and source_row:
            entries[(post_id, source_row)] = {
                **{field: str(row.get(field) or "").strip() for field in RESULT_FIELDS},
                "evidence_note": str(row.get("evidence_note") or "").strip(),
            }
    return entries


def write_csv(rows: list[dict]) -> None:
    fieldnames = [
        "experiment_format",
        "post_id",
        "platform",
        "song",
        "post_url",
        "published_date",
        "field",
        "current_value",
        "new_value",
        "evidence_note",
        "collection_hint",
        "source_row",
    ]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_wide_csv(rows: list[dict], existing: dict[tuple[str, str], dict]) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        key = (str(row.get("post_id") or ""), str(row.get("source_row") or ""))
        grouped.setdefault(key, []).append(row)
    fieldnames = [
        "experiment_format",
        "post_id",
        "platform",
        "song",
        "post_url",
        "published_date",
        "source_row",
        *RESULT_FIELDS,
        "evidence_note",
    ]
    wide_rows = []
    for key, group_rows in sorted(grouped.items(), key=lambda item: (item[1][0].get("published_date") or "", item[0][0])):
        first = group_rows[0]
        existing_row = existing.get(key, {})
        long_notes = [
            f"{row.get('field')}={row.get('evidence_note')}"
            for row in group_rows
            if str(row.get("new_value") or "").strip() and str(row.get("evidence_note") or "").strip()
        ]
        wide_row = {
            "experiment_format": first.get("experiment_format") or "",
            "post_id": first.get("post_id") or "",
            "platform": first.get("platform") or "",
            "song": first.get("song") or "",
            "post_url": first.get("post_url") or "",
            "published_date": first.get("published_date") or "",
            "source_row": first.get("source_row") or "",
            "evidence_note": existing_row.get("evidence_note") or "; ".join(long_notes),
        }
        long_by_field = {row.get("field"): row for row in group_rows}
        for field in RESULT_FIELDS:
            wide_row[field] = existing_row.get(field) or str((long_by_field.get(field) or {}).get("new_value") or "").strip()
        wide_rows.append(wide_row)
    OUT_WIDE_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_WIDE_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(wide_rows)
    return wide_rows


def queue_id(row: dict) -> str:
    content_id = str(row.get("content_id") or "").strip()
    if content_id.startswith("FP-"):
        return content_id
    notes = str(row.get("notes") or "")
    for part in notes.replace(";", " ").split():
        if part.startswith("queue_id="):
            return part.split("=", 1)[1].strip()
    return content_id


def published_lookup(rows: list[dict]) -> dict[str, dict]:
    lookup = {}
    for index, row in enumerate(rows, start=2):
        key = queue_id(row)
        if key:
            enriched = dict(row)
            enriched["_csv_row"] = index
            lookup[key] = enriched
    return lookup


def collection_hint(platform: str, field: str, url: str) -> str:
    platform_lower = platform.lower()
    if platform_lower == "x":
        return f"Open X analytics for {url or 'the post'} and record {field}."
    if platform_lower == "instagram":
        return f"Open Instagram insights for {url or 'the post'} and record {field}."
    if platform_lower == "facebook":
        return f"Open Meta Business Suite for {url or 'the post'} and record {field}."
    if platform_lower == "tiktok":
        return f"Open TikTok Studio analytics for {url or 'the post'} and record {field}."
    if "youtube" in platform_lower:
        return f"Open YouTube Studio analytics for {url or 'the post'} and record {field}."
    return f"Open the platform analytics for {url or 'the post'} and record {field}."


def build_rows(status: dict, published_rows: list[dict], existing: dict[tuple[str, str, str], dict]) -> tuple[list[dict], list[dict], list[str]]:
    growth = ((status.get("kpi") or {}).get("growth_goal") or {})
    experiments = growth.get("active_format_experiments") or []
    published = published_lookup(published_rows)
    rows = []
    missing_posts = []
    published_post_ids = []
    for experiment in experiments:
        experiment_format = experiment.get("format") or ""
        for asset in experiment.get("assets") or []:
            post_id = asset.get("id") or ""
            published_row = published.get(post_id)
            if not published_row:
                missing_posts.append({
                    "experiment_format": experiment_format,
                    "post_id": post_id,
                    "platform": asset.get("platform") or "",
                    "song": asset.get("song") or "",
                    "status": "not_in_published_log",
                    "next_action": "Publish or log the public URL before result metrics can be collected.",
                })
                continue
            published_post_ids.append(post_id)
            post_url = published_row.get("post_id_or_url") or ""
            platform = published_row.get("platform") or asset.get("platform") or ""
            for field in RESULT_FIELDS:
                current = str(published_row.get(field) or "").strip()
                if current:
                    continue
                source_row = str(published_row.get("_csv_row") or "")
                existing_entry = existing.get((post_id, field, source_row), {})
                rows.append({
                    "experiment_format": experiment_format,
                    "post_id": post_id,
                    "platform": platform,
                    "song": published_row.get("song_era") or asset.get("song") or "",
                    "post_url": post_url,
                    "published_date": published_row.get("date") or "",
                    "field": field,
                    "current_value": current,
                    "new_value": existing_entry.get("new_value") or "",
                    "evidence_note": existing_entry.get("evidence_note") or "",
                    "collection_hint": collection_hint(platform, field, post_url),
                    "source_row": source_row,
                })
    return rows, missing_posts, sorted(set(published_post_ids))


def build_markdown(packet: dict) -> str:
    summary = packet["summary"]
    lines = [
        "# Experiment Result Collection - Lily Roo",
        "",
        f"Generated: {packet['generated_at']}",
        "",
        "## Summary",
        f"- Experiment count: **{summary['experiment_count']}**",
        f"- Published experiment posts: **{summary['published_experiment_post_count']}**",
        f"- Missing published log posts: **{summary['missing_published_log_count']}**",
        f"- Pending result fields: **{summary['pending_result_field_count']}**",
        f"- Ready to import: **{summary['ready_to_import_count']}**",
        f"- Entry CSV: `{summary['entry_csv_path']}`",
        f"- Wide entry CSV: `{summary['wide_entry_csv_path']}`",
        "",
        "## Commands",
        f"- Fill `new_value` and `evidence_note` in `{summary['entry_csv_path']}`.",
        f"- Or fill one row per post in `{summary['wide_entry_csv_path']}`.",
        f"- Preview import: `{summary['result_import_preview_command']}`",
        f"- Preview wide import: `{summary['wide_result_import_preview_command']}`",
        f"- Apply after review: `{summary.get('result_import_apply_command') or 'blocked until new_value/evidence_note cells are filled'}`",
        "",
        "## Guardrails",
        "- This packet is review-only; it does not write result metrics into Published_Log.csv.",
        "- Do not log a placeholder URL or guessed metric value.",
        "- Fill only metrics visible in the platform analytics surface.",
        "",
        "## Missing Published Log Rows",
    ]
    missing = packet.get("missing_published_log_posts") or []
    if missing:
        for item in missing:
            lines.append(f"- `{item['post_id']}` ({item['experiment_format']}): {item['next_action']}")
    else:
        lines.append("- None.")
    lines.extend(["", "## Pending Result Fields"])
    rows = packet.get("pending_result_rows") or []
    if rows:
        for row in rows[:25]:
            lines.append(f"- `{row['post_id']}` {row['platform']} `{row['field']}` from row {row['source_row']}: {row['collection_hint']}")
        if len(rows) > 25:
            lines.append(f"- ...and {len(rows) - 25} more rows in `{summary['entry_csv_path']}`.")
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
    html = replace_json_embed(html, "embedded-experiment-result-collection", packet)
    html = replace_text_embed(html, "embedded-experiment-result-collection-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    status = read_json(PROMO_STATUS, {})
    published_rows = read_csv(PUBLISHED_LOG)
    rows, missing_posts, published_post_ids = build_rows(status, published_rows, existing_entries())
    write_csv(rows)
    wide_rows = write_wide_csv(rows, existing_wide_entries())
    experiments = (((status.get("kpi") or {}).get("growth_goal") or {}).get("active_format_experiments") or [])
    ready_rows = [
        row for row in rows
        if str(row.get("new_value") or "").strip() and str(row.get("evidence_note") or "").strip()
    ]
    ready_wide_rows = [
        row for row in wide_rows
        if any(str(row.get(field) or "").strip() for field in RESULT_FIELDS)
        and str(row.get("evidence_note") or "").strip()
    ]
    preview_command = f"python3 scripts/update_experiment_results.py --from-csv {OUT_CSV.relative_to(ROOT)} --dry-run"
    wide_preview_command = f"python3 scripts/update_experiment_results.py --from-wide-csv {OUT_WIDE_CSV.relative_to(ROOT)} --dry-run"
    packet = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "promo_engine_status": str(PROMO_STATUS.relative_to(ROOT)),
            "published_log": str(PUBLISHED_LOG.relative_to(ROOT)),
        },
        "summary": {
            "experiment_count": len(experiments),
            "published_experiment_post_count": len(published_post_ids),
            "missing_published_log_count": len(missing_posts),
            "pending_result_field_count": len(rows),
            "ready_to_import_count": len(ready_rows),
            "wide_ready_to_import_count": len(ready_wide_rows),
            "entry_csv_path": str(OUT_CSV.relative_to(ROOT)),
            "wide_entry_csv_path": str(OUT_WIDE_CSV.relative_to(ROOT)),
            "report_path": str(OUT_MD.relative_to(ROOT)),
            "result_import_preview_command": preview_command,
            "wide_result_import_preview_command": wide_preview_command,
            "result_import_apply_command": (
                f"python3 scripts/update_experiment_results.py --from-csv {OUT_CSV.relative_to(ROOT)} --apply --refresh-admin"
                if ready_rows else ""
            ),
            "wide_result_import_apply_command": (
                f"python3 scripts/update_experiment_results.py --from-wide-csv {OUT_WIDE_CSV.relative_to(ROOT)} --apply --refresh-admin"
                if ready_wide_rows else ""
            ),
            "apply_gate": "ready_rows_available" if ready_rows or ready_wide_rows else "blocked_until_new_values_and_evidence_filled",
        },
        "pending_result_rows": rows,
        "missing_published_log_posts": missing_posts,
        "guardrails": [
            "Review-only packet; no result metrics are written automatically.",
            "Do not log placeholder URLs or guessed metrics.",
            "Fill only values visible in each platform analytics surface.",
        ],
    }
    OUT_JSON.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(packet)
    OUT_MD.write_text(markdown, encoding="utf-8")
    sync_admin(packet, markdown)
    print(json.dumps({"output": str(OUT_JSON.relative_to(ROOT)), **packet["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
