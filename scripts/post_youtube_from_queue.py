#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import urllib.error
import urllib.parse
import urllib.request

from social_exec_common import YOUTUBE_ENV, append_published_log, get_row, load_env, resolve_media_path

TOKEN_URL = 'https://oauth2.googleapis.com/token'
CHANNELS_URL = 'https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true'
UPLOAD_INIT_URL = 'https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status'


def post_form(url: str, data: dict[str, str]) -> dict:
    body = urllib.parse.urlencode(data).encode('utf-8')
    req = urllib.request.Request(url, data=body, method='POST')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))


def refresh_access_token(env: dict[str, str]) -> str:
    required = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'YOUTUBE_REFRESH_TOKEN']
    missing = [k for k in required if not env.get(k)]
    if missing:
        raise RuntimeError(f'Missing YouTube OAuth keys in secrets/youtube-api.env: {", ".join(missing)}')
    data = post_form(TOKEN_URL, {
        'client_id': env['GOOGLE_CLIENT_ID'],
        'client_secret': env['GOOGLE_CLIENT_SECRET'],
        'refresh_token': env['YOUTUBE_REFRESH_TOKEN'],
        'grant_type': 'refresh_token',
    })
    token = data.get('access_token')
    if not token:
        raise RuntimeError(f'Unable to refresh YouTube access token: {data}')
    return token


def authed_json(url: str, token: str) -> dict:
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))


def upload_video(token: str, media_path: str, title: str, description: str, privacy_status: str) -> dict:
    meta = json.dumps({
        'snippet': {
            'title': title[:100],
            'description': description[:5000],
            'categoryId': '10',
        },
        'status': {
            'privacyStatus': privacy_status,
            'selfDeclaredMadeForKids': False,
        }
    }).encode('utf-8')
    mime = mimetypes.guess_type(media_path)[0] or 'video/mp4'
    size = os.path.getsize(media_path)
    init_req = urllib.request.Request(
        UPLOAD_INIT_URL,
        data=meta,
        method='POST',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json; charset=UTF-8',
            'X-Upload-Content-Length': str(size),
            'X-Upload-Content-Type': mime,
        },
    )
    with urllib.request.urlopen(init_req) as resp:
        upload_url = resp.headers.get('Location')
    if not upload_url:
        raise RuntimeError('YouTube resumable upload URL missing from init response')
    with open(media_path, 'rb') as f:
        body = f.read()
    upload_req = urllib.request.Request(
        upload_url,
        data=body,
        method='PUT',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': mime,
            'Content-Length': str(size),
        },
    )
    with urllib.request.urlopen(upload_req) as resp:
        return json.loads(resp.read().decode('utf-8'))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--post-id', required=True)
    parser.add_argument('--text', default='')
    parser.add_argument('--media-key', default='')
    parser.add_argument('--title', default='')
    parser.add_argument('--description', default='')
    parser.add_argument('--privacy-status', default='public')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    row = get_row(args.post_id)
    platform = (row.get('platform') or '').lower()
    if 'youtube' not in platform:
        raise RuntimeError(f'Queue row is not a YouTube post: {row.get("platform") or ""}')
    media_key = (args.media_key or row.get('media_key') or '').strip()
    media_path = resolve_media_path(media_key, row.get('clip_url', ''))
    if not media_path:
        raise RuntimeError('YouTube post needs media_key mapped in secrets/social-media-map.json or a local clip_url path')
    text = (args.text or row.get('text') or '').strip()
    title = (args.title or text or row.get('id') or 'Lily Roo upload').strip()
    description = (args.description or row.get('reply_text') or text).strip()
    env = load_env(YOUTUBE_ENV)
    token = refresh_access_token(env)
    channel = authed_json(CHANNELS_URL, token)
    channel_title = ((channel.get('items') or [{}])[0].get('snippet') or {}).get('title', '')
    if args.dry_run:
        print(json.dumps({
            'ok': True,
            'platform': 'YouTube',
            'dry_run': True,
            'channel_title': channel_title,
            'media_path': str(media_path),
            'title': title[:100],
            'description': description[:200],
            'privacy_status': args.privacy_status,
        }, ensure_ascii=False))
        return 0
    data = upload_video(token, str(media_path), title, description, args.privacy_status)
    video_id = (data.get('id') or '').strip()
    if not video_id:
        raise RuntimeError(f'YouTube upload did not return a video id: {data}')
    video_url = f'https://youtu.be/{video_id}'
    append_published_log('YouTube', video_url, 'Slow Walk', text, 'posted via YouTube Data API')
    print(json.dumps({'ok': True, 'platform': 'YouTube', 'video_id': video_id, 'video_url': video_url}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        raise
