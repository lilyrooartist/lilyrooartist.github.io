#!/usr/bin/env python3
"""Local-only setup form for the AOL -> Gmail bridge secrets."""

from __future__ import annotations

import argparse
import html
import subprocess
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = REPO_ROOT.parent / "secrets" / "aol-gmail-bridge.env"
BRIDGE = REPO_ROOT / "scripts" / "aol_gmail_bridge.py"

DEFAULTS = {
    "AOL_EMAIL": "lilyroo.artist@aol.com",
    "AOL_APP_PASSWORD": "",
    "AOL_IMAP_HOST": "imap.aol.com",
    "AOL_IMAP_PORT": "993",
    "AOL_MAILBOX": "INBOX",
    "GMAIL_EMAIL": "lilyroo.artist@gmail.com",
    "GMAIL_APP_PASSWORD": "",
    "GMAIL_IMAP_HOST": "imap.gmail.com",
    "GMAIL_IMAP_PORT": "993",
    "GMAIL_MAILBOX": "INBOX",
    "STATE_PATH": "../secrets/aol-gmail-bridge-state.json",
}


def load_env() -> dict[str, str]:
    values = dict(DEFAULTS)
    if not ENV_PATH.exists():
        return values
    for raw in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key in values:
            values[key] = value.strip().strip('"').strip("'")
    return values


def save_env(values: dict[str, str]) -> None:
    ENV_PATH.parent.mkdir(parents=True, exist_ok=True)
    ordered = [
        "AOL_EMAIL",
        "AOL_APP_PASSWORD",
        "AOL_IMAP_HOST",
        "AOL_IMAP_PORT",
        "AOL_MAILBOX",
        "",
        "GMAIL_EMAIL",
        "GMAIL_APP_PASSWORD",
        "GMAIL_IMAP_HOST",
        "GMAIL_IMAP_PORT",
        "GMAIL_MAILBOX",
        "",
        "STATE_PATH",
    ]
    lines = []
    for key in ordered:
        if not key:
            lines.append("")
        else:
            lines.append(f"{key}={values.get(key, DEFAULTS.get(key, ''))}")
    ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ENV_PATH.chmod(0o600)


def masked(value: str) -> str:
    return "set" if value.strip() else "missing"


def run_bridge_check() -> str:
    result = subprocess.run(
        ["python3", str(BRIDGE), "--env", str(ENV_PATH), "--check-logins"],
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=45,
    )
    return result.stdout.strip() or result.stderr.strip() or f"exit={result.returncode}"


def page(values: dict[str, str], message: str = "") -> str:
    def input_row(key: str, label: str, kind: str = "text") -> str:
        value = html.escape(values.get(key, ""))
        return f"""
        <label>{html.escape(label)}
          <input name="{html.escape(key)}" type="{kind}" value="{value}" autocomplete="off">
        </label>
        """

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AOL to Gmail Bridge Setup</title>
  <style>
    body{{font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:0;background:#111827;color:#e5e7eb}}
    main{{max-width:760px;margin:0 auto;padding:28px}}
    h1{{margin:0 0 8px;font-size:28px}}
    p{{color:#aab2c5;line-height:1.5}}
    form{{display:grid;gap:14px;margin-top:18px}}
    section{{border:1px solid #334155;background:#172033;border-radius:12px;padding:16px}}
    label{{display:grid;gap:6px;margin:10px 0;color:#cfd8eb;font-size:13px;font-weight:700}}
    input{{box-sizing:border-box;width:100%;border:1px solid #475569;background:#0b1020;color:#f8fafc;border-radius:8px;padding:10px;font-size:14px}}
    button{{width:max-content;border:0;border-radius:8px;background:#2563eb;color:#fff;padding:10px 14px;font-weight:800;cursor:pointer}}
    .status{{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}}
    .chip{{border:1px solid #475569;border-radius:999px;padding:5px 9px;color:#d8e2f5;background:#111827;font-size:12px;font-weight:800}}
    .ok{{border-color:#178c5a;color:#9bf0c5}}
    .bad{{border-color:#89404b;color:#ffb8c0}}
    pre{{white-space:pre-wrap;background:#0b1020;border:1px solid #334155;border-radius:10px;padding:12px;color:#dbeafe}}
  </style>
</head>
<body>
<main>
  <h1>AOL to Gmail Bridge Setup</h1>
  <p>Paste app passwords here. This page is served only on <code>127.0.0.1</code> and saves to <code>{html.escape(str(ENV_PATH))}</code>; secrets are not printed back after saving.</p>
  <div class="status">
    <span class="chip {'ok' if values.get('AOL_APP_PASSWORD') else 'bad'}">AOL password: {masked(values.get('AOL_APP_PASSWORD', ''))}</span>
    <span class="chip {'ok' if values.get('GMAIL_APP_PASSWORD') else 'bad'}">Gmail password: {masked(values.get('GMAIL_APP_PASSWORD', ''))}</span>
  </div>
  {f"<pre>{html.escape(message)}</pre>" if message else ""}
  <form method="post">
    <section>
      <h2>AOL source</h2>
      {input_row('AOL_EMAIL', 'AOL email')}
      {input_row('AOL_APP_PASSWORD', 'AOL app password', 'password')}
      {input_row('AOL_IMAP_HOST', 'AOL IMAP host')}
      {input_row('AOL_IMAP_PORT', 'AOL IMAP port')}
      {input_row('AOL_MAILBOX', 'AOL mailbox')}
    </section>
    <section>
      <h2>Gmail destination</h2>
      {input_row('GMAIL_EMAIL', 'Gmail email')}
      {input_row('GMAIL_APP_PASSWORD', 'Gmail app password', 'password')}
      {input_row('GMAIL_IMAP_HOST', 'Gmail IMAP host')}
      {input_row('GMAIL_IMAP_PORT', 'Gmail IMAP port')}
      {input_row('GMAIL_MAILBOX', 'Gmail mailbox')}
      {input_row('STATE_PATH', 'State path')}
    </section>
    <button name="action" value="save" type="submit">Save secrets</button>
    <button name="action" value="save-test" type="submit">Save and test login</button>
  </form>
</main>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        return

    def send_page(self, values: dict[str, str], message: str = "") -> None:
        body = page(values, message).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        self.send_page(load_env())

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0") or 0)
        form = urllib.parse.parse_qs(self.rfile.read(length).decode("utf-8"), keep_blank_values=True)
        current = load_env()
        for key in DEFAULTS:
            current[key] = form.get(key, [current.get(key, "")])[0].strip()
        save_env(current)
        message = f"Saved {ENV_PATH}."
        if form.get("action", ["save"])[0] == "save-test":
            message += "\n\n" + run_bridge_check()
        redacted = dict(current)
        redacted["AOL_APP_PASSWORD"] = "saved" if current.get("AOL_APP_PASSWORD") else ""
        redacted["GMAIL_APP_PASSWORD"] = "saved" if current.get("GMAIL_APP_PASSWORD") else ""
        self.send_page(redacted, message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local AOL Gmail bridge setup helper.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4189)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"AOL/Gmail bridge setup helper: http://{args.host}:{args.port}")
    print("Press Ctrl-C to stop.")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
