#!/usr/bin/env python3
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from post_youtube_from_queue import refresh_access_token
from social_exec_common import YOUTUBE_ENV, load_env

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "data" / "youtube_first_album_remaster_manifest.json"
OUTPUT = REPO_ROOT / "data" / "youtube_first_album_playlist.json"

PLAYLIST_TITLE = "I Learned It All in Fifteen Seconds - Lily Roo"
PLAYLIST_DESCRIPTION = (
    "The first Lily Roo album, in track order. Updated-art remastered videos "
    "with DistroKid Mixea Ultra HD audio masters."
)

API_ROOT = "https://www.googleapis.com/youtube/v3"


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


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_tracks() -> list[dict]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return sorted(manifest["tracks"], key=lambda item: int(item["track"]))


def find_playlist(token: str) -> dict | None:
    data = api_json(token, "playlists", {"part": "snippet,status", "mine": "true", "maxResults": 50})
    for item in data.get("items", []):
        title = (item.get("snippet") or {}).get("title", "")
        if "I Learned" in title and "Fifteen Seconds" in title:
            return item
    return None


def create_playlist(token: str) -> dict:
    return api_json(
        token,
        "playlists",
        {"part": "snippet,status"},
        method="POST",
        payload={
            "snippet": {
                "title": PLAYLIST_TITLE,
                "description": PLAYLIST_DESCRIPTION,
            },
            "status": {
                "privacyStatus": "public",
            },
        },
    )


def update_playlist(token: str, playlist: dict) -> dict:
    playlist_id = playlist["id"]
    status = dict((playlist.get("status") or {}))
    status["privacyStatus"] = "public"
    return api_json(
        token,
        "playlists",
        {"part": "snippet,status"},
        method="PUT",
        payload={
            "id": playlist_id,
            "snippet": {
                "title": PLAYLIST_TITLE,
                "description": PLAYLIST_DESCRIPTION,
            },
            "status": status,
        },
    )


def list_playlist_items(token: str, playlist_id: str) -> list[dict]:
    items: list[dict] = []
    page_token = ""
    while True:
        params = {
            "part": "snippet,contentDetails",
            "playlistId": playlist_id,
            "maxResults": 50,
        }
        if page_token:
            params["pageToken"] = page_token
        data = api_json(token, "playlistItems", params)
        items.extend(data.get("items", []))
        page_token = data.get("nextPageToken", "")
        if not page_token:
            return items


def delete_playlist_item(token: str, item_id: str) -> None:
    api_json(token, "playlistItems", {"id": item_id}, method="DELETE")


def add_video(token: str, playlist_id: str, video_id: str, position: int) -> dict:
    return api_json(
        token,
        "playlistItems",
        {"part": "snippet"},
        method="POST",
        payload={
            "snippet": {
                "playlistId": playlist_id,
                "position": position,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id,
                },
            },
        },
    )


def main() -> int:
    token = refresh_access_token(load_env(YOUTUBE_ENV))
    tracks = load_tracks()
    final_ids = [track["new_video_id"] for track in tracks]

    playlist = find_playlist(token)
    created = playlist is None
    if playlist is None:
        playlist = create_playlist(token)
    playlist = update_playlist(token, playlist)
    playlist_id = playlist["id"]

    before_items = list_playlist_items(token, playlist_id)
    for item in before_items:
        delete_playlist_item(token, item["id"])
    inserted = [add_video(token, playlist_id, video_id, index) for index, video_id in enumerate(final_ids)]
    after_items = list_playlist_items(token, playlist_id)

    payload = {
        "ok": True,
        "updated_at": utc_now(),
        "created": created,
        "playlist_id": playlist_id,
        "playlist_title": PLAYLIST_TITLE,
        "playlist_url": f"https://www.youtube.com/playlist?list={playlist_id}",
        "removed_items": len(before_items),
        "inserted_items": len(inserted),
        "tracks": [
            {
                "track": track["track"],
                "title": track["title"],
                "video_id": track["new_video_id"],
                "url": track["new_url"],
            }
            for track in tracks
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
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
