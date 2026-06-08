#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from post_youtube_from_queue import refresh_access_token, upload_video
from social_exec_common import YOUTUBE_ENV, load_env
from update_youtube_video_title import fetch_video, update_video

REPO_ROOT = Path(__file__).resolve().parents[1]
ALBUM_DIR = REPO_ROOT / "assets" / "albums" / "analog-myth"
MANIFEST = REPO_ROOT / "data" / "youtube_analog_myth_remaster_manifest.json"

ALBUM_LINKS = [
    "HyperFollow / pre-save: https://distrokid.com/hyperfollow/lilyroo/analog-myth",
    "Archive: https://www.lilyroo.com/music.html",
]

TRACKS = [
    {
        "track": 1,
        "title": "13",
        "old_video_id": "IahKaEXEA_0",
        "video": "video/01-13-youtube-remaster.mp4",
    },
    {
        "track": 2,
        "title": "Girls Camp",
        "old_video_id": "-930Tys3nbU",
        "video": "video/02-girls-camp-youtube-remaster.mp4",
    },
    {
        "track": 3,
        "title": "Analog Myth",
        "old_video_id": "wGFgXcTD1YE",
        "video": "video/03-analog-myth-youtube-remaster.mp4",
    },
    {
        "track": 4,
        "title": "Spilling the Tea",
        "old_video_id": "9yqSVkZRass",
        "video": "video/04-spilling-the-tea-youtube-remaster.mp4",
    },
    {
        "track": 5,
        "title": "No Mortgage",
        "old_video_id": "9rmy2JhBuF4",
        "video": "video/05-no-mortgage-youtube-remaster.mp4",
    },
    {
        "track": 6,
        "title": "Guards Down",
        "old_video_id": "M8RF-v1P4QY",
        "video": "video/06-guards-down-youtube-remaster.mp4",
    },
    {
        "track": 7,
        "title": "Slow Walk",
        "old_video_id": "R7evPASi8vM",
        "video": "video/07-slow-walk-youtube-remaster.mp4",
    },
    {
        "track": 8,
        "title": "The Power of Light",
        "old_video_id": "BkkBE2pXHSY",
        "video": "video/08-the-power-of-light-youtube-remaster.mp4",
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_manifest() -> dict:
    if not MANIFEST.exists():
        return {"tracks": []}
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def save_manifest(payload: dict) -> None:
    payload["updated_at"] = utc_now()
    MANIFEST.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def description_for(track: dict) -> str:
    links = "\n".join(ALBUM_LINKS + [f"YouTube Music: https://music.youtube.com/watch?v={track['new_video_id']}"])
    return (
        f"{track['title']} by Lily Roo.\n\n"
        "Remastered video for the album Analog Myth. "
        "This version uses the DistroKid Mixea 24-bit / 48 kHz WAV master and refreshed album imagery.\n\n"
        "Analog Myth releases July 1, 2026.\n\n"
        f"{links}\n\n"
        f"Archived original upload: https://youtu.be/{track['old_video_id']}"
    )


def archive_video(token: str, video_id: str, title: str, new_video_id: str) -> dict:
    video = fetch_video(token, video_id)
    snippet = dict(video.get("snippet") or {})
    status = dict(video.get("status") or {})
    if not snippet or not status:
        raise RuntimeError(f"Could not fetch editable metadata for video {video_id}")
    before_title = snippet.get("title", "")
    before_privacy = status.get("privacyStatus", "")
    snippet["title"] = f"{title} - Lily Roo (Archived Original)"[:100]
    prefix = (
        "Archived original upload. The remastered Analog Myth video is now canonical:\n"
        f"https://youtu.be/{new_video_id}\n\n"
    )
    old_description = snippet.get("description", "")
    if "Archived original upload." not in old_description:
        snippet["description"] = (prefix + old_description)[:5000]
    status["privacyStatus"] = "unlisted"
    updated = update_video(token, {"id": video_id, "snippet": snippet, "status": status})
    return {
        "before_title": before_title,
        "after_title": (updated.get("snippet") or {}).get("title", ""),
        "before_privacy": before_privacy,
        "after_privacy": (updated.get("status") or {}).get("privacyStatus", ""),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload Analog Myth YouTube remasters and archive originals.")
    parser.add_argument("--apply", action="store_true", help="Actually upload and archive. Default is dry-run.")
    parser.add_argument("--privacy-status", default="public", choices=["public", "unlisted", "private"])
    parser.add_argument("--start-track", type=int, default=1)
    parser.add_argument("--stop-track", type=int, default=8)
    parser.add_argument("--skip-uploaded", action="store_true")
    args = parser.parse_args()

    manifest = load_manifest()
    by_track = {int(item["track"]): item for item in manifest.get("tracks", []) if item.get("track")}
    selected = [t for t in TRACKS if args.start_track <= t["track"] <= args.stop_track]
    token = refresh_access_token(load_env(YOUTUBE_ENV)) if args.apply else ""

    for track in selected:
        video_path = ALBUM_DIR / track["video"]
        entry = dict(by_track.get(track["track"], {}))
        new_video_id = (entry.get("new_video_id") or "").strip()
        entry.update({
            "track": track["track"],
            "title": track["title"],
            "old_video_id": track["old_video_id"],
            "old_url": f"https://youtu.be/{track['old_video_id']}",
            "video_file": str(video_path.relative_to(REPO_ROOT)),
            "video_exists": video_path.exists(),
            "video_size": video_path.stat().st_size if video_path.exists() else 0,
        })
        if not video_path.exists():
            entry["error"] = "video file is missing"
            by_track[track["track"]] = entry
            continue
        if args.apply and not (args.skip_uploaded and new_video_id):
            uploaded = upload_video(
                token,
                str(video_path),
                f"{track['title']} - Lily Roo",
                "placeholder",
                args.privacy_status,
            )
            new_video_id = (uploaded.get("id") or "").strip()
            if not new_video_id:
                raise RuntimeError(f"YouTube upload did not return an id for track {track['track']}: {uploaded}")
        if new_video_id:
            track_with_id = {**track, "new_video_id": new_video_id}
            if args.apply:
                video = fetch_video(token, new_video_id)
                snippet = dict(video.get("snippet") or {})
                status = dict(video.get("status") or {})
                snippet["description"] = description_for(track_with_id)[:5000]
                update_video(token, {"id": new_video_id, "snippet": snippet, "status": status})
                entry["archive_result"] = archive_video(token, track["old_video_id"], track["title"], new_video_id)
            entry["new_video_id"] = new_video_id
            entry["new_url"] = f"https://youtu.be/{new_video_id}"
            entry["old_archived"] = bool(args.apply)
        entry["dry_run"] = not args.apply
        by_track[track["track"]] = entry

    payload = {
        "ok": all(item.get("video_exists") and not item.get("error") for item in by_track.values()),
        "applied": args.apply,
        "privacy_status": args.privacy_status,
        "audio_source": "DistroKid Mixea 24-bit/48k WAV masters, downloaded Jun 8 2026.",
        "video_source": "Refreshed Analog Myth imagery rendered with the pan motion treatment.",
        "tracks": [by_track[k] for k in sorted(by_track)],
    }
    save_manifest(payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
