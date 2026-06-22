#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import hmac
import json
import random
import re
import string
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from social_exec_common import SOCIAL_ENV, load_env


ROOT = Path(__file__).resolve().parents[1]
PUBLISHED_LOG = ROOT / "admin" / "content" / "Published_Log.csv"
OUT = ROOT / "data" / "x_post_results.json"
REPORT = ROOT / "admin" / "reports" / "x-post-results.md"
X_TWEETS_URL = "https://api.x.com/2/tweets"
RESULT_FIELDS = ["views", "likes", "comments", "shares", "saves"]


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


def tweet_id_from_url(value: str) -> str:
    match = re.search(r"/status/(\d+)", str(value or ""))
    return match.group(1) if match else ""


def candidate_rows(post_ids: set[str]) -> list[dict]:
    rows = []
    for row in read_published_rows():
        if (row.get("platform") or "").strip().lower() != "x":
            continue
        content_id = (row.get("content_id") or "").strip()
        if not content_id:
            continue
        if post_ids and content_id not in post_ids:
            continue
        tweet_id = tweet_id_from_url(row.get("post_id_or_url") or "")
        if not tweet_id:
            continue
        rows.append({
            "post_id": content_id,
            "source_row": row["_source_row"],
            "tweet_id": tweet_id,
            "url": row.get("post_id_or_url") or "",
            "existing_values": {field: (row.get(field) or "").strip() for field in RESULT_FIELDS},
        })
    return rows


def require_x_env() -> dict[str, str]:
    env = load_env(SOCIAL_ENV)
    missing = [
        name
        for name in ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"]
        if not (env.get(name) or "").strip()
    ]
    if missing:
        raise SystemExit(f"{SOCIAL_ENV.relative_to(ROOT.parent)} missing: {', '.join(missing)}")
    return env


def oauth_encode(value: str) -> str:
    return urllib.parse.quote(str(value), safe="~-._")


def oauth1_header(method: str, url: str, query: dict[str, str], env: dict[str, str]) -> str:
    oauth = {
        "oauth_consumer_key": env["X_API_KEY"],
        "oauth_nonce": "".join(random.choice(string.ascii_letters + string.digits) for _ in range(32)),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": env["X_ACCESS_TOKEN"],
        "oauth_version": "1.0",
    }
    signing_params = {**query, **oauth}
    param_string = "&".join(
        f"{oauth_encode(key)}={oauth_encode(value)}"
        for key, value in sorted(signing_params.items())
    )
    base_string = "&".join([method.upper(), oauth_encode(url), oauth_encode(param_string)])
    signing_key = f"{oauth_encode(env['X_API_SECRET'])}&{oauth_encode(env['X_ACCESS_TOKEN_SECRET'])}".encode()
    signature = base64.b64encode(
        hmac.new(signing_key, base_string.encode(), hashlib.sha1).digest()
    ).decode()
    oauth["oauth_signature"] = signature
    return "OAuth " + ", ".join(
        f'{oauth_encode(key)}="{oauth_encode(value)}"'
        for key, value in oauth.items()
    )


