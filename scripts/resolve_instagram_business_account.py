#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from post_meta_from_queue import DEFAULT_GRAPH_VERSION
from social_exec_common import REPO_ROOT, SOCIAL_ENV, load_env
from tiktok_oauth_handoff import append_or_update_env


OUT = REPO_ROOT / "data" / "instagram_business_account_resolution.json"


def graph_version(env: dict[str, str]) -> str:
    return str(env.get("META_GRAPH_VERSION") or DEFAULT_GRAPH_VERSION).strip() or DEFAULT_GRAPH_VERSION


def graph_get(url: str, params: dict[str, str], timeout: int) -> tuple[int, dict, str]:
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(full_url, headers={"Accept": "application/json"}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status, json.loads(response.read().decode("utf-8")), ""
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {}
        return exc.code, payload, f"HTTP {exc.code}: {exc.reason}"
    except (urllib.error.URLError, TimeoutError) as exc:
        return 0, {}, str(exc)


def safe_error(payload: dict, fallback: str) -> str:
    error = payload.get("error") if isinstance(payload, dict) else {}
    if isinstance(error, dict):
        message = str(error.get("message") or "").strip()
        code = str(error.get("code") or "").strip()
        return " ".join(part for part in [f"code={code}" if code else "", message] if part)[:500]
    return fallback[:500]


def build_packet(timeout: int, apply: bool) -> dict:
    env = load_env(SOCIAL_ENV)
    token = str(env.get("META_LONG_LIVED_TOKEN") or "").strip()
    page_id = str(env.get("FB_PAGE_ID") or "").strip()
    existing_ig = str(env.get("IG_BUSINESS_ACCOUNT_ID") or "").strip()
    missing = [name for name, value in [("META_LONG_LIVED_TOKEN", token), ("FB_PAGE_ID", page_id)] if not value]
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    packet = {
        "generated_at": generated_at,
        "safe_mode": True,
        "apply": apply,
        "redaction": "Meta token values are never printed. The resolved Instagram account id is safe to store as a local secret.",
        "source": {
            "local_secret_source": str(SOCIAL_ENV.relative_to(REPO_ROOT.parent)),
            "graph_version": graph_version(env),
            "output": str(OUT.relative_to(REPO_ROOT)),
        },
        "summary": {
            "status": "missing_local_input" if missing else "ready_to_resolve",
            "missing_local_input": missing,
            "existing_ig_business_account_id_present": bool(existing_ig),
            "resolved": False,
            "applied": False,
            "next_action": (
                f"Add {', '.join(missing)} to {SOCIAL_ENV}."
                if missing
                else "Run this resolver and inspect the resolved account, then re-run with --apply to write IG_BUSINESS_ACCOUNT_ID locally."
            ),
        },
    }
    if missing:
        return packet

    url = f"https://graph.facebook.com/{graph_version(env)}/{page_id}"
    status, payload, error = graph_get(
        url,
        {
            "fields": "name,instagram_business_account{id,username,name}",
            "access_token": token,
        },
        timeout,
    )
    account = payload.get("instagram_business_account") if isinstance(payload, dict) else {}
    account = account if isinstance(account, dict) else {}
    ig_id = str(account.get("id") or "").strip()
    packet["graph"] = {
        "http_status": status,
        "page_name": str(payload.get("name") or "") if isinstance(payload, dict) else "",
        "error": "" if status == 200 else safe_error(payload, error),
    }
    packet["resolved_account"] = {
        "id": ig_id,
        "username": str(account.get("username") or "").strip(),
        "name": str(account.get("name") or "").strip(),
    }
    if status == 200 and ig_id:
        if apply:
            append_or_update_env(SOCIAL_ENV, {"IG_BUSINESS_ACCOUNT_ID": ig_id})
        packet["summary"].update({
            "status": "applied" if apply else "resolved",
            "resolved": True,
            "applied": bool(apply),
            "resolved_id_present": True,
            "next_action": (
                "Push IG_BUSINESS_ACCOUNT_ID to the Worker and recapture readiness."
                if apply
                else "Re-run with --apply to write IG_BUSINESS_ACCOUNT_ID locally."
            ),
        })
    elif status == 200:
        packet["summary"].update({
            "status": "no_connected_instagram_account",
            "next_action": "Connect the Instagram Business/Creator account to the Lily Roo Facebook Page, then rerun this resolver.",
        })
    else:
        packet["summary"].update({
            "status": "graph_error",
            "next_action": "Check that META_LONG_LIVED_TOKEN can read the Page and includes the required Meta permissions, then rerun.",
        })
    return packet


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve IG_BUSINESS_ACCOUNT_ID from FB_PAGE_ID without printing Meta tokens.")
    parser.add_argument("--apply", action="store_true", help="Write resolved IG_BUSINESS_ACCOUNT_ID to secrets/social_api.env.")
    parser.add_argument("--out", default=str(OUT.relative_to(REPO_ROOT)))
    parser.add_argument("--timeout-seconds", type=int, default=20)
    args = parser.parse_args()
    out = Path(args.out)
    if not out.is_absolute():
        out = REPO_ROOT / out
    packet = build_packet(args.timeout_seconds, args.apply)
    out.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(out.relative_to(REPO_ROOT)),
        "status": packet["summary"]["status"],
        "resolved": packet["summary"].get("resolved", False),
        "applied": packet["summary"].get("applied", False),
        "missing_local_input": packet["summary"].get("missing_local_input", []),
    }, indent=2))
    return 0 if packet["summary"]["status"] in {"resolved", "applied"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
