#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = REPO_ROOT.parent
QUEUE_PATH = REPO_ROOT / 'data' / 'scheduled_posts.csv'
PUBLISHED_LOG = REPO_ROOT / 'admin' / 'content' / 'Published_Log.csv'
SECRETS_DIR = WORKSPACE_ROOT / 'secrets'
SOCIAL_MEDIA_MAP = SECRETS_DIR / 'social-media-map.json'
X_MEDIA_MAP = SECRETS_DIR / 'x-media-map.json'
SOCIAL_ENV = SECRETS_DIR / 'social_api.env'
YOUTUBE_ENV = SECRETS_DIR / 'youtube-api.env'


def load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def load_media_map() -> dict[str, str]:
    merged: dict[str, str] = {}
    for path in (SOCIAL_MEDIA_MAP, X_MEDIA_MAP):
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding='utf-8'))
                if isinstance(data, dict):
                    merged.update({str(k): str(v) for k, v in data.items()})
            except Exception:
                continue
    return merged


def media_map_value(media_key: str = '') -> str:
    media_key = (media_key or '').strip()
    if not media_key:
        return ''
    return load_media_map().get(media_key, '').strip()


def load_queue_rows() -> list[dict[str, str]]:
    with QUEUE_PATH.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def platform_slug(platform: str = '') -> str:
    value = str(platform or '').strip().lower()
    return {
        'youtube community': 'youtube',
        'youtube': 'youtube',
        'x': 'x',
        'twitter': 'x',
        'instagram': 'instagram',
        'tiktok': 'tiktok',
        'facebook': 'facebook',
    }.get(value, value)


def queue_index(rows: list[dict[str, str]] | None = None) -> dict[str, dict[str, str]]:
    source_rows = rows if rows is not None else load_queue_rows()
    return {
        str(row.get('id') or '').strip(): {key: (value or '').strip() for key, value in row.items()}
        for row in source_rows
        if str(row.get('id') or '').strip()
    }


def execution_superseded_reason(item: dict[str, Any], scheduled: dict[str, dict[str, str]] | None = None) -> str:
    post_id = str(item.get('post_id') or item.get('id') or '').strip()
    if not post_id:
        return ''
    scheduled = scheduled if scheduled is not None else queue_index()
    queue_row = scheduled.get(post_id)
    if not queue_row:
        return 'post_id_not_in_current_queue' if post_id.startswith('FP-') else ''
    execution_platform = platform_slug(str(item.get('platform') or ''))
    queue_platform = platform_slug(queue_row.get('platform') or '')
    if execution_platform and queue_platform and execution_platform != queue_platform:
        return f"platform_changed_to_{queue_row.get('platform') or 'current_queue'}"
    if item.get('reason') == 'manual_only' and queue_row.get('execution_mode') != 'manual' and queue_row.get('post_type') != 'community':
        return 'manual_execution_replaced_by_auto_queue_row'
    return ''


def current_execution_rows(rows: list[dict[str, Any]], scheduled: dict[str, dict[str, str]] | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    scheduled = scheduled if scheduled is not None else queue_index()
    current = []
    superseded = []
    for row in rows:
        reason = execution_superseded_reason(row, scheduled)
        if reason:
            item = dict(row)
            item['superseded_reason'] = reason
            superseded.append(item)
        else:
            current.append(row)
    return current, superseded


def get_row(post_id: str) -> dict[str, str]:
    post_id = (post_id or '').strip()
    for row in load_queue_rows():
        if (row.get('id') or '').strip() == post_id:
            return {k: (v or '').strip() for k, v in row.items()}
    raise ValueError(f'post id not found: {post_id}')


def resolve_media_path(media_key: str = '', fallback_path: str = '') -> Path | None:
    media_key = (media_key or '').strip()
    fallback_path = (fallback_path or '').strip()
    candidate = media_map_value(media_key)
    if candidate:
        public_path = local_public_url_path(candidate)
        if public_path:
            return public_path
        path = Path(candidate).expanduser()
        if path.exists():
            return path
    if fallback_path:
        public_path = local_public_url_path(fallback_path)
        if public_path:
            return public_path
    if fallback_path and not fallback_path.startswith('http'):
        path = Path(fallback_path).expanduser()
        if path.exists():
            return path
    return None


def local_public_url_path(value: str) -> Path | None:
    value = (value or '').strip()
    prefixes = ('https://www.lilyroo.com/', 'https://lilyroo.com/')
    for prefix in prefixes:
        if value.startswith(prefix):
            path = REPO_ROOT / value[len(prefix):]
            if path.exists():
                return path
    return None


def public_media_url(row: dict[str, str]) -> str:
    clip = (row.get('clip_url') or '').strip()
    image = (row.get('imagery_url') or '').strip()
    return clip or image


def song_from_row(row: dict[str, str]) -> str:
    explicit = (row.get('song') or row.get('title') or '').strip()
    if explicit:
        return explicit

    imagery = (row.get('imagery') or '').strip()
    markers = [' thumbnail', ' cover', ' performance', ' lyric', ' still']
    lower = imagery.lower()
    for marker in markers:
        idx = lower.find(marker)
        if idx > 0:
            return imagery[:idx].strip(' -:+')

    return ''


def append_published_log(platform: str, posted_url: str, song: str, text: str, notes: str = '', content_id: str = '') -> None:
    PUBLISHED_LOG.parent.mkdir(parents=True, exist_ok=True)
    file_exists = PUBLISHED_LOG.exists()
    default_fieldnames = [
        'date', 'platform', 'post_id_or_url', 'content_id', 'song', 'hook', 'cta_type',
        'youtube_linked', 'lilyroo_linked', 'views', 'likes', 'comments', 'shares', 'saves',
        'subs_delta', 'notes'
    ]
    if file_exists:
        with PUBLISHED_LOG.open(newline='', encoding='utf-8') as existing:
            fieldnames = next(csv.reader(existing), default_fieldnames)
    else:
        fieldnames = default_fieldnames
    from datetime import datetime
    import csv as _csv
    with PUBLISHED_LOG.open('a', newline='', encoding='utf-8') as f:
        writer = _csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        combined = ' '.join(x for x in [text, posted_url] if x)
        row = {
            'date': datetime.now().astimezone().date().isoformat(),
            'platform': platform,
            'post_id_or_url': posted_url or 'posted',
            'content_id': content_id,
            'song_era': song,
            'song': song,
            'hook': (text or '')[:140],
            'cta_type': cta_type(combined),
            'youtube_linked': 'yes' if 'youtu' in combined.lower() else 'no',
            'lilyroo_linked': 'yes' if 'lilyroo.com' in combined.lower() else 'no',
            'views': '', 'likes': '', 'comments': '', 'shares': '', 'saves': '',
            'subs_delta': '',
            'notes': notes,
        }
        writer.writerow({key: row.get(key, '') for key in fieldnames})


def cta_type(text: str) -> str:
    lower = (text or '').lower()
    if 'youtu' in lower:
        return 'youtube_link'
    if 'distrokid.com/hyperfollow' in lower:
        return 'hyperfollow_link'
    if 'open.spotify.com' in lower or 'spotify:' in lower:
        return 'spotify_link'
    if 'lilyroo.com' in lower:
        return 'site_link'
    return ''


def json_dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False)
