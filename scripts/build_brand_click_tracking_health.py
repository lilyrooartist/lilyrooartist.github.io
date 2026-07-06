#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data" / "scheduled_posts.csv"
FUTURE = ROOT / "admin" / "future-posts.json"
REDIRECT = ROOT / "go" / "am.html"
OUT = ROOT / "data" / "brand_click_tracking_health.json"
REPORT = ROOT / "admin" / "reports" / "brand-click-tracking-health.md"
REPORT_INDEX = ROOT / "admin" / "reports" / "index.html"
ADMIN_INDEX = ROOT / "admin" / "index.html"

CAMPAIGN_PREFIX = "FP-BRAND-AM"
TRACKING_HOST = "www.lilyroo.com"
TRACKING_PATH = "/go/am.html"
EXPECTED_DESTINATIONS = {"album", "echo", "video"}


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def post_parts(post_id: str) -> dict:
    normalized = str(post_id or "").strip().lower()
    match = re.match(r"^fp-brand-am(?:-w(\d+))?-(\d{2})-.+-(x|facebook)$", normalized)
    if not match:
        return {"post_id": normalized, "wave": "unknown", "track": "", "platform": ""}
    return {
        "post_id": normalized,
        "wave": f"w{match.group(1)}" if match.group(1) else "track-moments",
        "track": match.group(2),
        "platform": match.group(3),
    }


def future_ids() -> set[str]:
    payload = read_json(FUTURE, {})
    return {
        str(post.get("id") or "").strip()
        for post in payload.get("posts") or []
        if str(post.get("id") or "").strip().startswith(CAMPAIGN_PREFIX)
    }


def tracking_urls(reply_text: str) -> list[str]:
    return re.findall(r"https://www\.lilyroo\.com/go/am\.html\?[^\s]+", reply_text or "")


def validate_url(url: str, post_id: str) -> tuple[dict, list[str]]:
    issues: list[str] = []
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    destination = (query.get("to") or [""])[0]
    p_value = (query.get("p") or [""])[0]
    expected_post = post_id.lower()

    if parsed.scheme != "https":
        issues.append("tracking_url_not_https")
    if parsed.netloc != TRACKING_HOST:
        issues.append("tracking_url_wrong_host")
    if parsed.path != TRACKING_PATH:
        issues.append("tracking_url_wrong_path")
    if p_value != expected_post:
        issues.append("tracking_url_post_id_mismatch")
    if destination not in EXPECTED_DESTINATIONS:
        issues.append("tracking_url_unknown_destination")

    return {
        "url": url,
        "destination": destination,
        "post_id_param": p_value,
        "expected_post_id_param": expected_post,
        "ok": not issues,
        "issues": issues,
    }, issues


def redirect_health() -> dict:
    text = REDIRECT.read_text(encoding="utf-8") if REDIRECT.exists() else ""
    checks = {
        "exists": REDIRECT.exists(),
        "records_click": "/api/social/click" in text,
        "uses_send_beacon": "navigator.sendBeacon" in text,
        "has_fetch_fallback": 'fetch("/api/social/click"' in text,
        "adds_utm_source": "utm_source" in text,
        "adds_utm_campaign": "analog_myth_brand_growth" in text,
        "supports_album": "album:" in text,
        "supports_echo": "echo:" in text,
        "supports_video": 'destination === "video"' in text,
    }
    return {
        "path": rel(REDIRECT),
        "status": "ready" if all(checks.values()) else "attention",
        "checks": checks,
    }


