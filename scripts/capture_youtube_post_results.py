#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, time as dt_time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from post_youtube_from_queue import refresh_access_token
from social_exec_common import YOUTUBE_ENV, load_env


ROOT = Path(__file__).resolve().parents[1]
PUBLISHED_LOG = ROOT / "admin" / "content" / "Published_Log.csv"
OUT = ROOT / "data" / "youtube_post_results.json"
REPORT = ROOT / "admin" / "reports" / "youtube-post-results.md"
API_ROOT = "https://www.googleapis.com/youtube/v3"
RESULT_FIELDS = ["views", "likes", "comments"]
YOUTUBE_ENV_NAMES = ["GOOGLE_CLIENT_ID", "YOUTUBE_REFRESH_TOKEN"]
TZ = ZoneInfo("America/New_York")


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_published_rows() -> list[dict]:
    with PUBLISHED_LOG.open(newline="", encoding="utf-8") as handle:
        rows = []
        for index, row in enumerate(csv.DictReader(handle), start=2):
            row["_source_row"] = index
            rows.append(row)
        return rows


def video_id_from_url(url: str) -> str:
    parsed = urllib.parse.urlparse(str(url or "").strip())
    host = parsed.netloc.lower()
    if host in {"youtu.be", "www.youtu.be"}:
        return parsed.path.strip("/").split("/")[0]
    if host.endswith("youtube.com"):
        if parsed.path == "/watch":
            return urllib.parse.parse_qs(parsed.query).get("v", [""])[0]
        parts = [part for part in parsed.path.split("/") if part]
        if parts and parts[0] in {"shorts", "embed", "live"} and len(parts) > 1:
            return parts[1]
    return ""


def parse_published_at(value: str | None):
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        if "T" in raw:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=TZ)
            return parsed.astimezone(timezone.utc)
        parsed_date = datetime.fromisoformat(raw).date()
        return datetime.combine(parsed_date, dt_time(12, 0), TZ).astimezone(timezone.utc)
    except ValueError:
        return None


def candidate_rows(post_ids: set[str], min_age_hours: float = 0) -> list[dict]:
    rows = []
    now = datetime.now(timezone.utc)
    min_age = timedelta(hours=max(0, min_age_hours))
    for row in read_published_rows():
        if (row.get("platform") or "").strip().lower() != "youtube":
            continue
        content_id = (row.get("content_id") or "").strip()
        if not content_id:
            continue
        if post_ids and content_id not in post_ids:
            continue
        video_id = video_id_from_url(row.get("post_id_or_url") or "")
        if not video_id:
            continue
        published_at = parse_published_at(row.get("date"))
        measurement_due_at = published_at + min_age if published_at else None
        if min_age and (not measurement_due_at or measurement_due_at > now):
            continue
        rows.append({
            "post_id": content_id,
            "source_row": row["_source_row"],
            "video_id": video_id,
            "url": row.get("post_id_or_url") or "",
            "published_at": published_at.isoformat() if published_at else "",
            "measurement_due_at": measurement_due_at.isoformat() if measurement_due_at else "",
            "existing_values": {field: (row.get(field) or "").strip() for field in RESULT_FIELDS},
        })
    return rows


def missing_youtube_env(env: dict[str, str]) -> list[str]:
    return [name for name in YOUTUBE_ENV_NAMES if not (env.get(name) or "").strip()]


