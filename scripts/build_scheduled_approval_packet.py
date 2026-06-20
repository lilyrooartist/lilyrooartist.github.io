#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data" / "scheduled_posts.csv"
EXECUTIONS = ROOT / "data" / "social_execution_snapshot.json"
EXECUTOR_READINESS = ROOT / "data" / "executor_readiness_snapshot.json"
HYPERFOLLOW_SNAPSHOT = ROOT / "data" / "hyperfollow_store_links_snapshot.json"
ALIGNMENT_AUDIT = ROOT / "data" / "first_single_alignment_audit.json"
APPLE_MUSIC_SNAPSHOT = ROOT / "data" / "apple_music_release_snapshot.json"
YOUTUBE_TITLE_TRACK = ROOT / "data" / "youtube_title_track_snapshot.json"
YOUTUBE_MUSIC_SNAPSHOT = ROOT / "data" / "youtube_music_release_snapshot.json"
OUT = ROOT / "data" / "scheduled_approval_packet.json"
REPORT = ROOT / "admin" / "reports" / "scheduled-approval-packet.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"
URL_RE = re.compile(r"https?://[^\s|]+")


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def read_queue() -> dict[str, dict[str, str]]:
    with QUEUE.open(newline="", encoding="utf-8") as handle:
        return {
            row.get("id", ""): {key: (value or "").strip() for key, value in row.items()}
            for row in csv.DictReader(handle)
            if row.get("id")
        }


def copy_block(row: dict[str, str]) -> str:
    return "\n\n".join(part for part in [row.get("text") or "", row.get("reply_text") or ""] if part)


def approval_preview_command(post_id: str) -> str:
    return f"python3 scripts/update_scheduled_post_approval.py {post_id} --dry-run"


def approval_apply_command(post_id: str) -> str:
    return f"python3 scripts/update_scheduled_post_approval.py {post_id} --refresh-admin"


def approval_batch_command(rows: list[dict], *, dry_run: bool) -> str:
    ids = [row.get("id") or "" for row in rows if row.get("id")]
    if not ids:
        return ""
    suffix = " --dry-run" if dry_run else " --refresh-admin"
    return "python3 scripts/update_scheduled_post_approval.py " + " ".join(ids) + suffix


def approval_checked_batch_command(rows: list[dict], *, dry_run: bool) -> str:
    ids = [row.get("id") or "" for row in rows if row.get("id")]
    if not ids:
        return ""
    suffix = " --dry-run" if dry_run else " --refresh-admin"
    return "python3 scripts/update_scheduled_post_approval.py --checked-batch" + suffix


def approval_effect(row: dict, *, target_value: str = "yes") -> dict:
    previous = row.get("approved") or ""
    changed = previous != target_value
    return {
        "field": "approved",
        "from": previous,
        "to": target_value,
        "changed": changed,
        "summary": f"approved {previous!r} -> {target_value!r}",
    }


def approval_effect_summary(rows: list[dict]) -> dict:
    effects = [
        {
            "id": row.get("id") or "",
            "platform": row.get("platform") or "",
            "execution_mode": row.get("execution_mode") or "",
            "effect": row.get("approval_effect") or approval_effect(row),
        }
        for row in rows
        if row.get("id")
    ]
    return {
        "row_count": len(effects),
        "change_count": sum(1 for item in effects if (item.get("effect") or {}).get("changed")),
        "ids": [item["id"] for item in effects],
        "effects": effects,
    }


