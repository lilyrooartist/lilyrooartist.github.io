#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
GITHUB_REPO_URL = "https://github.com/lilyrooartist/lilyrooartist.github.io"
RELEASE_STATUS = ROOT / "data" / "distrokid_release_status.json"
MANUAL_METRICS = ROOT / "data" / "manual_social_stats.json"
LIVE_METRICS = ROOT / "data" / "live_social_metrics.json"
METRICS_HISTORY = ROOT / "data" / "metrics_history.json"
EXECUTOR_READINESS = ROOT / "data" / "executor_readiness_snapshot.json"
STORE_VERIFICATION_HISTORY = ROOT / "data" / "store_verification_history.json"
SOCIAL_EXECUTIONS = ROOT / "data" / "social_execution_snapshot.json"
SOCIAL_SCHEDULER_DRY_RUN = ROOT / "data" / "social_scheduler_dry_run.json"
PROMO_REFRESH_RUN = ROOT / "data" / "promo_admin_refresh_run.json"
PROMO_REFRESH_WORKFLOW_STATUS = ROOT / "data" / "promo_refresh_workflow_status.json"
PROMO_REFRESH_WORKFLOW = ROOT / ".github" / "workflows" / "promo-admin-refresh.yml"
SCHEDULED = ROOT / "data" / "scheduled_posts.csv"
PROMO_QUEUE_PLAN = ROOT / "data" / "promo_queue_plan.json"
PUBLISHED = ROOT / "admin" / "content" / "Published_Log.csv"
FUTURE_POSTS = ROOT / "admin" / "future-posts.json"
RESCHEDULE_SCRIPT = ROOT / "scripts" / "reschedule_scheduled_posts.py"
OUT = ROOT / "data" / "promo_engine_status.json"
ADMIN_INDEX = ROOT / "admin" / "index.html"

PROMO_PLATFORMS = ["X", "Instagram", "TikTok", "Facebook", "YouTube Community"]
YOUTUBE_MONETIZATION_SUBSCRIBER_TARGET = 1000
STORE_SERVICES = [
    ("Spotify", "spotify_url"),
    ("Apple Music", "apple_music_url"),
    ("YouTube Music", "youtube_music_url"),
    ("HyperFollow", "hyperfollow_url"),
    ("YouTube playlist", "youtube_playlist_url"),
]
SOURCE_MAX_AGE_HOURS = {
    "release_status": 72,
    "scheduled_posts": 72,
    "promo_queue_plan": 24,
    "published_log": 168,
    "manual_metrics": 72,
    "live_metrics": 24,
    "metrics_history": 24,
    "executor_readiness": 24,
    "store_verification_history": 24,
    "social_executions": 24,
    "social_scheduler_dry_run": 24,
    "promo_refresh_run": 24,
    "promo_refresh_workflow_status": 24,
}

RELEASE_TRACKS = {
    "I Learned It All in Fifteen Seconds": [
        "I Learned It All in Fifteen Seconds",
    ],
    "Twelve Dollars": [
        "Brain Rot",
        "Every Pearl in Carmel",
        "The Other One's Charging",
        "Twelve Dollars",
        "William and Dander",
        "Just Don't Talk About It",
        "Gluten Free Bread",
        "When Lily Talks",
    ],
    "Analog Myth": [
        "13",
        "Girls Camp",
        "Analog Myth",
        "Spilling the Tea",
        "No Mortgage",
        "Guards Down",
        "Slow Walk",
        "The Power of Light",
        "The Power of Light (My Second Room Has No Light Switch Reprise)",
    ],
}


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


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


def file_mtime(path: Path):
    if not path.exists():
        return None
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


def payload_timestamp(path: Path, payload):
    if isinstance(payload, dict):
        for key in ("generated_at", "updated_at"):
            parsed = parse_datetime(payload.get(key))
            if parsed:
                return parsed
    return file_mtime(path)


def freshness_row(name: str, path: Path, payload, now: datetime):
    timestamp = payload_timestamp(path, payload)
    max_age = SOURCE_MAX_AGE_HOURS[name]
    if timestamp is None:
        return {
            "name": name,
            "path": str(path.relative_to(ROOT)),
            "status": "missing",
            "age_hours": None,
            "max_age_hours": max_age,
            "timestamp": "",
            "refresh_command": refresh_command(name),
        }
    age_hours = round((now - timestamp).total_seconds() / 3600, 1)
    return {
        "name": name,
        "path": str(path.relative_to(ROOT)),
        "status": "fresh" if age_hours <= max_age else "stale",
        "age_hours": age_hours,
        "max_age_hours": max_age,
        "timestamp": timestamp.isoformat(),
        "refresh_command": refresh_command(name),
    }


def release_status_checked_no_change(row: dict, store_history: dict, now: datetime) -> dict:
    if row.get("status") != "stale":
        return row
    summary = store_history.get("summary") or {}
    checked_at = payload_timestamp(STORE_VERIFICATION_HISTORY, store_history)
    if not checked_at:
        return row
    checked_age = round((now - checked_at).total_seconds() / 3600, 1)
    if checked_age > SOURCE_MAX_AGE_HOURS["store_verification_history"]:
        return row
    if int(summary.get("snapshot_count") or 0) <= 0:
        return row
    if int(summary.get("found_in_snapshot") or 0) > 0:
        return row
    checked_pending = int(summary.get("checked_pending") or 0)
    if checked_pending <= 0:
        return row
    updated = dict(row)
    updated["status"] = "checked_no_change"
    updated["checked_at"] = checked_at.isoformat()
    updated["checked_age_hours"] = checked_age
    updated["evidence"] = f"{checked_pending} pending store links checked; no new public URLs found."
    updated["refresh_command"] = "Store checks are current; update data/distrokid_release_status.json when a verified public URL appears."
    return updated


def refresh_command(name: str) -> str:
    return {
        "release_status": "python3 scripts/verify_pending_store_links.py --refresh-admin; update data/distrokid_release_status.json when a public URL is verified.",
        "scheduled_posts": "python3 scripts/sync_future_posts.py",
        "promo_queue_plan": "python3 scripts/update_promo_engine_status.py && python3 scripts/generate_promo_queue_plan.py && python3 scripts/update_promo_engine_status.py",
        "published_log": "Export or append latest published posts to admin/content/Published_Log.csv.",
        "manual_metrics": "Update data/manual_social_stats.json with latest manual metrics.",
        "live_metrics": "python3 scripts/capture_live_metrics.py",
        "metrics_history": "python3 scripts/update_metrics_history.py --refresh-admin",
        "executor_readiness": "python3 scripts/capture_executor_readiness.py && python3 scripts/generate_promo_queue_plan.py && python3 scripts/update_promo_engine_status.py",
        "store_verification_history": "python3 scripts/verify_pending_store_links.py --refresh-admin",
        "social_executions": "python3 scripts/capture_social_executions.py && python3 scripts/update_promo_engine_status.py",
        "social_scheduler_dry_run": "python3 scripts/capture_scheduler_dry_run.py && python3 scripts/update_promo_engine_status.py",
        "promo_refresh_run": "python3 scripts/refresh_promo_admin.py",
        "promo_refresh_workflow_status": "python3 scripts/capture_github_workflow_status.py && python3 scripts/update_promo_engine_status.py",
    }.get(name, "")


