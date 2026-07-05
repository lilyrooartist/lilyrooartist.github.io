#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html import unescape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLISHED_LOG = ROOT / "admin" / "content" / "Published_Log.csv"
SOCIAL_EXECUTIONS = ROOT / "data" / "social_execution_snapshot.json"
OUT = ROOT / "data" / "brand_post_visibility.json"
REPORT = ROOT / "admin" / "reports" / "brand-post-visibility.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"
CAMPAIGN_PREFIX = "FP-BRAND-AM"
USER_AGENT = "Mozilla/5.0 Codex brand visibility probe"
UNAVAILABLE_MARKERS = [
    "this content isn't available",
    "this content is not available",
    "content isn't available right now",
    "may have been removed",
    "changed who can see it",
]


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def read_published_rows() -> list[dict]:
    if not PUBLISHED_LOG.exists():
        return []
    with PUBLISHED_LOG.open(newline="", encoding="utf-8") as handle:
        rows = []
        for index, row in enumerate(csv.DictReader(handle), start=2):
            row["_source_row"] = index
            rows.append(row)
        return rows


def execution_lookup() -> dict[str, dict]:
    snapshot = read_json(SOCIAL_EXECUTIONS, {})
    summary = snapshot.get("summary") or {}
    rows = []
    for key in ("current_executions", "posted", "latest_posted", "latest_attention"):
        rows.extend(summary.get(key) or [])
    return {
        str(row.get("post_id") or "").strip(): row
        for row in rows
        if str(row.get("post_id") or "").strip()
    }


def campaign_rows(limit: int) -> list[dict]:
    rows = [
        row for row in read_published_rows()
        if str(row.get("content_id") or "").startswith(CAMPAIGN_PREFIX)
        and str(row.get("platform") or "").strip() in {"X", "Facebook"}
        and str(row.get("post_id_or_url") or "").strip()
    ]
    rows.sort(key=lambda row: int(row.get("_source_row") or 0), reverse=True)
    return list(reversed(rows[:limit]))


def tweet_id(value: str) -> str:
    match = re.search(r"/status/(\d+)", value or "")
    return match.group(1) if match else ""


def facebook_ids_from_value(value: str) -> list[tuple[str, str]]:
    raw = str(value or "").strip()
    ids: list[tuple[str, str]] = []
    match = re.search(r"facebook\.com/(\d+)_(\d+)", raw)
    if match:
        ids.append((match.group(1), match.group(2)))
    match = re.search(r"facebook\.com/(\d+)/posts/(\d+)", raw)
    if match:
        ids.append((match.group(1), match.group(2)))
    parsed = urllib.parse.urlparse(raw)
    if "facebook.com" in parsed.netloc:
        query = urllib.parse.parse_qs(parsed.query)
        story = (query.get("story_fbid") or [""])[0]
        page = (query.get("id") or [""])[0]
        if page and story:
            ids.append((page, story))
    if re.fullmatch(r"\d+_\d+", raw):
        page, story = raw.split("_", 1)
        ids.append((page, story))
    unique = []
    seen = set()
    for page, story in ids:
        key = (page, story)
        if key not in seen:
            seen.add(key)
            unique.append(key)
    return unique


def facebook_candidates(row: dict, execution: dict | None) -> list[str]:
    raw_url = str(row.get("post_id_or_url") or "").strip()
    values = [raw_url]
    external_id = str((execution or {}).get("external_id") or "").strip()
    if external_id:
        values.append(external_id)
    candidates = [raw_url] if raw_url else []
    for value in values:
        for page, story in facebook_ids_from_value(value):
            candidates.extend([
                f"https://www.facebook.com/permalink.php?story_fbid={story}&id={page}",
                f"https://www.facebook.com/{page}_{story}",
            ])
    return unique_urls(candidates)


def unique_urls(urls: list[str]) -> list[str]:
    seen = set()
    result = []
    for url in urls:
        if not url or url in seen:
            continue
        seen.add(url)
        result.append(url)
    return result