def fetch_videos(video_ids: list[str], token: str) -> dict[str, dict]:
    if not video_ids:
        return {}
    rows = {}
    for start in range(0, len(video_ids), 50):
        chunk = video_ids[start:start + 50]
        params = urllib.parse.urlencode({
            "part": "snippet,statistics",
            "id": ",".join(chunk),
            "maxResults": "50",
        })
        request = urllib.request.Request(
            f"{API_ROOT}/videos?{params}",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "User-Agent": "LilyRooYouTubePostResults/1.0",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            raise SystemExit(f"YouTube API lookup failed with HTTP {error.code}: {body}") from error
        for item in payload.get("items") or []:
            video_id = str(item.get("id") or "").strip()
            if video_id:
                rows[video_id] = item
    return rows


def int_metric(stats: dict, key: str) -> int:
    raw = str(stats.get(key) or "").strip()
    return int(raw) if re.fullmatch(r"\d+", raw) else 0


def result_values(item: dict) -> dict[str, int]:
    stats = item.get("statistics") or {}
    return {
        "views": int_metric(stats, "viewCount"),
        "likes": int_metric(stats, "likeCount"),
        "comments": int_metric(stats, "commentCount"),
    }


def build_payload(rows: list[dict], videos: dict[str, dict]) -> dict:
    captured = []
    captured_at = datetime.now(timezone.utc).date().isoformat()
    for row in rows:
        item = videos.get(row["video_id"]) or {}
        metrics = result_values(item) if item else {}
        evidence_note = f"YouTube Data API public statistics {captured_at}; video_id={row['video_id']}"
        filled = {
            field: metrics[field]
            for field in RESULT_FIELDS
            if metrics and not row["existing_values"].get(field)
        }
        captured.append({
            **row,
            "title": (item.get("snippet") or {}).get("title", ""),
            "lookup_status": "ok" if item else "missing_from_youtube_api_response",
            "metrics": metrics,
            "fillable_results": filled,
            "filled_field_count": len(filled),
            "evidence_note": evidence_note,
            "direct_apply_command": " ".join([
                "python3 scripts/update_experiment_results.py",
                f"--post-id {row['post_id']}",
                f"--source-row {row['source_row']}",
                *(f"--{field} {value}" for field, value in filled.items()),
                f"--evidence-note '{evidence_note}'",
                "--apply --refresh-admin",
            ]) if filled else "",
        })
    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "published_log": relative(PUBLISHED_LOG),
            "local_secret_source": str(YOUTUBE_ENV.relative_to(ROOT.parent)),
            "youtube_endpoint": f"{API_ROOT}/videos",
            "api": "youtube.videos.list(part=snippet,statistics)",
        },
        "summary": {
            "status": "ready_to_import" if any(item["filled_field_count"] for item in captured) else "no_open_youtube_result_fields",
            "captured_post_count": len(captured),
            "fillable_post_count": sum(1 for item in captured if item["filled_field_count"]),
            "fillable_result_field_count": sum(item["filled_field_count"] for item in captured),
            "post_ids": [item["post_id"] for item in captured],
            "result_fields": RESULT_FIELDS,
            "apply_command": "python3 scripts/capture_youtube_post_results.py --apply-results --refresh-admin",
            "retry_command": "python3 scripts/capture_youtube_post_results.py --min-age-hours 24 --allow-empty --apply-results --refresh-admin",
            "report_path": relative(REPORT),
        },
        "rows": captured,
        "guardrails": [
            "Metrics come from public YouTube video statistics for already-published Lily Roo videos.",
            "This report does not contain OAuth credentials.",
            "Only views, likes, and comments are imported; shares, saves, and subscriber deltas stay blank unless another evidence source supplies them.",
            "Applying results goes through scripts/update_experiment_results.py so Published_Log.csv row IDs are verified.",
        ],
    }


