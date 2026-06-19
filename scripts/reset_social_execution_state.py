#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WRANGLER_CONFIG = ROOT / "workers" / "social-executor" / "wrangler.jsonc"
BINDING = "SOCIAL_EXECUTOR_STATE"
PREFIX = "post:"


def run_wrangler(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["npx", "wrangler", *args, "--config", str(WRANGLER_CONFIG)],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        check=False,
    )


def kv_key(post_id: str) -> str:
    return f"{PREFIX}{post_id.strip()}"


def read_state(post_id: str) -> dict:
    result = run_wrangler(["kv", "key", "get", kv_key(post_id), "--binding", BINDING, "--remote", "--text"])
    raw = (result.stdout or "").strip()
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "wrangler kv key get failed").strip()
        raise RuntimeError(detail)
    if not raw or raw == "Value not found":
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"KV state for {post_id} is not JSON: {raw[:120]}") from exc


def delete_state(post_id: str) -> None:
    result = run_wrangler(["kv", "key", "delete", kv_key(post_id), "--binding", BINDING, "--remote"])
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "wrangler kv key delete failed").strip()
        raise RuntimeError(detail)


def is_retry_capped(state: dict) -> bool:
    return (
        state.get("status") == "failed"
        and state.get("reason") == "max_attempts_exceeded"
        and int(state.get("attempts") or 0) >= 3
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preview or clear a social executor KV state record after platform repair."
    )
    parser.add_argument("post_id", help="Scheduled post id, for example FP-AUTO-263.")
    parser.add_argument("--apply", action="store_true", help="Delete the KV execution state. Default is dry-run.")
    parser.add_argument("--force", action="store_true", help="Allow clearing a state that is not max_attempts_exceeded.")
    args = parser.parse_args()

    post_id = args.post_id.strip()
    if not post_id:
        raise SystemExit("post_id is required")

    state = read_state(post_id)
    if not state:
        print(json.dumps({
            "ok": True,
            "post_id": post_id,
            "key": kv_key(post_id),
            "exists": False,
            "apply": args.apply,
            "action": "none",
        }, indent=2))
        return 0

    retry_capped = is_retry_capped(state)
    if not retry_capped and not args.force:
        print(json.dumps({
            "ok": False,
            "post_id": post_id,
            "key": kv_key(post_id),
            "exists": True,
            "apply": args.apply,
            "action": "refused",
            "reason": "state_is_not_max_attempts_exceeded",
            "state": state,
        }, indent=2, ensure_ascii=False))
        return 1

    action = "would_delete"
    if args.apply:
        delete_state(post_id)
        action = "deleted"

    print(json.dumps({
        "ok": True,
        "post_id": post_id,
        "key": kv_key(post_id),
        "exists": True,
        "apply": args.apply,
        "action": action,
        "retry_capped": retry_capped,
        "state": state,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
