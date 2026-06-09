#!/usr/bin/env python3
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "admin" / "content"
CATALOG = ROOT / "admin" / "backstory" / "catalog.json"
QUIPS = CONTENT / "20_QUIPS_BANK.csv"
QUEUE = ROOT / "data" / "scheduled_posts.csv"
FUTURE = ROOT / "admin" / "future-posts.json"
LIVE_METRICS = ROOT / "data" / "live_social_metrics.json"
SPOTIFY_SNAPSHOT = ROOT / "data" / "spotify_release_snapshot.json"
APPLE_MUSIC_SNAPSHOT = ROOT / "data" / "apple_music_release_snapshot.json"
YOUTUBE_PUBLIC = ROOT / "data" / "youtube_public_snapshot.json"
YOUTUBE_TITLE_TRACK = ROOT / "data" / "youtube_title_track_snapshot.json"
YOUTUBE_MUSIC_SNAPSHOT = ROOT / "data" / "youtube_music_release_snapshot.json"
HYPERFOLLOW_SNAPSHOT = ROOT / "data" / "hyperfollow_store_links_snapshot.json"
ALIGNMENT_AUDIT = ROOT / "data" / "first_single_alignment_audit.json"
PROMO_ENGINE_STATUS = ROOT / "data" / "promo_engine_status.json"
PROMO_QUEUE_PLAN = ROOT / "data" / "promo_queue_plan.json"
PROMO_QUEUE_APPLY = ROOT / "scripts" / "apply_promo_queue_plan.py"
REPORT = ROOT / "admin" / "reports" / "weekly-social-report.md"
INDEX = CONTENT / "content_index.json"


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fail(message, failures):
    failures.append(message)
    print(f"FAIL: {message}")


def ok(message):
    print(f"OK: {message}")


def validate_pack_pairs(failures):
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    missing = []
    for song in data.get("songs", []):
        for key in ("backstory_file", "visual_file"):
            ref = song.get(key, "")
            if not ref or not (ROOT / ref.lstrip("/")).exists():
                missing.append(f"{song.get('title', 'Unknown')} missing {key}")
    if missing:
        for item in missing:
            fail(item, failures)
    else:
        ok("all catalog songs have backstory and visual packs")


def validate_quips(failures):
    rows = read_csv(QUIPS)
    required = {"id", "theme", "tone", "quip", "ideal_platform", "cta"}
    if rows and set(rows[0].keys()) >= required:
        ok("quips CSV has required columns")
    else:
        fail("quips CSV is missing required columns", failures)
    ids = [row.get("id", "") for row in rows]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        fail(f"duplicate quip ids: {', '.join(duplicates)}", failures)
    else:
        ok(f"quip ids unique ({len(rows)} rows)")


def validate_queue(failures):
    rows = read_csv(QUEUE)
    required = {"id", "scheduled_at", "platform", "song", "text", "drafts", "approved", "execution_mode", "post_type"}
    if not rows:
        fail("scheduled queue is empty", failures)
        return
    if set(rows[0].keys()) >= required:
        ok("scheduled queue has required columns")
    else:
        fail("scheduled queue is missing required columns", failures)
    ids = [row.get("id", "") for row in rows]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        fail(f"duplicate queue ids: {', '.join(duplicates)}", failures)
    else:
        ok(f"queue ids unique ({len(rows)} rows)")
    for row in rows:
        for key in ("id", "scheduled_at", "platform", "text"):
            if not row.get(key, "").strip():
                fail(f"queue row {row.get('id') or '[missing id]'} missing {key}", failures)
        try:
            datetime.fromisoformat(row.get("scheduled_at", ""))
        except ValueError:
            fail(f"queue row {row.get('id')} has invalid scheduled_at", failures)
        approved = row.get("approved", "").strip().lower()
        if approved not in {"yes", "no"}:
            fail(f"queue row {row.get('id')} approved must be yes or no", failures)
        mode = row.get("execution_mode", "").strip().lower()
        if mode not in {"auto", "manual"}:
            fail(f"queue row {row.get('id')} execution_mode must be auto or manual", failures)
        post_type = row.get("post_type", "").strip().lower()
        if post_type not in {"text", "image", "video", "community", "link"}:
            fail(f"queue row {row.get('id')} has unsupported post_type {post_type or '[missing]'}", failures)


