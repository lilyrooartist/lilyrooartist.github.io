#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "github_actions_secret_presence.json"
DEFAULT_REPO = "lilyrooartist/lilyrooartist.github.io"
AUTH_SECRET_OPTIONS = [
    "LILYROO_EXECUTOR_BEARER_TOKEN",
    "LILYROO_ADMIN_PASSWORD",
]
OPTIONAL_SECRET_GROUPS = {
    "x_metric_capture": {
        "label": "X metric capture",
        "required_all": ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"],
        "unblocks": "Automated X post result capture for experiment and brand-growth learning.",
    },
    "facebook_metric_capture": {
        "label": "Facebook metric capture",
        "required_all": ["META_LONG_LIVED_TOKEN", "FB_PAGE_ID"],
        "unblocks": "Automated Facebook post engagement capture for experiment and brand-growth learning.",
    },
}


def run_gh(repo: str, timeout: int) -> tuple[int, str, str]:
    result = subprocess.run(
        ["gh", "secret", "list", "--repo", repo],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    return result.returncode, result.stdout, result.stderr


def parse_secret_names(stdout: str) -> list[str]:
    names = []
    for raw in stdout.splitlines():
        line = raw.strip()
        if not line:
            continue
        names.append(line.split()[0])
    return sorted(set(names))


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def build_packet(repo: str, timeout: int) -> dict:
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    try:
        returncode, stdout, stderr = run_gh(repo, timeout)
    except (subprocess.SubprocessError, FileNotFoundError) as exc:
        returncode, stdout, stderr = 1, "", str(exc)
    optional_secret_names = sorted({name for group in OPTIONAL_SECRET_GROUPS.values() for name in group["required_all"]})
    env_present = sorted(name for name in [*AUTH_SECRET_OPTIONS, *optional_secret_names] if os.environ.get(name))
    names = sorted(set((parse_secret_names(stdout) if returncode == 0 else []) + env_present))
    all_secret_names = [*AUTH_SECRET_OPTIONS, *optional_secret_names]
    presence = {name: name in names for name in all_secret_names}
    auth_presence = {name: presence.get(name, False) for name in AUTH_SECRET_OPTIONS}
    optional_groups = {}
    for group_id, group in OPTIONAL_SECRET_GROUPS.items():
        required = group["required_all"]
        group_presence = {name: presence.get(name, False) for name in required}
        missing = [name for name, is_present in group_presence.items() if not is_present]
        optional_groups[group_id] = {
            "label": group["label"],
            "status": "ready" if not missing else "missing",
            "required_all": required,
            "present_count": len(required) - len(missing),
            "missing_count": len(missing),
            "missing": missing,
            "presence": group_presence,
            "unblocks": group["unblocks"],
        }
    present_auth = [name for name, is_present in auth_presence.items() if is_present]
    missing_options = [name for name, is_present in auth_presence.items() if not is_present]
    metric_ready = [group for group in optional_groups.values() if group["status"] == "ready"]
    metric_missing = sorted({name for group in optional_groups.values() for name in group["missing"]})
    ok = returncode == 0 or bool(env_present)
    ready = ok and bool(present_auth)
    return {
        "generated_at": generated_at,
        "safe_mode": True,
        "redaction": "Only GitHub Actions secret names are checked; secret values are never available or written.",
        "source": {
            "repo": repo,
            "command": f"gh secret list --repo {repo}",
            "env_presence_fallback": bool(env_present) and returncode != 0,
        },
        "ok": ok,
        "returncode": returncode,
        "error": "" if ok else (stderr or stdout).strip()[:500],
        "summary": {
            "status": "ready" if ready else "missing_auth_secret" if ok else "unknown",
            "auth_option_count": len(AUTH_SECRET_OPTIONS),
            "auth_present_count": len(present_auth),
            "present_required_count": sum(1 for is_present in presence.values() if is_present),
            "missing_required_count": 0 if present_auth else len(missing_options),
            "checked_secret_count": len(names),
            "present_auth_secrets": present_auth,
            "missing_auth_options": missing_options,
            "missing_required_secrets": [] if present_auth else missing_options,
            "optional_group_count": len(optional_groups),
            "optional_ready_group_count": len(metric_ready),
            "optional_missing_secret_count": len(metric_missing),
            "optional_missing_secret_names": metric_missing,
            "next_action": (
                "GitHub Actions has scheduler auth and optional metric-capture secrets."
                if ready and not metric_missing
                else f"Scheduler auth is ready; add optional metric-capture secrets: {', '.join(metric_missing)}."
                if ready
                else f"Add one GitHub Actions repo secret: {' or '.join(missing_options)}."
                if ok
                else "Run gh auth status, then rerun this secret presence capture locally."
            ),
        },
        "auth_secret_options": AUTH_SECRET_OPTIONS,
        "required_secrets": AUTH_SECRET_OPTIONS,
        "optional_secret_groups": optional_groups,
        "presence": presence,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture GitHub Actions secret-name presence without reading values.")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--out", default=str(OUT.relative_to(ROOT)))
    parser.add_argument("--timeout-seconds", type=int, default=20)
    args = parser.parse_args()

    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    packet = build_packet(args.repo, args.timeout_seconds)
    out.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": display_path(out),
        "status": packet["summary"]["status"],
        "present_required_count": packet["summary"]["present_required_count"],
        "missing_required_count": packet["summary"]["missing_required_count"],
        "optional_missing_secret_count": packet["summary"]["optional_missing_secret_count"],
    }, indent=2))
    return 0 if packet.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
