#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from social_exec_common import REPO_ROOT, get_row

WORKSPACE = REPO_ROOT.parent
X_SCRIPT = REPO_ROOT / 'scripts' / 'post_x_from_queue.py'
YT_SCRIPT = REPO_ROOT / 'scripts' / 'post_youtube_from_queue.py'
META_SCRIPT = REPO_ROOT / 'scripts' / 'post_meta_from_queue.py'
TIKTOK_SCRIPT = REPO_ROOT / 'scripts' / 'post_tiktok_from_queue.py'


def extract_json_blob(text: str) -> dict | None:
    text = (text or '').strip()
    if not text:
        return None
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1 or end < start:
        return None
    try:
        return json.loads(text[start:end+1])
    except Exception:
        return None


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(200, {'ok': True})

    def do_GET(self):
        if self.path != '/health':
            self._send(404, {'ok': False, 'error': 'Not found'})
            return
        self._send(200, {
            'ok': True,
            'service': 'lilyroo-social-executor',
            'supported_platforms': ['X', 'Instagram', 'Facebook', 'TikTok', 'YouTube Shorts'],
        })

    def do_POST(self):
        if self.path != '/execute':
            self._send(404, {'ok': False, 'error': 'Not found'})
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            payload = json.loads(self.rfile.read(length) or b'{}')
            post_id = (payload.get('postId') or '').strip()
            text = (payload.get('text') or '').strip()
            reply_text = (payload.get('replyText') or '').strip()
            media_key = (payload.get('mediaKey') or '').strip()
            dry_run = bool(payload.get('dryRun'))
            if not post_id:
                raise ValueError('postId is required')
            row = get_row(post_id)
            platform = (row.get('platform') or '').lower()
            cmd = ['python3']
            if 'x' == platform or platform.startswith('x'):
                cmd += [str(X_SCRIPT), '--post-id', post_id]
                if text:
                    cmd += ['--text', text]
                if reply_text:
                    cmd += ['--reply-text', reply_text]
                if media_key or row.get('x_media_key'):
                    cmd += ['--media-key', media_key or row.get('x_media_key', '')]
                if dry_run:
                    cmd += ['--dry-run']
            elif 'youtube' in platform:
                cmd += [str(YT_SCRIPT), '--post-id', post_id]
                if text:
                    cmd += ['--text', text]
                if media_key or row.get('media_key'):
                    cmd += ['--media-key', media_key or row.get('media_key', '')]
                if dry_run:
                    cmd += ['--dry-run']
            elif 'instagram' in platform or 'facebook' in platform:
                cmd += [str(META_SCRIPT), '--post-id', post_id]
                if text:
                    cmd += ['--text', text]
                if dry_run:
                    cmd += ['--dry-run']
            elif 'tiktok' in platform:
                cmd += [str(TIKTOK_SCRIPT), '--post-id', post_id]
                if text:
                    cmd += ['--text', text]
                if media_key or row.get('media_key'):
                    cmd += ['--media-key', media_key or row.get('media_key', '')]
                if dry_run:
                    cmd += ['--dry-run']
            else:
                raise RuntimeError(f'Unsupported platform: {row.get("platform") or ""}')
            result = subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=str(REPO_ROOT))
            stdout = (result.stdout or '').strip()
            stderr = (result.stderr or '').strip()
            if result.returncode != 0:
                payload = extract_json_blob(stdout) or extract_json_blob(stderr)
                if isinstance(payload, dict):
                    self._send(500, payload)
                    return
                self._send(500, {'ok': False, 'error': stderr or stdout or 'unknown error'})
                return
            data = extract_json_blob(stdout) or {'ok': True}
            self._send(200, data)
        except Exception as exc:
            self._send(500, {'ok': False, 'error': str(exc)})


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 8765), Handler)
    print('social_execute_bridge listening on http://127.0.0.1:8765')
    server.serve_forever()
