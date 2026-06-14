#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data" / "scheduled_posts.csv"
PUBLISHED_LOG = ROOT / "admin" / "content" / "Published_Log.csv"
SOCIAL_EXECUTIONS = ROOT / "data" / "social_execution_snapshot.json"


def parse_datetime(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value or "").strip())
    except ValueError as exc:
        raise SystemExit(f"Invalid datetime: {value}") from exc
    if parsed.tzinfo is None:
        return parsed.astimezone()
    return parsed


def read_rows() -> tuple[list[dict[str, str]], list[str]]:
    with QUEUE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_rows(rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with QUEUE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_published_ids() -> set[str]:
    ids = set()
    if not PUBLISHED_LOG.exists():
        return ids
    with PUBLISHED_LOG.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            content_id = (row.get("content_id") or "").strip()
            if content_id.startswith("FP-AUTO-"):
                ids.add(content_id)
            for match in re.findall(r"\bqueue_id=(FP-AUTO-\d+)\b", row.get("notes") or ""):
                ids.add(match)
    return ids


def load_execution_blockers() -> dict[str, dict[str, str]]:
    if not SOCIAL_EXECUTIONS.exists():
        return {}
    try:
        snapshot = json.loads(SOCIAL_EXECUTIONS.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    summary = snapshot.get("summary") or {}
    blockers = {}
    for key in ("platform_fix_needed", "approval_needed", "latest_attention"):
        for row in summary.get(key) or []:
            post_id = row.get("post_id")
            if post_id and post_id not in blockers:
                blockers[post_id] = row
    return blockers


def refresh_admin() -> None:
    commands = [
        ["python3", "scripts/sync_future_posts.py"],
        ["python3", "scripts/update_metrics_history.py", "--refresh-admin"],
        ["python3", "scripts/update_promo_engine_status.py"],
        ["python3", "scripts/generate_promo_queue_plan.py"],
        ["python3", "scripts/update_promo_engine_status.py"],
    ]
    for command in commands:
        subprocess.run(command, cwd=ROOT, check=True)


def selected_rows(rows: list[dict[str, str]], args) -> list[dict[str, str]]:
    wanted = set(args.id or [])
    now = datetime.now().astimezone()
    published_ids = set() if args.include_published else load_published_ids()
    selected = []
    for row in rows:
        row_id = row.get("id", "")
        if row_id in published_ids:
            continue
        scheduled_at = parse_datetime(row.get("scheduled_at", ""))
        is_approved = str(row.get("approved") or "").strip().lower() == "yes"
        if wanted and row_id in wanted:
            selected.append(row)
        elif args.approved_backlog and is_approved and scheduled_at < now:
            selected.append(row)
    if wanted:
        found = {row.get("id") for row in selected}
        missing = sorted(wanted - found)
        if missing:
            raise SystemExit("Missing scheduled post id(s): " + ", ".join(missing))
    return selected


def next_slots(start_at: datetime, count: int, spacing_hours: int) -> list[datetime]:
    return [start_at + timedelta(hours=spacing_hours * index) for index in range(count)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Preview or apply new scheduled_at values for scheduled post rows.")
    parser.add_argument("--id", action="append", default=[], help="Specific scheduled post id to reschedule. Repeatable.")
    parser.add_argument("--approved-backlog", action="store_true", help="Select approved rows whose scheduled_at is already in the past.")
    parser.add_argument("--include-published", action="store_true", help="Allow rows already recorded in admin/content/Published_Log.csv.")
    parser.add_argument("--start-at", required=True, help="First replacement ISO datetime, for example 2026-06-15T10:00:00-04:00.")
    parser.add_argument("--spacing-hours", type=int, default=24, help="Hours between selected rows. Default: 24.")
    parser.add_argument("--apply", action="store_true", help="Write the new scheduled_at values. Default is dry-run.")
    parser.add_argument("--allow-blocked", action="store_true", help="Allow applying rows with known executor/platform blockers.")
    parser.add_argument("--refresh-admin", action="store_true", help="Refresh generated admin artifacts after applying.")
    args = parser.parse_args()

    if not args.id and not args.approved_backlog:
        raise SystemExit("Select rows with --id or --approved-backlog.")
    if args.spacing_hours <= 0:
        raise SystemExit("--spacing-hours must be positive.")

    rows, fieldnames = read_rows()
    selected = selected_rows(rows, args)
    selected.sort(key=lambda row: row.get("scheduled_at", ""))
    slots = next_slots(parse_datetime(args.start_at), len(selected), args.spacing_hours)
    replacements = dict(zip([row.get("id", "") for row in selected], slots))
    blockers = load_execution_blockers()
    selected_blockers = {row.get("id", ""): blockers[row.get("id", "")] for row in selected if row.get("id", "") in blockers}

    print(f"Rows selected: {len(selected)}")
    for row in selected:
        row_id = row.get("id", "")
        replacement = replacements[row_id].isoformat()
        print(f"- {row_id} {row.get('platform', '')} {row.get('song', '')}: {row.get('scheduled_at', '')} -> {replacement}")
        blocker = selected_blockers.get(row_id)
        if blocker:
            detail = blocker.get("error_summary") or blocker.get("reason") or blocker.get("status") or "executor attention required"
            print(f"  WARNING: known blocker: {detail}")

    if not args.apply:
        print("Dry run only. Re-run with --apply to write the schedule.")
        return 0
    if selected_blockers and not args.allow_blocked:
        blocked_ids = ", ".join(sorted(selected_blockers))
        raise SystemExit(
            "Refusing to apply blocked reschedule for "
            + blocked_ids
            + ". Fix/clear executor blockers first, or rerun with --allow-blocked after deliberate review."
        )

    for row in rows:
        row_id = row.get("id", "")
        if row_id in replacements:
            row["scheduled_at"] = replacements[row_id].isoformat()
    write_rows(rows, fieldnames)
    print(f"Updated {len(selected)} row(s) in {QUEUE}")
    if args.refresh_admin:
        refresh_admin()
        print("Refreshed future posts, metrics history, promo status, promo plan, and admin embeds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
