#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STORE_RUN = ROOT / "output/launch-audit/analog-myth-store-verification-run.json"
STORE_SNAPSHOT_ROOT = ROOT / "output/launch-audit/store-verification"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def summarize_payload(payload: dict) -> dict:
    if not payload:
        return {}
    keys = (
        "ok",
        "checked",
        "failed",
        "live_checked",
        "require_store_links",
        "launch_ready",
        "applied",
        "mode",
        "changed_files",
        "error",
        "not_live_or_failed",
        "timed_out",
        "output",
    )
    summary = {key: payload[key] for key in keys if key in payload}
    if "summary" in payload and isinstance(payload["summary"], dict):
        summary["summary"] = payload["summary"]
    return summary


def run_step(name: str, command: list[str]) -> dict:
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    step = {
        "name": name,
        "command": " ".join(command),
        "returncode": proc.returncode,
        "stderr": proc.stderr.strip(),
    }
    stdout = proc.stdout.strip()
    if stdout:
        try:
            step["stdout_summary"] = summarize_payload(json.loads(stdout))
        except json.JSONDecodeError:
            step["stdout"] = stdout[:2000]
    return step


def parse_json_stdout(step: dict) -> dict:
    return step.get("stdout_summary") or {}


def store_summary() -> dict:
    if not STORE_RUN.exists():
        return {
            "checked": 0,
            "verified": 0,
            "not_live_or_failed": 0,
            "timed_out": 0,
            "all_public_links_verified": False,
        }
    payload = json.loads(STORE_RUN.read_text(encoding="utf-8"))
    summary = payload.get("summary", {})
    return {
        "checked": summary.get("checked", 0),
        "verified": summary.get("ok", 0),
        "not_live_or_failed": summary.get("not_live_or_failed", 0),
        "timed_out": summary.get("timed_out", 0),
        "all_public_links_verified": bool(payload.get("all_public_links_verified")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Analog Myth July 1 launch sequence.")
    parser.add_argument("--apply", action="store_true", help="Apply verified launch links after a successful dry run.")
    parser.add_argument("--allow-prelaunch", action="store_true", help="Exit 0 when the package is healthy but store links are not public yet.")
    parser.add_argument("--live", action="store_true", help="Check live lilyroo.com launch URLs in readiness steps.")
    parser.add_argument("--step-timeout-seconds", type=int, default=25, help="Timeout for each public store lookup subprocess.")
    args = parser.parse_args()

    readiness_command = ["python3", "scripts/check_analog_myth_launch_readiness.py"]
    if args.live:
        readiness_command.append("--live")
    steps = [run_step("preflight_readiness", readiness_command)]
    if steps[-1]["returncode"] != 0:
        output = {
            "ok": False,
            "launch_ready": False,
            "applied": False,
            "reason": "preflight_readiness_failed",
            "steps": steps,
        }
        print(json.dumps(output, indent=2))
        return 1

    verify_command = [
        "python3",
        "scripts/verify_pending_store_links.py",
        "--release",
        "Analog Myth",
        "--step-timeout-seconds",
        str(args.step_timeout_seconds),
        "--out",
        display_path(STORE_RUN),
        "--snapshot-root",
        display_path(STORE_SNAPSHOT_ROOT),
    ]
    steps.append(run_step("verify_store_links", verify_command))
    if steps[-1]["returncode"] != 0:
        output = {
            "ok": False,
            "launch_ready": False,
            "applied": False,
            "reason": "store_verification_command_failed",
            "steps": steps,
        }
        print(json.dumps(output, indent=2))
        return 1

    steps.append(run_step("dry_run_apply_links", ["python3", "scripts/apply_analog_myth_launch_links.py"]))
    dry_run_payload = parse_json_stdout(steps[-1])
    launch_ready = steps[-1]["returncode"] == 0
    applied = False

    if args.apply and launch_ready:
        steps.append(run_step("apply_links", ["python3", "scripts/apply_analog_myth_launch_links.py", "--apply"]))
        applied = steps[-1]["returncode"] == 0
        launch_ready = applied
        final_readiness_command = ["python3", "scripts/check_analog_myth_launch_readiness.py", "--require-store-links"]
        steps.append(run_step("final_readiness", final_readiness_command))
        launch_ready = launch_ready and steps[-1]["returncode"] == 0

    summary = store_summary()
    reason = ""
    if not launch_ready:
        reason = dry_run_payload.get("error") or "launch_links_not_ready"
    output = {
        "ok": launch_ready or args.allow_prelaunch,
        "launch_ready": launch_ready,
        "applied": applied,
        "allow_prelaunch": args.allow_prelaunch,
        "reason": reason,
        "store_summary": summary,
        "steps": steps,
    }
    if args.apply and args.live:
        output["post_deploy_live_check"] = "python3 scripts/check_analog_myth_launch_readiness.py --require-store-links --live"
        output["local_launch_ready"] = launch_ready
        output["public_launch_ready"] = False
        output["public_launch_ready_reason"] = "Run post_deploy_live_check after committing, pushing, and waiting for GitHub Pages deploy."
    else:
        output["local_launch_ready"] = launch_ready
        output["public_launch_ready"] = launch_ready
    print(json.dumps(output, indent=2))
    if launch_ready or args.allow_prelaunch:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