def source_freshness(release_status, manual, live, metrics_history, executor_readiness, store_history, social_executions, social_scheduler_dry_run, promo_refresh_run, promo_refresh_workflow_status, promo_plan, future_posts, now: datetime):
    rows = [
        release_status_checked_no_change(freshness_row("release_status", RELEASE_STATUS, release_status, now), store_history, now),
        freshness_row("scheduled_posts", FUTURE_POSTS, future_posts, now),
        freshness_row("promo_queue_plan", PROMO_QUEUE_PLAN, promo_plan, now),
        freshness_row("published_log", PUBLISHED, None, now),
        freshness_row("manual_metrics", MANUAL_METRICS, manual, now),
        freshness_row("live_metrics", LIVE_METRICS, live, now),
        freshness_row("metrics_history", METRICS_HISTORY, metrics_history, now),
        freshness_row("executor_readiness", EXECUTOR_READINESS, executor_readiness, now),
        freshness_row("store_verification_history", STORE_VERIFICATION_HISTORY, store_history, now),
        freshness_row("social_executions", SOCIAL_EXECUTIONS, social_executions, now),
        freshness_row("social_scheduler_dry_run", SOCIAL_SCHEDULER_DRY_RUN, social_scheduler_dry_run, now),
        freshness_row("promo_refresh_run", PROMO_REFRESH_RUN, promo_refresh_run, now),
        freshness_row("promo_refresh_workflow_status", PROMO_REFRESH_WORKFLOW_STATUS, promo_refresh_workflow_status, now),
    ]
    stale = [row for row in rows if row["status"] == "stale"]
    missing = [row for row in rows if row["status"] == "missing"]
    checked_no_change = [row for row in rows if row["status"] == "checked_no_change"]
    return {
        "summary": {
            "fresh": sum(1 for row in rows if row["status"] == "fresh"),
            "stale": len(stale),
            "missing": len(missing),
            "checked_no_change": len(checked_no_change),
            "checked_at": now.isoformat(),
        },
        "sources": rows,
        "actions": [
            freshness_action_message(row)
            for row in stale + missing
        ],
    }


def freshness_action_message(row: dict) -> str:
    name = row["name"].replace("_", " ")
    if row.get("name") == "manual_metrics":
        return (
            "Refresh manual metrics: fill data/manual_metric_collection_template.csv, "
            "preview with python3 scripts/update_manual_social_stats.py --from-csv --dry-run, "
            "then import with python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin."
        )
    return f"Refresh {name}: {row['refresh_command']}"


def norm(value: str | None) -> str:
    return " ".join(str(value or "").strip().lower().split())


def shell_quote(value: str) -> str:
    return "'" + str(value).replace("'", "'\"'\"'") + "'"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", norm(value))
    return slug.strip("-") or "release"


def platform_bucket(platform: str) -> str:
    platform = (platform or "").strip()
    return "YouTube Community" if platform.lower() == "youtube community" else platform


def row_release(row, release_title: str, track_lookup: set[str]) -> bool:
    haystack = [
        row.get("song"),
        row.get("song_era"),
        row.get("hook"),
        row.get("content_id"),
        row.get("text"),
        row.get("notes"),
    ]
    normalized = [norm(item) for item in haystack if item]
    release_norm = norm(release_title)
    if any(release_norm and release_norm in item for item in normalized):
        return True
    return any(track and any(track in item for item in normalized) for track in track_lookup)


def release_link_count(release):
    keys = [
        "spotify_url",
        "apple_music_url",
        "youtube_music_url",
        "hyperfollow_url",
        "youtube_playlist_url",
    ]
    return sum(1 for key in keys if str(release.get(key) or "").strip())


def metric_state(manual, live):
    platforms = live.get("platforms") if isinstance(live, dict) else {}
    live_count = sum(1 for data in (platforms or {}).values() if isinstance(data, dict) and data.get("ok"))
    pending_manual = []
    pending_by_platform = {}
    auto_covered = []
    collection_steps = []
    for platform, values in (manual or {}).items():
        if not isinstance(values, dict):
            continue
        for key, value in values.items():
            if value == "pending":
                live_value = live_metric_value(platforms, platform, key)
                if live_value is not None:
                    auto_covered.append({
                        "field": f"{platform}.{key}",
                        "source": (platforms.get(platform) or {}).get("source", "live metrics"),
                        "value": live_value,
                    })
                    continue
                pending_manual.append(f"{platform}.{key}")
                pending_by_platform.setdefault(platform, []).append(key)
    pending_update_args = [f"{field}=VALUE" for field in pending_manual]
    pending_update_command = ""
    if pending_update_args:
        pending_update_command = "python3 scripts/update_manual_social_stats.py " + " ".join(pending_update_args) + " --refresh-admin"
    pending_update_by_platform = {
        platform: "python3 scripts/update_manual_social_stats.py "
        + " ".join(f"{platform}.{field}=VALUE" for field in fields)
        + " --refresh-admin"
        for platform, fields in sorted(pending_by_platform.items())
        if fields
    }
    for platform, fields in sorted(pending_by_platform.items()):
        platform_metrics = (platforms or {}).get(platform) or {}
        fields_display = ", ".join(fields)
        command = pending_update_by_platform.get(platform, "")
        reason = platform_metrics.get("reason") or platform_metrics.get("analytics_status") or metric_collection_reason(platform)
        collection_steps.append({
            "platform": platform,
            "fields": fields,
            "summary": f"{platform}: collect {fields_display}",
            "reason": reason,
            "collection_url": metric_collection_url(platform, manual, live),
            "csv_path": "data/manual_metric_collection_template.csv",
            "report_path": "admin/reports/manual-metric-collection.md",
            "worksheet_import_preview_command": "python3 scripts/update_manual_social_stats.py --from-csv --dry-run",
            "worksheet_import_command": "python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin",
            "command": command,
        })
    return {
        "live_platform_count": live_count,
        "pending_manual_fields": pending_manual,
        "pending_manual_by_platform": dict(sorted(pending_by_platform.items())),
        "pending_manual_update_command": pending_update_command,
        "pending_manual_update_by_platform": pending_update_by_platform,
        "auto_covered_fields": auto_covered,
        "manual_metric_collection_steps": collection_steps,
        "updated_at": live.get("updated_at") if isinstance(live, dict) else "",
    }