def fetch_tweets(tweet_ids: list[str], env: dict[str, str]) -> dict[str, dict]:
    query = {
        "ids": ",".join(tweet_ids),
        "tweet.fields": "public_metrics,organic_metrics,non_public_metrics,created_at",
    }
    request = urllib.request.Request(
        X_TWEETS_URL + "?" + urllib.parse.urlencode(query),
        headers={
            "Authorization": oauth1_header("GET", X_TWEETS_URL, query, env),
            "Accept": "application/json",
            "User-Agent": "LilyRooXPostResults/1.0",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise SystemExit(f"X API lookup failed with HTTP {error.code}: {body}") from error
    return {str(item.get("id")): item for item in payload.get("data") or []}


def int_metric(payload: dict, *paths: str) -> int:
    for path in paths:
        cursor = payload
        for part in path.split("."):
            cursor = cursor.get(part) if isinstance(cursor, dict) else None
        if cursor is not None:
            try:
                return int(cursor)
            except (TypeError, ValueError):
                continue
    return 0


def result_values(tweet: dict) -> dict[str, int]:
    public = tweet.get("public_metrics") or {}
    shares = int_metric(tweet, "public_metrics.retweet_count") + int_metric(tweet, "public_metrics.quote_count")
    return {
        "views": int_metric(tweet, "organic_metrics.impression_count", "non_public_metrics.impression_count", "public_metrics.impression_count"),
        "likes": int(public.get("like_count") or 0),
        "comments": int(public.get("reply_count") or 0),
        "shares": shares,
        "saves": int(public.get("bookmark_count") or 0),
    }


def build_payload(rows: list[dict], tweets: dict[str, dict]) -> dict:
    captured = []
    for row in rows:
        tweet = tweets.get(row["tweet_id"]) or {}
        metrics = result_values(tweet) if tweet else {}
        evidence_note = f"X API tweet metrics {datetime.now(timezone.utc).date().isoformat()}"
        filled = {
            field: metrics[field]
            for field in RESULT_FIELDS
            if metrics and not row["existing_values"].get(field)
        }
        captured.append({
            **row,
            "created_at": tweet.get("created_at") or "",
            "lookup_status": "ok" if tweet else "missing_from_x_api_response",
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
            "local_secret_source": str(SOCIAL_ENV.relative_to(ROOT.parent)),
            "x_endpoint": X_TWEETS_URL,
        },
        "summary": {
            "status": "ready_to_import" if any(item["filled_field_count"] for item in captured) else "no_open_x_result_fields",
            "captured_post_count": len(captured),
            "fillable_post_count": sum(1 for item in captured if item["filled_field_count"]),
            "fillable_result_field_count": sum(item["filled_field_count"] for item in captured),
            "post_ids": [item["post_id"] for item in captured],
            "result_fields": RESULT_FIELDS,
            "apply_command": "python3 scripts/capture_x_post_results.py --apply-results --refresh-admin",
            "report_path": relative(REPORT),
        },
        "rows": captured,
        "redaction": "Secret values are never written here; X OAuth credentials stay in the local secret source.",
    }


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# X Post Results - Lily Roo",
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
            f"  - Views: `{metrics.get('views', 0)}`; likes: `{metrics.get('likes', 0)}`; comments: `{metrics.get('comments', 0)}`; shares: `{metrics.get('shares', 0)}`; saves: `{metrics.get('saves', 0)}`",
            f"  - Fillable fields: `{', '.join(item.get('fillable_results') or {}) or 'none'}`",
            f"  - Evidence: {item['evidence_note']}",
        ])
        if item.get("direct_apply_command"):
            lines.append(f"  - Apply: `{item['direct_apply_command']}`")
    lines.extend([
        "",
        "## Guardrails",
        "- Metrics come from the X API for already-published Lily Roo posts.",
        "- This report does not contain OAuth credentials.",
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
    parser = argparse.ArgumentParser(description="Capture X metrics for Lily Roo published posts.")
    parser.add_argument("--post-id", action="append", default=[], help="Restrict to one content_id. Can be repeated.")
    parser.add_argument("--apply-results", action="store_true", help="Import captured metrics into Published_Log.csv.")
    parser.add_argument("--refresh-admin", action="store_true", help="Refresh admin after applying results.")
    args = parser.parse_args()

    if args.refresh_admin and not args.apply_results:
        raise SystemExit("--refresh-admin requires --apply-results")
    rows = candidate_rows(set(args.post_id))
    if not rows:
        raise SystemExit("No matching published X rows with tweet URLs found.")
    env = require_x_env()
    tweets = fetch_tweets([row["tweet_id"] for row in rows], env)
    payload = build_payload(rows, tweets)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT.write_text(build_markdown(payload), encoding="utf-8")
    if args.apply_results:
        apply_results(payload, args.refresh_admin)
    print(json.dumps({"output": relative(OUT), **payload["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
