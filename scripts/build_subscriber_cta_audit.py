#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMO_PLAN = ROOT / "data" / "promo_queue_plan.json"
APPROVAL_RUNWAY = ROOT / "data" / "approval_runway.json"
FUTURE_POSTS = ROOT / "admin" / "future-posts.json"
OUT = ROOT / "data" / "subscriber_cta_audit.json"
REPORT = ROOT / "admin" / "reports" / "subscriber-cta-audit.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"


SOLICITATION_TERMS = ("subscribe", "subscribers", "1,000", "1000", "help us", "help lily roo")
YOUTUBE_TERMS = ("youtube", "youtu.be", "youtube.com")
RELEASE_LINK_TERMS = ("album room", "album page", "playlist", "stream", "listen", "echo", "video")
ACTIVE_CAMPAIGN_PREFIX = "FP-BRAND-AM"


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def cta_strength(text: str) -> str:
    lower = str(text or "").lower()
    has_solicitation = any(term in lower for term in SOLICITATION_TERMS)
    has_youtube = any(term in lower for term in YOUTUBE_TERMS)
    if has_solicitation:
        return "solicitation"
    if has_youtube:
        return "youtube_link"
    if any(term in lower for term in RELEASE_LINK_TERMS):
        return "soft_listen"
    return "missing"


def score_strength(strength: str) -> int:
    return {
        "youtube_link": 3,
        "soft_listen": 2,
        "missing": 1,
        "solicitation": 0,
    }.get(strength, 0)


def best_variant(post: dict) -> tuple[str, str]:
    candidates = [post.get("text") or ""]
    candidates.extend(post.get("drafts") or [])
    candidates.append(post.get("reply_text") or "")
    best_text = ""
    best_strength = "missing"
    for candidate in candidates:
        strength = cta_strength(candidate)
        if score_strength(strength) > score_strength(best_strength):
            best_text = candidate
            best_strength = strength
    return best_text, best_strength


def approval_lookup(runway: dict) -> dict:
    return {
        row.get("id"): row
        for row in runway.get("rows") or []
        if row.get("id")
    }


def build_rows(plan: dict, runway: dict) -> list[dict]:
    runway_by_id = approval_lookup(runway)
    rows = []
    for post in plan.get("posts") or []:
        selected = post.get("text") or ""
        selected_strength = cta_strength(selected)
        recommended_text, recommended_strength = best_variant(post)
        readiness = runway_by_id.get(post.get("id")) or {}
        needs_swap = selected_strength == "solicitation" and recommended_strength != "solicitation"
        if str(post.get("approved") or "").lower() == "yes":
            action = "Already approved; do not repost solicitation copy."
        elif needs_swap:
            action = "Use the non-soliciting variant before approval."
        elif selected_strength == "solicitation":
            action = "Selected copy is solicitation-style; rewrite before approval."
        else:
            action = "Selected copy is song-forward and non-soliciting."
        rows.append({
            "id": post.get("id") or "",
            "release": post.get("song") or "",
            "platform": post.get("platform") or "",
            "approved": post.get("approved") or "",
            "readiness_state": readiness.get("readiness_state") or "",
            "selected_strength": selected_strength,
            "recommended_strength": recommended_strength,
            "selected_text": selected,
            "recommended_text": recommended_text,
            "needs_subscriber_cta_swap": needs_swap,
            "approval_preview_command": readiness.get("approval_preview_command") or "",
            "approval_command": readiness.get("approval_command") or post.get("approval_command") or "",
            "action": action,
        })
    return rows


def future_posts(payload) -> list[dict]:
    if isinstance(payload, dict):
        return payload.get("posts") or []
    if isinstance(payload, list):
        return payload
    return []


def future_row_id(row: dict) -> str:
    return str(row.get("id") or row.get("queue_id") or row.get("content_id") or "").strip()


