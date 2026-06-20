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
MANUAL_SOCIAL_STATS = ROOT / "data" / "manual_social_stats.json"
METRICS_HISTORY = ROOT / "data" / "metrics_history.json"
EXECUTOR_READINESS = ROOT / "data" / "executor_readiness_snapshot.json"
STORE_VERIFICATION_HISTORY = ROOT / "data" / "store_verification_history.json"
SOCIAL_EXECUTION_SNAPSHOT = ROOT / "data" / "social_execution_snapshot.json"
SOCIAL_SCHEDULER_DRY_RUN = ROOT / "data" / "social_scheduler_dry_run.json"
PROMO_REFRESH_RUN = ROOT / "data" / "promo_admin_refresh_run.json"
PROMO_REFRESH_WORKFLOW_STATUS = ROOT / "data" / "promo_refresh_workflow_status.json"
PROMO_CONSISTENCY_AUDIT = ROOT / "data" / "promo_consistency_audit.json"
TIKTOK_SETUP_PREFLIGHT = ROOT / "data" / "tiktok_setup_preflight.json"
TIKTOK_REPAIR_RUNBOOK = ROOT / "data" / "tiktok_repair_runbook.json"
PROMO_OPERATIONS_PACKET = ROOT / "data" / "promo_operations_packet.json"
PUBLISHED_LOG_RECONCILIATION = ROOT / "data" / "published_log_reconciliation.json"
HUMAN_HANDOFF_PACKET = ROOT / "data" / "human_handoff_packet.json"
PROMOTION_BLOCKER_LEDGER = ROOT / "data" / "promotion_blocker_ledger.json"
PLATFORM_REPAIR_STATUS = ROOT / "data" / "platform_repair_status.json"
APPROVAL_RUNWAY = ROOT / "data" / "approval_runway.json"
SCHEDULED_APPROVAL_PACKET = ROOT / "data" / "scheduled_approval_packet.json"
SUBSCRIBER_CTA_AUDIT = ROOT / "data" / "subscriber_cta_audit.json"
MANUAL_DISTRIBUTION_PACKET = ROOT / "data" / "manual_distribution_packet.json"
MONETIZATION_ACTIVATION_PLAN = ROOT / "data" / "monetization_activation_plan.json"
BACKLOG_RESCHEDULE_PREVIEW = ROOT / "data" / "backlog_reschedule_preview.json"
MANUAL_METRIC_TEMPLATE = ROOT / "data" / "manual_metric_collection_template.csv"
MANUAL_METRIC_PACKET = ROOT / "data" / "manual_metric_collection_packet.json"
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
SCHEDULED_POST_RESCHEDULE = ROOT / "scripts" / "reschedule_scheduled_posts.py"
MANUAL_DISTRIBUTION_LOGGER = ROOT / "scripts" / "log_manual_distribution.py"
MANUAL_METRICS_UPDATER = ROOT / "scripts" / "update_manual_social_stats.py"
SOCIAL_EXECUTOR_WORKER = ROOT / "workers" / "social-executor" / "src" / "index.js"
STORE_LINK_VERIFIER = ROOT / "scripts" / "verify_pending_store_links.py"
SPOTIFY_SEARCH_VERIFIER = ROOT / "scripts" / "search_spotify_release.py"
YOUTUBE_MUSIC_SEARCH_VERIFIER = ROOT / "scripts" / "search_youtube_music_release.py"
METRICS_HISTORY_UPDATER = ROOT / "scripts" / "update_metrics_history.py"
EXECUTOR_READINESS_CAPTURE = ROOT / "scripts" / "capture_executor_readiness.py"
SOCIAL_EXECUTION_CAPTURE = ROOT / "scripts" / "capture_social_executions.py"
SOCIAL_EXECUTION_EXPORT = ROOT / "scripts" / "export_social_executions.py"
SOCIAL_SCHEDULER_CAPTURE = ROOT / "scripts" / "capture_scheduler_dry_run.py"
SOCIAL_EXECUTION_RESET = ROOT / "scripts" / "reset_social_execution_state.py"
PROMO_REFRESH_SCRIPT = ROOT / "scripts" / "refresh_promo_admin.py"
PROMO_REFRESH_WORKFLOW_CAPTURE = ROOT / "scripts" / "capture_github_workflow_status.py"
PROMO_REFRESH_WORKFLOW = ROOT / ".github" / "workflows" / "promo-admin-refresh.yml"
PROMO_CONSISTENCY_SCRIPT = ROOT / "scripts" / "build_promo_consistency_audit.py"
TIKTOK_SETUP_PREFLIGHT_SCRIPT = ROOT / "scripts" / "build_tiktok_setup_preflight.py"
TIKTOK_REPAIR_RUNBOOK_SCRIPT = ROOT / "scripts" / "build_tiktok_repair_runbook.py"
PROMO_OPERATIONS_SCRIPT = ROOT / "scripts" / "build_promo_operations_packet.py"
PUBLISHED_LOG_RECONCILIATION_SCRIPT = ROOT / "scripts" / "build_published_log_reconciliation.py"
HUMAN_HANDOFF_SCRIPT = ROOT / "scripts" / "build_human_handoff_packet.py"
PROMOTION_BLOCKER_LEDGER_SCRIPT = ROOT / "scripts" / "build_promotion_blocker_ledger.py"
PLATFORM_REPAIR_SCRIPT = ROOT / "scripts" / "build_platform_repair_status.py"
APPROVAL_RUNWAY_SCRIPT = ROOT / "scripts" / "build_approval_runway.py"
SCHEDULED_APPROVAL_SCRIPT = ROOT / "scripts" / "build_scheduled_approval_packet.py"
SUBSCRIBER_CTA_AUDIT_SCRIPT = ROOT / "scripts" / "build_subscriber_cta_audit.py"
MANUAL_DISTRIBUTION_PACKET_SCRIPT = ROOT / "scripts" / "build_manual_distribution_packet.py"
MONETIZATION_ACTIVATION_SCRIPT = ROOT / "scripts" / "build_monetization_activation_plan.py"
BACKLOG_RESCHEDULE_PREVIEW_SCRIPT = ROOT / "scripts" / "build_backlog_reschedule_preview.py"
MANUAL_METRIC_COLLECTION_SCRIPT = ROOT / "scripts" / "build_manual_metric_collection.py"
REPORT = ROOT / "admin" / "reports" / "weekly-social-report.md"
PROMO_CONSISTENCY_REPORT = ROOT / "admin" / "reports" / "promo-consistency-audit.md"
TIKTOK_SETUP_PREFLIGHT_REPORT = ROOT / "admin" / "reports" / "tiktok-setup-preflight.md"
TIKTOK_REPAIR_RUNBOOK_REPORT = ROOT / "admin" / "reports" / "tiktok-repair-runbook.md"
PROMO_OPERATIONS_REPORT = ROOT / "admin" / "reports" / "promo-operations-packet.md"
PUBLISHED_LOG_RECONCILIATION_REPORT = ROOT / "admin" / "reports" / "published-log-reconciliation.md"
HUMAN_HANDOFF_REPORT = ROOT / "admin" / "reports" / "human-handoff-packet.md"
PROMOTION_BLOCKER_LEDGER_REPORT = ROOT / "admin" / "reports" / "promotion-blocker-ledger.md"
PLATFORM_REPAIR_REPORT = ROOT / "admin" / "reports" / "platform-repair-status.md"
APPROVAL_RUNWAY_REPORT = ROOT / "admin" / "reports" / "approval-runway.md"
SCHEDULED_APPROVAL_REPORT = ROOT / "admin" / "reports" / "scheduled-approval-packet.md"
SUBSCRIBER_CTA_AUDIT_REPORT = ROOT / "admin" / "reports" / "subscriber-cta-audit.md"
MANUAL_DISTRIBUTION_REPORT = ROOT / "admin" / "reports" / "manual-distribution-packet.md"
MONETIZATION_ACTIVATION_REPORT = ROOT / "admin" / "reports" / "monetization-activation-plan.md"
BACKLOG_RESCHEDULE_PREVIEW_REPORT = ROOT / "admin" / "reports" / "backlog-reschedule-preview.md"
MANUAL_METRIC_REPORT = ROOT / "admin" / "reports" / "manual-metric-collection.md"
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


