#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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


def build_packet(repo: str, timeout: int) -> dict:
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    try:
        returncode, stdout, stderr = run_gh(repo, timeout)
    except (subprocess.SubprocessError, FileNotFoundError) as exc:
        returncode, stdout, stderr = 1, "", str(exc)
    names = parse_secret_names(stdout) if returncode == 0 else []
    presence = {name: name in names for name in AUTH_SECRET_OPTIONS}
    present_auth = [name for name, is_present in presence.items() if is_present]
    missing_options = [name for name, is_present in presence.items() if not is_present]
    ok = returncode == 0
    ready = ok and bool(present_auth)
    return {
        "generated_at": generated_at,
        "safe_mode": True,
        "redaction": "Only GitHub Actions secret names are checked; secret values are never available or written.",
        "source": {
            "repo": repo,
            "command": f"gh secret list --repo {repo}",
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
            "next_action": (
                "GitHub Actions has a scheduler auth secret."
                if ready
                else f"Add one GitHub Actions repo secret: {' or '.join(missing_options)}."
                if ok
                else "Run gh auth status, then rerun this secret presence capture locally."
            ),
        },
        "auth_secret_options": AUTH_SECRET_OPTIONS,
        "required_secrets": AUTH_SECRET_OPTIONS,
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
        "output": str(out.relative_to(ROOT)),
        "status": packet["summary"]["status"],
        "present_required_count": packet["summary"]["present_required_count"],
        "missing_required_count": packet["summary"]["missing_required_count"],
    }, indent=2))
    return 0 if packet.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
