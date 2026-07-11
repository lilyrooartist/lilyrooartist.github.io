#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import statistics
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / "data" / "growth_reset_campaign.json"
CLIPS = ROOT / "data" / "growth_reset_clips.json"
QUEUE = ROOT / "data" / "scheduled_posts.csv"
CLICKS = ROOT / "data" / "brand_campaign_clicks.json"
YOUTUBE_RESULTS = ROOT / "data" / "youtube_post_results.json"
FACEBOOK_RESULTS = ROOT / "data" / "facebook_post_results.json"
LIVE_METRICS = ROOT / "data" / "live_social_metrics.json"
METRICS_HISTORY = ROOT / "data" / "metrics_history.json"
PAID_RESULTS = ROOT / "data" / "growth_reset_paid_results.json"
OUT = ROOT / "data" / "growth_reset_outcomes.json"
REPORT = ROOT / "admin" / "reports" / "growth-reset-outcomes.md"
PREFIX = "FP-GROWTH-RESET-"

START_DATE = date(2026, 7, 13)
END_DATE = START_DATE + timedelta(days=29)
TARGETS = {
    "native_video_plays": 5000,
    "qualified_clicks": 25,
    "youtube_subscribers": 11,
    "spotify_monthly_listeners": 10,
    "repeatable_formats": 2,
}


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def number(value):
    if value in (None, ""):
        return None
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None


def integer(value) -> int:
    parsed = number(value)
    return int(parsed) if parsed is not None else 0


def metric(row: dict, *names: str) -> float | None:
    sources = [row.get("metrics") or {}, row.get("existing_values") or {}, row]
    for source in sources:
        for name in names:
            value = number(source.get(name))
            if value is not None:
                return value
    return None


def history_snapshot(snapshots: list[dict], target: date) -> dict:
    eligible = []
    for snapshot in snapshots:
        try:
            snapshot_date = date.fromisoformat(str(snapshot.get("date") or ""))
        except ValueError:
            continue
        if snapshot_date <= target:
            eligible.append((snapshot_date, snapshot))
    return max(eligible, key=lambda item: item[0])[1] if eligible else {}


def history_change(snapshots: list[dict], latest: dict, days: int, platform: str, field: str):
    if not latest:
        return None
    try:
        latest_date = date.fromisoformat(str(latest.get("date") or ""))
    except ValueError:
        return None
    previous = history_snapshot(snapshots, latest_date - timedelta(days=days))
    current_value = number((latest.get(platform) or {}).get(field))
    previous_value = number((previous.get(platform) or {}).get(field))
    if current_value is None or previous_value is None:
        return None
    return current_value - previous_value


def post_id(row: dict) -> str:
    return str(row.get("post_id") or row.get("id") or "").strip()


def campaign_clicks(payload: dict) -> list[dict]:
    return [
        row for row in payload.get("recent_clicks") or []
        if str(row.get("post_id") or "").upper().startswith(PREFIX)
    ]


def clip_lookup(payload: dict) -> dict[str, dict]:
    rows = payload.get("clips") or payload.get("rows") or []
    lookup = {}
    for row in rows:
        key = str(row.get("clip_id") or row.get("id") or "").strip()
        if key:
            lookup[key] = row
    return lookup


def campaign_rows(payload: dict, queue: list[dict]) -> list[dict]:
    rows = [row for row in queue if str(row.get("id") or "").startswith(PREFIX)]
    return rows or payload.get("rows") or payload.get("posts") or []


def creative_key(row: dict) -> str:
    explicit = str(row.get("creative_id") or "").strip()
    if explicit:
        return explicit
    raw = str(row.get("id") or "")
    for suffix in ("-YOUTUBE", "-FACEBOOK", "-X"):
        if raw.endswith(suffix):
            return raw[: -len(suffix)]
    return raw


def platform_results(payload: dict) -> dict[str, dict]:
    return {
        post_id(row): row
        for row in payload.get("rows") or []
        if post_id(row).startswith(PREFIX)
    }