def cta_strength(text):
    lower = str(text or "").lower()
    has_hard = any(term in lower for term in ("subscribe", "subscribers", "1,000", "1000"))
    has_youtube = any(term in lower for term in ("youtube", "youtu.be", "youtube.com"))
    if has_hard and has_youtube:
        return "hard_subscribe"
    if has_hard:
        return "hard_goal"
    if has_youtube:
        return "youtube_link"
    if "playlist" in lower or "stream" in lower or "listen" in lower:
        return "soft_listen"
    return "missing"


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
    if SOCIAL_SCHEDULER_DRY_RUN.exists():
        scheduler_snapshot = json.loads(SOCIAL_SCHEDULER_DRY_RUN.read_text(encoding="utf-8"))
        summary = scheduler_snapshot.get("summary") or {}
        if scheduler_snapshot.get("dry_run") is True and "updated_at" in scheduler_snapshot and "would_post_count" in summary and "blocked_count" in summary:
            ok(f"social scheduler dry-run tracks {summary.get('result_count')} due result(s)")
        else:
            fail("social_scheduler_dry_run.json missing dry-run summary or timestamp", failures)
    else:
        fail("social_scheduler_dry_run.json missing; run scripts/capture_scheduler_dry_run.py", failures)
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
    if PROMO_REFRESH_WORKFLOW_STATUS.exists():
        workflow_status = json.loads(PROMO_REFRESH_WORKFLOW_STATUS.read_text(encoding="utf-8"))
        if workflow_status.get("source") == "github-actions-workflow-runs" and workflow_status.get("workflow") == "promo-admin-refresh.yml" and "latest_run" in workflow_status and "recent_runs" in workflow_status:
            ok("promo refresh workflow status snapshot present")
        else:
            fail("promo_refresh_workflow_status.json missing workflow run status fields", failures)
    else:
        fail("promo_refresh_workflow_status.json missing; run scripts/capture_github_workflow_status.py", failures)
    if PROMO_CONSISTENCY_AUDIT.exists():
        consistency = json.loads(PROMO_CONSISTENCY_AUDIT.read_text(encoding="utf-8"))
        summary = consistency.get("summary") or {}
        checks = consistency.get("checks") or []
        source = consistency.get("source") or {}
        if (
            consistency.get("safe_mode") is True
            and summary.get("check_count") == len(checks)
            and summary.get("passed") + summary.get("failed") == len(checks)
            and summary.get("status") == "pass"
            and summary.get("failed") == 0
            and all(check.get("name") and check.get("status") in {"pass", "fail"} and check.get("detail") for check in checks)
            and {"promo_engine_status", "promo_operations_packet", "promotion_blocker_ledger", "human_handoff_packet", "social_execution_snapshot", "social_scheduler_dry_run", "tiktok_setup_preflight"} <= set(source)
        ):
            ok(f"promo consistency audit passes {len(checks)} cross-surface check(s)")
        else:
            fail("promo_consistency_audit.json missing passing safe cross-surface checks", failures)
    else:
        fail("promo_consistency_audit.json missing; run scripts/build_promo_consistency_audit.py", failures)
    if TIKTOK_SETUP_PREFLIGHT.exists():
        preflight = json.loads(TIKTOK_SETUP_PREFLIGHT.read_text(encoding="utf-8"))
        summary = preflight.get("summary") or {}
        checks = preflight.get("checks") or []
        source = preflight.get("source") or {}
        blocked_count = sum(1 for check in checks if check.get("status") == "blocked")
        check_names = {check.get("name") for check in checks}
        required_checks = {
            "local_refresh_credentials",
            "worker_refresh_credentials",
            "worker_token_path",
            "public_posting_approval",
            "default_privacy",
            "admin_refresh_after_repair",
        }
        required_source = {"local_secret_source", "executor_readiness", "platform_repair_status", "wrangler_config"}
        if (
            preflight.get("safe_mode") is True
            and summary.get("status") in {"ready", "blocked"}
            and summary.get("check_count") == len(checks)
            and summary.get("blocked_count") == blocked_count
            and required_checks <= check_names
            and required_source <= set(source)
            and "Secret values" in (preflight.get("redaction") or "")
            and all(check.get("name") and check.get("status") in {"pass", "blocked", "review", "waiting"} and check.get("detail") for check in checks)
        ):
            ok(f"tiktok_setup_preflight.json tracks {len(checks)} safe setup check(s)")
        else:
            fail("tiktok_setup_preflight.json missing safe setup preflight checks", failures)
    else:
        fail("tiktok_setup_preflight.json missing; run scripts/build_tiktok_setup_preflight.py", failures)
    if TIKTOK_REPAIR_RUNBOOK.exists():
        runbook = json.loads(TIKTOK_REPAIR_RUNBOOK.read_text(encoding="utf-8"))
        summary = runbook.get("summary") or {}
        steps = runbook.get("steps") or []
        source = runbook.get("source") or {}
        blocked_count = sum(1 for step in steps if step.get("status") == "blocked")
        phases = {step.get("phase") for step in steps}
        step_ids = {step.get("id") for step in steps}
        required_steps = {
            "collect_local_oauth_credentials",
            "confirm_public_posting_approval",
            "preview_worker_secret_push",
            "apply_worker_secret_push",
            "recapture_readiness",
            "clear_backlog_gate",
        }
        required_source = {"tiktok_setup_preflight", "platform_repair_status", "executor_readiness", "backlog_reschedule_preview", "wrangler_config"}
        required_phases = {"Collect credentials", "Confirm approval", "Preview push", "Apply push", "Verify repair", "Clear gate"}
        if (
            runbook.get("safe_mode") is True
            and runbook.get("status") in {"blocked", "ready_for_apply", "ready_for_backlog_clearance"}
            and summary.get("step_count") == len(steps)
            and summary.get("blocked_step_count") == blocked_count
            and summary.get("phase_count") == len(phases)
            and required_steps <= step_ids
            and required_phases <= phases
            and required_source <= set(source)
            and set(summary.get("required_secret_names") or []) == {"TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REFRESH_TOKEN"}
            and "--approved-backlog" in (summary.get("backlog_preview_command") or "")
            and "--approved-only" not in json.dumps(runbook)
            and "Secret values" in (runbook.get("redaction") or "")
            and all(step.get("id") and step.get("phase") and step.get("title") and step.get("status") in {"pass", "ready", "waiting", "blocked"} and step.get("detail") for step in steps)
        ):
            ok(f"tiktok_repair_runbook.json tracks {len(steps)} guarded repair step(s)")
        else:
            fail("tiktok_repair_runbook.json missing guarded TikTok repair sequence", failures)
    else:
        fail("tiktok_repair_runbook.json missing; run scripts/build_tiktok_repair_runbook.py", failures)
    if PROMO_OPERATIONS_PACKET.exists():
        packet = json.loads(PROMO_OPERATIONS_PACKET.read_text(encoding="utf-8"))
        summary = packet.get("summary") or {}
        actions = packet.get("actions") or []
        if packet.get("safe_mode") is True and summary.get("action_count") == len(actions):
            ok(f"promo operations packet tracks {len(actions)} action(s)")
        else:
            fail("promo_operations_packet.json missing safe summary or action count", failures)
        if summary.get("phases") and summary.get("urgencies") and summary.get("next_action") and packet.get("next_action") == summary.get("next_action"):
            ok("promo operations packet summarizes phases and urgency")
        else:
            fail("promo_operations_packet.json missing phase or urgency summary", failures)
        action_kinds = {action.get("kind") for action in actions}
        required_kinds = {"approval_review", "store_verification", "manual_metrics", "platform_fix"}
        if required_kinds <= action_kinds and all("command" in action and "label" in action and "phase" in action and "urgency" in action for action in actions):
            ok("promo operations packet groups approval, store, metric, and platform work")
        else:
            fail("promo_operations_packet.json missing required action groups", failures)
        status = json.loads(PROMO_ENGINE_STATUS.read_text(encoding="utf-8")) if PROMO_ENGINE_STATUS.exists() else {}
        monetization = (status.get("kpi") or {}).get("monetization") or {}
        backlog_actions = [
            action for action in actions
            if action.get("kind") == "backlog_reschedule"
        ]
        if int(monetization.get("approved_backlog_posts") or 0):
            if (
                backlog_actions
                and all("--apply" not in (action.get("command") or "") for action in backlog_actions)
                and all(
                    (
                        ((action.get("context") or {}).get("apply_allowed_without_override") and (action.get("context") or {}).get("apply_command"))
                        or (
                            not (action.get("context") or {}).get("apply_allowed_without_override")
                            and not (action.get("context") or {}).get("apply_command")
                            and (action.get("context") or {}).get("blocked_apply_command")
                            and (action.get("context") or {}).get("override_apply_command")
                        )
                    )
                    for action in backlog_actions
                )
                and all("Normal apply is hidden" in ((action.get("context") or {}).get("note") or "") or "Safe apply is available" in ((action.get("context") or {}).get("note") or "") for action in backlog_actions)
                and summary.get("backlog_reschedules") == len(backlog_actions)
            ):
                ok("promo operations packet includes dry-run backlog reschedule action")
            else:
                fail("promo_operations_packet.json missing dry-run backlog reschedule action", failures)
        scheduled_batch_actions = [
            action for action in actions
            if action.get("kind") == "scheduled_approval_batch"
        ]
        scheduled_packet = json.loads(SCHEDULED_APPROVAL_PACKET.read_text(encoding="utf-8")) if SCHEDULED_APPROVAL_PACKET.exists() else {}
        scheduled_manifest = scheduled_packet.get("approval_decision_manifest") or {}
        if int((scheduled_packet.get("summary") or {}).get("approval_blocker_count") or 0):
            if (
                scheduled_batch_actions
                and summary.get("scheduled_approval_batches") == len(scheduled_batch_actions)
                and all("--dry-run" in (action.get("command") or "") for action in scheduled_batch_actions)
                and all("--dry-run" not in ((action.get("context") or {}).get("apply_command") or "") for action in scheduled_batch_actions)
                and all((action.get("context") or {}).get("approval_blocker_count") for action in scheduled_batch_actions)
                and all((action.get("context") or {}).get("checked_batch_ids") == ((scheduled_packet.get("summary") or {}).get("checked_batch_ids") or []) for action in scheduled_batch_actions)
                and all((action.get("context") or {}).get("blocked_review_ids") == ((scheduled_packet.get("summary") or {}).get("blocked_review_ids") or []) for action in scheduled_batch_actions)
                and all((action.get("context") or {}).get("decision_ready_ids") == (scheduled_manifest.get("ready_ids") or []) for action in scheduled_batch_actions)
                and all((action.get("context") or {}).get("decision_held_ids") == (scheduled_manifest.get("held_ids") or []) for action in scheduled_batch_actions)
                and all(((action.get("context") or {}).get("approval_decision_manifest") or {}).get("decisions") == (scheduled_manifest.get("decisions") or []) for action in scheduled_batch_actions)
                and all("--checked-batch" in ((action.get("context") or {}).get("decision_guardrail") or "") for action in scheduled_batch_actions)
                and all(
                    not int((scheduled_packet.get("summary") or {}).get("review_check_passed_count") or 0)
                    or action.get("command") == (scheduled_packet.get("summary") or {}).get("checked_batch_preview_command")
                    for action in scheduled_batch_actions
                )
            ):
                ok("promo operations packet includes scheduled approval batch preview")
            else:
                fail("promo_operations_packet.json missing scheduled approval batch preview", failures)
        approval_review_actions = [
            action for action in actions
            if action.get("kind") == "approval_review"
        ]
        if approval_review_actions and all(
            "--dry-run" in (action.get("command") or "")
            and "--dry-run" not in ((action.get("context") or {}).get("approval_command") or "")
            and ((action.get("context") or {}).get("preview_command") == action.get("command"))
            for action in approval_review_actions
        ):
            ok("promo operations packet uses dry-run approval previews")
        else:
            fail("promo_operations_packet.json approval review actions missing dry-run previews", failures)
        secret_platform_fix_actions = [
            action for action in actions
            if action.get("kind") == "platform_fix"
            and (action.get("context") or {}).get("repair_apply_command")
            and (action.get("context") or {}).get("reason") != "max_attempts_exceeded"
        ]
        if secret_platform_fix_actions and all(
            "--dry-run" in (action.get("command") or "")
            and "--dry-run" not in ((action.get("context") or {}).get("repair_apply_command") or "")
            for action in secret_platform_fix_actions
        ):
            ok("promo operations packet uses dry-run secret repair previews")
        else:
            fail("promo_operations_packet.json secret repair actions missing dry-run previews", failures)
        retry_reset_actions = [
            action for action in actions
            if action.get("kind") == "platform_fix"
            and (action.get("context") or {}).get("reason") == "max_attempts_exceeded"
        ]
        if retry_reset_actions:
            if all(
                "reset_social_execution_state.py" in ((action.get("context") or {}).get("retry_reset_preview_command") or "")
                and "check_social_executor_dry_run.py" in ((action.get("context") or {}).get("retry_reset_verification_command") or "")
                and "--apply" not in ((action.get("context") or {}).get("retry_reset_preview_command") or "")
                and "--apply" in ((action.get("context") or {}).get("retry_reset_apply_command") or "")
                and (action.get("context") or {}).get("retry_reset_note")
                for action in retry_reset_actions
            ):
                ok("promo operations packet includes verified retry reset previews for max-attempt rows")
            else:
                fail("promo_operations_packet.json missing verified retry reset previews for max-attempt rows", failures)
        else:
            ok("promo operations packet has no max-attempt retry reset rows")
        tiktok_actions = [
            action for action in actions
            if (action.get("context") or {}).get("platform") == "TikTok"
            and action.get("urgency") in {"blocked", "high"}
        ]
        if tiktok_actions and any(
            (action.get("context") or {}).get("missing_secrets")
            and (action.get("context") or {}).get("local_missing_secrets")
            and (action.get("context") or {}).get("local_secret_source")
            for action in tiktok_actions
        ):
            ok("promo operations packet includes TikTok remote and local missing-secret diagnostics")
        else:
            fail("promo_operations_packet.json missing TikTok remote/local missing-secret diagnostics", failures)
        manual_metric_actions = [
            action for action in actions
            if action.get("kind") == "manual_metrics"
        ]
        if manual_metric_actions and all(
            (action.get("context") or {}).get("priority")
            and (action.get("context") or {}).get("label")
            and (action.get("context") or {}).get("field_count")
            and (action.get("context") or {}).get("access_levels")
            and (action.get("context") or {}).get("csv_rows")
            and (action.get("context") or {}).get("worksheet_import_preview_command")
            and (action.get("context") or {}).get("worksheet_import_command")
            for action in manual_metric_actions
        ):
            ok("promo operations packet links priority-batched manual metric collection and worksheet import")
        else:
            fail("promo_operations_packet.json missing priority-batched manual metric collection/import context", failures)
        checked_store_actions = [
            action for action in actions
            if action.get("kind") == "store_verification"
            and (action.get("context") or {}).get("latest_snapshot")
        ]
        if checked_store_actions and all(
            str(action.get("label") or "").startswith("Re-check ")
            and (action.get("context") or {}).get("checked_at")
            and "Latest snapshot" in ((action.get("context") or {}).get("note") or "")
            for action in checked_store_actions
        ):
            ok("promo operations packet labels checked store snapshots as re-checks")
        else:
            fail("promo_operations_packet.json missing checked store re-check context", failures)
    else:
        fail("promo_operations_packet.json missing; run scripts/build_promo_operations_packet.py", failures)
    if PUBLISHED_LOG_RECONCILIATION.exists():
        reconciliation = json.loads(PUBLISHED_LOG_RECONCILIATION.read_text(encoding="utf-8"))
        reconciliation_summary = reconciliation.get("summary") or {}
        published_rows = read_csv(CONTENT / "Published_Log.csv") if (CONTENT / "Published_Log.csv").exists() else []
        worker = reconciliation.get("worker_export") or {}
        manual = reconciliation.get("manual_logging") or {}
        manual_packet = json.loads(MANUAL_DISTRIBUTION_PACKET.read_text(encoding="utf-8")) if MANUAL_DISTRIBUTION_PACKET.exists() else {}
        expected_unlogged_manual = int((manual_packet.get("summary") or {}).get("unlogged_manual_count") or 0)
        manual_approval_docket = manual_packet.get("manual_approval_docket") or {}
        manual_distribution_docket = manual_packet.get("manual_distribution_docket") or {}
        manual_rows = manual.get("rows") or []
        gate_counts = {}
        for row in manual_rows:
            gate = row.get("log_gate") or "unknown"
            gate_counts[gate] = gate_counts.get(gate, 0) + 1
        approval_gate = manual.get("approval_gate") or {}
        posting_gate = manual.get("posting_gate") or {}
        if (
            reconciliation.get("safe_mode") is True
            and reconciliation_summary.get("published_log_rows") == len(published_rows)
            and reconciliation_summary.get("unlogged_worker_posts") == worker.get("unlogged_worker_count")
            and reconciliation_summary.get("unlogged_manual_posts") == manual.get("unlogged_manual_count") == expected_unlogged_manual
            and reconciliation_summary.get("manual_log_gate_counts") == dict(sorted(gate_counts.items()))
            and reconciliation_summary.get("manual_logging_gate_status") == (manual_distribution_docket.get("status") or "unknown")
            and reconciliation_summary.get("next_gate") in {"worker_export", "manual_approval", "clear"}
            and reconciliation_summary.get("posting_gate_status") == (posting_gate.get("status") or "unknown")
            and "export_social_executions.py --dry-run" in (worker.get("preview_command") or "")
            and "export_social_executions.py --refresh-admin" in (worker.get("apply_command") or "")
            and (
                reconciliation_summary.get("next_gate") != "manual_approval"
                or reconciliation_summary.get("next_preview_command") == (approval_gate.get("preview_command") or "")
            )
            and approval_gate.get("ready_ids") == (manual_approval_docket.get("ready_ids") or [])
            and approval_gate.get("blocked_ids") == (manual_approval_docket.get("blocked_ids") or [])
            and approval_gate.get("preview_command") == (manual_approval_docket.get("preview_command") or "")
            and approval_gate.get("apply_command") == (manual_approval_docket.get("apply_command") or "")
            and posting_gate.get("review_count") == (manual_distribution_docket.get("review_count") or 0)
            and posting_gate.get("postable_count") == (manual_distribution_docket.get("postable_count") or 0)
            and all(row.get("log_gate") in {"blocked_until_manual_approval", "blocked_until_public_url", "ready_to_log"} and row.get("next_step") and "PUBLIC_URL" in (row.get("log_preview_command") or "") and "--apply" in (row.get("log_apply_command") or "") for row in manual_rows)
            and manual.get("guardrail")
        ):
            ok("published log reconciliation packages Worker export and manual URL logging checks")
        else:
            fail("published_log_reconciliation.json missing safe published-log reconciliation data", failures)
    else:
        fail("published_log_reconciliation.json missing; run scripts/build_published_log_reconciliation.py", failures)
    if HUMAN_HANDOFF_PACKET.exists():
        handoff = json.loads(HUMAN_HANDOFF_PACKET.read_text(encoding="utf-8"))
        summary = handoff.get("summary") or {}
        tasks = handoff.get("tasks") or []
        docket = handoff.get("action_docket") or {}
        docket_checklist = docket.get("checklist") or []
        phases = {task.get("phase") for task in tasks}
        owners = summary.get("owner_counts") or {}
        urgencies = summary.get("urgency_counts") or {}
        approval_task = next((task for task in tasks if task.get("id") == "approve-checked-scheduled-batch"), {})
        approval_impact = approval_task.get("impact") or {}
        blocker_projection = ((summary.get("blocker_summary") or {}).get("next_resolution_projection") or {})
        approval_runway = json.loads(APPROVAL_RUNWAY.read_text(encoding="utf-8")) if APPROVAL_RUNWAY.exists() else {}
        manual_approval_docket = approval_runway.get("manual_approval_docket") or {}
        manual_posting_step = next((item for item in docket_checklist if item.get("id") == "manual-posting-review"), {})
        metric_task_field_count = sum(int((task.get("impact") or {}).get("field_count") or 0) for task in tasks if task.get("phase") == "Manual metrics")
        if (
            handoff.get("safe_mode") is True
            and summary.get("task_count") == len(tasks)
            and sum(int(value or 0) for value in owners.values()) == len(tasks)
            and sum(int(value or 0) for value in urgencies.values()) == len(tasks)
            and {"Approval", "Manual distribution", "Manual metrics", "Platform setup", "Backlog recovery"} <= phases
            and all(task.get("id") and task.get("title") and task.get("owner") and task.get("urgency") and task.get("status") and task.get("source_path") for task in tasks)
            and approval_task
            and "--checked-batch" in approval_task.get("apply_command", "")
            and approval_impact.get("checked_ids") == blocker_projection.get("checked_ids")
            and approval_impact.get("blocked_ids_retained") == blocker_projection.get("blocked_ids_retained")
            and approval_impact.get("blockers_resolved") == blocker_projection.get("blockers_resolved")
            and approval_impact.get("approval_blockers_before") == blocker_projection.get("approval_blockers_before")
            and approval_impact.get("approval_blockers_after") == blocker_projection.get("approval_blockers_after")
            and approval_impact.get("auto_rows_unblocked") == blocker_projection.get("auto_rows_unblocked")
            and approval_impact.get("manual_rows_unblocked") == blocker_projection.get("manual_rows_unblocked")
            and docket.get("task_count") == len(tasks)
            and docket.get("roadmap_step_count") == len((summary.get("blocker_summary") or {}).get("blocker_unlock_roadmap") or [])
            and docket.get("ready_step_count") == len([item for item in docket_checklist if item.get("state") in {"ready", "ready_for_review", "needs_review", "needs_values"}])
            and docket.get("blocked_step_count") == len([item for item in docket_checklist if item.get("state") == "blocked"])
            and (docket.get("first_ready_step") or {}).get("id") == "review-checked-approval-batch"
            and manual_posting_step
            and manual_posting_step.get("ready_ids") == (manual_approval_docket.get("ready_ids") or [])
            and manual_posting_step.get("blocked_ids") == (manual_approval_docket.get("blocked_ids") or [])
            and manual_posting_step.get("preview_command") == (manual_approval_docket.get("preview_command") or "")
            and manual_posting_step.get("apply_command") == (manual_approval_docket.get("apply_command") or "")
            and manual_approval_docket.get("guardrail") in manual_posting_step.get("guardrail", "")
            and any(item.get("id") == "manual-metric-worksheet" and item.get("field_count") == metric_task_field_count and "--from-csv --dry-run" in item.get("preview_command", "") for item in docket_checklist)
            and any(item.get("id") == "platform-repair-gate" and item.get("state") == "blocked" and "push_social_worker_secrets.py --dry-run" in item.get("preview_command", "") for item in docket_checklist)
            and all(
                item.get("completion_evidence")
                and item.get("next_step_after_apply")
                and item.get("command_sequence")
                and (not item.get("apply_command") or any(sequence_item.get("step") == "apply_after_review" and sequence_item.get("command") == item.get("apply_command") for sequence_item in item.get("command_sequence") or []))
                and (not item.get("preview_command") or any(sequence_item.get("step") == "preview" and sequence_item.get("command") == item.get("preview_command") for sequence_item in item.get("command_sequence") or []))
                for item in docket_checklist
                if item.get("state") != "clear"
            )
            and any(task.get("phase") == "Manual metrics" and (task.get("impact") or {}).get("pending_assignments") for task in tasks)
            and any(task.get("phase") == "Platform setup" and (task.get("impact") or {}).get("missing_secrets") for task in tasks)
            and any(task.get("phase") == "Platform setup" and (task.get("impact") or {}).get("platform") == "TikTok" and (task.get("impact") or {}).get("preflight_status") and (task.get("impact") or {}).get("preflight_command") and (task.get("impact") or {}).get("preflight_report") for task in tasks)
        ):
            ok(f"human handoff packet packages {len(tasks)} human task(s)")
        else:
            fail("human_handoff_packet.json missing safe consolidated handoff tasks", failures)
    else:
        fail("human_handoff_packet.json missing; run scripts/build_human_handoff_packet.py", failures)
    if PLATFORM_REPAIR_STATUS.exists():
        repair_status = json.loads(PLATFORM_REPAIR_STATUS.read_text(encoding="utf-8"))
        repair_summary = repair_status.get("summary") or {}
        repair_rows = repair_status.get("rows") or []
        packet = json.loads(PROMO_OPERATIONS_PACKET.read_text(encoding="utf-8")) if PROMO_OPERATIONS_PACKET.exists() else {}
        platform_actions = [
            action for action in packet.get("actions") or []
            if action.get("kind") == "platform_fix"
        ]
        tiktok_rows = [
            row for row in repair_rows
            if str(row.get("platform") or "").lower() == "tiktok"
        ]
        if (
            repair_status.get("safe_mode") is True
            and repair_summary.get("platform_fix_count") == len(repair_rows) == len(platform_actions)
            and repair_summary.get("preview_command_count") == len([row for row in repair_rows if row.get("preview_command")])
            and repair_summary.get("retry_reset_count") == len([row for row in repair_rows if row.get("retry_reset_preview_command")])
            and repair_summary.get("checklist_item_count") == sum(len(row.get("repair_checklist") or []) for row in repair_rows)
            and repair_summary.get("checklist_blocked_count") == sum(int(row.get("repair_checklist_blocked_count") or 0) for row in repair_rows)
            and all(
                row.get("post_id")
                and row.get("platform")
                and row.get("priority")
                and row.get("repair_action")
                and row.get("preview_command")
                and row.get("repair_checklist")
                and all(item.get("id") and item.get("label") and item.get("status") and item.get("detail") for item in row.get("repair_checklist") or [])
                for row in repair_rows
            )
            and all(row.get("preflight_status") and row.get("preflight_command") and row.get("preflight_report") for row in tiktok_rows)
        ):
            ok(f"platform repair status tracks {len(repair_rows)} blocked platform repair(s)")
        else:
            fail("platform_repair_status.json missing repair row summary or preview commands", failures)
    else:
        fail("platform_repair_status.json missing; run scripts/build_platform_repair_status.py", failures)
    if APPROVAL_RUNWAY.exists():
        runway = json.loads(APPROVAL_RUNWAY.read_text(encoding="utf-8"))
        summary = runway.get("summary") or {}
        rows = runway.get("rows") or []
        recommended = summary.get("recommended_ids") or []
        recommended_manual = summary.get("recommended_manual_ids") or []
        blocked_ids = summary.get("blocked_ids") or []
        manual_docket = runway.get("manual_approval_docket") or {}
        manual_rows = [row for row in rows if row.get("readiness_state") == "manual_only"]
        blocked_rows = [row for row in rows if row.get("readiness_state") == "blocked"]
        if (
            runway.get("safe_mode") is True
            and summary.get("review_count") == len(rows)
            and summary.get("ready_after_approval") == len(recommended)
            and summary.get("recommended_manual_approval_count") == len(recommended_manual) == len(manual_rows)
            and summary.get("recommended_approval_count") == len(recommended) + len(recommended_manual)
            and blocked_ids == [row.get("id") for row in blocked_rows]
            and manual_docket.get("ready_ids") == recommended_manual
            and manual_docket.get("blocked_ids") == blocked_ids
            and "approve_promo_queue_plan.py" in (manual_docket.get("preview_command") or "")
            and "--dry-run" in (manual_docket.get("preview_command") or "")
            and "approve_promo_queue_plan.py" in (manual_docket.get("apply_command") or "")
            and "--refresh-admin" in (manual_docket.get("apply_command") or "")
            and manual_docket.get("guardrail")
            and all(row.get("approval_preview_command") and "--dry-run" in row.get("approval_preview_command", "") for row in rows)
        ):
            ok(f"approval runway ranks {len(rows)} draft approval(s)")
        else:
            fail("approval_runway.json missing safe approval runway summary or dry-run previews", failures)
    else:
        fail("approval_runway.json missing; run scripts/build_approval_runway.py", failures)
    if SCHEDULED_APPROVAL_PACKET.exists():
        approval_packet = json.loads(SCHEDULED_APPROVAL_PACKET.read_text(encoding="utf-8"))
        summary = approval_packet.get("summary") or {}
        rows = approval_packet.get("rows") or []
        checked_rows = [row for row in rows if row.get("review_check_passed")]
        blocked_rows = [row for row in rows if not row.get("review_check_passed")]
        checked_batch_effect = summary.get("checked_batch_effect") or {}
        batch_effect = summary.get("batch_effect") or {}
        checked_effects = checked_batch_effect.get("effects") or []
        batch_effects = batch_effect.get("effects") or []
        docket = approval_packet.get("approval_docket") or {}
        ready_docket = docket.get("ready_to_approve") or []
        held_docket = docket.get("held") or []
        decision_manifest = approval_packet.get("approval_decision_manifest") or {}
        decisions = decision_manifest.get("decisions") or []
        ready_decisions = [item for item in decisions if item.get("decision") == "ready_to_approve"]
        held_decisions = [item for item in decisions if item.get("decision") == "held"]
        if (
            approval_packet.get("safe_mode") is True
            and summary.get("approval_blocker_count") == len(rows)
            and summary.get("review_check_passed_count") + summary.get("review_check_blocked_count") == len(rows)
            and summary.get("checked_batch_ids") == [row.get("id") for row in checked_rows]
            and summary.get("blocked_review_ids") == [row.get("id") for row in blocked_rows]
            and isinstance(summary.get("review_check_status_counts"), dict)
            and checked_batch_effect.get("row_count") == len(checked_rows)
            and checked_batch_effect.get("ids") == [row.get("id") for row in checked_rows]
            and checked_batch_effect.get("change_count") == len([item for item in checked_effects if (item.get("effect") or {}).get("changed")])
            and docket.get("status") in {"ready_for_review", "blocked"}
            and docket.get("ready_count") == len(checked_rows)
            and docket.get("held_count") == len(blocked_rows)
            and [item.get("id") for item in ready_docket] == [row.get("id") for row in checked_rows]
            and [item.get("id") for item in held_docket] == [row.get("id") for row in blocked_rows]
            and docket.get("checked_batch_preview_command") == summary.get("checked_batch_preview_command")
            and docket.get("checked_batch_apply_command") == summary.get("checked_batch_apply_command")
            and (docket.get("checked_batch_effect") or {}).get("ids") == checked_batch_effect.get("ids")
            and all(item.get("paste_text") and item.get("asset_url") and item.get("destination_links") and item.get("preview_command") and item.get("apply_command") for item in ready_docket)
            and all(item.get("failed_review_checks") for item in held_docket)
            and decision_manifest.get("status") == docket.get("status")
            and decision_manifest.get("ready_ids") == [row.get("id") for row in checked_rows]
            and decision_manifest.get("held_ids") == [row.get("id") for row in blocked_rows]
            and (decision_manifest.get("expected_checked_batch_effect") or {}).get("ids") == checked_batch_effect.get("ids")
            and decision_manifest.get("review_command") == summary.get("checked_batch_preview_command")
            and decision_manifest.get("apply_after_review_command") == summary.get("checked_batch_apply_command")
            and "--checked-batch" in (decision_manifest.get("guardrail") or "")
            and [item.get("id") for item in ready_decisions] == [row.get("id") for row in checked_rows]
            and [item.get("id") for item in held_decisions] == [row.get("id") for row in blocked_rows]
            and all(item.get("checked_batch_member") is True and item.get("post_approval_next_step") and (item.get("approval_effect") or {}).get("to") == "yes" for item in ready_decisions)
            and all(item.get("checked_batch_member") is False and item.get("failed_check_names") and item.get("post_approval_next_step") for item in held_decisions)
            and batch_effect.get("row_count") == len(rows)
            and batch_effect.get("ids") == [row.get("id") for row in rows]
            and batch_effect.get("change_count") == len([item for item in batch_effects if (item.get("effect") or {}).get("changed")])
            and (
                not summary.get("review_check_passed_count")
                or (
                    summary.get("checked_batch_preview_command")
                    and "--dry-run" in summary.get("checked_batch_preview_command", "")
                    and "--checked-batch" in summary.get("checked_batch_preview_command", "")
                    and summary.get("checked_batch_apply_command")
                    and "--refresh-admin" in summary.get("checked_batch_apply_command", "")
                    and "--checked-batch" in summary.get("checked_batch_apply_command", "")
                    and summary.get("checked_batch_explicit_preview_command")
                    and "--dry-run" in summary.get("checked_batch_explicit_preview_command", "")
                    and summary.get("checked_batch_explicit_apply_command")
                    and "--refresh-admin" in summary.get("checked_batch_explicit_apply_command", "")
                )
            )
            and summary.get("preview_command_count") == len([row for row in rows if row.get("approval_preview_command")])
            and summary.get("apply_command_count") == len([row for row in rows if row.get("approval_apply_command")])
            and all(
                row.get("id")
                and row.get("platform")
                and row.get("copy_block")
                and row.get("asset_url")
                and row.get("review_checks")
                and (row.get("approval_effect") or {}).get("field") == "approved"
                and (row.get("approval_effect") or {}).get("to") == "yes"
                and isinstance((row.get("approval_effect") or {}).get("changed"), bool)
                and row.get("approval_review_status") in {"checked_batch_ready", "held_by_failed_checks", "needs_manual_review"}
                and row.get("checked_batch_member") is (row.get("approval_review_status") == "checked_batch_ready")
                and isinstance(row.get("failed_review_checks"), list)
                and row.get("approval_batch_reason")
                and (row.get("approval_review_status") != "held_by_failed_checks" or row.get("failed_review_checks"))
                and {"copy_present", "destination_links_present", "asset_file_present", "executor_blocker_confirmed", "platform_readiness"} <= {check.get("name") for check in row.get("review_checks", [])}
                and "--dry-run" in row.get("approval_preview_command", "")
                and "--refresh-admin" in row.get("approval_apply_command", "")
                for row in rows
            )
        ):
            ok(f"scheduled approval packet packages {len(rows)} approval blocker(s)")
        else:
            fail("scheduled_approval_packet.json missing safe approval blocker rows or commands", failures)
    else:
        fail("scheduled_approval_packet.json missing; run scripts/build_scheduled_approval_packet.py", failures)
    if SUBSCRIBER_CTA_AUDIT.exists():
        cta_audit = json.loads(SUBSCRIBER_CTA_AUDIT.read_text(encoding="utf-8"))
        summary = cta_audit.get("summary") or {}
        rows = cta_audit.get("rows") or []
        if (
            cta_audit.get("safe_mode") is True
            and summary.get("draft_count") == len(rows)
            and "subscriber_swap_count" in summary
            and all("selected_strength" in row and "recommended_strength" in row and "needs_subscriber_cta_swap" in row for row in rows)
        ):
            ok(f"subscriber CTA audit checks {len(rows)} draft CTA(s)")
        else:
            fail("subscriber_cta_audit.json missing safe CTA summary or row classifications", failures)
    else:
        fail("subscriber_cta_audit.json missing; run scripts/build_subscriber_cta_audit.py", failures)
    if MANUAL_DISTRIBUTION_PACKET.exists():
        manual_packet = json.loads(MANUAL_DISTRIBUTION_PACKET.read_text(encoding="utf-8"))
        summary = manual_packet.get("summary") or {}
        rows = manual_packet.get("rows") or []
        hard_rows = [row for row in rows if row.get("selected_cta_strength") in {"hard_subscribe", "hard_goal"}]
        logged_rows = [row for row in rows if row.get("logged")]
        unlogged_rows = [row for row in rows if not row.get("logged")]
        review_rows = [row for row in unlogged_rows if (row.get("manual_posting_packet") or {}).get("approval_required")]
        postable_rows = [row for row in unlogged_rows if (row.get("manual_posting_packet") or {}).get("postable_now")]
        docket = manual_packet.get("manual_distribution_docket") or {}
        approval_runway = json.loads(APPROVAL_RUNWAY.read_text(encoding="utf-8")) if APPROVAL_RUNWAY.exists() else {}
        runway_approval_docket = approval_runway.get("manual_approval_docket") or {}
        approval_docket = manual_packet.get("manual_approval_docket") or {}
        docket_review = docket.get("review_queue") or []
        docket_postable = docket.get("postable_now") or []
        docket_logged = docket.get("logged") or []
        if (
            manual_packet.get("safe_mode") is True
            and summary.get("manual_ready_count") == len(rows)
            and summary.get("youtube_community_count") == len([row for row in rows if row.get("platform") == "YouTube Community"])
            and summary.get("hard_cta_count") == len(hard_rows) == len(rows)
            and summary.get("logged_manual_count") == len(logged_rows)
            and summary.get("unlogged_manual_count") == len(unlogged_rows)
            and summary.get("public_url_log_needed_count") == len([row for row in rows if (row.get("log_effect") or {}).get("would_append")])
            and summary.get("ready_to_post_after_review_count") == len([row for row in unlogged_rows if row.get("readiness_state") == "manual_only"])
            and summary.get("manual_review_required_count") == len(review_rows)
            and summary.get("postable_now_count") == len(postable_rows)
            and summary.get("next_manual_action") in {"review_and_approve", "post_manually_then_log_url", "none"}
            and summary.get("public_community_url") == "https://www.youtube.com/@lilyroo.artist/community"
            and docket.get("status") in {"needs_review", "postable_now", "logged", "empty"}
            and docket.get("review_count") == len(review_rows)
            and docket.get("postable_count") == len(postable_rows)
            and docket.get("logged_count") == len(logged_rows)
            and [item.get("id") for item in docket_review] == [row.get("id") for row in review_rows]
            and [item.get("id") for item in docket_postable] == [row.get("id") for row in postable_rows]
            and [item.get("id") for item in docket_logged] == [row.get("id") for row in logged_rows]
            and docket.get("next_manual_action") == summary.get("next_manual_action")
            and docket.get("public_community_url") == "https://www.youtube.com/@lilyroo.artist/community"
            and approval_docket.get("ready_ids") == (runway_approval_docket.get("ready_ids") or [])
            and approval_docket.get("blocked_ids") == (runway_approval_docket.get("blocked_ids") or [])
            and approval_docket.get("preview_command") == (runway_approval_docket.get("preview_command") or "")
            and approval_docket.get("apply_command") == (runway_approval_docket.get("apply_command") or "")
            and approval_docket.get("guardrail") == (runway_approval_docket.get("guardrail") or "Manual-only approvals do not auto-post; posting and public URL logging remain separate after review.")
            and approval_docket.get("ready_count") == len(approval_docket.get("ready_to_review") or []) == len(review_rows)
            and all(item.get("id") and item.get("distribution_status") == "waiting_for_review" and item.get("postable_after_approval") is True for item in approval_docket.get("ready_to_review") or [])
            and all(item.get("paste_text") and item.get("asset_url") and item.get("destination_links") and item.get("approval_command") for item in docket_review)
            and all(item.get("paste_text") and item.get("asset_url") and "log_manual_distribution.py" in item.get("log_preview_command", "") and "--apply --refresh-admin" in item.get("log_apply_command", "") for item in docket_postable)
            and all(
                row.get("id")
                and row.get("text")
                and row.get("copy_block")
                and row.get("asset_download_url")
                and row.get("distribution_status") in {"waiting_for_review", "ready_for_manual_post", "logged"}
                and isinstance(row.get("logged"), bool)
                and row.get("approval_preview_command")
                and row.get("manual_workflow")
                and (row.get("log_effect") or {}).get("target") == "admin/content/Published_Log.csv"
                and (row.get("log_effect") or {}).get("content_id") == row.get("id")
                and (row.get("log_effect") or {}).get("url_placeholder") == "PUBLIC_URL"
                and isinstance((row.get("log_effect") or {}).get("would_append"), bool)
                and (row.get("manual_posting_packet") or {}).get("posting_surface") == "YouTube Studio Community"
                and (row.get("manual_posting_packet") or {}).get("public_community_url") == "https://www.youtube.com/@lilyroo.artist/community"
                and (row.get("manual_posting_packet") or {}).get("paste_text") == row.get("copy_block")
                and isinstance((row.get("manual_posting_packet") or {}).get("approval_required"), bool)
                and isinstance((row.get("manual_posting_packet") or {}).get("postable_now"), bool)
                and isinstance((row.get("manual_posting_packet") or {}).get("logging_required"), bool)
                and (row.get("manual_posting_packet") or {}).get("next_action") in {"review_and_approve", "post_manually_then_log_url", "already_logged"}
                and "log_manual_distribution.py" in row.get("log_preview_command", "")
                and "--apply" not in row.get("log_preview_command", "")
                and "--apply --refresh-admin" in row.get("log_apply_command", "")
                for row in rows
            )
        ):
            ok(f"manual distribution packet packages {len(rows)} manual post(s)")
        else:
            fail("manual_distribution_packet.json missing safe manual rows, copy blocks, log commands, hard CTAs, or preview commands", failures)
    else:
        fail("manual_distribution_packet.json missing; run scripts/build_manual_distribution_packet.py", failures)
    if MONETIZATION_ACTIVATION_PLAN.exists():
        activation = json.loads(MONETIZATION_ACTIVATION_PLAN.read_text(encoding="utf-8"))
        summary = activation.get("summary") or {}
        actions = activation.get("actions") or []
        runway = json.loads(APPROVAL_RUNWAY.read_text(encoding="utf-8")) if APPROVAL_RUNWAY.exists() else {}
        runway_summary = runway.get("summary") or {}
        manual_docket = runway.get("manual_approval_docket") or {}
        manual_ready_ids = manual_docket.get("ready_ids") or []
        auto_ready_ids = runway_summary.get("recommended_ids") or []
        manual_action = next(
            (action for action in actions if action.get("phase") == "Approve manual subscriber rows"),
            None,
        )
        if (
            activation.get("safe_mode") is True
            and summary.get("action_count") == len(actions)
            and "ready_subscriber_approval_count" in summary
            and "subscriber_swap_count" in summary
            and summary.get("ready_subscriber_approval_count") == len(auto_ready_ids) + len(manual_ready_ids)
            and summary.get("manual_subscriber_approval_count") == len(manual_ready_ids)
            and summary.get("manual_subscriber_approval_ids") == manual_ready_ids
            and summary.get("manual_subscriber_blocked_ids") == (manual_docket.get("blocked_ids") or [])
            and summary.get("manual_subscriber_approval_preview_command") == (manual_docket.get("preview_command") or "")
            and summary.get("manual_subscriber_approval_apply_command") == (manual_docket.get("apply_command") or "")
            and (
                (not manual_ready_ids and manual_action is None)
                or (
                    manual_ready_ids
                    and manual_action
                    and manual_action.get("status") == manual_docket.get("status")
                    and manual_action.get("command") == manual_docket.get("preview_command")
                    and manual_action.get("after_review_command") == manual_docket.get("apply_command")
                    and (manual_action.get("context") or {}).get("ready_ids") == manual_ready_ids
                    and (manual_action.get("context") or {}).get("guardrail") == manual_docket.get("guardrail")
                )
            )
            and all("phase" in action and "status" in action and "label" in action for action in actions)
        ):
            ok(f"monetization activation plan sequences {len(actions)} action(s)")
        else:
            fail("monetization_activation_plan.json missing safe activation summary or action phases", failures)
    else:
        fail("monetization_activation_plan.json missing; run scripts/build_monetization_activation_plan.py", failures)
    if BACKLOG_RESCHEDULE_PREVIEW.exists():
        backlog_preview = json.loads(BACKLOG_RESCHEDULE_PREVIEW.read_text(encoding="utf-8"))
        summary = backlog_preview.get("summary") or {}
        items = backlog_preview.get("items") or []
        blocked = [item for item in items if item.get("blocked")]
        if (
            backlog_preview.get("safe_mode") is True
            and summary.get("approved_backlog_count") == len(items)
            and summary.get("blocked_backlog_count") == len(blocked)
            and summary.get("clear_to_apply_count") == len(items) - len(blocked)
            and bool(summary.get("apply_allowed_without_override")) == (len(blocked) == 0)
            and summary.get("blocked_ids") == [item.get("id") for item in blocked]
            and summary.get("normal_apply_gate") == ("blocked_until_clearance_steps_complete" if blocked else "clear")
            and isinstance(summary.get("clearance_steps"), list)
            and (
                (not blocked and summary.get("apply_command") and not summary.get("blocked_apply_command") and not summary.get("override_apply_command"))
                or (blocked and not summary.get("apply_command") and summary.get("blocked_apply_command") and "--allow-blocked" in summary.get("override_apply_command", ""))
            )
            and all(
                item.get("id")
                and item.get("current_scheduled_at")
                and item.get("proposed_scheduled_at")
                and "blocks_normal_apply" in item
                and "safe_apply_available" in item
                and isinstance(item.get("clearance_steps"), list)
                and (not item.get("blocked") or item.get("clearance_steps"))
                for item in items
            )
        ):
            ok(f"backlog reschedule preview checks {len(items)} approved backlog row(s)")
        else:
            fail("backlog_reschedule_preview.json missing safe summary, blocker accounting, or proposed rows", failures)
    else:
        fail("backlog_reschedule_preview.json missing; run scripts/build_backlog_reschedule_preview.py", failures)
    if MANUAL_METRIC_TEMPLATE.exists():
        rows = read_csv(MANUAL_METRIC_TEMPLATE)
        required = {
            "platform",
            "field",
            "current_value",
            "new_value",
            "live_value",
            "collection_mode",
            "collection_priority",
            "metric_category",
            "access_level",
            "value_type",
            "example_value",
            "collection_instruction",
            "evidence_hint",
            "source_hint",
            "collection_url",
            "reason",
            "update_assignment",
            "import_effect",
            "platform_update_command",
            "csv_row",
            "ready_to_import",
        }
        if rows and set(rows[0].keys()) >= required:
            ok(f"manual metric CSV template has {len(rows)} pending field(s)")
        else:
            fail("manual_metric_collection_template.csv missing required columns or rows", failures)
        if PROMO_ENGINE_STATUS.exists():
            status = json.loads(PROMO_ENGINE_STATUS.read_text(encoding="utf-8"))
            expected = int((status.get("kpi") or {}).get("pending_manual_metric_fields") or 0)
            if len(rows) == expected:
                ok("manual metric CSV row count matches pending metric KPI")
            else:
                fail("manual_metric_collection_template.csv row count does not match pending metric KPI", failures)
    else:
        fail("manual_metric_collection_template.csv missing; run scripts/build_manual_metric_collection.py", failures)
    if MANUAL_METRIC_PACKET.exists():
        packet = json.loads(MANUAL_METRIC_PACKET.read_text(encoding="utf-8"))
        summary = packet.get("summary") or {}
        platforms = packet.get("platforms") or []
        rows = packet.get("rows") or []
        priority_batches = packet.get("priority_batches") or []
        live_import_rows = [row for row in rows if row.get("collection_mode") == "live_import_available"]
        manual_rows = [row for row in rows if row.get("collection_mode") != "live_import_available"]
        ready_rows = [row for row in rows if row.get("ready_to_import")]
        public_profile_rows = [row for row in rows if row.get("access_level") == "public_profile"]
        private_analytics_rows = [row for row in rows if row.get("access_level") == "private_analytics"]
        docket = packet.get("metric_collection_docket") or {}
        docket_groups = docket.get("platform_groups") or []
        waiting_count = len([row for row in rows if not row.get("ready_to_import")])
        batch_fields = [
            field
            for batch in priority_batches
            for field in (batch.get("fields") or [])
        ]
        if (
            packet.get("safe_mode") is True
            and summary.get("pending_field_count") == len(rows)
            and summary.get("platform_count") == len(platforms)
            and summary.get("priority_batch_count") == len(priority_batches)
            and summary.get("public_profile_field_count") == len(public_profile_rows)
            and summary.get("private_analytics_field_count") == len(private_analytics_rows)
            and summary.get("live_import_available_count") == len(live_import_rows)
            and summary.get("manual_collection_required_count") == len(manual_rows)
            and summary.get("ready_to_import_count") == len(ready_rows)
            and summary.get("preserved_new_value_count") == len(ready_rows)
            and summary.get("csv_path") == "data/manual_metric_collection_template.csv"
            and "--from-live --dry-run" in (summary.get("live_import_preview_command") or "")
            and "--from-live --refresh-admin" in (summary.get("live_import_command") or "")
            and "--from-csv --dry-run" in (summary.get("worksheet_import_preview_command") or "")
            and "--from-csv --refresh-admin" in (summary.get("worksheet_import_command") or "")
            and docket.get("status") in {"needs_values", "ready_to_import"}
            and docket.get("platform_count") == len(platforms)
            and docket.get("ready_to_import_count") == len(ready_rows)
            and docket.get("waiting_field_count") == waiting_count
            and docket.get("csv_path") == "data/manual_metric_collection_template.csv"
            and docket.get("worksheet_import_preview_command") == summary.get("worksheet_import_preview_command")
            and docket.get("worksheet_import_command") == summary.get("worksheet_import_command")
            and [group.get("platform") for group in docket_groups] == [platform.get("platform") for platform in platforms]
            and all(
                group.get("field_count") == len(group.get("fields") or [])
                and group.get("waiting_count") == len([field for field in group.get("fields") or [] if not field.get("ready_to_import")])
                and group.get("ready_to_import_count") == len([field for field in group.get("fields") or [] if field.get("ready_to_import")])
                and group.get("collection_url")
                and isinstance(group.get("priority_summary"), list)
                and group.get("worksheet_import_preview_command")
                and group.get("worksheet_import_command")
                for group in docket_groups
            )
            and priority_batches
            and [batch.get("priority") for batch in priority_batches] == sorted(batch.get("priority") for batch in priority_batches)
            and len(batch_fields) == len(rows)
            and all(
                batch.get("label")
                and batch.get("field_count") == len(batch.get("fields") or [])
                and batch.get("waiting_count") == len([field for field in batch.get("fields") or [] if not field.get("ready_to_import")])
                and batch.get("ready_to_import_count") == len([field for field in batch.get("fields") or [] if field.get("ready_to_import")])
                and batch.get("worksheet_import_preview_command") == summary.get("worksheet_import_preview_command")
                and all(field.get("platform") and field.get("field") and field.get("csv_row") and field.get("evidence_hint") for field in batch.get("fields") or [])
                for batch in priority_batches
            )
            and all(
                platform.get("platform")
                and platform.get("collection_url")
                and platform.get("field_count") == len(platform.get("fields") or [])
                and "live_import_available_count" in platform
                and "manual_collection_required_count" in platform
                and platform.get("ready_to_import_count") == len([field for field in platform.get("fields") or [] if field.get("ready_to_import")])
                and len(platform.get("collection_packets") or []) == len(platform.get("fields") or [])
                and platform.get("pending_assignments")
                and all(field.get("value_type") and field.get("example_value") and field.get("collection_instruction") and field.get("evidence_hint") and field.get("metric_category") and field.get("access_level") and field.get("import_effect") and field.get("csv_row") for field in platform.get("fields") or [])
                and all(packet.get("csv_row") and "ready_to_import" in packet and packet.get("update_assignment") and packet.get("import_effect") and packet.get("evidence_hint") and packet.get("access_level") for packet in platform.get("collection_packets") or [])
                and platform.get("worksheet_import_preview_command")
                for platform in platforms
            )
        ):
            ok(f"manual metric collection packet groups {len(platforms)} platform(s)")
        else:
            fail("manual_metric_collection_packet.json missing safe grouped metric collection data", failures)
    else:
        fail("manual_metric_collection_packet.json missing; run scripts/build_manual_metric_collection.py", failures)
    if PROMOTION_BLOCKER_LEDGER.exists():
        ledger = json.loads(PROMOTION_BLOCKER_LEDGER.read_text(encoding="utf-8"))
        summary = ledger.get("summary") or {}
        ledger_rows = ledger.get("rows") or []
        owner_counts = summary.get("owner_counts") or {}
        category_counts = summary.get("category_counts") or {}
        projection = summary.get("next_resolution_projection") or {}
        roadmap = summary.get("blocker_unlock_roadmap") or []
        roadmap_ids = {item.get("id") for item in roadmap}
        approval_runway = json.loads(APPROVAL_RUNWAY.read_text(encoding="utf-8")) if APPROVAL_RUNWAY.exists() else {}
        manual_approval_docket = approval_runway.get("manual_approval_docket") or {}
        manual_roadmap = next((item for item in roadmap if item.get("id") == "unlock-manual-distribution"), {})
        if (
            ledger.get("safe_mode") is True
            and summary.get("open_blocker_count") == len(ledger_rows)
            and summary.get("urgent_count") == len([row for row in ledger_rows if row.get("urgency") in {"critical", "high"}])
            and owner_counts
            and category_counts
            and projection.get("kind") == "checked_scheduled_approval_batch"
            and isinstance(projection.get("blockers_resolved"), int)
            and isinstance(projection.get("approval_blockers_after"), int)
            and {"unlock-checked-scheduled-approval", "unlock-manual-distribution", "unlock-tiktok-platform-repair", "unlock-backlog-reschedule", "unlock-manual-metrics"} <= roadmap_ids
            and all(
                item.get("id")
                and item.get("phase")
                and item.get("status")
                and item.get("owner") in {"tod", "external_platform", "codex"}
                and isinstance(item.get("blockers_resolved"), int)
                and item.get("unlocks")
                and item.get("source_path")
                for item in roadmap
            )
            and any(item.get("id") == "unlock-checked-scheduled-approval" and item.get("preview_command") == projection.get("preview_command") and item.get("apply_command") == projection.get("apply_command") for item in roadmap)
            and manual_roadmap
            and manual_roadmap.get("preview_command") == (manual_approval_docket.get("preview_command") or "")
            and manual_roadmap.get("apply_command") == (manual_approval_docket.get("apply_command") or "")
            and manual_roadmap.get("blocked_by") == (manual_approval_docket.get("blocked_ids") or [])
            and manual_roadmap.get("guardrail") == (manual_approval_docket.get("guardrail") or "Manual posting and public URL logging remain separate after approval.")
            and any(item.get("id") == "unlock-manual-metrics" and "update_manual_social_stats.py --from-csv --dry-run" in (item.get("preview_command") or "") for item in roadmap)
            and all(
                row.get("id")
                and row.get("blocker_id") == row.get("id")
                and row.get("title")
                and row.get("category")
                and row.get("owner") in {"codex", "tod", "external_platform"}
                and row.get("status")
                and row.get("evidence")
                and row.get("next_step")
                and row.get("source_path")
                and isinstance(row.get("impact") or {}, dict)
                for row in ledger_rows
            )
        ):
            ok(f"promotion blocker ledger tracks {len(ledger_rows)} open blocker(s)")
        else:
            fail("promotion_blocker_ledger.json missing safe owner/category blocker rows", failures)
        if SCHEDULED_APPROVAL_PACKET.exists():
            scheduled_packet = json.loads(SCHEDULED_APPROVAL_PACKET.read_text(encoding="utf-8"))
            scheduled_rows = scheduled_packet.get("rows") or []
            approval_rows = {
                row.get("id"): row
                for row in ledger_rows
                if row.get("category") == "approval"
            }
            if scheduled_rows and all(
                (
                    item.get("review_check_passed")
                    and (approval_rows.get(f"approval-{item.get('id')}") or {}).get("status") == "ready_for_reviewed_approval"
                    and ((approval_rows.get(f"approval-{item.get('id')}") or {}).get("impact") or {}).get("resolves_blocker") is True
                )
                or (
                    not item.get("review_check_passed")
                    and (approval_rows.get(f"approval-{item.get('id')}") or {}).get("status") == "blocked_by_review_checks"
                    and ((approval_rows.get(f"approval-{item.get('id')}") or {}).get("impact") or {}).get("resolves_blocker") is False
                )
                for item in scheduled_rows
            ):
                ok("promotion blocker ledger reflects scheduled approval review checks")
            else:
                fail("promotion_blocker_ledger.json missing scheduled approval review-check statuses", failures)
    else:
        fail("promotion_blocker_ledger.json missing; run scripts/build_promotion_blocker_ledger.py", failures)
    if MANUAL_METRIC_REPORT.exists():
        report_text = MANUAL_METRIC_REPORT.read_text(encoding="utf-8")
        if "Manual Metric Collection" in report_text and "Metric Collection Docket" in report_text and "Pending fields" in report_text and "Open: " in report_text and "--from-csv --refresh-admin" in report_text and "--from-live --dry-run" in report_text:
            ok("manual metric markdown report present")
        else:
            fail("manual-metric-collection.md missing expected sections", failures)
    else:
        fail("manual-metric-collection.md missing; run scripts/build_manual_metric_collection.py", failures)
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
        freshness_statuses = {"fresh", "stale", "missing", "checked_no_change", "gated_manual_pending"}
        summary = freshness.get("summary", {})
        if sources and sum(int(summary.get(state) or 0) for state in freshness_statuses) == len(sources):
            ok(f"promo engine freshness audit tracks {len(sources)} sources")
        else:
            fail("promo_engine_status.json missing source freshness audit", failures)
        for source in sources:
            name = source.get("name") or "[missing source]"
            if source.get("status") not in freshness_statuses:
                fail(f"promo engine freshness source {name} has invalid status", failures)
            for key in ("path", "max_age_hours", "refresh_command"):
                if not str(source.get(key) or "").strip():
                    fail(f"promo engine freshness source {name} missing {key}", failures)
            if source.get("status") == "checked_no_change" and not str(source.get("evidence") or "").strip():
                fail(f"promo engine freshness source {name} missing checked-no-change evidence", failures)
            if source.get("status") == "gated_manual_pending" and not (
                int(source.get("worker_unlogged_count") if source.get("worker_unlogged_count") is not None else -1) == 0
                and int(source.get("manual_unlogged_count") or 0) > 0
                and source.get("manual_approval_preview_command")
                and str(source.get("evidence") or "").strip()
            ):
                fail(f"promo engine freshness source {name} missing gated manual-pending evidence", failures)
            if source.get("name") == "published_log":
                if not (
                    isinstance(source.get("row_count"), int)
                    and str(source.get("latest_entry_date") or "").strip()
                    and "export_social_executions.py --dry-run" in (source.get("worker_export_preview_command") or "")
                    and "export_social_executions.py --refresh-admin" in (source.get("worker_export_apply_command") or "")
                    and "log_manual_distribution.py" in (source.get("manual_distribution_log_command_template") or "")
                    and str(source.get("evidence") or "").strip()
                ):
                    fail("promo engine published_log freshness source missing export/manual logging diagnostics", failures)
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
            if collection_steps and all(
                step.get("collection_url")
                and step.get("worksheet_import_preview_command")
                and step.get("worksheet_import_command")
                for step in collection_steps
            ):
                ok("promo engine manual metric steps include source links and worksheet import commands")
            else:
                fail("promo_engine_status.json manual metric steps missing source links or worksheet import commands", failures)
        manual_stats = json.loads(MANUAL_SOCIAL_STATS.read_text(encoding="utf-8")) if MANUAL_SOCIAL_STATS.exists() else {}
        facebook_followers_synced = str(((manual_stats.get("facebook") or {}).get("followers")) or "").strip().lower() != "pending"
        if auto_covered and any(item.get("field") == "facebook.followers" for item in auto_covered):
            ok("promo engine recognizes live API-covered manual metric fields")
        elif facebook_followers_synced:
            ok("promo engine synced live API-covered Facebook follower metric")
        else:
            fail("promo_engine_status.json missing API-covered or synced Facebook follower metric evidence", failures)
        history = kpi.get("metrics_history") or {}
        if history.get("snapshot_count") and history.get("latest_date"):
            ok(f"promo engine metrics history tracks {history.get('snapshot_count')} snapshot(s)")
        else:
            fail("promo_engine_status.json missing metrics history KPI summary", failures)
        monetization = kpi.get("monetization") or {}
        latest = history.get("latest") or {}
        latest_youtube = latest.get("youtube") or {}
        current_subscribers = int(latest_youtube.get("subscribers") or 0)
        live_metrics_snapshot = json.loads(LIVE_METRICS.read_text(encoding="utf-8")) if LIVE_METRICS.exists() else {}
        live_youtube = ((live_metrics_snapshot.get("platforms") or {}).get("youtube") or {}).get("metrics") or {}
        if live_youtube.get("subscribers") not in (None, ""):
            current_subscribers = int(live_youtube.get("subscribers"))
        target = int(monetization.get("target") or 0)
        if (
            target == 1000
            and int(monetization.get("current_subscribers") or 0) == current_subscribers
            and int(monetization.get("remaining_subscribers") or 0) == max(1000 - current_subscribers, 0)
            and "progress_percent" in monetization
        ):
            ok("promo engine tracks YouTube monetization subscriber gap")
        else:
            fail("promo_engine_status.json missing valid monetization subscriber gap", failures)
        runway = monetization.get("runway") or {}
        required_weekly = runway.get("required_subscribers_per_week") or {}
        if (
            runway.get("status")
            and int(runway.get("latest_subscribers") or 0) == current_subscribers
            and int(runway.get("snapshot_count") or 0) == int(history.get("snapshot_count") or 0)
            and "subscribers_per_week" in runway
            and float(required_weekly.get("365_days") or 0) >= 0
            and runway.get("action_needed")
        ):
            ok("promo engine tracks monetization runway pace")
        else:
            fail("promo_engine_status.json missing monetization runway pace", failures)
        plan_snapshot = json.loads(PROMO_QUEUE_PLAN.read_text(encoding="utf-8")) if PROMO_QUEUE_PLAN.exists() else {}
        plan_summary = plan_snapshot.get("summary") or {}
        future_snapshot = json.loads(FUTURE.read_text(encoding="utf-8")) if FUTURE.exists() else {}
        now_local = datetime.now().astimezone()
        approved_upcoming = 0
        approved_backlog = 0
        for row in future_snapshot.get("posts") or []:
            if str(row.get("approved") or "").strip().lower() != "yes":
                continue
            try:
                scheduled_at = datetime.fromisoformat(str(row.get("scheduled_at") or ""))
            except ValueError:
                scheduled_at = None
            if scheduled_at and scheduled_at >= now_local:
                approved_upcoming += 1
            else:
                approved_backlog += 1
        if (
            int(monetization.get("approved_upcoming_posts") or 0) == approved_upcoming
            and int(monetization.get("approved_backlog_posts") or 0) == approved_backlog
            and int(monetization.get("draft_review_posts") or 0) == int(plan_summary.get("review_posts") or 0)
            and isinstance(monetization.get("next_pressure") or [], list)
        ):
            ok("promo engine tracks monetization queue pressure")
        else:
            fail("promo_engine_status.json missing monetization queue pressure", failures)
        preview_command = monetization.get("backlog_reschedule_preview_command") or ""
        apply_command = monetization.get("backlog_reschedule_apply_command") or ""
        if (
            "scripts/reschedule_scheduled_posts.py" in preview_command
            and "--approved-backlog" in preview_command
            and "--start-at" in preview_command
            and "--apply" not in preview_command
            and "--apply --refresh-admin" in apply_command
        ):
            ok("promo engine includes dry-run backlog reschedule command")
        else:
            fail("promo_engine_status.json missing safe backlog reschedule command", failures)
        automation = kpi.get("refresh_automation") or {}
        if (
            automation.get("configured") is True
            and automation.get("path") == ".github/workflows/promo-admin-refresh.yml"
            and str(automation.get("actions_url") or "").endswith("/actions/workflows/promo-admin-refresh.yml")
            and str(automation.get("source_url") or "").endswith("/blob/main/.github/workflows/promo-admin-refresh.yml")
            and automation.get("cadence")
            and automation.get("manual_dispatch") is True
            and automation.get("commits_snapshots") is True
        ):
            ok("promo engine status includes scheduled refresh automation")
        else:
            fail("promo_engine_status.json missing scheduled refresh automation status", failures)
        if (
            automation.get("workflow_status_available") is True
            and "workflow_status_ok" in automation
            and "latest_run_status" in automation
            and "latest_run_conclusion" in automation
            and "workflow_status_action_needed" in automation
        ):
            ok("promo engine status includes scheduled workflow run health")
        else:
            fail("promo_engine_status.json missing scheduled workflow run health", failures)
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
        verification_counts = kpi.get("music_site_verification_state_counts") or {}
        if verification_counts:
            expected_counts = {
                "Live": int(store_history_summary.get("live") or 0),
                "Submitted": int(store_history_summary.get("submitted") or 0),
                "Pending": int(store_history_summary.get("pending") or 0),
                "Checked pending": int(store_history_summary.get("checked_pending") or 0),
                "Found in snapshot": int(store_history_summary.get("found_in_snapshot") or 0),
            }
            if all(int(verification_counts.get(label) or 0) == value for label, value in expected_counts.items()):
                ok("promo engine music site verification counts match store history")
            else:
                fail("promo_engine_status.json music site verification counts do not match store history", failures)
        else:
            fail("promo_engine_status.json missing music site verification counts", failures)
        if int(kpi.get("music_sites_pending") or 0) == int(store_history_summary.get("pending") or 0):
            ok("promo engine pending music site KPI matches unchecked pending stores")
        else:
            fail("promo_engine_status.json pending music site KPI includes checked-pending stores", failures)
        if int(kpi.get("music_sites_checked_pending") or 0) == int(store_history_summary.get("checked_pending") or 0):
            ok("promo engine checked-pending music site KPI matches store history")
        else:
            fail("promo_engine_status.json checked-pending music site KPI does not match store history", failures)
        execution_summary = kpi.get("social_execution_summary") or {}
        if "execution_count" in execution_summary and "status_counts" in execution_summary and "approval_needed_count" in execution_summary and "platform_fix_needed_count" in execution_summary:
            ok("promo engine includes social execution summary")
        else:
            fail("promo_engine_status.json missing categorized social execution summary", failures)
        scheduler_summary = kpi.get("social_scheduler_dry_run") or {}
        if scheduler_summary.get("dry_run") is True and "would_post_count" in scheduler_summary and "blocked_count" in scheduler_summary:
            ok("promo engine includes scheduler dry-run summary")
        else:
            fail("promo_engine_status.json missing scheduler dry-run summary", failures)
        if SOCIAL_EXECUTION_SNAPSHOT.exists():
            raw_execution = json.loads(SOCIAL_EXECUTION_SNAPSHOT.read_text(encoding="utf-8"))
            raw_summary = raw_execution.get("summary") or {}
            if execution_summary.get("platform_fix_needed_count") == len(raw_summary.get("platform_fix_needed") or []):
                ok("promo engine platform-fix count matches executor snapshot")
            else:
                fail("promo_engine_status.json platform-fix count does not match executor snapshot", failures)
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
            command_text = str(command.get("command") or "")
            if "scripts/capture_" not in command_text and "scripts/search_spotify_release.py" not in command_text and "scripts/search_youtube_music_release.py" not in command_text:
                fail(f"store verification command for {command.get('service') or 'unknown service'} missing capture script", failures)
        automatable_commands = [
            command for command in verification_commands
            if command.get("service") in {"Spotify", "Apple Music", "YouTube Music", "HyperFollow"}
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
        next_actions = status.get("next_actions") or []
        operational_next = kpi.get("operational_next_action") or {}
        if operational_next.get("label") and next_actions and operational_next.get("label") in next_actions[0] and status.get("health", {}).get("operational_next_action") == operational_next:
            ok("promo engine status mirrors operational next action")
        else:
            fail("promo_engine_status.json missing top-priority operational next action", failures)
        operator_docket = kpi.get("operator_docket") or {}
        handoff_packet = json.loads(HUMAN_HANDOFF_PACKET.read_text(encoding="utf-8")) if HUMAN_HANDOFF_PACKET.exists() else {}
        handoff_docket = handoff_packet.get("action_docket") or {}
        handoff_first = handoff_docket.get("first_ready_step") or {}
        if (
            operator_docket.get("available") is True
            and status.get("health", {}).get("operator_docket") == operator_docket
            and operator_docket.get("source_path") == "data/human_handoff_packet.json"
            and operator_docket.get("ready_step_count") == handoff_docket.get("ready_step_count")
            and operator_docket.get("blocked_step_count") == handoff_docket.get("blocked_step_count")
            and operator_docket.get("task_count") == handoff_docket.get("task_count")
            and (operator_docket.get("first_ready_step") or {}).get("id") == handoff_first.get("id")
            and any(handoff_first.get("label", "") in action for action in next_actions[:2])
        ):
            ok("promo engine status mirrors human handoff action docket")
        else:
            fail("promo_engine_status.json missing human handoff action docket summary", failures)
        unlock_impact = kpi.get("unlock_impact") or {}
        unlock_lanes = unlock_impact.get("lanes") or []
        blocker_ledger = json.loads(PROMOTION_BLOCKER_LEDGER.read_text(encoding="utf-8")) if PROMOTION_BLOCKER_LEDGER.exists() else {}
        blocker_summary = blocker_ledger.get("summary") or {}
        blocker_roadmap = blocker_summary.get("blocker_unlock_roadmap") or []
        blocker_projection = blocker_summary.get("next_resolution_projection") or {}
        expected_top_unlock = max(blocker_roadmap, key=lambda item: item.get("blockers_resolved") or 0, default={})
        if (
            unlock_impact.get("open_blocker_count") == blocker_summary.get("open_blocker_count")
            and unlock_impact.get("roadmap_step_count") == len(unlock_lanes) == len(blocker_roadmap)
            and unlock_impact.get("projected_resolvable_blockers") == sum(item.get("blockers_resolved") or 0 for item in blocker_roadmap)
            and unlock_impact.get("next_resolution_projection", {}).get("preview_command") == blocker_projection.get("preview_command")
            and (unlock_impact.get("immediate_unlock") or {}).get("id") == (blocker_roadmap[0].get("id") if blocker_roadmap else "")
            and (unlock_impact.get("top_unlock") or {}).get("id") == expected_top_unlock.get("id")
            and status.get("health", {}).get("unlock_impact") == unlock_impact
        ):
            ok("promo engine status summarizes blocker unlock impact")
        else:
            fail("promo_engine_status.json missing blocker unlock impact summary", failures)
        if pending_count and any("--from-csv --dry-run" in action for action in next_actions):
            ok("promo engine manual metric next action includes worksheet dry run")
        elif pending_count:
            fail("promo_engine_status.json manual metric next action missing worksheet dry run", failures)
        if (status.get("kpi") or {}).get("music_sites_checked_pending") and not any("Verify public store links" in action for action in next_actions):
            ok("promo engine checked-pending store actions avoid unchecked wording")
        elif (status.get("kpi") or {}).get("music_sites_checked_pending"):
            fail("promo_engine_status.json checked-pending store actions still say verify public store links", failures)
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
        hard_cta_posts = [
            post for post in posts
            if post.get("selected_cta_strength") in {"hard_subscribe", "hard_goal"}
            and cta_strength(post.get("text")) in {"hard_subscribe", "hard_goal"}
            and post.get("selected_copy_strategy") == "growth_first_subscriber_cta"
        ]
        if summary.get("selected_hard_cta_posts") == len(hard_cta_posts) == len(posts):
            ok("promo queue plan selects subscriber-growth CTA copy by default")
        else:
            fail("promo_queue_plan.json selected copy is not subscriber-growth CTA first", failures)
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
        approval_text = PROMO_QUEUE_APPROVE.read_text(encoding="utf-8")
        if "--refresh-admin" in approval_text and "--dry-run" in approval_text and "Dry run only" in approval_text:
            ok("promo queue approval script supports dry-run and refresh")
        else:
            fail("approve_promo_queue_plan.py missing dry-run or refresh support", failures)
    else:
        fail("approve_promo_queue_plan.py missing", failures)
    if SCHEDULED_POST_APPROVAL.exists():
        approval_text = SCHEDULED_POST_APPROVAL.read_text(encoding="utf-8")
        if "scheduled_posts.csv" in approval_text and "--refresh-admin" in approval_text and "--dry-run" in approval_text and "--checked-batch" in approval_text and "--allow-unchecked" in approval_text and "scheduled_approval_packet.json" in approval_text and "Refusing to approve unchecked" in approval_text and "Dry run only" in approval_text and "sync_future_posts.py" in approval_text:
            ok("scheduled post approval script can refresh admin")
        else:
            fail("update_scheduled_post_approval.py missing guarded checked-batch dry-run or refresh support", failures)
    else:
        fail("update_scheduled_post_approval.py missing", failures)
    if SCHEDULED_POST_RESCHEDULE.exists():
        reschedule_text = SCHEDULED_POST_RESCHEDULE.read_text(encoding="utf-8")
        if (
            "--approved-backlog" in reschedule_text
            and "--apply" in reschedule_text
            and "--allow-blocked" in reschedule_text
            and "Dry run only" in reschedule_text
            and "Published_Log.csv" in reschedule_text
            and "social_execution_snapshot.json" in reschedule_text
            and "Refusing to apply blocked reschedule" in reschedule_text
        ):
            ok("scheduled post reschedule script supports blocker-aware dry-run approved backlog previews")
        else:
            fail("reschedule_scheduled_posts.py missing blocker-aware dry-run approved backlog support", failures)
    else:
        fail("reschedule_scheduled_posts.py missing", failures)
    if MANUAL_METRICS_UPDATER.exists():
        ok("manual social stats updater present")
        updater_text = MANUAL_METRICS_UPDATER.read_text(encoding="utf-8")
        if "--from-csv" in updater_text and "--from-live" in updater_text and "live_social_metrics.json" in updater_text and "--dry-run" in updater_text and "new_value" in updater_text and "csv.DictReader" in updater_text and "No live-covered pending metrics available" in updater_text and "validate_metric_value" in updater_text and "Decimal" in updater_text:
            ok("manual social stats updater can import filled CSV values")
        else:
            fail("update_manual_social_stats.py missing filled CSV/live metric import support or numeric value guards", failures)
    else:
        fail("update_manual_social_stats.py missing", failures)
    if STORE_LINK_VERIFIER.exists():
        verifier_text = STORE_LINK_VERIFIER.read_text(encoding="utf-8")
        if "search_spotify_release.py" in verifier_text and "capture_apple_music_release.py" in verifier_text and "search_youtube_music_release.py" in verifier_text and "capture_hyperfollow_store_links.py" in verifier_text and "--refresh-admin" in verifier_text and "--step-timeout-seconds" in verifier_text and "TimeoutExpired" in verifier_text and '"timed_out"' in verifier_text:
            ok("pending store link verifier can refresh admin")
        else:
            fail("verify_pending_store_links.py missing capture, bounded timeout, or refresh support", failures)
    else:
        fail("verify_pending_store_links.py missing", failures)
    if SPOTIFY_SEARCH_VERIFIER.exists():
        spotify_search_text = SPOTIFY_SEARCH_VERIFIER.read_text(encoding="utf-8")
        if "public-web-search-plus-spotify-oembed" in spotify_search_text and "fetch_oembed" in spotify_search_text and "open.spotify.com/album" in spotify_search_text:
            ok("Spotify public search verifier validates candidates with oEmbed")
        else:
            fail("search_spotify_release.py missing public search or oEmbed validation", failures)
    else:
        fail("search_spotify_release.py missing", failures)
    if YOUTUBE_MUSIC_SEARCH_VERIFIER.exists():
        youtube_music_search_text = YOUTUBE_MUSIC_SEARCH_VERIFIER.read_text(encoding="utf-8")
        if "public-web-search-plus-youtube-music-html" in youtube_music_search_text and "music.youtube.com/watch" in youtube_music_search_text and "title_matches_official" in youtube_music_search_text:
            ok("YouTube Music public search verifier validates candidate titles")
        else:
            fail("search_youtube_music_release.py missing public search or title validation", failures)
    else:
        fail("search_youtube_music_release.py missing", failures)
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
    if SOCIAL_EXECUTION_EXPORT.exists():
        export_text = SOCIAL_EXECUTION_EXPORT.read_text(encoding="utf-8")
        if "PUBLISHED_LOG" in export_text and "--dry-run" in export_text and "--refresh-admin" in export_text and "refresh_promo_admin.py" in export_text and "append_published_log" in export_text:
            ok("social execution export can refresh published log safely")
        else:
            fail("export_social_executions.py missing dry-run published-log export or refresh support", failures)
    else:
        fail("export_social_executions.py missing", failures)
    if SOCIAL_SCHEDULER_CAPTURE.exists():
        scheduler_text = SOCIAL_SCHEDULER_CAPTURE.read_text(encoding="utf-8")
        if "social_scheduler_dry_run.json" in scheduler_text and "/scheduler/dry-run" in scheduler_text and "method=\"POST\"" in scheduler_text:
            ok("scheduler dry-run capture script present")
        else:
            fail("capture_scheduler_dry_run.py missing dry-run endpoint support", failures)
    else:
        fail("capture_scheduler_dry_run.py missing", failures)
    if PROMO_REFRESH_SCRIPT.exists():
        refresh_text = PROMO_REFRESH_SCRIPT.read_text(encoding="utf-8")
        required_bits = [
            "promo_admin_refresh_run.json",
            "capture_live_metrics.py",
            "update_manual_social_stats.py",
            "--from-live",
            "verify_pending_store_links.py",
            "capture_executor_readiness.py",
            "capture_social_executions.py",
            "capture_scheduler_dry_run.py",
            "capture_github_workflow_status.py",
            "build_promo_operations_packet.py",
            "build_approval_runway.py",
            "build_subscriber_cta_audit.py",
            "build_manual_distribution_packet.py",
            "build_monetization_activation_plan.py",
            "build_backlog_reschedule_preview.py",
            "build_platform_repair_status.py",
            "build_tiktok_setup_preflight.py",
            "build_manual_metric_collection.py",
            "build_promotion_blocker_ledger.py",
            "update_weekly_report.py",
            "timeout_seconds",
            "TimeoutExpired",
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
    if PROMO_REFRESH_WORKFLOW_CAPTURE.exists():
        workflow_capture_text = PROMO_REFRESH_WORKFLOW_CAPTURE.read_text(encoding="utf-8")
        if "promo_refresh_workflow_status.json" in workflow_capture_text and "api.github.com" in workflow_capture_text and "workflow_runs" in workflow_capture_text:
            ok("promo refresh workflow status capture script present")
        else:
            fail("capture_github_workflow_status.py missing GitHub workflow run capture support", failures)
    else:
        fail("capture_github_workflow_status.py missing", failures)
    if PROMO_REFRESH_WORKFLOW.exists():
        workflow_text = PROMO_REFRESH_WORKFLOW.read_text(encoding="utf-8")
        required_bits = [
            "schedule:",
            "workflow_dispatch:",
            "python3 scripts/refresh_promo_admin.py",
            "python3 scripts/validate_content_system.py",
            "contents: write",
            "GITHUB_TOKEN: ${{ github.token }}",
            "scripts/capture_github_workflow_status.py",
            "git add admin data",
        ]
        forbidden_bits = [
            "apply_promo_queue_plan.py --apply",
            "post_youtube_from_queue.py",
            "post_youtube_captions.py",
            "post_x_from_queue.py",
            "post_tiktok_from_queue.py",
        ]
        if all(bit in workflow_text for bit in required_bits) and not any(bit in workflow_text for bit in forbidden_bits):
            ok("promo admin scheduled refresh workflow is safe")
        else:
            fail("promo admin scheduled refresh workflow missing safe refresh coverage or includes posting commands", failures)
    else:
        fail("promo admin scheduled refresh workflow missing", failures)
    secret_push = ROOT / "scripts" / "push_social_worker_secrets.py"
    if secret_push.exists():
        secret_text = secret_push.read_text(encoding="utf-8")
        if "--dry-run" in secret_text and "would update" in secret_text and "wrangler" in secret_text:
            ok("social worker secret push script supports dry-run")
        else:
            fail("push_social_worker_secrets.py missing dry-run support", failures)
    else:
        fail("push_social_worker_secrets.py missing", failures)
    if SOCIAL_EXECUTION_RESET.exists():
        reset_text = SOCIAL_EXECUTION_RESET.read_text(encoding="utf-8")
        if (
            "wrangler" in reset_text
            and "kv" in reset_text
            and "key" in reset_text
            and "delete" in reset_text
            and "--apply" in reset_text
            and "max_attempts_exceeded" in reset_text
            and "SOCIAL_EXECUTOR_STATE" in reset_text
        ):
            ok("social execution reset script is dry-run-first and retry-cap scoped")
        else:
            fail("reset_social_execution_state.py missing dry-run-first retry reset behavior", failures)
    else:
        fail("reset_social_execution_state.py missing", failures)
    dry_run_checker = ROOT / "scripts" / "check_social_executor_dry_run.py"
    if dry_run_checker.exists():
        checker_text = dry_run_checker.read_text(encoding="utf-8")
        if "dryRun" in checker_text and "/api/social/execute" in checker_text and "urllib.request" in checker_text and "--apply" not in checker_text:
            ok("social executor dry-run checker verifies retry reset candidates")
        else:
            fail("check_social_executor_dry_run.py missing dry-run execute verification", failures)
    else:
        fail("check_social_executor_dry_run.py missing", failures)
    if PROMO_CONSISTENCY_SCRIPT.exists():
        consistency_text = PROMO_CONSISTENCY_SCRIPT.read_text(encoding="utf-8")
        if "promo_consistency_audit.json" in consistency_text and "promo-consistency-audit.md" in consistency_text and "promotion_blocker_ledger.json" in consistency_text and "human_handoff_packet.json" in consistency_text and "manual_metric_batch_count_matches_ledger" in consistency_text and "priority_batch_count" in consistency_text and "social_execution_snapshot.json" in consistency_text and "social_scheduler_dry_run.json" in consistency_text and "tiktok_setup_preflight.json" in consistency_text and "subprocess" not in consistency_text:
            ok("promo consistency audit builder is review-only")
        else:
            fail("build_promo_consistency_audit.py missing audit outputs or executes commands", failures)
    else:
        fail("build_promo_consistency_audit.py missing", failures)
    if TIKTOK_SETUP_PREFLIGHT_SCRIPT.exists():
        preflight_text = TIKTOK_SETUP_PREFLIGHT_SCRIPT.read_text(encoding="utf-8")
        if "tiktok_setup_preflight.json" in preflight_text and "tiktok-setup-preflight.md" in preflight_text and "TIKTOK_CLIENT_KEY" in preflight_text and "TIKTOK_PUBLIC_POSTING_APPROVED" in preflight_text and "Secret values" in preflight_text and "subprocess" not in preflight_text:
            ok("TikTok setup preflight builder is review-only")
        else:
            fail("build_tiktok_setup_preflight.py missing preflight outputs or exposes execution/secrets", failures)
    else:
        fail("build_tiktok_setup_preflight.py missing", failures)
    if TIKTOK_REPAIR_RUNBOOK_SCRIPT.exists():
        runbook_text = TIKTOK_REPAIR_RUNBOOK_SCRIPT.read_text(encoding="utf-8")
        if "tiktok_repair_runbook.json" in runbook_text and "tiktok-repair-runbook.md" in runbook_text and "Collect credentials" in runbook_text and "blocked_apply_command" in runbook_text and "backlog_reschedule_preview.json" in runbook_text and "--approved-backlog" in runbook_text and "--approved-only" not in runbook_text and "Secret values" in runbook_text and "subprocess" not in runbook_text:
            ok("TikTok repair runbook builder is review-only")
        else:
            fail("build_tiktok_repair_runbook.py missing runbook outputs or exposes execution/secrets", failures)
    else:
        fail("build_tiktok_repair_runbook.py missing", failures)
    if PROMO_OPERATIONS_SCRIPT.exists():
        packet_text = PROMO_OPERATIONS_SCRIPT.read_text(encoding="utf-8")
        if "promo_operations_packet.json" in packet_text and "promo-operations-packet.md" in packet_text and "approval_review" in packet_text and "urgency_for" in packet_text and "missing_secrets" in packet_text and "subprocess" not in packet_text:
            ok("promo operations packet builder is review-only")
        else:
            fail("build_promo_operations_packet.py missing review packet outputs or executes commands", failures)
    else:
        fail("build_promo_operations_packet.py missing", failures)
    if PUBLISHED_LOG_RECONCILIATION_SCRIPT.exists():
        reconciliation_text = PUBLISHED_LOG_RECONCILIATION_SCRIPT.read_text(encoding="utf-8")
        if "published_log_reconciliation.json" in reconciliation_text and "published-log-reconciliation.md" in reconciliation_text and "export_social_executions.py --dry-run" in reconciliation_text and "manual_distribution_packet.json" in reconciliation_text and "approval_gate" in reconciliation_text and "next_gate" in reconciliation_text and "manual_approval" in reconciliation_text and "log_gate" in reconciliation_text and "log_preview_command" in reconciliation_text and "subprocess" not in reconciliation_text:
            ok("published log reconciliation builder is review-only")
        else:
            fail("build_published_log_reconciliation.py missing safe reconciliation outputs or executes commands", failures)
    else:
        fail("build_published_log_reconciliation.py missing", failures)
    if HUMAN_HANDOFF_SCRIPT.exists():
        handoff_text = HUMAN_HANDOFF_SCRIPT.read_text(encoding="utf-8")
        if "human_handoff_packet.json" in handoff_text and "human-handoff-packet.md" in handoff_text and "promotion_blocker_ledger.json" in handoff_text and "manual_metric_collection_packet.json" in handoff_text and "priority_batches" in handoff_text and "batch_count" in handoff_text and "manual_distribution_packet.json" in handoff_text and "approval_runway.json" in handoff_text and "scheduled_approval_packet.json" in handoff_text and "platform_repair_status.json" in handoff_text and "tiktok_setup_preflight.json" in handoff_text and "action_docket" in handoff_text and "build_action_docket" in handoff_text and "command_sequence" in handoff_text and "completion_evidence" in handoff_text and "next_step_after_apply" in handoff_text and "subprocess" not in handoff_text:
            ok("human handoff packet builder is review-only")
        else:
            fail("build_human_handoff_packet.py missing handoff outputs or executes commands", failures)
    else:
        fail("build_human_handoff_packet.py missing", failures)
    if PROMOTION_BLOCKER_LEDGER_SCRIPT.exists():
        ledger_text = PROMOTION_BLOCKER_LEDGER_SCRIPT.read_text(encoding="utf-8")
        if "promotion_blocker_ledger.json" in ledger_text and "promotion-blocker-ledger.md" in ledger_text and "owner_counts" in ledger_text and "category_counts" in ledger_text and "manual_metric_collection_packet.json" in ledger_text and "priority_batches" in ledger_text and "manual_metric_batch" in ledger_text and "approval_runway.json" in ledger_text and "blocker_unlock_roadmap" in ledger_text and "build_unlock_roadmap" in ledger_text and "next_resolution_projection" in ledger_text and "approval_projection" in ledger_text and "subprocess" not in ledger_text:
            ok("promotion blocker ledger builder is review-only")
        else:
            fail("build_promotion_blocker_ledger.py missing ledger outputs or executes commands", failures)
    else:
        fail("build_promotion_blocker_ledger.py missing", failures)
    if PLATFORM_REPAIR_SCRIPT.exists():
        repair_text = PLATFORM_REPAIR_SCRIPT.read_text(encoding="utf-8")
        if "platform_repair_status.json" in repair_text and "platform-repair-status.md" in repair_text and "Repair Checklist" in repair_text and "repair_checklist" in repair_text and "checklist_blocked_count" in repair_text and "promo_operations_packet.json" in repair_text and "social_execution_snapshot.json" in repair_text and "executor_readiness_snapshot.json" in repair_text and "tiktok_setup_preflight.json" in repair_text and "subprocess" not in repair_text:
            ok("platform repair status builder is review-only")
        else:
            fail("build_platform_repair_status.py missing repair status outputs or executes commands", failures)
    else:
        fail("build_platform_repair_status.py missing", failures)
    if APPROVAL_RUNWAY_SCRIPT.exists():
        runway_text = APPROVAL_RUNWAY_SCRIPT.read_text(encoding="utf-8")
        if "approval_runway.json" in runway_text and "approval-runway.md" in runway_text and "subscriber_growth_score" in runway_text and "approval_preview_command" in runway_text and "manual_approval_docket" in runway_text and "build_manual_approval_docket" in runway_text and "subprocess" not in runway_text:
            ok("approval runway builder is review-only")
        else:
            fail("build_approval_runway.py missing runway outputs or executes commands", failures)
    else:
        fail("build_approval_runway.py missing", failures)
    if SCHEDULED_APPROVAL_SCRIPT.exists():
        scheduled_approval_text = SCHEDULED_APPROVAL_SCRIPT.read_text(encoding="utf-8")
        if "scheduled_approval_packet.json" in scheduled_approval_text and "scheduled-approval-packet.md" in scheduled_approval_text and "approval_preview_command" in scheduled_approval_text and "approval_apply_command" in scheduled_approval_text and "batch_preview_command" in scheduled_approval_text and "batch_apply_command" in scheduled_approval_text and "checked_batch_preview_command" in scheduled_approval_text and "checked_batch_apply_command" in scheduled_approval_text and "checked_batch_explicit_preview_command" in scheduled_approval_text and "checked_batch_explicit_apply_command" in scheduled_approval_text and "--checked-batch" in scheduled_approval_text and "approval_docket" in scheduled_approval_text and "approval_decision_manifest" in scheduled_approval_text and "ready_to_approve" in scheduled_approval_text and "review_checks" in scheduled_approval_text and "failed_review_checks" in scheduled_approval_text and "approval_review_status" in scheduled_approval_text and "executor_readiness_snapshot.json" in scheduled_approval_text and "subprocess" not in scheduled_approval_text:
            ok("scheduled approval packet builder is review-only")
        else:
            fail("build_scheduled_approval_packet.py missing approval packet outputs, batch commands, review checks, or executes commands", failures)
    else:
        fail("build_scheduled_approval_packet.py missing", failures)
    if SUBSCRIBER_CTA_AUDIT_SCRIPT.exists():
        cta_text = SUBSCRIBER_CTA_AUDIT_SCRIPT.read_text(encoding="utf-8")
        if "subscriber_cta_audit.json" in cta_text and "subscriber-cta-audit.md" in cta_text and "needs_subscriber_cta_swap" in cta_text and "subprocess" not in cta_text:
            ok("subscriber CTA audit builder is review-only")
        else:
            fail("build_subscriber_cta_audit.py missing CTA audit outputs or executes commands", failures)
    else:
        fail("build_subscriber_cta_audit.py missing", failures)
    if MANUAL_DISTRIBUTION_PACKET_SCRIPT.exists():
        manual_distribution_text = MANUAL_DISTRIBUTION_PACKET_SCRIPT.read_text(encoding="utf-8")
        if "manual_distribution_packet.json" in manual_distribution_text and "manual-distribution-packet.md" in manual_distribution_text and "Manual Posting Queue" in manual_distribution_text and "manual_distribution_docket" in manual_distribution_text and "manual_approval_docket" in manual_distribution_text and "review_queue" in manual_distribution_text and "copy_block" in manual_distribution_text and "manual_posting_packet" in manual_distribution_text and "postable_now" in manual_distribution_text and "log_manual_distribution.py" in manual_distribution_text and "Published_Log.csv" in manual_distribution_text and "distribution_status" in manual_distribution_text and "subprocess" not in manual_distribution_text:
            ok("manual distribution packet builder is review-only")
        else:
            fail("build_manual_distribution_packet.py missing manual distribution outputs or executes commands", failures)
    else:
        fail("build_manual_distribution_packet.py missing", failures)
    if MANUAL_DISTRIBUTION_LOGGER.exists():
        logger_text = MANUAL_DISTRIBUTION_LOGGER.read_text(encoding="utf-8")
        if "--apply" in logger_text and "--refresh-admin" in logger_text and "append_published_log" in logger_text and "dry_run" in logger_text and "validate_public_url" in logger_text and "already_logged" in logger_text and "PUBLIC_URL" in logger_text:
            ok("manual distribution logger is dry-run-first")
        else:
            fail("log_manual_distribution.py missing dry-run-first logging behavior or URL/duplicate guards", failures)
    else:
        fail("log_manual_distribution.py missing", failures)
    if MONETIZATION_ACTIVATION_SCRIPT.exists():
        activation_text = MONETIZATION_ACTIVATION_SCRIPT.read_text(encoding="utf-8")
        if "monetization_activation_plan.json" in activation_text and "monetization-activation-plan.md" in activation_text and "Activation Sequence" in activation_text and "subprocess" not in activation_text:
            ok("monetization activation plan builder is review-only")
        else:
            fail("build_monetization_activation_plan.py missing activation outputs or executes commands", failures)
    else:
        fail("build_monetization_activation_plan.py missing", failures)
    if BACKLOG_RESCHEDULE_PREVIEW_SCRIPT.exists():
        backlog_text = BACKLOG_RESCHEDULE_PREVIEW_SCRIPT.read_text(encoding="utf-8")
        if "backlog_reschedule_preview.json" in backlog_text and "backlog-reschedule-preview.md" in backlog_text and "Apply allowed without override" in backlog_text and "normal_apply_gate" in backlog_text and "clearance_steps" in backlog_text and "executor_readiness_snapshot.json" in backlog_text and "blocked_apply_command" in backlog_text and "override_apply_command" in backlog_text and "subprocess" not in backlog_text:
            ok("backlog reschedule preview builder is review-only")
        else:
            fail("build_backlog_reschedule_preview.py missing preview outputs or executes commands", failures)
    else:
        fail("build_backlog_reschedule_preview.py missing", failures)
    if MANUAL_METRIC_COLLECTION_SCRIPT.exists():
        collection_text = MANUAL_METRIC_COLLECTION_SCRIPT.read_text(encoding="utf-8")
        if "manual_metric_collection_template.csv" in collection_text and "manual_metric_collection_packet.json" in collection_text and "manual-metric-collection.md" in collection_text and "pending_manual_by_platform" in collection_text and "metric_collection_docket" in collection_text and "platform_groups" in collection_text and "priority_batches" in collection_text and "collection_priority" in collection_text and "metric_category" in collection_text and "access_level" in collection_text and "evidence_hint" in collection_text and "collection_url" in collection_text and "--from-live" in collection_text and "collection_mode" in collection_text and "live_import_available_count" in collection_text and "ready_to_import_count" in collection_text and "existing_new_values" in collection_text and "value_type" in collection_text and "import_effect" in collection_text and "subprocess" not in collection_text:
            ok("manual metric collection builder is review-only")
        else:
            fail("build_manual_metric_collection.py missing worksheet outputs or executes commands", failures)
    else:
        fail("build_manual_metric_collection.py missing", failures)
    if SOCIAL_EXECUTOR_WORKER.exists():
        worker_text = SOCIAL_EXECUTOR_WORKER.read_text(encoding="utf-8")
        if "page_impressions_unique" in worker_text and "reach_7d" in worker_text and "insights_status" in worker_text:
            ok("social executor captures Facebook reach when page insights are available")
        else:
            fail("social executor missing Facebook reach metric support", failures)
    else:
        fail("social executor Worker missing", failures)
    if PROMO_CONSISTENCY_REPORT.exists():
        consistency_report_text = PROMO_CONSISTENCY_REPORT.read_text(encoding="utf-8")
        if "Promo Consistency Audit" in consistency_report_text and "Checks" in consistency_report_text and "Guardrails" in consistency_report_text:
            ok("promo consistency markdown report present")
        else:
            fail("promo-consistency-audit.md missing expected sections", failures)
    else:
        fail("promo-consistency-audit.md missing", failures)
    if TIKTOK_SETUP_PREFLIGHT_REPORT.exists():
        preflight_report_text = TIKTOK_SETUP_PREFLIGHT_REPORT.read_text(encoding="utf-8")
        if "TikTok Setup Preflight" in preflight_report_text and "Checks" in preflight_report_text and "Guardrails" in preflight_report_text:
            ok("TikTok setup preflight markdown report present")
        else:
            fail("tiktok-setup-preflight.md missing expected sections", failures)
    else:
        fail("tiktok-setup-preflight.md missing", failures)
    if TIKTOK_REPAIR_RUNBOOK_REPORT.exists():
        runbook_report_text = TIKTOK_REPAIR_RUNBOOK_REPORT.read_text(encoding="utf-8")
        if "TikTok Repair Runbook" in runbook_report_text and "Sequence" in runbook_report_text and "Guardrails" in runbook_report_text:
            ok("TikTok repair runbook markdown report present")
        else:
            fail("tiktok-repair-runbook.md missing expected sections", failures)
    else:
        fail("tiktok-repair-runbook.md missing", failures)
    if PROMO_OPERATIONS_REPORT.exists():
        report_text = PROMO_OPERATIONS_REPORT.read_text(encoding="utf-8")
        if "Promo Operations Packet" in report_text and "Top Actions" in report_text:
            ok("promo operations markdown report present")
        else:
            fail("promo operations markdown report missing expected sections", failures)
    else:
        fail("promo-operations-packet.md missing", failures)
    if PUBLISHED_LOG_RECONCILIATION_REPORT.exists():
        reconciliation_report_text = PUBLISHED_LOG_RECONCILIATION_REPORT.read_text(encoding="utf-8")
        if "Published Log Reconciliation" in reconciliation_report_text and "Worker Export" in reconciliation_report_text and "Manual Logging" in reconciliation_report_text and "Guardrails" in reconciliation_report_text:
            ok("published log reconciliation markdown report present")
        else:
            fail("published-log-reconciliation.md missing expected sections", failures)
    else:
        fail("published-log-reconciliation.md missing", failures)
    if HUMAN_HANDOFF_REPORT.exists():
        handoff_report_text = HUMAN_HANDOFF_REPORT.read_text(encoding="utf-8")
        if "Human Handoff Packet" in handoff_report_text and "Action Docket" in handoff_report_text and "Tasks" in handoff_report_text and "Guardrails" in handoff_report_text:
            ok("human handoff markdown report present")
        else:
            fail("human-handoff-packet.md missing expected sections", failures)
    else:
        fail("human-handoff-packet.md missing", failures)
    if PROMOTION_BLOCKER_LEDGER_REPORT.exists():
        ledger_report_text = PROMOTION_BLOCKER_LEDGER_REPORT.read_text(encoding="utf-8")
        if "Promotion Blocker Ledger" in ledger_report_text and "Unlock Roadmap" in ledger_report_text and "Ledger" in ledger_report_text and "Guardrails" in ledger_report_text:
            ok("promotion blocker ledger markdown report present")
        else:
            fail("promotion-blocker-ledger.md missing expected sections", failures)
    else:
        fail("promotion-blocker-ledger.md missing", failures)
    if PLATFORM_REPAIR_REPORT.exists():
        repair_report_text = PLATFORM_REPAIR_REPORT.read_text(encoding="utf-8")
        if "Platform Repair Status" in repair_report_text and "Repair Checklist" in repair_report_text and "Guardrails" in repair_report_text:
            ok("platform repair markdown report present")
        else:
            fail("platform-repair-status.md missing expected sections", failures)
    else:
        fail("platform-repair-status.md missing", failures)
    if APPROVAL_RUNWAY_REPORT.exists():
        runway_report_text = APPROVAL_RUNWAY_REPORT.read_text(encoding="utf-8")
        if "Approval Runway" in runway_report_text and "Manual Approval Docket" in runway_report_text and "Recommended Sequence" in runway_report_text and "Guardrails" in runway_report_text:
            ok("approval runway markdown report present")
        else:
            fail("approval-runway.md missing expected sections", failures)
    else:
        fail("approval-runway.md missing", failures)
    if SCHEDULED_APPROVAL_REPORT.exists():
        scheduled_approval_report_text = SCHEDULED_APPROVAL_REPORT.read_text(encoding="utf-8")
        if "Scheduled Approval Packet" in scheduled_approval_report_text and "Approval Docket" in scheduled_approval_report_text and "Review Queue" in scheduled_approval_report_text and "Guardrails" in scheduled_approval_report_text:
            ok("scheduled approval markdown report present")
        else:
            fail("scheduled-approval-packet.md missing expected sections", failures)
    else:
        fail("scheduled-approval-packet.md missing", failures)
    if SUBSCRIBER_CTA_AUDIT_REPORT.exists():
        cta_report_text = SUBSCRIBER_CTA_AUDIT_REPORT.read_text(encoding="utf-8")
        if "Subscriber CTA Audit" in cta_report_text and "CTA Review Queue" in cta_report_text and "Guardrails" in cta_report_text:
            ok("subscriber CTA audit markdown report present")
        else:
            fail("subscriber-cta-audit.md missing expected sections", failures)
    else:
        fail("subscriber-cta-audit.md missing", failures)
    if MANUAL_DISTRIBUTION_REPORT.exists():
        manual_distribution_report = MANUAL_DISTRIBUTION_REPORT.read_text(encoding="utf-8")
        if "Manual Distribution Packet" in manual_distribution_report and "Manual Posting Docket" in manual_distribution_report and "Manual Posting Queue" in manual_distribution_report and "Guardrails" in manual_distribution_report:
            ok("manual distribution markdown report present")
        else:
            fail("manual-distribution-packet.md missing expected sections", failures)
    else:
        fail("manual-distribution-packet.md missing", failures)
    if MONETIZATION_ACTIVATION_REPORT.exists():
        activation_report_text = MONETIZATION_ACTIVATION_REPORT.read_text(encoding="utf-8")
        if "Monetization Activation Plan" in activation_report_text and "Activation Sequence" in activation_report_text and "Guardrails" in activation_report_text:
            ok("monetization activation markdown report present")
        else:
            fail("monetization-activation-plan.md missing expected sections", failures)
    else:
        fail("monetization-activation-plan.md missing", failures)
    if BACKLOG_RESCHEDULE_PREVIEW_REPORT.exists():
        backlog_report_text = BACKLOG_RESCHEDULE_PREVIEW_REPORT.read_text(encoding="utf-8")
        if "Backlog Reschedule Preview" in backlog_report_text and "Proposed Reschedule" in backlog_report_text and "Guardrails" in backlog_report_text:
            ok("backlog reschedule markdown report present")
        else:
            fail("backlog-reschedule-preview.md missing expected sections", failures)
    else:
        fail("backlog-reschedule-preview.md missing", failures)


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
    platform_checks = {
        "spotify executor marked not applicable": "label:'Spotify'" in text and "hasExecutor:false" in text,
        "executor chip explains manual metric state": "if(!hasExecutor) return '<span class=\"status-chip neutral\">Manual metrics</span>'" in text,
        "platform rows pass executor applicability": "config.hasExecutor!==false" in text,
        "checked no-change freshness neutral": "if(status==='checked_no_change') return 'neutral'" in text,
        "checked no-change hidden from urgent actions": "source.status!=='fresh'&&source.status!=='checked_no_change'" in text,
        "refresh automation shown": "Refresh automation:" in text and "refreshAutomation" in text,
        "workflow run health shown": "Workflow run:" in text and "Open latest refresh run" in text,
        "refresh workflow link shown": "Open refresh workflow runs" in text and "actions/workflows/promo-admin-refresh.yml" in text,
        "scheduler dry-run shown": "Scheduler dry-run:" in text and "social_scheduler_dry_run" in text,
        "unlock impact shown": "Unlock impact:" in text and "Immediate unlock:" in text and "Largest unlock lane:" in text,
        "handoff action docket shown": "Action docket:" in text and "First ready step:" in text,
        "published log reconciliation shown": "Published log reconciliation" in text and "Worker export" in text and "Manual Logging" in text,
        "manual approval docket shown": "Manual approval docket:" in text and "Preview manual approvals:" in text,
    }
    missing_platform = [label for label, present in platform_checks.items() if not present]
    if missing_platform:
        fail("admin platform snapshot executor labels missing " + ", ".join(missing_platform), failures)
    else:
        ok("admin platform snapshot separates metrics-only platforms from executor blocks")


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
