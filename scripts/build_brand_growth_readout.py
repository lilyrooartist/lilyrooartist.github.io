#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / "data" / "brand_growth_campaign.json"
QUEUE = ROOT / "data" / "scheduled_posts.csv"
FUTURE = ROOT / "admin" / "future-posts.json"
PUBLISHED_LOG = ROOT / "admin" / "content" / "Published_Log.csv"
EXECUTIONS = ROOT / "data" / "social_execution_snapshot.json"
X_RESULTS = ROOT / "data" / "x_post_results.json"
FACEBOOK_RESULTS = ROOT / "data" / "facebook_post_results.json"
LIVE_METRICS = ROOT / "data" / "live_social_metrics.json"
OUT = ROOT / "data" / "brand_growth_readout.json"
REPORT = ROOT / "admin" / "reports" / "brand-growth-readout.md"
REPORT_INDEX = ROOT / "admin" / "reports" / "index.html"
ADMIN_INDEX = ROOT / "admin" / "index.html"

TZ = ZoneInfo("America/New_York")
RESULT_FIELDS = ["views", "likes", "comments", "shares", "saves", "subs_delta"]
POST_PROOF_DELAY_MINUTES = 45
FIRST_MEASUREMENT_DELAY_HOURS = 24
CAMPAIGN_ID_PREFIX = "FP-BRAND-AM"


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


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


def parse_date(value: str | None):
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        return datetime.combine(datetime.fromisoformat(raw).date(), time(12, 0), TZ).astimezone(timezone.utc)
    except ValueError:
        return None


def iso_z(value: datetime | None) -> str:
    if not value:
        return ""
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def local_date(value: datetime | None) -> str:
    if not value:
        return "unscheduled"
    return value.astimezone(TZ).date().isoformat()


def queue_id(row: dict) -> str:
    content_id = str(row.get("content_id") or "").strip()
    if content_id.startswith("FP-"):
        return content_id
    notes = str(row.get("notes") or "")
    for part in notes.replace(";", " ").split():
        if part.startswith("queue_id="):
            return part.split("=", 1)[1].strip()
    return content_id


def by_id(rows: list[dict], key: str = "id") -> dict[str, dict]:
    return {
        str(row.get(key) or "").strip(): row
        for row in rows
        if str(row.get(key) or "").strip()
    }


def published_lookup() -> dict[str, dict]:
    rows = read_csv(PUBLISHED_LOG)
    lookup = {}
    for index, row in enumerate(rows, start=2):
        post_id = queue_id(row)
        if not post_id:
            continue
        enriched = dict(row)
        enriched["_source_row"] = index
        lookup[post_id] = enriched
    return lookup


def execution_lookup(snapshot: dict) -> dict[str, dict]:
    summary = snapshot.get("summary") or {}
    rows = []
    for key in ("current_executions", "posted", "latest_posted", "latest_attention", "approval_needed", "platform_fix_needed"):
        rows.extend(summary.get(key) or [])
    lookup = {}
    for row in rows:
        post_id = str(row.get("post_id") or "").strip()
        if post_id and post_id not in lookup:
            lookup[post_id] = row
    return lookup


def result_lookup(payload: dict) -> dict[str, dict]:
    return {
        str(row.get("post_id") or "").strip(): row
        for row in payload.get("rows") or []
        if str(row.get("post_id") or "").strip()
    }


def measured_fields(row: dict | None) -> list[str]:
    if not row:
        return []
    return [field for field in RESULT_FIELDS if str(row.get(field) or "").strip()]


def captured_fields(result_row: dict | None) -> list[str]:
    if not result_row:
        return []
    metrics = result_row.get("metrics") or {}
    return [field for field in RESULT_FIELDS if field in metrics]


def scheduled_status(scheduled_at: datetime | None, now: datetime) -> str:
    if not scheduled_at:
        return "unscheduled"
    return "scheduled_future" if scheduled_at > now else "scheduled_due"


def campaign_rows(campaign: dict, queue_rows: list[dict]) -> list[dict]:
    queue_campaign_rows = [
        row for row in queue_rows
        if str(row.get("id") or "").startswith(CAMPAIGN_ID_PREFIX)
    ]
    if queue_campaign_rows:
        return queue_campaign_rows
    return campaign.get("rows") or []


def capture_command(platform: str, post_ids: list[str]) -> str:
    if not post_ids:
        return ""
    script = "capture_x_post_results.py" if platform == "X" else "capture_facebook_post_results.py"
    ids = " ".join(f"--post-id {post_id}" for post_id in post_ids)
    return f"python3 scripts/{script} {ids}"


