#!/usr/bin/env python3
from __future__ import annotations

import json
import shlex
import csv
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMO_PLAN = ROOT / "data" / "promo_queue_plan.json"
APPROVAL_RUNWAY = ROOT / "data" / "approval_runway.json"
PUBLISHED_LOG = ROOT / "admin" / "content" / "Published_Log.csv"
OUT = ROOT / "data" / "manual_distribution_packet.json"
REPORT = ROOT / "admin" / "reports" / "manual-distribution-packet.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"
YOUTUBE_CHANNEL_URL = "https://www.youtube.com/@lilyroo.artist"
YOUTUBE_COMMUNITY_URL = "https://www.youtube.com/@lilyroo.artist/community"
URL_RE = re.compile(r"https?://[^\s|]+")


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def runway_lookup(runway: dict) -> dict[str, dict]:
    return {
        row.get("id"): row
        for row in runway.get("rows") or []
        if row.get("id")
    }


def published_lookup() -> dict[str, dict]:
    if not PUBLISHED_LOG.exists():
        return {}
    with PUBLISHED_LOG.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    lookup = {}
    for row in rows:
        content_id = (row.get("content_id") or "").strip()
        notes = row.get("notes") or ""
        manual_id = ""
        for part in notes.split(";"):
            part = part.strip()
            if part.startswith("manual_distribution_id="):
                manual_id = part.split("=", 1)[1].strip()
                break
        for key in {content_id, manual_id}:
            if key:
                lookup[key] = {
                    "logged": True,
                    "logged_at": row.get("date") or "",
                    "published_url": row.get("post_id_or_url") or "",
                    "published_log_content_id": content_id,
                    "published_log_notes": notes,
                }
    return lookup


def copy_block(post: dict) -> str:
    parts = [post.get("text") or ""]
    if post.get("reply_text"):
        parts.append(post.get("reply_text") or "")
    return "\n\n".join(part for part in parts if part)


def links_in_text(value: str) -> list[str]:
    return [match.group(0).rstrip(".,);]") for match in URL_RE.finditer(value or "")]


def log_command(post_id: str, apply: bool = False) -> str:
    command = f"python3 scripts/log_manual_distribution.py --id {shlex.quote(post_id)} --url PUBLIC_URL"
    if apply:
        command += " --apply --refresh-admin"
    return command


def log_effect(post: dict, published_row: dict) -> dict:
    post_id = post.get("id") or ""
    logged = bool(published_row.get("logged"))
    notes = f"manual_distribution_id={post_id}; source=data/manual_distribution_packet.json"
    return {
        "target": "admin/content/Published_Log.csv",
        "content_id": post_id,
        "platform": post.get("platform") or "Manual",
        "release": post.get("song") or "",
        "requires_public_url": not logged,
        "url_placeholder": "PUBLIC_URL",
        "duplicate_checked_by": ["content_id", "manual_distribution_id"],
        "notes": notes,
        "would_append": not logged,
        "summary": (
            "already logged; no append needed"
            if logged
            else f"append Published_Log.csv content_id={post_id} after public URL is available"
        ),
    }


def manual_posting_packet(post: dict, approved: str, logged: bool, distribution_status: str, published_row: dict, approval_command: str) -> dict:
    post_id = post.get("id") or ""
    approval_required = approved != "yes"
    postable_now = approved == "yes" and not logged
    if logged:
        next_action = "already_logged"
        next_command = ""
    elif approval_required:
        next_action = "review_and_approve"
        next_command = approval_command
    else:
        next_action = "post_manually_then_log_url"
        next_command = log_command(post_id)
    return {
        "posting_surface": "YouTube Studio Community",
        "public_channel_url": YOUTUBE_CHANNEL_URL,
        "public_community_url": YOUTUBE_COMMUNITY_URL,
        "paste_text": copy_block(post),
        "asset_url": post.get("clip_url") or post.get("imagery_url") or "",
        "approval_required": approval_required,
        "postable_now": postable_now,
        "logging_required": not logged,
        "logged": logged,
        "published_url": published_row.get("published_url") or "",
        "distribution_status": distribution_status,
        "next_action": next_action,
        "next_command": next_command,
    }


