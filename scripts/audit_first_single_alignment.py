#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "first_single_alignment_audit.json"

OFFICIAL_TITLE = "I Learned It All in Fifteen Seconds"
SPOTIFY_URL = "https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi"
APPLE_URL = "https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249"
YOUTUBE_URL = "https://www.youtube.com/watch?v=g1XuXj8W3Vs"
YOUTUBE_MUSIC_URL = "https://music.youtube.com/watch?v=g1XuXj8W3Vs"


def read_json(path: str) -> dict:
    full = ROOT / path
    if not full.exists():
        return {}
    return json.loads(full.read_text(encoding="utf-8"))


def read_text(path: str) -> str:
    full = ROOT / path
    if not full.exists():
        return ""
    return full.read_text(encoding="utf-8")


def check_title(public_title: str) -> dict:
    if not public_title:
        return {"status": "missing", "public_title": "", "matches": False}
    canonical_titles = {OFFICIAL_TITLE, f"{OFFICIAL_TITLE} - Lily Roo"}
    matches = public_title in canonical_titles
    return {
        "status": "ok" if matches else "action_required",
        "public_title": public_title,
        "matches": matches,
    }


def main() -> int:
    spotify = read_json("data/spotify_release_snapshot.json")
    apple = read_json("data/apple_music_release_snapshot.json")
    youtube = read_json("data/youtube_title_track_snapshot.json")
    youtube_music = read_json("data/youtube_music_release_snapshot.json")
    hyperfollow = read_json("data/hyperfollow_store_links_snapshot.json")
    home = read_text("index.html")
    archive = read_text("music.html")
    queue = read_text("data/scheduled_posts.csv")

    checks = {
        "official_title": {
            "status": "ok",
            "value": OFFICIAL_TITLE,
        },
        "website_home": {
            "status": "ok" if all(item in home for item in (OFFICIAL_TITLE, SPOTIFY_URL, APPLE_URL, YOUTUBE_MUSIC_URL)) else "action_required",
            "has_spotify": SPOTIFY_URL in home,
            "has_apple_music": APPLE_URL in home,
            "has_youtube_music": YOUTUBE_MUSIC_URL in home,
        },
        "website_archive": {
            "status": "ok" if all(item in archive for item in (OFFICIAL_TITLE, SPOTIFY_URL, APPLE_URL, YOUTUBE_MUSIC_URL)) else "action_required",
            "has_spotify": SPOTIFY_URL in archive,
            "has_apple_music": APPLE_URL in archive,
            "has_youtube_music": YOUTUBE_MUSIC_URL in archive,
        },
        "social_queue": {
            "status": "ok" if YOUTUBE_MUSIC_URL in queue and "Spotify and Apple Music" not in queue else "action_required",
            "has_youtube_music": YOUTUBE_MUSIC_URL in queue,
            "has_stale_spotify_apple_phrase": "Spotify and Apple Music" in queue,
        },
        "spotify": {
            **check_title(spotify.get("title", "")),
            "url": spotify.get("release_url") or SPOTIFY_URL,
        },
        "apple_music": {
            "status": "ok" if OFFICIAL_TITLE in (apple.get("collection_name") or "") else "action_required",
            "collection_name": apple.get("collection_name", ""),
            "url": apple.get("release_url") or APPLE_URL,
        },
        "youtube": {
            **check_title(youtube.get("public_title", "")),
            "url": youtube.get("url") or YOUTUBE_URL,
            "action": "" if youtube.get("title_matches_official") is True else "Update YouTube title to the official title or canonical artist-title form.",
        },
        "youtube_music": {
            **check_title(youtube_music.get("public_title", "")),
            "url": youtube_music.get("release_url") or YOUTUBE_MUSIC_URL,
            "action": "" if youtube_music.get("title_matches_official") is True else "Mirrors YouTube title; update YouTube title to the official title or canonical artist-title form.",
        },
        "amazon_music": {
            "status": "pending",
            "url": "",
            "evidence": "HyperFollow store list does not expose Amazon Music.",
            "hyperfollow_stores": hyperfollow.get("stores") or [],
        },
    }
    action_required = [name for name, check in checks.items() if check.get("status") == "action_required"]
    pending = [name for name, check in checks.items() if check.get("status") == "pending"]
    audit = {
        "ok": not action_required,
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "official_title": OFFICIAL_TITLE,
        "action_required": action_required,
        "pending": pending,
        "checks": checks,
    }
    OUT.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": audit["ok"],
        "action_required": action_required,
        "pending": pending,
        "output": str(OUT.relative_to(ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