def build() -> dict:
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    campaign = read_json(CAMPAIGN, {})
    clips = read_json(CLIPS, {})
    queue = read_csv(QUEUE)
    click_payload = read_json(CLICKS, {})
    youtube_payload = read_json(YOUTUBE_RESULTS, {})
    facebook_payload = read_json(FACEBOOK_RESULTS, {})
    live = read_json(LIVE_METRICS, {})
    history = read_json(METRICS_HISTORY, {})
    paid = read_json(PAID_RESULTS, {})

    rows = campaign_rows(campaign, queue)
    clip_map = clip_lookup(clips)
    clicks = campaign_clicks(click_payload)
    click_counts: dict[str, int] = defaultdict(int)
    for row in clicks:
        click_counts[str(row.get("post_id") or "").upper()] += 1

    results = platform_results(youtube_payload)
    results.update(platform_results(facebook_payload))
    creative_rows: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if str(row.get("post_type") or "").lower() != "video":
            continue
        creative_rows[creative_key(row)].append(row)

    creative_outcomes = []
    for key, post_rows in sorted(creative_rows.items()):
        sample = post_rows[0]
        result_rows = [results.get(str(row.get("id") or ""), {}) for row in post_rows]
        plays = sum(integer(metric(row, "views", "video_views", "total_video_views", "plays")) for row in result_rows)
        engagements = sum(
            integer(metric(row, "likes"))
            + integer(metric(row, "comments"))
            + integer(metric(row, "shares"))
            + integer(metric(row, "saves"))
            for row in result_rows
        )
        post_clicks = sum(click_counts.get(str(row.get("id") or "").upper(), 0) for row in post_rows)
        clip_id = str(sample.get("clip_id") or sample.get("media_key") or "").strip()
        clip = clip_map.get(clip_id, {})
        creative_outcomes.append({
            "creative_id": key,
            "clip_id": clip_id,
            "song": sample.get("song") or clip.get("song") or clip.get("track") or "",
            "concept": sample.get("concept") or clip.get("concept") or "",
            "destination": sample.get("destination") or clip.get("destination") or "",
            "post_ids": [row.get("id") for row in post_rows],
            "platforms": sorted({str(row.get("platform") or "") for row in post_rows if row.get("platform")}),
            "native_video_plays": plays,
            "qualified_clicks": post_clicks,
            "engagements": engagements,
            "destination_response_rate": round((post_clicks / plays) * 100, 3) if plays else None,
            "measurement_status": "measured" if plays or post_clicks or engagements else "waiting",
        })

    measured_plays = [row["native_video_plays"] for row in creative_outcomes if row["native_video_plays"] > 0]
    median_plays = statistics.median(measured_plays) if measured_plays else 0
    repeatable = [
        row for row in creative_outcomes
        if (median_plays and row["native_video_plays"] >= median_plays * 2)
        or (row["destination_response_rate"] is not None and row["destination_response_rate"] >= 2)
    ]

    plays_total = sum(row["native_video_plays"] for row in creative_outcomes)
    clicks_total = len(clicks)
    spend = round(sum(number(row.get("spend_usd")) or 0 for row in paid.get("rows") or []), 2)
    cost_per_click = round(spend / clicks_total, 2) if spend and clicks_total else None

    snapshots = history.get("snapshots") or []
    latest = snapshots[-1] if snapshots else {}
    baseline_snapshot = history_snapshot(snapshots, START_DATE - timedelta(days=1)) or latest
    youtube_live = ((live.get("platforms") or {}).get("youtube") or {})
    spotify_live = ((live.get("platforms") or {}).get("spotify") or {})
    youtube_subscribers = number((youtube_live.get("metrics") or {}).get("subscribers"))
    if youtube_subscribers is None:
        youtube_subscribers = number((latest.get("youtube") or {}).get("subscribers"))
    spotify_listeners = number((spotify_live.get("metrics") or {}).get("monthly_listeners"))
    if spotify_listeners is None:
        spotify_listeners = number((latest.get("spotify") or {}).get("monthly_listeners"))

    song_totals: dict[str, dict[str, int]] = defaultdict(lambda: {"plays": 0, "clicks": 0})
    format_totals: dict[str, dict[str, int]] = defaultdict(lambda: {"plays": 0, "clicks": 0})
    for row in creative_outcomes:
        song_totals[row["song"]]["plays"] += row["native_video_plays"]
        song_totals[row["song"]]["clicks"] += row["qualified_clicks"]
        format_totals[row["concept"]]["plays"] += row["native_video_plays"]
        format_totals[row["concept"]]["clicks"] += row["qualified_clicks"]

    def best(totals: dict[str, dict[str, int]]) -> dict:
        if not totals or not any(values["plays"] or values["clicks"] for values in totals.values()):
            return {"name": "Waiting for results", "plays": 0, "clicks": 0}
        name, values = max(totals.items(), key=lambda item: (item[1]["clicks"], item[1]["plays"], item[0]))
        return {"name": name or "Unlabeled", **values}

    current = {
        "native_video_plays": plays_total,
        "qualified_clicks": clicks_total,
        "youtube_subscribers": int(youtube_subscribers) if youtube_subscribers is not None else None,
        "spotify_monthly_listeners": int(spotify_listeners) if spotify_listeners is not None else None,
        "repeatable_formats": len(repeatable),
    }
    progress = {
        key: round((current[key] / target) * 100, 1) if current[key] is not None and target else None
        for key, target in TARGETS.items()
    }
    all_targets_reached = all(current[key] is not None and current[key] >= target for key, target in TARGETS.items())
    campaign_started = datetime.now(timezone.utc).date() >= START_DATE
    measured_count = sum(row["measurement_status"] == "measured" for row in creative_outcomes)
    paid_test_complete = bool(paid.get("test_complete"))
    any_threshold_hit = any(
        row["native_video_plays"] >= 500
        or (row["destination_response_rate"] is not None and row["destination_response_rate"] >= 1)
        for row in creative_outcomes
    )
    if all_targets_reached:
        status = "success"
    elif paid_test_complete and not any_threshold_hit:
        status = "stop_and_rethink"
    elif measured_count:
        status = "learning"
    elif campaign_started:
        status = "baseline"
    else:
        status = "scheduled"

    return {
        "generated_at": generated_at,
        "status": status,
        "campaign": {
            "name": "Lily Roo Growth Strategy Reset",
            "start_date": START_DATE.isoformat(),
            "end_date": END_DATE.isoformat(),
            "duration_days": 30,
            "budget_usd": 150,
            "spend_authorized": False,
            "spend_usd": spend,
            "cost_per_qualified_click": cost_per_click,
        },
        "baseline": {
            "snapshot_date": baseline_snapshot.get("date") or "",
            "youtube_subscribers": integer((baseline_snapshot.get("youtube") or {}).get("subscribers")) or 6,
            "youtube_total_views": integer((baseline_snapshot.get("youtube") or {}).get("total_views")) or 487,
            "spotify_monthly_listeners": integer((baseline_snapshot.get("spotify") or {}).get("monthly_listeners")) or 1,
        },
        "targets": TARGETS,
        "current": current,
        "progress_percent": progress,
        "change": {
            "youtube_subscribers_7d": history_change(snapshots, latest, 7, "youtube", "subscribers"),
            "youtube_subscribers_30d": history_change(snapshots, latest, 30, "youtube", "subscribers"),
            "youtube_total_views_7d": history_change(snapshots, latest, 7, "youtube", "total_views"),
            "youtube_total_views_30d": history_change(snapshots, latest, 30, "youtube", "total_views"),
            "spotify_monthly_listeners_7d": history_change(snapshots, latest, 7, "spotify", "monthly_listeners"),
            "spotify_monthly_listeners_30d": history_change(snapshots, latest, 30, "spotify", "monthly_listeners"),
        },
        "summary": {
            "creative_count": len(creative_outcomes),
            "measured_creative_count": measured_count,
            "scheduled_post_count": len(rows),
            "automatic_post_count": sum(str(row.get("execution_mode") or "auto").lower() == "auto" for row in rows),
            "manual_post_count": sum(str(row.get("execution_mode") or "").lower() == "manual" for row in rows),
            "median_native_plays": median_plays,
            "repeatable_format_count": len(repeatable),
            "best_song": best(song_totals),
            "best_format": best(format_totals),
            "next_decision": "Keep testing until the first six clips have organic results." if status in {"scheduled", "baseline"} else (
                "Replace the visual premise or song selection before further spend." if status == "stop_and_rethink" else
                "Scale only the formats beating the campaign median."
            ),
        },
        "creative_outcomes": creative_outcomes,
        "repeatable_formats": repeatable,
        "stop_rule": {
            "applies_after_paid_testing": True,
            "minimum_native_plays": 500,
            "minimum_destination_response_percent": 1,
            "triggered": status == "stop_and_rethink",
        },
        "sources": {
            "campaign": str(CAMPAIGN.relative_to(ROOT)),
            "clips": str(CLIPS.relative_to(ROOT)),
            "clicks": str(CLICKS.relative_to(ROOT)),
            "youtube_results": str(YOUTUBE_RESULTS.relative_to(ROOT)),
            "facebook_results": str(FACEBOOK_RESULTS.relative_to(ROOT)),
            "metrics_history": str(METRICS_HISTORY.relative_to(ROOT)),
            "paid_results_optional": str(PAID_RESULTS.relative_to(ROOT)),
        },
    }


