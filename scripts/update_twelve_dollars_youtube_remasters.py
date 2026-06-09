#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageOps

from post_youtube_from_queue import refresh_access_token, upload_video
from social_exec_common import YOUTUBE_ENV, load_env
from update_youtube_video_title import fetch_video, update_video

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = REPO_ROOT.parent
SOURCE_ALBUM_DIR = WORKSPACE_ROOT / "Lily Roo - 12 Dollars"
ALBUM_DIR = REPO_ROOT / "assets" / "albums" / "twelve-dollars"
ART_DIR = ALBUM_DIR / "art"
AUDIO_DIR = ALBUM_DIR / "audio"
VIDEO_DIR = ALBUM_DIR / "video"
MANIFEST = REPO_ROOT / "data" / "youtube_twelve_dollars_remaster_manifest.json"
PLAYLIST_OUTPUT = REPO_ROOT / "data" / "youtube_twelve_dollars_playlist.json"
RENDERER = REPO_ROOT / "scripts" / "render_pan_video.swift"

PLAYLIST_ID = "PLit3sD3SUfXVOB41L0JEae6LNTZtrg58n"
PLAYLIST_TITLE = "Twelve Dollars"
PLAYLIST_DESCRIPTION = (
    "The Lily Roo album Twelve Dollars, in track order. Full-bleed remastered YouTube videos "
    "with local DistroKid upload WAV masters."
)
API_ROOT = "https://www.googleapis.com/youtube/v3"
UPLOAD_API_ROOT = "https://www.googleapis.com/upload/youtube/v3"

STREAM_LINKS = [
    "Lily Roo archive: https://www.lilyroo.com/music.html",
]