def checked_batch_dry_run_preview(checked_rows: list[dict], summary: dict) -> dict:
    checked_ids = [row.get("id") or "" for row in checked_rows if row.get("id")]
    effect = summary.get("checked_batch_effect") or {}
    change_count = int(effect.get("change_count") or 0)
    output_lines = []
    for item in effect.get("effects") or []:
        row_effect = item.get("effect") or {}
        output_lines.append(
            f"{item.get('id')}: approved {row_effect.get('from')!r} -> {row_effect.get('to')!r}"
        )
    output_lines.extend([
        "Checked batch guard: "
        f"{len(checked_ids)} checked id(s); {len(checked_ids)} requested; "
        f"0 unchecked; {change_count} change(s).",
        "Dry run only; did not update data/scheduled_posts.csv",
    ])
    return {
        "status": "ready_for_review" if checked_ids else "blocked",
        "dry_run": True,
        "would_write_files": False,
        "command": summary.get("checked_batch_preview_command") or "",
        "apply_after_review_command": summary.get("checked_batch_apply_command") or "",
        "checked_batch_ids": checked_ids,
        "requested_ids": checked_ids,
        "unchecked_ids": [],
        "row_count": len(checked_ids),
        "change_count": change_count,
        "expected_effect": effect,
        "output_lines": output_lines,
        "post_apply_verification": [
            "python3 scripts/refresh_promo_admin.py",
            "python3 scripts/validate_content_system.py",
        ],
        "guardrail": "This is a computed dry-run preview; approval still requires human review and the --checked-batch apply command.",
    }


def docket_row(row: dict) -> dict:
    failed = row.get("failed_review_checks") or []
    return {
        "id": row.get("id") or "",
        "platform": row.get("platform") or "",
        "song": row.get("song") or "",
        "scheduled_at": row.get("scheduled_at") or "",
        "execution_mode": row.get("execution_mode") or "",
        "post_type": row.get("post_type") or "",
        "review_status": row.get("approval_review_status") or "",
        "checked_batch_member": bool(row.get("checked_batch_member")),
        "paste_text": row.get("copy_block") or "",
        "asset_url": row.get("asset_url") or "",
        "destination_links": row.get("destination_links") or links_in_text(row.get("copy_block") or ""),
        "destination_link_audit": row.get("destination_link_audit") or [],
        "destination_link_audit_summary": row.get("destination_link_audit_summary") or {},
        "failed_review_checks": failed,
        "approval_effect": row.get("approval_effect") or {},
        "preview_command": row.get("approval_preview_command") or "",
        "apply_command": row.get("approval_apply_command") or "",
        "manual_dispatch_required": bool(row.get("manual_dispatch")),
    }


def approval_docket(checked_rows: list[dict], blocked_rows: list[dict], summary: dict) -> dict:
    return {
        "status": "ready_for_review" if checked_rows else "blocked",
        "ready_count": len(checked_rows),
        "held_count": len(blocked_rows),
        "ready_to_approve": [docket_row(row) for row in checked_rows],
        "held": [docket_row(row) for row in blocked_rows],
        "checked_batch_preview_command": summary.get("checked_batch_preview_command") or "",
        "checked_batch_apply_command": summary.get("checked_batch_apply_command") or "",
        "checked_batch_dry_run_preview": summary.get("checked_batch_dry_run_preview") or {},
        "checked_batch_effect": summary.get("checked_batch_effect") or {},
        "guardrails": [
            "Review paste text, destination links, media, and platform readiness before applying the checked batch.",
            "Use --checked-batch so held rows with failed checks stay excluded.",
            "Manual-dispatch rows still need manual posting and public URL logging after approval.",
        ],
    }


def decision_manifest_row(row: dict, *, decision: str) -> dict:
    failed = row.get("failed_review_checks") or []
    passed = [item for item in row.get("review_checks") or [] if item.get("status") == "pass"]
    next_step = (
        "Apply through --checked-batch after human copy/media/link review."
        if decision == "ready_to_approve"
        else "Repair failed checks before including this row in an approval batch."
    )
    if decision == "ready_to_approve" and row.get("manual_dispatch"):
        next_step = "Apply through --checked-batch, then post manually and log the public URL."
    return {
        "id": row.get("id") or "",
        "decision": decision,
        "platform": row.get("platform") or "",
        "song": row.get("song") or "",
        "execution_mode": row.get("execution_mode") or "",
        "scheduled_at": row.get("scheduled_at") or "",
        "checked_batch_member": bool(row.get("checked_batch_member")),
        "approval_effect": row.get("approval_effect") or {},
        "passed_check_names": [item.get("name") for item in passed if item.get("name")],
        "failed_check_names": [item.get("name") for item in failed if item.get("name")],
        "decision_reason": row.get("approval_batch_reason") or "",
        "post_approval_next_step": next_step,
        "manual_dispatch_required": bool(row.get("manual_dispatch")),
    }


