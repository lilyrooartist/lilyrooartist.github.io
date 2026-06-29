#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from log_manual_distribution import already_logged, append_payload, find_row, payload_for_row


ROOT = Path(__file__).resolve().parents[1]
CLIPBOARD = ROOT / "data" / "manual_posting_clipboard.json"
OUT = ROOT / "data" / "youtube_community_url_reconciliation.json"
REPORT = ROOT / "admin" / "reports" / "youtube-community-url-reconciliation.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").lower()).strip()


def text_from_runs(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        if "simpleText" in value:
            return str(value.get("simpleText") or "")
        runs = value.get("runs")
        if isinstance(runs, list):
            return "".join(str(run.get("text") or "") for run in runs if isinstance(run, dict))
    return ""


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def extract_initial_data(html: str) -> dict:
    match = re.search(r"var ytInitialData = (\{.*?\});</script>", html)
    if not match:
        return {}
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return {}


def post_id_from_renderer(renderer: dict) -> str:
    for key in ("postId", "backstagePostId", "entityId", "post_id"):
        value = str(renderer.get(key) or "").strip()
        if value:
            return value
    endpoint = renderer.get("navigationEndpoint") or {}
    url = (((endpoint.get("commandMetadata") or {}).get("webCommandMetadata") or {}).get("url") or "")
    match = re.search(r"/post/([^/?#]+)", url)
    return match.group(1) if match else ""


def renderer_text(renderer: dict) -> str:
    candidates = [
        renderer.get("contentText"),
        renderer.get("content"),
        renderer.get("text"),
        renderer.get("title"),
        renderer.get("description"),
    ]
    parts = [text_from_runs(candidate) for candidate in candidates]
    return "\n".join(part for part in parts if part).strip()


def public_posts_from_html(html: str) -> list[dict]:
    data = extract_initial_data(html)
    posts = []
    seen = set()
    for node in walk(data):
        renderer = node.get("backstagePostRenderer") or node.get("postRenderer") or node.get("sharedPostRenderer")
        if not isinstance(renderer, dict):
            continue
        post_id = post_id_from_renderer(renderer)
        text = renderer_text(renderer)
        if not post_id and not text:
            continue
        key = post_id or text[:120]
        if key in seen:
            continue
        seen.add(key)
        posts.append({
            "post_id": post_id,
            "public_url": f"https://www.youtube.com/post/{post_id}" if post_id else "",
            "text": text,
            "text_preview": normalize(text)[:180],
        })
    if not posts:
        for post_id in sorted(set(re.findall(r"/post/([A-Za-z0-9_-]+)", html))):
            posts.append({
                "post_id": post_id,
                "public_url": f"https://www.youtube.com/post/{post_id}",
                "text": "",
                "text_preview": "",
            })
    return posts


def fetch_community_page(url: str, timeout: int) -> tuple[str, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 LilyRooPromotionBot/1.0",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.geturl(), response.read().decode("utf-8", errors="replace")


def score_match(card: dict, post: dict) -> dict:
    card_text = normalize(card.get("paste_text") or "")
    post_text = normalize(post.get("text") or "")
    if not card_text or not post_text:
        return {"score": 0, "reason": "missing_text"}
    first_line = normalize((card.get("paste_text") or "").splitlines()[0])
    if first_line and first_line in post_text:
        return {"score": 100, "reason": "first_line_exact"}
    probe = card_text[:120]
    if len(probe) >= 40 and probe in post_text:
        return {"score": 95, "reason": "leading_text_exact"}
    overlap = len(set(card_text.split()) & set(post_text.split()))
    total = max(1, len(set(card_text.split())))
    score = int((overlap / total) * 100)
    return {"score": score, "reason": "word_overlap"}


def build_payload(*, apply: bool, timeout: int) -> dict:
    clipboard = read_json(CLIPBOARD, {})
    summary = clipboard.get("summary") or {}
    url = summary.get("public_community_url") or "https://www.youtube.com/@lilyroo.artist/community"
    fetched_url = url
    fetch_error = ""
    posts = []
    try:
        fetched_url, html = fetch_community_page(url, timeout)
        posts = public_posts_from_html(html)
    except Exception as exc:  # network visibility is best-effort, not a mutation gate
        fetch_error = str(exc)

    matches = []
    waiting = []
    for card in clipboard.get("post_cards") or []:
        post_id = card.get("id") or ""
        if not card.get("postable_now") or not post_id:
            continue
        existing = already_logged(post_id)
        if existing:
            waiting.append({"id": post_id, "status": "already_logged", "url": existing.get("post_id_or_url") or ""})
            continue
        ranked = sorted(
            ({**score_match(card, post), **post} for post in posts if post.get("public_url")),
            key=lambda item: item["score"],
            reverse=True,
        )
        best = ranked[0] if ranked else {"score": 0, "reason": "no_public_posts_found"}
        if best.get("score", 0) >= 90 and best.get("public_url"):
            row = find_row(post_id)
            payload = payload_for_row(row, best["public_url"])
            matches.append({
                "id": post_id,
                "release": card.get("release") or "",
                "public_url": best["public_url"],
                "confidence": best["score"],
                "match_reason": best["reason"],
                "dry_run_command": f"python3 scripts/reconcile_youtube_community_urls.py",
                "apply_command": "python3 scripts/reconcile_youtube_community_urls.py --apply --refresh-admin",
                "log_payload": payload,
            })
        else:
            waiting.append({
                "id": post_id,
                "status": "waiting_for_public_match",
                "best_confidence": best.get("score", 0),
                "match_reason": best.get("reason", "no_match"),
            })

    if apply:
        for match in matches:
            append_payload(match["log_payload"])

    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "safe_mode": not apply,
        "source": {
            "manual_posting_clipboard": str(CLIPBOARD.relative_to(ROOT)),
            "community_url": url,
            "fetched_url": fetched_url,
            "published_log_target": "admin/content/Published_Log.csv",
        },
        "summary": {
            "status": "matches_ready" if matches else ("fetch_failed" if fetch_error else "waiting_for_public_posts"),
            "apply": apply,
            "public_post_count": len(posts),
            "match_count": len(matches),
            "waiting_count": len(waiting),
            "fetch_error": fetch_error,
            "apply_command": "python3 scripts/reconcile_youtube_community_urls.py --apply --refresh-admin" if matches else "",
            "next_action": (
                "Review matches, then run the apply command to log public URLs."
                if matches and not apply
                else (
                    "No manual YouTube Community rows are in the active plan."
                    if not waiting
                    else "Manual YouTube Community posting is removed from the active plan; remove or convert the waiting rows instead of posting them manually."
                )
            ),
        },
        "matches": matches,
        "waiting": waiting,
        "public_posts": posts[:10],
        "guardrails": [
            "Dry run only unless --apply is provided.",
            "Only matches with confidence >= 90 are loggable.",
            "This script reads the public YouTube Community page; it does not publish posts.",
        ],
    }


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# YouTube Community URL Reconciliation - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Status: **{summary['status']}**",
        f"- Public posts found: **{summary['public_post_count']}**",
        f"- Matches ready: **{summary['match_count']}**",
        f"- Waiting: **{summary['waiting_count']}**",
        f"- Apply command: `{summary.get('apply_command') or 'not available'}`",
        f"- Next action: {summary['next_action']}",
    ]
    if summary.get("fetch_error"):
        lines.append(f"- Fetch error: `{summary['fetch_error']}`")
    lines.extend(["", "## Matches"])
    if not payload["matches"]:
        lines.append("- No confident public URL matches yet.")
    for match in payload["matches"]:
        lines.append(f"- `{match['id']}` -> {match['public_url']} (`{match['confidence']}`, {match['match_reason']})")
    lines.extend(["", "## Waiting"])
    for item in payload["waiting"]:
        lines.append(f"- `{item.get('id')}`: {item.get('status')} ({item.get('match_reason', '')}, {item.get('best_confidence', '')})")
    lines.extend(["", "## Guardrails"])
    lines.extend(f"- {item}" for item in payload["guardrails"])
    lines.append("")
    return "\n".join(lines)


