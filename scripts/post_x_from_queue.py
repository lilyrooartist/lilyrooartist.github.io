#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import mimetypes
import os
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

from social_exec_common import (
    SOCIAL_ENV,
    append_published_log,
    get_row,
    load_env,
    media_map_value,
    resolve_media_path,
    song_from_row,
)

CREATE_POST_URL = 'https://api.x.com/2/tweets'
MEDIA_UPLOAD_URL = 'https://upload.twitter.com/1.1/media/upload.json'


def env_value(env: dict[str, str], *names: str) -> str:
    for name in names:
        value = (env.get(name) or '').strip()
        if value:
            return value
    return ''


def oauth_quote(value: str) -> str:
    return urllib.parse.quote(str(value), safe='~-._')


def oauth1_keys(env: dict[str, str]) -> dict[str, str]:
    return {
        'consumer_key': env_value(env, 'X_API_KEY', 'TWITTER_API_KEY', 'X_CONSUMER_KEY', 'TWITTER_CONSUMER_KEY'),
        'consumer_secret': env_value(env, 'X_API_SECRET', 'TWITTER_API_SECRET', 'X_CONSUMER_SECRET', 'TWITTER_CONSUMER_SECRET'),
        'token': env_value(env, 'X_ACCESS_TOKEN', 'TWITTER_ACCESS_TOKEN'),
        'token_secret': env_value(env, 'X_ACCESS_TOKEN_SECRET', 'TWITTER_ACCESS_TOKEN_SECRET'),
    }


def oauth1_header(method: str, url: str, env: dict[str, str], extra_params: dict[str, str] | None = None) -> str:
    keys = oauth1_keys(env)
    missing = [name for name, value in keys.items() if not value]
    if missing:
        raise RuntimeError(
            'X OAuth 1.0a posting needs X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, '
            'and X_ACCESS_TOKEN_SECRET in secrets/social_api.env'
        )
    params = {
        'oauth_consumer_key': keys['consumer_key'],
        'oauth_nonce': uuid.uuid4().hex,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_token': keys['token'],
        'oauth_version': '1.0',
    }
    if extra_params:
        params.update(extra_params)
    encoded = '&'.join(f'{oauth_quote(k)}={oauth_quote(v)}' for k, v in sorted(params.items()))
    base = '&'.join([method.upper(), oauth_quote(url), oauth_quote(encoded)])
    signing_key = f'{oauth_quote(keys["consumer_secret"])}&{oauth_quote(keys["token_secret"])}'.encode('utf-8')
    digest = hmac.new(signing_key, base.encode('utf-8'), hashlib.sha1).digest()
    params['oauth_signature'] = base64.b64encode(digest).decode('ascii')
    return 'OAuth ' + ', '.join(f'{oauth_quote(k)}="{oauth_quote(v)}"' for k, v in sorted(params.items()))


def bearer_token(env: dict[str, str]) -> str:
    return env_value(env, 'X_USER_ACCESS_TOKEN', 'X_BEARER_TOKEN', 'TWITTER_BEARER_TOKEN')


def authed_json_post(url: str, payload: dict, env: dict[str, str]) -> dict:
    body = json.dumps(payload).encode('utf-8')
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    token = bearer_token(env)
    if token:
        headers['Authorization'] = f'Bearer {token}'
    else:
        headers['Authorization'] = oauth1_header('POST', url, env)
    req = urllib.request.Request(url, data=body, method='POST', headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))


def multipart_body(field_name: str, path: Path) -> tuple[bytes, str]:
    boundary = '----lilyroo-' + uuid.uuid4().hex
    mime = mimetypes.guess_type(str(path))[0] or 'application/octet-stream'
    chunks = [
        f'--{boundary}\r\n'.encode('utf-8'),
        (
            f'Content-Disposition: form-data; name="{field_name}"; '
            f'filename="{path.name}"\r\nContent-Type: {mime}\r\n\r\n'
        ).encode('utf-8'),
        path.read_bytes(),
        f'\r\n--{boundary}--\r\n'.encode('utf-8'),
    ]
    return b''.join(chunks), f'multipart/form-data; boundary={boundary}'


