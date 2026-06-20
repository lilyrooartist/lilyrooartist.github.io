#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from decimal import Decimal, InvalidOperation
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MANUAL = ROOT / "data" / "manual_social_stats.json"
LIVE_METRICS = ROOT / "data" / "live_social_metrics.json"
DEFAULT_CSV = ROOT / "data" / "manual_metric_collection_template.csv"
NON_NUMERIC_FIELDS = {"artist_url", "profile_url", "release_url", "provider_url"}


def read_manual():
    if not MANUAL.exists():
        raise SystemExit(f"Missing {MANUAL}")
    return json.loads(MANUAL.read_text(encoding="utf-8"))


def read_live_metrics():
    if not LIVE_METRICS.exists():
        raise SystemExit(f"Missing {LIVE_METRICS}")
    return json.loads(LIVE_METRICS.read_text(encoding="utf-8"))


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


def csv_assignments(path: Path):
    if not path.exists():
        raise SystemExit(f"Missing {path}")
    assignments = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"platform", "field", "new_value"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"{path.relative_to(ROOT)} missing columns: {', '.join(sorted(missing))}")
        for index, row in enumerate(reader, start=2):
            value = str(row.get("new_value") or "").strip()
            if not value:
                continue
            platform = str(row.get("platform") or "").strip()
            metric = str(row.get("field") or "").strip()
            if not platform or not metric:
                raise SystemExit(f"{path.relative_to(ROOT)} row {index} missing platform or field")
            assignments.append(f"{platform}.{metric}={value}")
    return assignments


def live_metric_value(platforms, platform: str, metric: str):
    data = (platforms or {}).get(platform) or {}
    metrics = data.get("metrics") or {}
    if metric in metrics and metrics.get(metric) not in (None, ""):
        return metrics.get(metric)
    fallback_keys = {
        ("facebook", "followers"): ["page_likes"],
    }.get((platform, metric), [])
    for fallback_key in fallback_keys:
        if fallback_key in metrics and metrics.get(fallback_key) not in (None, ""):
            return metrics.get(fallback_key)
    return None


def live_assignments(manual: dict, live: dict) -> list[str]:
    platforms = live.get("platforms") if isinstance(live, dict) else {}
    assignments = []
    for platform, values in sorted((manual or {}).items()):
        if not isinstance(values, dict):
            continue
        for metric, current in sorted(values.items()):
            if current != "pending":
                continue
            live_value = live_metric_value(platforms, platform, metric)
            if live_value is not None:
                assignments.append(f"{platform}.{metric}={live_value}")
    return assignments


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


def validate_metric_value(platform: str, metric: str, value: str) -> str:
    if metric in NON_NUMERIC_FIELDS or metric.endswith("_url"):
        return str(value or "").strip()
    cleaned = str(value or "").strip().replace(",", "")
    if not cleaned or cleaned.lower() in {"pending", "n/a", "na", "none"}:
        raise SystemExit(f"{platform}.{metric} must be a collected non-negative numeric value, got {value!r}.")
    try:
        parsed = Decimal(cleaned)
    except InvalidOperation:
        raise SystemExit(f"{platform}.{metric} must be numeric, got {value!r}.")
    if parsed < 0:
        raise SystemExit(f"{platform}.{metric} must be non-negative, got {value!r}.")
    return cleaned


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
    parser.add_argument("assignments", nargs="*", help="Example: youtube.subscribers=6")
    parser.add_argument(
        "--from-csv",
        nargs="?",
        const=str(DEFAULT_CSV.relative_to(ROOT)),
        default="",
        help="Import filled new_value cells from the manual metric CSV.",
    )
    parser.add_argument("--from-live", action="store_true", help="Import pending metrics already covered by data/live_social_metrics.json.")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing manual stats.")
    parser.add_argument("--refresh-admin", action="store_true", help="Regenerate promo status and admin embeds after writing.")
    args = parser.parse_args()

    data = read_manual()
    assignments = list(args.assignments)
    if args.from_csv:
        csv_path = Path(args.from_csv)
        if not csv_path.is_absolute():
            csv_path = ROOT / csv_path
        assignments.extend(csv_assignments(csv_path))
    if args.from_live:
        assignments.extend(live_assignments(data, read_live_metrics()))
    if not assignments:
        if args.from_live and not args.assignments and not args.from_csv:
            print("No live-covered pending metrics available; manual stats unchanged.")
            return
        raise SystemExit("No metric assignments supplied. Add platform.metric=value args or fill new_value cells and use --from-csv.")

    changes = []
    for raw in assignments:
        platform, metric, value = parse_assignment(raw)
        normalized_value = validate_metric_value(platform, metric, value)
        previous = update_value(data, platform, metric, normalized_value)
        changes.append((platform, metric, previous, normalized_value))

    for platform, metric, previous, value in changes:
        print(f"{platform}.{metric}: {previous!r} -> {value!r}")
    if args.dry_run:
        print(f"Dry run only; did not update {MANUAL.relative_to(ROOT)}")
        return

    MANUAL.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {MANUAL.relative_to(ROOT)}")

    if args.refresh_admin:
        refresh_admin()
        print("Refreshed promo status and admin embeds")


if __name__ == "__main__":
    main()