def is_release_forward_future(row: dict) -> bool:
    post_id = future_row_id(row)
    haystack = " ".join(
        str(row.get(key) or "")
        for key in ("song", "text", "hook", "reply_text", "imagery", "notes")
    ).lower()
    return post_id.startswith(ACTIVE_CAMPAIGN_PREFIX) and "analog myth" in haystack


def build_future_rows(payload) -> list[dict]:
    rows = []
    for post in future_posts(payload):
        selected = post.get("text") or post.get("hook") or ""
        full_text = " ".join(
            str(value or "")
            for value in [
                selected,
                post.get("reply_text") or "",
                " ".join(post.get("drafts") or []),
            ]
        )
        selected_strength = cta_strength(full_text)
        auto_ready = (
            str(post.get("approved") or "").lower() == "yes"
            and str(post.get("execution_mode") or "").lower() == "auto"
        )
        release_forward = is_release_forward_future(post)
        issues = []
        if selected_strength == "solicitation":
            issues.append("solicitation")
        if not auto_ready:
            issues.append("not_auto_ready")
        if not release_forward:
            issues.append("not_analog_myth_release_forward")
        rows.append({
            "id": future_row_id(post),
            "release": post.get("song") or "",
            "platform": post.get("platform") or "",
            "scheduled_at": post.get("scheduled_at") or "",
            "approved": post.get("approved") or "",
            "execution_mode": post.get("execution_mode") or "",
            "selected_strength": selected_strength,
            "release_forward": release_forward,
            "auto_ready": auto_ready,
            "issue_count": len(issues),
            "issues": issues,
            "selected_text": selected,
            "action": (
                "Future post is auto-ready, Analog Myth focused, and non-soliciting."
                if not issues
                else "Fix or remove this queued post before relying on the active campaign."
            ),
        })
    return rows


def replace_json_embed(html: str, block_id: str, payload) -> str:
    marker = f'<script type="application/json" id="{block_id}">'
    end_marker = "</script>"
    encoded = json.dumps(payload, indent=2, ensure_ascii=False)
    start = html.find(marker)
    if start == -1:
        insert = f'\n{marker}{encoded}{end_marker}\n'
        return html.replace("<script>", insert + "\n<script>", 1)
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
        insert = f'\n{marker}{content.rstrip()}{end_marker}\n'
        return html.replace("<script>", insert + "\n<script>", 1)
    start_content = start + len(marker)
    end = html.find(end_marker, start_content)
    if end == -1:
        raise RuntimeError(f"Could not find end marker for {block_id}")
    return html[:start_content] + content.rstrip() + html[end:]


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    future_rows = payload.get("active_future_rows") or []
    issue_rows = [row for row in future_rows if row.get("issue_count")]
    lines = [
        "# Solicitation Copy Audit - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Draft posts: **{summary['draft_count']}**",
        f"- Selected solicitation-style CTAs: **{summary['selected_hard_cta_count']}**",
        f"- Non-soliciting swaps available: **{summary['subscriber_swap_count']}**",
        f"- Ready-after-approval rewrites: **{summary['ready_after_approval_swap_count']}**",
        f"- Active future posts checked: **{summary['active_future_count']}**",
        f"- Active future solicitation issues: **{summary['active_future_solicitation_count']}**",
        f"- Active future non-auto issues: **{summary['active_future_non_auto_count']}**",
        f"- Active future Analog Myth focus issues: **{summary['active_future_non_release_forward_count']}**",
        "",
        "## CTA Review Queue",
    ]
    for row in payload["rows"]:
        if not row["needs_subscriber_cta_swap"] and row["selected_strength"] != "solicitation":
            continue
        lines.append(f"- **{row['platform']} - {row['release']}** (`{row['id']}`)")
        lines.append(f"  - Selected strength: `{row['selected_strength']}`; recommended: `{row['recommended_strength']}`")
        lines.append(f"  - Action: {row['action']}")
        if row.get("recommended_text"):
            lines.append(f"  - Recommended copy: {row['recommended_text']}")
        if row.get("approval_preview_command"):
            lines.append(f"  - Preview: `{row['approval_preview_command']}`")
        if row.get("approval_command"):
            lines.append(f"  - Approve after CTA review: `{row['approval_command']}`")
    lines.extend([
        "",
        "## Active Future Queue",
        f"- Status: **{'ready' if summary.get('active_future_ready') else 'needs review'}**",
        "- The active queue should stay automatic, Analog Myth focused, and free of subscriber-count solicitation.",
    ])
    if issue_rows:
        for row in issue_rows:
            lines.append(f"- **{row['platform']} - {row['release']}** (`{row['id']}`)")
            lines.append(f"  - Scheduled: `{row['scheduled_at']}`")
            lines.append(f"  - Issues: `{', '.join(row['issues'])}`")
            lines.append(f"  - Action: {row['action']}")
    else:
        preview_rows = future_rows[:8]
        for row in preview_rows:
            lines.append(
                f"- `{row['id']}` ({row['platform']}): {row['scheduled_at']} - "
                f"{row['selected_strength']}; auto={row['auto_ready']}; release-forward={row['release_forward']}"
            )
    lines.append("")
    lines.append("## Guardrails")
    lines.append("- This audit does not edit, approve, apply, publish, or post anything.")
    lines.append("- Use it to choose stronger copy before running approval commands.")
    lines.append("- Active future posts must remain API-backed and release-forward; manual-only posting is out of scope.")
    lines.append("")
    return "\n".join(lines)


