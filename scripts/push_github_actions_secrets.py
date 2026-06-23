#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from social_exec_common import REPO_ROOT, SOCIAL_ENV, load_env


DEFAULT_REPO = "lilyrooartist/lilyrooartist.github.io"
AUTH_SECRET_SPECS = [
    {
        "github_name": "LILYROO_EXECUTOR_BEARER_TOKEN",
        "local_names": ["LILYROO_EXECUTOR_BEARER_TOKEN", "EXECUTOR_BEARER_TOKEN"],
        "purpose": "Bearer auth for scheduler/executor captures.",
    },
    {
        "github_name": "LILYROO_ADMIN_PASSWORD",
        "local_names": ["LILYROO_ADMIN_PASSWORD", "ADMIN_PASSWORD"],
        "purpose": "Admin-password fallback for scheduler/executor captures.",
    },
]


def local_value(env: dict[str, str], names: list[str]) -> tuple[str, str]:
    for name in names:
        value = str(env.get(name) or "").strip()
        if value:
            return name, value
    return "", ""


def run_gh_secret_set(repo: str, name: str, value: str, timeout: int) -> tuple[int, str, str]:
    result = subprocess.run(
        ["gh", "secret", "set", name, "--repo", repo, "--body", value],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    return result.returncode, result.stdout, result.stderr


def build_plan(env: dict[str, str], names: list[str] | None = None) -> list[dict]:
    selected = set(names or [spec["github_name"] for spec in AUTH_SECRET_SPECS])
    rows = []
    for spec in AUTH_SECRET_SPECS:
        if spec["github_name"] not in selected:
            continue
        source_name, value = local_value(env, spec["local_names"])
        rows.append({
            "github_name": spec["github_name"],
            "local_source_name": source_name,
            "local_source_names": spec["local_names"],
            "purpose": spec["purpose"],
            "local_value_present": bool(value),
            "local_value_length": len(value) if value else 0,
            "_value": value,
        })
    return rows


def public_row(row: dict) -> dict:
    return {
        "github_name": row["github_name"],
        "local_source_name": row["local_source_name"],
        "local_source_names": row["local_source_names"],
        "purpose": row["purpose"],
        "local_value_present": row["local_value_present"],
        "local_value_length": row["local_value_length"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Push local scheduler auth values to GitHub Actions secrets.")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--apply", action="store_true", help="Actually write GitHub Actions secrets. Default is dry-run.")
    parser.add_argument("--name", action="append", choices=[spec["github_name"] for spec in AUTH_SECRET_SPECS], help="Limit to one GitHub secret name. Can be repeated.")
    parser.add_argument("--timeout-seconds", type=int, default=20)
    args = parser.parse_args()

    env = load_env(SOCIAL_ENV)
    plan = build_plan(env, args.name)
    missing = [row for row in plan if not row["local_value_present"]]
    applied = []
    errors = []
    if args.apply and not missing:
        for row in plan:
            code, stdout, stderr = run_gh_secret_set(args.repo, row["github_name"], row["_value"], args.timeout_seconds)
            if code == 0:
                applied.append(row["github_name"])
            else:
                errors.append({
                    "github_name": row["github_name"],
                    "error": (stderr or stdout or "gh secret set failed").strip()[:500],
                })
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "dry_run": not args.apply,
        "repo": args.repo,
        "local_secret_source": str(SOCIAL_ENV.relative_to(REPO_ROOT.parent)),
        "redaction": "Secret values are never printed; dry-run reports presence and length only.",
        "summary": {
            "requested_count": len(plan),
            "local_ready_count": sum(1 for row in plan if row["local_value_present"]),
            "missing_local_count": len(missing),
            "applied_count": len(applied),
            "error_count": len(errors),
            "status": "applied" if args.apply and applied and not errors else "missing_local_input" if missing else "ready_to_apply" if not args.apply else "failed",
            "apply_command": "python3 scripts/push_github_actions_secrets.py --apply",
            "presence_capture_command": "python3 scripts/capture_github_actions_secret_presence.py",
        },
        "rows": [public_row(row) for row in plan],
        "missing_local": [public_row(row) for row in missing],
        "applied": applied,
        "errors": errors,
    }
    print(json.dumps(payload, indent=2))
    if errors:
        return 1
    if missing:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
