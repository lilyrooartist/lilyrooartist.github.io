#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import urllib.request

from social_exec_common import SOCIAL_ENV, append_published_log, get_row, load_env, resolve_media_path, song_from_row

CREATOR_INFO_URL = 'https://open.tiktokapis.com/v2/post/publish/creator_info/query/'
INIT_URL = 'https://open.tiktokapis.com/v2/post/publish/video/init/'
STATUS_URL = 'https://open.tiktokapis.com/v2/post/publish/status/fetch/'


def post_json(url: str, token: str, payload: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        method='POST',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json; charset=UTF-8',
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))


def put_bytes(url: str, data: bytes, content_type: str) -> None:
    req = urllib.request.Request(
        url,
        data=data,
        method='PUT',
        headers={
            'Content-Type': content_type,
            'Content-Length': str(len(data)),
            'Content-Range': f'bytes 0-{len(data)-1}/{len(data)}',
        },
    )
    with urllib.request.urlopen(req):
        return


def is_http_url(value: str) -> bool:
    return value.startswith('https://') or value.startswith('http://')


def status_from_payload(payload: dict) -> str:
    return str((payload.get('data') or {}).get('status') or '')


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--post-id', required=True)
    parser.add_argument('--text', default='')
    parser.add_argument('--media-key', default='')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    row = get_row(args.post_id)
    if 'tiktok' not in (row.get('platform') or '').lower():
        raise RuntimeError(f'Queue row is not a TikTok post: {row.get("platform") or ""}')
    media_key = (args.media_key or row.get('media_key') or '').strip()
    clip_url = (row.get('clip_url') or '').strip()
    public_video_url = clip_url if is_http_url(clip_url) else ''
    media_path = None if public_video_url else resolve_media_path(media_key, clip_url)
    title = (args.text or row.get('text') or '').strip()
    if not title:
        raise RuntimeError('TikTok post text/title is required')
    if args.dry_run:
        print(json.dumps({
            'ok': True,
            'platform': 'TikTok',
            'dry_run': True,
            'media_key': media_key,
            'media_ready': bool(public_video_url or media_path),
            'public_video_url': public_video_url,
            'media_path': str(media_path) if media_path else '',
            'title': title,
        }, ensure_ascii=False))
        return 0

    env = load_env(SOCIAL_ENV)
    token = env.get('TIKTOK_ACCESS_TOKEN', '')
    if not token:
        raise RuntimeError('TikTok posting needs TIKTOK_ACCESS_TOKEN in secrets/social_api.env')
    if not public_video_url and not media_path:
        raise RuntimeError('TikTok post needs a public clip_url, or media_key mapped in secrets/social-media-map.json, or a local clip_url path')
    info = post_json(CREATOR_INFO_URL, token, {})
    options = ((info.get('data') or {}).get('privacy_level_options') or [])
    desired = (row.get('desired_privacy') or env.get('TIKTOK_DEFAULT_PRIVACY') or 'PUBLIC_TO_EVERYONE').strip()
    privacy = desired if desired in options else ('SELF_ONLY' if 'SELF_ONLY' in options else (options[0] if options else 'SELF_ONLY'))
    payload = {
        'post_info': {
            'title': title,
            'privacy_level': privacy,
            'disable_comment': False,
            'disable_duet': False,
            'disable_stitch': False,
            'is_aigc': env.get('TIKTOK_IS_AIGC', 'true').strip().lower() not in {'0', 'false', 'no'},
        },
    }
    if public_video_url:
        payload['source_info'] = {
            'source': 'PULL_FROM_URL',
            'video_url': public_video_url,
        }
    else:
        size = os.path.getsize(media_path)
        payload['source_info'] = {
            'source': 'FILE_UPLOAD',
            'video_size': size,
            'chunk_size': size,
            'total_chunk_count': 1,
        }
    init = post_json(INIT_URL, token, payload)
    data = init.get('data') or {}
    upload_url = data.get('upload_url')
    publish_id = data.get('publish_id')
    if not upload_url or not publish_id:
        if public_video_url and publish_id:
            upload_url = ''
        else:
            raise RuntimeError(f'TikTok init failed: {init}')
    if upload_url and media_path:
        mime = mimetypes.guess_type(str(media_path))[0] or 'video/mp4'
        with open(media_path, 'rb') as f:
            put_bytes(upload_url, f.read(), mime)
    status = post_json(STATUS_URL, token, {'publish_id': publish_id})
    append_published_log('TikTok', publish_id, song_from_row(row), title, 'submitted via TikTok Content Posting API', content_id=args.post_id)
    print(json.dumps({'ok': True, 'platform': 'TikTok', 'publish_id': publish_id, 'status': status_from_payload(status) or 'submitted_for_processing', 'publish_status': status}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        raise
