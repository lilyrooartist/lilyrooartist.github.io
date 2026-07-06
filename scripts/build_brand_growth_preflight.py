#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from capture_scheduler_dry_run import auth_method, fetch, summarize  # noqa: E402


FUTURE = ROOT / "admin" / "future-posts.json"
READOUT = ROOT / "data" / "brand_growth_readout.json"
OUT = ROOT / "data" / "brand_growth_preflight.json"
REPORT = ROOT / "admin" / "reports" / "brand-growth-preflight.md"
REPORT_INDEX = ROOT / "admin" / "reports" / "index.html"
ADMIN_INDEX = ROOT / "admin" / "index.html"
CAMPAIGN_ID_PREFIX = "FP-BRAND-AM"


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def parse_datetime(value: str | None) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def iso_z(value: datetime | None) -> str:
    if not value:
        return ""
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def git_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def queue_url() -> str:
    repository = os.environ.get("GITHUB_REPOSITORY", "").strip() or "lilyrooartist/lilyrooartist.github.io"
    sha = os.environ.get("GITHUB_SHA", "").strip() or git_output(["rev-parse", "HEAD"])
    return f"https://raw.githubusercontent.com/{repository}/{sha}/admin/future-posts.json" if sha else ""


def local_first_party_static(url: str) -> Path | None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return None
    if parsed.netloc not in {"www.lilyroo.com", "lilyroo.com"}:
        return None
    path = urllib.parse.unquote(parsed.path or "/").lstrip("/")
    if not path or path.endswith("/"):
        path = f"{path}index.html"
    candidate = (ROOT / path).resolve()
    root = ROOT.resolve()
    if candidate == root or root not in candidate.parents:
        return None
    return candidate


def local_content_type(path: Path) -> str:
    suffix = path.suffix.lower()
    return {
        ".html": "text/html",
        ".htm": "text/html",
        ".json": "application/json",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".mp4": "video/mp4",
    }.get(suffix, "application/octet-stream")


def next_window(posts: list[dict], now: datetime) -> dict:
    campaign = [post for post in posts if str(post.get("id") or "").startswith(CAMPAIGN_ID_PREFIX)]
    by_day: dict[str, list[dict]] = {}
    for post in campaign:
        scheduled = parse_datetime(post.get("scheduled_at"))
        if not scheduled:
            continue
        by_day.setdefault(scheduled.date().isoformat(), []).append(post)
    for day, day_posts in sorted(by_day.items()):
        parsed = [parse_datetime(post.get("scheduled_at")) for post in day_posts]
        parsed = [item for item in parsed if item]
        if not parsed:
            continue
        last_at = max(parsed)
        if last_at >= now - timedelta(minutes=5):
            scheduled_time = last_at + timedelta(minutes=1)
            return {
                "date": day,
                "posts": sorted(day_posts, key=lambda post: post.get("scheduled_at") or ""),
                "scheduled_time": scheduled_time,
            }
    return {"date": "", "posts": [], "scheduled_time": None}


def measurement_due_time(posts: list[dict], fallback: datetime | None) -> datetime | None:
    parsed = [parse_datetime(post.get("scheduled_at")) for post in posts]
    parsed = [item for item in parsed if item]
    if parsed:
        return max(parsed) + timedelta(hours=24)
    if fallback:
        return fallback + timedelta(hours=24)
    return None


def check_url(url: str, label: str, timeout: int = 20) -> dict:
    if not url:
        return {"label": label, "url": "", "ok": False, "status": 0, "content_type": "", "content_length": "", "error": "missing_url"}
    local_path = local_first_party_static(url)
    if local_path and local_path.exists() and local_path.is_file():
        return {
            "label": label,
            "url": url,
            "ok": True,
            "status": 200,
            "final_url": url,
            "content_type": local_content_type(local_path),
            "content_length": str(local_path.stat().st_size),
            "error": "",
            "source": "local_static_file",
        }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, headers=headers, method=method)
        if method == "GET":
            request.add_header("Range", "bytes=0-0")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return {
                    "label": label,
                    "url": url,
                    "ok": 200 <= response.status < 400,
                    "status": response.status,
                    "final_url": response.geturl(),
                    "content_type": response.headers.get("content-type", ""),
                    "content_length": response.headers.get("content-length", ""),
                    "error": "",
                }
        except urllib.error.HTTPError as exc:
            if method == "HEAD" and exc.code in {403, 405, 501}:
                continue
            if exc.code in {403, 429} and "distrokid.com/hyperfollow/" in url:
                return {
                    "label": label,
                    "url": url,
                    "ok": False,
                    "status": exc.code,
                    "content_type": "",
                    "content_length": "",
                    "error": f"HTTP {exc.code}: {exc.reason}",
                    "readiness_warning": True,
                    "warning_reason": "distrokid_bot_blocked",
                }
            if exc.code == 429 and ("youtube.com" in url or "youtu.be" in url):
                return {
                    "label": label,
                    "url": url,
                    "ok": False,
                    "status": exc.code,
                    "content_type": "",
                    "content_length": "",
                    "error": f"HTTP {exc.code}: {exc.reason}",
                    "readiness_warning": True,
                    "warning_reason": "youtube_rate_limited",
                }
            return {"label": label, "url": url, "ok": False, "status": exc.code, "content_type": "", "content_length": "", "error": f"HTTP {exc.code}: {exc.reason}"}
        except (urllib.error.URLError, TimeoutError) as exc:
            if method == "HEAD":
                continue
            return {"label": label, "url": url, "ok": False, "status": 0, "content_type": "", "content_length": "", "error": str(exc)}
    return {"label": label, "url": url, "ok": False, "status": 0, "content_type": "", "content_length": "", "error": "unreachable"}


