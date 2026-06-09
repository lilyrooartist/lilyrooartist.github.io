#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

try:
    from social_exec_common import SOCIAL_ENV, load_env
except ImportError:
    SOCIAL_ENV = None

    def load_env(_path):
        return {}


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "social_execution_snapshot.json"
DEFAULT_URL = "https://www.lilyroo.com/api/social/executions"
ADMIN_PASSWORD_HEADER = "X-Lilyroo-Admin-Password"


def compact_error(value: str) -> str:
    text = " ".join(str(value or "").split())
    if not text:
        return ""
    if "Confirm your identity before you can publish as this Page" in text:
        return "Facebook blocked Page publishing until identity is confirmed in the Facebook app."
    if "instagram_business_account" in text:
        return "Instagram posting could not resolve instagram_business_account; reconnect or set IG_BUSINESS_ACCOUNT_ID."
    return text[:240]


def safe_execution(item: dict) -> dict:
    return {
        "post_id": item.get("post_id", ""),
        "platform": item.get("platform", ""),
        "status": item.get("status", ""),
        "reason": item.get("reason", ""),
        "attempts": item.get("attempts", 0),
        "updated_at": item.get("updated_at", ""),
        "source": item.get("source", ""),
        "post_url": item.get("post_url", ""),
        "error_summary": compact_error(item.get("error", "")),
    }


def auth_headers(password: str = "") -> dict[str, str]:
    headers = {
        "Accept": "application/json",
        "Origin": "https://www.lilyroo.com",
        "User-Agent": "LilyRooSocialExecutionCapture/1.0",
    }
    bearer = os.environ.get("LILYROO_EXECUTOR_BEARER_TOKEN", "").strip()
    if not bearer and SOCIAL_ENV:
        bearer = load_env(SOCIAL_ENV).get("EXECUTOR_BEARER_TOKEN", "").strip()
    if bearer:
        headers["Authorization"] = f"Bearer {bearer}"
        return headers
    password = password or os.environ.get("LILYROO_ADMIN_PASSWORD", "").strip()
    if password:
        headers[ADMIN_PASSWORD_HEADER] = password
    return headers


def fetch(url: str, password: str) -> tuple[int, dict, str]:
    request = urllib.request.Request(url, headers=auth_headers(password), method="GET")
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return response.status, payload, ""
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {}
        return exc.code, payload, f"HTTP {exc.code}: {exc.reason}"
    except (urllib.error.URLError, TimeoutError) as exc:
        return 0, {}, str(exc)


def summarize(payload: dict) -> dict:
    executions = payload.get("executions") if isinstance(payload, dict) else []
    executions = executions if isinstance(executions, list) else []
    status_counts = Counter(str(item.get("status") or "unknown") for item in executions if isinstance(item, dict))
    platform_counts = Counter(str(item.get("platform") or "Unknown") for item in executions if isinstance(item, dict))
    posted = [
        item for item in executions
        if isinstance(item, dict) and item.get("status") == "posted"
    ]
    failed = [
        item for item in executions
        if isinstance(item, dict) and item.get("status") in {"failed", "blocked", "skipped"}
    ]
    return {
        "execution_count": len(executions),
        "posted_count": len(posted),
        "attention_count": len(failed),
        "status_counts": dict(sorted(status_counts.items())),
        "platform_counts": dict(sorted(platform_counts.items())),
        "latest_posted": [safe_execution(item) for item in posted[:5]],
        "latest_attention": [safe_execution(item) for item in failed[:5]],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture website social executor state without posting or logging.")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--out", default=str(OUT.relative_to(ROOT)))
    parser.add_argument("--password", default=os.environ.get("LILYROO_ADMIN_PASSWORD", ""))
    args = parser.parse_args()

    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    status, payload, error = fetch(args.url, args.password)
    ok = status == 200 and bool(payload.get("ok"))
    summary = summarize(payload if ok else {})
    snapshot = {
        "ok": ok,
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": "lilyroo-social-executor-executions",
        "url": args.url,
        "http_status": status,
        "error": error or (payload.get("error") if isinstance(payload, dict) else ""),
        "password_supplied": bool(args.password),
        "summary": summary,
        "payload": {
            "ok": bool(payload.get("ok")) if isinstance(payload, dict) else False,
            "execution_count": len(payload.get("executions") or []) if isinstance(payload, dict) else 0,
        },
        "action_needed": "" if ok else "Set LILYROO_ADMIN_PASSWORD or LILYROO_EXECUTOR_BEARER_TOKEN and rerun to capture social execution state.",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": ok,
        "http_status": status,
        "execution_count": summary["execution_count"],
        "posted_count": summary["posted_count"],
        "attention_count": summary["attention_count"],
        "output": str(out.relative_to(ROOT)),
    }, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
