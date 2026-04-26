#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from post_meta_from_queue import facebook_post
from social_exec_common import REPO_ROOT, SOCIAL_ENV, get_row, load_env

REQUIRED_WORKER_SECRETS = {"EXECUTOR_BEARER_TOKEN", "META_LONG_LIVED_TOKEN", "FB_PAGE_ID"}
REQUIRED_LOCAL_SECRETS = {"META_LONG_LIVED_TOKEN", "FB_PAGE_ID"}
DEFAULT_EXECUTOR_URL = "https://www.lilyroo.com/api/social/execute"
WRANGLER_CONFIG = REPO_ROOT / "workers" / "social-executor" / "wrangler.jsonc"


def has_keys(env: dict[str, str], names: set[str]) -> dict[str, bool]:
    return {name: bool(env.get(name)) for name in sorted(names)}


def worker_secret_names() -> set[str]:
    result = subprocess.run(
        ["npx", "wrangler", "secret", "list", "--config", str(WRANGLER_CONFIG)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "wrangler secret list failed").strip())
    data = json.loads(result.stdout or "[]")
    return {str(item.get("name", "")) for item in data if isinstance(item, dict)}


def worker_dry_run(url: str, payload: dict[str, Any], token: str = "") -> dict[str, Any]:
    body = json.dumps({**payload, "dryRun": True}).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://www.lilyroo.com",
        "User-Agent": "Mozilla/5.0 LilyRooSocialCheck/1.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return {
                "status": response.status,
                "body": json.loads(response.read().decode("utf-8")),
            }
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            body_json: Any = json.loads(raw)
        except Exception:
            body_json = raw
        return {"status": exc.code, "body": body_json}


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the Lily Roo Facebook publishing path without publishing.")
    parser.add_argument("--post-id", default="FP-AUTO-210")
    parser.add_argument("--executor-url", default=DEFAULT_EXECUTOR_URL)
    parser.add_argument("--executor-token", default="")
    parser.add_argument("--check-worker-secrets", action="store_true")
    parser.add_argument("--check-worker-dry-run", action="store_true")
    parser.add_argument("--require-local-secrets", action="store_true")
    args = parser.parse_args()

    row = get_row(args.post_id)
    text = (row.get("text") or "").strip()
    if "facebook" not in (row.get("platform") or "").lower():
        raise RuntimeError(f'{args.post_id} is platform "{row.get("platform")}", not Facebook')
    if not text:
        raise RuntimeError(f"{args.post_id} is missing post text")

    local_env = load_env(SOCIAL_ENV)
    dry_run = facebook_post(row, text, local_env, True)
    payload = {
        "postId": row.get("id", ""),
        "platform": row.get("platform", ""),
        "song": row.get("song", ""),
        "text": text,
        "replyText": row.get("reply_text", ""),
        "mediaKey": row.get("media_key", ""),
        "imageryUrl": row.get("imagery_url", ""),
        "clipUrl": row.get("clip_url", ""),
        "mediaUrl": row.get("clip_url") or row.get("imagery_url") or "",
    }

    report: dict[str, Any] = {
        "ok": True,
        "post_id": args.post_id,
        "local_secret_file": str(SOCIAL_ENV),
        "local_secrets_present": has_keys(local_env, REQUIRED_LOCAL_SECRETS),
        "local_dry_run": dry_run,
    }

    if args.check_worker_secrets:
        names = worker_secret_names()
        present = {name: name in names for name in sorted(REQUIRED_WORKER_SECRETS)}
        report["worker_secrets_present"] = present
        if not all(present.values()):
            report["ok"] = False

    if args.check_worker_dry_run:
        token = args.executor_token or local_env.get("EXECUTOR_BEARER_TOKEN", "")
        dry = worker_dry_run(args.executor_url, payload, token)
        report["worker_dry_run"] = dry
        if dry.get("status") != 200 or not isinstance(dry.get("body"), dict) or not dry["body"].get("ok"):
            report["ok"] = False

    if args.require_local_secrets and not all(report["local_secrets_present"].values()):
        report["ok"] = False

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
