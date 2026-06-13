#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "promo_refresh_workflow_status.json"
REPO = "lilyrooartist/lilyrooartist.github.io"
WORKFLOW = "promo-admin-refresh.yml"
API_URL = f"https://api.github.com/repos/{REPO}/actions/workflows/{WORKFLOW}/runs?per_page=5"
ACTIONS_URL = f"https://github.com/{REPO}/actions/workflows/{WORKFLOW}"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sanitize_run(run: dict) -> dict:
    return {
        "id": run.get("id"),
        "status": run.get("status") or "",
        "conclusion": run.get("conclusion") or "",
        "event": run.get("event") or "",
        "created_at": run.get("created_at") or "",
        "updated_at": run.get("updated_at") or "",
        "html_url": run.get("html_url") or "",
        "head_branch": run.get("head_branch") or "",
        "head_sha": run.get("head_sha") or "",
    }


def action_needed(latest: dict | None, error: str = "") -> str:
    if error:
        return "Review GitHub Actions API access, then rerun workflow status capture."
    if not latest:
        return "Run the promo admin refresh workflow once so the dashboard can capture a latest run."
    status = latest.get("status") or ""
    conclusion = latest.get("conclusion") or ""
    if status in {"queued", "in_progress"}:
        return ""
    if conclusion == "success":
        return ""
    if conclusion:
        return f"Open the latest promo admin refresh workflow run and fix the {conclusion} result."
    return "Open the latest promo admin refresh workflow run and review its status."


def fetch_runs() -> tuple[int, dict, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "lilyroo-promo-admin-refresh",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(API_URL, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return int(response.status), payload, ""
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return int(exc.code), {}, body[:600]
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return 0, {}, str(exc)


def build_snapshot() -> dict:
    status, payload, error = fetch_runs()
    runs = [sanitize_run(run) for run in payload.get("workflow_runs", [])[:5]]
    latest = runs[0] if runs else None
    latest_ok = bool(latest) and (
        latest.get("status") in {"queued", "in_progress"}
        or latest.get("conclusion") == "success"
    )
    api_ok = status == 200 and not error
    needed = action_needed(latest, error if not api_ok else "")
    return {
        "ok": bool(api_ok and latest_ok),
        "updated_at": utc_now(),
        "source": "github-actions-workflow-runs",
        "repo": REPO,
        "workflow": WORKFLOW,
        "api_url": API_URL,
        "actions_url": ACTIONS_URL,
        "http_status": status,
        "error": error,
        "latest_run": latest or {},
        "recent_runs": runs,
        "action_needed": needed,
    }


def main() -> int:
    snapshot = build_snapshot()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": snapshot["ok"],
        "http_status": snapshot["http_status"],
        "latest_status": (snapshot["latest_run"] or {}).get("status", ""),
        "latest_conclusion": (snapshot["latest_run"] or {}).get("conclusion", ""),
        "output": str(OUT.relative_to(ROOT)),
    }, indent=2))
    return 0 if snapshot["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
