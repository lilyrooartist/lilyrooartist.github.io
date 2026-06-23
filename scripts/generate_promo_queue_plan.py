#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import csv
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parent.parent
PROMO_STATUS = ROOT / "data" / "promo_engine_status.json"
RELEASE_STATUS = ROOT / "data" / "distrokid_release_status.json"
OUT = ROOT / "data" / "promo_queue_plan.json"
ADMIN_INDEX = ROOT / "admin" / "index.html"
SCHEDULED = ROOT / "data" / "scheduled_posts.csv"
EXECUTOR_READINESS = ROOT / "data" / "executor_readiness_snapshot.json"

TZ = ZoneInfo("America/New_York")
PLATFORM_ORDER = ["X", "Instagram", "TikTok", "Facebook", "YouTube"]
TIME_WINDOWS = {
    "X": (10, 15),
    "Instagram": (14, 5),
    "TikTok": (20, 40),
    "Facebook": (11, 20),
    "YouTube": (18, 30),
}

HARD_CTA_TERMS = ("subscribe", "subscribers", "1,000", "1000")
YOUTUBE_TERMS = ("youtube", "youtu.be", "youtube.com")

ASSET_MAP = {
    "Twelve Dollars": {
        "image": "https://www.lilyroo.com/assets/albums/twelve-dollars/art/04-twelve-dollars.jpg",
        "video": "https://www.lilyroo.com/assets/albums/twelve-dollars/video/04-twelve-dollars-youtube-remaster.mp4",
        "media_key": "twelve-dollars-cover",
        "video_key": "twelve-dollars-video",
    },
    "Analog Myth": {
        "image": "https://www.lilyroo.com/assets/albums/analog-myth/art/03-analog-myth.jpg",
        "video": "https://www.lilyroo.com/assets/albums/analog-myth/video/03-analog-myth-youtube-remaster.mp4",
        "media_key": "analog-myth-cover",
        "video_key": "analog-myth-video",
    },
    "I Learned It All in Fifteen Seconds": {
        "image": "https://www.lilyroo.com/assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg",
        "video": "https://www.lilyroo.com/assets/albums/i-learned-it-all-in-fifteen-seconds/video/01-i-learned-it-all-in-fifteen-seconds-youtube-remaster.mp4",
        "media_key": "i-learned-cover",
        "video_key": "i-learned-video",
    },
}

