#!/usr/bin/env python3
from __future__ import annotations

import json
import argparse
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT = REPO_ROOT / "data" / "youtube_music_release_snapshot.json"
VIDEO_ID = "vK0mDIW65o4"
OFFICIAL_TITLE = "I Learned It All in Fifteen Seconds"
CANONICAL_YOUTUBE_TITLE = f"{OFFICIAL_TITLE} - Lily Roo"
YOUTUBE_MUSIC_URL = f"https://music.youtube.com/watch?v={VIDEO_ID}"


class MetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.meta: dict[str, str] = {}
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "title":
            self._in_title = True
            return
        if tag.lower() != "meta":
            return
        data = {key.lower(): value or "" for key, value in attrs}
        key = data.get("property") or data.get("name")
        value = data.get("content")
        if key and value:
            self.meta[key] = unescape(value)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data


def fetch_page(url: str) -> tuple[str, int]:
    request = urllib.request.Request(url, headers={
        "Accept": "text/html",
        "User-Agent": "LilyRooYouTubeMusicReleaseCapture/1.0",
    })
    with urllib.request.urlopen(request, timeout=25) as response:
        return response.read().decode("utf-8", errors="replace"), response.status


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture public YouTube Music metadata for a release video.")
    parser.add_argument("--url", default=YOUTUBE_MUSIC_URL, help="YouTube Music watch URL.")
    parser.add_argument("--video-id", default="", help="YouTube video id; overrides --url when supplied.")
    parser.add_argument("--title", default=OFFICIAL_TITLE, help="Official title to compare against.")
    parser.add_argument("--artist", default="Lily Roo")
    parser.add_argument("--out", default=str(OUT.relative_to(REPO_ROOT)), help="Output JSON path, relative to repo root or absolute.")
    args = parser.parse_args()
    url = args.url
    video_id = args.video_id.strip()
    if video_id:
        url = f"https://music.youtube.com/watch?v={urllib.parse.quote(video_id)}"
    elif "watch" in url:
        video_id = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get("v", [""])[0]
    official_title = args.title
    canonical_title = f"{official_title} - {args.artist}"
    out = Path(args.out)
    if not out.is_absolute():
        out = REPO_ROOT / out

    html, status = fetch_page(url)
    parser = MetaParser()
    parser.feed(html)
    public_title = (parser.meta.get("og:title") or parser.title).strip()
    description = parser.meta.get("og:description") or parser.meta.get("description") or ""
    title_mentions_artist = bool(re.search(rf"\b{re.escape(args.artist)}\b", description, re.I))
    snapshot = {
        "ok": status == 200 and bool(public_title),
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": "youtube-music-public-html",
        "release_url": url,
        "video_id": video_id,
        "official_title": official_title,
        "public_title": public_title,
        "title_matches_official": public_title in {official_title, canonical_title},
        "artist_name": args.artist if title_mentions_artist else "",
        "description_mentions_artist": title_mentions_artist,
        "description": description,
        "thumbnail_url": parser.meta.get("og:image", ""),
        "canonical_url": parser.meta.get("og:url", url),
        "http_status": status,
        "action_needed": "" if public_title in {official_title, canonical_title} else "Update public YouTube title to the official title or canonical artist-title form; YouTube Music mirrors the same public title.",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": snapshot["ok"],
        "release_url": snapshot["release_url"],
        "public_title": snapshot["public_title"],
        "title_matches_official": snapshot["title_matches_official"],
        "output": str(out.relative_to(REPO_ROOT)),
    }, indent=2))
    return 0 if snapshot["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
