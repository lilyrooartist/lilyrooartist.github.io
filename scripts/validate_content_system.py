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
METRICS_HISTORY = ROOT / "data" / "metrics_history.json"
EXECUTOR_READINESS = ROOT / "data" / "executor_readiness_snapshot.json"
STORE_VERIFICATION_HISTORY = ROOT / "data" / "store_verification_history.json"
SOCIAL_EXECUTION_SNAPSHOT = ROOT / "data" / "social_execution_snapshot.json"
PROMO_REFRESH_RUN = ROOT / "data" / "promo_admin_refresh_run.json"
PROMO_OPERATIONS_PACKET = ROOT / "data" / "promo_operations_packet.json"
SPOTIFY_SNAPSHOT = ROOT / "data" / "spotify_release_snapshot.json"
APPLE_MUSIC_SNAPSHOT = ROOT / "data" / "apple_music_release_snapshot.json"
YOUTUBE_PUBLIC = ROOT / "data" / "youtube_public_snapshot.json"
YOUTUBE_TITLE_TRACK = ROOT / "data" / "youtube_title_track_snapshot.json"
YOUTUBE_MUSIC_SNAPSHOT = ROOT / "data" / "youtube_music_release_snapshot.json"
HYPERFOLLOW_SNAPSHOT = ROOT / "data" / "hyperfollow_store_links_snapshot.json"
ALIGNMENT_AUDIT = ROOT / "data" / "first_single_alignment_audit.json"
PROMO_ENGINE_STATUS = ROOT / "data" / "promo_engine_status.json"
PROMO_QUEUE_PLAN = ROOT / "data" / "promo_queue_plan.json"
TWELVE_DOLLARS_REMASTER = ROOT / "data" / "youtube_twelve_dollars_remaster_manifest.json"
TWELVE_DOLLARS_PLAYLIST = ROOT / "data" / "youtube_twelve_dollars_playlist.json"
PROMO_QUEUE_APPLY = ROOT / "scripts" / "apply_promo_queue_plan.py"
PROMO_QUEUE_APPROVE = ROOT / "scripts" / "approve_promo_queue_plan.py"
SCHEDULED_POST_APPROVAL = ROOT / "scripts" / "update_scheduled_post_approval.py"
MANUAL_METRICS_UPDATER = ROOT / "scripts" / "update_manual_social_stats.py"
STORE_LINK_VERIFIER = ROOT / "scripts" / "verify_pending_store_links.py"
METRICS_HISTORY_UPDATER = ROOT / "scripts" / "update_metrics_history.py"
EXECUTOR_READINESS_CAPTURE = ROOT / "scripts" / "capture_executor_readiness.py"
SOCIAL_EXECUTION_CAPTURE = ROOT / "scripts" / "capture_social_executions.py"
PROMO_REFRESH_SCRIPT = ROOT / "scripts" / "refresh_promo_admin.py"
PROMO_OPERATIONS_SCRIPT = ROOT / "scripts" / "build_promo_operations_packet.py"
REPORT = ROOT / "admin" / "reports" / "weekly-social-report.md"
PROMO_OPERATIONS_REPORT = ROOT / "admin" / "reports" / "promo-operations-packet.md"
INDEX = CONTENT / "content_index.json"
ADMIN_INDEX = ROOT / "admin" / "index.html"


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
    if METRICS_HISTORY.exists():
        history_snapshot = json.loads(METRICS_HISTORY.read_text(encoding="utf-8"))
        snapshots = history_snapshot.get("snapshots") or []
        latest = snapshots[-1] if snapshots else {}
        if snapshots and latest.get("date") and "delta_from_previous" in latest:
            ok(f"metrics history has {len(snapshots)} snapshot(s)")
        else:
            fail("metrics_history.json missing snapshots or deltas", failures)
    else:
        fail("metrics_history.json missing; run scripts/update_metrics_history.py", failures)
    if EXECUTOR_READINESS.exists():
        readiness = json.loads(EXECUTOR_READINESS.read_text(encoding="utf-8"))
        if "summary" in readiness and "updated_at" in readiness and readiness.get("auth_method") in {"bearer", "admin_password", "none"}:
            ok("executor readiness snapshot present")
        else:
            fail("executor_readiness_snapshot.json missing summary, timestamp, or auth method", failures)
    else:
        fail("executor_readiness_snapshot.json missing; run scripts/capture_executor_readiness.py", failures)
    if STORE_VERIFICATION_HISTORY.exists():
        store_history = json.loads(STORE_VERIFICATION_HISTORY.read_text(encoding="utf-8"))
        summary = store_history.get("summary") or {}
        rows = store_history.get("rows") or []
        if summary.get("total_services") == len(rows) and "snapshot_count" in summary:
            ok(f"store verification history tracks {len(rows)} service states")
        else:
            fail("store_verification_history.json summary does not match rows", failures)
    else:
        fail("store_verification_history.json missing; run scripts/update_promo_engine_status.py", failures)
    if SOCIAL_EXECUTION_SNAPSHOT.exists():
        execution_snapshot = json.loads(SOCIAL_EXECUTION_SNAPSHOT.read_text(encoding="utf-8"))
        summary = execution_snapshot.get("summary") or {}
        if "updated_at" in execution_snapshot and execution_snapshot.get("auth_method") in {"bearer", "admin_password", "none"} and "execution_count" in summary and "approval_needed_count" in summary and "platform_fix_needed_count" in summary:
            ok(f"social execution snapshot tracks {summary.get('execution_count')} executor records")
        else:
            fail("social_execution_snapshot.json missing categorized summary, timestamp, or auth method", failures)
    else:
        fail("social_execution_snapshot.json missing; run scripts/capture_social_executions.py", failures)
    if PROMO_REFRESH_RUN.exists():
        refresh_run = json.loads(PROMO_REFRESH_RUN.read_text(encoding="utf-8"))
        summary = refresh_run.get("summary") or {}
        commands = refresh_run.get("commands") or refresh_run.get("steps") or []
        if "started_at" in refresh_run and "finished_at" in refresh_run and summary.get("command_count") == len(commands):
            ok(f"promo admin refresh run tracks {len(commands)} command(s)")
        else:
            fail("promo_admin_refresh_run.json missing timestamps or command summary", failures)
        if refresh_run.get("safe_mode") is True and all("command" in command and "returncode" in command for command in commands):
            ok("promo admin refresh run records safe command results")
        else:
            fail("promo_admin_refresh_run.json missing safe command result detail", failures)
    else:
        fail("promo_admin_refresh_run.json missing; run scripts/refresh_promo_admin.py", failures)
    if PROMO_OPERATIONS_PACKET.exists():
        packet = json.loads(PROMO_OPERATIONS_PACKET.read_text(encoding="utf-8"))
        summary = packet.get("summary") or {}
        actions = packet.get("actions") or []
        if packet.get("safe_mode") is True and summary.get("action_count") == len(actions):
            ok(f"promo operations packet tracks {len(actions)} action(s)")
        else:
            fail("promo_operations_packet.json missing safe summary or action count", failures)
        action_kinds = {action.get("kind") for action in actions}
        required_kinds = {"approval_review", "store_verification", "manual_metrics", "platform_fix"}
        if required_kinds <= action_kinds and all("command" in action and "label" in action for action in actions):
            ok("promo operations packet groups approval, store, metric, and platform work")
        else:
            fail("promo_operations_packet.json missing required action groups", failures)
    else:
        fail("promo_operations_packet.json missing; run scripts/build_promo_operations_packet.py", failures)
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
        freshness = status.get("freshness") or {}
        sources = freshness.get("sources") or []
        if sources and freshness.get("summary", {}).get("fresh", 0) + freshness.get("summary", {}).get("stale", 0) + freshness.get("summary", {}).get("missing", 0) == len(sources):
            ok(f"promo engine freshness audit tracks {len(sources)} sources")
        else:
            fail("promo_engine_status.json missing source freshness audit", failures)
        for source in sources:
            name = source.get("name") or "[missing source]"
            if source.get("status") not in {"fresh", "stale", "missing"}:
                fail(f"promo engine freshness source {name} has invalid status", failures)
            for key in ("path", "max_age_hours", "refresh_command"):
                if not str(source.get(key) or "").strip():
                    fail(f"promo engine freshness source {name} missing {key}", failures)
        kpi = status.get("kpi") or {}
        pending_count = kpi.get("pending_manual_metric_fields", 0)
        pending_details = kpi.get("pending_manual_metric_details") or []
        if len(pending_details) == pending_count:
            ok(f"promo engine manual metric gap detail tracks {pending_count} fields")
        else:
            fail("promo_engine_status.json manual metric gap detail does not match pending count", failures)
        pending_command = kpi.get("pending_manual_update_command") or ""
        pending_by_platform = kpi.get("pending_manual_update_by_platform") or {}
        auto_covered = kpi.get("auto_covered_manual_metric_fields") or []
        collection_steps = kpi.get("manual_metric_collection_steps") or []
        if pending_count:
            if "update_manual_social_stats.py" in pending_command and "--refresh-admin" in pending_command:
                ok("promo engine manual metric update command present")
            else:
                fail("promo_engine_status.json missing manual metric update command", failures)
            if pending_by_platform:
                ok(f"promo engine manual metric platform commands track {len(pending_by_platform)} platforms")
            else:
                fail("promo_engine_status.json missing manual metric platform commands", failures)
            if collection_steps:
                ok(f"promo engine manual metric collection steps track {len(collection_steps)} platforms")
            else:
                fail("promo_engine_status.json missing manual metric collection steps", failures)
        if auto_covered and any(item.get("field") == "facebook.followers" for item in auto_covered):
            ok("promo engine recognizes live API-covered manual metric fields")
        else:
            fail("promo_engine_status.json missing API-covered manual metric evidence", failures)
        history = kpi.get("metrics_history") or {}
        if history.get("snapshot_count") and history.get("latest_date"):
            ok(f"promo engine metrics history tracks {history.get('snapshot_count')} snapshot(s)")
        else:
            fail("promo_engine_status.json missing metrics history KPI summary", failures)
        music_site_counts = kpi.get("music_site_state_counts") or {}
        release_services = [
            service
            for release in releases
            for service in (release.get("store_services") or [])
        ]
        if release_services and sum(int(value or 0) for value in music_site_counts.values()) == len(release_services):
            ok(f"promo engine music site matrix tracks {len(release_services)} service states")
        else:
            fail("promo_engine_status.json missing music site service matrix", failures)
        verification_commands = [
            command
            for release in releases
            for command in (release.get("store_verification_commands") or [])
        ]
        expected_pending = [
            service
            for release in releases
            for service in (release.get("store_services") or [])
            if service.get("state") == "Pending" and service.get("label") not in {"DistroKid", "YouTube playlist"}
        ]
        if len(verification_commands) == len(expected_pending) == int(kpi.get("store_verification_command_count") or 0):
            ok(f"promo engine store verification commands track {len(verification_commands)} pending services")
        else:
            fail("promo_engine_status.json store verification commands do not match pending services", failures)
        store_history_summary = kpi.get("store_verification_history") or {}
        if store_history_summary.get("total_services") and "snapshot_count" in store_history_summary:
            ok("promo engine includes store verification history summary")
        else:
            fail("promo_engine_status.json missing store verification history summary", failures)
        execution_summary = kpi.get("social_execution_summary") or {}
        if "execution_count" in execution_summary and "status_counts" in execution_summary and "approval_needed_count" in execution_summary and "platform_fix_needed_count" in execution_summary:
            ok("promo engine includes social execution summary")
        else:
            fail("promo_engine_status.json missing categorized social execution summary", failures)
        refresh_run = kpi.get("last_refresh_run") or {}
        if "available" in refresh_run and "command_count" in refresh_run and "finished_at" in refresh_run:
            ok("promo engine includes last refresh run summary")
        else:
            fail("promo_engine_status.json missing last refresh run summary", failures)
        repair_rows = (execution_summary.get("approval_needed") or []) + (execution_summary.get("platform_fix_needed") or [])
        if repair_rows and all(row.get("repair_action") and row.get("repair_command") for row in repair_rows):
            ok(f"promo engine social execution rows include {len(repair_rows)} repair commands")
        else:
            fail("promo_engine_status.json social execution rows missing repair guidance", failures)
        for command in verification_commands:
            if "scripts/capture_" not in str(command.get("command") or ""):
                fail(f"store verification command for {command.get('service') or 'unknown service'} missing capture script", failures)
        automatable_commands = [
            command for command in verification_commands
            if command.get("service") in {"Apple Music", "HyperFollow"}
        ]
        snapshotted = [
            command for command in automatable_commands
            if (command.get("latest_snapshot") or {}).get("path")
            and (command.get("latest_snapshot") or {}).get("updated_at")
        ]
        if len(snapshotted) == len(automatable_commands):
            ok(f"promo engine store verifier has snapshot evidence for {len(snapshotted)} automatable pending checks")
        else:
            fail("promo_engine_status.json missing latest snapshot evidence for automatable pending store checks", failures)
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
        apply_command = plan.get("apply_command") or ""
        if "apply_promo_queue_plan.py --apply --refresh-admin" in apply_command:
            ok("promo queue plan includes refresh-aware apply command")
        else:
            fail("promo_queue_plan.json missing refresh-aware apply command", failures)
        apply_commands = plan.get("apply_commands") or {}
        apply_by_release = apply_commands.get("by_release") or {}
        if "apply_promo_queue_plan.py --apply --refresh-admin" in (apply_commands.get("all_approved") or ""):
            ok("promo queue plan includes all-approved apply command")
        else:
            fail("promo_queue_plan.json missing all-approved apply command", failures)
        if apply_by_release:
            ok(f"promo queue plan includes release apply commands for {len(apply_by_release)} release(s)")
        else:
            fail("promo_queue_plan.json missing release apply commands", failures)
        approval_commands = plan.get("approval_commands") or {}
        if summary.get("review_posts", 0):
            all_review_command = approval_commands.get("all_review") or ""
            by_release = approval_commands.get("by_release") or {}
            if "approve_promo_queue_plan.py --all --refresh-admin" in all_review_command:
                ok("promo queue plan includes all-review approval command")
            else:
                fail("promo_queue_plan.json missing all-review approval command", failures)
            if by_release:
                ok(f"promo queue plan includes release approval commands for {len(by_release)} release(s)")
            else:
                fail("promo_queue_plan.json missing release approval commands", failures)
        apply_preview = plan.get("apply_preview") or {}
        readiness_audit = plan.get("readiness_audit") or {}
        for key in ("ready_to_apply_posts", "review_posts", "scheduled_duplicate_posts", "ready_ids", "scheduled_duplicate_ids"):
            if key not in apply_preview:
                fail(f"promo_queue_plan.json apply_preview missing {key}", failures)
        if readiness_audit.get("rows") and readiness_audit.get("counts") is not None:
            ok("promo queue plan includes executor readiness audit")
        else:
            fail("promo_queue_plan.json missing executor readiness audit", failures)
        ready_ids = apply_preview.get("ready_ids") or []
        duplicate_ids = apply_preview.get("scheduled_duplicate_ids") or []
        if apply_preview.get("ready_to_apply_posts") == len(ready_ids):
            ok("promo queue apply preview tracks ready ids")
        else:
            fail("promo_queue_plan.json apply_preview ready count mismatch", failures)
        if apply_preview.get("scheduled_duplicate_posts") == len(duplicate_ids):
            ok("promo queue apply preview tracks duplicate ids")
        else:
            fail("promo_queue_plan.json apply_preview duplicate count mismatch", failures)
        for post in posts:
            for key in ("id", "scheduled_at", "platform", "song", "text", "execution_mode", "post_type", "approval_command"):
                if not str(post.get(key) or "").strip():
                    fail(f"promo queue plan row {post.get('id') or '[missing id]'} missing {key}", failures)
            if post.get("id") and post.get("approval_command") and post["id"] not in post["approval_command"]:
                fail(f"promo queue plan row {post.get('id')} approval_command does not reference row id", failures)
            if str(post.get("approved") or "").lower() not in {"yes", "no"}:
                fail(f"promo queue plan row {post.get('id') or '[missing id]'} approved must be yes or no", failures)
    else:
        fail("promo_queue_plan.json missing; run scripts/generate_promo_queue_plan.py", failures)
    if PROMO_QUEUE_APPLY.exists():
        ok("promo queue apply script present")
        apply_text = PROMO_QUEUE_APPLY.read_text(encoding="utf-8")
        if "--refresh-admin" in apply_text and "scripts/sync_future_posts.py" in apply_text:
            ok("promo queue apply script can refresh admin")
        else:
            fail("apply_promo_queue_plan.py missing --refresh-admin flow", failures)
        if "--release" in apply_text and "--platform" in apply_text:
            ok("promo queue apply script supports scoped release/platform apply")
        else:
            fail("apply_promo_queue_plan.py missing scoped release/platform apply", failures)
    else:
        fail("apply_promo_queue_plan.py missing", failures)
    if PROMO_QUEUE_APPROVE.exists():
        ok("promo queue approval script present")
    else:
        fail("approve_promo_queue_plan.py missing", failures)
    if SCHEDULED_POST_APPROVAL.exists():
        approval_text = SCHEDULED_POST_APPROVAL.read_text(encoding="utf-8")
        if "scheduled_posts.csv" in approval_text and "--refresh-admin" in approval_text and "sync_future_posts.py" in approval_text:
            ok("scheduled post approval script can refresh admin")
        else:
            fail("update_scheduled_post_approval.py missing scheduled queue refresh support", failures)
    else:
        fail("update_scheduled_post_approval.py missing", failures)
    if MANUAL_METRICS_UPDATER.exists():
        ok("manual social stats updater present")
    else:
        fail("update_manual_social_stats.py missing", failures)
    if STORE_LINK_VERIFIER.exists():
        verifier_text = STORE_LINK_VERIFIER.read_text(encoding="utf-8")
        if "capture_apple_music_release.py" in verifier_text and "capture_hyperfollow_store_links.py" in verifier_text and "--refresh-admin" in verifier_text:
            ok("pending store link verifier can refresh admin")
        else:
            fail("verify_pending_store_links.py missing capture or refresh support", failures)
    else:
        fail("verify_pending_store_links.py missing", failures)
    if METRICS_HISTORY_UPDATER.exists():
        history_text = METRICS_HISTORY_UPDATER.read_text(encoding="utf-8")
        if "metrics_history.json" in history_text and "--refresh-admin" in history_text:
            ok("metrics history updater can refresh admin")
        else:
            fail("update_metrics_history.py missing history or refresh support", failures)
    else:
        fail("update_metrics_history.py missing", failures)
    if EXECUTOR_READINESS_CAPTURE.exists():
        readiness_text = EXECUTOR_READINESS_CAPTURE.read_text(encoding="utf-8")
        if "executor_readiness_snapshot.json" in readiness_text and "X-Lilyroo-Admin-Password" in readiness_text:
            ok("executor readiness capture script present")
        else:
            fail("capture_executor_readiness.py missing readiness snapshot or auth header support", failures)
    else:
        fail("capture_executor_readiness.py missing", failures)
    if SOCIAL_EXECUTION_CAPTURE.exists():
        execution_text = SOCIAL_EXECUTION_CAPTURE.read_text(encoding="utf-8")
        if "social_execution_snapshot.json" in execution_text and "X-Lilyroo-Admin-Password" in execution_text:
            ok("social execution capture script present")
        else:
            fail("capture_social_executions.py missing execution snapshot or auth header support", failures)
    else:
        fail("capture_social_executions.py missing", failures)
    if PROMO_REFRESH_SCRIPT.exists():
        refresh_text = PROMO_REFRESH_SCRIPT.read_text(encoding="utf-8")
        required_bits = [
            "promo_admin_refresh_run.json",
            "capture_live_metrics.py",
            "verify_pending_store_links.py",
            "capture_executor_readiness.py",
            "capture_social_executions.py",
            "build_promo_operations_packet.py",
            "update_weekly_report.py",
        ]
        forbidden_bits = [
            "apply_promo_queue_plan.py --apply",
            '"scripts/post_youtube_from_queue.py"',
            '"scripts/post_youtube_captions.py"',
        ]
        if all(bit in refresh_text for bit in required_bits) and not any(bit in refresh_text for bit in forbidden_bits):
            ok("promo admin refresh script covers safe refresh steps")
        else:
            fail("refresh_promo_admin.py missing safe refresh coverage or includes posting commands", failures)
    else:
        fail("refresh_promo_admin.py missing", failures)
    if PROMO_OPERATIONS_SCRIPT.exists():
        packet_text = PROMO_OPERATIONS_SCRIPT.read_text(encoding="utf-8")
        if "promo_operations_packet.json" in packet_text and "promo-operations-packet.md" in packet_text and "approval_review" in packet_text and "subprocess" not in packet_text:
            ok("promo operations packet builder is review-only")
        else:
            fail("build_promo_operations_packet.py missing review packet outputs or executes commands", failures)
    else:
        fail("build_promo_operations_packet.py missing", failures)
    if PROMO_OPERATIONS_REPORT.exists():
        report_text = PROMO_OPERATIONS_REPORT.read_text(encoding="utf-8")
        if "Promo Operations Packet" in report_text and "Top Actions" in report_text:
            ok("promo operations markdown report present")
        else:
            fail("promo operations markdown report missing expected sections", failures)
    else:
        fail("promo-operations-packet.md missing", failures)


