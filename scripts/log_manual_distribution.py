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


def main() -> int:
    parser = argparse.ArgumentParser(description="Log a manually posted Lily Roo distribution row.")
    parser.add_argument("--id", required=True, help="Manual distribution row id, for example FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY.")
    parser.add_argument("--url", required=True, help="Public URL of the manually posted item.")
    parser.add_argument("--apply", action="store_true", help="Append to Published_Log.csv. Default is dry-run.")
    parser.add_argument("--refresh-admin", action="store_true", help="Refresh admin artifacts after appending. Requires --apply.")
    args = parser.parse_args()

    if args.refresh_admin and not args.apply:
        raise SystemExit("--refresh-admin requires --apply")

    row = find_row(args.id)
    public_url = validate_public_url(args.url)
    logged_row = already_logged(args.id)
    if logged_row:
        raise SystemExit(
            f"{args.id} is already logged in {PUBLISHED_LOG.relative_to(ROOT)} "
            f"as {logged_row.get('post_id_or_url') or logged_row.get('content_id') or 'an existing row'}."
        )
    notes = f"manual_distribution_id={args.id}; source=data/manual_distribution_packet.json"
    payload = {
        "ok": True,
        "dry_run": not args.apply,
        "post_id": args.id,
        "platform": row.get("platform") or "Manual",
        "release": row.get("release") or "",
        "url": public_url,
        "text": row.get("text") or "",
        "notes": notes,
        "target": str(PUBLISHED_LOG.relative_to(ROOT)),
    }

    if args.apply:
        append_published_log(
            row.get("platform") or "Manual",
            public_url,
            row.get("release") or "",
            row.get("text") or "",
            notes=notes,
            content_id=args.id,
        )
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