def sync_admin(payload: dict, markdown: str) -> None:
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    html = replace_json_embed(html, "embedded-subscriber-cta-audit", payload)
    html = replace_text_embed(html, "embedded-subscriber-cta-audit-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    now = datetime.now(timezone.utc)
    plan = read_json(PROMO_PLAN, {})
    runway = read_json(APPROVAL_RUNWAY, {})
    future = read_json(FUTURE_POSTS, {})
    rows = build_rows(plan, runway)
    active_future_rows = build_future_rows(future)
    selected_hard = [
        row for row in rows
        if row["selected_strength"] == "solicitation"
    ]
    swaps = [row for row in rows if row["needs_subscriber_cta_swap"]]
    ready_swaps = [
        row for row in swaps
        if row.get("readiness_state") == "ready_after_approval"
    ]
    future_solicitation_rows = [row for row in active_future_rows if row["selected_strength"] == "solicitation"]
    future_non_auto_rows = [row for row in active_future_rows if not row["auto_ready"]]
    future_non_release_rows = [row for row in active_future_rows if not row["release_forward"]]
    active_future_ready = not (future_solicitation_rows or future_non_auto_rows or future_non_release_rows)
    payload = {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "promo_queue_plan": str(PROMO_PLAN.relative_to(ROOT)),
            "approval_runway": str(APPROVAL_RUNWAY.relative_to(ROOT)),
            "future_posts": str(FUTURE_POSTS.relative_to(ROOT)),
        },
        "summary": {
            "draft_count": len(rows),
            "selected_hard_cta_count": len(selected_hard),
            "subscriber_swap_count": len(swaps),
            "ready_after_approval_swap_count": len(ready_swaps),
            "recommended_swap_ids": [row["id"] for row in swaps],
            "ready_after_approval_swap_ids": [row["id"] for row in ready_swaps],
            "active_future_count": len(active_future_rows),
            "active_future_ready": active_future_ready,
            "active_future_solicitation_count": len(future_solicitation_rows),
            "active_future_non_auto_count": len(future_non_auto_rows),
            "active_future_non_release_forward_count": len(future_non_release_rows),
            "active_future_issue_ids": [
                row["id"]
                for row in active_future_rows
                if row.get("issue_count")
            ],
        },
        "rows": rows,
        "active_future_rows": active_future_rows,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(payload)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(payload, markdown)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), "solicitation_swaps": len(swaps)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