def live_metric_value(platforms, platform: str, key: str):
    data = (platforms or {}).get(platform) or {}
    metrics = data.get("metrics") or {}
    if key in metrics and metrics.get(key) not in (None, ""):
        return metrics.get(key)
    fallback_keys = {
        ("facebook", "followers"): ["page_likes"],
    }.get((platform, key), [])
    for fallback_key in fallback_keys:
        if fallback_key in metrics and metrics.get(fallback_key) not in (None, ""):
            return metrics.get(fallback_key)
    return None


def metric_collection_reason(platform: str) -> str:
    return {
        "spotify": "Spotify streams, saves, monthly listeners, and artist followers require Spotify for Artists export or connected analytics access.",
        "tiktok": "TikTok metrics require OAuth credentials or manual Creator/Business analytics export.",
        "instagram": "Instagram metrics require a connected Business/Creator account or manual insights export.",
        "x": "X metrics require an access token with user lookup/analytics access or manual export.",
        "facebook": "Facebook reach requires Page insights access or manual Meta Business Suite export.",
    }.get(platform, "Manual platform export required.")


def metric_collection_url(platform: str, manual: dict, live: dict) -> str:
    defaults = {
        "facebook": "https://business.facebook.com/latest/insights",
        "instagram": "https://www.instagram.com/professional_dashboard/",
        "spotify": "https://artists.spotify.com/",
        "tiktok": "https://www.tiktok.com/creator-center/analytics",
        "x": "https://analytics.x.com/",
    }
    manual_platform = (manual.get(platform) or {}) if isinstance(manual, dict) else {}
    live_platform = ((live.get("platforms") or {}).get(platform) or {}) if isinstance(live, dict) else {}
    for key in ("artist_url", "profile_url", "release_url", "provider_url"):
        value = str(manual_platform.get(key) or live_platform.get(key) or "").strip()
        if value:
            return value
    return defaults.get(platform, "")


def metrics_history_state(metrics_history):
    snapshots = metrics_history.get("snapshots") if isinstance(metrics_history, dict) else []
    snapshots = snapshots or []
    latest = snapshots[-1] if snapshots else {}
    previous = snapshots[-2] if len(snapshots) > 1 else {}
    return {
        "snapshot_count": len(snapshots),
        "updated_at": metrics_history.get("updated_at", "") if isinstance(metrics_history, dict) else "",
        "latest_date": latest.get("date", ""),
        "latest": latest,
        "previous_date": previous.get("date", ""),
        "delta_from_previous": latest.get("delta_from_previous", {}),
    }


def int_metric(value, default=0):
    try:
        if value in (None, ""):
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def latest_youtube_subscribers(metrics: dict, history: dict) -> int:
    latest = history.get("latest") or {}
    latest_youtube = latest.get("youtube") or {}
    live_platforms = metrics.get("platforms") if isinstance(metrics, dict) else {}
    live_youtube = ((live_platforms or {}).get("youtube") or {}).get("metrics") or {}
    return int_metric(live_youtube.get("subscribers"), int_metric(latest_youtube.get("subscribers")))


def date_value(value: str | None):
    parsed = parse_datetime(value)
    if parsed:
        return parsed.date()
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw).date()
    except ValueError:
        return None


def monetization_runway(metrics_history: dict, subscribers: int, remaining: int, target: int) -> dict:
    snapshots = []
    for snapshot in (metrics_history.get("snapshots") or []):
        youtube = snapshot.get("youtube") or {}
        snapshot_date = date_value(snapshot.get("date") or snapshot.get("captured_at"))
        if not snapshot_date:
            continue
        snapshots.append({
            "date": snapshot_date,
            "subscribers": int_metric(youtube.get("subscribers")),
        })
    if not snapshots:
        return {
            "status": "insufficient_history",
            "snapshot_count": 0,
            "window_days": 0,
            "subscriber_delta": 0,
            "subscribers_per_week": 0,
            "estimated_weeks_to_target": None,
            "required_subscribers_per_week": {
                "90_days": round(remaining / (90 / 7), 2) if remaining else 0,
                "180_days": round(remaining / (180 / 7), 2) if remaining else 0,
                "365_days": round(remaining / (365 / 7), 2) if remaining else 0,
            },
            "action_needed": "Capture at least two dated YouTube metric snapshots to calculate monetization pace.",
        }
    first = snapshots[0]
    latest = snapshots[-1]
    window_days = max((latest["date"] - first["date"]).days, 0)
    subscriber_delta = subscribers - first["subscribers"]
    subscribers_per_week = round((subscriber_delta / window_days) * 7, 2) if window_days else 0
    estimated_weeks = round(remaining / subscribers_per_week, 1) if remaining and subscribers_per_week > 0 else None
    required = {
        "90_days": round(remaining / (90 / 7), 2) if remaining else 0,
        "180_days": round(remaining / (180 / 7), 2) if remaining else 0,
        "365_days": round(remaining / (365 / 7), 2) if remaining else 0,
    }
    if remaining <= 0:
        status = "target_reached"
        action_needed = "Monetization subscriber target reached; verify partner-program eligibility requirements."
    elif len(snapshots) < 2 or window_days == 0:
        status = "insufficient_history"
        action_needed = "Capture another dated YouTube metric snapshot to calculate subscriber pace."
    elif subscribers_per_week <= 0:
        status = "stalled"
        action_needed = "Restart subscriber-growth distribution: approve draft posts, clear executor blockers, and keep weekly metrics current."
    elif subscribers_per_week < required["365_days"]:
        status = "behind_365_day_pace"
        action_needed = "Increase weekly subscriber acquisition before the channel can reach 1,000 subscribers within a year."
    elif subscribers_per_week < required["180_days"]:
        status = "behind_180_day_pace"
        action_needed = "Current growth can reach the target, but not within six months; add more approved subscriber CTAs."
    else:
        status = "on_pace"
        action_needed = "Maintain approved distribution and monitor subscriber pace every refresh."
    return {
        "status": status,
        "snapshot_count": len(snapshots),
        "first_date": first["date"].isoformat(),
        "latest_date": latest["date"].isoformat(),
        "window_days": window_days,
        "first_subscribers": first["subscribers"],
        "latest_subscribers": subscribers,
        "subscriber_delta": subscriber_delta,
        "subscribers_per_week": subscribers_per_week,
        "estimated_weeks_to_target": estimated_weeks,
        "required_subscribers_per_week": required,
        "action_needed": action_needed,
    }