def replace_json_embed(html: str, block_id: str, payload) -> str:
    marker = f'<script type="application/json" id="{block_id}">'
    end_marker = "</script>"
    encoded = json.dumps(payload, indent=2, ensure_ascii=False)
    start = html.find(marker)
    if start == -1:
        return html.replace("<script>", f"\n{marker}{encoded}{end_marker}\n\n<script>", 1)
    start_content = start + len(marker)
    end = html.find(end_marker, start_content)
    if end == -1:
        raise RuntimeError(f"Could not find end marker for {block_id}")
    return html[:start_content] + encoded + html[end:]


def replace_text_embed(html: str, block_id: str, content: str) -> str:
    marker = f'<script type="text/plain" id="{block_id}">'
    end_marker = "</script>"
    start = html.find(marker)
    if start == -1:
        return html.replace("<script>", f"\n{marker}{content.rstrip()}{end_marker}\n\n<script>", 1)
    start_content = start + len(marker)
    end = html.find(end_marker, start_content)
    if end == -1:
        raise RuntimeError(f"Could not find end marker for {block_id}")
    return html[:start_content] + content.rstrip() + html[end:]


def sync_admin(payload: dict, markdown: str) -> None:
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    html = replace_json_embed(html, "embedded-youtube-community-url-reconciliation", payload)
    html = replace_text_embed(html, "embedded-youtube-community-url-reconciliation-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Find public YouTube Community URLs for pending manual Lily Roo posts.")
    parser.add_argument("--apply", action="store_true", help="Append confident matches to Published_Log.csv.")
    parser.add_argument("--refresh-admin", action="store_true", help="Refresh admin artifacts after applying matches.")
    parser.add_argument("--timeout-seconds", type=int, default=20)
    args = parser.parse_args()
    if args.refresh_admin and not args.apply:
        raise SystemExit("--refresh-admin requires --apply")

    payload = build_payload(apply=args.apply, timeout=args.timeout_seconds)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(payload)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(payload, markdown)
    if args.apply and args.refresh_admin:
        import subprocess

        subprocess.run(["python3", "scripts/refresh_promo_admin.py"], cwd=ROOT, check=True)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), **payload["summary"]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