def docket_row(row: dict) -> dict:
    posting = row.get("manual_posting_packet") or {}
    paste_text = posting.get("paste_text") or row.get("copy_block") or ""
    return {
        "id": row.get("id") or "",
        "platform": row.get("platform") or "",
        "release": row.get("release") or "",
        "scheduled_at": row.get("scheduled_at") or "",
        "distribution_status": row.get("distribution_status") or "",
        "subscriber_growth_score": row.get("subscriber_growth_score"),
        "selected_cta_strength": row.get("selected_cta_strength") or "",
        "posting_surface": posting.get("posting_surface") or "YouTube Studio Community",
        "public_community_url": posting.get("public_community_url") or YOUTUBE_COMMUNITY_URL,
        "paste_text": paste_text,
        "asset_url": posting.get("asset_url") or row.get("asset_download_url") or "",
        "destination_links": links_in_text(paste_text),
        "approval_required": bool(posting.get("approval_required")),
        "postable_now": bool(posting.get("postable_now")),
        "logging_required": bool(posting.get("logging_required")),
        "logged": bool(row.get("logged")),
        "published_url": row.get("published_url") or "",
        "next_action": posting.get("next_action") or "",
        "next_command": posting.get("next_command") or "",
        "approval_preview_command": row.get("approval_preview_command") or "",
        "approval_command": row.get("approval_command") or "",
        "log_preview_command": row.get("log_preview_command") or "",
        "log_apply_command": row.get("log_apply_command") or "",
        "log_effect": row.get("log_effect") or {},
    }


def manual_distribution_docket(rows: list[dict], summary: dict) -> dict:
    review_rows = [row for row in rows if (row.get("manual_posting_packet") or {}).get("approval_required") and not row.get("logged")]
    postable_rows = [row for row in rows if (row.get("manual_posting_packet") or {}).get("postable_now") and not row.get("logged")]
    logged_rows = [row for row in rows if row.get("logged")]
    status = "empty"
    if postable_rows:
        status = "postable_now"
    elif review_rows:
        status = "needs_review"
    elif logged_rows:
        status = "logged"
    return {
        "status": status,
        "review_count": len(review_rows),
        "postable_count": len(postable_rows),
        "logged_count": len(logged_rows),
        "review_queue": [docket_row(row) for row in review_rows],
        "postable_now": [docket_row(row) for row in postable_rows],
        "logged": [docket_row(row) for row in logged_rows],
        "next_manual_action": summary.get("next_manual_action") or "none",
        "public_community_url": summary.get("public_community_url") or YOUTUBE_COMMUNITY_URL,
        "guardrails": [
            "Manual posting happens in YouTube Studio Community, outside this repository.",
            "Approve a row before posting it, then log only after the public URL exists.",
            "Use the log preview command before applying a Published_Log.csv update.",
        ],
    }


def manual_approval_docket(runway: dict, rows: list[dict]) -> dict:
    docket = runway.get("manual_approval_docket") or {}
    ready_ids = docket.get("ready_ids") or []
    blocked_ids = docket.get("blocked_ids") or []
    rows_by_id = {row.get("id"): row for row in rows if row.get("id")}
    ready_rows = [
        {
            "id": post_id,
            "release": rows_by_id.get(post_id, {}).get("release") or "",
            "platform": rows_by_id.get(post_id, {}).get("platform") or "",
            "distribution_status": rows_by_id.get(post_id, {}).get("distribution_status") or "",
            "subscriber_growth_score": rows_by_id.get(post_id, {}).get("subscriber_growth_score"),
            "postable_after_approval": bool((rows_by_id.get(post_id, {}).get("manual_posting_packet") or {}).get("approval_required")),
        }
        for post_id in ready_ids
        if post_id in rows_by_id
    ]
    status = docket.get("status") or ("ready_for_manual_review" if ready_rows else "empty")
    return {
        "status": status,
        "ready_count": len(ready_rows),
        "blocked_count": len(blocked_ids),
        "ready_ids": [row["id"] for row in ready_rows],
        "blocked_ids": blocked_ids,
        "preview_command": docket.get("preview_command") or "",
        "apply_command": docket.get("apply_command") or "",
        "guardrail": docket.get("guardrail") or "Manual-only approvals do not auto-post; posting and public URL logging remain separate after review.",
        "ready_to_review": ready_rows,
    }


