#!/usr/bin/env python3
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from post_youtube_from_queue import refresh_access_token, upload_video
from social_exec_common import YOUTUBE_ENV, load_env
from update_youtube_video_title import fetch_video, update_video

REPO_ROOT = Path(__file__).resolve().parents[1]
VIDEO = REPO_ROOT / "assets" / "albums" / "twelve-dollars" / "video" / "04-twelve-dollars-youtube-remaster.mp4"
ART = REPO_ROOT / "assets" / "albums" / "twelve-dollars" / "art" / "04-twelve-dollars.jpg"
OUTPUT = REPO_ROOT / "data" / "youtube_twelve_dollars_remaster_manifest.json"

TITLE = "Twelve Dollars"
OLD_VIDEO_ID = "8DsCkwBPdhI"
API_ROOT = "https://www.googleapis.com"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def description_for(new_video_id: str) -> str:
    return (
        "Twelve Dollars by Lily Roo.\n\n"
        "Remastered video using the updated Twelve Dollars cover art and the local DistroKid upload WAV master.\n\n"
        "Lily Roo archive: https://www.lilyroo.com/music.html\n"
        f"YouTube Music: https://music.youtube.com/watch?v={new_video_id}\n\n"
        f"Archived original upload: https://youtu.be/{OLD_VIDEO_ID}"
    )


def archive_old_video(token: str, new_video_id: str) -> dict:
    video = fetch_video(token, OLD_VIDEO_ID)
    snippet = dict(video.get("snippet") or {})
    status = dict(video.get("status") or {})
    before_title = snippet.get("title", "")
    before_privacy = status.get("privacyStatus", "")
    snippet["title"] = "Twelve Dollars - Lily Roo (Archived Original)"[:100]
    prefix = (
        "Archived original upload. The updated-art remastered video is now canonical:\n"
        f"https://youtu.be/{new_video_id}\n\n"
    )
    old_description = snippet.get("description", "")
    if "Archived original upload." not in old_description:
        snippet["description"] = (prefix + old_description)[:5000]
    status["privacyStatus"] = "unlisted"
    updated = update_video(token, {"id": OLD_VIDEO_ID, "snippet": snippet, "status": status})
    return {
        "before_title": before_title,
        "after_title": (updated.get("snippet") or {}).get("title", ""),
        "before_privacy": before_privacy,
        "after_privacy": (updated.get("status") or {}).get("privacyStatus", ""),
    }


def set_thumbnail(token: str, video_id: str, image_path: Path) -> dict:
    url = f"{API_ROOT}/upload/youtube/v3/thumbnails/set?{urllib.parse.urlencode({'videoId': video_id})}"
    body = image_path.read_bytes()
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "image/jpeg",
            "Content-Length": str(len(body)),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return {"ok": True, "response": json.loads(response.read().decode("utf-8"))}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"error": raw}
        return {"ok": False, "status": exc.code, "error": payload}


def main() -> int:
    token = refresh_access_token(load_env(YOUTUBE_ENV))
    uploaded = upload_video(
        token,
        str(VIDEO),
        "Twelve Dollars - Lily Roo",
        "placeholder",
        "public",
    )
    new_video_id = (uploaded.get("id") or "").strip()
    if not new_video_id:
        raise RuntimeError(f"YouTube upload did not return an id: {uploaded}")

    video = fetch_video(token, new_video_id)
    snippet = dict(video.get("snippet") or {})
    status = dict(video.get("status") or {})
    snippet["description"] = description_for(new_video_id)[:5000]
    updated = update_video(token, {"id": new_video_id, "snippet": snippet, "status": status})
    archive_result = archive_old_video(token, new_video_id)
    thumbnail_result = set_thumbnail(token, new_video_id, ART)

    payload = {
        "ok": True,
        "updated_at": utc_now(),
        "title": TITLE,
        "old_video_id": OLD_VIDEO_ID,
        "old_url": f"https://youtu.be/{OLD_VIDEO_ID}",
        "new_video_id": new_video_id,
        "new_url": f"https://youtu.be/{new_video_id}",
        "youtube_music_url": f"https://music.youtube.com/watch?v={new_video_id}",
        "video_file": str(VIDEO.relative_to(REPO_ROOT)),
        "art_file": str(ART.relative_to(REPO_ROOT)),
        "audio_file": "assets/albums/twelve-dollars/audio/04-twelve-dollars.wav",
        "archive_result": archive_result,
        "thumbnail_result": thumbnail_result,
        "updated_title": (updated.get("snippet") or {}).get("title", ""),
        "privacy_status": (updated.get("status") or {}).get("privacyStatus", ""),
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
