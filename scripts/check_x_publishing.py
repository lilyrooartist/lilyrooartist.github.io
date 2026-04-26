#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from post_x_from_queue import oauth1_keys
from post_x_from_queue import oauth1_header
from social_exec_common import REPO_ROOT, SOCIAL_ENV, get_row, load_env

DEFAULT_EXECUTOR_URL = "https://www.lilyroo.com/api/social/execute"
DEFAULT_READINESS_URL = "https://www.lilyroo.com/api/social/readiness"
VERIFY_CREDENTIALS_URL = "https://api.x.com/1.1/account/verify_credentials.json"
WRANGLER_CONFIG = REPO_ROOT / "workers" / "social-executor" / "wrangler.jsonc"
X_OAUTH1_SECRET_NAMES = {"X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"}


def has_keys(env: dict[str, str], names: set[str]) -> dict[str, bool]:
    return {name: bool(env.get(name)) for name in sorted(names)}


def x_auth_state(env: dict[str, str]) -> dict[str, bool]:
    oauth1 = oauth1_keys(env)
    oauth1_complete = all(oauth1.values())
    return {
        "oauth2_user_token_present": bool(env.get("X_USER_ACCESS_TOKEN", "").strip()),
        "oauth1_complete": oauth1_complete,
        "text_posting_ready": bool(env.get("X_USER_ACCESS_TOKEN", "").strip()) or oauth1_complete,
    }


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


def worker_json_request(url: str, token: str = "", payload: dict[str, Any] | None = None) -> dict[str, Any]:
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://www.lilyroo.com",
        "User-Agent": "Mozilla/5.0 LilyRooXCheck/1.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    method = "POST" if payload is not None else "GET"
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
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


def local_verify_credentials(env: dict[str, str]) -> dict[str, Any]:
    request = urllib.request.Request(
        VERIFY_CREDENTIALS_URL,
        method="GET",
        headers={"Authorization": oauth1_header("GET", VERIFY_CREDENTIALS_URL, env)},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
            return {
                "ok": True,
                "status": response.status,
                "screen_name": data.get("screen_name", ""),
                "id_str": data.get("id_str", ""),
            }
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            body_json: Any = json.loads(raw)
        except Exception:
            body_json = raw
        return {"ok": False, "status": exc.code, "body": body_json}


def x_payload(row: dict[str, str], text: str) -> dict[str, Any]:
    return {
        "postId": row.get("id", ""),
        "platform": row.get("platform", ""),
        "song": row.get("song", ""),
        "text": text,
        "replyText": row.get("reply_text", ""),
        "mediaKey": (row.get("x_media_key") or row.get("media_key") or "").strip(),
        "imageryUrl": row.get("imagery_url", ""),
        "clipUrl": row.get("clip_url", ""),
        "mediaUrl": row.get("clip_url") or row.get("imagery_url") or "",
        "dryRun": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the Lily Roo X publishing path without publishing.")
    parser.add_argument("--post-id", default="FP-AUTO-213")
    parser.add_argument("--executor-url", default=DEFAULT_EXECUTOR_URL)
    parser.add_argument("--readiness-url", default=DEFAULT_READINESS_URL)
    parser.add_argument("--executor-token", default="")
    parser.add_argument("--check-local-x-auth", action="store_true")
    parser.add_argument("--check-worker-secrets", action="store_true")
    parser.add_argument("--check-worker-readiness", action="store_true")
    parser.add_argument("--check-worker-dry-run", action="store_true")
    args = parser.parse_args()

    row = get_row(args.post_id)
    text = (row.get("text") or "").strip()
    platform = (row.get("platform") or "").lower()
    if platform != "x" and not platform.startswith("x"):
        raise RuntimeError(f'{args.post_id} is platform "{row.get("platform")}", not X')
    if not text:
        raise RuntimeError(f"{args.post_id} is missing post text")

    media_key = (row.get("x_media_key") or row.get("media_key") or "").strip()
    local_env = load_env(SOCIAL_ENV)
    local_auth = x_auth_state(local_env)
    token = args.executor_token or local_env.get("EXECUTOR_BEARER_TOKEN", "")

    report: dict[str, Any] = {
        "ok": True,
        "post_id": args.post_id,
        "local_secret_file": str(SOCIAL_ENV),
        "local_x_auth": local_auth,
        "queue_media_key": media_key,
        "queue_media_mode": "explicit-media" if media_key else "text-only",
        "local_dry_run": {
            "ok": True,
            "platform": "X",
            "dry_run": True,
            "text": text,
            "reply_text": row.get("reply_text", ""),
            "media_key": media_key,
        },
    }

    if not local_auth["text_posting_ready"]:
        report["ok"] = False

    if media_key and not (local_env.get("X_MEDIA_MAP_JSON") or local_auth["oauth1_complete"]):
        report["ok"] = False
        report["media_warning"] = (
            "This row has an explicit media key. Set X_MEDIA_MAP_JSON for pre-uploaded media "
            "or complete OAuth 1.0a keys for image upload."
        )

    if args.check_local_x_auth:
        x_auth_check = local_verify_credentials(local_env)
        report["local_x_auth_check"] = x_auth_check
        if not x_auth_check.get("ok"):
            report["ok"] = False

    if args.check_worker_secrets:
        names = worker_secret_names()
        worker_x_auth = {
            "oauth2_user_token_present": "X_USER_ACCESS_TOKEN" in names,
            "oauth1_complete": X_OAUTH1_SECRET_NAMES.issubset(names),
        }
        worker_x_auth["text_posting_ready"] = (
            worker_x_auth["oauth2_user_token_present"] or worker_x_auth["oauth1_complete"]
        )
        present = {
            "EXECUTOR_BEARER_TOKEN": "EXECUTOR_BEARER_TOKEN" in names,
            "X_USER_ACCESS_TOKEN": "X_USER_ACCESS_TOKEN" in names,
            "X_MEDIA_MAP_JSON": "X_MEDIA_MAP_JSON" in names,
            **{name: name in names for name in sorted(X_OAUTH1_SECRET_NAMES)},
        }
        report["worker_secrets_present"] = present
        report["worker_x_auth"] = worker_x_auth
        if not present["EXECUTOR_BEARER_TOKEN"] or not worker_x_auth["text_posting_ready"]:
            report["ok"] = False
        if media_key and not (present["X_MEDIA_MAP_JSON"] or worker_x_auth["oauth1_complete"]):
            report["ok"] = False

    if args.check_worker_readiness:
        readiness = worker_json_request(args.readiness_url, token)
        report["worker_readiness"] = readiness
        if readiness.get("status") != 200 or not isinstance(readiness.get("body"), dict):
            report["ok"] = False
        elif not readiness["body"].get("platforms", {}).get("x", {}).get("text_posting_ready"):
            report["ok"] = False

    if args.check_worker_dry_run:
        dry = worker_json_request(args.executor_url, token, x_payload(row, text))
        report["worker_dry_run"] = dry
        if dry.get("status") != 200 or not isinstance(dry.get("body"), dict) or not dry["body"].get("ok"):
            report["ok"] = False

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