def build_rows(plan: dict, runway: dict, published: dict[str, dict]) -> list[dict]:
    runway_by_id = runway_lookup(runway)
    rows = []
    for post in plan.get("posts") or []:
        if post.get("execution_mode") != "manual":
            continue
        review = runway_by_id.get(post.get("id")) or {}
        published_row = published.get(post.get("id") or "") or {}
        logged = bool(published_row.get("logged"))
        approved = post.get("approved") or "no"
        if logged:
            distribution_status = "logged"
        elif approved == "yes":
            distribution_status = "ready_for_manual_post"
        else:
            distribution_status = "waiting_for_review"
        approval_command = review.get("approval_command") or post.get("approval_command") or ""
        posting_packet = manual_posting_packet(post, approved, logged, distribution_status, published_row, approval_command)
        rows.append({
            "id": post.get("id") or "",
            "platform": post.get("platform") or "",
            "release": post.get("song") or "",
            "scheduled_at": post.get("scheduled_at") or "",
            "post_type": post.get("post_type") or "",
            "approved": approved,
            "distribution_status": distribution_status,
            "logged": logged,
            "logged_at": published_row.get("logged_at") or "",
            "published_url": published_row.get("published_url") or "",
            "published_log_content_id": published_row.get("published_log_content_id") or "",
            "readiness_state": review.get("readiness_state") or "",
            "readiness_message": review.get("readiness_message") or "",
            "subscriber_growth_score": review.get("subscriber_growth_score"),
            "selected_cta_strength": post.get("selected_cta_strength") or "",
            "text": post.get("text") or "",
            "reply_text": post.get("reply_text") or "",
            "copy_block": copy_block(post),
            "imagery_url": post.get("imagery_url") or "",
            "clip_url": post.get("clip_url") or "",
            "asset_download_url": post.get("clip_url") or post.get("imagery_url") or "",
            "media_key": post.get("media_key") or "",
            "approval_preview_command": review.get("approval_preview_command") or "",
            "approval_command": approval_command,
            "log_preview_command": log_command(post.get("id") or ""),
            "log_apply_command": log_command(post.get("id") or "", apply=True),
            "log_effect": log_effect(post, published_row),
            "manual_posting_packet": posting_packet,
            "manual_workflow": [
                "Review the copy and linked playlist.",
                "Approve only after human review if it should become the current manual posting candidate.",
                "Post manually in YouTube Studio Community using the copy and asset below.",
                "After posting, run the log preview command with the public URL, then run the apply command to update Published_Log.csv and refresh Admin.",
                "Rows already found in Published_Log.csv are marked logged and should not be treated as pending manual work.",
            ],
        })
    return sorted(rows, key=lambda row: (row["scheduled_at"], row["release"], row["id"]))


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


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Manual Distribution Packet - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Manual-ready posts: **{summary['manual_ready_count']}**",
        f"- YouTube Community posts: **{summary['youtube_community_count']}**",
        f"- Hard subscriber CTAs: **{summary['hard_cta_count']}**",
        f"- Approved manual posts: **{summary['approved_manual_count']}**",
        f"- Logged manual posts: **{summary['logged_manual_count']}**",
        f"- Unlogged manual posts: **{summary['unlogged_manual_count']}**",
        f"- Public URL logs still needed: **{summary['public_url_log_needed_count']}**",
        "",
        "## Manual Posting Docket",
    ]
    docket = payload.get("manual_distribution_docket") or {}
    approval_docket = payload.get("manual_approval_docket") or {}
    lines.extend([
        f"- Status: **{docket.get('status', 'unknown')}**",
        f"- Needs review: **{docket.get('review_count', 0)}**",
        f"- Postable now: **{docket.get('postable_count', 0)}**",
        f"- Logged: **{docket.get('logged_count', 0)}**",
        f"- Public community surface: {docket.get('public_community_url') or YOUTUBE_COMMUNITY_URL}",
        "",
        "### Approval Gate",
        f"- Status: **{approval_docket.get('status', 'unknown')}**",
        f"- Ready approvals: **{approval_docket.get('ready_count', 0)}**",
        f"- Blocked approvals: **{approval_docket.get('blocked_count', 0)}**",
    ])
    if approval_docket.get("ready_ids"):
        lines.append(f"- Ready IDs: `{', '.join(approval_docket['ready_ids'])}`")
    if approval_docket.get("blocked_ids"):
        lines.append(f"- Blocked IDs: `{', '.join(approval_docket['blocked_ids'])}`")
    if approval_docket.get("preview_command"):
        lines.append(f"- Preview approvals: `{approval_docket['preview_command']}`")
    if approval_docket.get("apply_command"):
        lines.append(f"- Approve after review: `{approval_docket['apply_command']}`")
    if approval_docket.get("guardrail"):
        lines.append(f"- Guardrail: {approval_docket['guardrail']}")
    lines.extend([
        "",
        "### Needs Review",
    ])
    review_queue = docket.get("review_queue") or []
    if review_queue:
        for item in review_queue:
            lines.append(f"- **{item['platform']} - {item['release']}** (`{item['id']}`)")
            lines.append(f"  - Paste text: {item['paste_text']}")
            lines.append(f"  - Asset: {item['asset_url']}")
            if item.get("destination_links"):
                lines.append(f"  - Destination links: {', '.join(item['destination_links'])}")
            if item.get("approval_preview_command"):
                lines.append(f"  - Preview approval: `{item['approval_preview_command']}`")
            if item.get("approval_command"):
                lines.append(f"  - Approve after review: `{item['approval_command']}`")
    else:
        lines.append("- None")
    lines.extend([
        "",
        "### Postable Now",
    ])
    postable_now = docket.get("postable_now") or []
    if postable_now:
        for item in postable_now:
            lines.append(f"- **{item['platform']} - {item['release']}** (`{item['id']}`)")
            lines.append(f"  - Paste text: {item['paste_text']}")
            lines.append(f"  - Asset: {item['asset_url']}")
            lines.append(f"  - Log preview after posting: `{item['log_preview_command']}`")
            lines.append(f"  - Log apply after posting: `{item['log_apply_command']}`")
    else:
        lines.append("- None")
    lines.extend([
        "",
        "## Manual Posting Queue",
    ])
    for row in payload["rows"]:
        lines.append(f"- **{row['platform']} - {row['release']}** (`{row['id']}`)")
        lines.append(f"  - Scheduled target: `{row['scheduled_at']}`")
        lines.append(f"  - Distribution status: `{row['distribution_status']}`")
        if row.get("published_url"):
            lines.append(f"  - Published URL: {row['published_url']}")
        lines.append(f"  - Readiness: `{row['readiness_state']}`; CTA: `{row['selected_cta_strength']}`")
        lines.append(f"  - Copy: {row['text']}")
        if row.get("reply_text"):
            lines.append(f"  - Link/reply: {row['reply_text']}")
        if row.get("copy_block"):
            lines.append("  - Paste block:")
            for line in row["copy_block"].splitlines():
                lines.append(f"    {line}" if line else "    ")
        if row.get("asset_download_url"):
            lines.append(f"  - Asset: {row['asset_download_url']}")
        if row.get("manual_posting_packet"):
            packet = row["manual_posting_packet"]
            lines.append(f"  - Next manual action: `{packet.get('next_action')}`")
            lines.append(f"  - Postable now: `{packet.get('postable_now')}`; approval required: `{packet.get('approval_required')}`; logging required: `{packet.get('logging_required')}`")
            lines.append(f"  - Public community surface: {packet.get('public_community_url')}")
            if packet.get("next_command"):
                lines.append(f"  - Next command: `{packet['next_command']}`")
        if row.get("log_effect"):
            lines.append(f"  - Log effect: {row['log_effect']['summary']}")
        if row.get("approval_preview_command"):
            lines.append(f"  - Preview approval: `{row['approval_preview_command']}`")
        if row.get("approval_command"):
            lines.append(f"  - Approve after review: `{row['approval_command']}`")
        if row.get("log_preview_command"):
            lines.append(f"  - Preview public URL log: `{row['log_preview_command']}`")
        if row.get("log_apply_command"):
            lines.append(f"  - Apply public URL log after posting: `{row['log_apply_command']}`")
    lines.extend([
        "",
        "## Guardrails",
        "- This packet does not approve, schedule, publish, or post anything.",
        "- Use it as a human posting checklist for manual YouTube Community distribution.",
        "- Log the public post URL after manual posting so metrics and admin state stay accurate.",
        "",
    ])
    return "\n".join(lines)


