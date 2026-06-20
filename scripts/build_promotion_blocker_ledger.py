#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLATFORM_REPAIR = ROOT / "data" / "platform_repair_status.json"
SCHEDULED_APPROVAL = ROOT / "data" / "scheduled_approval_packet.json"
MANUAL_DISTRIBUTION = ROOT / "data" / "manual_distribution_packet.json"
MANUAL_METRICS = ROOT / "data" / "manual_metric_collection_packet.json"
BACKLOG_RESCHEDULE = ROOT / "data" / "backlog_reschedule_preview.json"
OUT = ROOT / "data" / "promotion_blocker_ledger.json"
REPORT = ROOT / "admin" / "reports" / "promotion-blocker-ledger.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"


OWNER_ORDER = {"codex": 0, "tod": 1, "external_platform": 2}
URGENCY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def row(
    blocker_id: str,
    title: str,
    category: str,
    owner: str,
    urgency: str,
    status: str,
    evidence: str,
    next_step: str,
    preview_command: str = "",
    apply_command: str = "",
    source_path: str = "",
    platform: str = "",
    release: str = "",
    external_url: str = "",
    guardrail: str = "",
) -> dict:
    return {
        "id": blocker_id,
        "blocker_id": blocker_id,
        "title": title,
        "category": category,
        "owner": owner,
        "urgency": urgency,
        "status": status,
        "platform": platform,
        "release": release,
        "evidence": evidence,
        "next_step": next_step,
        "preview_command": preview_command,
        "apply_command": apply_command,
        "source_path": source_path,
        "external_url": external_url,
        "guardrail": guardrail,
    }


def add_platform_repairs(rows: list[dict]) -> None:
    packet = read_json(PLATFORM_REPAIR, {})
    for item in packet.get("rows") or []:
        platform = item.get("platform") or "Platform"
        post_id = item.get("post_id") or platform
        reason = item.get("error_summary") or item.get("reason") or "Platform executor needs repair."
        missing = ", ".join(item.get("missing_secrets") or [])
        if missing:
            reason = f"{reason} Missing secrets: {missing}."
        local_missing = ", ".join(item.get("local_missing_secrets") or [])
        if local_missing:
            reason = f"{reason} Local secret source is missing: {local_missing}."
        owner = "external_platform" if platform in {"Facebook", "Instagram"} else "tod"
        next_step = item.get("repair_action") or "Complete the platform repair, then refresh admin."
        verification = item.get("retry_reset_verification_command") or ""
        if item.get("retry_reset_preview_command"):
            if verification:
                next_step = f"{next_step} Run `{verification}` before any retry reset; only reset if the worker reports executable."
            else:
                next_step = f"{next_step} After repair, preview retry reset before applying it."
        rows.append(row(
            blocker_id=f"platform-{post_id}",
            title=f"Repair {platform} executor",
            category="platform_repair",
            owner=owner,
            urgency="high",
            status="blocked",
            platform=platform,
            evidence=reason,
            next_step=next_step,
            preview_command=item.get("preview_command") or verification or item.get("retry_reset_preview_command") or "",
            apply_command=item.get("apply_command") or item.get("retry_reset_apply_command") or "",
            source_path=str(PLATFORM_REPAIR.relative_to(ROOT)),
            guardrail="Run retry resets only after the external platform repair is verified.",
        ))


def add_scheduled_approvals(rows: list[dict]) -> None:
    packet = read_json(SCHEDULED_APPROVAL, {})
    summary = packet.get("summary") or {}
    checked_preview = summary.get("checked_batch_preview_command") or ""
    checked_apply = summary.get("checked_batch_apply_command") or ""
    for item in packet.get("rows") or []:
        checks = item.get("review_checks") or []
        failed_checks = [check for check in checks if check.get("status") != "pass"]
        checks_passed = bool(item.get("review_check_passed"))
        evidence = f"{item.get('id')} is blocked by {item.get('reason') or 'not_approved'} in executor state."
        next_step = "Review copy, asset, destination links, and platform readiness before approving."
        status = "waiting_for_review"
        if checks_passed:
            status = "ready_for_reviewed_approval"
            evidence = f"{evidence} Automated review checks passed."
            if checked_preview and checked_apply:
                next_step = f"Use the checked batch after human review: preview `{checked_preview}`, then apply `{checked_apply}`."
        elif failed_checks:
            status = "blocked_by_review_checks"
            failed = "; ".join(f"{check.get('name')}: {check.get('detail')}" for check in failed_checks)
            evidence = f"{evidence} Failed review checks: {failed}"
            next_step = "Resolve failed review checks before approving this scheduled row."
        rows.append(row(
            blocker_id=f"approval-{item.get('id')}",
            title=f"Approve scheduled {item.get('platform') or 'post'} row",
            category="approval",
            owner="tod",
            urgency="high" if item.get("execution_mode") == "auto" else "medium",
            status=status,
            platform=item.get("platform") or "",
            release=item.get("song") or "",
            evidence=evidence,
            next_step=next_step,
            preview_command=item.get("approval_preview_command") or "",
            apply_command=item.get("approval_apply_command") or "",
            source_path=str(SCHEDULED_APPROVAL.relative_to(ROOT)),
            external_url=item.get("asset_url") or "",
            guardrail="Approval does not guarantee posting if the platform executor is still blocked.",
        ))


