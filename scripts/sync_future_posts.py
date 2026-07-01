#!/usr/bin/env python3
import csv, json, re
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/lilyroo/Library/Mobile Documents/com~apple~CloudDocs/Lily Roo')
REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / 'data' / 'scheduled_posts.csv'
FALLBACK_SOURCE = BASE / 'Backstory' / 'Scheduled_Posts.csv'
if not SOURCE.exists():
    SOURCE = FALLBACK_SOURCE
OUT = REPO_ROOT / 'admin' / 'future-posts.json'
PUBLISHED_LOG = REPO_ROOT / 'admin' / 'content' / 'Published_Log.csv'
ADMIN_INDEX = REPO_ROOT / 'admin' / 'index.html'

def infer_post_type(row):
    platform = (row.get('platform') or '').strip().lower()
    media = ((row.get('clip_url') or '') or (row.get('imagery_url') or '')).strip().lower()
    if 'youtube community' in platform:
        return 'community'
    if 'youtube' in platform or 'tiktok' in platform:
        return 'video'
    if media.endswith(('.mp4', '.mov', '.webm')):
        return 'video'
    if media.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
        return 'image'
    return 'text'

def execution_mode(row):
    explicit = (row.get('execution_mode') or '').strip().lower()
    if explicit:
        return explicit
    return 'manual' if infer_post_type(row) == 'community' else 'auto'

def load_published_ids(path: Path):
    ids = set()
    if not path.exists():
        return ids
    with path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            content_id = (r.get('content_id') or '').strip()
            if content_id.startswith('FP-'):
                ids.add(content_id)
            for match in re.findall(r'\bqueue_id=(FP-[A-Z0-9-]+)\b', r.get('notes') or ''):
                ids.add(match)
    return ids

def load_posts(path: Path, published_ids=None):
    items = []
    published_ids = published_ids or set()
    with path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            post_id = (r.get('id') or '').strip()
            if post_id in published_ids:
                continue
            drafts_raw = (r.get('drafts') or '').strip()
            drafts = [d.strip() for d in drafts_raw.split('||') if d.strip()] if drafts_raw else []
            text = (r.get('text') or '').strip()
            if not drafts and text:
                drafts = [text]
            items.append({
                'id': post_id,
                'scheduled_at': (r.get('scheduled_at') or '').strip(),
                'platform': (r.get('platform') or '').strip(),
                'song': (r.get('song') or '').strip(),
                'imagery': (r.get('imagery') or '').strip(),
                'imagery_url': (r.get('imagery_url') or '').strip(),
                'clip_url': (r.get('clip_url') or '').strip(),
                'text': text,
                'drafts': drafts,
                'reply_text': (r.get('reply_text') or '').strip(),
                'x_media_key': (r.get('x_media_key') or '').strip(),
                'media_key': (r.get('media_key') or '').strip(),
                'approved': (r.get('approved') or '').strip(),
                'execution_mode': execution_mode(r),
                'post_type': (r.get('post_type') or infer_post_type(r)).strip(),
                'desired_privacy': (r.get('desired_privacy') or '').strip(),
            })
    return items

published_ids = load_published_ids(PUBLISHED_LOG)

try:
    posts = load_posts(SOURCE, published_ids)
except OSError:
    SOURCE = FALLBACK_SOURCE
    posts = load_posts(SOURCE, published_ids)

posts.sort(key=lambda p: p.get('scheduled_at', ''))
payload = {
    'last_synced': datetime.now(timezone.utc).isoformat(),
    'source': str(SOURCE.relative_to(REPO_ROOT)) if SOURCE.is_relative_to(REPO_ROOT) else str(SOURCE),
    'published_log': str(PUBLISHED_LOG.relative_to(REPO_ROOT)),
    'excluded_published_ids': sorted(published_ids),
    'posts': posts,
}

OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

if ADMIN_INDEX.exists():
    html = ADMIN_INDEX.read_text(encoding='utf-8')
    embedded = json.dumps(payload, indent=2, ensure_ascii=False)
    updated = re.sub(
        r'(<script type="application/json" id="embedded-future-posts">)([\s\S]*?)(</script>)',
        lambda m: m.group(1) + embedded + m.group(3),
        html,
        count=1,
    )
    if updated != html:
        ADMIN_INDEX.write_text(updated, encoding='utf-8')

print(f'Wrote {OUT} with {len(posts)} posts')
