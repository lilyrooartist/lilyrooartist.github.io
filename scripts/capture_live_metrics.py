#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SECRETS_DIR = REPO_ROOT.parent / "secrets"
SOCIAL_ENV = SECRETS_DIR / "social_api.env"
WRANGLER_CONFIG = REPO_ROOT / "workers" / "social-executor" / "wrangler.jsonc"
OUT = REPO_ROOT / "data" / "live_social_metrics.json"
DEFAULT_URL = "https://www.lilyroo.com/api/social/metrics"
SPOTIFY_ARTIST_URL = "https://open.spotify.com/artist/4yzWmf64UKLwbAVwnDi49a"
TIKTOK_PROFILE_URL = "https://www.tiktok.com/@lilyroo930"


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def admin_password() -> str:
    explicit = os.environ.get("LILYROO_ADMIN_PASSWORD", "").strip()
    if explicit:
        return explicit
    text = WRANGLER_CONFIG.read_text(encoding="utf-8")
    match = re.search(r'"ADMIN_PASSWORD"\s*:\s*"([^"]+)"', text)
    return match.group(1) if match else ""


def bearer_token() -> str:
    explicit = os.environ.get("LILYROO_EXECUTOR_BEARER_TOKEN", "").strip()
    if explicit:
        return explicit
    return load_env(SOCIAL_ENV).get("EXECUTOR_BEARER_TOKEN", "").strip()


def fetch_metrics(url: str, password: str, bearer: str) -> dict:
    headers = {
        "Accept": "application/json",
        "User-Agent": "LilyRooMetricsCapture/1.0",
    }
    if password:
        headers["X-Lilyroo-Admin-Password"] = password
    elif bearer:
        headers["Authorization"] = f"Bearer {bearer}"
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            payload = json.loads(response.read().decode("utf-8"))
            payload["capture_status"] = response.status
            return payload
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            body = json.loads(raw)
        except Exception:
            body = {"raw": raw[:300]}
        return {
            "ok": False,
            "capture_status": exc.code,
            "error": body.get("error") or body,
        }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def read_existing_snapshot() -> dict:
    if not OUT.exists():
        return {"ok": True, "platforms": {}}
    try:
        payload = json.loads(OUT.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"ok": True, "platforms": {}}
    if not isinstance(payload, dict):
        return {"ok": True, "platforms": {}}
    payload.setdefault("platforms", {})
    return payload


def fetch_text(url: str) -> tuple[int, str, str]:
    request = urllib.request.Request(url, headers={
        "Accept": "text/html,application/xhtml+xml",
        "User-Agent": "LilyRooPublicMetricCapture/1.0",
    })
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            return int(response.status), response.read().decode("utf-8", errors="replace"), ""
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read().decode("utf-8", errors="replace")[:300], str(exc)
    except (urllib.error.URLError, TimeoutError) as exc:
        return 0, "", str(exc)


def parse_int(value: str):
    try:
        return int(str(value or "").replace(",", "").strip())
    except ValueError:
        return None


def spotify_public_metrics() -> dict:
    status, html, error = fetch_text(SPOTIFY_ARTIST_URL)
    metrics = {}
    description = ""
    monthly = None
    followers = None
    if html:
        desc_match = re.search(r'<meta\s+property="og:description"\s+content="([^"]+)"', html)
        description = unescape(desc_match.group(1)) if desc_match else ""
        monthly_match = re.search(r"Artist\s*·\s*([0-9,]+)\s+monthly listeners?", description, re.I)
        monthly = parse_int(monthly_match.group(1)) if monthly_match else None
        follower_match = re.search(
            r"<p[^>]*>\s*([0-9,]+)\s*</p>\s*<p[^>]*>\s*Followers\s*</p>",
            html,
            re.I,
        )
        followers = parse_int(follower_match.group(1)) if follower_match else None
    if monthly is not None:
        metrics["monthly_listeners"] = monthly
    if followers is not None:
        metrics["artist_followers"] = followers
    return {
        "ok": bool(metrics),
        "source": "spotify-public-artist-page",
        "metrics": metrics,
        "profile_url": SPOTIFY_ARTIST_URL,
        "http_status": status,
        "description": description,
        "public_capture_status": "ok" if metrics else (error or "No public Spotify listener/follower values found."),
    }


def tiktok_public_metrics() -> dict:
    status, html, error = fetch_text(TIKTOK_PROFILE_URL)
    follower_count = None
    display_name = ""
    if html:
        script_match = re.search(
            r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>',
            html,
            re.S,
        )
        if script_match:
            try:
                payload = json.loads(unescape(script_match.group(1)))
            except json.JSONDecodeError:
                payload = {}
            user_detail = (((payload.get("__DEFAULT_SCOPE__") or {}).get("webapp.user-detail") or {}).get("userInfo") or {})
            stats = user_detail.get("statsV2") or user_detail.get("stats") or {}
            user = user_detail.get("user") or {}
            follower_count = parse_int(stats.get("followerCount"))
            display_name = str(user.get("nickname") or user.get("uniqueId") or "").strip()
        if follower_count is None:
            fallback = re.search(r'"followerCount"\s*:\s*"?([0-9,]+)"?', html)
            follower_count = parse_int(fallback.group(1)) if fallback else None
    metrics = {}
    if follower_count is not None:
        metrics["followers"] = follower_count
    return {
        "ok": bool(metrics),
        "source": "tiktok-public-profile-page",
        "metrics": metrics,
        "profile_url": TIKTOK_PROFILE_URL,
        "http_status": status,
        "display_name": display_name,
        "public_capture_status": "ok" if metrics else (error or "No public TikTok follower value found."),
    }


def merge_public_metrics(payload: dict) -> dict:
    platforms = payload.setdefault("platforms", {})
    public_updates = {
        "spotify": spotify_public_metrics(),
        "tiktok": tiktok_public_metrics(),
    }
    for platform, update in public_updates.items():
        if not update.get("ok"):
            current = platforms.setdefault(platform, {})
            current.setdefault("public_capture_status", update.get("public_capture_status", "unavailable"))
            current.setdefault("public_profile_url", update.get("profile_url", ""))
            continue
        current = platforms.setdefault(platform, {})
        metrics = current.setdefault("metrics", {})
        metrics.update(update.get("metrics") or {})
        current.update({key: value for key, value in update.items() if key != "metrics"})
        current["ok"] = True
    payload["ok"] = any(isinstance(item, dict) and item.get("ok") for item in platforms.values())
    payload["updated_at"] = utc_now()
    payload["public_profile_capture"] = {
        "status": "ok" if any(item.get("ok") for item in public_updates.values()) else "unavailable",
        "platforms": public_updates,
    }
    return payload


def main() -> int:
    url = os.environ.get("LILYROO_METRICS_URL", DEFAULT_URL).strip() or DEFAULT_URL
    payload = fetch_metrics(url, admin_password(), bearer_token())
    if not payload.get("ok"):
        previous = read_existing_snapshot()
        previous["authenticated_capture_error"] = payload.get("error") or payload.get("capture_status") or "unknown"
        previous["authenticated_capture_status"] = payload.get("capture_status")
        payload = previous
    payload = merge_public_metrics(payload)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    platforms = sorted((payload.get("platforms") or {}).keys())
    print(json.dumps({
        "ok": bool(payload.get("ok")),
        "capture_status": payload.get("capture_status"),
        "updated_at": payload.get("updated_at"),
        "platforms": platforms,
        "output": str(OUT.relative_to(REPO_ROOT)),
    }, indent=2))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
