#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMO_PLAN = ROOT / "data" / "promo_queue_plan.json"
APPROVAL_RUNWAY = ROOT / "data" / "approval_runway.json"
OUT = ROOT / "data" / "manual_distribution_packet.json"
REPORT = ROOT / "admin" / "reports" / "manual-distribution-packet.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"


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


def build_rows(plan: dict, runway: dict) -> list[dict]:
    runway_by_id = runway_lookup(runway)
    rows = []
    for post in plan.get("posts") or []:
        if post.get("execution_mode") != "manual":
            continue
        review = runway_by_id.get(post.get("id")) or {}
        rows.append({
            "id": post.get("id") or "",
            "platform": post.get("platform") or "",
            "release": post.get("song") or "",
            "scheduled_at": post.get("scheduled_at") or "",
            "post_type": post.get("post_type") or "",
            "approved": post.get("approved") or "no",
            "readiness_state": review.get("readiness_state") or "",
            "readiness_message": review.get("readiness_message") or "",
            "subscriber_growth_score": review.get("subscriber_growth_score"),
            "selected_cta_strength": post.get("selected_cta_strength") or "",
            "text": post.get("text") or "",
            "reply_text": post.get("reply_text") or "",
            "imagery_url": post.get("imagery_url") or "",
            "clip_url": post.get("clip_url") or "",
            "media_key": post.get("media_key") or "",
            "approval_preview_command": review.get("approval_preview_command") or "",
            "approval_command": review.get("approval_command") or post.get("approval_command") or "",
            "manual_workflow": [
                "Review the copy and linked playlist.",
                "Approve only after human review if it should become the current manual posting candidate.",
                "Post manually in YouTube Studio Community using the copy and asset below.",
                "After posting, append the public URL to admin/content/Published_Log.csv and refresh Admin.",
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
        "",
        "## Manual Posting Queue",
    ]
    for row in payload["rows"]:
        lines.append(f"- **{row['platform']} - {row['release']}** (`{row['id']}`)")
        lines.append(f"  - Scheduled target: `{row['scheduled_at']}`")
        lines.append(f"  - Readiness: `{row['readiness_state']}`; CTA: `{row['selected_cta_strength']}`")
        lines.append(f"  - Copy: {row['text']}")
        if row.get("reply_text"):
            lines.append(f"  - Link/reply: {row['reply_text']}")
        if row.get("imagery_url"):
            lines.append(f"  - Asset: {row['imagery_url']}")
        if row.get("approval_preview_command"):
            lines.append(f"  - Preview approval: `{row['approval_preview_command']}`")
        if row.get("approval_command"):
            lines.append(f"  - Approve after review: `{row['approval_command']}`")
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
    rows = build_rows(plan, runway)
    hard_cta = [row for row in rows if row.get("selected_cta_strength") in {"hard_subscribe", "hard_goal"}]
    payload = {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "promo_queue_plan": str(PROMO_PLAN.relative_to(ROOT)),
            "approval_runway": str(APPROVAL_RUNWAY.relative_to(ROOT)),
        },
        "summary": {
            "manual_ready_count": len(rows),
            "youtube_community_count": sum(1 for row in rows if row.get("platform") == "YouTube Community"),
            "hard_cta_count": len(hard_cta),
            "approved_manual_count": sum(1 for row in rows if str(row.get("approved") or "").lower() == "yes"),
            "ready_to_post_after_review_count": sum(1 for row in rows if row.get("readiness_state") == "manual_only"),
        },
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
