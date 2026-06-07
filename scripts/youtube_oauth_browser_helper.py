#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import base64
import hashlib
import secrets
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SECRETS_DIR = REPO_ROOT.parent / "secrets"
YOUTUBE_ENV = SECRETS_DIR / "youtube-api.env"
HOST = "127.0.0.1"
PORT = 8766
REDIRECT_URI = f"http://{HOST}:{PORT}"
TOKEN_URL = "https://oauth2.googleapis.com/token"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

state = {
    "csrf": "",
    "client_id": "",
    "client_secret": "",
    "code_verifier": "",
    "last_error": "",
    "saved": False,
}


def load_existing_env() -> dict[str, str]:
    values: dict[str, str] = {}
    if not YOUTUBE_ENV.exists():
        return values
    for raw in YOUTUBE_ENV.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def start_google_consent(client_id: str, client_secret: str = "") -> str:
    if not client_id:
        raise ValueError("Client ID is required.")
    state["client_id"] = client_id
    state["client_secret"] = client_secret
    state["csrf"] = secrets.token_urlsafe(24)
    state["code_verifier"] = secrets.token_urlsafe(64)
    state["last_error"] = ""
    params = urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": state["csrf"],
        "code_challenge": code_challenge(state["code_verifier"]),
        "code_challenge_method": "S256",
    })
    return f"{AUTH_URL}?{params}"


def page(title: str, body: str) -> bytes:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px auto; max-width: 820px; line-height: 1.45; }}
    label {{ display:block; font-weight:700; margin-top:18px; }}
    input, textarea {{ box-sizing:border-box; width:100%; padding:10px; font:inherit; border:1px solid #b9c0ca; border-radius:6px; }}
    textarea {{ min-height:150px; }}
    button {{ margin-top:18px; padding:10px 16px; font:inherit; font-weight:700; border:0; border-radius:6px; background:#1a5fb4; color:white; cursor:pointer; }}
    code {{ background:#f3f5f7; padding:2px 5px; border-radius:4px; }}
    .note {{ background:#f7f9fc; border:1px solid #d8e0ec; border-radius:8px; padding:14px; }}
    .error {{ background:#fff3f1; border-color:#f2b8af; }}
    .ok {{ background:#effaf1; border-color:#a6d9ad; }}
  </style>
</head>
<body>{body}</body>
</html>""".encode("utf-8")


def parse_form(body: bytes) -> dict[str, str]:
    parsed = urllib.parse.parse_qs(body.decode("utf-8"), keep_blank_values=True)
    return {key: values[-1].strip() for key, values in parsed.items()}


def oauth_values(form: dict[str, str]) -> tuple[str, str]:
    raw_json = form.get("client_json", "")
    if raw_json:
        data = json.loads(raw_json)
        payload = data.get("installed") or data.get("web") or data
        return str(payload["client_id"]).strip(), str(payload.get("client_secret", "")).strip()
    return form.get("client_id", ""), form.get("client_secret", "")


def code_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def exchange_code(code: str) -> dict:
    params = {
        "code": code,
        "client_id": state["client_id"],
        "code_verifier": state["code_verifier"],
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    if state["client_secret"]:
        params["client_secret"] = state["client_secret"]
    body = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(TOKEN_URL, data=body, method="POST", headers={
        "Content-Type": "application/x-www-form-urlencoded",
    })
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise ValueError(f"Token exchange failed ({exc.code}): {body}") from exc


def save_env(refresh_token: str) -> None:
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    lines = [f"GOOGLE_CLIENT_ID={state['client_id']}"]
    if state["client_secret"]:
        lines.append(f"GOOGLE_CLIENT_SECRET={state['client_secret']}")
    lines.extend([f"YOUTUBE_REFRESH_TOKEN={refresh_token}", ""])
    YOUTUBE_ENV.write_text("\n".join(lines), encoding="utf-8")
    YOUTUBE_ENV.chmod(0o600)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return

    def send_html(self, code: int, body: bytes) -> None:
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def redirect(self, url: str) -> None:
        self.send_response(302)
        self.send_header("Location", url)
        self.end_headers()

    def do_GET(self) -> None:
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if self.path.startswith("/oauth2callback") or query.get("code") or query.get("error"):
            return self.oauth_callback()
        if self.path.startswith("/existing"):
            try:
                values = load_existing_env()
                return self.redirect(start_google_consent(
                    values.get("GOOGLE_CLIENT_ID", ""),
                    values.get("GOOGLE_CLIENT_SECRET", ""),
                ))
            except Exception as exc:
                state["last_error"] = str(exc)
                return self.redirect("/")
        message = ""
        if state["last_error"]:
            message = f'<div class="note error"><b>Error:</b> {html.escape(state["last_error"])}</div>'
        self.send_html(200, page("YouTube OAuth Setup", f"""
<h1>YouTube OAuth Setup</h1>
<div class="note">
  <p>This helper saves <code>{html.escape(str(YOUTUBE_ENV))}</code> locally. Secret values are not printed.</p>
  <p>Use a Google OAuth <b>Desktop app</b> client. The helper uses PKCE, so the client secret is optional for current Desktop clients.</p>
  <p>This flow requests YouTube upload and video-management scopes so uploads can be made public and old uploads can be deleted.</p>
</div>
{message}
<form method="get" action="/existing">
  <button type="submit">Use saved OAuth client</button>
</form>
<form method="post" action="/start">
  <label for="client_json">OAuth client JSON</label>
  <textarea id="client_json" name="client_json" placeholder='Paste downloaded client JSON here, or use the fields below'></textarea>
  <label for="client_id">Client ID</label>
  <input id="client_id" name="client_id" autocomplete="off">
  <label for="client_secret">Client secret (optional)</label>
  <input id="client_secret" name="client_secret" autocomplete="off">
  <button type="submit">Start Google consent</button>
</form>
"""))

    def do_POST(self) -> None:
        if self.path != "/start":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        try:
            form = parse_form(self.rfile.read(length))
            client_id, client_secret = oauth_values(form)
            self.redirect(start_google_consent(client_id, client_secret))
        except Exception as exc:
            state["last_error"] = str(exc)
            self.redirect("/")

    def oauth_callback(self) -> None:
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        try:
            if query.get("state", [""])[-1] != state["csrf"]:
                raise ValueError("OAuth state did not match. Start again.")
            if query.get("error"):
                raise ValueError(query.get("error_description", query["error"])[-1])
            code = query.get("code", [""])[-1]
            if not code:
                raise ValueError("OAuth callback did not include a code.")
            token_data = exchange_code(code)
            refresh_token = token_data.get("refresh_token", "")
            if not refresh_token:
                raise ValueError("Google did not return a refresh token. Start again and make sure prompt=consent is used.")
            save_env(refresh_token)
            state["saved"] = True
            self.send_html(200, page("YouTube OAuth Saved", f"""
<h1>YouTube OAuth Saved</h1>
<div class="note ok">
  <p>Saved YouTube OAuth credentials to <code>{html.escape(str(YOUTUBE_ENV))}</code>.</p>
  <p>Next, run <code>python3 scripts/update_youtube_video_title.py --apply</code> from the site repo to fix the first single title capitalization.</p>
  <p>You can close this tab.</p>
</div>
"""))
        except Exception as exc:
            state["last_error"] = str(exc)
            self.redirect("/")


def main() -> int:
    print(f"YouTube OAuth helper listening at http://{HOST}:{PORT}")
    print(f"Redirect URI: {REDIRECT_URI}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
