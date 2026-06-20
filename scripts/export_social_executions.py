#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

from social_exec_common import PUBLISHED_LOG, SOCIAL_ENV, append_published_log, get_row, load_env, song_from_row

DEFAULT_URL = "https://www.lilyroo.com/api/social/executions"
ROOT = Path(__file__).resolve().parents[1]


def auth_headers() -> dict[str, str]:
    import os

    headers = {
        "Accept": "application/json",
        "Origin": "https://www.lilyroo.com",
        "User-Agent": "Mozilla/5.0 LilyRooExecutionExport/1.0",
    }
    bearer = os.environ.get("LILYROO_EXECUTOR_BEARER_TOKEN", "").strip()
    if not bearer:
        bearer = load_env(SOCIAL_ENV).get("EXECUTOR_BEARER_TOKEN", "").strip()
    if bearer:
        headers["Authorization"] = f"Bearer {bearer}"
        return headers

    password = os.environ.get("LILYROO_ADMIN_PASSWORD", "").strip()
    if password:
        headers["X-Lilyroo-Admin-Password"] = password
    return headers


def fetch_executions(url: str) -> list[dict]:
    request = urllib.request.Request(url, headers=auth_headers(), method="GET")
    with urllib.request.urlopen(request, timeout=25) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not payload.get("ok"):
        raise RuntimeError(payload.get("error") or "execution endpoint returned ok=false")
    return payload.get("executions") or []


def logged_content_ids() -> set[str]:
    if not PUBLISHED_LOG.exists():
        return set()
    import csv

    ids = set()
    with PUBLISHED_LOG.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            content_id = (row.get("content_id") or "").strip()
            if content_id:
                ids.add(content_id)
    return ids


def main() -> int:
    parser = argparse.ArgumentParser(description="Export posted Worker execution records into Published_Log.csv.")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--refresh-admin", action="store_true", help="Refresh admin artifacts after appending posted records. Requires non-dry-run.")
    args = parser.parse_args()

    if args.refresh_admin and args.dry_run:
        raise SystemExit("--refresh-admin cannot be combined with --dry-run")

    existing = logged_content_ids()
    added = 0
    for item in fetch_executions(args.url):
        post_id = (item.get("post_id") or "").strip()
        if item.get("status") != "posted" or not post_id or post_id in existing:
            continue
        row = get_row(post_id)
        platform = item.get("platform") or row.get("platform") or "Social"
        post_url = item.get("post_url") or "posted"
        text = row.get("text") or ""
        notes = f"queue_id={post_id}; exported from Worker execution state"
        if args.dry_run:
            print(json.dumps({"post_id": post_id, "platform": platform, "post_url": post_url}, ensure_ascii=False))
        else:
            append_published_log(platform, post_url, song_from_row(row), text, notes, content_id=post_id)
        existing.add(post_id)
        added += 1
    if args.refresh_admin and not args.dry_run:
        subprocess.run(["python3", "scripts/refresh_promo_admin.py"], cwd=ROOT, check=True)
    print(json.dumps({"ok": True, "added": added, "dry_run": args.dry_run}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