def approved_queue_counts(future_posts: dict, now: datetime) -> dict:
    counts = {
        "approved_upcoming_posts": 0,
        "approved_backlog_posts": 0,
        "review_upcoming_posts": 0,
        "review_backlog_posts": 0,
    }
    for row in future_posts.get("posts") or []:
        approved = norm(row.get("approved")) == "yes"
        scheduled_at = parse_datetime(row.get("scheduled_at"))
        is_upcoming = bool(scheduled_at and scheduled_at >= now)
        if approved and is_upcoming:
            counts["approved_upcoming_posts"] += 1
        elif approved:
            counts["approved_backlog_posts"] += 1
        elif is_upcoming:
            counts["review_upcoming_posts"] += 1
        else:
            counts["review_backlog_posts"] += 1
    return counts


def monetization_state(metrics: dict, history: dict, metrics_history: dict, promo_plan: dict, future_posts: dict, execution_state: dict, now: datetime) -> dict:
    subscribers = latest_youtube_subscribers(metrics, history)
    target = YOUTUBE_MONETIZATION_SUBSCRIBER_TARGET
    remaining = max(target - subscribers, 0)
    progress = round((subscribers / target) * 100, 2) if target else 0
    runway = monetization_runway(metrics_history, subscribers, remaining, target)
    plan_summary = promo_plan.get("summary") or {}
    apply_preview = promo_plan.get("apply_preview") or {}
    queue_counts = approved_queue_counts(future_posts, now)
    approved_upcoming = queue_counts["approved_upcoming_posts"]
    review_posts = int_metric(plan_summary.get("review_posts"))
    draft_posts = int_metric(plan_summary.get("draft_posts"))
    approved_plan_posts = int_metric(plan_summary.get("approved_posts"))
    ready_to_apply = int_metric(apply_preview.get("ready_to_apply_posts"))
    approval_blockers = int_metric(execution_state.get("approval_needed_count"))
    platform_fix_blockers = int_metric(execution_state.get("platform_fix_needed_count"))
    reschedule_start = (datetime.now().astimezone() + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0).isoformat()
    reschedule_preview_command = f"python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at {shell_quote(reschedule_start)} --spacing-hours 24"
    reschedule_apply_command = reschedule_preview_command + " --apply --refresh-admin"
    next_pressure = []
    if approved_upcoming <= 0 and review_posts > 0:
        next_pressure.append("No approved upcoming posts; review draft promo queue rows to restart subscriber-growth distribution.")
    if queue_counts["approved_backlog_posts"]:
        next_pressure.append(f"{queue_counts['approved_backlog_posts']} approved unpublished posts are past their scheduled time; repair executor/platform blockers or reschedule them.")
    if approval_blockers:
        next_pressure.append(f"{approval_blockers} executor records are blocked by approval.")
    if platform_fix_blockers:
        next_pressure.append(f"{platform_fix_blockers} executor records need platform repair before they can publish.")
    if runway.get("status") in {"stalled", "behind_365_day_pace", "behind_180_day_pace"}:
        next_pressure.append(runway["action_needed"])
    return {
        "target": target,
        "current_subscribers": subscribers,
        "remaining_subscribers": remaining,
        "progress_percent": progress,
        "source": "youtube live metrics, with metrics history fallback",
        "runway": runway,
        "approved_upcoming_posts": approved_upcoming,
        "approved_backlog_posts": queue_counts["approved_backlog_posts"],
        "review_upcoming_posts": queue_counts["review_upcoming_posts"],
        "review_backlog_posts": queue_counts["review_backlog_posts"],
        "draft_review_posts": review_posts,
        "draft_posts": draft_posts,
        "approved_plan_posts": approved_plan_posts,
        "ready_to_apply_posts": ready_to_apply,
        "approval_blockers": approval_blockers,
        "platform_fix_blockers": platform_fix_blockers,
        "backlog_reschedule_preview_command": reschedule_preview_command,
        "backlog_reschedule_apply_command": reschedule_apply_command,
        "next_pressure": next_pressure,
    }


def refresh_run_state(promo_refresh_run):
    if not isinstance(promo_refresh_run, dict) or not promo_refresh_run:
        return {
            "ok": False,
            "available": False,
            "finished_at": "",
            "duration_seconds": None,
            "command_count": 0,
            "passed": 0,
            "failed": 0,
            "allowed_failures": 0,
            "action_needed": "Run python3 scripts/refresh_promo_admin.py",
        }
    summary = promo_refresh_run.get("summary") or {}
    commands = promo_refresh_run.get("commands") or promo_refresh_run.get("steps") or []
    failed_commands = [
        {
            "name": command.get("name", "unknown"),
            "required": bool(command.get("required")),
            "returncode": command.get("returncode"),
            "stderr_tail": command.get("stderr_tail") or command.get("stderr") or "",
        }
        for command in commands
        if not command.get("ok")
    ]
    return {
        "ok": bool(promo_refresh_run.get("ok")),
        "available": True,
        "safe_mode": bool(promo_refresh_run.get("safe_mode")),
        "finalized": bool(promo_refresh_run.get("finalized")),
        "finished_at": promo_refresh_run.get("finished_at", ""),
        "duration_seconds": promo_refresh_run.get("duration_seconds"),
        "command_count": int(summary.get("command_count") or summary.get("steps_run") or len(commands) or 0),
        "passed": int(summary.get("passed") or 0),
        "failed": int(summary.get("failed") or summary.get("required_failed") or 0),
        "allowed_failures": int(summary.get("allowed_failures") or summary.get("optional_failed") or 0),
        "failed_commands": failed_commands[:4],
        "action_needed": "" if promo_refresh_run.get("ok") else "Review failed promo refresh command output.",
    }


def workflow_status_state(workflow_status: dict) -> dict:
    if not isinstance(workflow_status, dict) or not workflow_status:
        return {
            "workflow_status_available": False,
            "workflow_status_ok": False,
            "latest_run_status": "",
            "latest_run_conclusion": "",
            "latest_run_updated_at": "",
            "latest_run_url": "",
            "workflow_status_action_needed": "Run python3 scripts/capture_github_workflow_status.py.",
        }
    latest = workflow_status.get("latest_run") or {}
    return {
        "workflow_status_available": True,
        "workflow_status_ok": bool(workflow_status.get("ok")),
        "latest_run_status": latest.get("status", ""),
        "latest_run_conclusion": latest.get("conclusion", ""),
        "latest_run_updated_at": latest.get("updated_at", ""),
        "latest_run_url": latest.get("html_url", ""),
        "workflow_status_action_needed": workflow_status.get("action_needed", ""),
    }