def validate_report(failures):
    text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    if re.search(r"\*\*Last updated:\*\*\s*\d{4}-\d{2}-\d{2}", text):
        ok("weekly report has a Last updated timestamp")
    else:
        fail("weekly report missing Last updated timestamp", failures)


def validate_admin_execution_feedback(failures):
    text = ADMIN_INDEX.read_text(encoding="utf-8") if ADMIN_INDEX.exists() else ""
    checks = {
        "live feedback region": 'data-role="exec-feedback" aria-live="polite"' in text,
        "working acknowledgement": "Publishing ${p.platform || 'post'} now" in text,
        "success acknowledgement": "Published successfully" in text,
        "failure helper": "socialExecutorFailureMessage" in text,
        "failed status": "statusEl.textContent='Failed'" in text,
        "long feedback wrapping": "overflow-wrap:anywhere" in text,
    }
    missing = [label for label, present in checks.items() if not present]
    if missing:
        fail("admin execute feedback missing " + ", ".join(missing), failures)
    else:
        ok("admin execute button has working/success/error feedback")


def validate_twelve_dollars_remasters(failures):
    if not TWELVE_DOLLARS_REMASTER.exists() or not TWELVE_DOLLARS_PLAYLIST.exists():
        fail("Twelve Dollars remaster manifest or playlist snapshot missing", failures)
        return
    manifest = json.loads(TWELVE_DOLLARS_REMASTER.read_text(encoding="utf-8"))
    playlist = json.loads(TWELVE_DOLLARS_PLAYLIST.read_text(encoding="utf-8"))
    tracks = manifest.get("tracks") or []
    playlist_tracks = playlist.get("tracks") or []
    expected_titles = [
        "Brain Rot",
        "Every Pearl in Carmel",
        "The Other One's Charging",
        "Twelve Dollars",
        "William and Dander",
        "Just Don't Talk About It",
        "Gluten Free Bread",
        "When Lily Talks",
    ]
    manifest_titles = [track.get("title") for track in tracks]
    playlist_titles = [track.get("title") for track in playlist_tracks]
    if manifest.get("ok") and manifest.get("applied") and manifest_titles == expected_titles:
        ok("Twelve Dollars remaster manifest tracks all eight canonical videos")
    else:
        fail("Twelve Dollars remaster manifest does not match canonical track list", failures)
    if playlist.get("ok") and playlist.get("verified_items") == 8 and playlist_titles == expected_titles:
        ok("Twelve Dollars playlist snapshot verifies eight-track order")
    else:
        fail("Twelve Dollars playlist snapshot does not verify canonical order", failures)
    for track in tracks:
        title = track.get("title") or "[missing title]"
        if not track.get("new_video_id"):
            fail(f"Twelve Dollars remaster missing new_video_id for {title}", failures)
        if not track.get("old_archived"):
            fail(f"Twelve Dollars remaster old upload not archived for {title}", failures)
        if (track.get("thumbnail_result") or {}).get("ok") is not True:
            fail(f"Twelve Dollars remaster thumbnail not confirmed for {title}", failures)
        for key in ("video_file", "thumbnail_file"):
            path = ROOT / str(track.get(key) or "")
            if not path.exists():
                fail(f"Twelve Dollars remaster {title} missing {key}", failures)


def main():
    failures = []
    validate_pack_pairs(failures)
    validate_quips(failures)
    validate_queue(failures)
    validate_generated_outputs(failures)
    validate_report(failures)
    validate_admin_execution_feedback(failures)
    validate_twelve_dollars_remasters(failures)
    if failures:
        print(f"\n{len(failures)} validation issue(s)")
        return 1
    print("\ncontent system validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