def upload_image(path: Path, env: dict[str, str]) -> str:
    body, content_type = multipart_body('media', path)
    req = urllib.request.Request(
        MEDIA_UPLOAD_URL,
        data=body,
        method='POST',
        headers={
            'Authorization': oauth1_header('POST', MEDIA_UPLOAD_URL, env),
            'Content-Type': content_type,
            'Content-Length': str(len(body)),
        },
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    media_id = str(data.get('media_id_string') or data.get('media_id') or '').strip()
    if not media_id:
        raise RuntimeError(f'X media upload did not return a media id: {data}')
    return media_id


def media_ids_from_key(media_key: str, row: dict[str, str], env: dict[str, str]) -> list[str]:
    media_key = (media_key or row.get('x_media_key') or '').strip()
    if not media_key:
        return []

    mapped = media_map_value(media_key)
    if mapped:
        ids = [part.strip() for part in mapped.split(',') if part.strip()]
        if ids and all(part.isdigit() for part in ids):
            return ids

    path = resolve_media_path(media_key, row.get('imagery_url', ''))
    if not path:
        raise RuntimeError(
            'X post media_key must map to a numeric media id in secrets/x-media-map.json '
            'or to a local image path for upload'
        )
    if path.suffix.lower() not in {'.jpg', '.jpeg', '.png', '.gif', '.webp'}:
        raise RuntimeError('X local media upload currently supports images only; use a pre-uploaded media id for video/GIF')
    return [upload_image(path, env)]


def create_post(text: str, env: dict[str, str], media_ids: list[str] | None = None, reply_to: str = '') -> dict:
    payload: dict = {'text': text}
    if media_ids:
        payload['media'] = {'media_ids': media_ids}
    if reply_to:
        payload['reply'] = {'in_reply_to_tweet_id': reply_to}
    return authed_json_post(CREATE_POST_URL, payload, env)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--post-id', required=True)
    parser.add_argument('--text', default='')
    parser.add_argument('--reply-text', default='')
    parser.add_argument('--media-key', default='')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    row = get_row(args.post_id)
    platform = (row.get('platform') or '').lower()
    if platform != 'x' and not platform.startswith('x'):
        raise RuntimeError(f'Queue row is not an X post: {row.get("platform") or ""}')

    text = (args.text or row.get('text') or '').strip()
    reply_text = (args.reply_text or row.get('reply_text') or '').strip()
    media_key = (args.media_key or row.get('x_media_key') or '').strip()
    if not text:
        raise RuntimeError('X post text is required')

    if args.dry_run:
        print(json.dumps({
            'ok': True,
            'platform': 'X',
            'dry_run': True,
            'text': text,
            'reply_text': reply_text,
            'media_key': media_key,
            'auth_modes': ['bearer', 'oauth1'],
        }, ensure_ascii=False))
        return 0

    env = load_env(SOCIAL_ENV)
    media_ids = media_ids_from_key(media_key, row, env)
    data = create_post(text, env, media_ids=media_ids)
    post_id = str(((data.get('data') or {}).get('id') or '')).strip()
    if not post_id:
        raise RuntimeError(f'X create post did not return an id: {data}')

    reply_id = ''
    if reply_text:
        reply = create_post(reply_text, env, reply_to=post_id)
        reply_id = str(((reply.get('data') or {}).get('id') or '')).strip()

    post_url = f'https://x.com/i/web/status/{post_id}'
    append_published_log('X', post_url, song_from_row(row), text, 'posted via X API')
    print(json.dumps({
        'ok': True,
        'platform': 'X',
        'tweet_id': post_id,
        'tweet_url': post_url,
        'reply_id': reply_id,
    }, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        raise