def add_manual_distribution(rows: list[dict]) -> None:
    packet = read_json(MANUAL_DISTRIBUTION, {})
    for item in packet.get("rows") or []:
        if item.get("logged"):
            continue
        approved = item.get("approved") == "yes"
        preview_command = item.get("log_preview_command") if approved else item.get("approval_preview_command")
        apply_command = item.get("log_apply_command") if approved else item.get("approval_command")
        next_step = "Post manually, then log the public URL so admin status can stop treating the row as pending."
        if not approved:
            next_step = "Review and approve the copy first, then post manually and log the public URL."
        log_command = item.get("log_apply_command") or ""
        guardrail = "Manual posting happens outside this repo; only log the URL after the post is live."
        if log_command and not approved:
            guardrail = f"{guardrail} URL logging command after posting: {log_command}"
        rows.append(row(
            blocker_id=f"manual-{item.get('id')}",
            title=f"Manually post {item.get('platform') or 'distribution'} copy",
            category="manual_distribution",
            owner="tod",
            urgency="medium",
            status="ready_for_manual_post" if approved else "waiting_for_review",
            platform=item.get("platform") or "",
            release=item.get("release") or "",
            evidence=f"{item.get('id')} is packaged for manual distribution.",
            next_step=next_step,
            preview_command=preview_command or "",
            apply_command=apply_command or "",
            source_path=str(MANUAL_DISTRIBUTION.relative_to(ROOT)),
            external_url=item.get("asset_download_url") or item.get("asset_url") or "",
            guardrail=guardrail,
        ))


def add_manual_metrics(rows: list[dict]) -> None:
    packet = read_json(MANUAL_METRICS, {})
    for item in packet.get("platforms") or []:
        fields = [field.get("field") for field in item.get("fields") or [] if field.get("field")]
        rows.append(row(
            blocker_id=f"metrics-{item.get('platform')}",
            title=f"Fill {item.get('platform')} manual metrics",
            category="manual_metrics",
            owner="tod",
            urgency="low",
            status="waiting_for_manual_values",
            platform=item.get("platform") or "",
            evidence=f"{len(fields)} pending field(s): {', '.join(fields)}.",
            next_step="Open the metric source, fill the CSV worksheet, preview import, then refresh admin.",
            preview_command=item.get("worksheet_import_preview_command") or "",
            apply_command=item.get("worksheet_import_command") or "",
            source_path=str(MANUAL_METRICS.relative_to(ROOT)),
            external_url=item.get("collection_url") or "",
            guardrail="Do not guess analytics values; import only values copied from the platform source.",
        ))


def add_backlog(rows: list[dict]) -> None:
    packet = read_json(BACKLOG_RESCHEDULE, {})
    summary = packet.get("summary") or {}
    blocked = int(summary.get("blocked_backlog_count") or 0)
    approved = int(summary.get("approved_backlog_count") or 0)
    if not approved:
        return
    status = "blocked" if blocked else "ready_to_preview"
    rows.append(row(
        blocker_id="backlog-reschedule",
        title="Reschedule approved past-due backlog",
        category="backlog_reschedule",
        owner="codex" if not blocked else "external_platform",
        urgency="high",
        status=status,
        evidence=f"{approved} approved backlog row(s); {blocked} still have executor blockers.",
        next_step="Preview a new schedule. Apply only after known executor blockers clear.",
        preview_command=summary.get("preview_command") or "",
        apply_command=summary.get("apply_command") or "",
        source_path=str(BACKLOG_RESCHEDULE.relative_to(ROOT)),
        guardrail="The apply command refuses known blocked rows unless deliberately overridden.",
    ))