def approval_decision_manifest(checked_rows: list[dict], blocked_rows: list[dict], summary: dict) -> dict:
    ready = [decision_manifest_row(row, decision="ready_to_approve") for row in checked_rows]
    held = [decision_manifest_row(row, decision="held") for row in blocked_rows]
    return {
        "status": "ready_for_review" if ready else "blocked",
        "ready_ids": [row.get("id") for row in ready if row.get("id")],
        "held_ids": [row.get("id") for row in held if row.get("id")],
        "decisions": ready + held,
        "expected_checked_batch_effect": summary.get("checked_batch_effect") or {},
        "checked_batch_dry_run_preview": summary.get("checked_batch_dry_run_preview") or {},
        "review_command": summary.get("checked_batch_preview_command") or "",
        "apply_after_review_command": summary.get("checked_batch_apply_command") or "",
        "guardrail": "Only ready_to_approve decisions may be applied through --checked-batch; held rows require repair first.",
    }


def platform_slug(platform: str) -> str:
    value = str(platform or "").strip().lower()
    return {
        "youtube community": "youtube",
        "x": "x",
        "instagram": "instagram",
        "tiktok": "tiktok",
        "facebook": "facebook",
    }.get(value, value)


def links_in_text(value: str) -> list[str]:
    return [match.group(0).rstrip(".,);]") for match in URL_RE.finditer(value or "")]


def canonical_url(value: str) -> str:
    parsed = urlparse(value or "")
    if not parsed.scheme or not parsed.netloc:
        return value or ""
    return parsed._replace(query="", fragment="").geturl().rstrip("/")


def add_destination_evidence(
    evidence: dict[str, list[dict]],
    url: str,
    *,
    source: str,
    label: str,
    status: str,
) -> None:
    if not url:
        return
    key = canonical_url(url)
    item = {"source": source, "label": label, "status": status}
    evidence.setdefault(key, [])
    if item not in evidence[key]:
        evidence[key].append(item)


def destination_evidence_index() -> dict[str, list[dict]]:
    evidence: dict[str, list[dict]] = {}

    hyperfollow = read_json(HYPERFOLLOW_SNAPSHOT, {})
    for item in hyperfollow.get("links") or []:
        add_destination_evidence(
            evidence,
            item.get("url") or "",
            source=str(HYPERFOLLOW_SNAPSHOT.relative_to(ROOT)),
            label=f"HyperFollow {item.get('store') or 'store'} link",
            status="known_store_link",
        )

    alignment = read_json(ALIGNMENT_AUDIT, {})
    for service, item in ((alignment.get("checks") or {}).items()):
        if isinstance(item, dict):
            add_destination_evidence(
                evidence,
                item.get("url") or "",
                source=str(ALIGNMENT_AUDIT.relative_to(ROOT)),
                label=f"{service} alignment check: {item.get('status') or 'unknown'}",
                status="known_alignment_check",
            )

    apple = read_json(APPLE_MUSIC_SNAPSHOT, {})
    add_destination_evidence(
        evidence,
        apple.get("release_url") or "",
        source=str(APPLE_MUSIC_SNAPSHOT.relative_to(ROOT)),
        label=f"Apple Music release snapshot: {apple.get('collection_name') or 'release'}",
        status="known_release_snapshot",
    )

    youtube = read_json(YOUTUBE_TITLE_TRACK, {})
    add_destination_evidence(
        evidence,
        youtube.get("url") or "",
        source=str(YOUTUBE_TITLE_TRACK.relative_to(ROOT)),
        label=f"YouTube title-track snapshot: {youtube.get('public_title') or 'title track'}",
        status="known_release_snapshot",
    )
    add_destination_evidence(
        evidence,
        youtube.get("author_url") or "",
        source=str(YOUTUBE_TITLE_TRACK.relative_to(ROOT)),
        label=f"YouTube artist channel snapshot: {youtube.get('author_name') or 'artist channel'}",
        status="known_artist_profile",
    )

    youtube_music = read_json(YOUTUBE_MUSIC_SNAPSHOT, {})
    youtube_music_label = f"YouTube Music release snapshot: {youtube_music.get('public_title') or 'release'}"
    add_destination_evidence(
        evidence,
        youtube_music.get("release_url") or "",
        source=str(YOUTUBE_MUSIC_SNAPSHOT.relative_to(ROOT)),
        label=youtube_music_label,
        status="known_release_snapshot",
    )
    add_destination_evidence(
        evidence,
        youtube_music.get("canonical_url") or "",
        source=str(YOUTUBE_MUSIC_SNAPSHOT.relative_to(ROOT)),
        label=youtube_music_label,
        status="known_release_snapshot",
    )

    return evidence