COPY_MAP = {
    "Twelve Dollars": {
        "hook": "A small amount of money, a large amount of stage light.",
        "x": "Twelve Dollars is the part where the stage gets too bright and the joke gets honest. Full album playlist is live.",
        "instagram": "Twelve Dollars is live on YouTube: stage lights, scattered bills, impossible shoes, and one very stubborn little signal.",
        "tiktok": "Twelve Dollars is what happens when the joke walks on stage wearing impossible shoes. Full album playlist is live.",
        "facebook": "Twelve Dollars is live in the Lily Roo archive. The remastered videos are up, the playlist is public, and the stage finally has the right kind of trouble on it.",
        "youtube": "Twelve Dollars is live in the Lily Roo archive. Subscribe and help the signal climb toward 1,000.",
        "community": "New album transmission: Twelve Dollars. Remastered videos, updated art, full playlist live now.",
    },
    "Analog Myth": {
        "hook": "Time broke, so Lily Roo made an album out of the pieces.",
        "x": "Analog Myth is the clock lying politely while the songs keep receipts. Full remastered playlist is live.",
        "instagram": "Analog Myth is a little archive of broken clocks, exposed throws, and songs that keep arriving late on purpose.",
        "tiktok": "Time broke. The songs kept moving. Analog Myth is live in the archive.",
        "facebook": "Analog Myth is live on YouTube now, with remastered videos and the album order finally lined up the way the transmission wants it.",
        "youtube": "Analog Myth is live in the Lily Roo archive. Subscribe and help the signal climb toward 1,000.",
        "community": "Analog Myth transmission is live: 13, Girls Camp, Analog Myth, Spilling the Tea, No Mortgage, Guards Down, Slow Walk, The Power of Light.",
    },
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


def slug(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().lower()).strip("-")
    return cleaned or "item"


def plan_id(title: str, platform: str) -> str:
    return f"FP-PLAN-{slug(title).upper()}-{slug(platform).upper()}"


def winner_plan_id(title: str, platform: str, format_name: str) -> str:
    return f"FP-WIN-{slug(title).upper()}-{slug(platform).upper()}-{slug(format_name).upper()}"


def story_plan_id(title: str, platform: str) -> str:
    return f"FP-STORY-{slug(title).upper()}-{slug(platform).upper()}-ARCHIVE-CTA"


def approval_command(post_id: str) -> str:
    return f"python3 scripts/approve_promo_queue_plan.py --id {post_id} --refresh-admin"


def approval_scope_command(*, release: str = "", platform: str = "", all_posts: bool = False) -> str:
    parts = ["python3", "scripts/approve_promo_queue_plan.py"]
    if all_posts:
        parts.append("--all")
    if release:
        parts.extend(["--release", json.dumps(release)])
    if platform:
        parts.extend(["--platform", json.dumps(platform)])
    parts.append("--refresh-admin")
    return " ".join(parts)


def apply_command() -> str:
    return "python3 scripts/apply_promo_queue_plan.py --apply --refresh-admin"


def apply_scope_command(*, release: str = "", platform: str = "") -> str:
    parts = ["python3", "scripts/apply_promo_queue_plan.py", "--apply"]
    if release:
        parts.extend(["--release", json.dumps(release)])
    if platform:
        parts.extend(["--platform", json.dumps(platform)])
    parts.append("--refresh-admin")
    return " ".join(parts)


def prior_approval_lookup(plan):
    by_id = {}
    by_slot = {}
    for post in plan.get("posts") or []:
        approved = "yes" if str(post.get("approved") or "").lower() == "yes" else "no"
        by_id[str(post.get("id") or "")] = approved
        key = (
            str(post.get("song") or "").strip().lower(),
            str(post.get("platform") or "").strip().lower(),
            str(post.get("post_type") or "").strip().lower(),
        )
        by_slot[key] = approved
    return by_id, by_slot


def preserved_approval(by_id, by_slot, post):
    post_id = str(post.get("id") or "")
    if by_id.get(post_id) == "yes":
        return "yes"
    key = (
        str(post.get("song") or "").strip().lower(),
        str(post.get("platform") or "").strip().lower(),
        str(post.get("post_type") or "").strip().lower(),
    )
    return "yes" if by_slot.get(key) == "yes" else "no"


def first_future_slot(index: int, platform: str) -> str:
    now = datetime.now(TZ)
    base = now.date() + timedelta(days=1 + index)
    hour, minute = TIME_WINDOWS.get(platform, (12, 0))
    return datetime(base.year, base.month, base.day, hour, minute, tzinfo=TZ).isoformat()


def release_lookup(status):
    return {release.get("title"): release for release in status.get("releases", [])}


def cta_url(release):
    for key in ("spotify_url", "youtube_playlist_url", "youtube_music_url", "apple_music_url", "hyperfollow_url"):
        value = str(release.get(key) or "").strip()
        if value:
            return value
    return "https://www.lilyroo.com/music.html"


def cta_text(release):
    url = cta_url(release)
    if "spotify.com" in url:
        return f"Stream: {url}"
    if "youtube.com/playlist" in url:
        return f"Full playlist: {url}"
    if "music.youtube.com" in url:
        return f"YouTube Music: {url}"
    return f"Listen: {url}"


def post_type(platform):
    if platform in {"TikTok", "YouTube"}:
        return "video"
    return "image"


def execution_mode(platform):
    return "auto"


def copy_for(title, platform):
    copy = COPY_MAP.get(title, {})
    key = platform.lower()
    return copy.get(key) or f"{title} is live in the Lily Roo archive."


def winner_story_copy(title: str, platform: str) -> str:
    copy = COPY_MAP.get(title, {})
    if platform == "X":
        return copy.get("x") or copy.get("hook") or f"{title} is live in the Lily Roo archive."
    if platform == "Facebook":
        return copy.get("facebook") or copy.get("hook") or f"{title} is live in the Lily Roo archive."
    if platform == "Instagram":
        return copy.get("instagram") or copy.get("hook") or f"{title} is live in the Lily Roo archive."
    return copy_for(title, platform)


def draft_variants(title, platform):
    copy = COPY_MAP.get(title, {})
    base = copy_for(title, platform)
    hook = copy.get("hook", f"{title} is live in the archive.")
    return [
        base,
        f"{hook} Full signal on YouTube.",
        f"{title} is part of the Lily Roo archive now. Help us build the signal to 1,000 subscribers.",
    ]


def cta_strength(text: str) -> str:
    lower = str(text or "").lower()
    has_hard = any(term in lower for term in HARD_CTA_TERMS)
    has_youtube = any(term in lower for term in YOUTUBE_TERMS)
    if has_hard and has_youtube:
        return "hard_subscribe"
    if has_hard:
        return "hard_goal"
    if has_youtube:
        return "youtube_link"
    if "playlist" in lower or "stream" in lower or "listen" in lower:
        return "soft_listen"
    return "missing"


def score_strength(strength: str) -> int:
    return {
        "hard_subscribe": 4,
        "hard_goal": 3,
        "youtube_link": 2,
        "soft_listen": 1,
        "missing": 0,
    }.get(strength, 0)


def selected_growth_copy(variants: list[str]) -> tuple[str, str]:
    best_text = ""
    best_strength = "missing"
    for variant in variants:
        strength = cta_strength(variant)
        if score_strength(strength) > score_strength(best_strength):
            best_text = variant
            best_strength = strength
    if best_text:
        return best_text, best_strength
    return "", "missing"


def winner_ready_formats(promo: dict) -> list[dict]:
    candidates = (((promo.get("kpi") or {}).get("growth_goal") or {}).get("top_repeatable_format_candidates") or [])
    return [
        candidate
        for candidate in candidates
        if candidate.get("evidence_status") == "winner_ready"
    ]


def ready_platforms(readiness: dict) -> set[str]:
    summary = readiness.get("summary") or {}
    platform_map = summary.get("platforms") or {}
    return {platform for platform, ready in platform_map.items() if ready}


def winner_platforms(format_name: str, readiness: dict) -> list[str]:
    ready = ready_platforms(readiness)
    if format_name == "Release-art image + story hook":
        return [platform for platform in ("X", "Facebook", "Instagram") if platform in ready]
    if format_name == "YouTube Community archive/playlist CTA":
        return ["YouTube"] if "YouTube" in ready or "YouTube Community" in ready else []
    return []


def release_platform_type_key(row: dict) -> tuple[str, str, str]:
    return (
        str(row.get("song") or "").strip().lower(),
        str(row.get("platform") or "").strip().lower(),
        str(row.get("post_type") or "").strip().lower(),
    )


def scheduled_release_platform_type_keys(rows: list[dict]) -> set[tuple[str, str, str]]:
    return {release_platform_type_key(row) for row in rows}


def winner_followup_posts(*, promo: dict, releases: dict, readiness: dict, scheduled_rows: list[dict], existing_posts: list[dict], start_index: int, prior_by_id: dict, prior_by_slot: dict) -> list[dict]:
    scheduled_keys = scheduled_release_platform_type_keys(scheduled_rows)
    planned_keys = scheduled_release_platform_type_keys(existing_posts)
    posts = []
    post_index = start_index
    release_titles = [title for title in ("Twelve Dollars", "Analog Myth", "I Learned It All in Fifteen Seconds") if title in releases]

    for candidate in winner_ready_formats(promo):
        format_name = candidate.get("format") or ""
        for title in release_titles:
            assets = ASSET_MAP.get(title, {})
            release = releases.get(title, {"title": title})
            for platform in winner_platforms(format_name, readiness):
                kind = post_type(platform)
                key = (title.lower(), platform.lower(), kind)
                if key in scheduled_keys or key in planned_keys:
                    continue
                media_url = assets.get("video" if kind == "video" else "image", "")
                media_key = assets.get("video_key" if kind == "video" else "media_key", "")
                if not media_url and not media_key:
                    continue
                draft_id = winner_plan_id(title, platform, format_name)
                base = winner_story_copy(title, platform)
                hook = (COPY_MAP.get(title, {}) or {}).get("hook", f"{title} is live in the archive.")
                selected_text = f"{title} is part of the Lily Roo archive now. Help us build the signal to 1,000 subscribers."
                drafts = [
                    selected_text,
                    base,
                    f"{hook} The archive version is live now.",
                ]
                post = {
                    "id": draft_id,
                    "scheduled_at": first_future_slot(post_index, platform),
                    "platform": platform,
                    "song": title,
                    "imagery": f"{title} winner-format follow-up",
                    "imagery_url": assets.get("image", "") if kind == "video" else media_url,
                    "clip_url": media_url if kind == "video" else "",
                    "text": selected_text,
                    "drafts": drafts,
                    "reply_text": cta_text(release),
                    "selected_cta_strength": "hard_goal",
                    "selected_copy_strategy": "growth_first_subscriber_cta",
                    "winner_format": format_name,
                    "winner_format_replication_note": "The row reuses release-art imagery from the measured winner while preserving the queue-wide subscriber-growth CTA gate.",
                    "winner_format_evidence_status": candidate.get("evidence_status") or "",
                    "winner_format_average_result": candidate.get("average_result_per_measured_post", 0),
                    "x_media_key": "",
                    "media_key": media_key,
                    "approved": "no",
                    "execution_mode": execution_mode(platform),
                    "post_type": kind,
                    "desired_privacy": "public" if platform == "YouTube" else "",
                    "reason": f"Replicate winner-ready format '{format_name}' on a ready platform while blocked channels stay visible.",
                    "approval_command": approval_command(draft_id),
                }
                post["approved"] = preserved_approval(prior_by_id, prior_by_slot, post)
                posts.append(post)
                planned_keys.add(key)
                post_index += 1
    return posts


def story_text_followup_posts(*, releases: dict, readiness: dict, scheduled_rows: list[dict], existing_posts: list[dict], start_index: int, prior_by_id: dict, prior_by_slot: dict) -> list[dict]:
    ready = ready_platforms(readiness)
    platforms = [platform for platform in ("X", "Facebook") if platform in ready]
    if not platforms:
        return []
    scheduled_keys = scheduled_release_platform_type_keys(scheduled_rows)
    planned_keys = scheduled_release_platform_type_keys(existing_posts)
    posts = []
    post_index = start_index
    release_titles = [title for title in ("Twelve Dollars", "Analog Myth", "I Learned It All in Fifteen Seconds") if title in releases]

    for title in release_titles:
        release = releases.get(title, {"title": title})
        copy = COPY_MAP.get(title, {})
        hook = copy.get("hook") or f"{title} is live in the Lily Roo archive."
        for platform in platforms:
            key = (title.lower(), platform.lower(), "text")
            if key in scheduled_keys or key in planned_keys:
                continue
            draft_id = story_plan_id(title, platform)
            platform_copy = winner_story_copy(title, platform)
            selected_text = f"{hook} Subscribe on YouTube and help Lily Roo push this signal toward 1,000."
            drafts = [
                selected_text,
                f"{platform_copy} Subscribe on YouTube and help the signal climb toward 1,000.",
                f"{title} is part of the Lily Roo archive now. If this found you, send one more play/view into the signal.",
            ]
            post = {
                "id": draft_id,
                "scheduled_at": first_future_slot(post_index, platform),
                "platform": platform,
                "song": title,
                "imagery": "",
                "imagery_url": "",
                "clip_url": "",
                "text": selected_text,
                "drafts": drafts,
                "reply_text": cta_text(release),
                "selected_cta_strength": "hard_subscribe",
                "selected_copy_strategy": "growth_first_subscriber_cta",
                "format_candidate_role": "throughput_buffer",
                "x_media_key": "",
                "media_key": "",
                "approved": "no",
                "execution_mode": execution_mode(platform),
                "post_type": "text",
                "desired_privacy": "",
                "reason": "Create a ready-platform text/story variant from existing Lily Roo release copy while blocked media channels are repaired.",
                "approval_command": approval_command(draft_id),
            }
            post["approved"] = preserved_approval(prior_by_id, prior_by_slot, post)
            posts.append(post)
            planned_keys.add(key)
            post_index += 1
    return posts



def plan_summary(posts):
    counts = Counter("approved" if post.get("approved") == "yes" else "review" for post in posts)
    execution = Counter(post.get("execution_mode") or "unknown" for post in posts)
    releases = {}
    for title in sorted({post.get("song") or "Untitled release" for post in posts}):
        release_posts = [post for post in posts if (post.get("song") or "Untitled release") == title]
        releases[title] = {
            "draft_posts": len(release_posts),
            "approved_posts": sum(1 for post in release_posts if post.get("approved") == "yes"),
            "review_posts": sum(1 for post in release_posts if post.get("approved") != "yes"),
            "platforms": sorted({post.get("platform") for post in release_posts if post.get("platform")}),
        }
    platforms = {}
    for platform in sorted({post.get("platform") or "Unknown" for post in posts}):
        platform_posts = [post for post in posts if (post.get("platform") or "Unknown") == platform]
        platforms[platform] = {
            "draft_posts": len(platform_posts),
            "approved_posts": sum(1 for post in platform_posts if post.get("approved") == "yes"),
            "review_posts": sum(1 for post in platform_posts if post.get("approved") != "yes"),
        }
    return {
        "draft_posts": len(posts),
        "approved_posts": counts["approved"],
        "review_posts": counts["review"],
        "auto_posts": execution["auto"],
        "manual_posts": execution["manual"],
        "selected_hard_cta_posts": sum(1 for post in posts if post.get("selected_cta_strength") in {"hard_subscribe", "hard_goal"}),
        "releases": releases,
        "platforms": platforms,
    }


def apply_preview(posts, scheduled_rows):
    scheduled_ids = {row.get("id") for row in scheduled_rows if row.get("id")}
    approved = [post for post in posts if post.get("approved") == "yes"]
    ready = [post for post in approved if post.get("id") not in scheduled_ids]
    duplicates = [post for post in approved if post.get("id") in scheduled_ids]
    review = [post for post in posts if post.get("approved") != "yes"]
    return {
        "ready_to_apply_posts": len(ready),
        "review_posts": len(review),
        "scheduled_duplicate_posts": len(duplicates),
        "ready_ids": [post.get("id") for post in ready],
        "scheduled_duplicate_ids": [post.get("id") for post in duplicates],
    }


def readiness_for_platform(readiness, platform: str) -> dict:
    if platform == "YouTube Community":
        return {
            "state": "manual_only",
            "ready": False,
            "message": "Legacy YouTube Community rows should be converted to API-postable YouTube video rows.",
        }
    if not readiness:
        return {
            "state": "unknown",
            "ready": None,
            "message": "No executor readiness snapshot captured yet.",
        }
    if not readiness.get("ok"):
        return {
            "state": "unknown",
            "ready": None,
            "message": readiness.get("action_needed") or readiness.get("error") or "Executor readiness could not be captured.",
        }
    summary = readiness.get("summary") or {}
    platform_map = summary.get("platforms") or {}
    if platform not in platform_map:
        return {
            "state": "unknown",
            "ready": None,
            "message": "Executor readiness snapshot does not include this platform.",
        }
    ready = bool(platform_map.get(platform))
    return {
        "state": "ready" if ready else "blocked",
        "ready": ready,
        "message": "Ready after approval." if ready else "Executor credentials or platform setup are not ready.",
    }


def readiness_audit(posts, readiness):
    rows = []
    counts = Counter()
    for post in posts:
        item = readiness_for_platform(readiness, post.get("platform") or "")
        if post.get("approved") != "yes" and item["state"] == "ready":
            state = "ready_after_approval"
        else:
            state = item["state"]
        counts[state] += 1
        rows.append({
            "id": post.get("id", ""),
            "platform": post.get("platform", ""),
            "execution_mode": post.get("execution_mode", ""),
            "approved": post.get("approved", "no"),
            "state": state,
            "message": item["message"],
        })
    return {
        "source": str(EXECUTOR_READINESS.relative_to(ROOT)),
        "updated_at": readiness.get("updated_at", "") if isinstance(readiness, dict) else "",
        "ok": bool(readiness.get("ok")) if isinstance(readiness, dict) else False,
        "counts": dict(sorted(counts.items())),
        "rows": rows,
    }


def approval_commands(posts):
    review_posts = [post for post in posts if post.get("approved") != "yes"]
    releases = sorted({post.get("song") for post in review_posts if post.get("song")})
    platforms = sorted({post.get("platform") for post in review_posts if post.get("platform")})
    return {
        "all_review": approval_scope_command(all_posts=True) if review_posts else "",
        "by_release": {
            release: approval_scope_command(release=release)
            for release in releases
        },
        "by_platform": {
            platform: approval_scope_command(platform=platform)
            for platform in platforms
        },
    }


def apply_commands(posts):
    releases = sorted({post.get("song") for post in posts if post.get("song")})
    platforms = sorted({post.get("platform") for post in posts if post.get("platform")})
    return {
        "all_approved": apply_command(),
        "by_release": {
            release: apply_scope_command(release=release)
            for release in releases
        },
        "by_platform": {
            platform: apply_scope_command(platform=platform)
            for platform in platforms
        },
    }


def build_plan():
    promo = read_json(PROMO_STATUS, {})
    releases = release_lookup(read_json(RELEASE_STATUS, {}))
    readiness = read_json(EXECUTOR_READINESS, {})
    prior_by_id, prior_by_slot = prior_approval_lookup(read_json(OUT, {}))
    scheduled_rows = read_csv(SCHEDULED)
    posts = []
    post_index = 0

    for release_health in promo.get("releases", []):
        title = release_health.get("title")
        missing = [platform for platform in PLATFORM_ORDER if platform in (release_health.get("missing_platforms") or [])]
        if not missing and release_health.get("queued_posts") == 0 and release_health.get("status") != "healthy":
            missing = ["X", "Instagram", "Facebook"]
        release = releases.get(title, {"title": title})
        assets = ASSET_MAP.get(title, {})
        for platform in missing:
            kind = post_type(platform)
            media_url = assets.get("video" if kind == "video" else "image", "")
            media_key = assets.get("video_key" if kind == "video" else "media_key", "")
            draft_id = plan_id(title, platform)
            drafts = draft_variants(title, platform)
            selected_text, selected_strength = selected_growth_copy(drafts)
            post = {
                "id": draft_id,
                "scheduled_at": first_future_slot(post_index, platform),
                "platform": platform,
                "song": title,
                "imagery": f"{title} promo coverage",
                "imagery_url": media_url if kind != "video" else assets.get("image", ""),
                "clip_url": media_url if kind == "video" else "",
                "text": selected_text or copy_for(title, platform),
                "drafts": drafts,
                "reply_text": cta_text(release),
                "selected_cta_strength": selected_strength,
                "selected_copy_strategy": "growth_first_subscriber_cta",
                "x_media_key": "",
                "media_key": media_key,
                "approved": "no",
                "execution_mode": execution_mode(platform),
                "post_type": kind,
                "desired_privacy": "PUBLIC_TO_EVERYONE" if platform == "TikTok" else "",
                "reason": f"Promo health flagged missing {platform} coverage for {title}.",
                "approval_command": approval_command(draft_id),
            }
            post["approved"] = preserved_approval(prior_by_id, prior_by_slot, post)
            posts.append(post)
            post_index += 1

    posts.extend(winner_followup_posts(
        promo=promo,
        releases=releases,
        readiness=readiness,
        scheduled_rows=scheduled_rows,
        existing_posts=posts,
        start_index=post_index,
        prior_by_id=prior_by_id,
        prior_by_slot=prior_by_slot,
    ))
    posts.extend(story_text_followup_posts(
        releases=releases,
        readiness=readiness,
        scheduled_rows=scheduled_rows,
        existing_posts=posts,
        start_index=len(posts) + post_index,
        prior_by_id=prior_by_id,
        prior_by_slot=prior_by_slot,
    ))

    return {
        "generated_at": datetime.now(TZ).isoformat(),
        "source": {
            "promo_engine_status": str(PROMO_STATUS.relative_to(ROOT)),
            "release_status": str(RELEASE_STATUS.relative_to(ROOT)),
        },
        "mode": "draft_plan_only",
        "csv_target": "data/scheduled_posts.csv",
        "apply_note": "Mark reviewed rows approved=yes, then apply approved rows into the live schedule.",
        "apply_command": apply_command(),
        "approval_commands": approval_commands(posts),
        "apply_commands": apply_commands(posts),
        "summary": plan_summary(posts),
        "apply_preview": apply_preview(posts, scheduled_rows),
        "readiness_audit": readiness_audit(posts, readiness),
        "posts": posts,
    }


def replace_json_embed(html: str, block_id: str, payload) -> str:
    marker = f'<script type="application/json" id="{block_id}">'
    end_marker = "</script>"
    encoded = json.dumps(payload, indent=2, ensure_ascii=False)
    start = html.find(marker)
    if start == -1:
        insert_at = html.find("<script>")
        if insert_at == -1:
            return html
        return html[:insert_at] + f"{marker}{encoded}{end_marker}\n\n" + html[insert_at:]
    content_start = start + len(marker)
    content_end = html.find(end_marker, content_start)
    if content_end == -1:
        return html
    return html[:content_start] + encoded + html[content_end:]


def sync_admin_embed(plan):
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    updated = replace_json_embed(html, "embedded-promo-queue-plan", plan)
    if updated != html:
        ADMIN_INDEX.write_text(updated, encoding="utf-8")


def main():
    plan = build_plan()
    OUT.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    sync_admin_embed(plan)
    print(f"Wrote {OUT} with {len(plan['posts'])} draft posts")


if __name__ == "__main__":
    main()