def sync_admin(payload: dict, markdown: str) -> None:
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    html = replace_json_embed(html, "embedded-manual-distribution-packet", payload)
    html = replace_text_embed(html, "embedded-manual-distribution-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    now = datetime.now(timezone.utc)
    plan = read_json(PROMO_PLAN, {})
    runway = read_json(APPROVAL_RUNWAY, {})
    published = published_lookup()
    rows = build_rows(plan, runway, published)
    hard_cta = [row for row in rows if row.get("selected_cta_strength") in {"hard_subscribe", "hard_goal"}]
    logged_rows = [row for row in rows if row.get("logged")]
    unlogged_rows = [row for row in rows if not row.get("logged")]
    log_needed_rows = [row for row in rows if (row.get("log_effect") or {}).get("would_append")]
    review_rows = [row for row in unlogged_rows if (row.get("manual_posting_packet") or {}).get("approval_required")]
    postable_rows = [row for row in unlogged_rows if (row.get("manual_posting_packet") or {}).get("postable_now")]
    summary = {
        "manual_ready_count": len(rows),
        "youtube_community_count": sum(1 for row in rows if row.get("platform") == "YouTube Community"),
        "hard_cta_count": len(hard_cta),
        "approved_manual_count": sum(1 for row in rows if str(row.get("approved") or "").lower() == "yes"),
        "logged_manual_count": len(logged_rows),
        "unlogged_manual_count": len(unlogged_rows),
        "public_url_log_needed_count": len(log_needed_rows),
        "ready_to_post_after_review_count": sum(1 for row in unlogged_rows if row.get("readiness_state") == "manual_only"),
        "ready_for_manual_post_count": sum(1 for row in unlogged_rows if row.get("distribution_status") == "ready_for_manual_post"),
        "waiting_for_review_count": sum(1 for row in unlogged_rows if row.get("distribution_status") == "waiting_for_review"),
        "manual_review_required_count": len(review_rows),
        "postable_now_count": len(postable_rows),
        "next_manual_action": "review_and_approve" if review_rows else ("post_manually_then_log_url" if postable_rows else "none"),
        "public_community_url": YOUTUBE_COMMUNITY_URL,
    }
    payload = {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "promo_queue_plan": str(PROMO_PLAN.relative_to(ROOT)),
            "approval_runway": str(APPROVAL_RUNWAY.relative_to(ROOT)),
            "published_log": str(PUBLISHED_LOG.relative_to(ROOT)),
        },
        "summary": summary,
        "manual_approval_docket": manual_approval_docket(runway, rows),
        "manual_distribution_docket": manual_distribution_docket(rows, summary),
        "rows": rows,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(payload)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(payload, markdown)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), "manual_ready": len(rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
