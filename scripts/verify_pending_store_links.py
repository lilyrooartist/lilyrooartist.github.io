#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from time import monotonic
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE_STATUS = ROOT / "data" / "distrokid_release_status.json"
OUT = ROOT / "data" / "store_verification_run.json"
DEFAULT_STEP_TIMEOUT_SECONDS = 5


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def trim(value: str, limit: int = 3000) -> str:
    value = (value or "").strip()
    value = sanitize_output(value)
    return value if len(value) <= limit else value[:limit] + "\n...[truncated]"


def sanitize_output(value: str) -> str:
    text = value or ""
    for src, dst in (
        (str(ROOT), "<repo>"),
        (str(ROOT.parent), "<workspace>"),
    ):
        text = text.replace(src, dst)
    return text


def run(command: list[str], *, timeout_seconds: int) -> dict:
    started = monotonic()
    timed_out = False
    try:
        proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=timeout_seconds)
        returncode = proc.returncode
        stdout = proc.stdout
        stderr = proc.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        returncode = 124
        stdout = exc.stdout or ""
        stderr = (exc.stderr or "") + f"\nTimed out after {timeout_seconds} seconds."
    return {
        "command": " ".join(command),
        "timeout_seconds": timeout_seconds,
        "timed_out": timed_out,
        "duration_seconds": round(monotonic() - started, 2),
        "returncode": returncode,
        "stdout": trim(stdout),
        "stderr": trim(stderr),
    }


def write_run_snapshot(results: list[dict], step_timeout_seconds: int, out: Path) -> dict:
    lookup_results = [
        result for result in results
        if "scripts/update_promo_engine_status.py" not in result.get("command", "")
    ]
    admin_update_results = [
        result for result in results
        if "scripts/update_promo_engine_status.py" in result.get("command", "")
    ]
    ok_count = sum(1 for result in lookup_results if result["returncode"] == 0)
    timed_out_count = sum(1 for result in lookup_results if result.get("timed_out"))
    failed = [result for result in lookup_results if result["returncode"] != 0]
    admin_update_ok = all(result["returncode"] == 0 for result in admin_update_results) if admin_update_results else None
    snapshot = {
        "ok": admin_update_ok is not False,
        "updated_at": datetime_now(),
        "source": "public-store-link-verification-run",
        "step_timeout_seconds": step_timeout_seconds,
        "summary": {
            "checked": len(lookup_results),
            "ok": ok_count,
            "not_live_or_failed": len(lookup_results) - ok_count,
            "timed_out": timed_out_count,
            "failed": len(failed),
            "admin_update_count": len(admin_update_results),
            "admin_update_ok": admin_update_ok,
        },
        "retry_command": f"python3 scripts/verify_pending_store_links.py --refresh-admin --step-timeout-seconds {step_timeout_seconds}",
        "results": results,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return snapshot


def datetime_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def hyperfollow_url(title: str) -> str:
    return f"https://distrokid.com/hyperfollow/lilyroo/{slugify(title)}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture public evidence for automatable pending store links.")
    parser.add_argument("--release", default="", help="Optional release title to verify.")
    parser.add_argument("--out", default=str(OUT.relative_to(ROOT)), help="Output run JSON path, relative to repo root or absolute.")
    parser.add_argument("--refresh-admin", action="store_true", help="Regenerate promo engine status/admin embeds after checks.")
    parser.add_argument("--step-timeout-seconds", type=int, default=DEFAULT_STEP_TIMEOUT_SECONDS, help="Maximum seconds for each public store lookup subprocess.")
    args = parser.parse_args()
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out

    status = json.loads(RELEASE_STATUS.read_text(encoding="utf-8"))
    results = []
    for release in status.get("releases", []):
        title = release.get("title") or ""
        if args.release and title != args.release:
            continue
        slug = slugify(title)
        output_root = Path("data") / "store-verification" / slug
        if not release.get("spotify_url"):
            results.append(run([
                "python3",
                "scripts/search_spotify_release.py",
                "--artist",
                status.get("artist", "Lily Roo"),
                "--title",
                title,
                "--out",
                str(output_root / "spotify_release_snapshot.json"),
            ], timeout_seconds=args.step_timeout_seconds))
        if not release.get("apple_music_url"):
            results.append(run([
                "python3",
                "scripts/capture_apple_music_release.py",
                "--artist",
                status.get("artist", "Lily Roo"),
                "--title",
                title,
                "--out",
                str(output_root / "apple_music_release_snapshot.json"),
            ], timeout_seconds=args.step_timeout_seconds))
        if not release.get("youtube_music_url"):
            results.append(run([
                "python3",
                "scripts/search_youtube_music_release.py",
                "--artist",
                status.get("artist", "Lily Roo"),
                "--title",
                title,
                "--out",
                str(output_root / "youtube_music_release_snapshot.json"),
            ], timeout_seconds=args.step_timeout_seconds))
        if not release.get("hyperfollow_url"):
            results.append(run([
                "python3",
                "scripts/capture_hyperfollow_store_links.py",
                "--url",
                hyperfollow_url(title),
                "--out",
                str(output_root / "hyperfollow_store_links_snapshot.json"),
            ], timeout_seconds=args.step_timeout_seconds))

    snapshot = write_run_snapshot(results, args.step_timeout_seconds, out)

    if args.refresh_admin:
        update_result = run(["python3", "scripts/update_promo_engine_status.py"], timeout_seconds=args.step_timeout_seconds)
        results.append(update_result)
        snapshot = write_run_snapshot(results, args.step_timeout_seconds, out)

    summary = snapshot["summary"]
    print(json.dumps({
        "checked": summary["checked"],
        "ok": summary["ok"],
        "not_live_or_failed": summary["not_live_or_failed"],
        "timed_out": summary["timed_out"],
        "step_timeout_seconds": args.step_timeout_seconds,
        "output": str(out.relative_to(ROOT)),
        "results": results,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
