#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data" / "scheduled_posts.csv"

VIDEO_ASSETS = {
    "I Learned It All in Fifteen Seconds": {
        "clip_url": "https://www.lilyroo.com/assets/ig/01_i_learned_it_all_60s.mp4",
        "media_key": "i-learned-60s",
    },
    "Twelve Dollars": {
        "clip_url": "https://www.lilyroo.com/assets/albums/twelve-dollars/video/04-twelve-dollars-youtube-remaster.mp4",
        "media_key": "twelve-dollars-video",
    },
    "Analog Myth": {
        "clip_url": "https://www.lilyroo.com/assets/albums/analog-myth/video/03-analog-myth-youtube-remaster.mp4",
        "media_key": "analog-myth-video",
    },
}


def read_rows() -> tuple[list[str], list[dict]]:
    if not QUEUE.exists():
        raise SystemExit(f"Missing queue: {QUEUE}")
    with QUEUE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def is_manual_community(row: dict) -> bool:
    platform = str(row.get("platform") or "").strip().lower()
    execution_mode = str(row.get("execution_mode") or "").strip().lower()
    post_type = str(row.get("post_type") or "").strip().lower()
    return platform == "youtube community" or execution_mode == "manual" and post_type == "community"


def convert_row(row: dict) -> tuple[dict, dict | None]:
    if not is_manual_community(row):
        return row, None
    song = str(row.get("song") or "").strip()
    asset = VIDEO_ASSETS.get(song)
    if not asset:
        return row, {
            "id": row.get("id") or "",
            "song": song,
            "status": "blocked",
            "reason": "missing_api_video_asset",
        }
    converted = dict(row)
    converted["platform"] = "YouTube"
    converted["execution_mode"] = "auto"
    converted["post_type"] = "video"
    converted["clip_url"] = asset["clip_url"]
    converted["media_key"] = asset["media_key"]
    converted["desired_privacy"] = converted.get("desired_privacy") or "public"
    if "#Shorts" not in str(converted.get("text") or "") and song == "I Learned It All in Fifteen Seconds":
        converted["text"] = f"{converted.get('text', '').rstrip()} #Shorts".strip()
    return converted, {
        "id": row.get("id") or "",
        "song": song,
        "status": "converted",
        "from_platform": row.get("platform") or "",
        "to_platform": converted["platform"],
        "from_execution_mode": row.get("execution_mode") or "",
        "to_execution_mode": converted["execution_mode"],
        "from_post_type": row.get("post_type") or "",
        "to_post_type": converted["post_type"],
        "clip_url": converted["clip_url"],
    }


def write_rows(fieldnames: list[str], rows: list[dict]) -> None:
    with QUEUE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def refresh_admin() -> None:
    subprocess.run(["python3", "scripts/refresh_promo_admin.py"], cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert legacy manual YouTube Community queue rows into API-postable YouTube video rows.")
    parser.add_argument("--apply", action="store_true", help="Write converted rows to data/scheduled_posts.csv. Default is dry-run.")
    parser.add_argument("--refresh-admin", action="store_true", help="Refresh admin packets after applying.")
    args = parser.parse_args()

    fieldnames, rows = read_rows()
    converted_rows = []
    changes = []
    blocked = []
    for row in rows:
        converted, change = convert_row(row)
        converted_rows.append(converted)
        if change:
            (changes if change["status"] == "converted" else blocked).append(change)

    payload = {
        "queue": str(QUEUE.relative_to(ROOT)),
        "dry_run": not args.apply,
        "converted_count": len(changes),
        "blocked_count": len(blocked),
        "converted": changes,
        "blocked": blocked,
        "guardrail": "This script changes local queue rows only; it does not publish posts externally.",
    }
    print(json.dumps(payload, indent=2))

    if args.apply:
        write_rows(fieldnames, converted_rows)
        if args.refresh_admin:
            refresh_admin()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
