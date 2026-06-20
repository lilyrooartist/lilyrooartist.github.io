#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "data" / "live_social_metrics.json"
MANUAL = ROOT / "data" / "manual_social_stats.json"
QUEUE = ROOT / "data" / "scheduled_posts.csv"
PUBLISHED = ROOT / "admin" / "content" / "Published_Log.csv"
OUT = ROOT / "data" / "metrics_history.json"


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_date(value: str | None):
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw[:10]).date()
    except ValueError:
        return None


def parse_datetime(value: str | None):
    raw = str(value or "").strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def metric(platforms: dict, platform: str, key: str):
    value = ((platforms.get(platform) or {}).get("metrics") or {}).get(key)
    return value if value not in (None, "") else None


def manual_value(manual: dict, platform: str, key: str):
    value = (manual.get(platform) or {}).get(key)
    if value in (None, "", "pending"):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        try:
            return float(value)
        except (TypeError, ValueError):
            return value


def dot_get(payload: dict, path: str):
    value = payload
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def delta(current, previous):
    if current is None or previous is None:
        return None
    if not isinstance(current, (int, float)) or not isinstance(previous, (int, float)):
        return None
    return current - previous


def build_snapshot(now: datetime) -> dict:
    live = read_json(LIVE, {})
    manual = read_json(MANUAL, {})
    platforms = live.get("platforms") if isinstance(live, dict) else {}
    queue_rows = read_csv(QUEUE)
    published_rows = read_csv(PUBLISHED)
    today = now.date()
    cutoff = today - timedelta(days=30)
    published_30d = [
        row for row in published_rows
        if (parsed := parse_date(row.get("date"))) and parsed >= cutoff
    ]
    approved_upcoming = [
        row for row in queue_rows
        if str(row.get("approved") or "").lower() == "yes"
        and (scheduled := parse_datetime(row.get("scheduled_at")))
        and scheduled >= now
    ]
    approved_total = [
        row for row in queue_rows
        if str(row.get("approved") or "").lower() == "yes"
    ]
    return {
        "date": today.isoformat(),
        "captured_at": now.isoformat().replace("+00:00", "Z"),
        "live_metrics_updated_at": live.get("updated_at", ""),
        "youtube": {
            "subscribers": metric(platforms, "youtube", "subscribers") or manual_value(manual, "youtube", "subscribers"),
            "total_views": metric(platforms, "youtube", "total_views") or manual_value(manual, "youtube", "total_views"),
            "video_count": metric(platforms, "youtube", "video_count") or manual_value(manual, "youtube", "video_count"),
        },
        "facebook": {
            "followers": metric(platforms, "facebook", "followers"),
            "page_likes": metric(platforms, "facebook", "page_likes"),
            "reach_7d": manual_value(manual, "facebook", "reach_7d"),
        },
        "spotify": {
            "artist_followers": manual_value(manual, "spotify", "artist_followers"),
            "monthly_listeners": manual_value(manual, "spotify", "monthly_listeners"),
            "release_streams": manual_value(manual, "spotify", "release_streams"),
            "saves": manual_value(manual, "spotify", "saves"),
        },
        "instagram": {
            "followers": metric(platforms, "instagram", "followers") or manual_value(manual, "instagram", "followers"),
            "profile_visits_7d": manual_value(manual, "instagram", "profile_visits_7d"),
        },
        "tiktok": {
            "followers": metric(platforms, "tiktok", "followers") or manual_value(manual, "tiktok", "followers"),
            "profile_views_7d": manual_value(manual, "tiktok", "profile_views_7d"),
        },
        "x": {
            "followers": metric(platforms, "x", "followers") or manual_value(manual, "x", "followers"),
            "impressions_7d": manual_value(manual, "x", "impressions_7d"),
        },
        "publishing": {
            "published_30d": len(published_30d),
            "published_total": len(published_rows),
        },
        "queue": {
            "approved_upcoming": len(approved_upcoming),
            "approved_total": len(approved_total),
            "scheduled_total": len(queue_rows),
        },
    }


def attach_deltas(snapshot: dict, previous: dict | None) -> dict:
    fields = [
        "youtube.subscribers",
        "youtube.total_views",
        "youtube.video_count",
        "facebook.followers",
        "facebook.page_likes",
        "instagram.followers",
        "tiktok.followers",
        "x.followers",
        "publishing.published_30d",
        "publishing.published_total",
        "queue.approved_upcoming",
        "queue.approved_total",
        "queue.scheduled_total",
    ]
    snapshot["delta_from_previous"] = {
        field: delta(dot_get(snapshot, field), dot_get(previous or {}, field))
        for field in fields
    }
    return snapshot


def set_dot(payload: dict, path: str, value):
    parts = path.split(".")
    target = payload
    for part in parts[:-1]:
        target = target.setdefault(part, {})
    target[parts[-1]] = value


def preserve_snapshot_values(snapshot: dict, source_snapshot: dict | None, marker: str, fields: list[str]) -> dict:
    if not source_snapshot:
        return snapshot
    preserved = []
    for field in fields:
        if dot_get(snapshot, field) is None and dot_get(source_snapshot, field) is not None:
            set_dot(snapshot, field, dot_get(source_snapshot, field))
            preserved.append(field)
    if preserved:
        snapshot[marker] = preserved
    return snapshot


def preserve_same_day_values(snapshot: dict, same_day: dict | None) -> dict:
    return preserve_snapshot_values(
        snapshot,
        same_day,
        "preserved_from_same_day_snapshot",
        [
            "youtube.subscribers",
            "youtube.total_views",
            "youtube.video_count",
            "facebook.followers",
            "facebook.page_likes",
            "instagram.followers",
            "tiktok.followers",
            "x.followers",
        ],
    )


def preserve_previous_cumulative_values(snapshot: dict, previous: dict | None) -> dict:
    return preserve_snapshot_values(
        snapshot,
        previous,
        "preserved_from_previous_snapshot",
        [
            "youtube.total_views",
            "youtube.video_count",
        ],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Append or update today's Lily Roo promo metrics history snapshot.")
    parser.add_argument("--refresh-admin", action="store_true", help="Regenerate promo status/admin embeds after updating history.")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    history = read_json(OUT, {"snapshots": []})
    snapshots = history.get("snapshots") or []
    same_day = next((item for item in reversed(snapshots) if item.get("date") == now.date().isoformat()), None)
    snapshots = [item for item in snapshots if item.get("date") != now.date().isoformat()]
    previous = snapshots[-1] if snapshots else None
    snapshot = preserve_same_day_values(build_snapshot(now), same_day)
    snapshot = preserve_previous_cumulative_values(snapshot, previous)
    snapshot = attach_deltas(snapshot, previous)
    snapshots.append(snapshot)
    history = {
        "updated_at": now.isoformat().replace("+00:00", "Z"),
        "source": [
            str(LIVE.relative_to(ROOT)),
            str(MANUAL.relative_to(ROOT)),
            str(QUEUE.relative_to(ROOT)),
            str(PUBLISHED.relative_to(ROOT)),
        ],
        "snapshots": snapshots[-90:],
    }
    OUT.write_text(json.dumps(history, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "updated": str(OUT.relative_to(ROOT)),
        "snapshots": len(history["snapshots"]),
        "latest": snapshot,
    }, indent=2))

    if args.refresh_admin:
        subprocess.run(["python3", "scripts/update_promo_engine_status.py"], cwd=ROOT, check=True)
        print("Refreshed promo status and admin embeds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