def write_report(payload: dict) -> None:
    current = payload["current"]
    targets = payload["targets"]
    summary = payload["summary"]
    lines = [
        "# Lily Roo Growth Reset Outcomes",
        "",
        f"Generated: {payload['generated_at']}",
        f"Status: **{payload['status'].replace('_', ' ')}**",
        "",
        "## Scorecard",
        f"- Native video plays: **{current['native_video_plays']} / {targets['native_video_plays']}**",
        f"- Qualified clicks: **{current['qualified_clicks']} / {targets['qualified_clicks']}**",
        f"- YouTube subscribers: **{current['youtube_subscribers']} / {targets['youtube_subscribers']}**",
        f"- Spotify monthly listeners: **{current['spotify_monthly_listeners']} / {targets['spotify_monthly_listeners']}**",
        f"- Repeatable formats: **{current['repeatable_formats']} / {targets['repeatable_formats']}**",
        "",
        "## Current Leaders",
        f"- Song: **{summary['best_song']['name']}** ({summary['best_song']['plays']} plays, {summary['best_song']['clicks']} clicks)",
        f"- Format: **{summary['best_format']['name']}** ({summary['best_format']['plays']} plays, {summary['best_format']['clicks']} clicks)",
        f"- Next decision: {summary['next_decision']}",
        "",
        "## Budget",
        f"- Planned: **${payload['campaign']['budget_usd']}**",
        f"- Authorized: **{'yes' if payload['campaign']['spend_authorized'] else 'no'}**",
        f"- Recorded spend: **${payload['campaign']['spend_usd']:.2f}**",
        f"- Cost per qualified click: **{payload['campaign']['cost_per_qualified_click'] if payload['campaign']['cost_per_qualified_click'] is not None else 'not available'}**",
        "",
        "No ad spend is activated by this report.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = build()
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_report(payload)
    print(json.dumps({
        "output": str(OUT.relative_to(ROOT)),
        "status": payload["status"],
        "creative_count": payload["summary"]["creative_count"],
        "native_video_plays": payload["current"]["native_video_plays"],
        "qualified_clicks": payload["current"]["qualified_clicks"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
