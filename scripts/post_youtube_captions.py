#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

from post_youtube_from_queue import refresh_access_token
from social_exec_common import YOUTUBE_ENV, load_env

CAPTIONS_UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/captions"


def multipart_body(metadata: dict, caption_path: Path, mime: str) -> tuple[bytes, str]:
    boundary = f"LilyRoo{uuid.uuid4().hex}"
    caption_bytes = caption_path.read_bytes()
    parts = [
        (
            f"--{boundary}\r\n"
            "Content-Type: application/json; charset=UTF-8\r\n\r\n"
            f"{json.dumps(metadata, ensure_ascii=False)}\r\n"
        ).encode("utf-8"),
        (
            f"--{boundary}\r\n"
            f"Content-Type: {mime}\r\n\r\n"
        ).encode("utf-8"),
        caption_bytes,
        f"\r\n--{boundary}--\r\n".encode("utf-8"),
    ]
    return b"".join(parts), boundary


def upload_captions(token: str, video_id: str, caption_path: Path, language: str, name: str) -> dict:
    mime = "application/octet-stream"
    metadata = {
        "kind": "youtube#caption",
        "snippet": {
            "videoId": video_id,
            "language": language,
            "name": name,
            "isDraft": False,
        }
    }
    body, boundary = multipart_body(metadata, caption_path, mime)
    url = f"{CAPTIONS_UPLOAD_URL}?{urllib.parse.urlencode({'uploadType': 'multipart', 'part': 'snippet'})}"
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/related; boundary={boundary}",
            "Content-Length": str(len(body)),
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"YouTube captions upload failed ({exc.code}): {detail}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video-id", required=True)
    parser.add_argument("--caption-file", required=True)
    parser.add_argument("--language", default="en")
    parser.add_argument("--name", default="English")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    caption_path = Path(args.caption_file)
    if not caption_path.exists():
        raise FileNotFoundError(caption_path)

    if args.dry_run:
        print(json.dumps({
            "ok": True,
            "dry_run": True,
            "video_id": args.video_id,
            "caption_file": str(caption_path),
            "language": args.language,
            "name": args.name,
        }, ensure_ascii=False))
        return 0

    env = load_env(YOUTUBE_ENV)
    token = refresh_access_token(env)
    data = upload_captions(token, args.video_id, caption_path, args.language, args.name)
    print(json.dumps({"ok": True, "platform": "YouTube", "caption_id": data.get("id", ""), "raw": data}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        raise
