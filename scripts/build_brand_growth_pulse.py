#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
READOUT = ROOT / "data" / "brand_growth_readout.json"
PREFLIGHT = ROOT / "data" / "brand_growth_preflight.json"
POSTING_STATUS = ROOT / "data" / "posting_automation_status.json"
CLICKS = ROOT / "data" / "brand_campaign_clicks.json"
X_RESULTS = ROOT / "data" / "x_post_results.json"
FACEBOOK_RESULTS = ROOT / "data" / "facebook_post_results.json"
OUT = ROOT / "data" / "brand_growth_pulse.json"
REPORT = ROOT / "admin" / "reports" / "brand-growth-pulse.md"
REPORT_INDEX = ROOT / "admin" / "reports" / "index.html"
ADMIN_INDEX = ROOT / "admin" / "index.html"


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def parse_datetime(value: str | None):
    raw = str(value or "").strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def iso_z(value: datetime | None) -> str:
    if not value:
        return ""
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def hours_until(value: str | None, now: datetime) -> float | None:
    parsed = parse_datetime(value)
    if not parsed:
        return None
    return round((parsed - now).total_seconds() / 3600, 2)


def missing_metric_names(x_results: dict, facebook_results: dict) -> list[str]:
    names = []
    for payload in (x_results, facebook_results):
        summary = payload.get("summary") or {}
        names.extend(summary.get("missing_secret_names") or [])
    return sorted(set(str(name) for name in names if name))


def listify_counts(items) -> dict:
    if isinstance(items, dict):
        return items
    if not isinstance(items, list):
        return {}
    result = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        key = item.get("key") or item.get("label") or item.get("name") or item.get("value")
        value = item.get("value") if "value" in item else item.get("count")
        if key is not None:
            result[str(key)] = int(value or 0)
    return result


def title_from_campaign_id(value: str | None) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "Analog Myth post"
    slug = raw
    for prefix in ("FP-BRAND-AM-", "FP-LAUNCH-ANALOG-MYTH-", "PODCAST-ANALOG-MYTH-"):
        if slug.upper().startswith(prefix):
            slug = slug[len(prefix):]
            break
    for suffix in ("-FACEBOOK", "-X"):
        if slug.upper().endswith(suffix):
            slug = slug[: -len(suffix)]
            break
    parts = [
        part
        for part in slug.lower().split("-")
        if part and not (part.startswith("w") and part[1:].isdigit())
    ]
    if parts and parts[0].isdigit() and len(parts) > 1:
        parts = parts[1:]
    title = " ".join(part.capitalize() for part in parts)
    return title or "Analog Myth post"


def row_timestamp(row: dict, key: str) -> datetime:
    return parse_datetime(row.get(key)) or datetime.max.replace(tzinfo=timezone.utc)


def learning_row(row: dict, learning_use: str) -> dict:
    return {
        "post_id": row.get("id") or row.get("content_id") or "",
        "platform": row.get("platform") or "",
        "title": title_from_campaign_id(row.get("id") or row.get("content_id")),
        "status": row.get("status") or "",
        "scheduled_at": row.get("scheduled_at") or "",
        "measurement_due_at": row.get("measurement_due_at") or "",
        "post_url": row.get("post_url") or row.get("post_id_or_url") or "",
        "public_visibility_ok": row.get("public_visibility_ok"),
        "learning_use": learning_use,
    }


