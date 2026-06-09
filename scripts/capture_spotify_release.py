#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import urllib.parse
import urllib.request
import argparse
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MANUAL = REPO_ROOT / "data" / "manual_social_stats.json"
OUT = REPO_ROOT / "data" / "spotify_release_snapshot.json"
DEFAULT_RELEASE_URL = "https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi"
DEFAULT_ARTIST_URL = "https://open.spotify.com/artist/4yzWmf64UKLwbAVwnDi49a"
OEMBED_URL = "https://open.spotify.com/oembed"


def release_url(explicit_arg: str = "") -> str:
    if explicit_arg.strip():
        return explicit_arg.strip()
    explicit = os.environ.get("SPOTIFY_RELEASE_URL", "").strip()
    if explicit:
        return explicit
    if MANUAL.exists():
        manual = json.loads(MANUAL.read_text(encoding="utf-8"))
        configured = (manual.get("spotify") or {}).get("release_url", "").strip()
        if configured:
            return configured
    return DEFAULT_RELEASE_URL


def album_id(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) >= 2 and parts[0] == "album":
        return parts[1]
    return ""


def fetch_oembed(url: str) -> dict:
    endpoint = OEMBED_URL + "?" + urllib.parse.urlencode({"url": url})
    request = urllib.request.Request(endpoint, headers={
        "Accept": "application/json",
        "User-Agent": "LilyRooSpotifyReleaseCapture/1.0",
    })
    with urllib.request.urlopen(request, timeout=25) as response:
        payload = json.loads(response.read().decode("utf-8"))
        payload["http_status"] = response.status
        return payload


def fetch_artist_url(url: str) -> str:
    request = urllib.request.Request(url, headers={
        "Accept": "text/html",
        "User-Agent": "LilyRooSpotifyReleaseCapture/1.0",
    })
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            html = response.read().decode("utf-8", errors="replace")
    except OSError:
        return DEFAULT_ARTIST_URL
    match = re.search(r"https://open\\.spotify\\.com/artist/[A-Za-z0-9]+", html)
    return match.group(0) if match else DEFAULT_ARTIST_URL


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture public Spotify oEmbed release metadata.")
    parser.add_argument("--release-url", default="", help="Spotify album/single URL to capture.")
    parser.add_argument("--out", default=str(OUT.relative_to(REPO_ROOT)), help="Output JSON path, relative to repo root or absolute.")
    args = parser.parse_args()
    out = Path(args.out)
    if not out.is_absolute():
        out = REPO_ROOT / out

    url = release_url(args.release_url)
    oembed = fetch_oembed(url)
    snapshot = {
        "ok": True,
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": "spotify-oembed-public",
        "release_url": url,
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
        "analytics_status": "Streams, saves, monthly listeners, and artist followers still require Spotify for Artists export/API access.",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": snapshot["ok"],
        "title": snapshot["title"],
        "album_id": snapshot["album_id"],
        "thumbnail_url": snapshot["thumbnail_url"],
        "output": str(out.relative_to(REPO_ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
