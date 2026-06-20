#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from typing import Any

from social_exec_common import SOCIAL_ENV, get_row, load_env


DEFAULT_EXECUTOR_URL = "https://www.lilyroo.com/api/social/execute"


def row_payload(row: dict[str, str]) -> dict[str, Any]:
    return {
        "postId": row.get("id", ""),
        "platform": row.get("platform", ""),
        "song": row.get("song", ""),
        "text": row.get("text", ""),
        "replyText": row.get("reply_text", ""),
        "mediaKey": row.get("media_key") or row.get("x_media_key") or "",
        "imageryUrl": row.get("imagery_url", ""),
        "clipUrl": row.get("clip_url", ""),
        "mediaUrl": row.get("clip_url") or row.get("imagery_url") or "",
        "approved": row.get("approved", ""),
        "executionMode": row.get("execution_mode", ""),
        "postType": row.get("post_type", ""),
        "desiredPrivacy": row.get("desired_privacy", ""),
    }


def worker_dry_run(url: str, payload: dict[str, Any], token: str = "") -> dict[str, Any]:
    body = json.dumps({**payload, "dryRun": True}).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://www.lilyroo.com",
        "User-Agent": "Mozilla/5.0 LilyRooSocialExecutorDryRun/1.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            return {
                "status": response.status,
                "body": json.loads(response.read().decode("utf-8")),
            }
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            body_json: Any = json.loads(raw)
        except json.JSONDecodeError:
            body_json = raw
        return {"status": exc.code, "body": body_json}


def main() -> int:
    parser = argparse.ArgumentParser(description="Check a scheduled social post through the worker dry-run path.")
    parser.add_argument("--post-id", required=True)
    parser.add_argument("--executor-url", default=DEFAULT_EXECUTOR_URL)
    parser.add_argument("--executor-token", default="")
    args = parser.parse_args()

    row = get_row(args.post_id)
    token = args.executor_token or load_env(SOCIAL_ENV).get("EXECUTOR_BEARER_TOKEN", "")
    dry = worker_dry_run(args.executor_url, row_payload(row), token)
    body = dry.get("body") if isinstance(dry.get("body"), dict) else {}
    report = {
        "ok": dry.get("status") == 200 and bool(body.get("ok")) and bool(body.get("executable")),
        "post_id": args.post_id,
        "platform": row.get("platform", ""),
        "approved": row.get("approved", ""),
        "worker_dry_run": dry,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