def build_learning_plan(
    readout: dict,
    readout_summary: dict,
    click_summary: dict,
    missing_metrics: list[str],
    now: datetime,
) -> dict:
    rows = [row for row in (readout.get("rows") or []) if isinstance(row, dict)]
    ready_rows = sorted(
        [row for row in rows if row.get("status") == "ready_for_metric_capture"],
        key=lambda row: row_timestamp(row, "measurement_due_at"),
    )
    waiting_rows = sorted(
        [row for row in rows if row.get("status") == "posted_waiting_measurement_window"],
        key=lambda row: row_timestamp(row, "measurement_due_at"),
    )
    future_rows = sorted(
        [row for row in rows if row.get("status") == "scheduled_future"],
        key=lambda row: row_timestamp(row, "scheduled_at"),
    )
    click_count = int(click_summary.get("click_count") or 0)
    ready_count = len(ready_rows)
    waiting_count = len(waiting_rows)

    if ready_count and missing_metrics:
        status = "learning_waiting_for_connected_metrics"
        headline = "Post-window learning loop is queued"
        label = "Learning queued"
        note = "Public proof and first-party click tracking are ready; private X/Facebook result counts can join after analytics credentials are connected."
    elif ready_count:
        status = "ready_to_compare_posts"
        headline = "Post-window learning is ready"
        label = "Ready"
        note = "Public URLs are saved and the connected metrics commands can compare the newest posts."
    elif click_count:
        status = "learn_from_clicks"
        headline = "Click response is ready to review"
        label = "Review clicks"
        note = "First-party clicks are available, so the next creative pass can favor the destinations and tracks with response."
    elif waiting_count:
        status = "waiting_for_measurement_window"
        headline = "Newest posts are waiting for first result checks"
        label = "Waiting"
        note = "Recent posts are public. The first useful result window opens after the platform has had time to accumulate response."
    else:
        status = "watch_next_post_window"
        headline = "Watch the next automatic post window"
        label = "Watching"
        note = "The next learning signal starts when the upcoming queued posts publish and their public URLs are captured."

    next_due = ""
    if not ready_count:
        for row in waiting_rows:
            if row.get("measurement_due_at"):
                next_due = row.get("measurement_due_at")
                break
    if not next_due and not ready_count:
        next_due = readout_summary.get("next_measurement_due_at") or ""

    selected = []
    seen = set()
    for row, use in (
        *[(row, "Ready for post-window comparison") for row in ready_rows[:4]],
        *[(row, "Waiting for first useful result check") for row in waiting_rows[:2]],
        *[(row, "Next queued learning input") for row in future_rows[:2]],
    ):
        key = row.get("id") or row.get("content_id")
        if not key or key in seen:
            continue
        seen.add(key)
        selected.append(learning_row(row, use))

    return {
        "status": status,
        "label": label,
        "headline": headline,
        "next_learning_question": "Which Analog Myth posts are turning attention into album, Echo Thread, or video clicks?",
        "measurement_due_count": ready_count,
        "waiting_measurement_count": waiting_count,
        "scheduled_future_count": int(readout_summary.get("future_queue_visible_rows") or len(future_rows)),
        "next_learning_due_at": next_due,
        "next_metric_post_ids": readout_summary.get("next_metric_post_ids") or [row.get("id") for row in ready_rows[:2]],
        "next_proof_post_ids": readout_summary.get("next_proof_post_ids") or [row.get("id") for row in future_rows[:2]],
        "click_refresh_command": readout_summary.get("campaign_click_refresh_command") or "python3 scripts/capture_brand_campaign_clicks.py",
        "pulse_refresh_command": "python3 scripts/build_brand_growth_pulse.py",
        "proof_command": readout_summary.get("proof_apply_command") or "",
        "metric_capture_commands": [
            command
            for command in (
                readout_summary.get("x_metric_capture_command"),
                readout_summary.get("facebook_metric_capture_command"),
            )
            if command
        ],
        "automation_note": "No manual posting is required; this loop uses automatic posts, public URL proof, first-party click checks, and optional connected X/Facebook metrics.",
        "credential_note": "X/Facebook result counts need connected analytics credentials, but the campaign can keep posting and learning from first-party clicks without them." if missing_metrics else "",
        "rows": selected,
        "hours_until_next_learning_due": hours_until(next_due, now),
    }


