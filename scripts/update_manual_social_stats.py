#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MANUAL = ROOT / "data" / "manual_social_stats.json"


def read_manual():
    if not MANUAL.exists():
        raise SystemExit(f"Missing {MANUAL}")
    return json.loads(MANUAL.read_text(encoding="utf-8"))


def parse_assignment(raw: str):
    if "=" not in raw:
        raise SystemExit(f"Expected platform.metric=value, got: {raw}")
    path, value = raw.split("=", 1)
    if "." not in path:
        raise SystemExit(f"Expected platform.metric=value, got: {raw}")
    platform, metric = path.split(".", 1)
    platform = platform.strip()
    metric = metric.strip()
    if not platform or not metric:
        raise SystemExit(f"Expected platform.metric=value, got: {raw}")
    return platform, metric, value.strip()


def update_value(data, platform: str, metric: str, value: str):
    if platform not in data or not isinstance(data[platform], dict):
        known = ", ".join(sorted(data))
        raise SystemExit(f"Unknown platform '{platform}'. Known platforms: {known}")
    if metric not in data[platform]:
        known = ", ".join(sorted(data[platform]))
        raise SystemExit(f"Unknown metric '{platform}.{metric}'. Known metrics: {known}")
    previous = data[platform].get(metric)
    data[platform][metric] = value
    return previous


def refresh_admin():
    commands = [
        ["python3", "scripts/update_promo_engine_status.py"],
        ["python3", "scripts/generate_promo_queue_plan.py"],
        ["python3", "scripts/update_promo_engine_status.py"],
    ]
    for command in commands:
        subprocess.run(command, cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(
        description="Update data/manual_social_stats.json with platform.metric=value assignments."
    )
    parser.add_argument("assignments", nargs="+", help="Example: youtube.subscribers=6")
    parser.add_argument("--refresh-admin", action="store_true", help="Regenerate promo status and admin embeds after writing.")
    args = parser.parse_args()

    data = read_manual()
    changes = []
    for raw in args.assignments:
        platform, metric, value = parse_assignment(raw)
        previous = update_value(data, platform, metric, value)
        changes.append((platform, metric, previous, value))

    MANUAL.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for platform, metric, previous, value in changes:
        print(f"{platform}.{metric}: {previous!r} -> {value!r}")
    print(f"Updated {MANUAL.relative_to(ROOT)}")

    if args.refresh_admin:
        refresh_admin()
        print("Refreshed promo status and admin embeds")


if __name__ == "__main__":
    main()
