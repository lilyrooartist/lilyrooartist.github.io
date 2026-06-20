#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data" / "scheduled_posts.csv"


def read_rows() -> tuple[list[dict[str, str]], list[str]]:
    with QUEUE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


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
    parser.add_argument("ids", nargs="+")
    parser.add_argument("--unapprove", action="store_true", help="Set approved=no instead of approved=yes.")
    parser.add_argument("--dry-run", action="store_true", help="Preview approval changes without writing scheduled_posts.csv.")
    parser.add_argument("--refresh-admin", action="store_true")
    args = parser.parse_args()

    rows, fieldnames = read_rows()
    wanted = set(args.ids)
    found = set()
    value = "no" if args.unapprove else "yes"
    for row in rows:
        row_id = row.get("id", "")
        if row_id in wanted:
            found.add(row_id)
            previous = row.get("approved", "")
            row["approved"] = value
            print(f"{row_id}: approved {previous!r} -> {value!r}")
    missing = sorted(wanted - found)
    if missing:
        raise SystemExit("Missing scheduled post id(s): " + ", ".join(missing))
    if args.dry_run:
        print("Dry run only; did not update data/scheduled_posts.csv")
        return 0

    write_rows(rows, fieldnames)
    if args.refresh_admin:
        refresh_admin()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
