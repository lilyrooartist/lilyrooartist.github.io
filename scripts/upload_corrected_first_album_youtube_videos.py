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
ALBUM_DIR = REPO_ROOT / "assets" / "albums" / "i-learned-it-all-in-fifteen-seconds"
MANIFEST = REPO_ROOT / "data" / "youtube_first_album_remaster_manifest.json"

STREAM_LINKS = [
    "Spotify: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi",
    "Apple Music: https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249",
]

TRACKS = [
    {
        "track": 1,
        "title": "I Learned It All in Fifteen Seconds",
        "original_video_id": "Hve5drBlN58",
        "superseded_video_id": "v9HzFvfvXxQ",
        "centered_video_id": "g1XuXj8W3Vs",
        "video": "video/01-i-learned-it-all-in-fifteen-seconds-youtube-remaster.mp4",
    },
    {
        "track": 2,
        "title": "Second Serve",
        "original_video_id": "_nxa0D-gqns",
        "superseded_video_id": "DftaEEuMb4o",
        "centered_video_id": "KTzM2WrKme4",
        "video": "video/02-second-serve-youtube-remaster.mp4",
    },
    {
        "track": 3,
        "title": "My Second Room Has No Light Switch",
        "original_video_id": "k3VdR2FE0EI",
        "superseded_video_id": "1n2cqma4S-g",
        "centered_video_id": "PUYKobQ0-ac",
        "video": "video/03-my-second-room-has-no-light-switch-youtube-remaster.mp4",
    },
    {
        "track": 4,
        "title": "The Importance of Bearing Witness",
        "original_video_id": "cVuK20aaJb8",
        "superseded_video_id": "KkFO5ePgP2o",
        "centered_video_id": "nZkTunrTbv4",
        "video": "video/04-the-importance-of-bearing-witness-youtube-remaster.mp4",
    },
    {
        "track": 5,
        "title": "Sliding Out of Bed",
        "original_video_id": "_A1vEHSYuyY",
        "superseded_video_id": "kYTq2G9dBqo",
        "centered_video_id": "PWZL_UXaW_k",
        "video": "video/05-sliding-out-of-bed-youtube-remaster.mp4",
    },
    {
        "track": 6,
        "title": "Dinner Table Tilt",
        "original_video_id": "n6-vpeop_wc",
        "superseded_video_id": "vLzv0sNYuk8",
        "centered_video_id": "kOECPc1ghTc",
        "video": "video/06-dinner-table-tilt-youtube-remaster.mp4",
    },
    {
        "track": 7,
        "title": "Yeah, I Play the Violin",
        "original_video_id": "6TG-96QM_n0",
        "superseded_video_id": "4wE92atmgtE",
        "centered_video_id": "aKKZu5vFe90",
        "video": "video/07-yeah-i-play-the-violin-youtube-remaster.mp4",
    },
    {
        "track": 8,
        "title": "More Difference (Reprise)",
        "original_video_id": "uOo30diDXOs",
        "superseded_video_id": "SQJIlUwJhh4",
        "centered_video_id": "iPEilc2WO60",
        "video": "video/08-more-difference-reprise-youtube-remaster.mp4",
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
    links = "\n".join(STREAM_LINKS + [f"YouTube Music: https://music.youtube.com/watch?v={track['corrected_video_id']}"])
    return (
        f"{track['title']} by Lily Roo.\n\n"
        "Corrected remastered video for the album I Learned It All in Fifteen Seconds. "
        "This upload keeps the original motion-video treatment and uses the DistroKid Mixea Ultra HD WAV master.\n\n"
        f"{links}\n\n"
        f"Original upload archived at: https://youtu.be/{track['original_video_id']}\n"
        f"Superseded old-art remaster archived at: https://youtu.be/{track['superseded_video_id']}\n"
        f"Superseded centered-art remaster archived at: https://youtu.be/{track['centered_video_id']}"
    )


def archive_video(token: str, video_id: str, title: str, corrected_video_id: str) -> dict:
    video = fetch_video(token, video_id)
    snippet = dict(video.get("snippet") or {})
    status = dict(video.get("status") or {})
    if not snippet or not status:
        raise RuntimeError(f"Could not fetch editable metadata for video {video_id}")
    before_title = snippet.get("title", "")
    before_privacy = status.get("privacyStatus", "")
    snippet["title"] = f"{title} - Lily Roo (Archived Superseded Remaster)"[:100]
    prefix = (
        "Archived superseded remaster. The corrected updated-art pan remaster is now canonical:\n"
        f"https://youtu.be/{corrected_video_id}\n\n"
    )
    old_description = snippet.get("description", "")
    if "Archived superseded remaster." not in old_description:
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
    parser = argparse.ArgumentParser(description="Upload corrected original-motion first-album remasters.")
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
        corrected_video_id = (entry.get("corrected_video_id") or "").strip()
        entry.update({
            "track": track["track"],
            "title": track["title"],
            "old_video_id": track["original_video_id"],
            "old_url": f"https://youtu.be/{track['original_video_id']}",
            "superseded_original_motion_video_id": track["superseded_video_id"],
            "superseded_original_motion_url": f"https://youtu.be/{track['superseded_video_id']}",
            "superseded_centered_video_id": track["centered_video_id"],
            "superseded_centered_url": f"https://youtu.be/{track['centered_video_id']}",
            "video_file": str(video_path.relative_to(REPO_ROOT)),
            "video_exists": video_path.exists(),
            "video_size": video_path.stat().st_size if video_path.exists() else 0,
        })
        if not video_path.exists():
            entry["error"] = "corrected video file is missing"
            by_track[track["track"]] = entry
            continue
        if args.apply and not (args.skip_uploaded and corrected_video_id):
            uploaded = upload_video(
                token,
                str(video_path),
                f"{track['title']} - Lily Roo",
                "placeholder",
                args.privacy_status,
            )
            corrected_video_id = (uploaded.get("id") or "").strip()
            if not corrected_video_id:
                raise RuntimeError(f"YouTube upload did not return an id for track {track['track']}: {uploaded}")
        if corrected_video_id:
            track_with_id = {**track, "corrected_video_id": corrected_video_id}
            if args.apply:
                video = fetch_video(token, corrected_video_id)
                snippet = dict(video.get("snippet") or {})
                status = dict(video.get("status") or {})
                snippet["description"] = description_for(track_with_id)[:5000]
                update_video(token, {"id": corrected_video_id, "snippet": snippet, "status": status})
                entry["superseded_original_motion_archive_result"] = archive_video(
                    token,
                    track["superseded_video_id"],
                    track["title"],
                    corrected_video_id,
                )
            entry["new_video_id"] = corrected_video_id
            entry["new_url"] = f"https://youtu.be/{corrected_video_id}"
            entry["corrected_video_id"] = corrected_video_id
            entry["corrected_url"] = f"https://youtu.be/{corrected_video_id}"
            entry["superseded_original_motion_archived"] = bool(args.apply)
        entry["dry_run"] = not args.apply
        by_track[track["track"]] = entry

    payload = {
        "ok": all(item.get("video_exists") and not item.get("error") for item in by_track.values()),
        "applied": args.apply,
        "privacy_status": args.privacy_status,
        "audio_source": "DistroKid Mixea Ultra HD WAV, 24-bit/48k, downloaded Jun 7 2026.",
        "video_source": "Updated album art rendered with the pan motion treatment and DistroKid Mixea masters.",
        "tracks": [by_track[k] for k in sorted(by_track)],
    }
    save_manifest(payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
