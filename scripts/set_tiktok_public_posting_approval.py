#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from social_exec_common import REPO_ROOT, SOCIAL_ENV, load_env


WRANGLER_CONFIG = REPO_ROOT / "workers" / "social-executor" / "wrangler.jsonc"
VAR_NAME = "TIKTOK_PUBLIC_POSTING_APPROVED"


def read_config() -> dict:
    if not WRANGLER_CONFIG.exists():
        raise RuntimeError(f"Missing Wrangler config: {WRANGLER_CONFIG}")
    return json.loads(WRANGLER_CONFIG.read_text(encoding="utf-8"))


def write_config(config: dict) -> None:
    WRANGLER_CONFIG.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def local_approval_confirmed() -> bool:
    return str(load_env(SOCIAL_ENV).get(VAR_NAME, "")).strip().lower() == "true"


def deploy_worker() -> None:
    result = subprocess.run(
        ["npx", "wrangler", "deploy", "--config", str(WRANGLER_CONFIG)],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "wrangler deploy failed").strip())
    print(result.stdout.strip() or "deployed social executor")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guarded helper for setting the TikTok public-posting approval Worker var."
    )
    parser.add_argument(
        "--approved",
        action="store_true",
        help="Assert that TikTok public posting approval has been confirmed externally.",
    )
    parser.add_argument("--apply", action="store_true", help="Write the Wrangler var change locally.")
    parser.add_argument("--deploy", action="store_true", help="Deploy the Worker after writing the local var.")
    args = parser.parse_args()

    config = read_config()
    vars_block = config.setdefault("vars", {})
    current = str(vars_block.get(VAR_NAME, "false")).lower()
    local_confirmed = local_approval_confirmed()
    target = "true" if args.approved else "false"

    if args.approved and not local_confirmed:
        raise RuntimeError(
            f"{SOCIAL_ENV.relative_to(REPO_ROOT.parent)} must contain {VAR_NAME}=true before this helper can enable public posting."
        )
    if args.deploy and not args.apply:
        raise RuntimeError("--deploy requires --apply so the local Wrangler config matches the deployment.")

    summary = {
        "wrangler_config": str(WRANGLER_CONFIG.relative_to(REPO_ROOT)),
        "local_approval_confirmed": local_confirmed,
        "current_worker_var": current,
        "target_worker_var": target,
        "would_change": current != target,
        "apply": args.apply,
        "deploy": args.deploy,
    }
    print(json.dumps(summary, indent=2))

    if not args.apply:
        return 0

    vars_block[VAR_NAME] = target
    write_config(config)
    print(f"updated {WRANGLER_CONFIG.relative_to(REPO_ROOT)} {VAR_NAME}={target}")

    if args.deploy:
        deploy_worker()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
