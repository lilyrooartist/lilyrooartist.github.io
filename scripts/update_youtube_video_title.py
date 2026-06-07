#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request

from post_youtube_from_queue import refresh_access_token
from social_exec_common import YOUTUBE_ENV, load_env

VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
DEFAULT_VIDEO_ID = "vK0mDIW65o4"
DEFAULT_TITLE = "I Learned It All in Fifteen Seconds"
OLD_TITLE = "I Learned it all in Fifteen Seconds"


def api_json(url: str, token: str, *, method: str = "GET", payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    if body is not None:
        headers["Content-Type"] = "application/json; charset=UTF-8"
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"error": raw}
        raise RuntimeError(f"YouTube API {method} failed ({exc.code}): {json.dumps(data, ensure_ascii=False)}") from exc


def fetch_video(token: str, video_id: str) -> dict:
    params = urllib.parse.urlencode({
        "part": "snippet,status",
        "id": video_id,
    })
    data = api_json(f"{VIDEOS_URL}?{params}", token)
    items = data.get("items") or []
    if not items:
        raise RuntimeError(f"YouTube video not found or not owned by this OAuth account: {video_id}")
    return items[0]


def update_title_resource(video: dict, title: str, *, normalize_description: bool = False) -> dict:
    snippet = dict(video.get("snippet") or {})
    status = dict(video.get("status") or {})
    if not snippet:
        raise RuntimeError("YouTube response did not include snippet metadata.")
    if not status:
        raise RuntimeError("YouTube response did not include status metadata.")
    before_title = snippet.get("title", "")
    before_description = snippet.get("description", "")
    snippet["title"] = title[:100]
    if normalize_description:
        snippet["description"] = before_description.replace(OLD_TITLE, title)
    return {
        "id": video.get("id"),
        "snippet": snippet,
        "status": status,
        "_before_title": before_title,
        "_before_description": before_description,
    }


def update_video(token: str, resource: dict) -> dict:
    payload = {
        "id": resource["id"],
        "snippet": resource["snippet"],
        "status": resource["status"],
    }
    params = urllib.parse.urlencode({"part": "snippet,status"})
    return api_json(f"{VIDEOS_URL}?{params}", token, method="PUT", payload=payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely update the public title of an existing Lily Roo YouTube video.")
    parser.add_argument("--video-id", default=DEFAULT_VIDEO_ID)
    parser.add_argument("--title", default=DEFAULT_TITLE)
    parser.add_argument("--normalize-description", action="store_true", help="Replace old title casing inside the video description too.")
    parser.add_argument("--apply", action="store_true", help="Actually call videos.update. Without this, only prints the planned change.")
    args = parser.parse_args()

    env = load_env(YOUTUBE_ENV)
    token = refresh_access_token(env)
    video = fetch_video(token, args.video_id)
    resource = update_title_resource(video, args.title, normalize_description=args.normalize_description)
    before_description = resource["_before_description"]
    after_description = resource["snippet"].get("description", "")
    result = {
        "ok": True,
        "dry_run": not args.apply,
        "video_id": args.video_id,
        "before_title": resource["_before_title"],
        "after_title": resource["snippet"]["title"],
        "description_changed": before_description != after_description,
        "privacy_status": resource["status"].get("privacyStatus", ""),
    }
    if args.apply:
        updated = update_video(token, resource)
        result["updated_title"] = (updated.get("snippet") or {}).get("title", "")
        result["updated_description_changed"] = result["description_changed"]
        result["url"] = f"https://www.youtube.com/watch?v={args.video_id}"
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2, ensure_ascii=False))
        raise SystemExit(1)