def audit_destination_links(links: list[str], evidence: dict[str, list[dict]]) -> list[dict]:
    audit = []
    for url in links:
        matched = evidence.get(canonical_url(url), [])
        audit.append({
            "url": url,
            "canonical_url": canonical_url(url),
            "status": "verified_local_evidence" if matched else "needs_manual_review",
            "evidence": matched,
            "evidence_count": len(matched),
            "guardrail": "Local snapshot/evidence audit only; no approval or live network check was performed.",
        })
    return audit


def audit_summary(audit: list[dict]) -> dict:
    verified = sum(1 for item in audit if item.get("status") == "verified_local_evidence")
    return {
        "link_count": len(audit),
        "verified_local_evidence_count": verified,
        "needs_manual_review_count": len(audit) - verified,
        "all_links_have_local_evidence": bool(audit) and verified == len(audit),
    }


def audit_sources_line(audit: dict) -> str:
    evidence = audit.get("evidence") or []
    if not evidence:
        return "no local evidence"
    return "; ".join(f"{item.get('label')} ({item.get('source')})" for item in evidence)


def local_public_path(url: str) -> Path | None:
    parsed = urlparse(url or "")
    if parsed.netloc not in {"www.lilyroo.com", "lilyroo.com", "lilyrooartist.github.io"}:
        return None
    if not parsed.path:
        return None
    return ROOT / parsed.path.lstrip("/")


def check(name: str, status: str, detail: str) -> dict:
    return {"name": name, "status": status, "detail": detail}


def review_checks(row: dict[str, str], item: dict, readiness: dict) -> list[dict]:
    checks = []
    text = row.get("text") or ""
    reply_text = row.get("reply_text") or ""
    media_url = row.get("clip_url") or row.get("imagery_url") or ""
    links = links_in_text("\n".join([text, reply_text]))
    local_asset = local_public_path(media_url)
    platform = row.get("platform") or item.get("platform") or ""
    platform_ready = ((readiness.get("summary") or {}).get("platforms") or {}).get(platform)
    platform_payload = ((readiness.get("payload") or {}).get("platforms") or {}).get(platform_slug(platform)) or {}
    missing_secrets = ", ".join(platform_payload.get("missing_secrets") or [])

    checks.append(check(
        "copy_present",
        "pass" if text else "fail",
        f"{len(text)} characters of primary copy." if text else "Primary copy is empty.",
    ))
    checks.append(check(
        "destination_links_present",
        "pass" if links else "fail",
        f"{len(links)} link(s): {', '.join(links)}" if links else "No destination links found in copy or reply text.",
    ))
    if media_url and local_asset:
        checks.append(check(
            "asset_file_present",
            "pass" if local_asset.exists() else "fail",
            f"{media_url} maps to {local_asset.relative_to(ROOT)}.",
        ))
    elif media_url:
        checks.append(check("asset_file_present", "review", f"{media_url} is external; review manually."))
    else:
        checks.append(check("asset_file_present", "fail", "No media URL is attached."))
    checks.append(check(
        "executor_blocker_confirmed",
        "pass" if item.get("reason") == "not_approved" else "review",
        f"Current executor state is {item.get('status') or 'unknown'} / {item.get('reason') or 'unknown'}.",
    ))
    if platform_ready is True:
        readiness_detail = "Executor readiness snapshot marks platform ready."
        readiness_status = "pass"
    elif platform_ready is False:
        readiness_detail = "Executor readiness snapshot marks platform blocked."
        if missing_secrets:
            readiness_detail += f" Missing secrets: {missing_secrets}."
        readiness_status = "fail"
    else:
        readiness_detail = "Platform readiness is absent from the snapshot."
        readiness_status = "review"
    checks.append(check("platform_readiness", readiness_status, readiness_detail))
    return checks