def pick_primary_action(
    readout_summary: dict,
    preflight_summary: dict,
    posting_summary: dict,
    click_summary: dict,
    missing_metrics: list[str],
    now: datetime,
) -> dict:
    active_campaign_ready = (
        preflight_summary.get("status") == "ready"
        and int(preflight_summary.get("scheduler_blocked_count") or 0) == 0
    )
    proof_due_at = (
        readout_summary.get("next_proof_due_at")
        or posting_summary.get("active_campaign_next_proof_due_at")
        or preflight_summary.get("next_proof_due_at")
        or preflight_summary.get("scheduled_time")
    )
    proof_hours = hours_until(proof_due_at, now)
    ready_metrics = int(readout_summary.get("ready_for_metric_capture_rows") or 0)
    click_count = int(click_summary.get("click_count") or 0)

    if preflight_summary.get("status") != "ready" or int(preflight_summary.get("scheduler_blocked_count") or 0):
        return {
            "state": "posting_needs_check",
            "label": "Refresh the next posting window",
            "why": "The next Analog Myth scheduler check is not clean.",
            "command": "python3 scripts/build_brand_growth_preflight.py",
            "due_at": "",
        }
    if proof_hours is not None and proof_hours <= 0:
        return {
            "state": "proof_due",
            "label": "Capture the posts that should have run",
            "why": "The next proof window is due. Export confirmed public URLs into the activity log.",
            "command": "python3 scripts/capture_social_executions.py && python3 scripts/export_social_executions.py --refresh-admin",
            "due_at": proof_due_at,
        }
    if active_campaign_ready and proof_hours is not None and proof_hours > 0:
        return {
            "state": "campaign_running",
            "label": "Let the next automated posts run",
            "why": "The active X/Facebook Analog Myth campaign is queued and ready; proof capture starts after the next window.",
            "command": "python3 scripts/refresh_promo_admin.py",
            "due_at": proof_due_at,
        }
    if ready_metrics and not missing_metrics:
        return {
            "state": "measure_posts",
            "label": "Capture result counts for fresh posts",
            "why": f"{ready_metrics} Analog Myth post(s) have public URLs and are ready for automated X/Facebook result capture.",
            "command": " && ".join(
                command for command in (
                    readout_summary.get("x_metric_capture_command"),
                    readout_summary.get("facebook_metric_capture_command"),
                )
                if command
            ) or "python3 scripts/build_brand_growth_readout.py",
            "due_at": "",
        }
    if ready_metrics and missing_metrics:
        return {
            "state": "measurement_waiting_for_credentials",
            "label": "Keep posting; connect result metrics when approved",
            "why": f"{ready_metrics} recent {'post is' if ready_metrics == 1 else 'posts are'} ready to measure, but X/Meta result metrics are not connected.",
            "command": "python3 scripts/capture_brand_campaign_clicks.py && python3 scripts/build_brand_growth_pulse.py",
            "due_at": proof_due_at or "",
        }
    if click_count:
        return {
            "state": "learn_from_clicks",
            "label": "Review first-party click response",
            "why": "Campaign links are recording click evidence, so the next content pass can favor the strongest tracks and destinations.",
            "command": "python3 scripts/capture_brand_campaign_clicks.py && python3 scripts/build_brand_growth_pulse.py",
            "due_at": "",
        }
    return {
        "state": "campaign_running",
        "label": "Let the next automated posts run",
        "why": "The active X/Facebook Analog Myth campaign is queued and ready; proof capture starts after the next window.",
        "command": "python3 scripts/refresh_promo_admin.py",
        "due_at": proof_due_at or "",
    }