def post_slot_watch(rows: list[dict], now: datetime) -> tuple[list[dict], dict]:
    by_day: dict[str, list[dict]] = {}
    for row in rows:
        scheduled_at = parse_datetime(row.get("scheduled_at"))
        by_day.setdefault(local_date(scheduled_at), []).append(row)

    windows = []
    for day, day_rows in sorted(by_day.items()):
        parsed_times = [parse_datetime(row.get("scheduled_at")) for row in day_rows]
        parsed_times = [item for item in parsed_times if item]
        first_at = min(parsed_times) if parsed_times else None
        last_at = max(parsed_times) if parsed_times else None
        proof_due_at = last_at + timedelta(minutes=POST_PROOF_DELAY_MINUTES) if last_at else None
        measurement_due_at = last_at + timedelta(hours=FIRST_MEASUREMENT_DELAY_HOURS) if last_at else None
        status_counts = Counter(row.get("status") or "unknown" for row in day_rows)
        rows_needing_proof = [
            row["id"]
            for row in day_rows
            if row.get("status") in {"scheduled_due", "posted_needs_published_log_export", "execution_attention"}
        ]
        rows_waiting_publication = [
            row["id"]
            for row in day_rows
            if row.get("status") in {"scheduled_future", "scheduled_due"}
        ]
        rows_ready_for_metrics = [
            row["id"]
            for row in day_rows
            if row.get("status") == "ready_for_metric_capture"
        ]
        if status_counts.get("execution_attention"):
            status = "attention"
            next_action = "Inspect executor state, then refresh and export posted URLs after the issue is resolved."
        elif rows_ready_for_metrics:
            status = "measurement_due"
            next_action = "Capture metrics for logged campaign posts and import reviewed result fields."
        elif rows_needing_proof or (proof_due_at and now >= proof_due_at and rows_waiting_publication):
            status = "proof_due"
            next_action = "Capture executions and export posted Worker URLs into Published_Log.csv."
        elif first_at and now >= first_at:
            status = "publishing_window"
            next_action = "Scheduled posting window is open; capture executor state shortly after the final slot."
        elif status_counts.get("posted_waiting_measurement_window"):
            status = "posted_waiting_measurement"
            next_action = "Wait for the first measurement window before capturing result metrics."
        elif status_counts.get("measured") == len(day_rows):
            status = "measured"
            next_action = "Compare the result totals against the rest of the campaign."
        else:
            status = "scheduled_future"
            next_action = "Wait for the scheduled executor; proof capture starts after the final slot."
        windows.append({
            "date": day,
            "status": status,
            "post_ids": [row["id"] for row in day_rows],
            "platforms": sorted({row.get("platform") for row in day_rows if row.get("platform")}),
            "first_scheduled_at": iso_z(first_at),
            "last_scheduled_at": iso_z(last_at),
            "proof_due_at": iso_z(proof_due_at),
            "measurement_due_at": iso_z(measurement_due_at),
            "status_counts": dict(sorted(status_counts.items())),
            "rows_needing_proof": rows_needing_proof,
            "rows_ready_for_metrics": rows_ready_for_metrics,
            "capture_executions_command": "python3 scripts/capture_social_executions.py",
            "proof_preview_command": "python3 scripts/capture_social_executions.py && python3 scripts/export_social_executions.py --dry-run",
            "proof_apply_command": "python3 scripts/capture_social_executions.py && python3 scripts/export_social_executions.py --refresh-admin",
            "metric_capture_command": " && ".join(
                command
                for command in (
                    capture_command("X", [row["id"] for row in day_rows if row.get("platform") == "X" and row.get("status") == "ready_for_metric_capture"]),
                    capture_command("Facebook", [row["id"] for row in day_rows if row.get("platform") == "Facebook" and row.get("status") == "ready_for_metric_capture"]),
                )
                if command
            ),
            "next_action": next_action,
        })

    actionable = [
        window for window in windows
        if window["status"] in {"attention", "proof_due", "publishing_window", "measurement_due"}
    ]
    future = [window for window in windows if window["status"] == "scheduled_future"]
    next_window = actionable[0] if actionable else (future[0] if future else (windows[-1] if windows else {}))
    summary = {
        "window_count": len(windows),
        "status_counts": dict(sorted(Counter(window["status"] for window in windows).items())),
        "next_window_date": next_window.get("date", ""),
        "next_window_status": next_window.get("status", ""),
        "next_proof_due_at": next_window.get("proof_due_at", ""),
        "next_measurement_due_at": next_window.get("measurement_due_at", ""),
        "next_post_ids": next_window.get("post_ids", []),
        "proof_delay_minutes": POST_PROOF_DELAY_MINUTES,
        "first_measurement_delay_hours": FIRST_MEASUREMENT_DELAY_HOURS,
        "proof_preview_command": next_window.get("proof_preview_command", ""),
        "proof_apply_command": next_window.get("proof_apply_command", ""),
    }
    return windows, summary


