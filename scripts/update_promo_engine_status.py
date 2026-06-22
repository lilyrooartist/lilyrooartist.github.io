#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
GITHUB_REPO_URL = "https://github.com/lilyrooartist/lilyrooartist.github.io"
RELEASE_STATUS = ROOT / "data" / "distrokid_release_status.json"
MANUAL_METRICS = ROOT / "data" / "manual_social_stats.json"
MANUAL_METRIC_PACKET = ROOT / "data" / "manual_metric_collection_packet.json"
LIVE_METRICS = ROOT / "data" / "live_social_metrics.json"
METRICS_HISTORY = ROOT / "data" / "metrics_history.json"
EXECUTOR_READINESS = ROOT / "data" / "executor_readiness_snapshot.json"
STORE_VERIFICATION_HISTORY = ROOT / "data" / "store_verification_history.json"
STORE_VERIFICATION_RUN = ROOT / "data" / "store_verification_run.json"
SOCIAL_EXECUTIONS = ROOT / "data" / "social_execution_snapshot.json"
SOCIAL_SCHEDULER_DRY_RUN = ROOT / "data" / "social_scheduler_dry_run.json"
PROMO_REFRESH_RUN = ROOT / "data" / "promo_admin_refresh_run.json"
PROMO_REFRESH_WORKFLOW_STATUS = ROOT / "data" / "promo_refresh_workflow_status.json"
PROMO_REFRESH_WORKFLOW = ROOT / ".github" / "workflows" / "promo-admin-refresh.yml"
SCHEDULED = ROOT / "data" / "scheduled_posts.csv"
PROMO_QUEUE_PLAN = ROOT / "data" / "promo_queue_plan.json"
PROMO_OPERATIONS_PACKET = ROOT / "data" / "promo_operations_packet.json"
PROMOTION_BLOCKER_LEDGER = ROOT / "data" / "promotion_blocker_ledger.json"
HUMAN_HANDOFF_PACKET = ROOT / "data" / "human_handoff_packet.json"
HUMAN_HANDOFF_RESOLUTION_PREVIEW = ROOT / "data" / "human_handoff_resolution_preview.json"
PROMO_UNLOCK_SEQUENCE = ROOT / "data" / "promo_unlock_sequence.json"
SCHEDULED_APPROVAL_PACKET = ROOT / "data" / "scheduled_approval_packet.json"
MANUAL_DISTRIBUTION_PACKET = ROOT / "data" / "manual_distribution_packet.json"
MANUAL_POSTING_CLIPBOARD = ROOT / "data" / "manual_posting_clipboard.json"
PUBLISHED_LOG_RECONCILIATION = ROOT / "data" / "published_log_reconciliation.json"
BACKLOG_RESCHEDULE_PREVIEW = ROOT / "data" / "backlog_reschedule_preview.json"
EXPERIMENT_RESULT_COLLECTION = ROOT / "data" / "experiment_result_collection_packet.json"
EXPERIMENT_RESULT_CLIPBOARD = ROOT / "data" / "experiment_result_clipboard.json"
EXPERIMENT_PUBLISH_RUNWAY = ROOT / "data" / "experiment_publish_runway.json"
PUBLISHED = ROOT / "admin" / "content" / "Published_Log.csv"
FUTURE_POSTS = ROOT / "admin" / "future-posts.json"
RESCHEDULE_SCRIPT = ROOT / "scripts" / "reschedule_scheduled_posts.py"
OUT = ROOT / "data" / "promo_engine_status.json"
ADMIN_INDEX = ROOT / "admin" / "index.html"

PROMO_PLATFORMS = ["X", "Instagram", "TikTok", "Facebook", "YouTube Community"]
YOUTUBE_MONETIZATION_SUBSCRIBER_TARGET = 1000
GROWTH_GOAL_START_DATE = "2026-06-22"
GROWTH_GOAL_DAYS = 30
GROWTH_GOAL_LIFT = 0.25
FORMAT_WINNER_COUNT = 3
MIN_MEASURED_POSTS_PER_WINNING_FORMAT = 2
MAX_EXPERIMENT_ASSETS_PER_FORMAT = 16
STORE_RECHECK_INTERVAL_HOURS = 24
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
    "manual_metric_packet": 24,
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
    row = {
        "name": name,
        "path": str(path.relative_to(ROOT)),
        "status": "fresh" if age_hours <= max_age else "stale",
        "age_hours": age_hours,
        "max_age_hours": max_age,
        "timestamp": timestamp.isoformat(),
        "refresh_command": refresh_command(name),
    }
    if name == "published_log":
        row.update(published_log_details(path))
    return row


def published_log_details(path: Path) -> dict:
    rows = read_csv(path)
    details = {
        "row_count": len(rows),
        "worker_export_preview_command": "python3 scripts/export_social_executions.py --dry-run",
        "worker_export_apply_command": "python3 scripts/export_social_executions.py --refresh-admin",
        "manual_distribution_log_command_template": "python3 scripts/log_manual_distribution.py --id MANUAL_DISTRIBUTION_ID --url PUBLIC_URL --apply --refresh-admin",
    }
    if rows:
        latest = rows[-1]
        details.update({
            "latest_entry_date": latest.get("date") or "",
            "latest_entry_platform": latest.get("platform") or "",
            "latest_entry_content_id": latest.get("content_id") or "",
            "latest_entry_url": latest.get("post_id_or_url") or "",
        })
        details["evidence"] = (
            f"{len(rows)} logged row(s); latest is {latest.get('date') or 'unknown date'} "
            f"for {latest.get('platform') or 'unknown platform'} "
            f"({latest.get('content_id') or latest.get('post_id_or_url') or 'no content id'})."
        )
    else:
        details["evidence"] = "Published log exists but contains no rows."
    return details


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


def published_log_gated_manual(row: dict, social_executions: dict, manual_distribution: dict) -> dict:
    if row.get("status") != "stale":
        return row
    execution_summary = social_executions.get("summary") or {}
    manual_summary = manual_distribution.get("summary") or {}
    unlogged_worker = int(execution_summary.get("posted_count") or 0)
    unlogged_manual = int(manual_summary.get("unlogged_manual_count") or 0)
    if unlogged_worker or not unlogged_manual:
        return row
    approval_docket = manual_distribution.get("manual_approval_docket") or {}
    distribution_docket = manual_distribution.get("manual_distribution_docket") or {}
    review_count = int(distribution_docket.get("review_count") or 0)
    postable_count = int(distribution_docket.get("postable_count") or 0)
    if not review_count and not postable_count:
        return row
    updated = dict(row)
    updated["status"] = "gated_manual_pending"
    updated["worker_unlogged_count"] = 0
    updated["manual_unlogged_count"] = unlogged_manual
    updated["manual_review_count"] = review_count
    updated["manual_postable_count"] = postable_count
    updated["manual_approval_preview_command"] = approval_docket.get("preview_command") or ""
    updated["manual_approval_apply_command"] = approval_docket.get("apply_command") or ""
    updated["public_community_url"] = manual_summary.get("public_community_url") or distribution_docket.get("public_community_url") or ""
    updated["evidence"] = (
        f"{row.get('evidence') or 'Published log is older than the freshness window.'} "
        f"No unlogged Worker posts are available; {unlogged_manual} manual row(s) are gated by review/posting before URL logging."
    )
    updated["refresh_command"] = (
        "Review and approve the manual YouTube Community rows, post them manually, then log real public URLs; "
        "Worker export has no unlogged posted records right now."
    )
    return updated


