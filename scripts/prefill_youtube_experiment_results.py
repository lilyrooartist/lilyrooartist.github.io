#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from post_youtube_from_queue import refresh_access_token
from social_exec_common import YOUTUBE_ENV, load_env


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "data" / "experiment_result_entry_wide_template.csv"
OUT_CSV = ROOT / "data" / "youtube_experiment_public_metrics.csv"
OUT_JSON = ROOT / "data" / "youtube_experiment_public_metrics.json"
OUT_REPORT = ROOT / "admin" / "reports" / "youtube-experiment-public-metrics.md"
API_ROOT = "https://www.googleapis.com/youtube/v3"
RESULT_FIELDS = ("views", "likes", "comments", "shares", "saves", "subs_delta")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


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


def fetch_video_statistics(token: str, video_ids: list[str]) -> tuple[dict[str, dict], str]:
    if not video_ids:
        return {}, ""
    params = urllib.parse.urlencode({
        "part": "snippet,statistics",
        "id": ",".join(video_ids),
        "maxResults": "50",
    })
    request = urllib.request.Request(
        f"{API_ROOT}/videos?{params}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": "LilyRooYouTubeExperimentPrefill/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            error_payload = json.loads(raw)
        except json.JSONDecodeError:
            error_payload = {"error": raw[:300]}
        message = (error_payload.get("error") or {}).get("message") if isinstance(error_payload.get("error"), dict) else error_payload.get("error")
        return {}, f"YouTube API request failed ({exc.code}): {message or 'unknown error'}"
    rows = {}
    for item in payload.get("items") or []:
        video_id = str(item.get("id") or "").strip()
        if video_id:
            rows[video_id] = item
    return rows, ""


def numeric_stat(stats: dict, key: str) -> str:
    raw = str(stats.get(key) or "").strip()
    return raw if re.fullmatch(r"\d+", raw) else ""


def metric_row(row: dict, item: dict, captured_at: str) -> tuple[dict, dict]:
    stats = item.get("statistics") or {}
    video_id = str(item.get("id") or "").strip()
    out = {key: str(row.get(key) or "") for key in row.keys()}
    values = {
        "views": numeric_stat(stats, "viewCount"),
        "likes": numeric_stat(stats, "likeCount"),
        "comments": numeric_stat(stats, "commentCount"),
    }
    imported_fields = []
    for field, value in values.items():
        if value:
            out[field] = value
            imported_fields.append(field)
    out["shares"] = ""
    out["saves"] = ""
    out["subs_delta"] = ""
    if imported_fields:
        out["evidence_note"] = f"YouTube Data API public statistics {captured_at}; video_id={video_id}"
    return out, {
        "post_id": row.get("post_id") or "",
        "video_id": video_id,
        "post_url": row.get("post_url") or "",
        "importable_fields": imported_fields,
        "statistics": {field: out[field] for field in imported_fields},
        "title": (item.get("snippet") or {}).get("title", ""),
    }


def build_payload(template: Path) -> tuple[dict, list[str], list[dict]]:
    captured_at = utc_now()
    fieldnames, rows = read_csv(template)
    youtube_rows = [
        row for row in rows
        if str(row.get("platform") or "").strip().lower() == "youtube"
    ]
    video_ids = []
    id_by_post = {}
    for row in youtube_rows:
        video_id = video_id_from_url(row.get("post_url") or "")
        if video_id:
            id_by_post[row.get("post_id") or ""] = video_id
            video_ids.append(video_id)
    video_ids = sorted(set(video_ids))

    env = load_env(YOUTUBE_ENV)
    credential_keys = ["GOOGLE_CLIENT_ID", "YOUTUBE_REFRESH_TOKEN"]
    missing = [key for key in credential_keys if not env.get(key)]
    items = {}
    error = ""
    if missing:
        error = f"Missing YouTube OAuth key(s): {', '.join(missing)}"
    else:
        try:
            token = refresh_access_token(env)
            items, error = fetch_video_statistics(token, video_ids)
        except Exception as exc:
            error = str(exc)

    output_rows = []
    measurement_rows = []
    missing_video_ids = []
    for row in youtube_rows:
        post_id = row.get("post_id") or ""
        video_id = id_by_post.get(post_id, "")
        item = items.get(video_id)
        if item:
            out_row, measurement = metric_row(row, item, captured_at[:10])
            if measurement["importable_fields"]:
                output_rows.append(out_row)
                measurement_rows.append(measurement)
        elif video_id:
            missing_video_ids.append(video_id)

    payload = {
        "generated_at": captured_at,
        "safe_mode": True,
        "source": {
            "template": rel(template),
            "youtube_env": "secrets/youtube-api.env",
            "api": "youtube.videos.list(part=snippet,statistics)",
        },
        "summary": {
            "status": "ready_to_import" if output_rows else ("blocked" if error else "no_public_metrics"),
            "template_row_count": len(rows),
            "youtube_template_row_count": len(youtube_rows),
            "video_id_count": len(video_ids),
            "api_item_count": len(items),
            "importable_post_count": len(output_rows),
            "importable_field_count": sum(len(row["importable_fields"]) for row in measurement_rows),
            "missing_video_ids": missing_video_ids,
            "error": error,
            "output_csv": rel(OUT_CSV),
            "preview_command": f"python3 scripts/update_experiment_results.py --from-wide-csv {rel(OUT_CSV)} --dry-run",
            "apply_command": f"python3 scripts/update_experiment_results.py --from-wide-csv {rel(OUT_CSV)} --apply --refresh-admin" if output_rows else "",
        },
        "measurements": measurement_rows,
        "guardrails": [
            "This prefill reads public YouTube video statistics only.",
            "It writes a review CSV; it does not update Published_Log.csv or refresh admin state.",
            "The normal update_experiment_results.py dry-run/apply gate remains required before import.",
            "Secret values are never written to generated files.",
        ],
    }
    return payload, fieldnames, output_rows


def markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# YouTube Experiment Public Metrics - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Status: **{summary['status']}**",
        f"- YouTube template rows: **{summary['youtube_template_row_count']}**",
        f"- Importable posts: **{summary['importable_post_count']}**",
        f"- Importable fields: **{summary['importable_field_count']}**",
        f"- Output CSV: `{summary['output_csv']}`",
        f"- Preview: `{summary['preview_command']}`",
    ]
    if summary.get("apply_command"):
        lines.append(f"- Apply after review: `{summary['apply_command']}`")
    if summary.get("error"):
        lines.append(f"- Error: `{summary['error']}`")
    lines.extend(["", "## Measurements"])
    for row in payload.get("measurements") or []:
        metrics = ", ".join(f"{key}={value}" for key, value in (row.get("statistics") or {}).items())
        lines.append(f"- `{row.get('post_id')}` `{row.get('video_id')}` {metrics}")
    if not payload.get("measurements"):
        lines.append("- No importable YouTube public metrics were found.")
    lines.extend(["", "## Guardrails"])
    for item in payload.get("guardrails") or []:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Prefill experiment result CSV rows from public YouTube video statistics.")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE.relative_to(ROOT)), help="Wide experiment result template.")
    args = parser.parse_args()
    template = Path(args.template)
    if not template.is_absolute():
        template = ROOT / template
    payload, fieldnames, rows = build_payload(template)
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(OUT_CSV, fieldnames, rows)
    OUT_REPORT.write_text(markdown(payload), encoding="utf-8")
    print(json.dumps({"output": rel(OUT_JSON), **payload["summary"]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
