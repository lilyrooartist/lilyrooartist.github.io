#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
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


def norm(value: str | None) -> str:
    return " ".join(str(value or "").strip().lower().split())


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
    for platform, values in (manual or {}).items():
        if not isinstance(values, dict):
            continue
        for key, value in values.items():
            if value == "pending":
                pending_manual.append(f"{platform}.{key}")
    return {
        "live_platform_count": live_count,
        "pending_manual_fields": pending_manual,
        "updated_at": live.get("updated_at") if isinstance(live, dict) else "",
    }


def plan_rows_for_release(plan, release_title: str, track_lookup: set[str]):
    rows = []
    for post in plan.get("posts") or []:
        if row_release(post, release_title, track_lookup):
            rows.append(post)
    return rows


def build_status():
    release_status = read_json(RELEASE_STATUS, {})
    manual = read_json(MANUAL_METRICS, {})
    live = read_json(LIVE_METRICS, {})
    promo_plan = read_json(PROMO_QUEUE_PLAN, {})
    scheduled_rows = read_csv(SCHEDULED)
    published_rows = read_csv(PUBLISHED)
    metrics = metric_state(manual, live)

    releases = []
    all_actions = []
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

        actions = []
        if link_count < 3:
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
    score = round((healthy_count / len(releases)) * 100) if releases else 0
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
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
            "live_metrics_updated_at": metrics["updated_at"],
        },
        "health": {
            "score": score,
            "healthy_releases": healthy_count,
            "tracked_releases": len(releases),
            "open_action_count": len(all_actions),
        },
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
