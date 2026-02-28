#!/usr/bin/env python3
import csv, json
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/lilyroo/Library/Mobile Documents/com~apple~CloudDocs/Lily Roo')
SOURCE = BASE / 'Backstory' / 'Scheduled_Posts.csv'
FALLBACK_SOURCE = BASE / 'lilyrooartist.github.io' / 'data' / 'scheduled_posts.csv'
if not SOURCE.exists():
    SOURCE = FALLBACK_SOURCE
OUT = BASE / 'lilyrooartist.github.io' / 'admin' / 'future-posts.json'

posts = []
with SOURCE.open(newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        drafts_raw = (r.get('drafts') or '').strip()
        drafts = [d.strip() for d in drafts_raw.split('||') if d.strip()] if drafts_raw else []
        text = (r.get('text') or '').strip()
        if not drafts and text:
            drafts = [text]
        posts.append({
            'id': (r.get('id') or '').strip(),
            'scheduled_at': (r.get('scheduled_at') or '').strip(),
            'platform': (r.get('platform') or '').strip(),
            'imagery': (r.get('imagery') or '').strip(),
            'text': text,
            'drafts': drafts,
        })

posts.sort(key=lambda p: p.get('scheduled_at', ''))
payload = {
    'last_synced': datetime.now(timezone.utc).isoformat(),
    'source': str(SOURCE),
    'posts': posts,
}

OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(f'Wrote {OUT} with {len(posts)} posts')
