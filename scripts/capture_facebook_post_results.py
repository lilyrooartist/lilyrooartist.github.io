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
from datetime import datetime, timezone
from pathlib import Path

from social_exec_common import SOCIAL_ENV, load_env


ROOT = Path(__file__).resolve().parents[1]
PUBLISHED_LOG = ROOT / "admin" / "content" / "Published_Log.csv"
OUT = ROOT / "data" / "facebook_post_results.json"
REPORT = ROOT / "admin" / "reports" / "facebook-post-results.md"
GRAPH_VERSION = "v20.0"
GRAPH_BASE = f"https://graph.facebook.com/{GRAPH_VERSION}"
RESULT_FIELDS = ["likes", "comments", "shares"]


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


def facebook_object_id(value: str) -> str:
    raw = str(value or "").strip()
    if re.fullmatch(r"\d+_\d+", raw):
        return raw
    match = re.search(r"facebook\.com/(\d+)_(\d+)", raw)
    if match:
        return f"{match.group(1)}_{match.group(2)}"
    return ""


def candidate_rows(post_ids: set[str]) -> list[dict]:
    rows = []
    for row in read_published_rows():
        if (row.get("platform") or "").strip().lower() != "facebook":
            continue
        content_id = (row.get("content_id") or "").strip()
        if not content_id:
            continue
        if post_ids and content_id not in post_ids:
            continue
        object_id = facebook_object_id(row.get("post_id_or_url") or "")
        if not object_id:
            continue
        rows.append({
            "post_id": content_id,
            "source_row": row["_source_row"],
            "facebook_object_id": object_id,
            "url": row.get("post_id_or_url") or "",
            "existing_values": {field: (row.get(field) or "").strip() for field in RESULT_FIELDS},
        })
    return rows


def require_meta_env() -> dict[str, str]:
    env = load_env(SOCIAL_ENV)
    missing = [
        name
        for name in ["META_LONG_LIVED_TOKEN", "FB_PAGE_ID"]
        if not (env.get(name) or "").strip()
    ]
    if missing:
        raise SystemExit(f"{SOCIAL_ENV.relative_to(ROOT.parent)} missing: {', '.join(missing)}")
    return env


def graph_get(path: str, params: dict[str, str]) -> dict:
    url = f"{GRAPH_BASE}/{path}?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=25) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Facebook Graph lookup failed with HTTP {error.code}: {body}") from error


def fetch_post(object_id: str, token: str) -> dict:
    return graph_get(
        object_id,
        {
            "fields": "id,created_time,permalink_url,shares,likes.summary(true).limit(0),reactions.summary(true).limit(0),comments.summary(true).limit(0)",
            "access_token": token,
        },
    )


def fetch_clicks(object_id: str, token: str) -> int | None:
    payload = graph_get(
        f"{object_id}/insights",
        {
            "metric": "post_clicks",
            "access_token": token,
        },
    )
    for item in payload.get("data") or []:
        if item.get("name") == "post_clicks":
            values = item.get("values") or []
            if values:
                try:
                    return int(values[0].get("value") or 0)
                except (TypeError, ValueError):
                    return None
    return None


def result_values(post: dict) -> dict[str, int]:
    shares_payload = post.get("shares") or {}
    return {
        "likes": int(((post.get("reactions") or {}).get("summary") or {}).get("total_count") or 0),
        "comments": int(((post.get("comments") or {}).get("summary") or {}).get("total_count") or 0),
        "shares": int(shares_payload.get("count") or 0),
    }


