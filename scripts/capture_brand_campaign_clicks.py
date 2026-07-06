#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from social_exec_common import SOCIAL_ENV, load_env


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "brand_campaign_clicks.json"
REPORT = ROOT / "admin" / "reports" / "brand-campaign-clicks.md"
REPORT_INDEX = ROOT / "admin" / "reports" / "index.html"
DEFAULT_URL = "https://www.lilyroo.com/api/social/clicks"


def auth_headers() -> dict[str, str]:
    env = load_env(SOCIAL_ENV)
    headers = {
        "Accept": "application/json",
        "Origin": "https://www.lilyroo.com",
        "User-Agent": "LilyRooBrandClickCapture/1.0",
    }
    bearer = os.environ.get("LILYROO_EXECUTOR_BEARER_TOKEN", "").strip() or env.get("EXECUTOR_BEARER_TOKEN", "").strip()
    if bearer:
        headers["Authorization"] = f"Bearer {bearer}"
    return headers


def fetch(url: str) -> tuple[int, dict, str]:
    request = urllib.request.Request(url, headers=auth_headers(), method="GET")
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            return response.status, json.loads(response.read().decode("utf-8")), ""
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {}
        return exc.code, payload, f"HTTP {exc.code}: {exc.reason}"
    except (urllib.error.URLError, TimeoutError) as exc:
        return 0, {}, str(exc)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def empty_summary() -> dict:
    return {
        "click_count": 0,
        "post_count": 0,
        "first_click_at": "",
        "last_click_at": "",
        "by_post_id": [],
        "by_platform": [],
        "by_destination": [],
        "by_wave": [],
        "by_track": [],
    }


def build_report(snapshot: dict) -> str:
    summary = snapshot.get("summary") or empty_summary()
    lines = [
        "# Brand Campaign Clicks - Lily Roo",
        "",
        f"Generated: {snapshot['updated_at']}",
        "",
        "## Summary",
        f"- Status: **{'ready' if snapshot.get('ok') else 'attention'}**",
        f"- Clicks captured: **{summary.get('click_count', 0)}**",
        f"- Posts with clicks: **{summary.get('post_count', 0)}**",
        f"- First click: `{summary.get('first_click_at') or 'none yet'}`",
        f"- Last click: `{summary.get('last_click_at') or 'none yet'}`",
        f"- Retention: **{snapshot.get('retention_days', 'unknown')} days**",
        "",
        "## Breakdown",
    ]
    for label, key in (
        ("Platform", "by_platform"),
        ("Destination", "by_destination"),
        ("Wave", "by_wave"),
        ("Track", "by_track"),
    ):
        rows = summary.get(key) or []
        lines.append(f"### {label}")
        if not rows:
            lines.append("- No clicks recorded yet.")
        for row in rows[:12]:
            lines.append(f"- {row.get('key')}: **{row.get('count', 0)}**")
        lines.append("")
    lines.append("## Recent Clicks")
    clicks = snapshot.get("recent_clicks") or []
    if not clicks:
        lines.append("- No clicks recorded yet.")
    for click in clicks[:20]:
        lines.append(
            f"- `{click.get('recorded_at') or ''}` {click.get('platform') or 'social'} "
            f"{click.get('destination') or 'album'} `{click.get('post_id') or ''}`"
        )
    lines.extend([
        "",
        "## Guardrails",
        "- Click capture stores campaign metadata only; it does not store IP addresses.",
        "- Public posting links continue to redirect even if telemetry is unavailable.",
        "- Use this as directional campaign evidence, not as a complete analytics replacement.",
        "",
    ])
    return "\n".join(lines)


def sync_report_index() -> None:
    if not REPORT_INDEX.exists():
        return
    html = REPORT_INDEX.read_text(encoding="utf-8")
    link = '<li><a href="/admin/reports/brand-campaign-clicks.md" target="_blank">Brand Campaign Clicks</a></li>'
    if link in html:
        return
    marker = '<li><a href="/admin/reports/brand-growth-readout.md" target="_blank">Brand Growth Readout</a></li>'
    if marker in html:
        html = html.replace(marker, marker + "\n        " + link, 1)
    else:
        html = html.replace("</ul>", f"        {link}\n      </ul>", 1)
    REPORT_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture Lily Roo Analog Myth campaign click telemetry from the social Worker.")
    parser.add_argument("--url", default=DEFAULT_URL)
    args = parser.parse_args()

    status, payload, error = fetch(args.url)
    ok = status == 200 and bool(payload.get("ok"))
    summary = payload.get("summary") if ok else empty_summary()
    clicks = payload.get("clicks") if ok else []
    snapshot = {
        "ok": ok,
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": "lilyroo-social-executor-clicks",
        "url": args.url,
        "http_status": status,
        "error": error or (payload.get("error") if isinstance(payload, dict) else ""),
        "retention_days": payload.get("retention_days") if isinstance(payload, dict) else "",
        "summary": summary or empty_summary(),
        "recent_clicks": clicks[:50] if isinstance(clicks, list) else [],
        "report_path": rel(REPORT),
        "refresh_command": "python3 scripts/capture_brand_campaign_clicks.py",
    }
    OUT.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT.write_text(build_report(snapshot), encoding="utf-8")
    sync_report_index()
    print(json.dumps({
        "ok": ok,
        "http_status": status,
        "click_count": snapshot["summary"].get("click_count", 0),
        "post_count": snapshot["summary"].get("post_count", 0),
        "output": rel(OUT),
    }, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