def build_payload() -> dict:
    now = datetime.now(timezone.utc)
    readout = read_json(READOUT, {})
    preflight = read_json(PREFLIGHT, {})
    posting = read_json(POSTING_STATUS, {})
    clicks = read_json(CLICKS, {})
    x_results = read_json(X_RESULTS, {})
    facebook_results = read_json(FACEBOOK_RESULTS, {})

    readout_summary = readout.get("summary") or {}
    preflight_summary = preflight.get("summary") or {}
    posting_summary = posting.get("summary") or {}
    click_summary = clicks.get("summary") or {}
    missing_metrics = missing_metric_names(x_results, facebook_results)
    optional_inputs = []
    primary_action = pick_primary_action(
        readout_summary,
        preflight_summary,
        posting_summary,
        click_summary,
        missing_metrics,
        now,
    )
    learning_plan = build_learning_plan(readout, readout_summary, click_summary, missing_metrics, now)

    next_post_at = readout_summary.get("next_scheduled_at") or preflight_summary.get("scheduled_time") or ""
    proof_due_at = primary_action.get("due_at") or readout_summary.get("next_proof_due_at") or posting_summary.get("active_campaign_next_proof_due_at") or ""
    status = primary_action["state"]
    blockers = []
    if missing_metrics:
        optional_inputs.append({
            "kind": "credential",
            "label": "X/Meta result metrics",
            "detail": "Automatic result counts can import views, likes, comments, shares, or saves after credential setup. Posting does not depend on this.",
            "missing_names": missing_metrics,
            "help_needed": "Confirm before pushing or entering social API secrets anywhere outside the local machine.",
        })
    if int(preflight_summary.get("scheduler_blocked_count") or 0):
        blockers.append({
            "kind": "scheduler",
            "label": "Next scheduler window",
            "detail": "The next scheduler dry-run has blocked rows.",
            "missing_names": [],
            "help_needed": "",
        })

    recommendations = [
        {
            "label": primary_action["label"],
            "detail": primary_action["why"],
            "command": primary_action["command"],
        },
        {
            "label": learning_plan["headline"],
            "detail": f"{learning_plan['next_learning_question']} {learning_plan['automation_note']}",
            "command": f"{learning_plan['click_refresh_command']} && {learning_plan['pulse_refresh_command']}",
        },
        {
            "label": "Preserve the no-manual-posting lane",
            "detail": "Keep Analog Myth promotion on API-backed X/Facebook rows until another platform has a real automated path.",
            "command": "python3 scripts/build_posting_automation_status.py",
        },
    ]
    if missing_metrics:
        recommendations.append({
            "label": "Optional: connect X/Meta result capture",
            "detail": "This is the only current measurement setup needing help; do it only after explicit approval for secret handling.",
            "command": "python3 scripts/push_github_actions_secrets.py --name FB_PAGE_ID --name META_LONG_LIVED_TOKEN --name X_ACCESS_TOKEN --name X_ACCESS_TOKEN_SECRET --name X_API_KEY --name X_API_SECRET",
        })

    return {
        "generated_at": iso_z(now),
        "safe_mode": True,
        "status": status,
        "source": {
            "brand_growth_readout": rel(READOUT),
            "brand_growth_preflight": rel(PREFLIGHT),
            "posting_automation_status": rel(POSTING_STATUS),
            "brand_campaign_clicks": rel(CLICKS),
            "x_post_results": rel(X_RESULTS),
            "facebook_post_results": rel(FACEBOOK_RESULTS),
        },
        "summary": {
            "status": status,
            "primary_action": primary_action,
            "active_campaign_ready": bool(posting_summary.get("active_campaign_ready")),
            "posting_preflight_ready": preflight_summary.get("status") == "ready",
            "queued_future_posts": int(readout_summary.get("future_queue_visible_rows") or 0),
            "posted_or_measured_rows": int(readout_summary.get("posted_or_measured_rows") or 0),
            "ready_for_metric_capture_rows": int(readout_summary.get("ready_for_metric_capture_rows") or 0),
            "click_count": int(click_summary.get("click_count") or 0),
            "click_post_count": int(click_summary.get("post_count") or 0),
            "clicks_by_platform": listify_counts(click_summary.get("by_platform")),
            "clicks_by_destination": listify_counts(click_summary.get("by_destination")),
            "next_post_at": next_post_at,
            "proof_due_at": proof_due_at,
            "hours_until_next_post": hours_until(next_post_at, now),
            "hours_until_proof_due": hours_until(proof_due_at, now),
            "missing_metric_credentials": missing_metrics,
            "learning_status": learning_plan["status"],
            "learning_headline": learning_plan["headline"],
            "next_learning_question": learning_plan["next_learning_question"],
            "measurement_due_rows": learning_plan["measurement_due_count"],
            "waiting_measurement_rows": learning_plan["waiting_measurement_count"],
            "next_learning_due_at": learning_plan["next_learning_due_at"],
            "manual_posting_required": False,
            "report_path": rel(REPORT),
            "refresh_command": "python3 scripts/build_brand_growth_pulse.py",
        },
        "learning_plan": learning_plan,
        "recommendations": recommendations,
        "blockers": blockers,
        "optional_inputs": optional_inputs,
        "guardrails": [
            "No manual posting is introduced by this pulse.",
            "Do not solicit subscribers or use audience-target copy in public Lily Roo posts.",
            "Do not transmit social API secrets without explicit approval for the destination.",
            "Click telemetry is first-party, aggregate, and does not store IP addresses.",
        ],
    }


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    primary = summary["primary_action"]
    learning = payload.get("learning_plan") or {}
    lines = [
        "# Brand Growth Pulse - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Current Pulse",
        f"- Status: **{summary['status']}**",
        f"- Primary action: **{primary['label']}**",
        f"- Why: {primary['why']}",
        f"- Command: `{primary['command'] or 'n/a'}`",
        f"- Active campaign ready: **{summary['active_campaign_ready']}**",
        f"- Posting preflight ready: **{summary['posting_preflight_ready']}**",
        f"- Future queued posts: **{summary['queued_future_posts']}**",
        f"- Posted or measured rows: **{summary['posted_or_measured_rows']}**",
        f"- Ready for result capture: **{summary['ready_for_metric_capture_rows']}**",
        f"- First-party clicks: **{summary['click_count']}** across **{summary['click_post_count']}** post(s)",
        f"- Next post at: `{summary['next_post_at'] or 'n/a'}`",
        f"- Proof due at: `{summary['proof_due_at'] or 'n/a'}`",
        f"- Hours until next post: `{summary['hours_until_next_post']}`",
        f"- Hours until proof due: `{summary['hours_until_proof_due']}`",
        "",
        "## Post-Window Learning",
        f"- Status: **{learning.get('status', 'unknown')}**",
        f"- Headline: **{learning.get('headline', 'Post-window learning')}**",
        f"- Question: {learning.get('next_learning_question', 'n/a')}",
        f"- Measurement due rows: **{learning.get('measurement_due_count', 0)}**",
        f"- Waiting measurement rows: **{learning.get('waiting_measurement_count', 0)}**",
        f"- Future scheduled rows: **{learning.get('scheduled_future_count', 0)}**",
        f"- Next learning due at: `{learning.get('next_learning_due_at') or 'n/a'}`",
        f"- Click refresh: `{learning.get('click_refresh_command') or 'n/a'}`",
        f"- Pulse refresh: `{learning.get('pulse_refresh_command') or 'n/a'}`",
        f"- Automation note: {learning.get('automation_note', 'n/a')}",
    ]
    if learning.get("credential_note"):
        lines.append(f"- Credential note: {learning['credential_note']}")
    learning_rows = learning.get("rows") or []
    if learning_rows:
        lines.append("- Rows:")
        for row in learning_rows:
            lines.append(
                f"  - `{row.get('post_id')}` ({row.get('platform') or 'platform'}): "
                f"{row.get('title') or 'Analog Myth post'} - {row.get('learning_use') or row.get('status') or 'tracked'}"
            )
    lines.extend([
        "",
        "## Recommendations",
    ])
    for item in payload.get("recommendations") or []:
        lines.append(f"- **{item['label']}**: {item['detail']}")
        if item.get("command"):
            lines.append(f"  - Command: `{item['command']}`")
    lines.extend(["", "## Blockers"])
    blockers = payload.get("blockers") or []
    if blockers:
        for item in blockers:
            lines.append(f"- **{item['label']}**: {item['detail']}")
            if item.get("missing_names"):
                lines.append(f"  - Missing names: `{', '.join(item['missing_names'])}`")
            if item.get("help_needed"):
                lines.append(f"  - Help needed: {item['help_needed']}")
    else:
        lines.append("- No active posting blockers.")
    lines.extend(["", "## Guardrails"])
    for item in payload.get("guardrails") or []:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def replace_json_embed(html: str, block_id: str, payload) -> str:
    marker = f'<script type="application/json" id="{block_id}">'
    end_marker = "</script>"
    encoded = json.dumps(payload, indent=2, ensure_ascii=False)
    start = html.find(marker)
    if start == -1:
        return html.replace("<script>", f"\n{marker}{encoded}{end_marker}\n\n<script>", 1)
    content_start = start + len(marker)
    content_end = html.find(end_marker, content_start)
    if content_end == -1:
        raise RuntimeError(f"Could not find end marker for {block_id}")
    return html[:content_start] + encoded + html[content_end:]


