#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from social_exec_common import REPO_ROOT, SECRETS_DIR, SOCIAL_ENV, YOUTUBE_ENV, load_env

WRANGLER_CONFIG = REPO_ROOT / "workers" / "social-executor" / "wrangler.jsonc"
SOCIAL_MEDIA_MAP = SECRETS_DIR / "social-media-map.json"
X_MEDIA_MAP = SECRETS_DIR / "x-media-map.json"

ENV_SECRET_FILES = {
    "EXECUTOR_BEARER_TOKEN": SOCIAL_ENV,
    "META_LONG_LIVED_TOKEN": SOCIAL_ENV,
    "FB_PAGE_ID": SOCIAL_ENV,
    "IG_BUSINESS_ACCOUNT_ID": SOCIAL_ENV,
    "TIKTOK_ACCESS_TOKEN": SOCIAL_ENV,
    "GOOGLE_CLIENT_ID": YOUTUBE_ENV,
    "GOOGLE_CLIENT_SECRET": YOUTUBE_ENV,
    "YOUTUBE_REFRESH_TOKEN": YOUTUBE_ENV,
    "X_USER_ACCESS_TOKEN": SOCIAL_ENV,
    "X_API_KEY": SOCIAL_ENV,
    "X_API_SECRET": SOCIAL_ENV,
    "X_ACCESS_TOKEN": SOCIAL_ENV,
    "X_ACCESS_TOKEN_SECRET": SOCIAL_ENV,
}

JSON_SECRET_FILES = {
    "SOCIAL_MEDIA_MAP_JSON": SOCIAL_MEDIA_MAP,
    "X_MEDIA_MAP_JSON": X_MEDIA_MAP,
}


def load_secret_value(name: str) -> str:
    env_path = ENV_SECRET_FILES.get(name)
    if env_path:
        value = load_env(env_path).get(name, "").strip()
        if not value:
            raise RuntimeError(f"{name} is missing from {env_path}")
        return value

    json_path = JSON_SECRET_FILES.get(name)
    if json_path:
        if not json_path.exists():
            raise RuntimeError(f"{name} source file is missing: {json_path}")
        data = json.loads(json_path.read_text(encoding="utf-8"))
        return json.dumps(data, separators=(",", ":"), ensure_ascii=False)

    raise RuntimeError(f"Unsupported secret name: {name}")


def put_secret(name: str, value: str) -> None:
    result = subprocess.run(
        ["npx", "wrangler", "secret", "put", name, "--config", str(WRANGLER_CONFIG)],
        cwd=str(REPO_ROOT),
        input=value,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or f"failed to put {name}").strip())
    print(f"updated {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Push selected local social secrets into the Cloudflare Worker.")
    parser.add_argument(
        "names",
        nargs="+",
        help="Secret names to push, for example X_USER_ACCESS_TOKEN or EXECUTOR_BEARER_TOKEN.",
    )
    args = parser.parse_args()

    for name in args.names:
        put_secret(name, load_secret_value(name))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
