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
DEFAULT_STEP_TIMEOUT_SECONDS = 5


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def trim(value: str, limit: int = 3000) -> str:
    value = (value or "").strip()
    return value if len(value) <= limit else value[:limit] + "\n...[truncated]"


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


def hyperfollow_url(title: str) -> str:
    return f"https://distrokid.com/hyperfollow/lilyroo/{slugify(title)}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture public evidence for automatable pending store links.")
    parser.add_argument("--release", default="", help="Optional release title to verify.")
    parser.add_argument("--refresh-admin", action="store_true", help="Regenerate promo engine status/admin embeds after checks.")
    parser.add_argument("--step-timeout-seconds", type=int, default=DEFAULT_STEP_TIMEOUT_SECONDS, help="Maximum seconds for each public store lookup subprocess.")
    args = parser.parse_args()

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

    if args.refresh_admin:
        results.append(run(["python3", "scripts/update_promo_engine_status.py"], timeout_seconds=args.step_timeout_seconds))

    ok_count = sum(1 for result in results if result["returncode"] == 0)
    timed_out_count = sum(1 for result in results if result.get("timed_out"))
    print(json.dumps({
        "checked": len(results),
        "ok": ok_count,
        "not_live_or_failed": len(results) - ok_count,
        "timed_out": timed_out_count,
        "step_timeout_seconds": args.step_timeout_seconds,
        "results": results,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
