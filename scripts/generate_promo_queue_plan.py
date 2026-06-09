#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parent.parent
PROMO_STATUS = ROOT / "data" / "promo_engine_status.json"
RELEASE_STATUS = ROOT / "data" / "distrokid_release_status.json"
OUT = ROOT / "data" / "promo_queue_plan.json"
ADMIN_INDEX = ROOT / "admin" / "index.html"

TZ = ZoneInfo("America/New_York")
PLATFORM_ORDER = ["X", "Instagram", "TikTok", "Facebook", "YouTube Community"]
TIME_WINDOWS = {
    "X": (10, 15),
    "Instagram": (14, 5),
    "TikTok": (20, 40),
    "Facebook": (11, 20),
    "YouTube Community": (18, 30),
}

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
        "community": "New album transmission: Twelve Dollars. Remastered videos, updated art, full playlist live now.",
    },
    "Analog Myth": {
        "hook": "Time broke, so Lily Roo made an album out of the pieces.",
        "x": "Analog Myth is the clock lying politely while the songs keep receipts. Full remastered playlist is live.",
        "instagram": "Analog Myth is a little archive of broken clocks, exposed throws, and songs that keep arriving late on purpose.",
        "tiktok": "Time broke. The songs kept moving. Analog Myth is live in the archive.",
        "facebook": "Analog Myth is live on YouTube now, with remastered videos and the album order finally lined up the way the transmission wants it.",
        "community": "Analog Myth transmission is live: 13, Girls Camp, Analog Myth, Spilling the Tea, No Mortgage, Guards Down, Slow Walk, The Power of Light.",
    },
}


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def slug(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().lower()).strip("-")
    return cleaned or "item"


def plan_id(title: str, platform: str) -> str:
    return f"FP-PLAN-{slug(title).upper()}-{slug(platform).upper()}"


def approval_command(post_id: str) -> str:
    return f"python3 scripts/approve_promo_queue_plan.py --id {post_id} --refresh-admin"


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
    if platform == "YouTube Community":
        return "community"
    if platform == "TikTok":
        return "video"
    return "image"


def execution_mode(platform):
    return "manual" if platform == "YouTube Community" else "auto"


def copy_for(title, platform):
    copy = COPY_MAP.get(title, {})
    key = "community" if platform == "YouTube Community" else platform.lower()
    return copy.get(key) or f"{title} is live in the Lily Roo archive."


def draft_variants(title, platform):
    copy = COPY_MAP.get(title, {})
    base = copy_for(title, platform)
    hook = copy.get("hook", f"{title} is live in the archive.")
    return [
        base,
        f"{hook} Full signal on YouTube.",
        f"{title} is part of the Lily Roo archive now. Help us build the signal to 1,000 subscribers.",
    ]


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
        "releases": releases,
        "platforms": platforms,
    }


def build_plan():
    promo = read_json(PROMO_STATUS, {})
    releases = release_lookup(read_json(RELEASE_STATUS, {}))
    prior_by_id, prior_by_slot = prior_approval_lookup(read_json(OUT, {}))
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
            post = {
                "id": draft_id,
                "scheduled_at": first_future_slot(post_index, platform),
                "platform": platform,
                "song": title,
                "imagery": f"{title} promo coverage",
                "imagery_url": media_url if kind != "video" else assets.get("image", ""),
                "clip_url": media_url if kind == "video" else "",
                "text": copy_for(title, platform),
                "drafts": draft_variants(title, platform),
                "reply_text": cta_text(release),
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

    return {
        "generated_at": datetime.now(TZ).isoformat(),
        "source": {
            "promo_engine_status": str(PROMO_STATUS.relative_to(ROOT)),
            "release_status": str(RELEASE_STATUS.relative_to(ROOT)),
        },
        "mode": "draft_plan_only",
        "csv_target": "data/scheduled_posts.csv",
        "apply_note": "Mark reviewed rows approved=yes, then run scripts/apply_promo_queue_plan.py --apply and scripts/sync_future_posts.py.",
        "summary": plan_summary(posts),
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
