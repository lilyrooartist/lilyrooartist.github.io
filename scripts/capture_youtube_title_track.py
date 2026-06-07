#!/usr/bin/env python3
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT = REPO_ROOT / "data" / "youtube_title_track_snapshot.json"
VIDEO_ID = "vK0mDIW65o4"
OFFICIAL_TITLE = "I Learned It All in Fifteen Seconds"
CANONICAL_YOUTUBE_TITLE = f"{OFFICIAL_TITLE} - Lily Roo"
OEMBED_URL = "https://www.youtube.com/oembed"


def fetch_oembed(video_id: str) -> dict:
    endpoint = OEMBED_URL + "?" + urllib.parse.urlencode({
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "format": "json",
    })
    request = urllib.request.Request(endpoint, headers={
        "Accept": "application/json",
        "User-Agent": "LilyRooYouTubeTitleTrackCapture/1.0",
    })
    with urllib.request.urlopen(request, timeout=25) as response:
        payload = json.loads(response.read().decode("utf-8"))
        payload["http_status"] = response.status
        return payload


def main() -> int:
    oembed = fetch_oembed(VIDEO_ID)
    public_title = oembed.get("title", "")
    snapshot = {
        "ok": True,
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": "youtube-oembed-public",
        "video_id": VIDEO_ID,
        "url": f"https://www.youtube.com/watch?v={VIDEO_ID}",
        "official_title": OFFICIAL_TITLE,
        "public_title": public_title,
        "title_matches_official": public_title in {OFFICIAL_TITLE, CANONICAL_YOUTUBE_TITLE},
        "author_name": oembed.get("author_name", ""),
        "author_url": oembed.get("author_url", ""),
        "thumbnail_url": oembed.get("thumbnail_url", ""),
        "http_status": oembed.get("http_status"),
        "action_needed": "" if public_title in {OFFICIAL_TITLE, CANONICAL_YOUTUBE_TITLE} else "Update public YouTube title to the official title or canonical artist-title form.",
    }
    OUT.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": snapshot["ok"],
        "video_id": snapshot["video_id"],
        "public_title": snapshot["public_title"],
        "title_matches_official": snapshot["title_matches_official"],
        "output": str(OUT.relative_to(REPO_ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
