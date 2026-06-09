#!/usr/bin/env python3
from __future__ import annotations

import json
import argparse
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT = REPO_ROOT / "data" / "apple_music_release_snapshot.json"
SEARCH_URL = "https://itunes.apple.com/search"
ARTIST = "Lily Roo"
TITLE = "I Learned It All in Fifteen Seconds"


def fetch_release(artist: str, title: str) -> dict:
    params = {
        "term": f"{artist} {title}",
        "entity": "album",
        "limit": "10",
        "country": "US",
    }
    request = urllib.request.Request(
        SEARCH_URL + "?" + urllib.parse.urlencode(params),
        headers={
            "Accept": "application/json",
            "User-Agent": "LilyRooAppleMusicReleaseCapture/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=25) as response:
        payload = json.loads(response.read().decode("utf-8"))
    for item in payload.get("results", []):
        if item.get("artistName") == artist and title.lower() in item.get("collectionName", "").lower():
            return item
    raise RuntimeError(f"Apple Music release not found for {artist} - {title}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture public Apple Music/iTunes release metadata.")
    parser.add_argument("--artist", default=ARTIST)
    parser.add_argument("--title", default=TITLE)
    parser.add_argument("--out", default=str(OUT.relative_to(REPO_ROOT)), help="Output JSON path, relative to repo root or absolute.")
    args = parser.parse_args()
    out = Path(args.out)
    if not out.is_absolute():
        out = REPO_ROOT / out

    item = fetch_release(args.artist, args.title)
    snapshot = {
        "ok": True,
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": "itunes-search-api",
        "artist_name": item.get("artistName", ""),
        "artist_id": item.get("artistId"),
        "artist_url": item.get("artistViewUrl", "").replace("?uo=4", ""),
        "collection_name": item.get("collectionName", ""),
        "collection_id": item.get("collectionId"),
        "release_url": item.get("collectionViewUrl", "").replace("?uo=4", ""),
        "artwork_url": item.get("artworkUrl100", "").replace("100x100bb.jpg", "1200x1200bb.jpg"),
        "explicitness": item.get("collectionExplicitness", ""),
        "track_count": item.get("trackCount"),
        "copyright": item.get("copyright", ""),
        "country": item.get("country", ""),
        "release_date": item.get("releaseDate", ""),
        "primary_genre": item.get("primaryGenreName", ""),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": snapshot["ok"],
        "collection_name": snapshot["collection_name"],
        "collection_id": snapshot["collection_id"],
        "release_url": snapshot["release_url"],
        "output": str(out.relative_to(REPO_ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
