#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMO_PLAN = ROOT / "data" / "promo_queue_plan.json"
APPROVAL_RUNWAY = ROOT / "data" / "approval_runway.json"
OUT = ROOT / "data" / "subscriber_cta_audit.json"
REPORT = ROOT / "admin" / "reports" / "subscriber-cta-audit.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"


HARD_CTA_TERMS = ("subscribe", "subscribers", "1,000", "1000")
YOUTUBE_TERMS = ("youtube", "youtu.be", "youtube.com")


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


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
        needs_swap = score_strength(recommended_strength) > score_strength(selected_strength)
        if str(post.get("approved") or "").lower() == "yes":
            action = "Already approved; keep CTA under metrics observation."
        elif needs_swap:
            action = "Use the stronger subscriber CTA variant before approval."
        elif selected_strength in {"hard_subscribe", "hard_goal"}:
            action = "Selected copy already has a hard subscriber CTA."
        else:
            action = "Selected copy has a soft CTA; review whether the platform needs a harder subscribe ask."
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
    lines = [
        "# Subscriber CTA Audit - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Draft posts: **{summary['draft_count']}**",
        f"- Selected hard CTAs: **{summary['selected_hard_cta_count']}**",
        f"- Stronger subscriber variants available: **{summary['subscriber_swap_count']}**",
        f"- Ready-after-approval swaps: **{summary['ready_after_approval_swap_count']}**",
        "",
        "## CTA Review Queue",
    ]
    for row in payload["rows"]:
        if not row["needs_subscriber_cta_swap"] and row["selected_strength"] not in {"hard_subscribe", "hard_goal"}:
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
    lines.append("")
    lines.append("## Guardrails")
    lines.append("- This audit does not edit, approve, apply, publish, or post anything.")
    lines.append("- Use it to choose stronger copy before running approval commands.")
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
    rows = build_rows(plan, runway)
    selected_hard = [
        row for row in rows
        if row["selected_strength"] in {"hard_subscribe", "hard_goal"}
    ]
    swaps = [row for row in rows if row["needs_subscriber_cta_swap"]]
    ready_swaps = [
        row for row in swaps
        if row.get("readiness_state") == "ready_after_approval"
    ]
    payload = {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "promo_queue_plan": str(PROMO_PLAN.relative_to(ROOT)),
            "approval_runway": str(APPROVAL_RUNWAY.relative_to(ROOT)),
        },
        "summary": {
            "draft_count": len(rows),
            "selected_hard_cta_count": len(selected_hard),
            "subscriber_swap_count": len(swaps),
            "ready_after_approval_swap_count": len(ready_swaps),
            "recommended_swap_ids": [row["id"] for row in swaps],
            "ready_after_approval_swap_ids": [row["id"] for row in ready_swaps],
        },
        "rows": rows,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(payload)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(payload, markdown)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), "subscriber_swaps": len(swaps)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
