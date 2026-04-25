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


def load_queue_rows() -> list[dict[str, str]]:
    with QUEUE_PATH.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def get_row(post_id: str) -> dict[str, str]:
    post_id = (post_id or '').strip()
    for row in load_queue_rows():
        if (row.get('id') or '').strip() == post_id:
            return {k: (v or '').strip() for k, v in row.items()}
    raise ValueError(f'post id not found: {post_id}')


def resolve_media_path(media_key: str = '', fallback_path: str = '') -> Path | None:
    media_key = (media_key or '').strip()
    fallback_path = (fallback_path or '').strip()
    media_map = load_media_map()
    candidate = media_map.get(media_key) if media_key else None
    if candidate:
        path = Path(candidate).expanduser()
        if path.exists():
            return path
    if fallback_path and not fallback_path.startswith('http'):
        path = Path(fallback_path).expanduser()
        if path.exists():
            return path
    return None


def public_media_url(row: dict[str, str]) -> str:
    clip = (row.get('clip_url') or '').strip()
    image = (row.get('imagery_url') or '').strip()
    return clip or image


def append_published_log(platform: str, posted_url: str, song: str, text: str, notes: str = '') -> None:
    PUBLISHED_LOG.parent.mkdir(parents=True, exist_ok=True)
    file_exists = PUBLISHED_LOG.exists()
    fieldnames = [
        'date', 'platform', 'post_id_or_url', 'content_id', 'song', 'hook', 'cta_type',
        'youtube_linked', 'lilyroo_linked', 'views', 'likes', 'comments', 'shares', 'saves',
        'followers_delta', 'subs_delta', 'notes'
    ]
    from datetime import datetime
    import csv as _csv
    with PUBLISHED_LOG.open('a', newline='', encoding='utf-8') as f:
        writer = _csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        combined = ' '.join(x for x in [text, posted_url] if x)
        writer.writerow({
            'date': datetime.now().astimezone().date().isoformat(),
            'platform': platform,
            'post_id_or_url': posted_url or 'posted',
            'content_id': '',
            'song': song,
            'hook': (text or '')[:140],
            'cta_type': 'youtube_link' if 'youtu' in combined.lower() else ('site_link' if 'lilyroo.com' in combined.lower() else ''),
            'youtube_linked': 'yes' if 'youtu' in combined.lower() else 'no',
            'lilyroo_linked': 'yes' if 'lilyroo.com' in combined.lower() else 'no',
            'views': '', 'likes': '', 'comments': '', 'shares': '', 'saves': '',
            'followers_delta': '', 'subs_delta': '',
            'notes': notes,
        })


def json_dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False)