def refresh_automation_state(workflow_status: dict) -> dict:
    path = str(PROMO_REFRESH_WORKFLOW.relative_to(ROOT))
    source_url = f"{GITHUB_REPO_URL}/blob/main/{path}"
    actions_url = f"{GITHUB_REPO_URL}/actions/workflows/{PROMO_REFRESH_WORKFLOW.name}"
    workflow_state = workflow_status_state(workflow_status)
    if not PROMO_REFRESH_WORKFLOW.exists():
        return {
            "configured": False,
            "path": path,
            "source_url": source_url,
            "actions_url": actions_url,
            "cadence": "",
            "manual_dispatch": False,
            "commits_snapshots": False,
            "safe_refresh_command": "",
            "action_needed": "Add .github/workflows/promo-admin-refresh.yml.",
            **workflow_state,
        }
    text = PROMO_REFRESH_WORKFLOW.read_text(encoding="utf-8")
    match = re.search(r"cron:\s*[\"']([^\"']+)[\"']", text)
    safe_command = "python3 scripts/refresh_promo_admin.py"
    return {
        "configured": True,
        "path": path,
        "source_url": source_url,
        "actions_url": actions_url,
        "cadence": match.group(1) if match else "",
        "manual_dispatch": "workflow_dispatch:" in text,
        "commits_snapshots": "git add admin data" in text,
        "safe_refresh_command": safe_command if safe_command in text else "",
        "action_needed": "" if safe_command in text and "schedule:" in text else "Review promo admin refresh workflow configuration.",
        **workflow_state,
    }


def social_execution_state(snapshot, scheduled_rows=None):
    summary = snapshot.get("summary") if isinstance(snapshot, dict) else {}
    summary = summary or {}
    scheduled = {
        row.get("id"): row
        for row in (scheduled_rows or [])
        if row.get("id")
    }
    attention = summary.get("latest_attention") or []
    categorized_attention = dedupe_execution_rows(
        (summary.get("approval_needed") or [])
        + (summary.get("platform_fix_needed") or [])
    )
    source_rows = categorized_attention or attention
    approval_needed = []
    platform_fix_needed = []
    for item in source_rows:
        queue_row = scheduled.get(item.get("post_id"), {})
        enriched = {
            **item,
            "song": queue_row.get("song", ""),
            "approved": queue_row.get("approved", ""),
        }
        if item.get("reason") == "not_approved" or queue_row.get("approved") == "no":
            enriched["repair_action"] = "Review this queued post, set approved=yes only if it should publish, then refresh the admin queue."
            enriched["repair_command"] = f"python3 scripts/update_scheduled_post_approval.py {shell_quote(item.get('post_id', ''))} --refresh-admin"
            approval_needed.append(enriched)
        else:
            guidance = social_platform_repair_guidance(item)
            enriched.update(guidance)
            platform_fix_needed.append(enriched)
    return {
        "ok": bool(snapshot.get("ok")) if isinstance(snapshot, dict) else False,
        "updated_at": snapshot.get("updated_at", "") if isinstance(snapshot, dict) else "",
        "http_status": snapshot.get("http_status", "") if isinstance(snapshot, dict) else "",
        "execution_count": int(summary.get("execution_count") or 0),
        "posted_count": int(summary.get("posted_count") or 0),
        "attention_count": int(summary.get("attention_count") or 0),
        "approval_needed_count": len(approval_needed),
        "platform_fix_needed_count": len(platform_fix_needed),
        "status_counts": summary.get("status_counts") or {},
        "platform_counts": summary.get("platform_counts") or {},
        "latest_attention": attention,
        "approval_needed": approval_needed,
        "platform_fix_needed": platform_fix_needed,
        "action_needed": snapshot.get("action_needed", "") if isinstance(snapshot, dict) else "Run scripts/capture_social_executions.py.",
    }


def social_scheduler_dry_run_state(snapshot):
    summary = snapshot.get("summary") if isinstance(snapshot, dict) else {}
    summary = summary or {}
    return {
        "ok": bool(snapshot.get("ok")) if isinstance(snapshot, dict) else False,
        "updated_at": snapshot.get("updated_at", "") if isinstance(snapshot, dict) else "",
        "http_status": snapshot.get("http_status", "") if isinstance(snapshot, dict) else "",
        "auth_method": snapshot.get("auth_method", "") if isinstance(snapshot, dict) else "",
        "requested_scheduled_time": snapshot.get("requested_scheduled_time", "") if isinstance(snapshot, dict) else "",
        "checked_at": snapshot.get("checked_at", "") if isinstance(snapshot, dict) else "",
        "dry_run": bool(snapshot.get("dry_run")) if isinstance(snapshot, dict) else False,
        "due_count": int(summary.get("due_count") or 0),
        "result_count": int(summary.get("result_count") or 0),
        "would_post_count": int(summary.get("would_post_count") or 0),
        "blocked_count": int(summary.get("blocked_count") or 0),
        "status_counts": summary.get("status_counts") or {},
        "platform_counts": summary.get("platform_counts") or {},
        "would_post": summary.get("would_post") or [],
        "blocked": summary.get("blocked") or [],
        "action_needed": snapshot.get("action_needed", "") if isinstance(snapshot, dict) else "Run scripts/capture_scheduler_dry_run.py.",
    }