def build_missing_secret_payload(rows: list[dict], missing: list[str]) -> dict:
    captured_at = datetime.now(timezone.utc).date().isoformat()
    captured = [
        {
            **row,
            "title": "",
            "lookup_status": "skipped_missing_secrets",
            "metrics": {},
            "fillable_results": {},
            "filled_field_count": 0,
            "evidence_note": f"YouTube metric capture skipped {captured_at}: missing credential name(s) {', '.join(missing)}",
            "direct_apply_command": "",
        }
        for row in rows
    ]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "published_log": relative(PUBLISHED_LOG),
            "local_secret_source": str(YOUTUBE_ENV.relative_to(ROOT.parent)),
            "youtube_endpoint": f"{API_ROOT}/videos",
            "api": "youtube.videos.list(part=snippet,statistics)",
        },
        "summary": {
            "status": "skipped_missing_secrets",
            "captured_post_count": len(captured),
            "fillable_post_count": 0,
            "fillable_result_field_count": 0,
            "post_ids": [item["post_id"] for item in captured],
            "result_fields": RESULT_FIELDS,
            "missing_secret_names": missing,
            "apply_command": "python3 scripts/capture_youtube_post_results.py --apply-results --refresh-admin",
            "retry_command": "python3 scripts/capture_youtube_post_results.py --min-age-hours 24 --allow-empty --apply-results --refresh-admin",
            "report_path": relative(REPORT),
            "next_action": "Add the missing YouTube OAuth credential names locally or in GitHub Actions, then rerun capture.",
        },
        "rows": captured,
        "redaction": "Secret names are listed for operator diagnostics; secret values are never written here.",
        "guardrails": [
            "Metrics come from public YouTube video statistics for already-published Lily Roo videos when OAuth credentials are present.",
            "This skipped report does not contain OAuth credentials.",
            "Only views, likes, and comments are imported; shares, saves, and subscriber deltas stay blank unless another evidence source supplies them.",
            "Applying results goes through scripts/update_experiment_results.py so Published_Log.csv row IDs are verified.",
        ],
    }


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# YouTube Post Results - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Status: **{summary['status']}**",
        f"- Captured posts: **{summary['captured_post_count']}**",
        f"- Fillable posts: **{summary['fillable_post_count']}**",
        f"- Fillable result fields: **{summary['fillable_result_field_count']}**",
        f"- Apply command: `{summary['apply_command']}`",
    ]
    if summary.get("missing_secret_names"):
        lines.extend([
            f"- Missing credential names: `{', '.join(summary['missing_secret_names'])}`",
            f"- Next action: {summary.get('next_action', '')}",
        ])
    lines.extend(["", "## Rows"])
    for item in payload["rows"]:
        metrics = item.get("metrics") or {}
        lines.extend([
            f"- **{item['post_id']}** row `{item['source_row']}`",
            f"  - URL: {item['url']}",
            f"  - Video ID: `{item['video_id']}`",
            f"  - Lookup: `{item.get('lookup_status') or 'unknown'}`",
            f"  - Views: `{metrics.get('views', 0)}`; likes: `{metrics.get('likes', 0)}`; comments: `{metrics.get('comments', 0)}`",
            f"  - Fillable fields: `{', '.join(item.get('fillable_results') or {}) or 'none'}`",
            f"  - Evidence: {item['evidence_note']}",
        ])
        if item.get("direct_apply_command"):
            lines.append(f"  - Apply: `{item['direct_apply_command']}`")
    lines.extend(["", "## Guardrails"])
    for item in payload.get("guardrails") or []:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def apply_results(payload: dict, refresh_admin: bool) -> None:
    for item in payload["rows"]:
        values = item.get("fillable_results") or {}
        if not values:
            continue
        command = [
            "python3",
            "scripts/update_experiment_results.py",
            "--post-id",
            item["post_id"],
            "--source-row",
            str(item["source_row"]),
            "--evidence-note",
            item["evidence_note"],
        ]
        for field, value in values.items():
            command.extend([f"--{field}", str(value)])
        command.append("--apply")
        subprocess.run(command, cwd=ROOT, check=True)
    if refresh_admin:
        subprocess.run(["python3", "scripts/refresh_promo_admin.py"], cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture YouTube public video metrics for Lily Roo published posts.")
    parser.add_argument("--post-id", action="append", default=[], help="Restrict to one content_id. Can be repeated.")
    parser.add_argument("--min-age-hours", type=float, default=0, help="Only capture rows whose published date is at least this old.")
    parser.add_argument("--allow-empty", action="store_true", help="Write an empty report instead of failing when no rows match.")
    parser.add_argument("--skip-missing-secrets", action="store_true", help="Write a skipped report and exit 0 when YouTube credentials are absent.")
    parser.add_argument("--apply-results", action="store_true", help="Import captured metrics into Published_Log.csv.")
    parser.add_argument("--refresh-admin", action="store_true", help="Refresh admin after applying results.")
    args = parser.parse_args()

    if args.refresh_admin and not args.apply_results:
        raise SystemExit("--refresh-admin requires --apply-results")
    rows = candidate_rows(set(args.post_id), args.min_age_hours)
    if not rows:
        if args.allow_empty:
            payload = build_payload([], {})
            payload["summary"]["status"] = "no_matching_youtube_rows"
            OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            REPORT.write_text(build_markdown(payload), encoding="utf-8")
            print(json.dumps({"output": relative(OUT), **payload["summary"]}, indent=2))
            return 0
        raise SystemExit("No matching published YouTube rows with video URLs found.")
    env = load_env(YOUTUBE_ENV)
    missing = missing_youtube_env(env)
    if missing:
        if args.skip_missing_secrets:
            payload = build_missing_secret_payload(rows, missing)
            OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            REPORT.write_text(build_markdown(payload), encoding="utf-8")
            print(json.dumps({"output": relative(OUT), **payload["summary"]}, indent=2))
            return 0
        raise SystemExit(f"{YOUTUBE_ENV.relative_to(ROOT.parent)} missing: {', '.join(missing)}")
    token = refresh_access_token(env)
    videos = fetch_videos([row["video_id"] for row in rows], token)
    payload = build_payload(rows, videos)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT.write_text(build_markdown(payload), encoding="utf-8")
    if args.apply_results:
        apply_results(payload, args.refresh_admin)
    print(json.dumps({"output": relative(OUT), **payload["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