def request_url(url: str, accept: str = "text/html,*/*;q=0.8") -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": accept,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read(250000).decode("utf-8", errors="replace")
            return {
                "ok": True,
                "http_status": response.status,
                "final_url": response.geturl(),
                "content_type": response.headers.get("content-type") or "",
                "body": body,
                "error": "",
            }
    except urllib.error.HTTPError as error:
        body = error.read(250000).decode("utf-8", errors="replace")
        return {
            "ok": False,
            "http_status": error.code,
            "final_url": error.geturl() if hasattr(error, "geturl") else url,
            "content_type": error.headers.get("content-type") if error.headers else "",
            "body": body,
            "error": f"HTTP {error.code}",
        }
    except Exception as exc:
        return {
            "ok": False,
            "http_status": 0,
            "final_url": url,
            "content_type": "",
            "body": "",
            "error": str(exc)[:300],
        }


def plain_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", unescape(text)).strip()


def hook_terms(row: dict) -> list[str]:
    hook = re.sub(r"\s+", " ", str(row.get("hook") or "")).strip()
    if not hook:
        return []
    words = [word.strip(".,!?;:()[]\"'").lower() for word in hook.split()]
    words = [word for word in words if len(word) >= 5]
    return words[:6]


def text_matches(row: dict, text: str) -> bool:
    haystack = (text or "").lower()
    terms = hook_terms(row)
    if not terms:
        return False
    matches = sum(1 for term in terms if term in haystack)
    return matches >= min(3, len(terms))


def check_x(row: dict) -> dict:
    post_url = str(row.get("post_id_or_url") or "").strip()
    tid = tweet_id(post_url)
    if not tid:
        return visibility_row(row, "missing_tweet_id", False, "", {}, "X status URL did not contain a tweet id.")
    oembed_url = "https://publish.twitter.com/oembed?" + urllib.parse.urlencode({
        "url": f"https://twitter.com/lilyrooartist/status/{tid}",
    })
    response = request_url(oembed_url, "application/json,*/*;q=0.8")
    body = response.pop("body", "")
    text = ""
    if response["ok"]:
        try:
            payload = json.loads(body)
            text = plain_text(payload.get("html") or "")
            response["final_url"] = payload.get("url") or response.get("final_url") or oembed_url
        except json.JSONDecodeError:
            text = body
    matched = text_matches(row, text)
    visible = bool(response["ok"] and matched)
    status = "visible_copy_confirmed" if visible else "probe_failed"
    note = "X public oEmbed returned Lily Roo post copy." if visible else response.get("error") or "X oEmbed did not confirm the expected copy."
    return visibility_row(row, status, visible, oembed_url, response, note, matched)


def check_facebook(row: dict, execution: dict | None) -> dict:
    candidates = facebook_candidates(row, execution)
    attempts = []
    for url in candidates:
        response = request_url(url)
        body = response.pop("body", "")
        text = plain_text(body)
        lowered = text.lower()
        unavailable = any(marker in lowered for marker in UNAVAILABLE_MARKERS)
        matched = text_matches(row, text)
        attempts.append({
            "url": url,
            **response,
            "unavailable_marker_found": unavailable,
            "copy_matched": matched,
        })
        if response["http_status"] == 200 and not unavailable:
            status = "page_loaded_no_unavailable_marker"
            note = "Facebook public page loaded without the common unavailable-content marker."
            return visibility_row(row, status, True, url, response, note, matched, attempts)
    best = attempts[0] if attempts else {}
    if any(attempt.get("unavailable_marker_found") for attempt in attempts):
        status = "unavailable_marker_found"
        note = "Facebook returned an unavailable-content marker for this post."
    else:
        status = "probe_failed"
        note = (best.get("error") or "No Facebook candidate loaded successfully.").strip()
    return visibility_row(row, status, False, best.get("url") or "", best, note, False, attempts)