def refresh_command(name: str) -> str:
    return {
        "release_status": "python3 scripts/verify_pending_store_links.py --refresh-admin; update data/distrokid_release_status.json when a public URL is verified.",
        "scheduled_posts": "python3 scripts/sync_future_posts.py",
        "promo_queue_plan": "python3 scripts/update_promo_engine_status.py && python3 scripts/generate_promo_queue_plan.py && python3 scripts/update_promo_engine_status.py",
        "published_log": "Preview Worker export with python3 scripts/export_social_executions.py --dry-run; after review run python3 scripts/export_social_executions.py --refresh-admin. For manual posts, log the public URL with scripts/log_manual_distribution.py.",
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


def source_freshness(release_status, manual, live, metrics_history, executor_readiness, store_history, social_executions, social_scheduler_dry_run, promo_refresh_run, promo_refresh_workflow_status, promo_plan, future_posts, manual_distribution, now: datetime):
    rows = [
        release_status_checked_no_change(freshness_row("release_status", RELEASE_STATUS, release_status, now), store_history, now),
        freshness_row("scheduled_posts", FUTURE_POSTS, future_posts, now),
        freshness_row("promo_queue_plan", PROMO_QUEUE_PLAN, promo_plan, now),
        published_log_gated_manual(freshness_row("published_log", PUBLISHED, None, now), social_executions, manual_distribution),
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
    gated_manual_pending = [row for row in rows if row["status"] == "gated_manual_pending"]
    return {
        "summary": {
            "fresh": sum(1 for row in rows if row["status"] == "fresh"),
            "stale": len(stale),
            "missing": len(missing),
            "checked_no_change": len(checked_no_change),
            "gated_manual_pending": len(gated_manual_pending),
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
    if row.get("status") == "gated_manual_pending":
        command = row.get("manual_approval_preview_command") or "python3 scripts/approve_promo_queue_plan.py --all --dry-run"
        return f"Resolve manual published-log gate: review manual YouTube Community approvals with {command}, then post and log public URLs."
    if row.get("name") == "published_log":
        return (
            "Refresh published log: preview Worker-posted records with "
            "python3 scripts/export_social_executions.py --dry-run; after review run "
            "python3 scripts/export_social_executions.py --refresh-admin. For manual distribution, use "
            "python3 scripts/log_manual_distribution.py --id MANUAL_DISTRIBUTION_ID --url PUBLIC_URL --apply --refresh-admin."
        )
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


METRIC_ACCESS_LEVEL = {
    "followers": "public_profile",
    "artist_followers": "public_profile",
    "monthly_listeners": "public_profile",
    "reach_7d": "private_analytics",
    "profile_visits_7d": "private_analytics",
    "profile_views_7d": "private_analytics",
    "impressions_7d": "private_analytics",
    "release_streams": "private_analytics",
    "saves": "private_analytics",
}


def metric_state(manual, live):
    platforms = live.get("platforms") if isinstance(live, dict) else {}
    live_count = sum(1 for data in (platforms or {}).values() if isinstance(data, dict) and data.get("ok"))
    pending_manual = []
    pending_by_platform = {}
    pending_public = []
    pending_private = []
    public_capture_backlog = []
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
                field_id = f"{platform}.{key}"
                access_level = METRIC_ACCESS_LEVEL.get(key, "private_analytics")
                pending_manual.append(field_id)
                if access_level == "public_profile":
                    pending_public.append(field_id)
                    public_capture_backlog.append({
                        "field": field_id,
                        "platform": platform,
                        "metric": key,
                        "access_level": access_level,
                        "collection_url": metric_collection_url(platform, manual, live),
                        "source_hint": metric_collection_reason(platform),
                        "live_import_preview_command": "python3 scripts/update_manual_social_stats.py --from-live --dry-run",
                    })
                else:
                    pending_private.append(field_id)
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
        reason = (
            platform_metrics.get("reason")
            or platform_metrics.get("analytics_status")
            or platform_metrics.get("insights_status")
            or metric_collection_reason(platform)
        )
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
        "pending_public_metric_fields": pending_public,
        "pending_private_metric_fields": pending_private,
        "public_metric_capture_backlog": public_capture_backlog,
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


def numeric_metric(value):
    if value in (None, "", "pending"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def total_plays_views(snapshot: dict | None):
    if not isinstance(snapshot, dict):
        return None
    values = [
        (snapshot.get("youtube") or {}).get("total_views"),
        (snapshot.get("spotify") or {}).get("release_streams"),
        (snapshot.get("instagram") or {}).get("profile_visits_7d"),
        (snapshot.get("tiktok") or {}).get("profile_views_7d"),
        (snapshot.get("x") or {}).get("impressions_7d"),
        (snapshot.get("facebook") or {}).get("reach_7d"),
    ]
    numeric_values = [value for value in (numeric_metric(item) for item in values) if value is not None]
    if not numeric_values:
        return None
    return int(round(sum(numeric_values)))


def row_metric_total(row: dict) -> int:
    total = 0
    for key in ("views", "likes", "comments", "shares", "saves", "subs_delta"):
        value = numeric_metric(row.get(key))
        if value is not None:
            total += int(value)
    return total


def format_key(row: dict) -> str:
    platform = str(row.get("platform") or "Unknown platform").strip() or "Unknown platform"
    post_type = str(row.get("post_type") or "").strip()
    if not post_type:
        has_clip = bool(str(row.get("clip_url") or "").strip())
        has_image = bool(str(row.get("imagery_url") or row.get("media_key") or row.get("imagery") or "").strip())
        if platform.lower() == "youtube community":
            post_type = "community"
        elif has_clip:
            post_type = "video"
        elif has_image:
            post_type = "image"
        else:
            post_type = "text"
    cta = str(row.get("cta_type") or row.get("selected_copy_strategy") or row.get("selected_cta_strength") or "").strip()
    return " + ".join(part for part in (platform, post_type, cta) if part)


def experiment_format_key(row: dict) -> str:
    winner_format = str(row.get("winner_format") or "").strip()
    if winner_format:
        return winner_format
    platform = platform_bucket(row.get("platform") or "")
    has_clip = bool(str(row.get("clip_url") or "").strip())
    has_image = bool(str(row.get("imagery_url") or row.get("media_key") or row.get("imagery") or "").strip())
    cta = str(row.get("selected_cta_strength") or row.get("cta_type") or row.get("selected_copy_strategy") or "").strip().lower()
    hard_cta = "hard" in cta or "subscribe" in cta or "youtube" in cta
    if has_clip:
        return "Short video clip + platform-native CTA"
    if platform == "YouTube Community":
        return "YouTube Community archive/playlist CTA"
    if has_image:
        return "Release-art image + growth CTA" if hard_cta else "Release-art image + story hook"
    return "Text story hook + link CTA"


def candidate_row_id(row: dict) -> str:
    content_id = str(row.get("content_id") or row.get("id") or "").strip()
    if content_id:
        return content_id
    notes = str(row.get("notes") or "")
    for part in notes.replace(";", " ").split():
        if part.startswith("manual_distribution_id=") or part.startswith("queue_id="):
            return part.split("=", 1)[1].strip()
    return str(row.get("post_id_or_url") or "").strip()


def top_format_candidates(published_rows: list[dict], scheduled_rows: list[dict], promo_plan: dict) -> list[dict]:
    candidates: dict[str, dict] = {}
    active_rows = list(scheduled_rows) + list(promo_plan.get("posts") or [])
    active_rows_by_id = {
        candidate_row_id(row): row
        for row in active_rows
        if candidate_row_id(row)
    }
    active_formats = {
        experiment_format_key(row)
        for row in active_rows
    }

    def bucket(row: dict, source: str):
        basis_row = row
        row_id = candidate_row_id(row)
        if source == "published" and row_id in active_rows_by_id:
            basis_row = active_rows_by_id[row_id]
        key = experiment_format_key(basis_row)
        if active_formats and key not in active_formats:
            return
        candidate = candidates.setdefault(key, {
            "format": key,
            "format_basis": "experiment_format",
            "published_count": 0,
            "scheduled_count": 0,
            "planned_count": 0,
            "measured_result_total": 0,
            "measured_post_count": 0,
            "unmeasured_published_count": 0,
            "mapped_active_post_ids": [],
            "example_hooks": [],
        })
        if source == "published":
            candidate["published_count"] += 1
            metric_total = row_metric_total(row)
            if metric_total:
                candidate["measured_result_total"] += metric_total
                candidate["measured_post_count"] += 1
            else:
                candidate["unmeasured_published_count"] += 1
        elif source == "scheduled":
            candidate["scheduled_count"] += 1
        else:
            candidate["planned_count"] += 1
        if row_id and row_id not in candidate["mapped_active_post_ids"] and len(candidate["mapped_active_post_ids"]) < 5:
            candidate["mapped_active_post_ids"].append(row_id)
        hook = str(basis_row.get("hook") or basis_row.get("text") or basis_row.get("imagery") or row.get("hook") or row.get("text") or "").strip()
        if hook and hook not in candidate["example_hooks"] and len(candidate["example_hooks"]) < 2:
            candidate["example_hooks"].append(hook[:160])

    for row in scheduled_rows:
        bucket(row, "scheduled")
    for row in promo_plan.get("posts") or []:
        bucket(row, "planned")
    for row in published_rows:
        bucket(row, "published")

    ranked = []
    for candidate in candidates.values():
        measured = candidate["measured_post_count"]
        candidate["minimum_measured_posts"] = MIN_MEASURED_POSTS_PER_WINNING_FORMAT
        candidate["needed_measured_posts"] = max(MIN_MEASURED_POSTS_PER_WINNING_FORMAT - measured, 0)
        candidate["evidence_status"] = (
            "winner_ready"
            if measured >= MIN_MEASURED_POSTS_PER_WINNING_FORMAT
            else "partially_measured"
            if measured
            else "needs_result_metrics"
        )
        candidate["average_result_per_measured_post"] = (
            round(candidate["measured_result_total"] / measured, 2)
            if measured else 0
        )
        candidate["decision_note"] = (
            "Enough measured posts to compare as a repeatable format."
            if candidate["evidence_status"] == "winner_ready"
            else (
                f"Need {candidate['needed_measured_posts']} more measured post(s) before this can be called a winning format; "
                f"{candidate['unmeasured_published_count']} published post(s) in this format still need result metrics."
            )
        )
        candidate["score"] = (
            candidate["measured_result_total"] * 10
            + candidate["published_count"] * 3
            + candidate["scheduled_count"] * 2
            + candidate["planned_count"]
        )
        ranked.append(candidate)
    ranked.sort(key=lambda item: (-item["score"], item["format"]))
    return ranked[:3]


def format_winner_readiness(candidates: list[dict], result_collection: dict) -> dict:
    ready_candidates = [
        candidate for candidate in candidates
        if candidate.get("measured_post_count", 0) >= MIN_MEASURED_POSTS_PER_WINNING_FORMAT
    ]
    pending_summary = (result_collection.get("summary") or {}) if isinstance(result_collection, dict) else {}
    missing_count = int_metric(pending_summary.get("missing_published_log_count"))
    pending_fields = int_metric(pending_summary.get("pending_result_field_count"))
    ready_imports = int_metric(pending_summary.get("ready_to_import_count"))
    blockers = []
    if len(ready_candidates) < FORMAT_WINNER_COUNT:
        blockers.append(
            f"{FORMAT_WINNER_COUNT - len(ready_candidates)} more format candidate(s) need at least "
            f"{MIN_MEASURED_POSTS_PER_WINNING_FORMAT} measured posts."
        )
    if pending_fields:
        blockers.append(f"{pending_fields} post-result field(s) still need collected values.")
    if missing_count:
        blockers.append(f"{missing_count} experiment post(s) still need public URLs in Published_Log.csv.")
    return {
        "status": "ready_to_name_winners" if len(ready_candidates) >= FORMAT_WINNER_COUNT else "needs_more_result_evidence",
        "winner_count_target": FORMAT_WINNER_COUNT,
        "minimum_measured_posts_per_format": MIN_MEASURED_POSTS_PER_WINNING_FORMAT,
        "ready_candidate_count": len(ready_candidates),
        "ready_candidates": [candidate.get("format") for candidate in ready_candidates[:FORMAT_WINNER_COUNT]],
        "pending_result_field_count": pending_fields,
        "ready_to_import_count": ready_imports,
        "missing_published_log_count": missing_count,
        "blockers": blockers,
        "next_action": (
            "Name the top 3 repeatable formats from measured results."
            if len(ready_candidates) >= FORMAT_WINNER_COUNT
            else "Collect/import post results and log missing public URLs before declaring the top 3 formats."
        ),
    }


def enrich_format_decision_paths(candidates: list[dict], result_clipboard: dict) -> list[dict]:
    priorities = result_clipboard.get("measurement_priority_cards") or []
    handoff = result_clipboard.get("post_log_measurement_handoff") or {}
    handoff_ids = set(handoff.get("pending_post_ids") or [])
    by_format: dict[str, list[dict]] = {}
    for item in priorities:
        fmt = item.get("experiment_format") or "Unknown format"
        by_format.setdefault(fmt, []).append(item)
    enriched = []
    for candidate in candidates:
        item = dict(candidate)
        fmt = item.get("format") or "Unknown format"
        format_priorities = by_format.get(fmt, [])
        collect = [row for row in format_priorities if row.get("action") == "collect_metrics"]
        post_and_log = [row for row in format_priorities if row.get("action") == "post_and_log_public_url"]
        log_url = [row for row in format_priorities if row.get("action") == "log_public_url"]
        blocked = [row for row in format_priorities if row.get("action") == "clear_platform_blocker"]
        first = next(iter(collect or post_and_log or log_url or blocked), {})
        if collect:
            next_action = "Collect result metrics for logged posts."
        elif post_and_log:
            next_action = "Publish manual posts and log real public URLs."
        elif log_url:
            next_action = "Log public URLs for already-published posts."
        elif blocked:
            next_action = "Clear platform blocker before this format can produce evidence."
        else:
            next_action = "Keep publishing and refresh result collection."
        item["decision_unblock"] = {
            "status": "winner_ready" if item.get("evidence_status") == "winner_ready" else "needs_evidence",
            "next_action": next_action,
            "first_action": first.get("action") or "",
            "first_post_id": first.get("post_id") or "",
            "first_platform": first.get("platform") or "",
            "measurement_ready_count": len(collect),
            "post_and_log_count": len(post_and_log),
            "log_url_count": len(log_url),
            "blocked_count": len(blocked),
            "post_log_handoff_count": len([row for row in post_and_log if row.get("post_id") in handoff_ids]),
            "candidate_post_ids": [row.get("post_id") for row in format_priorities if row.get("post_id")],
            "preview_command": first.get("direct_preview_command_template") or first.get("log_preview_command") or "",
            "apply_command": first.get("direct_apply_command_template") or first.get("log_apply_command") or "",
            "report_path": (
                "admin/reports/experiment-result-clipboard.md"
                if collect or log_url or blocked
                else first.get("manual_posting_report") or "admin/reports/experiment-result-clipboard.md"
            ),
        }
        if item["decision_unblock"]["post_log_handoff_count"]:
            item["decision_unblock"]["handoff_report"] = "admin/reports/experiment-result-clipboard.md"
            item["decision_unblock"]["handoff_note"] = "Post-log measurement rows are prebuilt once public URLs are logged."
        enriched.append(item)
    return enriched


def metric_confidence_state(metrics: dict, freshness: dict) -> dict:
    summary = freshness.get("summary") or {}
    pending_manual = metrics.get("pending_manual_fields") or []
    pending_public = metrics.get("pending_public_metric_fields") or []
    pending_private = metrics.get("pending_private_metric_fields") or []
    stale_count = int(summary.get("stale") or 0)
    gated_manual_count = int(summary.get("gated_manual_pending") or 0)
    if pending_private:
        status = "needs_private_analytics"
        note = "Growth totals include the latest available values, but private analytics fields still need manual collection."
    elif pending_public:
        status = "needs_public_metric_capture"
        note = "Growth totals include the latest available values, but public profile metrics still need capture or import."
    elif stale_count or gated_manual_count:
        status = "source_freshness_attention"
        note = "Growth totals are available, but at least one source is stale or gated by manual URL logging."
    else:
        status = "current"
        note = "Growth totals are backed by current source snapshots and no pending manual metric fields."
    return {
        "status": status,
        "pending_manual_metric_fields": len(pending_manual),
        "pending_public_metric_fields": len(pending_public),
        "pending_private_metric_fields": len(pending_private),
        "stale_source_count": stale_count,
        "gated_manual_source_count": gated_manual_count,
        "live_platform_count": metrics.get("live_platform_count", 0),
        "manual_metric_collection_report": "admin/reports/manual-metric-collection.md",
        "manual_metric_collection_template": "data/manual_metric_collection_template.csv",
        "manual_metric_import_preview_command": "python3 scripts/update_manual_social_stats.py --from-csv --dry-run",
        "manual_metric_import_apply_command": "python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin",
        "confidence_note": note,
    }


def tracking_fields_for_platform(platform: str) -> list[str]:
    normalized = platform_bucket(platform).lower()
    if normalized == "youtube community" or normalized == "youtube":
        return ["views", "likes", "comments", "shares", "subs_delta", "youtube.total_views", "youtube.subscribers"]
    if normalized == "tiktok":
        return ["views", "likes", "comments", "shares", "saves", "tiktok.followers", "tiktok.profile_views_7d"]
    if normalized == "instagram":
        return ["views", "likes", "comments", "shares", "saves", "instagram.followers", "instagram.profile_visits_7d"]
    if normalized == "facebook":
        return ["views", "likes", "comments", "shares", "facebook.followers", "facebook.reach_7d"]
    if normalized == "x":
        return ["views", "likes", "comments", "shares", "x.followers", "x.impressions_7d"]
    return ["views", "likes", "comments", "shares", "saves", "subs_delta"]


def experiment_asset(row: dict) -> dict:
    return {
        "id": row.get("id") or row.get("post_id_or_url") or "",
        "platform": row.get("platform") or "",
        "song": row.get("song") or row.get("song_era") or "",
        "post_type": row.get("post_type") or ("video" if row.get("clip_url") else "image" if row.get("imagery_url") else "text"),
        "scheduled_at": row.get("scheduled_at") or row.get("date") or "",
        "approved": row.get("approved") or "",
        "execution_mode": row.get("execution_mode") or "",
        "imagery_url": row.get("imagery_url") or "",
        "clip_url": row.get("clip_url") or "",
        "copy": (row.get("text") or row.get("hook") or "")[:220],
        "approval_command": row.get("approval_command") or "",
    }


def active_format_experiments(scheduled_rows: list[dict], promo_plan: dict, now: datetime) -> list[dict]:
    experiments: dict[str, dict] = {}

    def add_row(row: dict, source: str):
        key = experiment_format_key(row)
        platform = row.get("platform") or ""
        experiment = experiments.setdefault(key, {
            "format": key,
            "hypothesis": f"{key} can turn existing Lily Roo release assets into measurable plays/views growth across the platforms where it fits.",
            "status": "queued_or_planned",
            "scheduled_count": 0,
            "planned_count": 0,
            "approved_count": 0,
            "blocked_count": 0,
            "platforms": [],
            "known_blockers": [],
            "assets": [],
            "tracking_fields": tracking_fields_for_platform(platform),
            "measurement_window_days": 7,
            "result_destination": "admin/content/Published_Log.csv plus data/manual_social_stats.json",
            "next_action": "",
        })
        bucketed_platform = platform_bucket(platform)
        if bucketed_platform and bucketed_platform not in experiment["platforms"]:
            experiment["platforms"].append(bucketed_platform)
        if source == "scheduled":
            experiment["scheduled_count"] += 1
        else:
            experiment["planned_count"] += 1
        if str(row.get("approved") or "").lower() == "yes":
            experiment["approved_count"] += 1
        else:
            experiment["blocked_count"] += 1
            if bucketed_platform == "TikTok":
                for blocker in ("TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REFRESH_TOKEN", "TIKTOK_PUBLIC_POSTING_APPROVED"):
                    if blocker not in experiment["known_blockers"]:
                        experiment["known_blockers"].append(blocker)
            elif row.get("approval_command"):
                blocker = "manual approval"
                if blocker not in experiment["known_blockers"]:
                    experiment["known_blockers"].append(blocker)
        if len(experiment["assets"]) < MAX_EXPERIMENT_ASSETS_PER_FORMAT:
            experiment["assets"].append(experiment_asset(row))
        experiment["tracking_fields"] = sorted(set(experiment["tracking_fields"]) | set(tracking_fields_for_platform(platform)))

    for row in scheduled_rows:
        scheduled_at = parse_datetime(row.get("scheduled_at"))
        approved = str(row.get("approved") or "").lower() == "yes"
        if approved or (scheduled_at and scheduled_at >= now - timedelta(days=7)):
            add_row(row, "scheduled")
    for row in promo_plan.get("posts") or []:
        add_row(row, "planned")

    ranked = []
    for experiment in experiments.values():
        experiment["platforms"] = sorted(experiment["platforms"])
        if experiment["approved_count"] and experiment["blocked_count"]:
            command = next((asset["approval_command"] for asset in experiment["assets"] if asset.get("approval_command")), "")
            experiment["next_action"] = (
                "Measure approved rows now; "
                + (f"review blocked variant with {command}." if command else "keep blocked variants visible until their approval/platform gate clears.")
            )
            experiment["status"] = "partially_ready"
        elif experiment["planned_count"] and experiment["blocked_count"]:
            command = next((asset["approval_command"] for asset in experiment["assets"] if asset.get("approval_command")), "")
            experiment["next_action"] = command or "Review and approve the planned row, then refresh the admin status."
            experiment["status"] = "needs_review"
        elif experiment["scheduled_count"] and experiment["approved_count"]:
            experiment["next_action"] = "Publish or confirm the scheduled row, then log public URL and 7-day result metrics."
            experiment["status"] = "ready_to_measure"
        else:
            experiment["next_action"] = "Keep this format in the experiment backlog until a publishable row exists."
            experiment["status"] = "backlog"
        experiment["score"] = (
            experiment["approved_count"] * 5
            + experiment["scheduled_count"] * 3
            + experiment["planned_count"] * 2
            - experiment["blocked_count"]
        )
        ranked.append(experiment)
    ranked.sort(key=lambda item: (-item["score"], item["format"]))
    return ranked[:3]


def growth_goal_state(metrics_history: dict, published_rows: list[dict], scheduled_rows: list[dict], promo_plan: dict, now: datetime, result_collection: dict | None = None, result_clipboard: dict | None = None, metric_confidence: dict | None = None) -> dict:
    snapshots = metrics_history.get("snapshots") if isinstance(metrics_history, dict) else []
    snapshots = snapshots or []
    latest = snapshots[-1] if snapshots else {}
    goal_start = date_value(GROWTH_GOAL_START_DATE)
    baseline_snapshot = None
    for snapshot in snapshots:
        snapshot_date = date_value(snapshot.get("date") or snapshot.get("captured_at"))
        if goal_start and snapshot_date and snapshot_date >= goal_start:
            baseline_snapshot = snapshot
            break
    baseline_policy = "first_snapshot_on_or_after_goal_start"
    if baseline_snapshot is None and snapshots:
        baseline_snapshot = latest
        baseline_policy = "latest_available_snapshot_until_goal_start_capture"
    baseline_total = total_plays_views(baseline_snapshot)
    current_total = total_plays_views(latest)
    target_total = int(round(baseline_total * (1 + GROWTH_GOAL_LIFT))) if baseline_total is not None else None
    delta = current_total - baseline_total if current_total is not None and baseline_total is not None else None
    percent_to_target = round((current_total / target_total) * 100, 2) if current_total is not None and target_total else None
    lift_percent = round((delta / baseline_total) * 100, 2) if delta is not None and baseline_total else None
    goal_end = (goal_start + timedelta(days=GROWTH_GOAL_DAYS)).isoformat() if goal_start else ""
    days_remaining = max(((goal_start + timedelta(days=GROWTH_GOAL_DAYS)) - now.date()).days, 0) if goal_start else None
    if baseline_total is None or current_total is None:
        status = "needs_baseline_metrics"
        action_needed = "Capture or import plays/views metrics so the 30-day growth target has a baseline."
    elif current_total >= target_total:
        status = "target_reached"
        action_needed = "Keep publishing and identify the winning repeatable formats from measured post results."
    elif not published_rows and not (promo_plan.get("posts") or []):
        status = "needs_distribution"
        action_needed = "Create and approve platform-native posts so the growth goal has active distribution."
    else:
        status = "in_progress"
        action_needed = "Publish or approve the next platform-native rows, then refresh manual/public metrics to rank formats by results."
    candidates = enrich_format_decision_paths(
        top_format_candidates(published_rows, scheduled_rows, promo_plan),
        result_clipboard or {},
    )
    return {
        "primary": "Grow total plays/views by 25% in 30 days",
        "goal_start_date": GROWTH_GOAL_START_DATE,
        "goal_end_date": goal_end,
        "goal_days": GROWTH_GOAL_DAYS,
        "target_lift_percent": round(GROWTH_GOAL_LIFT * 100, 2),
        "baseline_total_plays_views": baseline_total,
        "baseline_snapshot_date": (baseline_snapshot or {}).get("date", ""),
        "baseline_policy": baseline_policy,
        "current_total_plays_views": current_total,
        "target_total_plays_views": target_total,
        "delta_plays_views": delta,
        "lift_percent": lift_percent,
        "percent_to_target": percent_to_target,
        "days_remaining": days_remaining,
        "status": status,
        "action_needed": action_needed,
        "top_repeatable_format_candidates": candidates,
        "format_winner_readiness": format_winner_readiness(candidates, result_collection or {}),
        "active_format_experiments": active_format_experiments(scheduled_rows, promo_plan, now),
        "metric_confidence": metric_confidence or {},
        "metric_sources": [
            "youtube.total_views",
            "spotify.release_streams",
            "instagram.profile_visits_7d",
            "tiktok.profile_views_7d",
            "x.impressions_7d",
            "facebook.reach_7d",
        ],
    }


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
    reschedule_preview_command = f"python3 scripts/reschedule_scheduled_posts.py --approved-backlog --exclude-manual-handoff --start-at {shell_quote(reschedule_start)} --spacing-hours 24"
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
            "source_revision": {},
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
        "source_revision": promo_refresh_run.get("source_revision") or {},
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
            "latest_run_head_sha": "",
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
        "latest_run_head_sha": latest.get("head_sha", ""),
        "latest_run_updated_at": latest.get("updated_at", ""),
        "latest_run_url": latest.get("html_url", ""),
        "workflow_status_action_needed": workflow_status.get("action_needed", ""),
    }


GENERATED_REFRESH_PATHS = {
    "admin/index.html",
    "data/approval_runway.json",
    "data/backlog_reschedule_preview.json",
    "data/executor_readiness_snapshot.json",
    "data/experiment_publish_runway.json",
    "data/experiment_result_clipboard.json",
    "data/experiment_result_collection_packet.json",
    "data/experiment_result_entry_template.csv",
    "data/experiment_result_entry_wide_template.csv",
    "data/human_handoff_packet.json",
    "data/human_handoff_resolution_preview.json",
    "data/human_handoff_resolution_worksheet.csv",
    "data/live_social_metrics.json",
    "data/manual_distribution_packet.json",
    "data/manual_distribution_url_template.csv",
    "data/manual_posting_clipboard.json",
    "data/youtube_community_url_reconciliation.json",
    "data/manual_metric_collection_packet.json",
    "data/manual_metric_collection_template.csv",
    "data/manual_metric_entry_template.csv",
    "data/metrics_history.json",
    "data/monetization_activation_plan.json",
    "data/platform_repair_status.json",
    "data/promo_admin_refresh_run.json",
    "data/promo_consistency_audit.json",
    "data/promo_engine_status.json",
    "data/promo_operations_packet.json",
    "data/promo_queue_plan.json",
    "data/promo_refresh_workflow_status.json",
    "data/promo_unlock_sequence.json",
    "data/promotion_blocker_ledger.json",
    "data/published_log_reconciliation.json",
    "data/scheduled_approval_packet.json",
    "data/social_execution_snapshot.json",
    "data/social_scheduler_dry_run.json",
    "data/store_verification_history.json",
    "data/store_verification_run.json",
    "data/subscriber_cta_audit.json",
    "data/tiktok_repair_runbook.json",
    "data/tiktok_setup_preflight.json",
}

GENERATED_REFRESH_PREFIXES = (
    "admin/reports/",
    "data/manual-posting-cards/",
    "data/store-verification/",
)


def generated_refresh_path(path: str) -> bool:
    return path in GENERATED_REFRESH_PATHS or any(path.startswith(prefix) for prefix in GENERATED_REFRESH_PREFIXES)


def changed_paths_since(commit: str) -> list[str]:
    if not commit:
        return []
    output = git_output(["diff", "--name-only", f"{commit}..HEAD"])
    return [line.strip() for line in output.splitlines() if line.strip()]


def refresh_coverage_state(source_commit: str, latest_head_sha: str) -> dict:
    if not source_commit or not latest_head_sha:
        return {
            "covered": False,
            "basis": "missing_source_or_workflow_head",
            "changed_paths_since_latest_run": [],
            "uncovered_paths_since_latest_run": [],
        }
    if source_commit == latest_head_sha:
        return {
            "covered": True,
            "basis": "exact_source_commit",
            "changed_paths_since_latest_run": [],
            "uncovered_paths_since_latest_run": [],
        }
    changed = changed_paths_since(latest_head_sha)
    uncovered = [path for path in changed if not generated_refresh_path(path)]
    return {
        "covered": bool(changed and not uncovered),
        "basis": "generated_refresh_outputs_only" if changed and not uncovered else "source_changed_after_latest_run",
        "changed_paths_since_latest_run": changed[:40],
        "uncovered_paths_since_latest_run": uncovered[:20],
    }


def refresh_automation_state(workflow_status: dict) -> dict:
    source_revision = source_revision_state()
    path = str(PROMO_REFRESH_WORKFLOW.relative_to(ROOT))
    source_url = f"{GITHUB_REPO_URL}/blob/main/{path}"
    actions_url = f"{GITHUB_REPO_URL}/actions/workflows/{PROMO_REFRESH_WORKFLOW.name}"
    workflow_state = workflow_status_state(workflow_status)
    latest_head_sha = workflow_state.get("latest_run_head_sha") or ""
    source_commit = source_revision.get("commit") or ""
    coverage = refresh_coverage_state(source_commit, latest_head_sha)
    latest_covers_source = bool(coverage.get("covered"))
    current_run_capture_in_progress = (
        latest_covers_source
        and coverage.get("basis") == "exact_source_commit"
        and workflow_state.get("latest_run_status") in {"queued", "in_progress"}
        and not workflow_state.get("latest_run_conclusion")
    )
    current_run_capture_note = (
        "The workflow status snapshot was captured while the exact source refresh run was still active; "
        "use GitHub Actions as the completion authority after the run exits."
        if current_run_capture_in_progress
        else ""
    )
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
            "source_revision": source_revision,
            "latest_run_covers_source_commit": latest_covers_source,
            "latest_run_coverage_basis": coverage.get("basis", ""),
            "changed_paths_since_latest_run": coverage.get("changed_paths_since_latest_run", []),
            "uncovered_paths_since_latest_run": coverage.get("uncovered_paths_since_latest_run", []),
            "current_run_capture_in_progress": current_run_capture_in_progress,
            "current_run_capture_note": current_run_capture_note,
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
        "source_revision": source_revision,
        "latest_run_covers_source_commit": latest_covers_source,
        "latest_run_coverage_basis": coverage.get("basis", ""),
        "changed_paths_since_latest_run": coverage.get("changed_paths_since_latest_run", []),
        "uncovered_paths_since_latest_run": coverage.get("uncovered_paths_since_latest_run", []),
        "current_run_capture_in_progress": current_run_capture_in_progress,
        "current_run_capture_note": current_run_capture_note,
        "action_needed": "" if safe_command in text and "schedule:" in text else "Review promo admin refresh workflow configuration.",
        **workflow_state,
    }


def git_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def source_revision_state() -> dict:
    commit = git_output(["rev-parse", "HEAD"])
    short = git_output(["rev-parse", "--short", "HEAD"])
    branch = git_output(["branch", "--show-current"])
    commit_time = git_output(["log", "-1", "--format=%cI"])
    return {
        "commit": commit,
        "short_commit": short,
        "branch": branch,
        "committed_at": commit_time,
        "source_url": f"{GITHUB_REPO_URL}/commit/{commit}" if commit else "",
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
        + (summary.get("manual_handoff_needed") or [])
    )
    source_rows = categorized_attention or attention
    approval_needed = []
    platform_fix_needed = []
    manual_handoff_needed = []
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
        elif (
            item.get("reason") == "manual_only"
            or queue_row.get("execution_mode") == "manual"
            or queue_row.get("post_type") == "community"
        ):
            enriched["repair_action"] = "Post this row through the manual posting clipboard, then log the public URL."
            enriched["repair_command"] = "Open admin/reports/manual-posting-clipboard.md"
            manual_handoff_needed.append(enriched)
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
        "manual_handoff_needed_count": len(manual_handoff_needed),
        "status_counts": summary.get("status_counts") or {},
        "platform_counts": summary.get("platform_counts") or {},
        "latest_attention": attention,
        "approval_needed": approval_needed,
        "platform_fix_needed": platform_fix_needed,
        "manual_handoff_needed": manual_handoff_needed,
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
            "repair_action": "Add TikTok OAuth credentials, then push TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, and TIKTOK_REFRESH_TOKEN for upload-draft mode. Confirm public posting approval separately before direct public posting.",
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


def store_recheck_metadata(snapshot: dict, now: datetime) -> dict:
    checked_at = parse_datetime(snapshot.get("updated_at")) if snapshot else None
    if not checked_at:
        return {
            "checked_at": "",
            "checked_age_hours": None,
            "recheck_interval_hours": STORE_RECHECK_INTERVAL_HOURS,
            "next_recheck_at": "",
            "recheck_due": True,
            "recheck_status": "needs_first_check",
        }
    next_recheck = checked_at + timedelta(hours=STORE_RECHECK_INTERVAL_HOURS)
    age_hours = round((now - checked_at).total_seconds() / 3600, 1)
    due = now >= next_recheck
    return {
        "checked_at": checked_at.isoformat(),
        "checked_age_hours": age_hours,
        "recheck_interval_hours": STORE_RECHECK_INTERVAL_HOURS,
        "next_recheck_at": next_recheck.isoformat(),
        "recheck_due": due,
        "recheck_status": "recheck_due" if due else "waiting_for_release_propagation",
    }


def apply_store_recheck_metadata(snapshot: dict, now: datetime) -> dict:
    if not snapshot:
        return {}
    enriched = dict(snapshot)
    enriched.update(store_recheck_metadata(snapshot, now))
    return enriched


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
            snapshot = apply_store_recheck_metadata(
                verification_snapshot_summary(verification_snapshot_path(release_slug, label)),
                now,
            )
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
            "recheck_interval_hours": STORE_RECHECK_INTERVAL_HOURS,
            "recheck_due": sum(
                1 for row in rows
                if row.get("state") == "Checked pending" and (row.get("latest_snapshot") or {}).get("recheck_due")
            ),
            "waiting_for_next_recheck": sum(
                1 for row in rows
                if row.get("state") == "Checked pending" and not (row.get("latest_snapshot") or {}).get("recheck_due")
            ),
            "oldest_checked_pending_age_hours": max(
                [
                    (row.get("latest_snapshot") or {}).get("checked_age_hours")
                    for row in rows
                    if row.get("state") == "Checked pending"
                    and (row.get("latest_snapshot") or {}).get("checked_age_hours") is not None
                ] or [None]
            ),
            "next_recheck_at": min(
                [
                    (row.get("latest_snapshot") or {}).get("next_recheck_at")
                    for row in rows
                    if row.get("state") == "Checked pending"
                    and (row.get("latest_snapshot") or {}).get("next_recheck_at")
                ] or [""]
            ),
        },
        "rows": rows,
    }
    STORE_VERIFICATION_HISTORY.write_text(json.dumps(history, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return history


def store_verification_commands(release, store_services, now: datetime):
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
        latest = apply_store_recheck_metadata(
            verification_snapshot_summary(verification_snapshot_path(release_slug, label)),
            now,
        )
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


def blocker_unlock_impact(ledger: dict) -> dict:
    summary = ledger.get("summary") if isinstance(ledger, dict) else {}
    roadmap = summary.get("blocker_unlock_roadmap") or []
    projection = summary.get("next_resolution_projection") or {}
    lanes = []
    for item in roadmap:
        blockers_resolved = int_metric(item.get("blockers_resolved"))
        lanes.append({
            "id": item.get("id") or "",
            "phase": item.get("phase") or "",
            "status": item.get("status") or "",
            "owner": item.get("owner") or "",
            "blockers_resolved": blockers_resolved,
            "blocked_by": item.get("blocked_by") or [],
            "preview_command": item.get("preview_command") or "",
            "apply_command": item.get("apply_command") or "",
            "source_path": item.get("source_path") or "",
        })
    top_unlock = max(lanes, key=lambda lane: lane["blockers_resolved"], default={})
    immediate_unlock = lanes[0] if lanes else {}
    projected_after = projection.get("approval_blockers_after")
    return {
        "open_blocker_count": int_metric(summary.get("open_blocker_count")),
        "urgent_count": int_metric(summary.get("urgent_count")),
        "owner_counts": summary.get("owner_counts") or {},
        "category_counts": summary.get("category_counts") or {},
        "roadmap_step_count": len(lanes),
        "projected_resolvable_blockers": sum(lane["blockers_resolved"] for lane in lanes),
        "user_action_blocker_count": int_metric((summary.get("owner_counts") or {}).get("tod")),
        "external_blocker_count": int_metric((summary.get("owner_counts") or {}).get("external_platform")),
        "next_resolution_projection": {
            "label": projection.get("label") or "",
            "blockers_resolved": int_metric(projection.get("blockers_resolved")),
            "approval_blockers_after": int_metric(projected_after) if projected_after is not None else None,
            "preview_command": projection.get("preview_command") or "",
            "apply_command": projection.get("apply_command") or "",
            "guardrail": projection.get("guardrail") or "",
        },
        "immediate_unlock": immediate_unlock,
        "top_unlock": top_unlock,
        "lanes": lanes,
        "source_path": str(PROMOTION_BLOCKER_LEDGER.relative_to(ROOT)),
    }


def operator_docket_state(handoff: dict) -> dict:
    docket = handoff.get("action_docket") if isinstance(handoff, dict) else {}
    docket = docket or {}
    checklist = docket.get("checklist") or []
    first_ready = docket.get("first_ready_step") or next(
        (
            item
            for item in checklist
            if item.get("state") in {"ready", "ready_for_review", "needs_review", "needs_values"}
        ),
        {},
    )
    blocked_steps = docket.get("blocked_steps") or [
        item for item in checklist if item.get("state") == "blocked"
    ]
    return {
        "source_path": str(HUMAN_HANDOFF_PACKET.relative_to(ROOT)),
        "available": bool(docket),
        "ready_step_count": int_metric(docket.get("ready_step_count")),
        "blocked_step_count": int_metric(docket.get("blocked_step_count")),
        "roadmap_step_count": int_metric(docket.get("roadmap_step_count")),
        "task_count": int_metric(docket.get("task_count")),
        "manual_post_count": int_metric(docket.get("manual_post_count")),
        "manual_metric_field_count": int_metric(docket.get("manual_metric_field_count")),
        "first_ready_step": first_ready,
        "blocked_steps": blocked_steps,
        "checklist": checklist,
    }


def handoff_resolution_preview_state(preview: dict) -> dict:
    summary = preview.get("summary") if isinstance(preview, dict) else {}
    summary = summary or {}
    previews = preview.get("previews") if isinstance(preview, dict) else []
    previews = previews or []
    status_counts = summary.get("status_counts") or {}
    input_missing = [
        item for item in previews
        if item.get("preview_status") == "input_missing"
    ]
    warning = [
        item for item in previews
        if item.get("preview_status") == "preview_ok_with_warning"
    ]
    ready = [
        item for item in previews
        if item.get("preview_status") == "preview_ok"
    ]
    return {
        "source_path": str(HUMAN_HANDOFF_RESOLUTION_PREVIEW.relative_to(ROOT)),
        "available": bool(preview),
        "worksheet_row_count": int_metric(summary.get("worksheet_row_count")),
        "preview_count": int_metric(summary.get("preview_count")),
        "executed_preview_count": int_metric(summary.get("executed_preview_count")),
        "skipped_preview_count": int_metric(summary.get("skipped_preview_count")),
        "status_counts": status_counts,
        "phase_counts": summary.get("phase_counts") or {},
        "ready_preview_count": len(ready),
        "input_missing_count": len(input_missing),
        "warning_preview_count": len(warning),
        "ready_previews": ready,
        "input_missing_previews": input_missing,
        "warning_previews": warning,
        "safe_command_policy": summary.get("safe_command_policy") or "",
        "mutation_guardrail": summary.get("mutation_guardrail") or "",
    }


def handoff_resolution_preview_next_action(state: dict) -> str:
    if not state.get("available"):
        return ""
    ready_count = int_metric(state.get("ready_preview_count"))
    missing_count = int_metric(state.get("input_missing_count"))
    warning_count = int_metric(state.get("warning_preview_count"))
    parts = []
    if ready_count:
        parts.append(f"{ready_count} preview-clean")
    if missing_count:
        parts.append(f"{missing_count} missing input")
    if warning_count:
        parts.append(f"{warning_count} warning")
    if not parts:
        parts.append("no previewable rows")
    return (
        "Review handoff preview health: "
        + ", ".join(parts)
        + f"; see {state.get('source_path')}."
    )


def promo_unlock_sequence_state(sequence: dict) -> dict:
    summary = sequence.get("summary") if isinstance(sequence, dict) else {}
    summary = summary or {}
    steps = sequence.get("steps") if isinstance(sequence, dict) else []
    steps = steps or []
    current_id = summary.get("current_step_id") or ""
    current_step = next((step for step in steps if step.get("id") == current_id), steps[0] if steps else {})
    ready_steps = [step for step in steps if step.get("gate_state") == "ready_for_human_review"]
    blocked_steps = [
        step for step in steps
        if step.get("gate_state") in {"blocked", "blocked_until_input", "preview_ready_with_blocker_warning"}
    ]
    return {
        "source_path": str(PROMO_UNLOCK_SEQUENCE.relative_to(ROOT)),
        "available": bool(sequence),
        "step_count": int_metric(summary.get("step_count")),
        "ready_for_human_review_count": int_metric(summary.get("ready_for_human_review_count")),
        "blocked_or_warning_count": int_metric(summary.get("blocked_or_warning_count")),
        "total_projected_resolution_units": int_metric(summary.get("total_projected_resolution_units")),
        "open_blocker_count": int_metric(summary.get("open_blocker_count")),
        "current_step_id": current_id,
        "current_gate_state": summary.get("current_gate_state") or "",
        "current_step": current_step,
        "ready_steps": ready_steps,
        "blocked_or_warning_steps": blocked_steps,
        "operator_contract": sequence.get("operator_contract") or {},
    }


def promo_unlock_sequence_next_action(state: dict) -> str:
    if not state.get("available"):
        return ""
    current = state.get("current_step") or {}
    command = ""
    for item in current.get("commands") or []:
        if item.get("step") == "preview":
            command = item.get("command") or ""
            break
    return (
        "Current unlock gate: "
        + f"{current.get('phase') or state.get('current_step_id')} "
        + f"({state.get('current_gate_state')}); "
        + f"{int_metric(state.get('ready_for_human_review_count'))} ready, "
        + f"{int_metric(state.get('blocked_or_warning_count'))} blocked/warning"
        + (f"; preview {command}" if command else "")
        + f"; see {state.get('source_path')}."
    )


def manual_distribution_state(packet: dict) -> dict:
    summary = packet.get("summary") if isinstance(packet, dict) else {}
    summary = summary or {}
    approval_docket = packet.get("manual_approval_docket") if isinstance(packet, dict) else {}
    approval_docket = approval_docket or {}
    distribution_docket = packet.get("manual_distribution_docket") if isinstance(packet, dict) else {}
    distribution_docket = distribution_docket or {}
    completion_manifest = packet.get("manual_completion_manifest") if isinstance(packet, dict) else {}
    completion_manifest = completion_manifest or {}
    review_queue = distribution_docket.get("review_queue") or []
    postable_now = distribution_docket.get("postable_now") or []
    return {
        "source_path": str(MANUAL_DISTRIBUTION_PACKET.relative_to(ROOT)),
        "available": bool(packet),
        "status": distribution_docket.get("status") or summary.get("next_manual_action") or "unknown",
        "manual_ready_count": int_metric(summary.get("manual_ready_count")),
        "review_count": int_metric(distribution_docket.get("review_count")),
        "postable_count": int_metric(distribution_docket.get("postable_count")),
        "logged_count": int_metric(distribution_docket.get("logged_count")),
        "unlogged_manual_count": int_metric(summary.get("unlogged_manual_count")),
        "approval_ready_count": int_metric(approval_docket.get("ready_count")),
        "approval_blocked_count": int_metric(approval_docket.get("blocked_count")),
        "approval_ready_ids": approval_docket.get("ready_ids") or [],
        "approval_blocked_ids": approval_docket.get("blocked_ids") or [],
        "approval_preview_command": approval_docket.get("preview_command") or "",
        "approval_apply_command": approval_docket.get("apply_command") or "",
        "public_community_url": summary.get("public_community_url") or distribution_docket.get("public_community_url") or "",
        "review_queue": review_queue,
        "postable_now": postable_now,
        "manual_completion_manifest": completion_manifest,
        "guardrails": distribution_docket.get("guardrails") or [],
    }


def manual_posting_clipboard_state(packet: dict) -> dict:
    summary = packet.get("summary") if isinstance(packet, dict) else {}
    summary = summary or {}
    return {
        "source_path": str(MANUAL_POSTING_CLIPBOARD.relative_to(ROOT)),
        "report_path": "admin/reports/manual-posting-clipboard.md",
        "available": bool(packet),
        "status": summary.get("status") or "unknown",
        "postable_count": int_metric(summary.get("postable_count")),
        "waiting_public_url_count": int_metric(summary.get("waiting_public_url_count")),
        "public_community_url": summary.get("public_community_url") or "",
        "batch_log_preview_command": summary.get("batch_log_preview_command") or "",
        "batch_log_apply_command": summary.get("batch_log_apply_command") or "",
        "batch_log_partial_apply_command": summary.get("batch_log_partial_apply_command") or "",
        "public_url_reconciliation_status": summary.get("public_url_reconciliation_status") or "not_run",
        "public_url_reconciliation_match_count": int_metric(summary.get("public_url_reconciliation_match_count")),
        "public_url_reconciliation_command": summary.get("public_url_reconciliation_command") or "",
        "public_url_reconciliation_apply_command": summary.get("public_url_reconciliation_apply_command") or "",
        "pending_log_ids": summary.get("pending_log_ids") or [],
        "first_url_acceleration": packet.get("first_url_acceleration") or {},
        "post_cards": packet.get("post_cards") or [],
    }


def published_log_reconciliation_state(packet: dict) -> dict:
    summary = packet.get("summary") if isinstance(packet, dict) else {}
    summary = summary or {}
    manual = packet.get("manual_logging") if isinstance(packet, dict) else {}
    manual = manual or {}
    approval_gate = manual.get("approval_gate") or {}
    posting_gate = manual.get("posting_gate") or {}
    return {
        "source_path": str(PUBLISHED_LOG_RECONCILIATION.relative_to(ROOT)),
        "available": bool(packet),
        "status": summary.get("published_log_status") or "unknown",
        "reconciliation_needed": bool(summary.get("reconciliation_needed")),
        "unlogged_worker_posts": int_metric(summary.get("unlogged_worker_posts")),
        "unlogged_manual_posts": int_metric(summary.get("unlogged_manual_posts")),
        "manual_log_gate_counts": summary.get("manual_log_gate_counts") or {},
        "manual_logging_gate_status": summary.get("manual_logging_gate_status") or "",
        "next_gate": summary.get("next_gate") or "",
        "next_manual_gate": summary.get("next_manual_gate") or "",
        "url_logging_status": summary.get("url_logging_status") or "",
        "url_logging_session_file": summary.get("url_logging_session_file") or "",
        "url_logging_worksheet": summary.get("url_logging_worksheet") or "",
        "url_logging_partial_apply_command": summary.get("url_logging_partial_apply_command") or "",
        "next_preview_command": summary.get("next_preview_command") or "",
        "next_apply_command": summary.get("next_apply_command") or "",
        "approval_gate": approval_gate,
        "posting_gate": posting_gate,
        "rows": manual.get("rows") or [],
        "guardrail": manual.get("guardrail") or "",
    }


def manual_distribution_next_action(distribution: dict, reconciliation: dict, clipboard: dict | None = None) -> str:
    if not distribution.get("available") and not reconciliation.get("available"):
        return ""
    unlogged_manual = int_metric(reconciliation.get("unlogged_manual_posts")) or int_metric(distribution.get("unlogged_manual_count"))
    review_count = int_metric(distribution.get("review_count"))
    postable_count = int_metric(distribution.get("postable_count"))
    if not unlogged_manual and not review_count and not postable_count:
        return ""
    preview = reconciliation.get("next_preview_command") or distribution.get("approval_preview_command") or ""
    gate = reconciliation.get("next_gate") or distribution.get("status") or "manual_distribution"
    if review_count:
        return (
            f"Resolve manual distribution gate: {review_count} YouTube Community row(s) need review "
            f"({gate}); preview with {preview}."
        )
    if postable_count:
        clipboard_path = (clipboard or {}).get("report_path") or (clipboard or {}).get("source_path") or ""
        suffix = f" Use {clipboard_path}." if clipboard_path else ""
        return (
            f"Resolve manual distribution gate: {postable_count} approved YouTube Community row(s) need manual posting "
            f"and public URL logging; open {distribution.get('public_community_url') or 'the YouTube Community page'}."
            + suffix
        )
    return (
        f"Resolve published-log reconciliation: {unlogged_manual} manual row(s) remain gated "
        f"({gate}); preview with {preview}."
    )


def store_verification_state(store_history: dict, releases: list[dict], verification_run: dict) -> dict:
    summary = store_history.get("summary") if isinstance(store_history, dict) else {}
    summary = summary or {}
    rows = store_history.get("rows") if isinstance(store_history, dict) else []
    rows = rows or []
    checked_pending = [
        row for row in rows
        if row.get("state") == "Checked pending"
    ]
    found_in_snapshot = [
        row for row in rows
        if row.get("state") == "Found in snapshot"
    ]
    pending = [
        row for row in rows
        if row.get("state") == "Pending"
    ]
    commands = []
    for release in releases:
        title = release.get("title") or ""
        for command in release.get("store_verification_commands") or []:
            commands.append({
                "release": title,
                "service": command.get("service") or "",
                "command": command.get("command") or "",
                "latest_snapshot": command.get("latest_snapshot") or {},
                "note": command.get("note") or "",
            })
    stale_snapshots = [
        command for command in commands
        if not (command.get("latest_snapshot") or {}).get("updated_at")
    ]
    recheck_due_rows = [
        row for row in checked_pending
        if (row.get("latest_snapshot") or {}).get("recheck_due")
    ]
    waiting_recheck_rows = [
        row for row in checked_pending
        if not (row.get("latest_snapshot") or {}).get("recheck_due")
    ]
    run_summary = verification_run.get("summary") if isinstance(verification_run, dict) else {}
    run_summary = run_summary or {}
    latest_run = {
        "source_path": str(STORE_VERIFICATION_RUN.relative_to(ROOT)),
        "available": bool(verification_run),
        "updated_at": verification_run.get("updated_at", "") if isinstance(verification_run, dict) else "",
        "step_timeout_seconds": int_metric(verification_run.get("step_timeout_seconds")) if isinstance(verification_run, dict) else 0,
        "checked": int_metric(run_summary.get("checked")),
        "ok": int_metric(run_summary.get("ok")),
        "not_live_or_failed": int_metric(run_summary.get("not_live_or_failed")),
        "timed_out": int_metric(run_summary.get("timed_out")),
        "failed": int_metric(run_summary.get("failed")),
        "admin_update_ok": run_summary.get("admin_update_ok"),
        "retry_command": verification_run.get("retry_command", "") if isinstance(verification_run, dict) else "",
    }
    return {
        "source_path": str(STORE_VERIFICATION_HISTORY.relative_to(ROOT)),
        "available": bool(store_history),
        "total_services": int_metric(summary.get("total_services")),
        "live_count": int_metric(summary.get("live")),
        "pending_count": int_metric(summary.get("pending")),
        "checked_pending_count": int_metric(summary.get("checked_pending")),
        "found_in_snapshot_count": int_metric(summary.get("found_in_snapshot")),
        "snapshot_count": int_metric(summary.get("snapshot_count")),
        "verification_command_count": len(commands),
        "checked_pending_rows": checked_pending,
        "found_in_snapshot_rows": found_in_snapshot,
        "pending_rows": pending,
        "verification_commands": commands,
        "stale_snapshot_count": len(stale_snapshots),
        "recheck_interval_hours": int_metric(summary.get("recheck_interval_hours")) or STORE_RECHECK_INTERVAL_HOURS,
        "recheck_due_count": int_metric(summary.get("recheck_due")),
        "waiting_for_next_recheck_count": int_metric(summary.get("waiting_for_next_recheck")),
        "oldest_checked_pending_age_hours": summary.get("oldest_checked_pending_age_hours"),
        "next_recheck_at": summary.get("next_recheck_at") or "",
        "recheck_due_rows": recheck_due_rows,
        "waiting_recheck_rows": waiting_recheck_rows,
        "latest_run": latest_run,
        "last_run_timeout_count": int_metric(latest_run.get("timed_out")),
        "refresh_command": latest_run.get("retry_command") or "python3 scripts/verify_pending_store_links.py --refresh-admin",
        "apply_found_url_instruction": "When a public URL is verified, copy it into data/distrokid_release_status.json and refresh Admin.",
    }


def store_verification_next_action(state: dict) -> str:
    checked = int_metric(state.get("checked_pending_count"))
    found = int_metric(state.get("found_in_snapshot_count"))
    pending = int_metric(state.get("pending_count"))
    command = state.get("refresh_command") or "python3 scripts/verify_pending_store_links.py --refresh-admin"
    if found:
        return (
            f"Apply verified store URLs: {found} music site snapshot(s) found public URLs; "
            "copy them into data/distrokid_release_status.json and refresh Admin."
        )
    if checked:
        timed_out = int_metric(state.get("last_run_timeout_count"))
        timeout_note = f" Last run had {timed_out} timeout(s)." if timed_out else ""
        due_count = int_metric(state.get("recheck_due_count"))
        next_recheck = state.get("next_recheck_at") or ""
        if not due_count and next_recheck:
            return (
                f"Re-check checked-pending store links: {checked} music site snapshot(s) still have no public URL; "
                f"next recommended re-check after {next_recheck}. Run {command} then."
            )
        return (
            f"Re-check checked-pending store links: {checked} music site snapshot(s) still have no public URL; "
            f"{due_count or checked} due for re-check now; run {command}.{timeout_note}"
        )
    if pending:
        return (
            f"Verify public store links: {pending} music site(s) still need first public checks; "
            f"run {command}."
        )
    return ""


def refresh_automation_next_action(automation: dict) -> str:
    if not automation.get("configured"):
        return automation.get("action_needed") or "Configure promo admin refresh workflow."
    if automation.get("workflow_status_action_needed"):
        return f"Repair promo admin refresh workflow: {automation['workflow_status_action_needed']}"
    if automation.get("workflow_status_available") and not automation.get("latest_run_covers_source_commit"):
        source = (automation.get("source_revision") or {}).get("short_commit") or "current source"
        return (
            f"Refresh automation coverage: latest scheduled run has not covered {source}; "
            f"dispatch {automation.get('actions_url') or 'the promo admin refresh workflow'} or wait for the next scheduled run."
        )
    return ""


def manual_metric_next_action(packet: dict) -> str:
    manifest = packet.get("worksheet_import_manifest") if isinstance(packet, dict) else {}
    manifest = manifest or {}
    preview = manifest.get("preview_command") or "python3 scripts/update_manual_social_stats.py --from-csv --dry-run"
    apply_gate = manifest.get("apply_gate") or "unknown"
    ready = int_metric(manifest.get("ready_row_count"))
    waiting = int_metric(manifest.get("waiting_row_count"))
    if manifest:
        if ready:
            apply_command = manifest.get("apply_command") or "python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin"
            return (
                f"Refresh manual metrics: {ready} worksheet row(s) ready and {waiting} waiting; "
                f"preview with {preview}, then import with {apply_command}."
            )
        return (
            f"Refresh manual metrics: {waiting} worksheet row(s) still need new_value entries "
            f"({apply_gate}); preview with {preview} after filling values."
        )
    return (
        "Refresh manual metrics: fill data/manual_metric_collection_template.csv, "
        f"preview with {preview}, then import with python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin."
    )


def public_metric_capture_next_action(metrics: dict, packet: dict) -> str:
    backlog = (packet.get("public_metric_capture_backlog") or {}) if isinstance(packet, dict) else {}
    count = int_metric(backlog.get("field_count")) or len(metrics.get("public_metric_capture_backlog") or [])
    if not count:
        return ""
    return (
        f"Automate public profile metrics: {count} public-profile field(s) still need capture adapters; "
        "see data/manual_metric_collection_packet.json public_metric_capture_backlog."
    )


def experiment_result_next_action(packet: dict, clipboard: dict | None = None) -> str:
    summary = packet.get("summary") if isinstance(packet, dict) else {}
    summary = summary or {}
    pending = int_metric(summary.get("pending_result_field_count"))
    ready = int_metric(summary.get("ready_to_import_count"))
    wide_ready = int_metric(summary.get("wide_ready_to_import_count"))
    long_preview = summary.get("result_import_preview_command") or "python3 scripts/update_experiment_results.py --from-csv data/experiment_result_entry_template.csv --dry-run"
    wide_preview = summary.get("wide_result_import_preview_command") or "python3 scripts/update_experiment_results.py --from-wide-csv data/experiment_result_entry_wide_template.csv --dry-run"
    if ready:
        apply_command = summary.get("result_import_apply_command") or "python3 scripts/update_experiment_results.py --from-csv data/experiment_result_entry_template.csv --apply --refresh-admin"
        return (
            f"Import experiment results: {ready} filled result row(s) ready; "
            f"preview with {long_preview}, then apply with {apply_command}."
        )
    if wide_ready:
        apply_command = summary.get("wide_result_import_apply_command") or "python3 scripts/update_experiment_results.py --from-wide-csv data/experiment_result_entry_wide_template.csv --apply --refresh-admin"
        return (
            f"Import experiment results: {wide_ready} filled post result row(s) ready; "
            f"preview with {wide_preview}, then apply with {apply_command}."
        )
    if pending:
        report = ((clipboard or {}).get("summary") or {}).get("report_path") or "admin/reports/experiment-result-clipboard.md"
        wide_csv = summary.get("wide_entry_csv_path") or "data/experiment_result_entry_wide_template.csv"
        priority = next(iter(((clipboard or {}).get("measurement_priority_cards") or [])), {})
        if priority:
            labels = {
                "collect_metrics": "measure",
                "post_and_log_public_url": "post and log",
                "log_public_url": "log public URL for",
                "clear_platform_blocker": "clear blocker for",
            }
            priority_label = labels.get(priority.get("action"), priority.get("action") or "work on")
            priority_text = (
                f" first priority: {priority_label} {priority.get('post_id') or 'the top post'} "
                f"on {priority.get('platform') or 'its platform'}."
            )
            if priority.get("direct_preview_command_template"):
                priority_text += f" Direct preview template: {priority['direct_preview_command_template']}."
            if priority.get("direct_apply_command_template"):
                priority_text += f" Direct apply template after review: {priority['direct_apply_command_template']}."
        else:
            priority_text = ""
        return (
            f"Collect experiment results: {pending} post-result field(s) need new_value plus evidence_note; "
            f"use {report};{priority_text} Then preview import with {wide_preview} after filling {wide_csv}."
        )
    return ""


def experiment_publish_next_action(packet: dict) -> str:
    summary = packet.get("summary") if isinstance(packet, dict) else {}
    summary = summary or {}
    review_ready = int_metric(summary.get("review_ready_manual_count"))
    postable = int_metric(summary.get("postable_now_count"))
    if review_ready:
        step = next((item for item in packet.get("steps") or [] if item.get("id") == "review_manual_youtube_community"), {})
        command = step.get("preview_command") or "python3 scripts/approve_promo_queue_plan.py --dry-run"
        return f"Publish runway: {review_ready} manual YouTube Community experiment row(s) need review; preview with {command}."
    if postable:
        return f"Publish runway: {postable} approved manual row(s) are ready to post and log from data/experiment_publish_runway.json."
    return ""


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
    promo_operations = read_json(PROMO_OPERATIONS_PACKET, {})
    promotion_blockers = read_json(PROMOTION_BLOCKER_LEDGER, {})
    human_handoff = read_json(HUMAN_HANDOFF_PACKET, {})
    handoff_resolution_preview = read_json(HUMAN_HANDOFF_RESOLUTION_PREVIEW, {})
    promo_unlock_sequence = read_json(PROMO_UNLOCK_SEQUENCE, {})
    scheduled_approval = read_json(SCHEDULED_APPROVAL_PACKET, {})
    manual_distribution = read_json(MANUAL_DISTRIBUTION_PACKET, {})
    manual_posting_clipboard = read_json(MANUAL_POSTING_CLIPBOARD, {})
    published_log_reconciliation = read_json(PUBLISHED_LOG_RECONCILIATION, {})
    backlog_reschedule_preview = read_json(BACKLOG_RESCHEDULE_PREVIEW, {})
    experiment_result_collection = read_json(EXPERIMENT_RESULT_COLLECTION, {})
    experiment_result_clipboard = read_json(EXPERIMENT_RESULT_CLIPBOARD, {})
    experiment_publish_runway = read_json(EXPERIMENT_PUBLISH_RUNWAY, {})
    manual_metric_packet = read_json(MANUAL_METRIC_PACKET, {})
    store_verification_run = read_json(STORE_VERIFICATION_RUN, {})
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
    freshness = source_freshness(release_status, manual, live, metrics_history, executor_readiness, store_history, social_executions, social_scheduler_dry_run, promo_refresh_run, promo_refresh_workflow_status, promo_plan, future_posts, manual_distribution, now)
    metric_confidence = metric_confidence_state(metrics, freshness)
    growth_goal = growth_goal_state(metrics_history, published_rows, scheduled_rows, promo_plan, now, experiment_result_collection, experiment_result_clipboard, metric_confidence)

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
        verification_commands = store_verification_commands(release, store_services, now)

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
    store_verification = store_verification_state(store_history, releases, store_verification_run)
    score = round((healthy_count / len(releases)) * 100) if releases else 0
    freshness_summary = freshness["summary"]
    freshness_actions = freshness["actions"]
    all_actions = freshness_actions + all_actions
    operational_next_action = promo_operations.get("next_action") or (promo_operations.get("summary") or {}).get("next_action") or {}
    operations_action_count = int((promo_operations.get("summary") or {}).get("action_count") or 0)
    unlock_impact = blocker_unlock_impact(promotion_blockers)
    operator_docket = operator_docket_state(human_handoff)
    handoff_preview = handoff_resolution_preview_state(handoff_resolution_preview)
    unlock_sequence = promo_unlock_sequence_state(promo_unlock_sequence)
    manual_distribution = manual_distribution_state(manual_distribution)
    manual_posting_clipboard = manual_posting_clipboard_state(manual_posting_clipboard)
    published_log_reconciliation = published_log_reconciliation_state(published_log_reconciliation)
    operator_first_step = operator_docket.get("first_ready_step") or {}
    operator_first_step_text = ""
    if operator_first_step.get("label"):
        command = operator_first_step.get("preview_command") or operator_first_step.get("apply_command") or ""
        operator_first_step_text = (
            f"First handoff step: {operator_first_step['label']}"
            + (f" — {command}" if command else "")
        )
    operational_next_action_text = ""
    if operational_next_action.get("label"):
        command = operational_next_action.get("command") or ""
        operational_next_action_text = (
            f"Next operational action: {operational_next_action['label']}"
            + (f" — {command}" if command else "")
        )
    manual_metric_action = manual_metric_next_action(manual_metric_packet)
    experiment_publish_action = experiment_publish_next_action(experiment_publish_runway)
    experiment_result_action = experiment_result_next_action(experiment_result_collection, experiment_result_clipboard)
    public_metric_capture_action = public_metric_capture_next_action(metrics, manual_metric_packet)
    manual_distribution_action = manual_distribution_next_action(manual_distribution, published_log_reconciliation, manual_posting_clipboard)
    store_verification_action = store_verification_next_action(store_verification)
    refresh_automation_action = refresh_automation_next_action(refresh_automation)
    handoff_preview_action = handoff_resolution_preview_next_action(handoff_preview)
    unlock_sequence_action = promo_unlock_sequence_next_action(unlock_sequence)
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
    growth_goal_action = ""
    if growth_goal.get("action_needed") and growth_goal.get("status") != "target_reached":
        growth_goal_action = f"30-day growth goal: {growth_goal['action_needed']}"
        all_actions.insert(0, growth_goal_action)
    partial_clear = (backlog_reschedule_preview.get("partial_clear_apply_manifest") or {}) if backlog_reschedule_preview else {}
    partial_clear_preview = partial_clear.get("recommended_next_command") or ""
    if partial_clear_preview:
        all_actions.insert(0, f"Preview clear approved backlog row: {partial_clear_preview}")
    elif monetization.get("approved_backlog_posts") and monetization.get("backlog_reschedule_preview_command"):
        all_actions.insert(0, f"Preview approved backlog reschedule: {monetization['backlog_reschedule_preview_command']}")
    if metrics["pending_manual_fields"] and not any("--from-csv --dry-run" in action for action in all_actions[:8]):
        all_actions.insert(0, manual_metric_action)
    if public_metric_capture_action and public_metric_capture_action not in all_actions:
        all_actions.insert(0, public_metric_capture_action)
    if manual_distribution_action and manual_distribution_action not in all_actions:
        all_actions.insert(0, manual_distribution_action)
    if store_verification_action and store_verification_action not in all_actions:
        all_actions.insert(0, store_verification_action)
    if refresh_automation_action and refresh_automation_action not in all_actions:
        all_actions.insert(0, refresh_automation_action)
    if handoff_preview_action and handoff_preview_action not in all_actions:
        all_actions.insert(0, handoff_preview_action)
    if unlock_sequence_action and unlock_sequence_action not in all_actions:
        all_actions.insert(0, unlock_sequence_action)
    if operational_next_action_text:
        all_actions = [action for action in all_actions if action != operational_next_action_text]
        all_actions.insert(0, operational_next_action_text)
    if operator_first_step_text:
        all_actions = [action for action in all_actions if action != operator_first_step_text]
        insert_at = 1 if operational_next_action_text and all_actions[:1] == [operational_next_action_text] else 0
        all_actions.insert(insert_at, operator_first_step_text)
    if growth_goal_action:
        all_actions = [action for action in all_actions if action != growth_goal_action]
        insert_at = 2 if len(all_actions) >= 2 else len(all_actions)
        all_actions.insert(insert_at, growth_goal_action)
    if manual_distribution_action:
        all_actions = [action for action in all_actions if action != manual_distribution_action]
        insert_at = 3 if len(all_actions) >= 3 else len(all_actions)
        all_actions.insert(insert_at, manual_distribution_action)
    if experiment_publish_action:
        all_actions = [action for action in all_actions if action != experiment_publish_action]
        insert_at = 4 if len(all_actions) >= 4 else len(all_actions)
        all_actions.insert(insert_at, experiment_publish_action)
    if metrics["pending_manual_fields"]:
        all_actions = [action for action in all_actions if action != manual_metric_action]
        insert_at = 5 if len(all_actions) >= 5 else len(all_actions)
        all_actions.insert(insert_at, manual_metric_action)
    if experiment_result_action:
        all_actions = [action for action in all_actions if action != experiment_result_action]
        insert_at = 6 if len(all_actions) >= 6 else len(all_actions)
        all_actions.insert(insert_at, experiment_result_action)
    if store_verification_action:
        all_actions = [action for action in all_actions if action != store_verification_action]
        insert_at = 7 if len(all_actions) >= 7 else len(all_actions)
        all_actions.insert(insert_at, store_verification_action)
    return {
        "generated_at": now.isoformat(),
        "source": {
            "release_status": str(RELEASE_STATUS.relative_to(ROOT)),
            "scheduled_posts": str(SCHEDULED.relative_to(ROOT)),
            "promo_queue_plan": str(PROMO_QUEUE_PLAN.relative_to(ROOT)),
            "promo_operations_packet": str(PROMO_OPERATIONS_PACKET.relative_to(ROOT)),
            "promotion_blocker_ledger": str(PROMOTION_BLOCKER_LEDGER.relative_to(ROOT)),
            "human_handoff_packet": str(HUMAN_HANDOFF_PACKET.relative_to(ROOT)),
            "human_handoff_resolution_preview": str(HUMAN_HANDOFF_RESOLUTION_PREVIEW.relative_to(ROOT)),
            "promo_unlock_sequence": str(PROMO_UNLOCK_SEQUENCE.relative_to(ROOT)),
            "manual_distribution_packet": str(MANUAL_DISTRIBUTION_PACKET.relative_to(ROOT)),
            "manual_posting_clipboard": str(MANUAL_POSTING_CLIPBOARD.relative_to(ROOT)),
            "published_log_reconciliation": str(PUBLISHED_LOG_RECONCILIATION.relative_to(ROOT)),
            "experiment_result_collection": str(EXPERIMENT_RESULT_COLLECTION.relative_to(ROOT)),
            "experiment_result_clipboard": str(EXPERIMENT_RESULT_CLIPBOARD.relative_to(ROOT)),
            "experiment_publish_runway": str(EXPERIMENT_PUBLISH_RUNWAY.relative_to(ROOT)),
            "published_log": str(PUBLISHED.relative_to(ROOT)),
            "manual_metrics": str(MANUAL_METRICS.relative_to(ROOT)),
            "manual_metric_packet": str(MANUAL_METRIC_PACKET.relative_to(ROOT)),
            "live_metrics": str(LIVE_METRICS.relative_to(ROOT)),
            "metrics_history": str(METRICS_HISTORY.relative_to(ROOT)),
            "executor_readiness": str(EXECUTOR_READINESS.relative_to(ROOT)),
            "store_verification_history": str(STORE_VERIFICATION_HISTORY.relative_to(ROOT)),
            "store_verification_run": str(STORE_VERIFICATION_RUN.relative_to(ROOT)),
            "social_executions": str(SOCIAL_EXECUTIONS.relative_to(ROOT)),
            "social_scheduler_dry_run": str(SOCIAL_SCHEDULER_DRY_RUN.relative_to(ROOT)),
            "promo_refresh_run": str(PROMO_REFRESH_RUN.relative_to(ROOT)),
            "promo_refresh_workflow_status": str(PROMO_REFRESH_WORKFLOW_STATUS.relative_to(ROOT)),
        },
        "objective": "Build a repeatable Lily Roo promotion engine that turns every release, clip, and story asset into measurable audience growth.",
        "kpi": {
            "primary": growth_goal["primary"],
            "growth_goal": growth_goal,
            "secondary": "Reach 1,000 YouTube subscribers",
            "monetization": monetization,
            "live_platform_count": metrics["live_platform_count"],
            "pending_manual_metric_fields": len(metrics["pending_manual_fields"]),
            "pending_manual_metric_details": metrics["pending_manual_fields"],
            "pending_public_profile_metric_fields": len(metrics["pending_public_metric_fields"]),
            "pending_public_profile_metric_details": metrics["pending_public_metric_fields"],
            "pending_private_analytics_metric_fields": len(metrics["pending_private_metric_fields"]),
            "pending_private_analytics_metric_details": metrics["pending_private_metric_fields"],
            "public_metric_capture_backlog": manual_metric_packet.get("public_metric_capture_backlog") or {
                "status": "needs_capture_adapter" if metrics["public_metric_capture_backlog"] else "clear",
                "field_count": len(metrics["public_metric_capture_backlog"]),
                "fields": metrics["public_metric_capture_backlog"],
            },
            "pending_manual_by_platform": metrics["pending_manual_by_platform"],
            "pending_manual_update_command": metrics["pending_manual_update_command"],
            "pending_manual_update_by_platform": metrics["pending_manual_update_by_platform"],
            "auto_covered_manual_metric_fields": metrics["auto_covered_fields"],
            "manual_metric_collection_steps": metrics["manual_metric_collection_steps"],
            "manual_metric_import_manifest": manual_metric_packet.get("worksheet_import_manifest") or {},
            "manual_metric_completion_manifest": manual_metric_packet.get("metric_completion_manifest") or {},
            "live_metrics_updated_at": metrics["updated_at"],
            "metrics_history": history,
            "experiment_results": {
                "available": bool(experiment_result_collection),
                "source_path": str(EXPERIMENT_RESULT_COLLECTION.relative_to(ROOT)),
                "summary": experiment_result_collection.get("summary") or {},
                "pending_result_field_count": (experiment_result_collection.get("summary") or {}).get("pending_result_field_count", 0),
                "ready_to_import_count": (experiment_result_collection.get("summary") or {}).get("ready_to_import_count", 0),
                "missing_published_log_count": (experiment_result_collection.get("summary") or {}).get("missing_published_log_count", 0),
                "entry_csv_path": (experiment_result_collection.get("summary") or {}).get("entry_csv_path", ""),
                "wide_entry_csv_path": (experiment_result_collection.get("summary") or {}).get("wide_entry_csv_path", ""),
                "result_import_preview_command": (experiment_result_collection.get("summary") or {}).get("result_import_preview_command", ""),
                "wide_result_import_preview_command": (experiment_result_collection.get("summary") or {}).get("wide_result_import_preview_command", ""),
                "result_import_apply_command": (experiment_result_collection.get("summary") or {}).get("result_import_apply_command", ""),
                "wide_result_import_apply_command": (experiment_result_collection.get("summary") or {}).get("wide_result_import_apply_command", ""),
            },
            "experiment_result_clipboard": {
                "available": bool(experiment_result_clipboard),
                "source_path": str(EXPERIMENT_RESULT_CLIPBOARD.relative_to(ROOT)),
                "summary": experiment_result_clipboard.get("summary") or {},
                "metric_cards": experiment_result_clipboard.get("metric_cards") or [],
                "missing_public_url_cards": experiment_result_clipboard.get("missing_public_url_cards") or [],
                "measurement_priority_cards": experiment_result_clipboard.get("measurement_priority_cards") or [],
            },
            "experiment_publish_runway": {
                "available": bool(experiment_publish_runway),
                "source_path": str(EXPERIMENT_PUBLISH_RUNWAY.relative_to(ROOT)),
                "summary": experiment_publish_runway.get("summary") or {},
                "steps": experiment_publish_runway.get("steps") or [],
            },
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
            "store_verification": store_verification,
            "social_execution_summary": execution_state,
            "social_scheduler_dry_run": scheduler_state,
            "last_refresh_run": refresh_run,
            "refresh_automation": refresh_automation,
            "operational_next_action": operational_next_action,
            "unlock_impact": unlock_impact,
            "promo_unlock_sequence": unlock_sequence,
            "operator_docket": operator_docket,
            "handoff_resolution_preview": handoff_preview,
            "scheduled_approval": {
                "source_path": str(SCHEDULED_APPROVAL_PACKET.relative_to(ROOT)),
                "available": bool(scheduled_approval),
                "summary": scheduled_approval.get("summary") or {},
                "approval_decision_manifest": scheduled_approval.get("approval_decision_manifest") or {},
                "approval_apply_manifest": scheduled_approval.get("approval_apply_manifest") or {},
                "approval_review_runbook": scheduled_approval.get("approval_review_runbook") or {},
            },
            "manual_distribution": manual_distribution,
            "manual_posting_clipboard": manual_posting_clipboard,
            "published_log_reconciliation": published_log_reconciliation,
            "backlog_reschedule": {
                "source_path": str(BACKLOG_RESCHEDULE_PREVIEW.relative_to(ROOT)),
                "available": bool(backlog_reschedule_preview),
                "summary": backlog_reschedule_preview.get("summary") or {},
                "backlog_clearance_manifest": backlog_reschedule_preview.get("backlog_clearance_manifest") or {},
                "partial_clear_apply_manifest": backlog_reschedule_preview.get("partial_clear_apply_manifest") or {},
            },
            "stale_source_count": freshness_summary["stale"],
            "missing_source_count": freshness_summary["missing"],
        },
        "health": {
            "score": score,
            "healthy_releases": healthy_count,
            "tracked_releases": len(releases),
            "open_action_count": operations_action_count or len(all_actions),
            "status_queue_count": len(all_actions),
            "fresh_sources": freshness_summary["fresh"],
            "stale_sources": freshness_summary["stale"],
            "missing_sources": freshness_summary["missing"],
            "operational_next_action": operational_next_action,
            "unlock_impact": unlock_impact,
            "promo_unlock_sequence": unlock_sequence,
            "operator_docket": operator_docket,
            "handoff_resolution_preview": handoff_preview,
            "manual_distribution": manual_distribution,
            "manual_posting_clipboard": manual_posting_clipboard,
            "published_log_reconciliation": published_log_reconciliation,
            "store_verification": store_verification,
        },
        "freshness": freshness,
        "releases": releases,
        "next_actions": all_actions[:12],
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