def build_payload(rows: list[dict], env: dict[str, str]) -> dict:
    captured = []
    for row in rows:
        post = fetch_post(row["facebook_object_id"], env["META_LONG_LIVED_TOKEN"])
        metrics = result_values(post)
        clicks = fetch_clicks(row["facebook_object_id"], env["META_LONG_LIVED_TOKEN"])
        evidence_note = f"Facebook Graph post metrics {datetime.now(timezone.utc).date().isoformat()}"
        filled = {
            field: metrics[field]
            for field in RESULT_FIELDS
            if not row["existing_values"].get(field)
        }
        captured.append({
            **row,
            "created_time": post.get("created_time") or "",
            "permalink_url": post.get("permalink_url") or "",
            "lookup_status": "ok",
            "metrics": metrics,
            "post_clicks_not_imported_as_views": clicks,
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
            "local_secret_source": str(SOCIAL_ENV.relative_to(ROOT.parent)),
            "graph_version": GRAPH_VERSION,
        },
        "summary": {
            "status": "ready_to_import" if any(item["filled_field_count"] for item in captured) else "no_open_facebook_result_fields",
            "captured_post_count": len(captured),
            "fillable_post_count": sum(1 for item in captured if item["filled_field_count"]),
            "fillable_result_field_count": sum(item["filled_field_count"] for item in captured),
            "post_ids": [item["post_id"] for item in captured],
            "result_fields": RESULT_FIELDS,
            "apply_command": "python3 scripts/capture_facebook_post_results.py --apply-results --refresh-admin",
            "report_path": relative(REPORT),
        },
        "rows": captured,
        "redaction": "Secret values are never written here; Meta credentials stay in the local secret source.",
        "views_guardrail": "Post clicks are captured for context but are not imported as views.",
    }


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Facebook Post Results - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Status: **{summary['status']}**",
        f"- Captured posts: **{summary['captured_post_count']}**",
        f"- Fillable posts: **{summary['fillable_post_count']}**",
        f"- Fillable result fields: **{summary['fillable_result_field_count']}**",
        f"- Apply command: `{summary['apply_command']}`",
        "",
        "## Rows",
    ]
    for item in payload["rows"]:
        metrics = item.get("metrics") or {}
        lines.extend([
            f"- **{item['post_id']}** row `{item['source_row']}`",
            f"  - URL: {item['url']}",
            f"  - Lookup: `{item.get('lookup_status') or 'unknown'}`",
            f"  - Likes: `{metrics.get('likes', 0)}`; comments: `{metrics.get('comments', 0)}`; shares: `{metrics.get('shares', 0)}`",
            f"  - Post clicks captured but not imported as views: `{item.get('post_clicks_not_imported_as_views')}`",
            f"  - Fillable fields: `{', '.join(item.get('fillable_results') or {}) or 'none'}`",
            f"  - Evidence: {item['evidence_note']}",
        ])
        if item.get("direct_apply_command"):
            lines.append(f"  - Apply: `{item['direct_apply_command']}`")
    lines.extend([
        "",
        "## Guardrails",
        "- Metrics come from the Facebook Graph API for already-published Lily Roo posts.",
        "- This report does not contain Meta credentials.",
        "- Post clicks are not treated as views.",
        "- Applying results goes through scripts/update_experiment_results.py so Published_Log.csv row IDs are verified.",
        "",
    ])
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
    parser = argparse.ArgumentParser(description="Capture Facebook metrics for Lily Roo published posts.")
    parser.add_argument("--post-id", action="append", default=[], help="Restrict to one content_id. Can be repeated.")
    parser.add_argument("--apply-results", action="store_true", help="Import captured metrics into Published_Log.csv.")
    parser.add_argument("--refresh-admin", action="store_true", help="Refresh admin after applying results.")
    args = parser.parse_args()

    if args.refresh_admin and not args.apply_results:
        raise SystemExit("--refresh-admin requires --apply-results")
    rows = candidate_rows(set(args.post_id))
    if not rows:
        raise SystemExit("No matching published Facebook rows with Graph object ids found.")
    env = require_meta_env()
    payload = build_payload(rows, env)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT.write_text(build_markdown(payload), encoding="utf-8")
    if args.apply_results:
        apply_results(payload, args.refresh_admin)
    print(json.dumps({"output": relative(OUT), **payload["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