def grouped_counts(rows: list[dict], key: str) -> dict:
    counts = {}
    for item in rows:
        value = item.get(key) or "unknown"
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Promotion Blocker Ledger - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Open blockers: **{summary['open_blocker_count']}**",
        f"- User-owned: **{summary['owner_counts'].get('tod', 0)}**",
        f"- External platform-owned: **{summary['owner_counts'].get('external_platform', 0)}**",
        f"- Codex-actionable: **{summary['owner_counts'].get('codex', 0)}**",
        f"- High or critical: **{summary['urgent_count']}**",
        "",
        "## Ledger",
    ]
    for item in payload["rows"]:
        lines.append(f"- **[{item['urgency']}] {item['title']}** (`{item['id']}`)")
        lines.append(f"  - Owner: `{item['owner']}`; status: `{item['status']}`; category: `{item['category']}`")
        if item.get("evidence"):
            lines.append(f"  - Evidence: {item['evidence']}")
        if item.get("next_step"):
            lines.append(f"  - Next step: {item['next_step']}")
        if item.get("external_url"):
            lines.append(f"  - Open: {item['external_url']}")
        if item.get("preview_command"):
            lines.append(f"  - Preview/check: `{item['preview_command']}`")
        if item.get("apply_command"):
            lines.append(f"  - Apply/log after review: `{item['apply_command']}`")
        if item.get("guardrail"):
            lines.append(f"  - Guardrail: {item['guardrail']}")
    lines.extend([
        "",
        "## Guardrails",
        "- This ledger does not approve posts, post externally, push secrets, or invent metric values.",
        "- Treat external platform repairs and manual values as blockers until fresh admin evidence proves they cleared.",
        "",
    ])
    return "\n".join(lines)


def replace_json_embed(html: str, block_id: str, payload) -> str:
    marker = f'<script type="application/json" id="{block_id}">'
    end_marker = "</script>"
    encoded = json.dumps(payload, indent=2, ensure_ascii=False)
    start = html.find(marker)
    if start == -1:
        insert = f"\n{marker}{encoded}{end_marker}\n"
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
        insert = f"\n{marker}{content.rstrip()}{end_marker}\n"
        return html.replace("<script>", insert + "\n<script>", 1)
    start_content = start + len(marker)
    end = html.find(end_marker, start_content)
    if end == -1:
        raise RuntimeError(f"Could not find end marker for {block_id}")
    return html[:start_content] + content.rstrip() + html[end:]


def sync_admin(payload: dict, markdown: str) -> None:
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    html = replace_json_embed(html, "embedded-promotion-blocker-ledger", payload)
    html = replace_text_embed(html, "embedded-promotion-blocker-ledger-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def build_ledger() -> dict:
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    rows: list[dict] = []
    add_backlog(rows)
    add_platform_repairs(rows)
    add_scheduled_approvals(rows)
    add_manual_distribution(rows)
    add_manual_metrics(rows)
    rows.sort(key=lambda item: (
        URGENCY_ORDER.get(item.get("urgency"), 9),
        OWNER_ORDER.get(item.get("owner"), 9),
        item.get("category") or "",
        item.get("title") or "",
    ))
    summary = {
        "open_blocker_count": len(rows),
        "urgent_count": sum(1 for item in rows if item.get("urgency") in {"critical", "high"}),
        "owner_counts": grouped_counts(rows, "owner"),
        "category_counts": grouped_counts(rows, "category"),
        "status_counts": grouped_counts(rows, "status"),
        "sources": [
            str(BACKLOG_RESCHEDULE.relative_to(ROOT)),
            str(PLATFORM_REPAIR.relative_to(ROOT)),
            str(SCHEDULED_APPROVAL.relative_to(ROOT)),
            str(MANUAL_DISTRIBUTION.relative_to(ROOT)),
            str(MANUAL_METRICS.relative_to(ROOT)),
        ],
    }
    return {
        "generated_at": now,
        "safe_mode": True,
        "summary": summary,
        "rows": rows,
    }


def main() -> int:
    ledger = build_ledger()
    OUT.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(ledger)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(ledger, markdown)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), "open_blockers": ledger["summary"]["open_blocker_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
