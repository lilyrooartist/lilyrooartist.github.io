#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import secrets
import sys
from pathlib import Path
from urllib import parse, request

from social_exec_common import REPO_ROOT, SOCIAL_ENV, load_env


AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
DEFAULT_SCOPES = "user.info.basic,video.upload,video.publish"
REQUIRED_BASE = ["TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REDIRECT_URI"]
TOKEN_NAMES = ["TIKTOK_REFRESH_TOKEN", "TIKTOK_ACCESS_TOKEN"]


def redacted_presence(env: dict[str, str], names: list[str]) -> dict[str, bool]:
    return {name: bool(str(env.get(name) or "").strip()) for name in names}


def append_or_update_env(path: Path, updates: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    seen: set[str] = set()
    out: list[str] = []
    for raw in existing:
        stripped = raw.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in updates:
                out.append(f"{key}={updates[key]}")
                seen.add(key)
                continue
        out.append(raw)
    for key, value in updates.items():
        if key not in seen:
            out.append(f"{key}={value}")
    path.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")


def auth_url(env: dict[str, str], scopes: str, state: str) -> str:
    params = {
        "client_key": env["TIKTOK_CLIENT_KEY"],
        "scope": scopes,
        "response_type": "code",
        "redirect_uri": env["TIKTOK_REDIRECT_URI"],
        "state": state,
    }
    return f"{AUTH_URL}?{parse.urlencode(params)}"


def exchange_code(env: dict[str, str], code: str, timeout: int) -> dict:
    body = parse.urlencode({
        "client_key": env["TIKTOK_CLIENT_KEY"],
        "client_secret": env["TIKTOK_CLIENT_SECRET"],
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": env["TIKTOK_REDIRECT_URI"],
    }).encode("utf-8")
    req = request.Request(
        TOKEN_URL,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fail(message: str) -> int:
    print(json.dumps({"ok": False, "error": message}, indent=2))
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate TikTok OAuth handoff URLs and exchange authorization codes without printing secrets."
    )
    parser.add_argument("--print-auth-url", action="store_true", help="Print the TikTok authorization URL.")
    parser.add_argument("--exchange-code", help="Exchange a TikTok authorization code for tokens.")
    parser.add_argument("--apply", action="store_true", help="Write returned tokens to secrets/social_api.env.")
    parser.add_argument("--scopes", default=DEFAULT_SCOPES, help="Comma-separated TikTok OAuth scopes.")
    parser.add_argument("--state", help="OAuth anti-forgery state. Generated when omitted.")
    parser.add_argument("--timeout-seconds", type=int, default=30)
    args = parser.parse_args()

    env = load_env(SOCIAL_ENV)
    missing_base = [name for name in REQUIRED_BASE if not str(env.get(name) or "").strip()]
    state = args.state or secrets.token_urlsafe(24)
    payload = {
        "ok": True,
        "safe_mode": True,
        "source": {
            "local_secret_source": str(SOCIAL_ENV.relative_to(REPO_ROOT.parent)),
            "repo": str(REPO_ROOT),
        },
        "requirements": {
            "required_before_auth_url": ["TIKTOK_CLIENT_KEY", "TIKTOK_REDIRECT_URI"],
            "required_before_exchange": REQUIRED_BASE,
            "requested_scopes": args.scopes,
        },
        "presence": redacted_presence(env, REQUIRED_BASE + TOKEN_NAMES),
        "missing_base": missing_base,
        "redaction": "Secret values and token values are never printed.",
    }

    if args.print_auth_url:
        missing_for_url = [name for name in ["TIKTOK_CLIENT_KEY", "TIKTOK_REDIRECT_URI"] if not str(env.get(name) or "").strip()]
        if missing_for_url:
            return fail(f"Missing local values for auth URL: {', '.join(missing_for_url)}")
        payload["auth_url"] = auth_url(env, args.scopes, state)
        payload["state"] = state

    if args.exchange_code:
        if missing_base:
            return fail(f"Missing local values for token exchange: {', '.join(missing_base)}")
        if not args.apply:
            payload["exchange_ready"] = True
            payload["apply_required"] = "Re-run with --exchange-code CODE --apply to call TikTok and store returned tokens locally."
        else:
            try:
                data = exchange_code(env, args.exchange_code, args.timeout_seconds)
            except Exception as exc:
                return fail(f"TikTok token exchange failed: {exc}")
            refresh_token = str(data.get("refresh_token") or "").strip()
            access_token = str(data.get("access_token") or "").strip()
            if not refresh_token:
                safe_data = {key: value for key, value in data.items() if key not in {"access_token", "refresh_token"}}
                return fail(f"TikTok response did not include refresh_token: {safe_data}")
            updates = {"TIKTOK_REFRESH_TOKEN": refresh_token}
            if access_token:
                updates["TIKTOK_ACCESS_TOKEN"] = access_token
            append_or_update_env(SOCIAL_ENV, updates)
            payload["exchange_applied"] = True
            payload["written_names"] = sorted(updates)
            payload["tiktok_response"] = {
                "open_id_present": bool(data.get("open_id")),
                "scope": data.get("scope", ""),
                "expires_in": data.get("expires_in", ""),
                "refresh_expires_in": data.get("refresh_expires_in", ""),
                "token_type": data.get("token_type", ""),
            }

    if not args.print_auth_url and not args.exchange_code:
        payload["next_actions"] = [
            "Add TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, and TIKTOK_REDIRECT_URI to secrets/social_api.env.",
            "Run python3 scripts/tiktok_oauth_handoff.py --print-auth-url.",
            "Authorize video.upload and video.publish with the Lily Roo TikTok account, then exchange the returned code with --exchange-code CODE --apply.",
        ]

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
