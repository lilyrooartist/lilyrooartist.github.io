#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RELEASE_STATUS = ROOT / "data" / "distrokid_release_status.json"
MANUAL_METRICS = ROOT / "data" / "manual_social_stats.json"
LIVE_METRICS = ROOT / "data" / "live_social_metrics.json"
SCHEDULED = ROOT / "data" / "scheduled_posts.csv"
PROMO_QUEUE_PLAN = ROOT / "data" / "promo_queue_plan.json"
PUBLISHED = ROOT / "admin" / "content" / "Published_Log.csv"
OUT = ROOT / "data" / "promo_engine_status.json"
ADMIN_INDEX = ROOT / "admin" / "index.html"

PROMO_PLATFORMS = ["X", "Instagram", "TikTok", "Facebook", "YouTube Community"]
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


def refresh_command(name: str) -> str:
    return {
        "release_status": "python3 scripts/verify_pending_store_links.py --refresh-admin; update data/distrokid_release_status.json when a public URL is verified.",
        "scheduled_posts": "python3 scripts/sync_future_posts.py",
        "promo_queue_plan": "python3 scripts/update_promo_engine_status.py && python3 scripts/generate_promo_queue_plan.py && python3 scripts/update_promo_engine_status.py",
        "published_log": "Export or append latest published posts to admin/content/Published_Log.csv.",
        "manual_metrics": "Update data/manual_social_stats.json with latest manual metrics.",
        "live_metrics": "python3 scripts/capture_live_metrics.py",
    }.get(name, "")


def source_freshness(release_status, manual, live, promo_plan, now: datetime):
    rows = [
        freshness_row("release_status", RELEASE_STATUS, release_status, now),
        freshness_row("scheduled_posts", SCHEDULED, None, now),
        freshness_row("promo_queue_plan", PROMO_QUEUE_PLAN, promo_plan, now),
        freshness_row("published_log", PUBLISHED, None, now),
        freshness_row("manual_metrics", MANUAL_METRICS, manual, now),
        freshness_row("live_metrics", LIVE_METRICS, live, now),
    ]
    stale = [row for row in rows if row["status"] == "stale"]
    missing = [row for row in rows if row["status"] == "missing"]
    return {
        "summary": {
            "fresh": sum(1 for row in rows if row["status"] == "fresh"),
            "stale": len(stale),
            "missing": len(missing),
            "checked_at": now.isoformat(),
        },
        "sources": rows,
        "actions": [
            f"Refresh {row['name'].replace('_', ' ')}: {row['refresh_command']}"
            for row in stale + missing
        ],
    }


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
    for platform, values in (manual or {}).items():
        if not isinstance(values, dict):
            continue
        for key, value in values.items():
            if value == "pending":
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
    return {
        "live_platform_count": live_count,
        "pending_manual_fields": pending_manual,
        "pending_manual_by_platform": dict(sorted(pending_by_platform.items())),
        "pending_manual_update_command": pending_update_command,
        "pending_manual_update_by_platform": pending_update_by_platform,
        "updated_at": live.get("updated_at") if isinstance(live, dict) else "",
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
    return ROOT / "data" / "store-verification" / release_slug / filename


def verification_snapshot_summary(path: Path) -> dict:
    if not path.exists():
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
            search_url = "https://open.spotify.com/search/" + release_slug.replace("-", "%20") + "%20Lily%20Roo/albums"
            command = (
                f"open {shell_quote(search_url)} && "
                f"python3 scripts/capture_spotify_release.py --release-url SPOTIFY_ALBUM_URL "
                f"--out {shell_quote(output_root + '/spotify_release_snapshot.json')}"
            )
            note = "Search Spotify, copy the public album URL, then replace SPOTIFY_ALBUM_URL before running the capture."
        elif label == "Apple Music":
            command = (
                f"python3 scripts/capture_apple_music_release.py --artist {shell_quote(artist)} "
                f"--title {shell_quote(title)} "
                f"--out {shell_quote(output_root + '/apple_music_release_snapshot.json')}"
            )
            note = "Uses the public iTunes Search API; if it finds the release, copy release_url into data/distrokid_release_status.json."
        elif label == "YouTube Music":
            command = (
                f"python3 scripts/capture_youtube_music_release.py --url YOUTUBE_MUSIC_URL "
                f"--title {shell_quote(title)} "
                f"--out {shell_quote(output_root + '/youtube_music_release_snapshot.json')}"
            )
            note = "Replace YOUTUBE_MUSIC_URL with the public music.youtube.com/watch URL once the release appears."
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
    promo_plan = read_json(PROMO_QUEUE_PLAN, {})
    scheduled_rows = read_csv(SCHEDULED)
    published_rows = read_csv(PUBLISHED)
    metrics = metric_state(manual, live)
    freshness = source_freshness(release_status, manual, live, promo_plan, now)

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
            if pending_store_labels:
                actions.append("Verify public store links for " + ", ".join(pending_store_labels[:4]) + ".")
            else:
                actions.append("Verify and add remaining public store links.")
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
            actions.append("Refresh pending manual metrics before weekly reporting.")

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
    score = round((healthy_count / len(releases)) * 100) if releases else 0
    freshness_summary = freshness["summary"]
    freshness_actions = freshness["actions"]
    all_actions = freshness_actions + all_actions
    return {
        "generated_at": now.isoformat(),
        "source": {
            "release_status": str(RELEASE_STATUS.relative_to(ROOT)),
            "scheduled_posts": str(SCHEDULED.relative_to(ROOT)),
            "promo_queue_plan": str(PROMO_QUEUE_PLAN.relative_to(ROOT)),
            "published_log": str(PUBLISHED.relative_to(ROOT)),
            "manual_metrics": str(MANUAL_METRICS.relative_to(ROOT)),
            "live_metrics": str(LIVE_METRICS.relative_to(ROOT)),
        },
        "objective": "Promote Lily Roo releases and keep lilyroo.com/admin status and metrics current.",
        "kpi": {
            "primary": "Reach 1,000 YouTube subscribers",
            "live_platform_count": metrics["live_platform_count"],
            "pending_manual_metric_fields": len(metrics["pending_manual_fields"]),
            "pending_manual_metric_details": metrics["pending_manual_fields"],
            "pending_manual_by_platform": metrics["pending_manual_by_platform"],
            "pending_manual_update_command": metrics["pending_manual_update_command"],
            "pending_manual_update_by_platform": metrics["pending_manual_update_by_platform"],
            "live_metrics_updated_at": metrics["updated_at"],
            "music_site_state_counts": dict(sorted(store_state_counts.items())),
            "music_sites_live": store_state_counts.get("Live", 0),
            "music_sites_submitted": store_state_counts.get("Submitted", 0),
            "music_sites_pending": store_state_counts.get("Pending", 0),
            "store_verification_command_count": verification_command_count,
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
