#!/usr/bin/env python3
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "admin" / "content"
CATALOG = ROOT / "admin" / "backstory" / "catalog.json"
QUIPS = CONTENT / "20_QUIPS_BANK.csv"
QUEUE = ROOT / "data" / "scheduled_posts.csv"
FUTURE = ROOT / "admin" / "future-posts.json"
REPORT = ROOT / "admin" / "reports" / "weekly-social-report.md"
INDEX = CONTENT / "content_index.json"


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fail(message, failures):
    failures.append(message)
    print(f"FAIL: {message}")


def ok(message):
    print(f"OK: {message}")


def validate_pack_pairs(failures):
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    missing = []
    for song in data.get("songs", []):
        for key in ("backstory_file", "visual_file"):
            ref = song.get(key, "")
            if not ref or not (ROOT / ref.lstrip("/")).exists():
                missing.append(f"{song.get('title', 'Unknown')} missing {key}")
    if missing:
        for item in missing:
            fail(item, failures)
    else:
        ok("all catalog songs have backstory and visual packs")


def validate_quips(failures):
    rows = read_csv(QUIPS)
    required = {"id", "theme", "tone", "quip", "ideal_platform", "cta"}
    if rows and set(rows[0].keys()) >= required:
        ok("quips CSV has required columns")
    else:
        fail("quips CSV is missing required columns", failures)
    ids = [row.get("id", "") for row in rows]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        fail(f"duplicate quip ids: {', '.join(duplicates)}", failures)
    else:
        ok(f"quip ids unique ({len(rows)} rows)")


def validate_queue(failures):
    rows = read_csv(QUEUE)
    required = {"id", "scheduled_at", "platform", "song", "text", "drafts"}
    if not rows:
        fail("scheduled queue is empty", failures)
        return
    if set(rows[0].keys()) >= required:
        ok("scheduled queue has required columns")
    else:
        fail("scheduled queue is missing required columns", failures)
    ids = [row.get("id", "") for row in rows]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        fail(f"duplicate queue ids: {', '.join(duplicates)}", failures)
    else:
        ok(f"queue ids unique ({len(rows)} rows)")
    for row in rows:
        for key in ("id", "scheduled_at", "platform", "text"):
            if not row.get(key, "").strip():
                fail(f"queue row {row.get('id') or '[missing id]'} missing {key}", failures)
        try:
            datetime.fromisoformat(row.get("scheduled_at", ""))
        except ValueError:
            fail(f"queue row {row.get('id')} has invalid scheduled_at", failures)


def validate_generated_outputs(failures):
    if FUTURE.exists():
        future = json.loads(FUTURE.read_text(encoding="utf-8"))
        if future.get("posts"):
            ok(f"future-posts.json has {len(future['posts'])} posts")
        else:
            fail("future-posts.json has no posts", failures)
    else:
        fail("future-posts.json missing", failures)
    if INDEX.exists():
        index = json.loads(INDEX.read_text(encoding="utf-8"))
        ok(f"content index generated with {index.get('counts', {}).get('songs', 0)} songs")
    else:
        fail("content_index.json missing; run scripts/build_content_index.py", failures)


def validate_report(failures):
    text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    if re.search(r"\*\*Last updated:\*\*\s*\d{4}-\d{2}-\d{2}", text):
        ok("weekly report has a Last updated timestamp")
    else:
        fail("weekly report missing Last updated timestamp", failures)


def main():
    failures = []
    validate_pack_pairs(failures)
    validate_quips(failures)
    validate_queue(failures)
    validate_generated_outputs(failures)
    validate_report(failures)
    if failures:
        print(f"\n{len(failures)} validation issue(s)")
        return 1
    print("\ncontent system validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
