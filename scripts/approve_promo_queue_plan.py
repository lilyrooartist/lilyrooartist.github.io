#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "data" / "promo_queue_plan.json"


def read_plan():
    if not PLAN.exists():
        raise SystemExit(f"Missing {PLAN}; run scripts/generate_promo_queue_plan.py first")
    return json.loads(PLAN.read_text(encoding="utf-8"))


def norm(value: str | None) -> str:
    return " ".join(str(value or "").strip().lower().split())


def selected_posts(plan, args):
    posts = plan.get("posts") or []
    if args.all:
        return posts

    wanted_ids = set(args.id or [])
    release = norm(args.release)
    platform = norm(args.platform)
    selected = []
    for post in posts:
        if wanted_ids and post.get("id") in wanted_ids:
            selected.append(post)
            continue
        if release and norm(post.get("song")) != release:
            continue
        if platform and norm(post.get("platform")) != platform:
            continue
        if release or platform:
            selected.append(post)

    if wanted_ids:
        found = {post.get("id") for post in selected}
        missing = sorted(wanted_ids - found)
        if missing:
            raise SystemExit(f"Plan is missing requested id(s): {', '.join(missing)}")
    return selected


def summarize(plan):
    posts = plan.get("posts") or []
    approved = sum(1 for post in posts if post.get("approved") == "yes")
    review = len(posts) - approved
    releases = {}
    platforms = {}
    for post in posts:
        release = post.get("song") or "Untitled release"
        platform = post.get("platform") or "Unknown"
        releases.setdefault(release, {"draft_posts": 0, "approved_posts": 0, "review_posts": 0, "platforms": set()})
        platforms.setdefault(platform, {"draft_posts": 0, "approved_posts": 0, "review_posts": 0})
        releases[release]["draft_posts"] += 1
        releases[release]["platforms"].add(platform)
        platforms[platform]["draft_posts"] += 1
        if post.get("approved") == "yes":
            releases[release]["approved_posts"] += 1
            platforms[platform]["approved_posts"] += 1
        else:
            releases[release]["review_posts"] += 1
            platforms[platform]["review_posts"] += 1

    return {
        "draft_posts": len(posts),
        "approved_posts": approved,
        "review_posts": review,
        "auto_posts": sum(1 for post in posts if post.get("execution_mode") == "auto"),
        "manual_posts": sum(1 for post in posts if post.get("execution_mode") == "manual"),
        "releases": {
            release: {**data, "platforms": sorted(data["platforms"])}
            for release, data in sorted(releases.items())
        },
        "platforms": dict(sorted(platforms.items())),
    }


def write_plan(plan):
    plan["summary"] = summarize(plan)
    PLAN.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def refresh_admin():
    commands = [
        ["python3", "scripts/update_promo_engine_status.py"],
        ["python3", "scripts/generate_promo_queue_plan.py"],
        ["python3", "scripts/update_promo_engine_status.py"],
    ]
    for command in commands:
        subprocess.run(command, cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description="Mark promo queue plan rows approved or unapproved.")
    parser.add_argument("--id", action="append", help="Approve a specific FP-PLAN id. Repeatable.")
    parser.add_argument("--release", help="Select rows for a release title.")
    parser.add_argument("--platform", help="Select rows for a platform.")
    parser.add_argument("--all", action="store_true", help="Select all draft rows.")
    parser.add_argument("--unapprove", action="store_true", help="Set selected rows approved=no instead of yes.")
    parser.add_argument("--dry-run", action="store_true", help="Preview selected rows without changing approval state.")
    parser.add_argument("--refresh-admin", action="store_true", help="Regenerate promo status and admin embeds after writing.")
    args = parser.parse_args()

    if not (args.all or args.id or args.release or args.platform):
        raise SystemExit("Select rows with --id, --release, --platform, or --all")

    plan = read_plan()
    posts = selected_posts(plan, args)
    if not posts:
        raise SystemExit("No promo plan rows matched the selection")

    value = "no" if args.unapprove else "yes"
    for post in posts:
        previous = post.get("approved", "no")
        print(f"{post.get('id')}: approved {previous!r} -> {value!r}")
    if args.dry_run:
        print(f"Dry run only; no changes written to {PLAN.relative_to(ROOT)}")
        return

    for post in posts:
        post["approved"] = value
    write_plan(plan)
    print(f"Updated {PLAN.relative_to(ROOT)} ({len(posts)} row(s))")

    if args.refresh_admin:
        refresh_admin()
        print("Refreshed promo status and admin embeds")


if __name__ == "__main__":
    main()
