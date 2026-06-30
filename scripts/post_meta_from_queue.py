#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import urllib.parse
import urllib.request

from social_exec_common import SOCIAL_ENV, append_published_log, get_row, load_env, public_media_url, song_from_row

DEFAULT_GRAPH_VERSION = 'v25.0'


def api_post(url: str, data: dict[str, str]) -> dict:
    body = urllib.parse.urlencode(data).encode('utf-8')
    req = urllib.request.Request(url, data=body, method='POST')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))


def graph_base(env: dict[str, str]) -> str:
    version = (env.get('META_GRAPH_VERSION') or DEFAULT_GRAPH_VERSION).strip()
    return f'https://graph.facebook.com/{version}'


def append_cta(text: str, cta: str) -> str:
    text = (text or '').strip()
    cta = (cta or '').strip()
    if not cta:
        return text
    if not text:
        return cta
    if cta in text:
        return text
    return f'{text}\n\n{cta}'


def facebook_post(row: dict[str, str], text: str, env: dict[str, str], dry_run: bool) -> dict:
    media_url = public_media_url(row)
    cta = row.get('reply_text', '')
    force_link = (row.get('post_type') or '').strip().lower() == 'link'
    if dry_run:
        return {
            'ok': True,
            'platform': 'Facebook',
            'dry_run': True,
            'mode': 'photo' if media_url else 'feed',
            'media_url': media_url,
            'link': cta if force_link else '',
            'text': append_cta(text, '' if force_link else cta),
        }
    token = env.get('META_LONG_LIVED_TOKEN', '')
    page_id = env.get('FB_PAGE_ID', '')
    if not token or not page_id:
        raise RuntimeError('Facebook posting needs META_LONG_LIVED_TOKEN and FB_PAGE_ID in secrets/social_api.env')
    if media_url and not force_link:
        data = api_post(f'{graph_base(env)}/{page_id}/photos', {
            'url': media_url,
            'caption': append_cta(text, cta),
            'published': 'true',
            'access_token': token,
        })
    else:
        payload = {'message': append_cta(text, '' if force_link else cta), 'access_token': token}
        if force_link and cta:
            payload['link'] = cta
        data = api_post(f'{graph_base(env)}/{page_id}/feed', payload)
    post_id = data.get('post_id') or data.get('id') or ''
    post_url = f'https://www.facebook.com/{post_id}' if post_id else 'posted'
    append_published_log('Facebook', post_url, song_from_row(row), text, 'posted via Meta Graph API', content_id=row.get('id', ''))
    return {'ok': True, 'platform': 'Facebook', 'post_id': post_id, 'post_url': post_url, 'raw': data}


def instagram_post(row: dict[str, str], text: str, env: dict[str, str], dry_run: bool) -> dict:
    media_url = public_media_url(row)
    if not media_url:
        raise RuntimeError('Instagram posting needs a public imagery_url or clip_url in the queue row')
    lower = media_url.lower()
    is_video = lower.endswith('.mp4') or lower.endswith('.mov') or lower.endswith('.webm')
    if dry_run:
        return {
            'ok': True,
            'platform': 'Instagram',
            'dry_run': True,
            'mode': 'video' if is_video else 'image',
            'media_url': media_url,
            'text': text,
        }
    token = env.get('META_LONG_LIVED_TOKEN', '')
    ig_id = env.get('IG_BUSINESS_ACCOUNT_ID', '')
    if not token or not ig_id:
        raise RuntimeError('Instagram posting needs META_LONG_LIVED_TOKEN and IG_BUSINESS_ACCOUNT_ID in secrets/social_api.env')
    create_payload = {'caption': text, 'access_token': token}
    if is_video:
        create_payload.update({'media_type': 'REELS', 'video_url': media_url})
    else:
        create_payload.update({'image_url': media_url})
    creation = api_post(f'{graph_base(env)}/{ig_id}/media', create_payload)
    creation_id = creation.get('id')
    if not creation_id:
        raise RuntimeError(f'Instagram media creation failed: {creation}')
    publish = api_post(f'{graph_base(env)}/{ig_id}/media_publish', {
        'creation_id': creation_id,
        'access_token': token,
    })
    media_id = publish.get('id') or ''
    append_published_log('Instagram', media_id or 'posted', song_from_row(row), text, 'posted via Instagram Graph API', content_id=row.get('id', ''))
    return {'ok': True, 'platform': 'Instagram', 'creation_id': creation_id, 'media_id': media_id, 'raw': publish}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--post-id', required=True)
    parser.add_argument('--text', default='')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    row = get_row(args.post_id)
    text = (args.text or row.get('text') or '').strip()
    if not text:
        raise RuntimeError('post text is required')
    env = load_env(SOCIAL_ENV)
    platform = (row.get('platform') or '').lower()
    if 'facebook' in platform:
        result = facebook_post(row, text, env, args.dry_run)
    elif 'instagram' in platform:
        result = instagram_post(row, text, env, args.dry_run)
    else:
        raise RuntimeError(f'Unsupported Meta platform: {row.get("platform") or ""}')
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        raise