def dedupe_execution_rows(rows: list[dict]) -> list[dict]:
    seen = set()
    deduped = []
    for row in rows:
        key = row.get("post_id") or (
            row.get("platform"),
            row.get("status"),
            row.get("reason"),
            row.get("updated_at"),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def social_platform_repair_guidance(item: dict) -> dict:
    platform = str(item.get("platform") or "").strip().lower()
    error = str(item.get("error_summary") or "")
    post_id = str(item.get("post_id") or "").strip()
    if "instagram" in platform or "instagram_business_account" in error:
        return {
            "repair_action": "Reconnect the Instagram Business/Creator account to the Facebook Page or set IG_BUSINESS_ACCOUNT_ID, then push the worker secret and recapture readiness.",
            "repair_command": "python3 scripts/push_social_worker_secrets.py IG_BUSINESS_ACCOUNT_ID && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py",
        }
    if "facebook" in platform or "identity" in error:
        command = "python3 scripts/check_facebook_publishing.py --post-id "
        command += shell_quote(post_id) if post_id else "POST_ID"
        command += " --check-worker-dry-run"
        return {
            "repair_action": "Open the Facebook app as the Page admin and complete the identity confirmation prompt, then run a worker dry-run check.",
            "repair_command": command,
        }
    if "tiktok" in platform:
        return {
            "repair_action": "Add TikTok OAuth credentials and confirm public posting approval, then push TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, and TIKTOK_REFRESH_TOKEN to the worker.",
            "repair_command": "python3 scripts/push_social_worker_secrets.py TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN && python3 scripts/refresh_promo_admin.py",
        }
    return {
        "repair_action": "Review platform credentials/readiness, then rerun the social execution capture.",
        "repair_command": "LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_executor_readiness.py && LILYROO_ADMIN_PASSWORD=... python3 scripts/capture_social_executions.py",
    }


def store_service_states(release):
    status_text = " ".join(
        str(release.get(key) or "")
        for key in ("distrokid_status", "store_status", "release_date", "primary_cta")
    ).lower()
    distrokid_state = "Submitted" if any(
        word in status_text for word in ("submitted", "uploaded", "prepared", "public")
    ) else "Pending"
    services = [
        {
            "label": "DistroKid",
            "state": distrokid_state,
            "url": "",
        }
    ]
    for label, key in STORE_SERVICES:
        url = str(release.get(key) or "").strip()
        services.append({
            "label": label,
            "state": "Live" if url else "Pending",
            "url": url,
        })
    return services


def hyperfollow_guess(title: str) -> str:
    return "https://distrokid.com/hyperfollow/lilyroo/" + slugify(title)


def verification_snapshot_path(release_slug: str, service: str) -> Path:
    filename = {
        "Spotify": "spotify_release_snapshot.json",
        "Apple Music": "apple_music_release_snapshot.json",
        "YouTube Music": "youtube_music_release_snapshot.json",
        "HyperFollow": "hyperfollow_store_links_snapshot.json",
    }.get(service, "")
    if not filename:
        return Path()
    return ROOT / "data" / "store-verification" / release_slug / filename


def verification_snapshot_summary(path: Path) -> dict:
    if not path or not path.exists() or not path.is_file():
        return {}
    try:
        snapshot = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "path": str(path.relative_to(ROOT)),
            "ok": False,
            "updated_at": "",
            "summary": "Snapshot is not valid JSON.",
        }
    summary = ""
    if snapshot.get("ok"):
        summary = snapshot.get("release_url") or ", ".join(snapshot.get("stores") or []) or "public link verified"
    else:
        summary = snapshot.get("action_needed") or snapshot.get("error") or "public link not verified yet"
    return {
        "path": str(path.relative_to(ROOT)),
        "ok": bool(snapshot.get("ok")),
        "updated_at": snapshot.get("updated_at", ""),
        "summary": summary,
    }


