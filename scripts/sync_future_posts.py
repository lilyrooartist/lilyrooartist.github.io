#!/usr/bin/env python3
import csv, json
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/lilyroo/Library/Mobile Documents/com~apple~CloudDocs/Lily Roo')
REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / 'data' / 'scheduled_posts.csv'
FALLBACK_SOURCE = BASE / 'Backstory' / 'Scheduled_Posts.csv'
if not SOURCE.exists():
    SOURCE = FALLBACK_SOURCE
OUT = REPO_ROOT / 'admin' / 'future-posts.json'

def load_posts(path: Path):
    items = []
    with path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            drafts_raw = (r.get('drafts') or '').strip()
            drafts = [d.strip() for d in drafts_raw.split('||') if d.strip()] if drafts_raw else []
            text = (r.get('text') or '').strip()
            if not drafts and text:
                drafts = [text]
            items.append({
                'id': (r.get('id') or '').strip(),
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
            })
    return items

try:
    posts = load_posts(SOURCE)
except OSError:
    SOURCE = FALLBACK_SOURCE
    posts = load_posts(SOURCE)

posts.sort(key=lambda p: p.get('scheduled_at', ''))
payload = {
    'last_synced': datetime.now(timezone.utc).isoformat(),
    'source': str(SOURCE.relative_to(REPO_ROOT)) if SOURCE.is_relative_to(REPO_ROOT) else str(SOURCE),
    'posts': posts,
}

OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(f'Wrote {OUT} with {len(posts)} posts')