def checks_passed(checks: list[dict]) -> bool:
    return bool(checks) and all(item.get("status") == "pass" for item in checks)


def approval_review_status(checks: list[dict]) -> str:
    if checks_passed(checks):
        return "checked_batch_ready"
    if any(item.get("status") == "fail" for item in checks):
        return "held_by_failed_checks"
    return "needs_manual_review"


def failed_review_checks(checks: list[dict]) -> list[dict]:
    return [item for item in checks if item.get("status") == "fail"]


def build_rows(queue: dict[str, dict[str, str]], executions: dict, readiness: dict, evidence: dict[str, list[dict]]) -> list[dict]:
    rows = []
    for item in (executions.get("summary") or {}).get("approval_needed") or []:
        post_id = item.get("post_id") or ""
        row = queue.get(post_id) or {}
        if not row:
            continue
        media_url = row.get("clip_url") or row.get("imagery_url") or ""
        destination_links = links_in_text(copy_block(row))
        link_audit = audit_destination_links(destination_links, evidence)
        checks = review_checks(row, item, readiness)
        review_status = approval_review_status(checks)
        rows.append({
            "id": post_id,
            "platform": row.get("platform") or item.get("platform") or "",
            "song": row.get("song") or "",
            "scheduled_at": row.get("scheduled_at") or "",
            "execution_mode": row.get("execution_mode") or "",
            "post_type": row.get("post_type") or "",
            "approved": row.get("approved") or "",
            "status": item.get("status") or "",
            "reason": item.get("reason") or "",
            "attempts": item.get("attempts") or 0,
            "text": row.get("text") or "",
            "reply_text": row.get("reply_text") or "",
            "copy_block": copy_block(row),
            "imagery_url": row.get("imagery_url") or "",
            "clip_url": row.get("clip_url") or "",
            "asset_url": media_url,
            "destination_links": destination_links,
            "destination_link_audit": link_audit,
            "destination_link_audit_summary": audit_summary(link_audit),
            "media_key": row.get("media_key") or "",
            "desired_privacy": row.get("desired_privacy") or "",
            "review_checks": checks,
            "review_check_passed": checks_passed(checks),
            "failed_review_checks": failed_review_checks(checks),
            "approval_review_status": review_status,
            "checked_batch_member": review_status == "checked_batch_ready",
            "approval_batch_reason": "All automated review checks passed." if review_status == "checked_batch_ready" else "Held outside checked batch until failed/review checks clear.",
            "approval_effect": approval_effect(row),
            "approval_preview_command": approval_preview_command(post_id),
            "approval_apply_command": approval_apply_command(post_id),
            "recommendation": "Review copy, media, destination links, and platform readiness before approval.",
            "manual_dispatch": row.get("execution_mode") == "manual",
        })
    return sorted(rows, key=lambda row: (row.get("scheduled_at") or "", row.get("platform") or "", row.get("id") or ""))


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Scheduled Approval Packet - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Approval blockers: **{summary['approval_blocker_count']}**",
        f"- Auto rows: **{summary['auto_count']}**",
        f"- Manual rows: **{summary['manual_count']}**",
        f"- Review checks passed: **{summary['review_check_passed_count']}**",
        f"- Review checks blocked: **{summary['review_check_blocked_count']}**",
        f"- Checked batch IDs: `{', '.join(summary['checked_batch_ids'])}`" if summary.get("checked_batch_ids") else "- Checked batch IDs: none",
        f"- Blocked review IDs: `{', '.join(summary['blocked_review_ids'])}`" if summary.get("blocked_review_ids") else "- Blocked review IDs: none",
        f"- Checked-only preview: `{summary['checked_batch_preview_command']}`" if summary.get("checked_batch_preview_command") else "- Checked-only preview: none",
        f"- Checked-only approve after review: `{summary['checked_batch_apply_command']}`" if summary.get("checked_batch_apply_command") else "- Checked-only approve after review: none",
        f"- Checked-only explicit preview: `{summary['checked_batch_explicit_preview_command']}`" if summary.get("checked_batch_explicit_preview_command") else "- Checked-only explicit preview: none",
        f"- Checked-only explicit approve after review: `{summary['checked_batch_explicit_apply_command']}`" if summary.get("checked_batch_explicit_apply_command") else "- Checked-only explicit approve after review: none",
        f"- Checked-only effect: **{summary['checked_batch_effect']['change_count']}** row(s) would change approval state" if summary.get("checked_batch_effect") else "- Checked-only effect: none",
        f"- Batch preview: `{summary['batch_preview_command']}`" if summary.get("batch_preview_command") else "- Batch preview: none",
        f"- Batch approve after review: `{summary['batch_apply_command']}`" if summary.get("batch_apply_command") else "- Batch approve after review: none",
        f"- Batch effect: **{summary['batch_effect']['change_count']}** row(s) would change approval state" if summary.get("batch_effect") else "- Batch effect: none",
        "",
        "## Approval Docket",
    ]
    docket = payload.get("approval_docket") or {}
    decision_manifest = payload.get("approval_decision_manifest") or {}
    lines.extend([
        f"- Status: **{docket.get('status', 'unknown')}**",
        f"- Ready to approve: **{docket.get('ready_count', 0)}**",
        f"- Held: **{docket.get('held_count', 0)}**",
        f"- Checked batch preview: `{docket.get('checked_batch_preview_command') or 'none'}`",
        f"- Checked batch approve after review: `{docket.get('checked_batch_apply_command') or 'none'}`",
        f"- Checked batch dry-run result: **{(docket.get('checked_batch_dry_run_preview') or {}).get('change_count', 0)}** change(s), **{(docket.get('checked_batch_dry_run_preview') or {}).get('row_count', 0)}** reviewed row(s), no files written",
        f"- Decision manifest: **{len(decision_manifest.get('decisions') or [])}** reviewed row(s); ready `{', '.join(decision_manifest.get('ready_ids') or []) or 'none'}`; held `{', '.join(decision_manifest.get('held_ids') or []) or 'none'}`",
        "",
        "### Ready to Approve",
    ])
    ready_rows = docket.get("ready_to_approve") or []
    if ready_rows:
        for item in ready_rows:
            lines.append(f"- **{item['platform']} - {item['song']}** (`{item['id']}`)")
            lines.append(f"  - Scheduled: `{item['scheduled_at']}`; mode: `{item['execution_mode']}`; type: `{item['post_type']}`")
            lines.append(f"  - Paste text: {item['paste_text']}")
            lines.append(f"  - Asset: {item['asset_url']}")
            if item.get("destination_links"):
                lines.append(f"  - Destination links: {', '.join(item['destination_links'])}")
            if item.get("destination_link_audit"):
                lines.append("  - Destination link evidence:")
                for audit in item["destination_link_audit"]:
                    lines.append(f"    - `{audit['status']}` {audit['url']}: {audit_sources_line(audit)}")
            if item.get("manual_dispatch_required"):
                lines.append("  - Manual dispatch required after approval.")
            lines.append(f"  - Preview: `{item['preview_command']}`")
            lines.append(f"  - Apply after review: `{item['apply_command']}`")
    else:
        lines.append("- None")
    lines.extend([
        "",
        "### Held",
    ])
    held_rows = docket.get("held") or []
    if held_rows:
        for item in held_rows:
            lines.append(f"- **{item['platform']} - {item['song']}** (`{item['id']}`)")
            for failed in item.get("failed_review_checks") or []:
                lines.append(f"  - Held by `{failed.get('name')}`: {failed.get('detail')}")
    else:
        lines.append("- None")
    lines.extend([
        "",
        "## Review Queue",
    ])
    for row in payload["rows"]:
        lines.append(f"- **{row['platform']} - {row['song']}** (`{row['id']}`)")
        lines.append(f"  - Scheduled: `{row['scheduled_at']}`; mode: `{row['execution_mode']}`; type: `{row['post_type']}`")
        lines.append(f"  - Reason: `{row['reason']}`")
        lines.append(f"  - Copy: {row['text']}")
        if row.get("reply_text"):
            lines.append(f"  - Link/reply: {row['reply_text']}")
        if row.get("asset_url"):
            lines.append(f"  - Asset: {row['asset_url']}")
        if row.get("review_checks"):
            lines.append("  - Review checks:")
            for item in row["review_checks"]:
                lines.append(f"    - `{item['status']}` {item['name']}: {item['detail']}")
        if row.get("destination_link_audit"):
            lines.append("  - Destination link evidence:")
            for audit in row["destination_link_audit"]:
                lines.append(f"    - `{audit['status']}` {audit['url']}: {audit_sources_line(audit)}")
        lines.append(f"  - Approval review status: `{row.get('approval_review_status')}`")
        lines.append(f"  - Checked batch member: `{row.get('checked_batch_member')}`")
        if row.get("failed_review_checks"):
            lines.append("  - Failed checks holding this row:")
            for item in row["failed_review_checks"]:
                lines.append(f"    - `{item['name']}`: {item['detail']}")
        if row.get("approval_batch_reason"):
            lines.append(f"  - Batch reason: {row['approval_batch_reason']}")
        if row.get("approval_effect"):
            effect = row["approval_effect"]
            lines.append(f"  - Approval effect: `{effect['summary']}`")
        lines.append(f"  - Preview approval: `{row['approval_preview_command']}`")
        lines.append(f"  - Approve after review: `{row['approval_apply_command']}`")
    lines.extend([
        "",
        "## Guardrails",
        "- This packet does not approve, publish, or post anything.",
        "- Use preview commands before approval apply commands.",
        "- Manual rows still require human posting and public URL logging after approval.",
        "",
    ])
    return "\n".join(lines)