def visibility_row(
    row: dict,
    status: str,
    visible: bool,
    checked_url: str,
    response: dict,
    note: str,
    copy_matched: bool = False,
    attempts: list[dict] | None = None,
) -> dict:
    return {
        "post_id": row.get("content_id") or "",
        "platform": row.get("platform") or "",
        "published_date": row.get("date") or "",
        "source_row": row.get("_source_row") or "",
        "logged_url": row.get("post_id_or_url") or "",
        "checked_url": checked_url,
        "final_url": response.get("final_url") or "",
        "http_status": response.get("http_status") or 0,
        "content_type": response.get("content_type") or "",
        "visibility_status": status,
        "public_visibility_ok": bool(visible),
        "copy_matched": bool(copy_matched),
        "note": note,
        "attempts": attempts or [],
    }


def build_payload(limit: int) -> dict:
    rows = campaign_rows(limit)
    executions = execution_lookup()
    checked = []
    for row in rows:
        platform = str(row.get("platform") or "")
        execution = executions.get(str(row.get("content_id") or ""))
        if platform == "X":
            checked.append(check_x(row))
        elif platform == "Facebook":
            checked.append(check_facebook(row, execution))
    ok_count = sum(1 for row in checked if row["public_visibility_ok"])
    attention = [row for row in checked if not row["public_visibility_ok"]]
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "generated_at": generated_at,
        "safe_mode": True,
        "source": {
            "published_log": relative(PUBLISHED_LOG),
            "social_execution_snapshot": relative(SOCIAL_EXECUTIONS),
            "row_filter": f"{CAMPAIGN_PREFIX} X/Facebook published rows",
            "limit": limit,
        },
        "summary": {
            "status": "attention" if attention else "verified",
            "checked_post_count": len(checked),
            "public_visibility_ok_count": ok_count,
            "attention_count": len(attention),
            "x_copy_confirmed_count": sum(1 for row in checked if row["platform"] == "X" and row["copy_matched"]),
            "facebook_page_loaded_count": sum(1 for row in checked if row["platform"] == "Facebook" and row["public_visibility_ok"]),
            "report_path": relative(REPORT),
            "refresh_command": "python3 scripts/capture_brand_post_visibility.py",
        },
        "rows": checked,
        "guardrails": [
            "Read-only public URL probe; it does not publish, edit, or collect private analytics.",
            "X visibility is confirmed through public oEmbed post copy.",
            "Facebook visibility is limited to public page load checks because unauthenticated Facebook pages do not reliably expose post copy.",
            "A Facebook page load without an unavailable-content marker is treated as a visibility pass; metric capture still requires Meta API credentials.",
        ],
    }


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Brand Post Visibility - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Status: **{summary['status']}**",
        f"- Checked posts: **{summary['checked_post_count']}**",
        f"- Public visibility OK: **{summary['public_visibility_ok_count']}**",
        f"- Attention: **{summary['attention_count']}**",
        f"- X copy confirmed: **{summary['x_copy_confirmed_count']}**",
        f"- Facebook pages loaded: **{summary['facebook_page_loaded_count']}**",
        "",
        "## Rows",
    ]
    for row in payload["rows"]:
        lines.extend([
            f"- **{row['post_id']}** {row['platform']} - `{row['visibility_status']}`",
            f"  - Logged URL: {row['logged_url']}",
            f"  - Checked URL: {row['checked_url']}",
            f"  - HTTP: `{row['http_status']}`; copy matched: `{row['copy_matched']}`",
            f"  - Note: {row['note']}",
        ])
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
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    html = replace_json_embed(html, "embedded-brand-post-visibility", payload)
    html = replace_text_embed(html, "embedded-brand-post-visibility-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify public visibility of recent Analog Myth brand posts.")
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args()
    payload = build_payload(max(1, args.limit))
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(payload)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(payload, markdown)
    print(json.dumps({"output": relative(OUT), **payload["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
