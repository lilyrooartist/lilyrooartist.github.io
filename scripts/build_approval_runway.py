#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMO_STATUS = ROOT / "data" / "promo_engine_status.json"
PROMO_PLAN = ROOT / "data" / "promo_queue_plan.json"
OUT = ROOT / "data" / "approval_runway.json"
REPORT = ROOT / "admin" / "reports" / "approval-runway.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def preview_command(command: str) -> str:
    command = str(command or "").strip()
    if not command:
        return ""
    if "--refresh-admin" in command:
        return command.replace("--refresh-admin", "--dry-run").strip()
    if "--dry-run" not in command:
        return command + " --dry-run"
    return command


def readiness_rows(plan: dict) -> dict:
    return {
        row.get("id"): row
        for row in ((plan.get("readiness_audit") or {}).get("rows") or [])
        if row.get("id")
    }


def subscriber_score(post: dict, readiness: dict) -> int:
    state = readiness.get("state") or "unknown"
    platform = str(post.get("platform") or "").lower()
    text = " ".join(str(post.get(key) or "") for key in ("text", "reply_text", "reason")).lower()
    score = {
        "ready_after_approval": 100,
        "manual_only": 75,
        "unknown": 40,
        "blocked": 10,
    }.get(state, 35)
    if "youtube" in platform:
        score += 18
    if "subscribe" in text or "1,000" in text or "1000" in text:
        score += 15
    if "youtube" in text:
        score += 8
    if "tiktok" in platform and state == "blocked":
        score -= 15
    return max(score, 0)


def build_rows(plan: dict) -> list[dict]:
    readiness_by_id = readiness_rows(plan)
    rows = []
    for post in plan.get("posts") or []:
        if str(post.get("approved") or "").lower() == "yes":
            continue
        readiness = readiness_by_id.get(post.get("id")) or {}
        approval_command = post.get("approval_command") or ""
        row = {
            "id": post.get("id") or "",
            "release": post.get("song") or "",
            "platform": post.get("platform") or "",
            "scheduled_at": post.get("scheduled_at") or "",
            "execution_mode": post.get("execution_mode") or "",
            "post_type": post.get("post_type") or "",
            "readiness_state": readiness.get("state") or "unknown",
            "readiness_message": readiness.get("message") or "",
            "text": post.get("text") or "",
            "subscriber_growth_score": subscriber_score(post, readiness),
            "approval_preview_command": preview_command(approval_command),
            "approval_command": approval_command,
        }
        if row["readiness_state"] == "ready_after_approval":
            row["recommendation"] = "Review copy, then approve to unlock an auto-publishable subscriber CTA."
        elif row["readiness_state"] == "manual_only":
            row["recommendation"] = "Review copy and use the manual posting workflow; approval will not auto-post this row."
        elif row["readiness_state"] == "blocked":
            row["recommendation"] = "Repair platform readiness before approval can create reliable distribution."
        else:
            row["recommendation"] = "Review readiness before approving."
        rows.append(row)
    return sorted(rows, key=lambda row: (-row["subscriber_growth_score"], row["platform"], row["id"]))


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
        "# Approval Runway - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Drafts needing review: **{summary['review_count']}**",
        f"- Ready after approval: **{summary['ready_after_approval']}**",
        f"- Manual-only drafts: **{summary['manual_only']}**",
        f"- Blocked drafts: **{summary['blocked']}**",
        f"- Recommended approvals: **{summary['recommended_approval_count']}**",
        f"- Monetization runway: **{summary['runway_status']}**, {summary['subscribers_per_week']} subs/week observed, {summary['required_subscribers_per_week_365']} subs/week needed for 365 days",
        "",
        "## Recommended Sequence",
    ]
    for row in payload["rows"][:8]:
        lines.append(f"- **{row['platform']} - {row['release']}** (`{row['id']}`)")
        lines.append(f"  - Readiness: `{row['readiness_state']}`; score: `{row['subscriber_growth_score']}`")
        lines.append(f"  - Recommendation: {row['recommendation']}")
        if row.get("text"):
            lines.append(f"  - Copy: {row['text']}")
        if row.get("approval_preview_command"):
            lines.append(f"  - Preview: `{row['approval_preview_command']}`")
        if row.get("approval_command"):
            lines.append(f"  - Approve after review: `{row['approval_command']}`")
    lines.append("")
    lines.append("## Guardrails")
    lines.append("- This runway does not approve, apply, publish, or post anything.")
    lines.append("- Run preview commands first, then approval commands only after copy review.")
    lines.append("- Applying approved rows to the live queue remains a separate deliberate step.")
    lines.append("")
    return "\n".join(lines)


def sync_admin(payload: dict, markdown: str) -> None:
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    html = replace_json_embed(html, "embedded-approval-runway", payload)
    html = replace_text_embed(html, "embedded-approval-runway-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    now = datetime.now(timezone.utc)
    status = read_json(PROMO_STATUS, {})
    plan = read_json(PROMO_PLAN, {})
    monetization = (status.get("kpi") or {}).get("monetization") or {}
    runway = monetization.get("runway") or {}
    rows = build_rows(plan)
    ready_rows = [row for row in rows if row["readiness_state"] == "ready_after_approval"]
    summary = {
        "review_count": len(rows),
        "ready_after_approval": len(ready_rows),
        "manual_only": sum(1 for row in rows if row["readiness_state"] == "manual_only"),
        "blocked": sum(1 for row in rows if row["readiness_state"] == "blocked"),
        "recommended_approval_count": len(ready_rows),
        "recommended_ids": [row["id"] for row in ready_rows],
        "runway_status": runway.get("status") or "",
        "subscribers_per_week": runway.get("subscribers_per_week"),
        "required_subscribers_per_week_365": (runway.get("required_subscribers_per_week") or {}).get("365_days"),
        "all_review_preview_command": preview_command(((plan.get("approval_commands") or {}).get("all_review") or "")),
        "all_review_approval_command": (plan.get("approval_commands") or {}).get("all_review") or "",
    }
    payload = {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "promo_engine_status": str(PROMO_STATUS.relative_to(ROOT)),
            "promo_queue_plan": str(PROMO_PLAN.relative_to(ROOT)),
        },
        "summary": summary,
        "rows": rows,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(payload)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(payload, markdown)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), "review_count": len(rows), "recommended": len(ready_rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
