#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "data" / "promo_queue_plan.json"
QUEUE = ROOT / "data" / "scheduled_posts.csv"

QUEUE_FIELDS = [
    "id",
    "scheduled_at",
    "platform",
    "song",
    "imagery",
    "imagery_url",
    "clip_url",
    "text",
    "drafts",
    "reply_text",
    "x_media_key",
    "media_key",
    "approved",
    "execution_mode",
    "post_type",
    "desired_privacy",
]


def read_plan():
    if not PLAN.exists():
        raise SystemExit(f"Missing {PLAN}; run scripts/generate_promo_queue_plan.py first")
    return json.loads(PLAN.read_text(encoding="utf-8"))


def read_queue():
    if not QUEUE.exists():
        raise SystemExit(f"Missing {QUEUE}")
    with QUEUE.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def queue_row(post):
    row = {field: "" for field in QUEUE_FIELDS}
    for field in QUEUE_FIELDS:
        value = post.get(field, "")
        if field == "drafts" and isinstance(value, list):
            value = "||".join(item.strip() for item in value if item.strip())
        row[field] = str(value or "")
    if row["approved"].lower() != "yes":
        row["approved"] = "no"
    return row


def selected_posts(plan, ids):
    posts = plan.get("posts") or []
    if ids:
        wanted = set(ids)
        posts = [post for post in posts if post.get("id") in wanted]
        missing = sorted(wanted - {post.get("id") for post in posts})
        if missing:
            raise SystemExit(f"Plan is missing requested id(s): {', '.join(missing)}")
    return posts


def validate_rows(rows):
    errors = []
    for row in rows:
        for key in ("id", "scheduled_at", "platform", "song", "text", "execution_mode", "post_type"):
            if not row.get(key):
                errors.append(f"{row.get('id') or '[missing id]'} missing {key}")
        if row.get("execution_mode") not in {"auto", "manual"}:
            errors.append(f"{row.get('id')} has unsupported execution_mode {row.get('execution_mode')}")
        if row.get("post_type") not in {"text", "image", "video", "community", "link"}:
            errors.append(f"{row.get('id')} has unsupported post_type {row.get('post_type')}")
    if errors:
        raise SystemExit("\n".join(errors))


def write_queue(existing, additions):
    with QUEUE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=QUEUE_FIELDS)
        writer.writeheader()
        writer.writerows(existing)
        writer.writerows(additions)


def main():
    parser = argparse.ArgumentParser(description="Append approved promo plan rows into data/scheduled_posts.csv.")
    parser.add_argument("--apply", action="store_true", help="Actually append rows. Default is dry-run.")
    parser.add_argument("--include-unapproved", action="store_true", help="Allow rows with approved != yes.")
    parser.add_argument("--id", action="append", default=[], help="Only apply a specific FP-PLAN id. Repeatable.")
    args = parser.parse_args()

    plan = read_plan()
    existing = read_queue()
    existing_ids = {row.get("id") for row in existing}
    posts = selected_posts(plan, args.id)
    if not args.include_unapproved:
        posts = [post for post in posts if str(post.get("approved") or "").lower() == "yes"]
    additions = [queue_row(post) for post in posts if post.get("id") not in existing_ids]
    skipped_duplicates = [post.get("id") for post in posts if post.get("id") in existing_ids]

    validate_rows(additions)

    print(f"Plan rows selected: {len(posts)}")
    print(f"Rows to append: {len(additions)}")
    if skipped_duplicates:
        print(f"Skipped duplicates: {', '.join(skipped_duplicates)}")
    for row in additions:
        print(f"- {row['id']} {row['scheduled_at']} {row['platform']} {row['song']} approved={row['approved']}")

    if not args.apply:
        print("Dry run only. Re-run with --apply to append rows.")
        return
    write_queue(existing, additions)
    print(f"Appended {len(additions)} row(s) to {QUEUE}")


if __name__ == "__main__":
    main()
