#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WRANGLER_CONFIG = REPO_ROOT / "workers" / "social-executor" / "wrangler.jsonc"
OUT = REPO_ROOT / "data" / "live_social_metrics.json"
DEFAULT_URL = "https://www.lilyroo.com/api/social/metrics"


def admin_password() -> str:
    explicit = os.environ.get("LILYROO_ADMIN_PASSWORD", "").strip()
    if explicit:
        return explicit
    text = WRANGLER_CONFIG.read_text(encoding="utf-8")
    match = re.search(r'"ADMIN_PASSWORD"\s*:\s*"([^"]+)"', text)
    return match.group(1) if match else ""


def fetch_metrics(url: str, password: str) -> dict:
    headers = {
        "Accept": "application/json",
        "User-Agent": "LilyRooMetricsCapture/1.0",
    }
    if password:
        headers["X-Lilyroo-Admin-Password"] = password
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            payload = json.loads(response.read().decode("utf-8"))
            payload["capture_status"] = response.status
            return payload
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            body = json.loads(raw)
        except Exception:
            body = {"raw": raw[:300]}
        return {
            "ok": False,
            "capture_status": exc.code,
            "error": body.get("error") or body,
        }


def main() -> int:
    url = os.environ.get("LILYROO_METRICS_URL", DEFAULT_URL).strip() or DEFAULT_URL
    payload = fetch_metrics(url, admin_password())
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    platforms = sorted((payload.get("platforms") or {}).keys())
    print(json.dumps({
        "ok": bool(payload.get("ok")),
        "capture_status": payload.get("capture_status"),
        "updated_at": payload.get("updated_at"),
        "platforms": platforms,
        "output": str(OUT.relative_to(REPO_ROOT)),
    }, indent=2))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
