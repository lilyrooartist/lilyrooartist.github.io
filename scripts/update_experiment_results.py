#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from decimal import Decimal, InvalidOperation
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "data" / "experiment_result_entry_template.csv"
DEFAULT_WIDE_CSV = ROOT / "data" / "experiment_result_entry_wide_template.csv"
PUBLISHED_LOG = ROOT / "admin" / "content" / "Published_Log.csv"

RESULT_FIELDS = {"views", "likes", "comments", "shares", "saves", "subs_delta"}
SIGNED_FIELDS = {"subs_delta"}


def queue_id(row: dict) -> str:
    content_id = str(row.get("content_id") or "").strip()
    if content_id.startswith("FP-"):
        return content_id
    notes = str(row.get("notes") or "")
    for part in notes.replace(";", " ").split():
        if part.startswith("queue_id="):
            return part.split("=", 1)[1].strip()
    return content_id


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    if not path.exists():
        raise SystemExit(f"Missing {relative(path)}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def normalize_result_value(field: str, raw: str) -> str:
    value = str(raw or "").strip().replace(",", "")
    if not value or value.lower() in {"pending", "n/a", "na", "none"}:
        raise SystemExit(f"{field} must be a collected numeric result value, got {raw!r}.")
    try:
        parsed = Decimal(value)
    except InvalidOperation:
        raise SystemExit(f"{field} must be numeric, got {raw!r}.")
    if parsed != parsed.to_integral_value():
        raise SystemExit(f"{field} must be an integer result value, got {raw!r}.")
    if parsed < 0 and field not in SIGNED_FIELDS:
        raise SystemExit(f"{field} must be non-negative, got {raw!r}.")
    return str(int(parsed))


def load_entries(path: Path) -> list[dict]:
    fieldnames, rows = read_csv(path)
    required = {"post_id", "field", "new_value", "evidence_note", "source_row"}
    missing = required - set(fieldnames)
    if missing:
        raise SystemExit(f"{relative(path)} missing columns: {', '.join(sorted(missing))}")
    entries = []
    seen = set()
    for index, row in enumerate(rows, start=2):
        value = str(row.get("new_value") or "").strip()
        if not value:
            continue
        post_id = str(row.get("post_id") or "").strip()
        field = str(row.get("field") or "").strip()
        source_row = str(row.get("source_row") or "").strip()
        evidence_note = str(row.get("evidence_note") or "").strip()
        if field not in RESULT_FIELDS:
            raise SystemExit(f"{relative(path)} row {index} has unsupported result field: {field}")
        if not post_id or not source_row:
            raise SystemExit(f"{relative(path)} row {index} missing post_id or source_row")
        if not evidence_note:
            raise SystemExit(f"{relative(path)} row {index} needs evidence_note before import")
        key = (post_id, field, source_row)
        if key in seen:
            raise SystemExit(f"{relative(path)} has duplicate result entry for {post_id} {field} row {source_row}")
        seen.add(key)
        entries.append({
            "csv_row": index,
            "post_id": post_id,
            "field": field,
            "source_row": int(source_row),
            "value": normalize_result_value(field, value),
            "evidence_note": evidence_note,
        })
    return entries


def load_wide_entries(path: Path) -> list[dict]:
    fieldnames, rows = read_csv(path)
    required = {"post_id", "source_row", "evidence_note", *RESULT_FIELDS}
    missing = required - set(fieldnames)
    if missing:
        raise SystemExit(f"{relative(path)} missing columns: {', '.join(sorted(missing))}")
    entries = []
    seen = set()
    for index, row in enumerate(rows, start=2):
        filled_fields = [
            field
            for field in sorted(RESULT_FIELDS)
            if str(row.get(field) or "").strip()
        ]
        if not filled_fields:
            continue
        post_id = str(row.get("post_id") or "").strip()
        source_row = str(row.get("source_row") or "").strip()
        evidence_note = str(row.get("evidence_note") or "").strip()
        if not post_id or not source_row:
            raise SystemExit(f"{relative(path)} row {index} missing post_id or source_row")
        if not evidence_note:
            raise SystemExit(f"{relative(path)} row {index} needs evidence_note before import")
        for field in filled_fields:
            key = (post_id, field, source_row)
            if key in seen:
                raise SystemExit(f"{relative(path)} has duplicate result entry for {post_id} {field} row {source_row}")
            seen.add(key)
            entries.append({
                "csv_row": index,
                "post_id": post_id,
                "field": field,
                "source_row": int(source_row),
                "value": normalize_result_value(field, row.get(field) or ""),
                "evidence_note": evidence_note,
            })
    return entries


def load_direct_entries(args: argparse.Namespace) -> list[dict]:
    post_id = str(args.post_id or "").strip()
    source_row = str(args.source_row or "").strip()
    evidence_note = str(args.evidence_note or "").strip()
    if not post_id or not source_row:
        raise SystemExit("--post-id and --source-row are required for direct metric entry.")
    entries = []
    for field in sorted(RESULT_FIELDS):
        raw = getattr(args, field)
        if raw is None or str(raw).strip() == "":
            continue
        if not evidence_note:
            raise SystemExit("--evidence-note is required when direct metric values are supplied.")
        entries.append({
            "csv_row": None,
            "post_id": post_id,
            "field": field,
            "source_row": int(source_row),
            "value": normalize_result_value(field, raw),
            "evidence_note": evidence_note,
        })
    if not entries:
        raise SystemExit("No direct result values supplied; provide at least one metric field.")
    return entries


def direct_arg_names(field: str) -> list[str]:
    dashed = f"--{field.replace('_', '-')}"
    underscored = f"--{field}"
    return [dashed] if dashed == underscored else [dashed, underscored]


def apply_entries(entries: list[dict], published_rows: list[dict]) -> tuple[list[dict], list[dict]]:
    changes = []
    already_filled = []
    for entry in entries:
        row_index = entry["source_row"] - 2
        if row_index < 0 or row_index >= len(published_rows):
            raise SystemExit(f"Published_Log.csv row {entry['source_row']} is outside the current published log")
        row = published_rows[row_index]
        actual_post_id = queue_id(row)
        if actual_post_id != entry["post_id"]:
            raise SystemExit(
                f"Published_Log.csv row {entry['source_row']} is {actual_post_id!r}, "
                f"not {entry['post_id']!r}; rebuild the result collection packet."
            )
        current = str(row.get(entry["field"]) or "").strip()
        if current:
            already_filled.append({
                "post_id": entry["post_id"],
                "field": entry["field"],
                "source_row": entry["source_row"],
                "current_value": current,
            })
            continue
        row[entry["field"]] = entry["value"]
        notes = str(row.get("notes") or "").strip()
        evidence = f"result_evidence:{entry['field']}={entry['evidence_note']}"
        row["notes"] = f"{notes}; {evidence}" if notes else evidence
        changes.append({
            "post_id": entry["post_id"],
            "field": entry["field"],
            "source_row": entry["source_row"],
            "new_value": entry["value"],
            "evidence_note": entry["evidence_note"],
        })
    return changes, already_filled


def refresh_admin() -> None:
    subprocess.run(["python3", "scripts/refresh_promo_admin.py"], cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Import filled experiment result values into Published_Log.csv.")
    parser.add_argument(
        "--from-csv",
        default="",
        help="CSV generated by scripts/build_experiment_result_collection.py.",
    )
    parser.add_argument(
        "--from-wide-csv",
        default="",
        help="Wide one-row-per-post CSV generated by scripts/build_experiment_result_collection.py.",
    )
    parser.add_argument("--post-id", default="", help="Direct entry post id from the result clipboard.")
    parser.add_argument("--source-row", default="", help="Published_Log.csv source row for direct entry.")
    parser.add_argument("--evidence-note", default="", help="Evidence note for direct metric entry.")
    for field in sorted(RESULT_FIELDS):
        parser.add_argument(*direct_arg_names(field), dest=field, default=None, help=f"Direct entry value for {field}.")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing Published_Log.csv.")
    parser.add_argument("--apply", action="store_true", help="Write filled result values to Published_Log.csv.")
    parser.add_argument("--refresh-admin", action="store_true", help="Refresh admin artifacts after applying.")
    args = parser.parse_args()

    if args.apply == args.dry_run:
        raise SystemExit("Choose exactly one of --dry-run or --apply.")
    if args.refresh_admin and not args.apply:
        raise SystemExit("--refresh-admin requires --apply.")
    if args.from_csv and args.from_wide_csv:
        raise SystemExit("Choose only one of --from-csv or --from-wide-csv.")
    direct_requested = bool(args.post_id or args.source_row or args.evidence_note or any(getattr(args, field) not in (None, "") for field in RESULT_FIELDS))
    if direct_requested and (args.from_csv or args.from_wide_csv):
        raise SystemExit("Direct metric entry cannot be combined with --from-csv or --from-wide-csv.")

    if direct_requested:
        source_format = "direct"
        source = Path("<direct>")
        entries = load_direct_entries(args)
    else:
        source_format = "wide" if args.from_wide_csv else "long"
        source_arg = args.from_wide_csv or args.from_csv or str(DEFAULT_CSV.relative_to(ROOT))
        source = Path(source_arg)
        if not source.is_absolute():
            source = ROOT / source
        entries = load_wide_entries(source) if source_format == "wide" else load_entries(source)
    if not entries:
        raise SystemExit(f"No filled result values found in {relative(source)}.")
    published_fields, published_rows = read_csv(PUBLISHED_LOG)
    missing_log_fields = RESULT_FIELDS - set(published_fields)
    if missing_log_fields:
        raise SystemExit(f"{relative(PUBLISHED_LOG)} missing result columns: {', '.join(sorted(missing_log_fields))}")
    changes, already_filled = apply_entries(entries, published_rows)
    if not changes:
        raise SystemExit("No importable result changes found; all filled entries are already present.")

    if args.apply:
        write_csv(PUBLISHED_LOG, published_fields, published_rows)
        if args.refresh_admin:
            refresh_admin()

    payload = {
        "ok": True,
        "dry_run": not args.apply,
        "source_csv": relative(source),
        "source_format": source_format,
        "target": relative(PUBLISHED_LOG),
        "filled_entry_count": len(entries),
        "change_count": len(changes),
        "already_filled_count": len(already_filled),
        "changes": changes,
        "already_filled": already_filled,
        "action": "updated_published_log_results" if args.apply else "would_update_published_log_results",
        "post_apply_verification": [
            "python3 scripts/refresh_promo_admin.py",
            "python3 scripts/validate_content_system.py",
        ],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
