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
OUT = ROOT / "data" / "social_scheduler_dry_run.json"
DEFAULT_URL = "https://www.lilyroo.com/api/social/scheduler/dry-run"
ADMIN_PASSWORD_HEADER = "X-Lilyroo-Admin-Password"


def auth_value(name: str) -> str:
    explicit = os.environ.get(name, "").strip()
    if explicit:
        return explicit
    if not SOCIAL_ENV:
        return ""
    return load_env(SOCIAL_ENV).get(name, "").strip()


def auth_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://www.lilyroo.com",
        "User-Agent": "LilyRooSchedulerDryRunCapture/1.0",
    }
    bearer = auth_value("LILYROO_EXECUTOR_BEARER_TOKEN") or auth_value("EXECUTOR_BEARER_TOKEN")
    if bearer:
        headers["Authorization"] = f"Bearer {bearer}"
        return headers
    password = auth_value("LILYROO_ADMIN_PASSWORD") or auth_value("ADMIN_PASSWORD")
    if password:
        headers[ADMIN_PASSWORD_HEADER] = password
    return headers


def auth_method() -> str:
    if auth_value("LILYROO_EXECUTOR_BEARER_TOKEN") or auth_value("EXECUTOR_BEARER_TOKEN"):
        return "bearer"
    if auth_value("LILYROO_ADMIN_PASSWORD") or auth_value("ADMIN_PASSWORD"):
        return "admin_password"
    return "none"


def fetch(url: str, scheduled_time: str) -> tuple[int, dict, str]:
    body = json.dumps({"scheduledTime": scheduled_time}).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=auth_headers(), method="POST")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
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


def safe_result(item: dict) -> dict:
    return {
        "post_id": item.get("post_id", ""),
        "platform": item.get("platform", ""),
        "status": item.get("status", ""),
        "reason": item.get("reason", ""),
        "post_type": item.get("post_type", ""),
        "attempts": item.get("attempts", 0),
        "updated_at": item.get("updated_at", ""),
        "source": item.get("source", ""),
        "error_summary": str(item.get("error", ""))[:240],
    }


def summarize(payload: dict) -> dict:
    results = payload.get("results") if isinstance(payload, dict) else []
    results = results if isinstance(results, list) else []
    status_counts = Counter(str(item.get("status") or "unknown") for item in results if isinstance(item, dict))
    platform_counts = Counter(str(item.get("platform") or "Unknown") for item in results if isinstance(item, dict))
    would_post = [item for item in results if isinstance(item, dict) and item.get("status") == "would_post"]
    blocked = [item for item in results if isinstance(item, dict) and item.get("status") in {"blocked", "failed", "skipped"}]
    return {
        "due_count": int(payload.get("due_count") or 0) if isinstance(payload, dict) else 0,
        "result_count": len(results),
        "would_post_count": len(would_post),
        "blocked_count": len(blocked),
        "status_counts": dict(sorted(status_counts.items())),
        "platform_counts": dict(sorted(platform_counts.items())),
        "would_post": [safe_result(item) for item in would_post],
        "blocked": [safe_result(item) for item in blocked],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture a read-only social scheduler dry-run snapshot.")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--scheduled-time", default=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    parser.add_argument("--out", default=str(OUT.relative_to(ROOT)))
    args = parser.parse_args()

    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    status, payload, error = fetch(args.url, args.scheduled_time)
    ok = status == 200 and bool(payload.get("ok")) and payload.get("dry_run") is True
    summary = summarize(payload if isinstance(payload, dict) else {})
    snapshot = {
        "ok": ok,
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": "lilyroo-social-scheduler-dry-run",
        "url": args.url,
        "http_status": status,
        "error": error or (payload.get("error") if isinstance(payload, dict) else ""),
        "auth_method": auth_method(),
        "requested_scheduled_time": args.scheduled_time,
        "dry_run": True,
        "checked_at": payload.get("checked_at", "") if isinstance(payload, dict) else "",
        "summary": summary,
        "payload": {
            "ok": bool(payload.get("ok")) if isinstance(payload, dict) else False,
            "due_count": payload.get("due_count", 0) if isinstance(payload, dict) else 0,
            "result_count": payload.get("result_count", 0) if isinstance(payload, dict) else 0,
        },
        "action_needed": "" if ok else "Set LILYROO_ADMIN_PASSWORD or LILYROO_EXECUTOR_BEARER_TOKEN and rerun to capture scheduler dry-run state.",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": ok,
        "http_status": status,
        "due_count": summary["due_count"],
        "would_post_count": summary["would_post_count"],
        "blocked_count": summary["blocked_count"],
        "output": str(out.relative_to(ROOT)),
    }, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