def build_payload() -> dict:
    now = datetime.now(timezone.utc)
    visible_ids = future_ids()
    rows = []
    issue_counts = Counter()
    destination_counts = Counter()
    platform_counts = Counter()
    wave_counts = Counter()
    track_counts = Counter()
    x_main_album_link_count = 0
    expected_x_main_album_link_count = 0

    for row in read_csv(QUEUE):
        post_id = str(row.get("id") or "").strip()
        if not post_id.startswith(CAMPAIGN_PREFIX) or post_id not in visible_ids:
            continue
        if str(row.get("approved") or "").strip().lower() != "yes":
            continue
        if str(row.get("execution_mode") or "").strip().lower() != "auto":
            continue

        parts = post_parts(post_id)
        urls = tracking_urls(row.get("reply_text") or "")
        main_text_urls = tracking_urls(row.get("text") or "")
        row_issues: list[str] = []
        url_results = []
        main_text_url_results = []
        destinations = set()
        for url in urls:
            result, issues = validate_url(url, post_id)
            url_results.append(result)
            row_issues.extend(issues)
            if result["destination"]:
                destinations.add(result["destination"])
                destination_counts[result["destination"]] += 1

        missing_destinations = sorted(EXPECTED_DESTINATIONS - destinations)
        for destination in missing_destinations:
            row_issues.append(f"missing_{destination}_tracking_link")
        if len(urls) != len(EXPECTED_DESTINATIONS):
            row_issues.append("unexpected_tracking_link_count")
        if not row.get("reply_text"):
            row_issues.append("missing_reply_text")

        main_album_link_ok = True
        if parts["platform"] == "x":
            expected_x_main_album_link_count += 1
            main_album_link_ok = False
            for url in main_text_urls:
                result, issues = validate_url(url, post_id)
                main_text_url_results.append(result)
                if not issues and result["destination"] == "album":
                    main_album_link_ok = True
            if main_album_link_ok:
                x_main_album_link_count += 1
            else:
                row_issues.append("missing_x_main_album_link")

        for issue in sorted(set(row_issues)):
            issue_counts[issue] += 1
        platform_counts[parts["platform"] or str(row.get("platform") or "unknown").lower()] += 1
        wave_counts[parts["wave"]] += 1
        if parts["track"]:
            track_counts[parts["track"]] += 1

        rows.append({
            "id": post_id,
            "platform": row.get("platform") or "",
            "scheduled_at": row.get("scheduled_at") or "",
            "wave": parts["wave"],
            "track": parts["track"],
            "tracking_url_count": len(urls),
            "destinations": sorted(destinations),
            "missing_destinations": missing_destinations,
            "ok": not row_issues,
            "issues": sorted(set(row_issues)),
            "tracking_urls": url_results,
            "main_text_album_link_ok": main_album_link_ok,
            "main_text_tracking_urls": main_text_url_results,
        })

    redirect = redirect_health()
    ready_rows = sum(1 for row in rows if row["ok"])
    broken_rows = len(rows) - ready_rows
    total_urls = sum(row["tracking_url_count"] for row in rows)
    expected_urls = len(rows) * len(EXPECTED_DESTINATIONS)
    status = "ready" if rows and not broken_rows and total_urls == expected_urls and redirect["status"] == "ready" else "attention"

    return {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "scheduled_posts": rel(QUEUE),
            "future_posts": rel(FUTURE),
            "redirect_page": rel(REDIRECT),
        },
        "summary": {
            "status": status,
            "future_campaign_rows": len(rows),
            "ready_future_campaign_rows": ready_rows,
            "broken_future_campaign_rows": broken_rows,
            "tracking_url_count": total_urls,
            "expected_tracking_url_count": expected_urls,
            "x_main_album_link_count": x_main_album_link_count,
            "expected_x_main_album_link_count": expected_x_main_album_link_count,
            "destination_counts": dict(sorted(destination_counts.items())),
            "platform_counts": dict(sorted(platform_counts.items())),
            "wave_counts": dict(sorted(wave_counts.items())),
            "track_counts": dict(sorted(track_counts.items())),
            "issue_counts": dict(sorted(issue_counts.items())),
            "redirect_status": redirect["status"],
            "report_path": rel(REPORT),
            "refresh_command": "python3 scripts/build_brand_click_tracking_health.py",
        },
        "redirect": redirect,
        "rows": rows,
        "guardrails": [
            "This check is read-only and does not post.",
            "Tracking links use first-party Lily Roo redirect URLs.",
            "Click capture stores campaign metadata only and does not store IP addresses.",
            "Every future Analog Myth auto post should carry album, Echo Thread, and video destinations.",
            "Every future X Analog Myth auto post should carry the album destination in the main post text.",
        ],
    }


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Brand Click Tracking Health - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Status: **{summary['status']}**",
        f"- Future campaign rows ready: **{summary['ready_future_campaign_rows']} / {summary['future_campaign_rows']}**",
        f"- Tracking URLs checked: **{summary['tracking_url_count']} / {summary['expected_tracking_url_count']}**",
        f"- X main-post album links: **{summary['x_main_album_link_count']} / {summary['expected_x_main_album_link_count']}**",
        f"- Redirect page: **{summary['redirect_status']}**",
        f"- Destinations: **{', '.join(f'{key}: {value}' for key, value in summary['destination_counts'].items()) or 'none'}**",
        f"- Issues: **{', '.join(f'{key}: {value}' for key, value in summary['issue_counts'].items()) or 'none'}**",
        "",
        "## Redirect Checks",
    ]
    for key, value in (payload.get("redirect") or {}).get("checks", {}).items():
        lines.append(f"- {key}: **{'ok' if value else 'attention'}**")
    lines.extend(["", "## Future Rows"])
    for row in payload["rows"]:
        lines.append(
            f"- `{row['id']}` {row['platform']} {row['scheduled_at']} - "
            f"**{'ready' if row['ok'] else 'attention'}** "
            f"({row['tracking_url_count']} link{'s' if row['tracking_url_count'] != 1 else ''})"
        )
        if row.get("issues"):
            lines.append(f"  - Issues: `{', '.join(row['issues'])}`")
        else:
            lines.append(f"  - Destinations: `{', '.join(row['destinations'])}`")
        if row.get("platform") == "X":
            lines.append(f"  - Main-post album link: **{'ready' if row.get('main_text_album_link_ok') else 'attention'}**")
    lines.extend(["", "## Guardrails"])
    for item in payload.get("guardrails") or []:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def replace_json_embed(html: str, block_id: str, payload) -> str:
    marker = f'<script type="application/json" id="{block_id}">'
    end_marker = "</script>"
    encoded = json.dumps(payload, indent=2, ensure_ascii=False)
    start = html.find(marker)
    if start == -1:
        return html.replace("<script>", f"\n{marker}{encoded}{end_marker}\n\n<script>", 1)
    content_start = start + len(marker)
    content_end = html.find(end_marker, content_start)
    if content_end == -1:
        raise RuntimeError(f"Could not find end marker for {block_id}")
    return html[:content_start] + encoded + html[content_end:]