TRACKS = [
    {
        "track": 1,
        "title": "Brain Rot",
        "old_video_id": "iI5wRXLmTM8",
        "art": "assets/img/remastered/brain-rot-face-shadow-v2.png",
        "audio": "../Lily Roo - 12 Dollars/05_distrokid_upload/01-brain-rot.wav",
        "video": "assets/albums/twelve-dollars/video/01-brain-rot-youtube-remaster.mp4",
        "thumbnail": "assets/albums/twelve-dollars/art/01-brain-rot-youtube-thumbnail.jpg",
    },
    {
        "track": 2,
        "title": "Every Pearl in Carmel",
        "old_video_id": "mJVDj-RJtlg",
        "art": "assets/albums/twelve-dollars/art/02-every-pearl-in-carmel-pan-source.jpg",
        "audio": "../Lily Roo - 12 Dollars/05_distrokid_upload/02-every-pearl-in-carmel.wav",
        "video": "assets/albums/twelve-dollars/video/02-every-pearl-in-carmel-youtube-remaster.mp4",
        "thumbnail": "assets/albums/twelve-dollars/art/02-every-pearl-in-carmel-youtube-thumbnail.jpg",
    },
    {
        "track": 3,
        "title": "The Other One's Charging",
        "old_video_id": "6lXKGPD36dc",
        "art": "assets/albums/twelve-dollars/art/03-the-other-ones-charging-pan-source.jpg",
        "audio": "../Lily Roo - 12 Dollars/05_distrokid_upload/03-the-other-ones-charging.wav",
        "video": "assets/albums/twelve-dollars/video/03-the-other-ones-charging-youtube-remaster.mp4",
        "thumbnail": "assets/albums/twelve-dollars/art/03-the-other-ones-charging-youtube-thumbnail.jpg",
    },
    {
        "track": 4,
        "title": "Twelve Dollars",
        "old_video_id": "8DsCkwBPdhI",
        "existing_video_id": "G2RlCwZKOsk",
        "art": "assets/albums/twelve-dollars/art/04-twelve-dollars.jpg",
        "audio": "assets/albums/twelve-dollars/audio/04-twelve-dollars.wav",
        "video": "assets/albums/twelve-dollars/video/04-twelve-dollars-youtube-remaster.mp4",
        "thumbnail": "assets/albums/twelve-dollars/art/04-twelve-dollars-youtube-thumbnail.jpg",
    },
    {
        "track": 5,
        "title": "William and Dander",
        "old_video_id": "CA7T9sFvRYk",
        "art": "assets/img/William and Dander.jpeg",
        "audio": "../Lily Roo - 12 Dollars/05_distrokid_upload/05-william-and-dander.wav",
        "video": "assets/albums/twelve-dollars/video/05-william-and-dander-youtube-remaster.mp4",
        "thumbnail": "assets/albums/twelve-dollars/art/05-william-and-dander-youtube-thumbnail.jpg",
    },
    {
        "track": 6,
        "title": "Just Don't Talk About It",
        "old_video_id": "5czT_TIS1rQ",
        "art": "assets/albums/twelve-dollars/art/06-just-dont-talk-about-it-pan-source.jpg",
        "audio": "../Lily Roo - 12 Dollars/05_distrokid_upload/06-just-dont-talk-about-it.wav",
        "video": "assets/albums/twelve-dollars/video/06-just-dont-talk-about-it-youtube-remaster.mp4",
        "thumbnail": "assets/albums/twelve-dollars/art/06-just-dont-talk-about-it-youtube-thumbnail.jpg",
    },
    {
        "track": 7,
        "title": "Gluten Free Bread",
        "old_video_id": "tdcQ2mG1j6A",
        "art": "assets/img/Gluten Free Bread.jpeg",
        "audio": "../Lily Roo - 12 Dollars/05_distrokid_upload/07-gluten-free-bread.wav",
        "video": "assets/albums/twelve-dollars/video/07-gluten-free-bread-youtube-remaster.mp4",
        "thumbnail": "assets/albums/twelve-dollars/art/07-gluten-free-bread-youtube-thumbnail.jpg",
    },
    {
        "track": 8,
        "title": "When Lily Talks",
        "old_video_id": "wM6JE2yaDcg",
        "art": "assets/img/When Lily Talks.jpeg",
        "audio": "../Lily Roo - 12 Dollars/05_distrokid_upload/08-when-lily-talks.wav",
        "video": "assets/albums/twelve-dollars/video/08-when-lily-talks-youtube-remaster.mp4",
        "thumbnail": "assets/albums/twelve-dollars/art/08-when-lily-talks-youtube-thumbnail.jpg",
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def repo_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (REPO_ROOT / path).resolve()


def load_manifest() -> dict:
    if not MANIFEST.exists():
        return {"tracks": []}
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if "tracks" in payload:
        return payload
    if payload.get("new_video_id"):
        track_four = next(track for track in TRACKS if track["track"] == 4)
        entry = {
            "track": 4,
            "title": track_four["title"],
            "old_video_id": payload.get("old_video_id", track_four["old_video_id"]),
            "old_url": payload.get("old_url", f"https://youtu.be/{track_four['old_video_id']}"),
            "video_file": payload.get("video_file", track_four["video"]),
            "audio_file": payload.get("audio_file", track_four["audio"]),
            "thumbnail_file": payload.get("youtube_thumbnail_file", track_four["thumbnail"]),
            "new_video_id": payload["new_video_id"],
            "new_url": payload.get("new_url", f"https://youtu.be/{payload['new_video_id']}"),
            "old_archived": True,
            "archive_result": payload.get("archive_result", {}),
            "thumbnail_result": payload.get("thumbnail_result", {}),
        }
        return {"tracks": [entry], "legacy_single_track_manifest": payload}
    return {"tracks": []}


def save_manifest(payload: dict) -> None:
    payload["updated_at"] = utc_now()
    MANIFEST.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_thumbnail(art_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(art_path) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        thumb = ImageOps.fit(image, (1280, 720), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        thumb.save(output_path, "JPEG", quality=92, optimize=True)


def render_video(art_path: Path, audio_path: Path, output_path: Path, *, force: bool) -> None:
    if output_path.exists() and not force:
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["swift", str(RENDERER), str(art_path), str(audio_path), str(output_path)],
        cwd=str(REPO_ROOT),
        check=True,
    )


def description_for(track: dict, new_video_id: str) -> str:
    links = "\n".join(STREAM_LINKS + [f"YouTube Music: https://music.youtube.com/watch?v={new_video_id}"])
    return (
        f"{track['title']} by Lily Roo.\n\n"
        "Full-bleed remastered video for the album Twelve Dollars, using the local DistroKid upload WAV master. "
        "This corrected version fills the 16:9 frame with no sideboxing.\n\n"
        f"{links}\n\n"
        f"Archived original upload: https://youtu.be/{track['old_video_id']}"
    )


def set_thumbnail(token: str, video_id: str, image_path: Path) -> dict:
    url = f"{UPLOAD_API_ROOT}/thumbnails/set?{urllib.parse.urlencode({'videoId': video_id})}"
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


def archive_old_video(token: str, track: dict, new_video_id: str) -> dict:
    video = fetch_video(token, track["old_video_id"])
    snippet = dict(video.get("snippet") or {})
    status = dict(video.get("status") or {})
    if not snippet or not status:
        raise RuntimeError(f"Could not fetch editable metadata for old video {track['old_video_id']}")
    before_title = snippet.get("title", "")
    before_privacy = status.get("privacyStatus", "")
    snippet["title"] = f"{track['title']} - Lily Roo (Archived Original)"[:100]
    prefix = (
        "Archived original upload. The corrected full-bleed remaster is now canonical:\n"
        f"https://youtu.be/{new_video_id}\n\n"
    )
    old_description = snippet.get("description", "")
    if "corrected full-bleed remaster" not in old_description:
        snippet["description"] = (prefix + old_description)[:5000]
    status["privacyStatus"] = "unlisted"
    updated = update_video(token, {"id": track["old_video_id"], "snippet": snippet, "status": status})
    return {
        "before_title": before_title,
        "after_title": (updated.get("snippet") or {}).get("title", ""),
        "before_privacy": before_privacy,
        "after_privacy": (updated.get("status") or {}).get("privacyStatus", ""),
    }


def archive_superseded_video(token: str, video_id: str, title: str, new_video_id: str) -> dict:
    video = fetch_video(token, video_id)
    snippet = dict(video.get("snippet") or {})
    status = dict(video.get("status") or {})
    if not snippet or not status:
        raise RuntimeError(f"Could not fetch editable metadata for superseded video {video_id}")
    before_title = snippet.get("title", "")
    before_privacy = status.get("privacyStatus", "")
    snippet["title"] = f"{title} - Lily Roo (Archived Superseded Remaster)"[:100]
    prefix = (
        "Archived superseded remaster. The corrected full-bleed remaster is now canonical:\n"
        f"https://youtu.be/{new_video_id}\n\n"
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


def api_json(token: str, path: str, params: dict | None = None, *, method: str = "GET", payload: dict | None = None) -> dict:
    url = f"{API_ROOT}/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    if body is not None:
        headers["Content-Type"] = "application/json; charset=UTF-8"
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        if response.status == 204:
            return {}
        raw = response.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def update_playlist(token: str, video_ids: list[str]) -> dict:
    playlist = api_json(token, "playlists", {"part": "snippet,status", "id": PLAYLIST_ID})
    if not playlist.get("items"):
        raise RuntimeError(f"Twelve Dollars playlist not found: {PLAYLIST_ID}")
    status = dict((playlist["items"][0].get("status") or {}))
    status["privacyStatus"] = "public"
    api_json(
        token,
        "playlists",
        {"part": "snippet,status"},
        method="PUT",
        payload={
            "id": PLAYLIST_ID,
            "snippet": {
                "title": PLAYLIST_TITLE,
                "description": PLAYLIST_DESCRIPTION,
            },
            "status": status,
        },
    )

    before_items = list_playlist_items(token, PLAYLIST_ID)
    for item in before_items:
        api_json(token, "playlistItems", {"id": item["id"]}, method="DELETE")
    inserted = [add_video(token, video_id, index) for index, video_id in enumerate(video_ids)]
    after_items = wait_for_playlist_order(token, video_ids)
    payload = {
        "ok": True,
        "updated_at": utc_now(),
        "playlist_id": PLAYLIST_ID,
        "playlist_title": PLAYLIST_TITLE,
        "playlist_url": f"https://www.youtube.com/playlist?list={PLAYLIST_ID}",
        "removed_items": len(before_items),
        "inserted_items": len(inserted),
        "verified_items": len(after_items),
        "tracks": [
            {
                "track": track["track"],
                "title": track["title"],
                "video_id": video_id,
                "url": f"https://youtu.be/{video_id}",
            }
            for track, video_id in zip(TRACKS, video_ids)
        ],
        "current_playlist_order": [
            {
                "position": (item.get("snippet") or {}).get("position"),
                "video_id": (item.get("contentDetails") or {}).get("videoId"),
                "title": (item.get("snippet") or {}).get("title"),
            }
            for item in after_items
        ],
    }
    PLAYLIST_OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def list_playlist_items(token: str, playlist_id: str) -> list[dict]:
    items: list[dict] = []
    page_token = ""
    while True:
        params = {"part": "snippet,contentDetails", "playlistId": playlist_id, "maxResults": 50}
        if page_token:
            params["pageToken"] = page_token
        data = api_json(token, "playlistItems", params)
        items.extend(data.get("items", []))
        page_token = data.get("nextPageToken", "")
        if not page_token:
            return items


def add_video(token: str, video_id: str, position: int) -> dict:
    return api_json(
        token,
        "playlistItems",
        {"part": "snippet"},
        method="POST",
        payload={
            "snippet": {
                "playlistId": PLAYLIST_ID,
                "position": position,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id,
                },
            },
        },
    )


def wait_for_playlist_order(token: str, expected_ids: list[str]) -> list[dict]:
    deadline = time.monotonic() + 45
    last_items: list[dict] = []
    while time.monotonic() < deadline:
        last_items = list_playlist_items(token, PLAYLIST_ID)
        actual_ids = [(item.get("contentDetails") or {}).get("videoId") for item in last_items]
        if actual_ids == expected_ids:
            return last_items
        time.sleep(3)
    return last_items


def main() -> int:
    parser = argparse.ArgumentParser(description="Render, upload, archive, and playlist-sync full-bleed Twelve Dollars videos.")
    parser.add_argument("--apply", action="store_true", help="Upload/archive/update playlist. Default is render/dry-run only.")
    parser.add_argument("--render", action="store_true", help="Render missing local videos and thumbnails.")
    parser.add_argument("--force-render", action="store_true", help="Re-render videos even if output files already exist.")
    parser.add_argument("--skip-uploaded", action="store_true", help="Reuse existing new_video_id values from the manifest.")
    parser.add_argument("--privacy-status", default="public", choices=["public", "unlisted", "private"])
    parser.add_argument("--start-track", type=int, default=1)
    parser.add_argument("--stop-track", type=int, default=8)
    args = parser.parse_args()

    ART_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)

    existing_manifest = load_manifest()
    by_track = {int(item["track"]): item for item in existing_manifest.get("tracks", []) if item.get("track")}
    selected = [track for track in TRACKS if args.start_track <= track["track"] <= args.stop_track]
    token = refresh_access_token(load_env(YOUTUBE_ENV)) if args.apply else ""

    for track in selected:
        art_path = repo_path(track["art"])
        audio_path = repo_path(track["audio"])
        video_path = repo_path(track["video"])
        thumbnail_path = repo_path(track["thumbnail"])
        entry = dict(by_track.get(track["track"], {}))
        entry.pop("error", None)
        new_video_id = (entry.get("new_video_id") or track.get("existing_video_id") or "").strip()

        entry.update({
            "track": track["track"],
            "title": track["title"],
            "old_video_id": track["old_video_id"],
            "old_url": f"https://youtu.be/{track['old_video_id']}",
            "art_file": str(art_path.relative_to(REPO_ROOT)) if art_path.is_relative_to(REPO_ROOT) else str(art_path),
            "audio_file": str(audio_path.relative_to(REPO_ROOT)) if audio_path.is_relative_to(REPO_ROOT) else str(audio_path),
            "video_file": str(video_path.relative_to(REPO_ROOT)),
            "thumbnail_file": str(thumbnail_path.relative_to(REPO_ROOT)),
            "art_exists": art_path.exists(),
            "audio_exists": audio_path.exists(),
            "video_exists": video_path.exists(),
            "thumbnail_exists": thumbnail_path.exists(),
            "new_video_id": new_video_id,
            "new_url": f"https://youtu.be/{new_video_id}" if new_video_id else "",
        })

        missing = [name for name, path in (("art", art_path), ("audio", audio_path)) if not path.exists()]
        if missing:
            entry["error"] = "missing " + ", ".join(missing)
            by_track[track["track"]] = entry
            continue

        if args.render:
            make_thumbnail(art_path, thumbnail_path)
            render_video(art_path, audio_path, video_path, force=args.force_render)
            entry["video_exists"] = video_path.exists()
            entry["video_size"] = video_path.stat().st_size if video_path.exists() else 0
            entry["thumbnail_exists"] = thumbnail_path.exists()
            entry["thumbnail_size"] = thumbnail_path.stat().st_size if thumbnail_path.exists() else 0

        if not video_path.exists():
            entry["error"] = "remaster video file is missing"
            by_track[track["track"]] = entry
            continue

        if args.apply:
            superseded_video_id = new_video_id if new_video_id and not (args.skip_uploaded and new_video_id) else ""
            if not (args.skip_uploaded and new_video_id):
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
            video = fetch_video(token, new_video_id)
            snippet = dict(video.get("snippet") or {})
            status = dict(video.get("status") or {})
            snippet["description"] = description_for(track, new_video_id)[:5000]
            update_video(token, {"id": new_video_id, "snippet": snippet, "status": status})
            if thumbnail_path.exists():
                entry["thumbnail_result"] = set_thumbnail(token, new_video_id, thumbnail_path)
            if superseded_video_id and superseded_video_id != new_video_id:
                entry["superseded_video_id"] = superseded_video_id
                entry["superseded_url"] = f"https://youtu.be/{superseded_video_id}"
                entry["superseded_archive_result"] = archive_superseded_video(
                    token,
                    superseded_video_id,
                    track["title"],
                    new_video_id,
                )
                entry["superseded_archived"] = True
            if track["old_video_id"] != new_video_id:
                entry["archive_result"] = archive_old_video(token, track, new_video_id)
                entry["old_archived"] = True

        entry["new_video_id"] = new_video_id
        entry["new_url"] = f"https://youtu.be/{new_video_id}" if new_video_id else ""
        entry["dry_run"] = not args.apply
        by_track[track["track"]] = entry
        if args.apply:
            interim_tracks = [by_track[k] for k in sorted(by_track)]
            save_manifest({
                "ok": all(item.get("art_exists") and item.get("audio_exists") and item.get("video_exists") and not item.get("error") for item in interim_tracks),
                "applied": args.apply,
                "privacy_status": args.privacy_status,
                "audio_source": "Local Twelve Dollars DistroKid upload WAV masters.",
                "video_source": "Full-bleed crop-fill renders from Twelve Dollars artwork; no sideboxing.",
                "tracks": interim_tracks,
            })

    tracks = [by_track[k] for k in sorted(by_track)]
    payload = {
        "ok": all(item.get("art_exists") and item.get("audio_exists") and item.get("video_exists") and not item.get("error") for item in tracks),
        "applied": args.apply,
        "privacy_status": args.privacy_status,
        "audio_source": "Local Twelve Dollars DistroKid upload WAV masters.",
        "video_source": "Full-bleed crop-fill renders from Twelve Dollars artwork; no sideboxing.",
        "tracks": tracks,
    }
    if args.apply and all(item.get("new_video_id") for item in tracks):
        payload["playlist_result"] = update_playlist(token, [item["new_video_id"] for item in tracks])
    save_manifest(payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
