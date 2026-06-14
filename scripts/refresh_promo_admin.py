#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "promo_admin_refresh_run.json"
DISALLOWED_COMMAND_PARTS = {
    "--apply",
    "post_youtube_from_queue.py",
    "post_youtube_captions.py",
    "apply_promo_queue_plan.py",
    "update_scheduled_post_approval.py",
}


STEPS = [
    {
        "name": "capture_live_metrics",
        "command": ["python3", "scripts/capture_live_metrics.py"],
        "required": False,
        "preserve_on_failure": ["data/live_social_metrics.json"],
    },
    {
        "name": "verify_pending_store_links",
        "command": ["python3", "scripts/verify_pending_store_links.py", "--refresh-admin"],
        "required": False,
    },
    {
        "name": "capture_executor_readiness",
        "command": ["python3", "scripts/capture_executor_readiness.py"],
        "required": False,
        "preserve_on_failure": ["data/executor_readiness_snapshot.json"],
    },
    {
        "name": "capture_social_executions",
        "command": ["python3", "scripts/capture_social_executions.py"],
        "required": False,
        "preserve_on_failure": ["data/social_execution_snapshot.json"],
    },
    {
        "name": "generate_promo_queue_plan",
        "command": ["python3", "scripts/generate_promo_queue_plan.py"],
        "required": True,
    },
    {
        "name": "update_metrics_history",
        "command": ["python3", "scripts/update_metrics_history.py"],
        "required": False,
        "preserve_on_failure": ["data/metrics_history.json"],
    },
    {
        "name": "capture_github_workflow_status",
        "command": ["python3", "scripts/capture_github_workflow_status.py"],
        "required": False,
    },
]

FINALIZE_STEPS = [
    {
        "name": "update_promo_engine_status",
        "command": ["python3", "scripts/update_promo_engine_status.py"],
        "required": True,
    },
    {
        "name": "build_promo_operations_packet",
        "command": ["python3", "scripts/build_promo_operations_packet.py"],
        "required": True,
    },
    {
        "name": "build_approval_runway",
        "command": ["python3", "scripts/build_approval_runway.py"],
        "required": True,
    },
    {
        "name": "build_platform_repair_status",
        "command": ["python3", "scripts/build_platform_repair_status.py"],
        "required": True,
    },
    {
        "name": "build_manual_metric_collection",
        "command": ["python3", "scripts/build_manual_metric_collection.py"],
        "required": True,
    },
    {
        "name": "update_weekly_report",
        "command": ["python3", "scripts/update_weekly_report.py"],
        "required": True,
    },
]


def trim(value: str, limit: int = 4000) -> str:
    value = value.strip()
    return value if len(value) <= limit else value[:limit] + "\n...[truncated]"


def command_text(command: list[str]) -> str:
    return " ".join(command)


def assert_safe_steps(steps: list[dict]) -> None:
    for step in steps:
        command = command_text(step["command"])
        blocked = sorted(part for part in DISALLOWED_COMMAND_PARTS if part in command)
        if blocked:
            raise ValueError(f"Unsafe refresh step {step['name']} contains: {', '.join(blocked)}")


def run_step(step: dict, dry_run: bool) -> dict:
    command = step["command"]
    started = monotonic()
    backups = {}
    for relative in step.get("preserve_on_failure", []):
        path = ROOT / relative
        backups[relative] = path.read_bytes() if path.exists() else None
    if dry_run:
        return {
            "name": step["name"],
            "command": command_text(command),
            "required": step["required"],
            "returncode": 0,
            "ok": True,
            "duration_seconds": 0,
            "stdout_tail": "dry-run",
            "stderr_tail": "",
        }
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if not step["required"] and proc.returncode != 0:
        for relative, content in backups.items():
            path = ROOT / relative
            if content is None:
                if path.exists():
                    path.unlink()
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
    return {
        "name": step["name"],
        "command": command_text(command),
        "required": step["required"],
        "returncode": proc.returncode,
        "ok": proc.returncode == 0,
        "duration_seconds": round(monotonic() - started, 2),
        "stdout_tail": trim(proc.stdout),
        "stderr_tail": trim(proc.stderr),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the safe Lily Roo admin promo refresh pipeline.")
    parser.add_argument("--dry-run", action="store_true", help="Record the commands without running them.")
    parser.add_argument("--out", default=str(OUT.relative_to(ROOT)))
    args = parser.parse_args()

    assert_safe_steps(STEPS + FINALIZE_STEPS)
    started = datetime.now(timezone.utc)
    results = []
    for step in STEPS:
        result = run_step(step, args.dry_run)
        results.append(result)
        if step["required"] and not result["ok"]:
            break

    def build_snapshot(finalized: bool = False) -> dict:
        finished = datetime.now(timezone.utc)
        required_failed = [item for item in results if item["required"] and not item["ok"]]
        optional_failed = [item for item in results if not item["required"] and not item["ok"]]
        passed = [item for item in results if item["ok"]]
        failed = [item for item in results if not item["ok"]]
        return {
            "ok": not required_failed,
            "safe_mode": True,
            "finalized": finalized,
            "dry_run": bool(args.dry_run),
            "started_at": started.isoformat().replace("+00:00", "Z"),
            "finished_at": finished.isoformat().replace("+00:00", "Z"),
            "duration_seconds": round((finished - started).total_seconds(), 2),
            "summary": {
                "command_count": len(results),
                "passed": len(passed),
                "failed": len(failed),
                "required_failed": len(required_failed),
                "optional_failed": len(optional_failed),
                "allowed_failures": len(optional_failed),
                "optional_failures_tolerated": [item["name"] for item in optional_failed],
            },
            "commands": results,
            "steps": results,
        }

    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    snapshot = build_snapshot(finalized=False)
    out.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if snapshot["ok"]:
        for step in FINALIZE_STEPS:
            result = run_step(step, args.dry_run)
            results.append(result)
            if step["required"] and not result["ok"]:
                break

    snapshot = build_snapshot(finalized=True)
    out.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if snapshot["ok"] and not args.dry_run:
        subprocess.run(["python3", "scripts/update_promo_engine_status.py"], cwd=ROOT, check=True)

    try:
        output_path = str(out.relative_to(ROOT))
    except ValueError:
        output_path = str(out)
    print(json.dumps({
        "ok": snapshot["ok"],
        "dry_run": bool(args.dry_run),
        "command_count": snapshot["summary"]["command_count"],
        "required_failed": snapshot["summary"]["required_failed"],
        "optional_failed": snapshot["summary"]["optional_failed"],
        "output": output_path,
    }, indent=2))
    return 0 if snapshot["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
