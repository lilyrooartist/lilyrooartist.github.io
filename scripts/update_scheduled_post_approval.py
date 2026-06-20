#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data" / "scheduled_posts.csv"
SCHEDULED_APPROVAL_PACKET = ROOT / "data" / "scheduled_approval_packet.json"


def read_rows() -> tuple[list[dict[str, str]], list[str]]:
    with QUEUE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def read_checked_batch_ids() -> list[str]:
    if not SCHEDULED_APPROVAL_PACKET.exists():
        return []
    packet = json.loads(SCHEDULED_APPROVAL_PACKET.read_text(encoding="utf-8"))
    summary = packet.get("summary") or {}
    return [str(item) for item in (summary.get("checked_batch_ids") or []) if item]


def write_rows(rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with QUEUE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def refresh_admin() -> None:
    for command in (
        ["python3", "scripts/sync_future_posts.py"],
        ["python3", "scripts/update_metrics_history.py", "--refresh-admin"],
        ["python3", "scripts/update_promo_engine_status.py"],
    ):
        subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Mark rows in data/scheduled_posts.csv approved or unapproved.")
    parser.add_argument("ids", nargs="*")
    parser.add_argument(
        "--checked-batch",
        action="store_true",
        help="Approve the current checked_batch_ids from data/scheduled_approval_packet.json.",
    )
    parser.add_argument(
        "--allow-unchecked",
        action="store_true",
        help="Allow approval of IDs outside the checked scheduled approval batch.",
    )
    parser.add_argument("--unapprove", action="store_true", help="Set approved=no instead of approved=yes.")
    parser.add_argument("--dry-run", action="store_true", help="Preview approval changes without writing scheduled_posts.csv.")
    parser.add_argument("--refresh-admin", action="store_true")
    args = parser.parse_args()

    checked_batch_ids = read_checked_batch_ids()
    if args.checked_batch and args.ids:
        raise SystemExit("Use --checked-batch without explicit IDs so the reviewed packet remains the source of truth.")
    if args.checked_batch:
        if not checked_batch_ids:
            raise SystemExit("No checked scheduled approval batch IDs found. Run scripts/build_scheduled_approval_packet.py first.")
        ids = checked_batch_ids
    else:
        ids = args.ids
    if not ids:
        raise SystemExit("Provide scheduled post ID(s), or use --checked-batch.")
    if not args.unapprove and not args.allow_unchecked:
        unchecked = sorted(set(ids) - set(checked_batch_ids))
        if unchecked:
            raise SystemExit(
                "Refusing to approve unchecked scheduled post id(s): "
                + ", ".join(unchecked)
                + ". Use --checked-batch for reviewed rows, or --allow-unchecked only after manual review."
            )

    rows, fieldnames = read_rows()
    wanted = set(ids)
    found = set()
    value = "no" if args.unapprove else "yes"
    changed = 0
    for row in rows:
        row_id = row.get("id", "")
        if row_id in wanted:
            found.add(row_id)
            previous = row.get("approved", "")
            row["approved"] = value
            changed += int(previous != value)
            print(f"{row_id}: approved {previous!r} -> {value!r}")
    missing = sorted(wanted - found)
    if missing:
        raise SystemExit("Missing scheduled post id(s): " + ", ".join(missing))
    unchecked_count = len(set(ids) - set(checked_batch_ids))
    print(
        "Checked batch guard: "
        f"{len(checked_batch_ids)} checked id(s); {len(wanted)} requested; "
        f"{unchecked_count} unchecked; {changed} change(s)."
    )
    if args.dry_run:
        print("Dry run only; did not update data/scheduled_posts.csv")
        return 0

    write_rows(rows, fieldnames)
    if args.refresh_admin:
        refresh_admin()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
