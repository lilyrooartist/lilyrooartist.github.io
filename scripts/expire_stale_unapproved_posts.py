#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data" / "scheduled_posts.csv"
PUBLISHED_LOG = ROOT / "admin" / "content" / "Published_Log.csv"
ARCHIVE = ROOT / "data" / "expired_scheduled_posts.csv"
OUT = ROOT / "data" / "stale_scheduled_post_expiration.json"


def parse_datetime(value: str | None) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_now(value: str | None) -> datetime:
    parsed = parse_datetime(value)
    return parsed or datetime.now(timezone.utc)


def truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "approved"}


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not path.exists():
        return [], []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def published_ids(path: Path) -> set[str]:
    ids: set[str] = set()
    if not path.exists():
        return ids
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            content_id = str(row.get("content_id") or "").strip()
            if content_id.startswith("FP-"):
                ids.add(content_id)
            notes = str(row.get("notes") or "")
            ids.update(re.findall(r"\bqueue_id=(FP-[A-Z0-9-]+)\b", notes))
    return ids


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def append_archive(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    if not rows:
        return
    archive_fields = fieldnames[:]
    for field in ("expired_at", "expiration_reason"):
        if field not in archive_fields:
            archive_fields.append(field)

    existing, existing_fields = read_csv(path)
    if existing_fields and existing_fields != archive_fields:
        for field in existing_fields:
            if field not in archive_fields:
                archive_fields.append(field)
    by_id = {row.get("id", ""): row for row in existing if row.get("id")}
    for row in rows:
        by_id[row.get("id", "")] = row
    write_csv(path, list(by_id.values()), archive_fields)


def is_expirable(row: dict[str, str], *, now: datetime, cutoff: datetime, published: set[str]) -> tuple[bool, str]:
    post_id = str(row.get("id") or "").strip()
    if not post_id:
        return False, "missing_id"
    if post_id in published:
        return False, "already_published"
    if truthy(row.get("approved")):
        return False, "approved"

    scheduled_at = parse_datetime(row.get("scheduled_at"))
    if not scheduled_at:
        return False, "missing_or_invalid_scheduled_at"
    if scheduled_at > cutoff:
        return False, "inside_stale_grace_window"

    return True, f"unapproved_past_due_before_{cutoff.isoformat().replace('+00:00', 'Z')}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive stale unapproved scheduled posts before they feed the social scheduler.")
    parser.add_argument("--older-than-hours", type=float, default=24.0)
    parser.add_argument("--now", default="")
    parser.add_argument("--write", action="store_true", help="Write data/expired_scheduled_posts.csv.")
    parser.add_argument("--prune-source", action="store_true", help="Also remove expired rows from data/scheduled_posts.csv.")
    parser.add_argument("--out", default=str(OUT.relative_to(ROOT)))
    args = parser.parse_args()

    now = parse_now(args.now)
    cutoff = now - timedelta(hours=args.older_than_hours)
    rows, fieldnames = read_csv(QUEUE)
    published = published_ids(PUBLISHED_LOG)
    kept: list[dict[str, str]] = []
    expired: list[dict[str, str]] = []
    skipped_reasons: dict[str, int] = {}

    for row in rows:
        should_expire, reason = is_expirable(row, now=now, cutoff=cutoff, published=published)
        skipped_reasons[reason] = skipped_reasons.get(reason, 0) + (0 if should_expire else 1)
        if should_expire:
            item = dict(row)
            item["expired_at"] = now.isoformat().replace("+00:00", "Z")
            item["expiration_reason"] = reason
            expired.append(item)
        else:
            kept.append(row)

    report = {
        "ok": True,
        "mode": "write" if args.write else "dry_run",
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "source": str(QUEUE.relative_to(ROOT)),
        "archive": str(ARCHIVE.relative_to(ROOT)),
        "older_than_hours": args.older_than_hours,
        "cutoff": cutoff.isoformat().replace("+00:00", "Z"),
        "input_count": len(rows),
        "kept_count": len(kept),
        "expired_count": len(expired),
        "expired_ids": [row.get("id", "") for row in expired],
        "skipped_reasons": dict(sorted((key, value) for key, value in skipped_reasons.items() if value)),
        "source_pruned": bool(args.write and args.prune_source),
        "guardrail": "Only unapproved, unpublished, past-due rows outside the stale grace window are archived; source pruning requires --prune-source.",
    }

    if args.write and expired:
        append_archive(ARCHIVE, expired, fieldnames)
        if args.prune_source:
            write_csv(QUEUE, kept, fieldnames)

    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "mode": report["mode"],
        "expired_count": report["expired_count"],
        "expired_ids": report["expired_ids"],
        "output": str(out.relative_to(ROOT)),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