def replace_json_embed(html: str, block_id: str, payload) -> str:
    marker = f'<script type="application/json" id="{block_id}">'
    end_marker = "</script>"
    encoded = json.dumps(payload, indent=2, ensure_ascii=False)
    start = html.find(marker)
    if start == -1:
        return html.replace("<script>", f"\n{marker}{encoded}{end_marker}\n\n<script>", 1)
    start_content = start + len(marker)
    end = html.find(end_marker, start_content)
    if end == -1:
        raise RuntimeError(f"Could not find end marker for {block_id}")
    return html[:start_content] + encoded + html[end:]


def replace_text_embed(html: str, block_id: str, content: str) -> str:
    marker = f'<script type="text/plain" id="{block_id}">'
    end_marker = "</script>"
    start = html.find(marker)
    if start == -1:
        return html.replace("<script>", f"\n{marker}{content.rstrip()}{end_marker}\n\n<script>", 1)
    start_content = start + len(marker)
    end = html.find(end_marker, start_content)
    if end == -1:
        raise RuntimeError(f"Could not find end marker for {block_id}")
    return html[:start_content] + content.rstrip() + html[end:]


def sync_admin(payload: dict, markdown: str) -> None:
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    html = replace_json_embed(html, "embedded-scheduled-approval-packet", payload)
    html = replace_text_embed(html, "embedded-scheduled-approval-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    queue = read_queue()
    executions = read_json(EXECUTIONS, {})
    readiness = read_json(EXECUTOR_READINESS, {})
    evidence = destination_evidence_index()
    rows = build_rows(queue, executions, readiness, evidence)
    checked_rows = [row for row in rows if row.get("review_check_passed")]
    blocked_rows = [row for row in rows if not row.get("review_check_passed")]
    review_check_status_counts = {}
    for row in rows:
        for item in row.get("review_checks") or []:
            status = item.get("status") or "unknown"
            review_check_status_counts[status] = review_check_status_counts.get(status, 0) + 1
    batch_preview_command = approval_batch_command(rows, dry_run=True)
    batch_apply_command = approval_batch_command(rows, dry_run=False)
    checked_batch_preview_command = approval_checked_batch_command(checked_rows, dry_run=True)
    checked_batch_apply_command = approval_checked_batch_command(checked_rows, dry_run=False)
    checked_batch_explicit_preview_command = approval_batch_command(checked_rows, dry_run=True)
    checked_batch_explicit_apply_command = approval_batch_command(checked_rows, dry_run=False)
    checked_batch_effect = approval_effect_summary(checked_rows)
    batch_effect = approval_effect_summary(rows)
    summary = {
        "approval_blocker_count": len(rows),
        "auto_count": sum(1 for row in rows if row.get("execution_mode") == "auto"),
        "manual_count": sum(1 for row in rows if row.get("execution_mode") == "manual"),
        "review_check_passed_count": sum(1 for row in rows if row.get("review_check_passed")),
        "review_check_blocked_count": sum(1 for row in rows if not row.get("review_check_passed")),
        "checked_batch_ids": [row.get("id") for row in checked_rows if row.get("id")],
        "blocked_review_ids": [row.get("id") for row in blocked_rows if row.get("id")],
        "review_check_status_counts": dict(sorted(review_check_status_counts.items())),
        "checked_batch_preview_command": checked_batch_preview_command,
        "checked_batch_apply_command": checked_batch_apply_command,
        "checked_batch_explicit_preview_command": checked_batch_explicit_preview_command,
        "checked_batch_explicit_apply_command": checked_batch_explicit_apply_command,
        "checked_batch_effect": checked_batch_effect,
        "preview_command_count": sum(1 for row in rows if row.get("approval_preview_command")),
        "apply_command_count": sum(1 for row in rows if row.get("approval_apply_command")),
        "batch_preview_command": batch_preview_command,
        "batch_apply_command": batch_apply_command,
        "batch_effect": batch_effect,
    }
    summary["checked_batch_dry_run_preview"] = checked_batch_dry_run_preview(checked_rows, summary)
    payload = {
        "generated_at": now,
        "safe_mode": True,
        "source": {
            "scheduled_posts": str(QUEUE.relative_to(ROOT)),
            "social_execution_snapshot": str(EXECUTIONS.relative_to(ROOT)),
            "executor_readiness": str(EXECUTOR_READINESS.relative_to(ROOT)),
            "destination_evidence": [
                str(path.relative_to(ROOT))
                for path in [
                    HYPERFOLLOW_SNAPSHOT,
                    ALIGNMENT_AUDIT,
                    APPLE_MUSIC_SNAPSHOT,
                    YOUTUBE_TITLE_TRACK,
                    YOUTUBE_MUSIC_SNAPSHOT,
                ]
            ],
        },
        "summary": summary,
        "approval_docket": approval_docket(checked_rows, blocked_rows, summary),
        "approval_decision_manifest": approval_decision_manifest(checked_rows, blocked_rows, summary),
        "rows": rows,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(payload)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(payload, markdown)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), "approval_blockers": len(rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