def build_payload() -> dict:
    now = datetime.now(timezone.utc)
    campaign = read_json(CAMPAIGN, {})
    queue_rows = read_csv(QUEUE)
    future_posts = read_json(FUTURE, {}).get("posts") or []
    published = published_lookup()
    executions = execution_lookup(read_json(EXECUTIONS, {}))
    x_results = result_lookup(read_json(X_RESULTS, {}))
    facebook_results = result_lookup(read_json(FACEBOOK_RESULTS, {}))
    live_metrics = read_json(LIVE_METRICS, {})
    queue_by_id = by_id(queue_rows)
    future_by_id = by_id(future_posts)
    source_rows = campaign_rows(campaign, queue_rows)

    rows = []
    for source in source_rows:
        post_id = str(source.get("id") or "").strip()
        queue_row = queue_by_id.get(post_id) or source
        future_row = future_by_id.get(post_id) or {}
        published_row = published.get(post_id)
        execution = executions.get(post_id)
        platform = str(queue_row.get("platform") or source.get("platform") or "").strip()
        scheduled_at = parse_datetime(queue_row.get("scheduled_at") or source.get("scheduled_at"))
        measurement_due_at = None
        if execution and execution.get("updated_at"):
            measurement_due_at = parse_datetime(execution.get("updated_at"))
            if measurement_due_at:
                measurement_due_at += timedelta(hours=24)
        if not measurement_due_at and published_row:
            measurement_due_at = parse_date(published_row.get("date"))
            if measurement_due_at:
                measurement_due_at += timedelta(hours=24)
        result_row = x_results.get(post_id) if platform == "X" else facebook_results.get(post_id)
        imported_fields = measured_fields(published_row)
        api_fields = captured_fields(result_row)

        if imported_fields:
            status = "measured"
            next_action = "Review result totals and compare against the rest of the campaign."
        elif published_row and measurement_due_at and measurement_due_at <= now:
            status = "ready_for_metric_capture"
            next_action = capture_command(platform, [post_id])
        elif published_row:
            status = "posted_waiting_measurement_window"
            next_action = f"Wait until {measurement_due_at.isoformat() if measurement_due_at else 'the first measurement window'} before capturing metrics."
        elif execution and execution.get("status") == "posted":
            status = "posted_needs_published_log_export"
            next_action = "python3 scripts/export_social_executions.py --refresh-admin"
        elif execution and execution.get("status") in {"failed", "blocked", "skipped"}:
            status = "execution_attention"
            detail = execution.get("error_summary") or execution.get("reason") or "executor attention required"
            next_action = f"Inspect executor state for {post_id}: {detail}"
        else:
            status = scheduled_status(scheduled_at, now)
            next_action = "Wait for the scheduled social executor, then refresh admin and export executions." if status == "scheduled_future" else "Run scheduler dry-run or capture social executions to verify due post state."

        rows.append({
            "id": post_id,
            "platform": platform,
            "scheduled_at": queue_row.get("scheduled_at") or source.get("scheduled_at") or "",
            "approved": str(queue_row.get("approved") or "").strip(),
            "execution_mode": str(queue_row.get("execution_mode") or "").strip(),
            "post_type": str(queue_row.get("post_type") or "").strip(),
            "text": queue_row.get("text") or source.get("text") or "",
            "post_url": (published_row or {}).get("post_id_or_url") or (execution or {}).get("post_url") or "",
            "published_log_row": (published_row or {}).get("_source_row") or "",
            "execution_status": (execution or {}).get("status") or "",
            "execution_reason": (execution or {}).get("reason") or "",
            "measurement_due_at": measurement_due_at.isoformat() if measurement_due_at else "",
            "imported_result_fields": imported_fields,
            "captured_api_fields": api_fields,
            "status": status,
            "next_action": next_action,
            "visible_in_future_queue": bool(future_row),
        })

    status_counts = Counter(row["status"] for row in rows)
    platform_counts = Counter(row["platform"] for row in rows)
    ready_x_ids = [row["id"] for row in rows if row["platform"] == "X" and row["status"] == "ready_for_metric_capture"]
    ready_facebook_ids = [row["id"] for row in rows if row["platform"] == "Facebook" and row["status"] == "ready_for_metric_capture"]
    due_rows = [row for row in rows if row["status"] in {"scheduled_due", "execution_attention", "posted_needs_published_log_export", "ready_for_metric_capture"}]
    next_scheduled = sorted(
        [row for row in rows if row["status"] == "scheduled_future"],
        key=lambda row: row.get("scheduled_at") or "",
    )
    watch_windows, watch_summary = post_slot_watch(rows, now)
    live_platforms = (live_metrics.get("platforms") or {}) if isinstance(live_metrics, dict) else {}
    payload = {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "brand_growth_campaign": rel(CAMPAIGN),
            "scheduled_posts": rel(QUEUE),
            "future_posts": rel(FUTURE),
            "published_log": rel(PUBLISHED_LOG),
            "social_execution_snapshot": rel(EXECUTIONS),
            "x_post_results": rel(X_RESULTS),
            "facebook_post_results": rel(FACEBOOK_RESULTS),
            "live_social_metrics": rel(LIVE_METRICS),
        },
        "summary": {
            "campaign_row_count": len(rows),
            "platform_counts": dict(sorted(platform_counts.items())),
            "status_counts": dict(sorted(status_counts.items())),
            "approved_auto_rows": sum(1 for row in rows if row["approved"] == "yes" and row["execution_mode"] == "auto"),
            "future_queue_visible_rows": sum(1 for row in rows if row["visible_in_future_queue"]),
            "posted_or_measured_rows": sum(1 for row in rows if row["status"] in {"posted_waiting_measurement_window", "ready_for_metric_capture", "measured"}),
            "measured_rows": status_counts.get("measured", 0),
            "ready_for_metric_capture_rows": status_counts.get("ready_for_metric_capture", 0),
            "attention_rows": len(due_rows),
            "next_scheduled_post_id": (next_scheduled[0]["id"] if next_scheduled else ""),
            "next_scheduled_at": (next_scheduled[0]["scheduled_at"] if next_scheduled else ""),
            "x_metric_capture_command": capture_command("X", ready_x_ids),
            "facebook_metric_capture_command": capture_command("Facebook", ready_facebook_ids),
            "post_slot_watch_window_count": watch_summary.get("window_count", 0),
            "post_slot_watch_status_counts": watch_summary.get("status_counts", {}),
            "next_proof_window_date": watch_summary.get("next_window_date", ""),
            "next_proof_window_status": watch_summary.get("next_window_status", ""),
            "next_proof_due_at": watch_summary.get("next_proof_due_at", ""),
            "next_measurement_due_at": watch_summary.get("next_measurement_due_at", ""),
            "next_proof_post_ids": watch_summary.get("next_post_ids", []),
            "proof_preview_command": watch_summary.get("proof_preview_command", ""),
            "proof_apply_command": watch_summary.get("proof_apply_command", ""),
            "export_social_executions_command": "python3 scripts/export_social_executions.py --refresh-admin",
            "refresh_command": "python3 scripts/refresh_promo_admin.py",
            "report_path": rel(REPORT),
            "live_youtube_total_views": ((live_platforms.get("youtube") or {}).get("metrics") or {}).get("total_views"),
            "live_spotify_monthly_listeners": ((live_platforms.get("spotify") or {}).get("metrics") or {}).get("monthly_listeners"),
        },
        "post_slot_watch": {
            "summary": watch_summary,
            "windows": watch_windows,
        },
        "rows": rows,
        "next_actions": [
            row["next_action"] for row in due_rows[:6] if row.get("next_action")
        ] or [
            (
                f"Next proof window is {watch_summary.get('next_window_date')} after {watch_summary.get('next_proof_due_at')}; "
                f"watch {', '.join(watch_summary.get('next_post_ids') or [])}."
            ) if watch_summary.get("next_window_date") else (
                f"Next campaign post is {next_scheduled[0]['id']} at {next_scheduled[0]['scheduled_at']}." if next_scheduled else "No campaign rows remain."
            ),
        ],
        "guardrails": [
            "Readout only; it does not post or import metrics.",
            "Published_Log.csv is the source of truth for public URLs.",
            "Metric capture commands only target logged X/Facebook campaign post IDs.",
            "Post-slot proof commands only capture executor state and export confirmed Worker URLs.",
            "Unknown metrics remain blank until an API capture or visible analytics source proves them.",
        ],
    }
    return payload


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Brand Growth Readout - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Campaign rows: **{summary['campaign_row_count']}**",
        f"- Approved auto rows: **{summary['approved_auto_rows']}**",
        f"- Visible in future queue: **{summary['future_queue_visible_rows']}**",
        f"- Posted or measured rows: **{summary['posted_or_measured_rows']}**",
        f"- Measured rows: **{summary['measured_rows']}**",
        f"- Ready for metric capture: **{summary['ready_for_metric_capture_rows']}**",
        f"- Post-slot watch windows: **{summary.get('post_slot_watch_window_count', 0)}**",
        f"- Status counts: **{', '.join(f'{key}: {value}' for key, value in summary['status_counts'].items()) or 'none'}**",
        f"- Next scheduled: `{summary['next_scheduled_post_id'] or 'none'}` at `{summary['next_scheduled_at'] or 'n/a'}`",
        f"- Next proof due: `{summary.get('next_proof_due_at') or 'n/a'}`",
        f"- First measurement due: `{summary.get('next_measurement_due_at') or 'n/a'}`",
        f"- YouTube total views: **{summary.get('live_youtube_total_views', 'unknown')}**",
        f"- Spotify monthly listeners: **{summary.get('live_spotify_monthly_listeners', 'unknown')}**",
        "",
        "## Commands",
        f"- Refresh state: `{summary['refresh_command']}`",
        f"- Export posted URLs: `{summary['export_social_executions_command']}`",
        f"- Preview post-slot proof: `{summary.get('proof_preview_command') or 'waiting for scheduled campaign posts'}`",
        f"- Apply post-slot proof after scheduled executor runs: `{summary.get('proof_apply_command') or 'waiting for scheduled campaign posts'}`",
        f"- Capture X metrics: `{summary['x_metric_capture_command'] or 'waiting for logged X campaign posts'}`",
        f"- Capture Facebook metrics: `{summary['facebook_metric_capture_command'] or 'waiting for logged Facebook campaign posts'}`",
        "",
        "## Next Actions",
    ]
    for action in payload.get("next_actions") or []:
        lines.append(f"- {action}")
    lines.extend(["", "## Post-Slot Watch"])
    for window in (payload.get("post_slot_watch") or {}).get("windows") or []:
        lines.append(
            f"- `{window['date']}` **{window['status']}** proof due `{window.get('proof_due_at') or 'n/a'}` "
            f"for `{', '.join(window.get('post_ids') or [])}`"
        )
        if window.get("next_action"):
            lines.append(f"  - Next: {window['next_action']}")
        if window.get("proof_preview_command"):
            lines.append(f"  - Preview: `{window['proof_preview_command']}`")
        if window.get("metric_capture_command"):
            lines.append(f"  - Metrics: `{window['metric_capture_command']}`")
    lines.extend(["", "## Rows"])
    for row in payload["rows"]:
        lines.append(
            f"- `{row['id']}` {row['platform']} {row['scheduled_at']} - **{row['status']}**"
        )
        if row.get("post_url"):
            lines.append(f"  - URL: {row['post_url']}")
        if row.get("next_action"):
            lines.append(f"  - Next: {row['next_action']}")
        if row.get("imported_result_fields"):
            lines.append(f"  - Imported fields: `{', '.join(row['imported_result_fields'])}`")
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
        html = replace_json_embed(html, "embedded-brand-growth-readout", payload)
        html = replace_text_embed(html, "embedded-brand-growth-readout-report", markdown)
        ADMIN_INDEX.write_text(html, encoding="utf-8")
    if REPORT_INDEX.exists():
        html = REPORT_INDEX.read_text(encoding="utf-8")
        link = '<li><a href="/admin/reports/brand-growth-readout.md" target="_blank">Brand Growth Readout</a></li>'
        if link not in html:
            marker = '<li><a href="/admin/reports/brand-growth-campaign.md" target="_blank">Brand Growth Campaign</a></li>'
            html = html.replace(marker, marker + "\n        " + link, 1)
            REPORT_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    payload = build_payload()
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(payload)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(payload, markdown)
    print(json.dumps({"output": rel(OUT), **payload["summary"]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
