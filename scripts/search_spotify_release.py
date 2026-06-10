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

from capture_spotify_release import album_id, fetch_artist_url, fetch_oembed


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT = REPO_ROOT / "data" / "store-verification" / "spotify_release_search_snapshot.json"
SEARCH_ENDPOINTS = [
    "https://lite.duckduckgo.com/lite/",
    "https://html.duckduckgo.com/html/",
]


def norm(value: str | None) -> str:
    return " ".join(str(value or "").strip().lower().split())


def request_text(url: str) -> tuple[int, str, str]:
    request = urllib.request.Request(url, headers={
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent": "LilyRooSpotifyStoreVerifier/1.0",
    })
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            return response.status, response.read().decode("utf-8", errors="replace"), ""
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace"), f"HTTP {exc.code}: {exc.reason}"
    except urllib.error.URLError as exc:
        return 0, "", str(exc.reason)


def spotify_album_urls(text: str) -> list[str]:
    decoded = html.unescape(text)
    urls = set(re.findall(r"https?://open\.spotify\.com/album/[A-Za-z0-9]+", decoded))
    for encoded in re.findall(r"uddg=([^&\"'>]+)", decoded):
        url = urllib.parse.unquote(encoded)
        if re.match(r"https?://open\.spotify\.com/album/[A-Za-z0-9]+", url):
            urls.add(url.split("?")[0])
    return sorted(url.split("?")[0] for url in urls)


def search_urls(artist: str, title: str) -> tuple[list[str], list[dict]]:
    queries = [
        f'site:open.spotify.com/album "{title}" "{artist}"',
        f'"{title}" "{artist}" "open.spotify.com/album"',
    ]
    found: set[str] = set()
    attempts = []
    for query in queries:
        for endpoint in SEARCH_ENDPOINTS:
            url = endpoint + "?" + urllib.parse.urlencode({"q": query})
            status, body, error = request_text(url)
            urls = spotify_album_urls(body)
            found.update(urls)
            attempts.append({
                "query": query,
                "endpoint": endpoint,
                "http_status": status,
                "error": error,
                "candidate_count": len(urls),
            })
    return sorted(found), attempts


def candidate_snapshot(url: str) -> dict:
    try:
        oembed = fetch_oembed(url)
    except Exception as exc:  # noqa: BLE001 - snapshot should preserve public lookup failures.
        return {
            "release_url": url,
            "ok": False,
            "error": str(exc),
        }
    return {
        "release_url": url,
        "ok": True,
        "album_id": album_id(url),
        "artist_url": fetch_artist_url(url),
        "title": oembed.get("title", ""),
        "provider_name": oembed.get("provider_name", ""),
        "provider_url": oembed.get("provider_url", ""),
        "iframe_url": oembed.get("iframe_url", ""),
        "thumbnail_url": oembed.get("thumbnail_url", ""),
        "thumbnail_width": oembed.get("thumbnail_width"),
        "thumbnail_height": oembed.get("thumbnail_height"),
        "embed_width": oembed.get("width"),
        "embed_height": oembed.get("height"),
        "http_status": oembed.get("http_status"),
    }


def choose_match(candidates: list[dict], title: str) -> dict | None:
    wanted = norm(title)
    for candidate in candidates:
        if candidate.get("ok") and norm(candidate.get("title")) == wanted:
            return candidate
    return None


def write_snapshot(out: Path, snapshot: dict) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Search public web results for a Spotify album and validate candidates with Spotify oEmbed.")
    parser.add_argument("--artist", default="Lily Roo")
    parser.add_argument("--title", required=True)
    parser.add_argument("--out", default=str(OUT.relative_to(REPO_ROOT)), help="Output JSON path, relative to repo root or absolute.")
    args = parser.parse_args()
    out = Path(args.out)
    if not out.is_absolute():
        out = REPO_ROOT / out

    updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    urls, attempts = search_urls(args.artist, args.title)
    candidates = [candidate_snapshot(url) for url in urls]
    match = choose_match(candidates, args.title)
    if match:
        snapshot = {
            **match,
            "ok": True,
            "updated_at": updated_at,
            "source": "public-web-search-plus-spotify-oembed",
            "query_artist": args.artist,
            "query_title": args.title,
            "search_attempts": attempts,
            "candidate_urls": urls,
            "candidate_count": len(candidates),
            "analytics_status": "Streams, saves, monthly listeners, and artist followers still require Spotify for Artists export/API access.",
        }
    else:
        snapshot = {
            "ok": False,
            "updated_at": updated_at,
            "source": "public-web-search-plus-spotify-oembed",
            "query_artist": args.artist,
            "query_title": args.title,
            "release_url": "",
            "album_id": "",
            "artist_url": "",
            "title": "",
            "candidate_urls": urls,
            "candidate_count": len(candidates),
            "candidates": candidates[:5],
            "search_attempts": attempts,
            "action_needed": f"Spotify album not found for {args.artist} - {args.title}. Re-run after DistroKid exposes the public release.",
        }
    write_snapshot(out, snapshot)
    print(json.dumps({
        "ok": snapshot["ok"],
        "title": snapshot.get("title", ""),
        "album_id": snapshot.get("album_id", ""),
        "release_url": snapshot.get("release_url", ""),
        "candidate_count": snapshot.get("candidate_count", 0),
        "output": str(out.relative_to(REPO_ROOT)),
    }, indent=2))
    return 0 if snapshot["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
