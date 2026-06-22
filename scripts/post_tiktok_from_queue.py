#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import urllib.request
from pathlib import Path
from urllib import parse

from social_exec_common import SOCIAL_ENV, append_published_log, get_row, load_env, resolve_media_path, song_from_row

CREATOR_INFO_URL = 'https://open.tiktokapis.com/v2/post/publish/creator_info/query/'
INIT_URL = 'https://open.tiktokapis.com/v2/post/publish/video/init/'
UPLOAD_INIT_URL = 'https://open.tiktokapis.com/v2/post/publish/inbox/video/init/'
STATUS_URL = 'https://open.tiktokapis.com/v2/post/publish/status/fetch/'
TOKEN_URL = 'https://open.tiktokapis.com/v2/oauth/token/'
REFRESH_TOKEN_NAMES = ['TIKTOK_CLIENT_KEY', 'TIKTOK_CLIENT_SECRET', 'TIKTOK_REFRESH_TOKEN']


def append_or_update_env(path: Path, updates: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding='utf-8').splitlines() if path.exists() else []
    seen: set[str] = set()
    out: list[str] = []
    for raw in existing:
        stripped = raw.strip()
        if stripped and not stripped.startswith('#') and '=' in stripped:
            key = stripped.split('=', 1)[0].strip()
            if key in updates:
                out.append(f'{key}={updates[key]}')
                seen.add(key)
                continue
        out.append(raw)
    for key, value in updates.items():
        if key not in seen:
            out.append(f'{key}={value}')
    path.write_text('\n'.join(out).rstrip() + '\n', encoding='utf-8')


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


def form_post(url: str, payload: dict, timeout: int) -> dict:
    req = urllib.request.Request(
        url,
        data=parse.urlencode(payload).encode('utf-8'),
        method='POST',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'no-cache',
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
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


def boolish(value: str, default: bool) -> bool:
    raw = str(value or '').strip().lower()
    if not raw:
        return default
    return raw in {'1', 'true', 'yes', 'on'}


def missing_refresh_credentials(env: dict[str, str]) -> list[str]:
    return [name for name in REFRESH_TOKEN_NAMES if not str(env.get(name) or '').strip()]


def tiktok_access_token(env: dict[str, str], timeout: int, store_refreshed_token: bool) -> tuple[str, str]:
    token = str(env.get('TIKTOK_ACCESS_TOKEN') or '').strip()
    if token:
        return token, 'access_token'

    missing = missing_refresh_credentials(env)
    if missing:
        raise RuntimeError(f'TikTok posting needs TIKTOK_ACCESS_TOKEN or refresh credentials in secrets/social_api.env: {", ".join(missing)}')

    data = form_post(TOKEN_URL, {
        'client_key': env['TIKTOK_CLIENT_KEY'],
        'client_secret': env['TIKTOK_CLIENT_SECRET'],
        'grant_type': 'refresh_token',
        'refresh_token': env['TIKTOK_REFRESH_TOKEN'],
    }, timeout)
    token = str(data.get('access_token') or '').strip()
    if not token:
        safe = {key: value for key, value in data.items() if key not in {'access_token', 'refresh_token'}}
        raise RuntimeError(f'TikTok refresh did not return an access token: {safe}')

    if store_refreshed_token:
        updates = {'TIKTOK_ACCESS_TOKEN': token}
        refreshed = str(data.get('refresh_token') or '').strip()
        if refreshed:
            updates['TIKTOK_REFRESH_TOKEN'] = refreshed
        append_or_update_env(SOCIAL_ENV, updates)

    return token, 'refresh_token'


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--post-id', required=True)
    parser.add_argument('--text', default='')
    parser.add_argument('--media-key', default='')
    parser.add_argument(
        '--mode',
        choices=['direct', 'upload'],
        default='direct',
        help='direct publishes through video.publish; upload sends an inbox draft through video.upload for final review in TikTok.',
    )
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--store-refreshed-token', action='store_true', help='Write refreshed TikTok token values back to secrets/social_api.env.')
    parser.add_argument('--timeout-seconds', type=int, default=30)
    args = parser.parse_args()

    env = load_env(SOCIAL_ENV)
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
            'mode': args.mode,
            'endpoint': UPLOAD_INIT_URL if args.mode == 'upload' else INIT_URL,
            'required_scope': 'video.upload' if args.mode == 'upload' else 'video.publish',
            'media_key': media_key,
            'media_ready': bool(public_video_url or media_path),
            'public_video_url': public_video_url,
            'media_path': str(media_path) if media_path else '',
            'token_path_ready': bool(env.get('TIKTOK_ACCESS_TOKEN')) or not missing_refresh_credentials(env),
            'token_source': 'access_token' if env.get('TIKTOK_ACCESS_TOKEN') else ('refresh_token' if not missing_refresh_credentials(env) else ''),
            'missing_refresh_credentials': missing_refresh_credentials(env),
            'public_posting_approved': str(env.get('TIKTOK_PUBLIC_POSTING_APPROVED') or '').strip().lower() == 'true',
            'default_privacy': env.get('TIKTOK_DEFAULT_PRIVACY', 'PUBLIC_TO_EVERYONE'),
            'brand_content_toggle': boolish(env.get('TIKTOK_BRAND_CONTENT', ''), False),
            'brand_organic_toggle': boolish(env.get('TIKTOK_BRAND_ORGANIC', ''), True),
            'aigc_label_enabled': boolish(env.get('TIKTOK_IS_AIGC', ''), True),
            'title': title,
        }, ensure_ascii=False))
        return 0

    token, token_source = tiktok_access_token(env, args.timeout_seconds, args.store_refreshed_token)
    if not public_video_url and not media_path:
        raise RuntimeError('TikTok post needs a public clip_url, or media_key mapped in secrets/social-media-map.json, or a local clip_url path')
    payload = {}
    if args.mode == 'direct':
        info = post_json(CREATOR_INFO_URL, token, {})
        options = ((info.get('data') or {}).get('privacy_level_options') or [])
        desired = (row.get('desired_privacy') or env.get('TIKTOK_DEFAULT_PRIVACY') or 'PUBLIC_TO_EVERYONE').strip()
        privacy = desired if desired in options else ('SELF_ONLY' if 'SELF_ONLY' in options else (options[0] if options else 'SELF_ONLY'))
        payload['post_info'] = {
            'title': title,
            'privacy_level': privacy,
            'disable_comment': False,
            'disable_duet': False,
            'disable_stitch': False,
            'brand_content_toggle': boolish(env.get('TIKTOK_BRAND_CONTENT', ''), False),
            'brand_organic_toggle': boolish(env.get('TIKTOK_BRAND_ORGANIC', ''), True),
            'is_aigc': boolish(env.get('TIKTOK_IS_AIGC', ''), True),
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
    init = post_json(UPLOAD_INIT_URL if args.mode == 'upload' else INIT_URL, token, payload)
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
    if args.mode == 'direct':
        append_published_log('TikTok', publish_id, song_from_row(row), title, 'submitted via TikTok Content Posting API', content_id=args.post_id)
    print(json.dumps({
        'ok': True,
        'platform': 'TikTok',
        'mode': args.mode,
        'publish_id': publish_id,
        'status': status_from_payload(status) or 'submitted_for_processing',
        'token_source': token_source,
        'publish_status': status,
        'logged_to_published_log': args.mode == 'direct',
        'next_action': 'Open TikTok inbox notification, finish review, publish, then log the public URL.' if args.mode == 'upload' else 'Check TikTok status and public URL after processing.',
    }, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        raise