def replace_text_embed(html: str, block_id: str, content: str) -> str:
    marker = f'<script type="text/plain" id="{block_id}">'
    end_marker = "</script>"
    start = html.find(marker)
    if start == -1:
        return html.replace("<script>", f"\n{marker}{content.rstrip()}{end_marker}\n\n<script>", 1)
    content_start = start + len(marker)
    content_end = html.find(end_marker, content_start)
    if content_end == -1:
        raise RuntimeError(f"Could not find end marker for {block_id}")
    return html[:content_start] + content.rstrip() + html[content_end:]


def sync_admin(payload: dict, markdown: str) -> None:
    if ADMIN_INDEX.exists():
        html = ADMIN_INDEX.read_text(encoding="utf-8")
        html = replace_json_embed(html, "embedded-brand-click-tracking-health", payload)
        html = replace_text_embed(html, "embedded-brand-click-tracking-health-report", markdown)
        ADMIN_INDEX.write_text(html, encoding="utf-8")
    if REPORT_INDEX.exists():
        html = REPORT_INDEX.read_text(encoding="utf-8")
        link = '<li><a href="/admin/reports/brand-click-tracking-health.md" target="_blank">Brand Click Tracking Health</a></li>'
        if link not in html:
            marker = '<li><a href="/admin/reports/brand-campaign-clicks.md" target="_blank">Brand Campaign Clicks</a></li>'
            if marker in html:
                html = html.replace(marker, marker + "\n        " + link, 1)
            else:
                html = html.replace("</ul>", f"        {link}\n      </ul>", 1)
            REPORT_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    payload = build_payload()
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(payload)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(payload, markdown)
    print(json.dumps({"output": rel(OUT), **payload["summary"]}, indent=2, ensure_ascii=False))
    return 0 if payload["summary"]["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
