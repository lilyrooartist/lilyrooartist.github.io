#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "executor_readiness_snapshot.json"
DEFAULT_URL = "https://www.lilyroo.com/api/social/readiness"
ADMIN_PASSWORD_HEADER = "X-Lilyroo-Admin-Password"


def fetch(url: str, password: str) -> tuple[int, dict, str]:
    request = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "LilyRooExecutorReadinessCapture/1.0",
        ADMIN_PASSWORD_HEADER: password,
    })
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw), ""
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {}
        return exc.code, payload, f"HTTP {exc.code}: {exc.reason}"
    except (urllib.error.URLError, TimeoutError) as exc:
        return 0, {}, str(exc)


def platform_summary(payload: dict) -> dict:
    platforms = payload.get("platforms") if isinstance(payload, dict) else {}
    platforms = platforms or {}
    checks = {
        "X": bool((platforms.get("x") or {}).get("text_posting_ready")),
        "Instagram": bool((platforms.get("instagram") or {}).get("ready")),
        "TikTok": bool((platforms.get("tiktok") or {}).get("ready")),
        "Facebook": bool((platforms.get("facebook") or {}).get("ready")),
        "YouTube Community": bool((platforms.get("youtube") or {}).get("ready")),
    }
    return {
        "ready_platforms": [platform for platform, ready in checks.items() if ready],
        "blocked_platforms": [platform for platform, ready in checks.items() if not ready],
        "platforms": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture Lily Roo social executor readiness without posting.")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--out", default=str(OUT.relative_to(ROOT)))
    parser.add_argument("--password", default=os.environ.get("LILYROO_ADMIN_PASSWORD", ""))
    args = parser.parse_args()

    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    status, payload, error = fetch(args.url, args.password)
    summary = platform_summary(payload)
    snapshot = {
        "ok": status == 200 and bool(payload),
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": "lilyroo-social-executor-readiness",
        "url": args.url,
        "http_status": status,
        "error": error,
        "password_supplied": bool(args.password),
        "summary": summary,
        "payload": payload,
        "action_needed": "" if status == 200 else "Set LILYROO_ADMIN_PASSWORD and rerun to capture executor readiness.",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": snapshot["ok"],
        "http_status": status,
        "ready_platforms": summary["ready_platforms"],
        "blocked_platforms": summary["blocked_platforms"],
        "output": str(out.relative_to(ROOT)),
    }, indent=2))
    return 0 if snapshot["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
