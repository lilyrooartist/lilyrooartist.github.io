#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic

from capture_youtube_music_release import MetaParser, fetch_page


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT = REPO_ROOT / "data" / "store-verification" / "youtube_music_release_search_snapshot.json"
SEARCH_ENDPOINTS = [
    "https://lite.duckduckgo.com/lite/",
    "https://html.duckduckgo.com/html/",
]
REQUEST_TIMEOUT_SECONDS = 4
SEARCH_DEADLINE_SECONDS = 22


def request_text(url: str, timeout_seconds: float = REQUEST_TIMEOUT_SECONDS) -> tuple[int, str, str]:
    request = urllib.request.Request(url, headers={
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent": "LilyRooYouTubeMusicStoreVerifier/1.0",
    })
    try:
        with urllib.request.urlopen(request, timeout=max(1, timeout_seconds)) as response:
            return response.status, response.read().decode("utf-8", errors="replace"), ""
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace"), f"HTTP {exc.code}: {exc.reason}"
    except urllib.error.URLError as exc:
        return 0, "", str(exc.reason)


def normalize_watch_url(url: str) -> str:
    parsed = urllib.parse.urlparse(html.unescape(url))
    query = urllib.parse.parse_qs(parsed.query)
    video_id = (query.get("v") or [""])[0]
    if not video_id:
        return ""
    return f"https://music.youtube.com/watch?v={video_id}"


def youtube_music_urls(text: str) -> list[str]:
    decoded = html.unescape(text)
    raw_urls = set(re.findall(r"https?://(?:music|www)\.youtube\.com/watch\?v=[A-Za-z0-9_-]+", decoded))
    for encoded in re.findall(r"uddg=([^&\"'>]+)", decoded):
        url = urllib.parse.unquote(encoded)
        if re.match(r"https?://(?:music|www)\.youtube\.com/watch\?v=[A-Za-z0-9_-]+", url):
            raw_urls.add(url)
    return sorted({url for raw in raw_urls if (url := normalize_watch_url(raw))})


def search_urls(artist: str, title: str) -> tuple[list[str], list[dict]]:
    queries = [
        f'site:music.youtube.com/watch "{title}" "{artist}"',
        f'"{title}" "{artist}" "music.youtube.com/watch"',
        f'site:youtube.com/watch "{title}" "{artist}"',
    ]
    found: set[str] = set()
    attempts = []
    deadline = monotonic() + SEARCH_DEADLINE_SECONDS
    for query in queries:
        for endpoint in SEARCH_ENDPOINTS:
            remaining = deadline - monotonic()
            if remaining <= 1:
                attempts.append({
                    "query": query,
                    "endpoint": endpoint,
                    "http_status": 0,
                    "error": f"Skipped because search deadline {SEARCH_DEADLINE_SECONDS}s was reached.",
                    "candidate_count": 0,
                    "request_timeout_seconds": 0,
                    "skipped_due_to_deadline": True,
                })
                continue
            url = endpoint + "?" + urllib.parse.urlencode({"q": query})
            request_timeout = min(REQUEST_TIMEOUT_SECONDS, remaining)
            status, body, error = request_text(url, request_timeout)
            urls = youtube_music_urls(body)
            found.update(urls)
            attempts.append({
                "query": query,
                "endpoint": endpoint,
                "http_status": status,
                "error": error,
                "candidate_count": len(urls),
                "request_timeout_seconds": round(request_timeout, 2),
            })
    return sorted(found), attempts


def candidate_snapshot(url: str, artist: str, title: str) -> dict:
    try:
        page, status = fetch_page(url)
    except Exception as exc:  # noqa: BLE001 - snapshot should preserve public lookup failures.
        return {
            "release_url": url,
            "ok": False,
            "error": str(exc),
        }
    parser = MetaParser()
    parser.feed(page)
    public_title = (parser.meta.get("og:title") or parser.title).strip()
    description = parser.meta.get("og:description") or parser.meta.get("description") or ""
    canonical_title = f"{title} - {artist}"
    title_matches = public_title in {title, canonical_title}
    parsed = urllib.parse.urlparse(url)
    video_id = urllib.parse.parse_qs(parsed.query).get("v", [""])[0]
    return {
        "release_url": url,
        "ok": status == 200 and bool(public_title),
        "video_id": video_id,
        "official_title": title,
        "public_title": public_title,
        "title_matches_official": title_matches,
        "artist_name": artist if re.search(rf"\b{re.escape(artist)}\b", description, re.I) else "",
        "description_mentions_artist": bool(re.search(rf"\b{re.escape(artist)}\b", description, re.I)),
        "description": description,
        "thumbnail_url": parser.meta.get("og:image", ""),
        "canonical_url": parser.meta.get("og:url", url),
        "http_status": status,
    }


def choose_match(candidates: list[dict]) -> dict | None:
    for candidate in candidates:
        if candidate.get("ok") and candidate.get("title_matches_official"):
            return candidate
    return None


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Search public web results for a YouTube Music watch URL and validate the public title.")
    parser.add_argument("--artist", default="Lily Roo")
    parser.add_argument("--title", required=True)
    parser.add_argument("--out", default=str(OUT.relative_to(REPO_ROOT)), help="Output JSON path, relative to repo root or absolute.")
    args = parser.parse_args()
    out = Path(args.out)
    if not out.is_absolute():
        out = REPO_ROOT / out

    updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    urls, attempts = search_urls(args.artist, args.title)
    candidates = [candidate_snapshot(url, args.artist, args.title) for url in urls]
    match = choose_match(candidates)
    if match:
        snapshot = {
            **match,
            "ok": True,
            "updated_at": updated_at,
            "source": "public-web-search-plus-youtube-music-html",
            "query_artist": args.artist,
            "query_title": args.title,
            "candidate_urls": urls,
            "candidate_count": len(candidates),
            "search_attempts": attempts,
            "action_needed": "",
        }
    else:
        snapshot = {
            "ok": False,
            "updated_at": updated_at,
            "source": "public-web-search-plus-youtube-music-html",
            "query_artist": args.artist,
            "query_title": args.title,
            "release_url": "",
            "video_id": "",
            "official_title": args.title,
            "public_title": "",
            "title_matches_official": False,
            "candidate_urls": urls,
            "candidate_count": len(candidates),
            "candidates": candidates[:5],
            "search_attempts": attempts,
            "action_needed": f"YouTube Music release not found for {args.artist} - {args.title}. Re-run after DistroKid/YouTube Music exposes the public release.",
        }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": snapshot["ok"],
        "release_url": snapshot.get("release_url", ""),
        "public_title": snapshot.get("public_title", ""),
        "title_matches_official": snapshot.get("title_matches_official", False),
        "candidate_count": snapshot.get("candidate_count", 0),
        "output": display_path(out),
    }, indent=2))
    return 0 if snapshot["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
