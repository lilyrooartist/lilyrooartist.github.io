#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from post_youtube_from_queue import refresh_access_token, upload_video
from social_exec_common import YOUTUBE_ENV, load_env
from update_youtube_video_title import fetch_video, update_video

REPO_ROOT = Path(__file__).resolve().parents[1]
ALBUM_DIR = REPO_ROOT / "assets" / "albums" / "i-learned-it-all-in-fifteen-seconds"
MANIFEST = REPO_ROOT / "data" / "youtube_first_album_remaster_manifest.json"
STREAM_LINKS = [
    "Spotify: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi",
    "Apple Music: https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249",
    "YouTube Music: https://music.youtube.com/watch?v=g1XuXj8W3Vs",
]

TRACKS = [
    {
        "track": 1,
        "title": "I Learned It All in Fifteen Seconds",
        "old_video_id": "Hve5drBlN58",
        "video": "video/01-i-learned-it-all-in-fifteen-seconds-youtube-remaster.mp4",
    },
    {
        "track": 2,
        "title": "Second Serve",
        "old_video_id": "_nxa0D-gqns",
        "video": "video/02-second-serve-youtube-remaster.mp4",
    },
    {
        "track": 3,
        "title": "My Second Room Has No Light Switch",
        "old_video_id": "k3VdR2FE0EI",
        "video": "video/03-my-second-room-has-no-light-switch-youtube-remaster.mp4",
    },
    {
        "track": 4,
        "title": "The Importance of Bearing Witness",
        "old_video_id": "cVuK20aaJb8",
        "video": "video/04-the-importance-of-bearing-witness-youtube-remaster.mp4",
    },
    {
        "track": 5,
        "title": "Sliding Out of Bed",
        "old_video_id": "_A1vEHSYuyY",
        "video": "video/05-sliding-out-of-bed-youtube-remaster.mp4",
    },
    {
        "track": 6,
        "title": "Dinner Table Tilt",
        "old_video_id": "n6-vpeop_wc",
        "video": "video/06-dinner-table-tilt-youtube-remaster.mp4",
    },
    {
        "track": 7,
        "title": "Yeah, I Play the Violin",
        "old_video_id": "6TG-96QM_n0",
        "video": "video/07-yeah-i-play-the-violin-youtube-remaster.mp4",
    },
    {
        "track": 8,
        "title": "More Difference (Reprise)",
        "old_video_id": "uOo30diDXOs",
        "video": "video/08-more-difference-reprise-youtube-remaster.mp4",
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_manifest() -> dict:
    if not MANIFEST.exists():
        return {"updated_at": "", "tracks": []}
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def save_manifest(payload: dict) -> None:
    payload["updated_at"] = utc_now()
    MANIFEST.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def description_for(track: dict) -> str:
    links = "\n".join(STREAM_LINKS)
    return (
        f"{track['title']} by Lily Roo.\n\n"
        "Remastered replacement video for the first album I Learned It All in Fifteen Seconds, "
        "with updated album art and the current release audio master.\n\n"
        f"{links}\n\n"
        f"Original upload archived at: https://youtu.be/{track['old_video_id']}"
    )


def archive_old_video(token: str, track: dict, new_video_id: str) -> dict:
    video = fetch_video(token, track["old_video_id"])
    snippet = dict(video.get("snippet") or {})
    status = dict(video.get("status") or {})
    if not snippet or not status:
        raise RuntimeError(f"Could not fetch editable metadata for old video {track['old_video_id']}")
    before_title = snippet.get("title", "")
    before_privacy = status.get("privacyStatus", "")
    archive_title = f"{track['title']} - Lily Roo (Archived Original)"
    snippet["title"] = archive_title[:100]
    prefix = (
        "Archived original upload. A remastered replacement is now the canonical video:\n"
        f"https://youtu.be/{new_video_id}\n\n"
    )
    old_description = snippet.get("description", "")
    if "Archived original upload." not in old_description:
        snippet["description"] = (prefix + old_description)[:5000]
    status["privacyStatus"] = "unlisted"
    resource = {
        "id": track["old_video_id"],
        "snippet": snippet,
        "status": status,
    }
    updated = update_video(token, resource)
    return {
        "before_title": before_title,
        "after_title": (updated.get("snippet") or {}).get("title", ""),
        "before_privacy": before_privacy,
        "after_privacy": (updated.get("status") or {}).get("privacyStatus", ""),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload first-album YouTube replacement videos and archive old uploads.")
    parser.add_argument("--apply", action="store_true", help="Actually upload and archive. Default is dry-run.")
    parser.add_argument("--privacy-status", default="public", choices=["public", "unlisted", "private"])
    parser.add_argument("--start-track", type=int, default=1)
    parser.add_argument("--stop-track", type=int, default=8)
    parser.add_argument("--skip-uploaded", action="store_true", help="Do not re-upload tracks already carrying a new_video_id in the manifest.")
    args = parser.parse_args()

    manifest = load_manifest()
    by_track = {int(item["track"]): item for item in manifest.get("tracks", []) if item.get("track")}
    selected = [t for t in TRACKS if args.start_track <= t["track"] <= args.stop_track]
    result_tracks = []

    token = ""
    if args.apply:
        token = refresh_access_token(load_env(YOUTUBE_ENV))

    for track in selected:
        video_path = ALBUM_DIR / track["video"]
        existing = by_track.get(track["track"], {})
        entry = {
            "track": track["track"],
            "title": track["title"],
            "old_video_id": track["old_video_id"],
            "old_url": f"https://youtu.be/{track['old_video_id']}",
            "video_file": str(video_path.relative_to(REPO_ROOT)),
            "video_exists": video_path.exists(),
            "video_size": video_path.stat().st_size if video_path.exists() else 0,
            "new_video_id": existing.get("new_video_id", ""),
            "new_url": existing.get("new_url", ""),
            "old_archived": existing.get("old_archived", False),
            "archive_result": existing.get("archive_result", {}),
        }
        if not video_path.exists():
            entry["error"] = "replacement video file is missing"
            result_tracks.append(entry)
            continue
        if not args.apply:
            entry["dry_run"] = True
            result_tracks.append(entry)
            continue
        if args.skip_uploaded and entry["new_video_id"]:
            result_tracks.append(entry)
            continue
        uploaded = upload_video(
            token,
            str(video_path),
            f"{track['title']} - Lily Roo",
            description_for(track),
            args.privacy_status,
        )
        new_video_id = (uploaded.get("id") or "").strip()
        if not new_video_id:
            raise RuntimeError(f"YouTube upload did not return a video id for track {track['track']}: {uploaded}")
        entry["new_video_id"] = new_video_id
        entry["new_url"] = f"https://youtu.be/{new_video_id}"
        entry["archive_result"] = archive_old_video(token, track, new_video_id)
        entry["old_archived"] = True
        result_tracks.append(entry)

    merged = {**by_track}
    for entry in result_tracks:
        merged[int(entry["track"])] = entry
    payload = {
        "ok": all(item.get("video_exists") and not item.get("error") for item in merged.values()),
        "applied": args.apply,
        "privacy_status": args.privacy_status,
        "tracks": [merged[k] for k in sorted(merged)],
    }
    save_manifest(payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