def validate_generated_outputs(failures):
    if FUTURE.exists():
        future = json.loads(FUTURE.read_text(encoding="utf-8"))
        if future.get("posts"):
            ok(f"future-posts.json has {len(future['posts'])} posts")
        else:
            fail("future-posts.json has no posts", failures)
    else:
        fail("future-posts.json missing", failures)
    if INDEX.exists():
        index = json.loads(INDEX.read_text(encoding="utf-8"))
        ok(f"content index generated with {index.get('counts', {}).get('songs', 0)} songs")
    else:
        fail("content_index.json missing; run scripts/build_content_index.py", failures)
    if LIVE_METRICS.exists():
        snapshot = json.loads(LIVE_METRICS.read_text(encoding="utf-8"))
        platforms = snapshot.get("platforms") or {}
        if platforms:
            ok(f"live social metrics snapshot has {len(platforms)} platforms")
        else:
            fail("live social metrics snapshot has no platforms", failures)
    else:
        fail("live_social_metrics.json missing; run scripts/capture_live_metrics.py", failures)
    if SPOTIFY_SNAPSHOT.exists():
        snapshot = json.loads(SPOTIFY_SNAPSHOT.read_text(encoding="utf-8"))
        if snapshot.get("ok") and snapshot.get("title") and snapshot.get("thumbnail_url"):
            ok(f"Spotify release snapshot verifies {snapshot.get('title')}")
        else:
            fail("spotify_release_snapshot.json missing title or thumbnail_url", failures)
    else:
        fail("spotify_release_snapshot.json missing; run scripts/capture_spotify_release.py", failures)
    if APPLE_MUSIC_SNAPSHOT.exists():
        snapshot = json.loads(APPLE_MUSIC_SNAPSHOT.read_text(encoding="utf-8"))
        if snapshot.get("ok") and snapshot.get("collection_name") and snapshot.get("release_url"):
            ok(f"Apple Music release snapshot verifies {snapshot.get('collection_name')}")
        else:
            fail("apple_music_release_snapshot.json missing collection_name or release_url", failures)
    else:
        fail("apple_music_release_snapshot.json missing; run scripts/capture_apple_music_release.py", failures)
    if YOUTUBE_PUBLIC.exists():
        snapshot = json.loads(YOUTUBE_PUBLIC.read_text(encoding="utf-8"))
        if snapshot.get("ok") and snapshot.get("recent_video_count") and snapshot.get("recent_public_views_total") is not None:
            ok(f"YouTube public snapshot has {snapshot.get('recent_video_count')} recent videos")
        else:
            fail("youtube_public_snapshot.json missing recent video count or views", failures)
    else:
        fail("youtube_public_snapshot.json missing; run scripts/capture_youtube_public.py", failures)
    if YOUTUBE_TITLE_TRACK.exists():
        snapshot = json.loads(YOUTUBE_TITLE_TRACK.read_text(encoding="utf-8"))
        if snapshot.get("ok") and snapshot.get("public_title") and snapshot.get("url"):
            if snapshot.get("title_matches_official") is True:
                ok("YouTube title-track title matches official title")
            else:
                ok(f"YouTube title-track snapshot captured mismatch: {snapshot.get('public_title')}")
        else:
            fail("youtube_title_track_snapshot.json missing public_title or url", failures)
    else:
        fail("youtube_title_track_snapshot.json missing; run scripts/capture_youtube_title_track.py", failures)
    if YOUTUBE_MUSIC_SNAPSHOT.exists():
        snapshot = json.loads(YOUTUBE_MUSIC_SNAPSHOT.read_text(encoding="utf-8"))
        if snapshot.get("ok") and snapshot.get("public_title") and snapshot.get("release_url"):
            if snapshot.get("title_matches_official") is True:
                ok("YouTube Music release title matches official title")
            else:
                ok(f"YouTube Music snapshot captured mirrored title mismatch: {snapshot.get('public_title')}")
        else:
            fail("youtube_music_release_snapshot.json missing public_title or release_url", failures)
    else:
        fail("youtube_music_release_snapshot.json missing; run scripts/capture_youtube_music_release.py", failures)
    if HYPERFOLLOW_SNAPSHOT.exists():
        snapshot = json.loads(HYPERFOLLOW_SNAPSHOT.read_text(encoding="utf-8"))
        stores = snapshot.get("stores") or []
        if snapshot.get("ok") and stores:
            ok(f"HyperFollow store snapshot has {', '.join(stores)}")
        else:
            fail("hyperfollow_store_links_snapshot.json missing store links", failures)
    else:
        fail("hyperfollow_store_links_snapshot.json missing; run scripts/capture_hyperfollow_store_links.py", failures)
    if ALIGNMENT_AUDIT.exists():
        audit = json.loads(ALIGNMENT_AUDIT.read_text(encoding="utf-8"))
        checks = audit.get("checks") or {}
        if checks and "spotify" in checks and "youtube" in checks:
            pending = ", ".join(audit.get("pending") or []) or "none"
            action_required = ", ".join(audit.get("action_required") or []) or "none"
            ok(f"first single alignment audit present; action_required={action_required}; pending={pending}")
        else:
            fail("first_single_alignment_audit.json missing platform checks", failures)
    else:
        fail("first_single_alignment_audit.json missing; run scripts/audit_first_single_alignment.py", failures)
    if PROMO_ENGINE_STATUS.exists():
        status = json.loads(PROMO_ENGINE_STATUS.read_text(encoding="utf-8"))
        releases = status.get("releases") or []
        health = status.get("health") or {}
        if releases and health.get("tracked_releases") == len(releases):
            ok(f"promo engine status tracks {len(releases)} releases")
        else:
            fail("promo_engine_status.json missing release health summary", failures)
        if "next_actions" in status:
            ok(f"promo engine status has {len(status.get('next_actions') or [])} next actions")
        else:
            fail("promo_engine_status.json missing next_actions", failures)
    else:
        fail("promo_engine_status.json missing; run scripts/update_promo_engine_status.py", failures)
    if PROMO_QUEUE_PLAN.exists():
        plan = json.loads(PROMO_QUEUE_PLAN.read_text(encoding="utf-8"))
        posts = plan.get("posts") or []
        summary = plan.get("summary") or {}
        if posts and plan.get("mode") == "draft_plan_only":
            ok(f"promo queue plan has {len(posts)} draft posts")
        else:
            fail("promo_queue_plan.json missing draft posts or mode", failures)
        if summary.get("draft_posts") == len(posts):
            ok("promo queue plan summary matches draft post count")
        else:
            fail("promo_queue_plan.json summary draft_posts does not match posts", failures)
        for post in posts:
            for key in ("id", "scheduled_at", "platform", "song", "text", "execution_mode", "post_type"):
                if not str(post.get(key) or "").strip():
                    fail(f"promo queue plan row {post.get('id') or '[missing id]'} missing {key}", failures)
            if str(post.get("approved") or "").lower() not in {"yes", "no"}:
                fail(f"promo queue plan row {post.get('id') or '[missing id]'} approved must be yes or no", failures)
    else:
        fail("promo_queue_plan.json missing; run scripts/generate_promo_queue_plan.py", failures)
    if PROMO_QUEUE_APPLY.exists():
        ok("promo queue apply script present")
    else:
        fail("apply_promo_queue_plan.py missing", failures)


def validate_report(failures):
    text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    if re.search(r"\*\*Last updated:\*\*\s*\d{4}-\d{2}-\d{2}", text):
        ok("weekly report has a Last updated timestamp")
    else:
        fail("weekly report missing Last updated timestamp", failures)


def main():
    failures = []
    validate_pack_pairs(failures)
    validate_quips(failures)
    validate_queue(failures)
    validate_generated_outputs(failures)
    validate_report(failures)
    if failures:
        print(f"\n{len(failures)} validation issue(s)")
        return 1
    print("\ncontent system validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