def build_store_verification_history(release_status: dict, now: datetime) -> dict:
    rows = []
    counts = Counter()
    for release in release_status.get("releases", []):
        title = release.get("title") or "Untitled release"
        release_slug = slugify(title)
        for service in store_service_states(release):
            label = service["label"]
            if label == "DistroKid":
                continue
            snapshot = verification_snapshot_summary(verification_snapshot_path(release_slug, label))
            state = service["state"]
            if snapshot:
                if snapshot.get("ok") and state == "Pending":
                    state = "Found in snapshot"
                elif not snapshot.get("ok") and state == "Pending":
                    state = "Checked pending"
            counts[state] += 1
            rows.append({
                "release": title,
                "service": label,
                "state": state,
                "url": service.get("url", ""),
                "latest_snapshot": snapshot,
                "action": "" if state == "Live" else f"Verify {label} public URL for {title}.",
            })
    history = {
        "generated_at": now.isoformat(),
        "source": {
            "release_status": str(RELEASE_STATUS.relative_to(ROOT)),
            "store_verification_root": "data/store-verification",
        },
        "summary": {
            "total_services": len(rows),
            "live": counts.get("Live", 0),
            "submitted": counts.get("Submitted", 0),
            "pending": counts.get("Pending", 0),
            "checked_pending": counts.get("Checked pending", 0),
            "found_in_snapshot": counts.get("Found in snapshot", 0),
            "snapshot_count": sum(1 for row in rows if row.get("latest_snapshot")),
        },
        "rows": rows,
    }
    STORE_VERIFICATION_HISTORY.write_text(json.dumps(history, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return history


def store_verification_commands(release, store_services):
    title = release.get("title") or "Untitled release"
    artist = "Lily Roo"
    release_slug = slugify(title)
    output_root = f"data/store-verification/{release_slug}"
    commands = []
    for service in store_services:
        label = service["label"]
        if label in {"DistroKid", "YouTube playlist"} or service["state"] != "Pending":
            continue
        if label == "Spotify":
            command = (
                f"python3 scripts/search_spotify_release.py --artist {shell_quote(artist)} "
                f"--title {shell_quote(title)} "
                f"--out {shell_quote(output_root + '/spotify_release_snapshot.json')}"
            )
            note = "Searches public web results for Spotify album URLs, then validates exact-title candidates with Spotify oEmbed."
        elif label == "Apple Music":
            command = (
                f"python3 scripts/capture_apple_music_release.py --artist {shell_quote(artist)} "
                f"--title {shell_quote(title)} "
                f"--out {shell_quote(output_root + '/apple_music_release_snapshot.json')}"
            )
            note = "Uses the public iTunes Search API; if it finds the release, copy release_url into data/distrokid_release_status.json."
        elif label == "YouTube Music":
            command = (
                f"python3 scripts/search_youtube_music_release.py --artist {shell_quote(artist)} "
                f"--title {shell_quote(title)} "
                f"--out {shell_quote(output_root + '/youtube_music_release_snapshot.json')}"
            )
            note = "Searches public web results for YouTube Music watch URLs, then validates the public title."
        elif label == "HyperFollow":
            guessed_url = release.get("hyperfollow_url") or hyperfollow_guess(title)
            command = (
                f"python3 scripts/capture_hyperfollow_store_links.py --url {shell_quote(guessed_url)} "
                f"--out {shell_quote(output_root + '/hyperfollow_store_links_snapshot.json')}"
            )
            note = "Captures the public HyperFollow store buttons; confirm the guessed URL if DistroKid used a different slug."
        else:
            continue
        latest = verification_snapshot_summary(verification_snapshot_path(release_slug, label))
        commands.append({
            "service": label,
            "command": command,
            "note": note,
            "latest_snapshot": latest,
        })
    return commands


def store_link_action(pending_labels, verification_commands):
    if not pending_labels:
        return "Verify and add remaining public store links."
    checked = {
        command.get("service")
        for command in verification_commands
        if command.get("latest_snapshot")
    }
    labels = ", ".join(pending_labels[:4])
    if checked and set(pending_labels) <= checked:
        return f"Re-check checked-pending store links for {labels}; no public URLs were found in the latest snapshots."
    return "Verify public store links for " + labels + "."


def plan_rows_for_release(plan, release_title: str, track_lookup: set[str]):
    rows = []
    for post in plan.get("posts") or []:
        if row_release(post, release_title, track_lookup):
            rows.append(post)
    return rows


def build_status():
    now = datetime.now(timezone.utc)
    release_status = read_json(RELEASE_STATUS, {})
    manual = read_json(MANUAL_METRICS, {})
    live = read_json(LIVE_METRICS, {})
    metrics_history = read_json(METRICS_HISTORY, {})
    executor_readiness = read_json(EXECUTOR_READINESS, {})
    social_executions = read_json(SOCIAL_EXECUTIONS, {})
    social_scheduler_dry_run = read_json(SOCIAL_SCHEDULER_DRY_RUN, {})
    promo_refresh_run = read_json(PROMO_REFRESH_RUN, {})
    promo_refresh_workflow_status = read_json(PROMO_REFRESH_WORKFLOW_STATUS, {})
    promo_plan = read_json(PROMO_QUEUE_PLAN, {})
    future_posts = read_json(FUTURE_POSTS, {})
    store_history = build_store_verification_history(release_status, now)
    scheduled_rows = read_csv(SCHEDULED)
    published_rows = read_csv(PUBLISHED)
    metrics = metric_state(manual, live)
    history = metrics_history_state(metrics_history)
    refresh_run = refresh_run_state(promo_refresh_run)
    refresh_automation = refresh_automation_state(promo_refresh_workflow_status)
    execution_state = social_execution_state(social_executions, scheduled_rows)
    scheduler_state = social_scheduler_dry_run_state(social_scheduler_dry_run)
    monetization = monetization_state(live, history, metrics_history, promo_plan, future_posts, execution_state, now)
    freshness = source_freshness(release_status, manual, live, metrics_history, executor_readiness, store_history, social_executions, social_scheduler_dry_run, promo_refresh_run, promo_refresh_workflow_status, promo_plan, future_posts, now)

    releases = []
    all_actions = []
    store_state_counts = Counter()
    for release in release_status.get("releases", []):
        title = release.get("title") or "Untitled release"
        track_lookup = {norm(title)}
        track_lookup.update(norm(track) for track in RELEASE_TRACKS.get(title, []))

        queued = [row for row in scheduled_rows if row_release(row, title, track_lookup)]
        published = [row for row in published_rows if row_release(row, title, track_lookup)]
        planned = plan_rows_for_release(promo_plan, title, track_lookup)
        queued_platforms = sorted({platform_bucket(row.get("platform") or "") for row in queued if row.get("platform")})
        published_platforms = sorted({platform_bucket(row.get("platform") or "") for row in published if row.get("platform")})
        planned_platforms = sorted({platform_bucket(row.get("platform") or "") for row in planned if row.get("platform")})
        approved_plan_platforms = sorted({
            platform_bucket(row.get("platform") or "")
            for row in planned
            if row.get("platform") and str(row.get("approved") or "").lower() == "yes"
        })
        covered_platforms = set(queued_platforms) | set(published_platforms)
        missing_platforms = [platform for platform in PROMO_PLATFORMS if platform not in covered_platforms]
        planned_missing_platforms = [platform for platform in missing_platforms if platform in planned_platforms]
        unplanned_missing_platforms = [platform for platform in missing_platforms if platform not in planned_platforms]
        link_count = release_link_count(release)
        store_services = store_service_states(release)
        for service in store_services:
            store_state_counts[service["state"]] += 1
        live_store_labels = [service["label"] for service in store_services if service["state"] == "Live"]
        pending_store_labels = [service["label"] for service in store_services if service["state"] == "Pending"]
        verification_commands = store_verification_commands(release, store_services)

        actions = []
        if link_count < 3:
            actions.append(store_link_action(pending_store_labels, verification_commands))
        if not queued and planned:
            actions.append("Review and approve draft promo queue rows for this release.")
        elif not queued:
            actions.append("Create the next cross-platform promo queue for this release.")
        if approved_plan_platforms:
            actions.append("Apply approved promo plan rows and sync the future queue.")
        if planned_missing_platforms:
            actions.append("Approve planned promo coverage for " + ", ".join(planned_missing_platforms) + ".")
        if unplanned_missing_platforms:
            actions.append("Add promo coverage for " + ", ".join(unplanned_missing_platforms) + ".")
        if metrics["pending_manual_fields"]:
            actions.append("Fill manual metric worksheet and import it before weekly reporting.")

        status = "healthy"
        if actions:
            status = "needs_attention"
        if not published and not queued and planned:
            status = "planned_promo"
        elif not published and not queued:
            status = "no_active_promo"

        platform_counts = Counter(platform_bucket(row.get("platform") or "") for row in published if row.get("platform"))
        latest_published = ""
        dated = [row.get("date", "") for row in published if row.get("date")]
        if dated:
            latest_published = sorted(dated)[-1]

        release_result = {
            "title": title,
            "status": status,
            "primary_cta": release.get("primary_cta", "pending"),
            "release_date": release.get("release_date", "pending"),
            "store_link_count": link_count,
            "store_services": store_services,
            "live_store_services": live_store_labels,
            "pending_store_services": pending_store_labels,
            "store_verification_commands": verification_commands,
            "queued_posts": len(queued),
            "planned_posts": len(planned),
            "published_posts": len(published),
            "latest_published": latest_published,
            "queued_platforms": queued_platforms,
            "planned_platforms": planned_platforms,
            "approved_plan_platforms": approved_plan_platforms,
            "published_platforms": published_platforms,
            "published_platform_counts": dict(sorted(platform_counts.items())),
            "missing_platforms": missing_platforms,
            "planned_missing_platforms": planned_missing_platforms,
            "unplanned_missing_platforms": unplanned_missing_platforms,
            "actions": actions[:4],
        }
        releases.append(release_result)
        all_actions.extend(f"{title}: {action}" for action in actions)

    healthy_count = sum(1 for release in releases if release["status"] == "healthy")
    verification_command_count = sum(len(release.get("store_verification_commands") or []) for release in releases)
    store_history_summary = store_history["summary"]
    score = round((healthy_count / len(releases)) * 100) if releases else 0
    freshness_summary = freshness["summary"]
    freshness_actions = freshness["actions"]
    all_actions = freshness_actions + all_actions
    manual_metric_action = (
        "Refresh manual metrics: fill data/manual_metric_collection_template.csv, "
        "preview with python3 scripts/update_manual_social_stats.py --from-csv --dry-run, "
        "then import with python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin."
    )
    if execution_state["platform_fix_needed_count"]:
        platforms = ", ".join(sorted({
            item.get("platform", "Social")
            for item in execution_state.get("platform_fix_needed") or []
            if item.get("platform")
        }))
        all_actions.insert(0, f"Fix social executor platform failures for {platforms or 'configured platforms'}.")
    if execution_state["approval_needed_count"]:
        all_actions.insert(0, f"Review approval blockers for {execution_state['approval_needed_count']} queued executor records.")
    elif execution_state["attention_count"]:
        status_bits = ", ".join(
            f"{count} {status}"
            for status, count in sorted((execution_state.get("status_counts") or {}).items())
            if status in {"failed", "blocked", "skipped"}
        )
        all_actions.insert(0, f"Resolve social executor attention states: {status_bits or execution_state['attention_count']}.")
    for pressure in reversed(monetization["next_pressure"]):
        if pressure not in all_actions:
            all_actions.insert(0, pressure)
    if monetization.get("approved_backlog_posts") and monetization.get("backlog_reschedule_preview_command"):
        all_actions.insert(0, f"Preview approved backlog reschedule: {monetization['backlog_reschedule_preview_command']}")
    if metrics["pending_manual_fields"] and not any("--from-csv --dry-run" in action for action in all_actions[:8]):
        all_actions.insert(0, manual_metric_action)
    return {
        "generated_at": now.isoformat(),
        "source": {
            "release_status": str(RELEASE_STATUS.relative_to(ROOT)),
            "scheduled_posts": str(SCHEDULED.relative_to(ROOT)),
            "promo_queue_plan": str(PROMO_QUEUE_PLAN.relative_to(ROOT)),
            "published_log": str(PUBLISHED.relative_to(ROOT)),
            "manual_metrics": str(MANUAL_METRICS.relative_to(ROOT)),
            "live_metrics": str(LIVE_METRICS.relative_to(ROOT)),
            "metrics_history": str(METRICS_HISTORY.relative_to(ROOT)),
            "executor_readiness": str(EXECUTOR_READINESS.relative_to(ROOT)),
            "store_verification_history": str(STORE_VERIFICATION_HISTORY.relative_to(ROOT)),
            "social_executions": str(SOCIAL_EXECUTIONS.relative_to(ROOT)),
            "social_scheduler_dry_run": str(SOCIAL_SCHEDULER_DRY_RUN.relative_to(ROOT)),
            "promo_refresh_run": str(PROMO_REFRESH_RUN.relative_to(ROOT)),
            "promo_refresh_workflow_status": str(PROMO_REFRESH_WORKFLOW_STATUS.relative_to(ROOT)),
        },
        "objective": "Promote Lily Roo releases, keep lilyroo.com/admin status and metrics current, and drive YouTube monetization progress.",
        "kpi": {
            "primary": "Reach 1,000 YouTube subscribers",
            "monetization": monetization,
            "live_platform_count": metrics["live_platform_count"],
            "pending_manual_metric_fields": len(metrics["pending_manual_fields"]),
            "pending_manual_metric_details": metrics["pending_manual_fields"],
            "pending_manual_by_platform": metrics["pending_manual_by_platform"],
            "pending_manual_update_command": metrics["pending_manual_update_command"],
            "pending_manual_update_by_platform": metrics["pending_manual_update_by_platform"],
            "auto_covered_manual_metric_fields": metrics["auto_covered_fields"],
            "manual_metric_collection_steps": metrics["manual_metric_collection_steps"],
            "live_metrics_updated_at": metrics["updated_at"],
            "metrics_history": history,
            "music_site_state_counts": dict(sorted(store_state_counts.items())),
            "music_site_verification_state_counts": {
                "Live": store_history_summary.get("live", 0),
                "Submitted": store_history_summary.get("submitted", 0),
                "Pending": store_history_summary.get("pending", 0),
                "Checked pending": store_history_summary.get("checked_pending", 0),
                "Found in snapshot": store_history_summary.get("found_in_snapshot", 0),
            },
            "music_sites_live": store_history_summary.get("live", 0),
            "music_sites_submitted": store_history_summary.get("submitted", 0),
            "music_sites_pending": store_history_summary.get("pending", 0),
            "music_sites_checked_pending": store_history_summary.get("checked_pending", 0),
            "music_sites_found_in_snapshot": store_history_summary.get("found_in_snapshot", 0),
            "music_sites_missing_url": store_state_counts.get("Pending", 0),
            "store_verification_command_count": verification_command_count,
            "store_verification_history": store_history_summary,
            "social_execution_summary": execution_state,
            "social_scheduler_dry_run": scheduler_state,
            "last_refresh_run": refresh_run,
            "refresh_automation": refresh_automation,
            "stale_source_count": freshness_summary["stale"],
            "missing_source_count": freshness_summary["missing"],
        },
        "health": {
            "score": score,
            "healthy_releases": healthy_count,
            "tracked_releases": len(releases),
            "open_action_count": len(all_actions),
            "fresh_sources": freshness_summary["fresh"],
            "stale_sources": freshness_summary["stale"],
            "missing_sources": freshness_summary["missing"],
        },
        "freshness": freshness,
        "releases": releases,
        "next_actions": all_actions[:8],
    }


def main():
    status = build_status()
    OUT.write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    sync_admin_embeds(status)
    print(f"Wrote {OUT} with {len(status['releases'])} releases")


def replace_json_embed(html: str, block_id: str, payload) -> str:
    marker = f'<script type="application/json" id="{block_id}">'
    end_marker = "</script>"
    encoded = json.dumps(payload, indent=2, ensure_ascii=False)
    start = html.find(marker)
    if start == -1:
        insert_at = html.find("<script>")
        if insert_at == -1:
            return html
        block = f'{marker}{encoded}{end_marker}\n\n'
        return html[:insert_at] + block + html[insert_at:]
    content_start = start + len(marker)
    content_end = html.find(end_marker, content_start)
    if content_end == -1:
        return html
    return html[:content_start] + encoded + html[content_end:]


def sync_admin_embeds(status) -> None:
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    updated = replace_json_embed(html, "embedded-promo-engine-status", status)
    release_status = read_json(RELEASE_STATUS, {})
    updated = replace_json_embed(updated, "embedded-distrokid-release-status", release_status)
    if updated != html:
        ADMIN_INDEX.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
