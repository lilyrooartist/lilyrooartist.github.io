#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from social_exec_common import append_published_log


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "data" / "manual_distribution_packet.json"
PUBLISHED_LOG = ROOT / "admin" / "content" / "Published_Log.csv"


def read_packet() -> dict:
    if not PACKET.exists():
        raise RuntimeError("manual_distribution_packet.json is missing; run scripts/build_manual_distribution_packet.py")
    return json.loads(PACKET.read_text(encoding="utf-8"))


def find_row(post_id: str) -> dict:
    for row in read_packet().get("rows") or []:
        if row.get("id") == post_id:
            return row
    raise RuntimeError(f"manual distribution row not found: {post_id}")


def validate_public_url(value: str) -> str:
    url = (value or "").strip()
    parsed = urlparse(url)
    if url == "PUBLIC_URL" or not parsed.scheme or not parsed.netloc or parsed.scheme not in {"http", "https"}:
        raise SystemExit("--url must be the public http(s) URL of the posted manual item, not PUBLIC_URL.")
    return url


def already_logged(post_id: str) -> dict | None:
    if not PUBLISHED_LOG.exists():
        return None
    with PUBLISHED_LOG.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            content_id = (row.get("content_id") or "").strip()
            notes = row.get("notes") or ""
            if content_id == post_id or f"manual_distribution_id={post_id}" in notes:
                return row
    return None


def refresh_admin() -> None:
    subprocess.run(["python3", "scripts/refresh_promo_admin.py"], cwd=ROOT, check=True)


def payload_for_row(row: dict, public_url: str) -> dict:
    notes = f"manual_distribution_id={row.get('id')}; source=data/manual_distribution_packet.json"
    return {
        "post_id": row.get("id") or "",
        "platform": row.get("platform") or "Manual",
        "release": row.get("release") or "",
        "url": public_url,
        "text": row.get("text") or "",
        "notes": notes,
        "target": str(PUBLISHED_LOG.relative_to(ROOT)),
    }


def append_payload(payload: dict) -> None:
    append_published_log(
        payload.get("platform") or "Manual",
        payload.get("url") or "",
        payload.get("release") or "",
        payload.get("text") or "",
        notes=payload.get("notes") or "",
        content_id=payload.get("post_id") or "",
    )


def read_csv_entries(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            {key: (value or "").strip() for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def log_from_csv(path: Path, *, apply: bool, refresh: bool) -> dict:
    if not path.exists():
        raise SystemExit(f"{path} does not exist")
    entries = read_csv_entries(path)
    if not entries:
        raise SystemExit(f"{path} has no rows")
    seen_ids = set()
    ready = []
    waiting = []
    duplicates = []
    already = []
    for entry in entries:
        post_id = entry.get("id") or entry.get("manual_distribution_id") or ""
        url = entry.get("public_url") or entry.get("url") or ""
        if not post_id:
            waiting.append({"id": "", "reason": "missing_id"})
            continue
        if post_id in seen_ids:
            duplicates.append(post_id)
            continue
        seen_ids.add(post_id)
        if not url or url == "PUBLIC_URL":
            waiting.append({"id": post_id, "reason": "missing_public_url"})
            continue
        row = find_row(post_id)
        public_url = validate_public_url(url)
        logged_row = already_logged(post_id)
        if logged_row:
            already.append({
                "id": post_id,
                "existing": logged_row.get("post_id_or_url") or logged_row.get("content_id") or "",
            })
            continue
        ready.append(payload_for_row(row, public_url))
    if duplicates:
        raise SystemExit(f"Duplicate manual distribution id(s) in {path}: {', '.join(duplicates)}")
    if apply and waiting:
        raise SystemExit("Every CSV row needs a real public_url before --apply.")
    if apply:
        for payload in ready:
            append_payload(payload)
        if refresh:
            refresh_admin()
    return {
        "ok": True,
        "dry_run": not apply,
        "source_csv": str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path),
        "row_count": len(entries),
        "ready_count": len(ready),
        "waiting_count": len(waiting),
        "already_logged_count": len(already),
        "waiting": waiting,
        "already_logged": already,
        "entries": ready,
        "target": str(PUBLISHED_LOG.relative_to(ROOT)),
        "action": "appended_published_log_rows" if apply else "would_append_published_log_rows",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Log a manually posted Lily Roo distribution row.")
    parser.add_argument("--id", help="Manual distribution row id, for example FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY.")
    parser.add_argument("--url", help="Public URL of the manually posted item.")
    parser.add_argument("--from-csv", help="CSV with id and public_url columns for batch manual URL logging.")
    parser.add_argument("--apply", action="store_true", help="Append to Published_Log.csv. Default is dry-run.")
    parser.add_argument("--refresh-admin", action="store_true", help="Refresh admin artifacts after appending. Requires --apply.")
    args = parser.parse_args()

    if args.refresh_admin and not args.apply:
        raise SystemExit("--refresh-admin requires --apply")
    if args.from_csv and (args.id or args.url):
        raise SystemExit("--from-csv cannot be combined with --id/--url")
    if args.from_csv:
        print(json.dumps(log_from_csv(Path(args.from_csv), apply=args.apply, refresh=args.refresh_admin), indent=2, ensure_ascii=False))
        return 0
    if not args.id or not args.url:
        raise SystemExit("Provide --id and --url, or use --from-csv.")

    row = find_row(args.id)
    public_url = validate_public_url(args.url)
    logged_row = already_logged(args.id)
    if logged_row:
        raise SystemExit(
            f"{args.id} is already logged in {PUBLISHED_LOG.relative_to(ROOT)} "
            f"as {logged_row.get('post_id_or_url') or logged_row.get('content_id') or 'an existing row'}."
        )
    payload = {
        "ok": True,
        "dry_run": not args.apply,
        **payload_for_row(row, public_url),
    }

    if args.apply:
        append_payload(payload)
        if args.refresh_admin:
            refresh_admin()
        payload["logged"] = True
    else:
        payload["action"] = "would_append_published_log"
        payload["content_id"] = args.id

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