def replace_text_embed(html: str, block_id: str, content: str) -> str:
    marker = f'<script type="text/plain" id="{block_id}">'
    end_marker = "</script>"
    start = html.find(marker)
    if start == -1:
        return html.replace("<script>", f"\n{marker}{content.rstrip()}{end_marker}\n\n<script>", 1)
    content_start = start + len(marker)
    content_end = html.find(end_marker, content_start)
    if content_end == -1:
        raise RuntimeError(f"Could not find end marker for {block_id}")
    return html[:content_start] + content.rstrip() + html[content_end:]


def sync_admin(payload: dict, markdown: str) -> None:
    if ADMIN_INDEX.exists():
        html = ADMIN_INDEX.read_text(encoding="utf-8")
        html = replace_json_embed(html, "embedded-brand-growth-pulse", payload)
        html = replace_text_embed(html, "embedded-brand-growth-pulse-report", markdown)
        if "'reports/brand-growth-pulse.md'" not in html:
            html = html.replace(
                "'reports/brand-growth-readout.md':'embedded-brand-growth-readout-report',",
                "'reports/brand-growth-readout.md':'embedded-brand-growth-readout-report',\n    'reports/brand-growth-pulse.md':'embedded-brand-growth-pulse-report',",
                1,
            )
        if "'data/brand_growth_pulse.json'" not in html:
            html = html.replace(
                "'data/brand_growth_readout.json':'embedded-brand-growth-readout',",
                "'data/brand_growth_readout.json':'embedded-brand-growth-readout',\n    'data/brand_growth_pulse.json':'embedded-brand-growth-pulse',",
                1,
            )
        pulse_report_link = '<a class="source-link" href="reports/brand-growth-pulse.md" target="_blank" rel="noopener">Brand growth pulse</a>'
        if pulse_report_link not in html:
            html = html.replace(
                '<a class="source-link" href="reports/weekly-social-report.md" target="_blank" rel="noopener">Weekly report</a>',
                '<a class="source-link" href="reports/weekly-social-report.md" target="_blank" rel="noopener">Weekly report</a>\n                ' + pulse_report_link,
                1,
            )
        pulse_data_link = '<a class="source-link" href="../data/brand_growth_pulse.json" target="_blank" rel="noopener">Brand growth pulse JSON</a>'
        if pulse_data_link not in html:
            html = html.replace(
                '<a class="source-link" href="../data/promo_engine_status.json" target="_blank" rel="noopener">Promo health</a>',
                '<a class="source-link" href="../data/promo_engine_status.json" target="_blank" rel="noopener">Promo health</a>\n                ' + pulse_data_link,
                1,
            )
        ADMIN_INDEX.write_text(html, encoding="utf-8")
    if REPORT_INDEX.exists():
        html = REPORT_INDEX.read_text(encoding="utf-8")
        link = '<li><a href="/admin/reports/brand-growth-pulse.md" target="_blank">Brand Growth Pulse</a></li>'
        if link not in html:
            marker = '<li><a href="/admin/reports/brand-growth-readout.md" target="_blank">Brand Growth Readout</a></li>'
            html = html.replace(marker, marker + "\n        " + link, 1)
            REPORT_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    payload = build_payload()
    markdown = build_markdown(payload)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(payload, markdown)
    print(json.dumps({"output": rel(OUT), **payload["summary"]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