def link_checks(posts: list[dict]) -> list[dict]:
    checks = []
    seen: set[tuple[str, str]] = set()
    for post in posts:
        post_id = str(post.get("id") or "")
        if post.get("imagery_url"):
            key = (post_id, "imagery_url")
            seen.add(key)
            checks.append(check_url(str(post.get("imagery_url") or ""), f"{post_id} imagery_url"))
        for line in str(post.get("reply_text") or "").splitlines():
            if ": " not in line:
                continue
            label, url = line.split(": ", 1)
            if label not in {"Listen", "Album page", "Echo Thread", "Track video", "Analog Myth", "Track", "Playlist"}:
                continue
            key = (post_id, label)
            if key in seen:
                continue
            seen.add(key)
            checks.append(check_url(url.strip(), f"{post_id} {label}"))
    return checks


def expected_ids(posts: list[dict]) -> list[str]:
    return [str(post.get("id") or "").strip() for post in posts if str(post.get("id") or "").strip()]


def build_payload() -> dict:
    now = datetime.now(timezone.utc)
    future = read_json(FUTURE, {})
    readout = read_json(READOUT, {})
    posts = future.get("posts") or []
    window = next_window(posts, now)
    expected = expected_ids(window["posts"])
    scheduled_time = window.get("scheduled_time")
    current_measurement_due = measurement_due_time(window["posts"], scheduled_time)
    q_url = queue_url()

    scheduler_queue_source = "commit_queue_url" if q_url else "none"
    scheduler_fallback_reason = ""
    if scheduled_time and q_url:
        status, scheduler_payload, error = fetch(
            "https://www.lilyroo.com/api/social/scheduler/dry-run",
            iso_z(scheduled_time),
            q_url,
        )
        if status != 200 or not (isinstance(scheduler_payload, dict) and scheduler_payload.get("ok")):
            first_status = status
            first_error = error or (scheduler_payload.get("error") if isinstance(scheduler_payload, dict) else "")
            status, scheduler_payload, error = fetch(
                "https://www.lilyroo.com/api/social/scheduler/dry-run",
                iso_z(scheduled_time),
                "",
            )
            scheduler_queue_source = "live_queue_fallback"
            scheduler_fallback_reason = f"Commit queue probe returned HTTP {first_status}: {first_error or 'scheduler probe failed'}"
    else:
        status, scheduler_payload, error = 0, {}, "no future campaign window"
    scheduler_summary = summarize(scheduler_payload if isinstance(scheduler_payload, dict) else {})
    would_post_ids = [row.get("post_id") for row in scheduler_summary.get("would_post") or [] if row.get("post_id")]
    blocked_ids = [row.get("post_id") for row in scheduler_summary.get("blocked") or [] if row.get("post_id")]
    missing_due = [post_id for post_id in expected if post_id not in would_post_ids]
    unexpected_due = [post_id for post_id in would_post_ids if post_id not in expected]
    checks = link_checks(window["posts"])
    check_counts = Counter("ok" if item.get("ok") else "failed" for item in checks)
    warning_count = sum(1 for item in checks if item.get("readiness_warning"))
    blocking_failed_count = sum(1 for item in checks if not item.get("ok") and not item.get("readiness_warning"))
    ready = (
        bool(expected)
        and status == 200
        and scheduler_summary.get("would_post_count") == len(expected)
        and scheduler_summary.get("blocked_count") == 0
        and not missing_due
        and not unexpected_due
        and blocking_failed_count == 0
    )
    payload = {
        "generated_at": iso_z(now),
        "safe_mode": True,
        "source": {
            "future_posts": rel(FUTURE),
            "brand_growth_readout": rel(READOUT),
            "scheduler_endpoint": "https://www.lilyroo.com/api/social/scheduler/dry-run",
            "queue_url": q_url,
        },
        "summary": {
            "status": "ready" if ready else "needs_attention",
            "next_window_date": window.get("date", ""),
            "scheduled_time": iso_z(scheduled_time),
            "expected_post_count": len(expected),
            "expected_post_ids": expected,
            "scheduler_http_status": status,
            "scheduler_auth_method": auth_method(),
            "scheduler_queue_source": scheduler_queue_source,
            "scheduler_fallback_reason": scheduler_fallback_reason,
            "scheduler_due_count": scheduler_summary.get("due_count", 0),
            "scheduler_would_post_count": scheduler_summary.get("would_post_count", 0),
            "scheduler_blocked_count": scheduler_summary.get("blocked_count", 0),
            "missing_due_ids": missing_due,
            "unexpected_due_ids": unexpected_due,
            "blocked_ids": blocked_ids,
            "link_check_count": len(checks),
            "link_ok_count": check_counts.get("ok", 0),
            "link_failed_count": check_counts.get("failed", 0),
            "link_warning_count": warning_count,
            "link_blocking_failed_count": blocking_failed_count,
            "next_proof_due_at": iso_z(scheduled_time),
            "next_measurement_due_at": iso_z(current_measurement_due),
            "readout_next_proof_due_at": (readout.get("summary") or {}).get("next_proof_due_at", ""),
            "readout_next_measurement_due_at": (readout.get("summary") or {}).get("next_measurement_due_at", ""),
            "error": error,
        },
        "scheduler_summary": scheduler_summary,
        "link_checks": checks,
        "next_window_posts": [
            {
                "id": post.get("id") or "",
                "platform": post.get("platform") or "",
                "scheduled_at": post.get("scheduled_at") or "",
                "execution_mode": post.get("execution_mode") or "",
                "post_type": post.get("post_type") or "",
                "text": post.get("text") or "",
            }
            for post in window["posts"]
        ],
        "guardrails": [
            "Preflight is read-only; it calls the scheduler dry-run endpoint and HEAD-checks public URLs.",
            "It does not publish, approve, mutate, or import metrics.",
            "A ready preflight proves only that the next window is executable at the simulated due time.",
            "DistroKid HyperFollow 403/429 checks are non-blocking warnings because GitHub-hosted probes can be bot-filtered while the browser-visible public link remains the intended listening hub.",
            "YouTube 429 link checks are non-blocking warnings because GitHub-hosted probes can be rate-limited while the scheduler and Lily Roo-hosted links remain ready.",
        ],
    }
    return payload


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Brand Growth Preflight - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Status: **{summary['status']}**",
        f"- Next window: **{summary.get('next_window_date') or 'n/a'}** at `{summary.get('scheduled_time') or 'n/a'}`",
        f"- Expected posts: **{summary.get('expected_post_count', 0)}**",
        f"- Scheduler: HTTP **{summary.get('scheduler_http_status')}**, auth `{summary.get('scheduler_auth_method')}`, due **{summary.get('scheduler_due_count')}**, would post **{summary.get('scheduler_would_post_count')}**, blocked **{summary.get('scheduler_blocked_count')}**",
        f"- Link checks: **{summary.get('link_ok_count')} ok**, **{summary.get('link_failed_count')} failed**, **{summary.get('link_warning_count', 0)} warning**, **{summary.get('link_blocking_failed_count', summary.get('link_failed_count', 0))} blocking failed**",
        f"- Current window proof due: `{summary.get('next_proof_due_at') or 'n/a'}`",
        f"- Current window measurement due: `{summary.get('next_measurement_due_at') or 'n/a'}`",
        "",
        "## Expected Posts",
    ]
    for post in payload.get("next_window_posts") or []:
        lines.append(f"- `{post['id']}` {post['platform']} at `{post['scheduled_at']}`")
    if summary.get("missing_due_ids"):
        lines.extend(["", "## Missing From Dry Run"])
        for post_id in summary["missing_due_ids"]:
            lines.append(f"- `{post_id}`")
    if summary.get("unexpected_due_ids"):
        lines.extend(["", "## Unexpected Dry-Run Rows"])
        for post_id in summary["unexpected_due_ids"]:
            lines.append(f"- `{post_id}`")
    if summary.get("blocked_ids"):
        lines.extend(["", "## Blocked Rows"])
        for post_id in summary["blocked_ids"]:
            lines.append(f"- `{post_id}`")
    lines.extend(["", "## Link Checks"])
    for item in payload.get("link_checks") or []:
        marker = "ok" if item.get("ok") else ("warning" if item.get("readiness_warning") else "failed")
        detail = item.get("content_type") or item.get("error") or ""
        lines.append(f"- **{marker}** `{item.get('label')}` {item.get('status')} {detail}")
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


def sync_report_index() -> None:
    if not REPORT_INDEX.exists():
        return
    html = REPORT_INDEX.read_text(encoding="utf-8")
    link = '<li><a href="/admin/reports/brand-growth-preflight.md" target="_blank">Brand Growth Preflight</a></li>'
    if link in html:
        return
    marker = '<li><a href="/admin/reports/brand-growth-readout.md" target="_blank">Brand Growth Readout</a></li>'
    if marker in html:
        html = html.replace(marker, marker + "\n        " + link, 1)
        REPORT_INDEX.write_text(html, encoding="utf-8")


def sync_admin(payload: dict, markdown: str) -> None:
    if ADMIN_INDEX.exists():
        html = ADMIN_INDEX.read_text(encoding="utf-8")
        html = replace_json_embed(html, "embedded-brand-growth-preflight", payload)
        html = replace_text_embed(html, "embedded-brand-growth-preflight-report", markdown)
        ADMIN_INDEX.write_text(html, encoding="utf-8")
    sync_report_index()


def main() -> int:
    payload = build_payload()
    markdown = build_markdown(payload)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(payload, markdown)
    print(json.dumps({"output": rel(OUT), **payload["summary"]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
