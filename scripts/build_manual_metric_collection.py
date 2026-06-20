#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMO_STATUS = ROOT / "data" / "promo_engine_status.json"
MANUAL_STATS = ROOT / "data" / "manual_social_stats.json"
LIVE_METRICS = ROOT / "data" / "live_social_metrics.json"
OUT_CSV = ROOT / "data" / "manual_metric_collection_template.csv"
OUT_ENTRY_CSV = ROOT / "data" / "manual_metric_entry_template.csv"
OUT_JSON = ROOT / "data" / "manual_metric_collection_packet.json"
OUT_MD = ROOT / "admin" / "reports" / "manual-metric-collection.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"


SOURCE_HINTS = {
    "facebook": "Meta Business Suite > Insights",
    "instagram": "Instagram Professional Dashboard > Insights",
    "spotify": "Spotify for Artists > Music/Stats export",
    "tiktok": "TikTok Studio or Creator Center analytics",
    "x": "X Analytics or account profile metrics",
}


DEFAULT_COLLECTION_URLS = {
    "facebook": "https://business.facebook.com/latest/insights",
    "instagram": "https://www.instagram.com/professional_dashboard/",
    "spotify": "https://artists.spotify.com/",
    "tiktok": "https://www.tiktok.com/creator-center/analytics",
    "x": "https://analytics.x.com/",
}

PUBLIC_PROFILE_COLLECTION_URLS = {
    ("instagram", "followers"): "https://www.instagram.com/lilyroo.artist/",
    ("x", "followers"): "https://x.com/lilyrooartist",
}

LIVE_IMPORT_PREVIEW_COMMAND = "python3 scripts/update_manual_social_stats.py --from-live --dry-run"
LIVE_IMPORT_COMMAND = "python3 scripts/update_manual_social_stats.py --from-live --refresh-admin"
WORKSHEET_IMPORT_PREVIEW_COMMAND = "python3 scripts/update_manual_social_stats.py --from-csv --dry-run"
WORKSHEET_IMPORT_COMMAND = "python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin"
ENTRY_IMPORT_PREVIEW_COMMAND = "python3 scripts/update_manual_social_stats.py --from-csv data/manual_metric_entry_template.csv --dry-run"
ENTRY_IMPORT_COMMAND = "python3 scripts/update_manual_social_stats.py --from-csv data/manual_metric_entry_template.csv --refresh-admin"

METRIC_SPECS = {
    "followers": ("nonnegative_integer", "123", "Enter the current public follower count."),
    "artist_followers": ("nonnegative_integer", "123", "Enter the current Spotify artist follower count."),
    "monthly_listeners": ("nonnegative_integer", "123", "Enter the current Spotify monthly listener count."),
    "release_streams": ("nonnegative_integer", "1234", "Enter lifetime streams for the promoted release."),
    "saves": ("nonnegative_integer", "12", "Enter lifetime saves for the promoted release."),
    "reach_7d": ("nonnegative_integer", "123", "Enter reach for the last 7 days."),
    "profile_visits_7d": ("nonnegative_integer", "12", "Enter profile visits for the last 7 days."),
    "profile_views_7d": ("nonnegative_integer", "12", "Enter profile views for the last 7 days."),
    "impressions_7d": ("nonnegative_integer", "123", "Enter impressions for the last 7 days."),
}

METRIC_STRATEGY = {
    "followers": (1, "Audience size snapshot", "public_profile", "Capture the public follower count from the profile page or account dashboard."),
    "artist_followers": (1, "Audience size snapshot", "public_profile", "Capture the public Spotify artist follower count if visible, otherwise use Spotify for Artists."),
    "monthly_listeners": (1, "Audience size snapshot", "public_profile", "Capture the public Spotify monthly listeners count from the artist profile."),
    "reach_7d": (2, "Recent discovery and traffic", "private_analytics", "Use the last-7-days reach value from Meta insights."),
    "profile_visits_7d": (2, "Recent discovery and traffic", "private_analytics", "Use the last-7-days profile visits value from the professional dashboard."),
    "profile_views_7d": (2, "Recent discovery and traffic", "private_analytics", "Use the last-7-days profile views value from TikTok analytics."),
    "impressions_7d": (2, "Recent discovery and traffic", "private_analytics", "Use the last-7-days impressions value from X analytics."),
    "release_streams": (3, "Release depth metrics", "private_analytics", "Use lifetime streams for the promoted release from Spotify for Artists."),
    "saves": (3, "Release depth metrics", "private_analytics", "Use lifetime saves for the promoted release from Spotify for Artists."),
}


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def existing_new_values() -> dict[tuple[str, str], str]:
    values = {}
    for path in [OUT_CSV, OUT_ENTRY_CSV]:
        if not path.exists():
            continue
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                platform = str(row.get("platform") or "").strip()
                field = str(row.get("field") or "").strip()
                new_value = str(row.get("new_value") or "").strip()
                if platform and field and new_value:
                    values[(platform, field)] = new_value
    return values


def existing_entry_notes() -> dict[tuple[str, str], str]:
    if not OUT_ENTRY_CSV.exists():
        return {}
    notes = {}
    with OUT_ENTRY_CSV.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            platform = str(row.get("platform") or "").strip()
            field = str(row.get("field") or "").strip()
            evidence_note = str(row.get("evidence_note") or "").strip()
            if platform and field and evidence_note:
                notes[(platform, field)] = evidence_note
    return notes


def current_value(manual: dict, platform: str, field: str) -> str:
    return str(((manual.get(platform) or {}).get(field)) or "")


def collection_url(platform: str, field: str, manual: dict, live: dict) -> str:
    if (platform, field) in PUBLIC_PROFILE_COLLECTION_URLS:
        return PUBLIC_PROFILE_COLLECTION_URLS[(platform, field)]
    manual_platform = (manual.get(platform) or {}) if isinstance(manual, dict) else {}
    live_platform = ((live.get("platforms") or {}).get(platform) or {}) if isinstance(live, dict) else {}
    for key in ("artist_url", "profile_url", "public_profile_url", "release_url", "provider_url"):
        value = str(manual_platform.get(key) or live_platform.get(key) or "").strip()
        if value:
            return value
    return DEFAULT_COLLECTION_URLS.get(platform, "")


def live_metric_value(live: dict, platform: str, field: str):
    data = ((live.get("platforms") or {}).get(platform) or {}) if isinstance(live, dict) else {}
    metrics = data.get("metrics") or {}
    if field in metrics and metrics.get(field) not in (None, ""):
        return metrics.get(field)
    fallback_keys = {
        ("facebook", "followers"): ["page_likes"],
    }.get((platform, field), [])
    for key in fallback_keys:
        if key in metrics and metrics.get(key) not in (None, ""):
            return metrics.get(key)
    return None


def public_capture_status(live: dict, platform: str) -> str:
    data = ((live.get("public_profile_capture") or {}).get("platforms") or {}).get(platform) or {}
    status = str(data.get("public_capture_status") or "").strip()
    if status:
        return status
    data = ((live.get("platforms") or {}).get(platform) or {}) if isinstance(live, dict) else {}
    return str(data.get("public_capture_status") or "").strip()


def metric_spec(field: str) -> tuple[str, str, str]:
    return METRIC_SPECS.get(field, ("nonnegative_number", "123", "Enter the latest metric value."))


def metric_strategy(field: str) -> tuple[int, str, str, str]:
    return METRIC_STRATEGY.get(field, (4, "Other manual metrics", "private_analytics", "Use the linked platform source and record the latest available value."))


def import_effect(platform: str, field: str, current: str) -> str:
    return f"update data/manual_social_stats.json {platform}.{field} from {current!r} to the filled new_value"


def build_rows(status: dict, manual: dict, live: dict, preserved_values: dict[tuple[str, str], str], preserved_notes: dict[tuple[str, str], str]) -> list[dict]:
    kpi = status.get("kpi") or {}
    pending = kpi.get("pending_manual_by_platform") or {}
    commands = kpi.get("pending_manual_update_by_platform") or {}
    steps = {
        step.get("platform"): step
        for step in (kpi.get("manual_metric_collection_steps") or [])
        if step.get("platform")
    }
    rows = []
    for platform, fields in sorted(pending.items()):
        step = steps.get(platform) or {}
        for field in fields:
            live_value = live_metric_value(live, platform, field)
            collection_mode = "live_import_available" if live_value is not None else "manual_collection_required"
            current = current_value(manual, platform, field)
            value_type, example_value, instruction = metric_spec(field)
            priority, category, access_level, evidence_hint = metric_strategy(field)
            capture_status = public_capture_status(live, platform) if access_level == "public_profile" else ""
            adapter_blocker = "" if live_value is not None else capture_status
            rows.append({
                "platform": platform,
                "field": field,
                "current_value": current,
                "new_value": preserved_values.get((platform, field), ""),
                "evidence_note": preserved_notes.get((platform, field), ""),
                "live_value": "" if live_value is None else str(live_value),
                "collection_mode": collection_mode,
                "collection_priority": priority,
                "metric_category": category,
                "access_level": access_level,
                "value_type": value_type,
                "example_value": example_value,
                "collection_instruction": instruction,
                "evidence_hint": evidence_hint,
                "source_hint": SOURCE_HINTS.get(platform, "Manual platform export"),
                "collection_url": collection_url(platform, field, manual, live),
                "public_capture_status": capture_status,
                "adapter_blocker": adapter_blocker,
                "reason": step.get("reason") or "",
                "update_assignment": f"{platform}.{field}=VALUE",
                "import_effect": import_effect(platform, field, current),
                "platform_update_command": commands.get(platform, ""),
            })
    for index, row in enumerate(rows, start=2):
        row["csv_row"] = index
        row["ready_to_import"] = bool(str(row.get("new_value") or "").strip())
    return rows


def write_csv(rows: list[dict]) -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "platform",
        "field",
        "current_value",
        "new_value",
        "evidence_note",
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
        "public_capture_status",
        "adapter_blocker",
        "reason",
        "update_assignment",
        "import_effect",
        "platform_update_command",
        "csv_row",
        "ready_to_import",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_entry_csv(rows: list[dict]) -> None:
    OUT_ENTRY_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "platform",
        "field",
        "new_value",
        "evidence_note",
        "current_value",
        "value_type",
        "example_value",
        "collection_priority",
        "metric_category",
        "access_level",
        "collection_url",
        "collection_instruction",
        "evidence_hint",
        "csv_row",
        "update_assignment",
        "import_effect",
    ]
    with OUT_ENTRY_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows({key: row.get(key, "") for key in fieldnames} for row in rows)


def build_packet(rows: list[dict], generated_at: str) -> dict:
    by_platform = {}
    live_import_rows = [row for row in rows if row.get("collection_mode") == "live_import_available"]
    manual_rows = [row for row in rows if row.get("collection_mode") != "live_import_available"]
    public_manual_rows = [
        row for row in manual_rows
        if row.get("access_level") == "public_profile" and not row.get("ready_to_import")
    ]
    private_manual_rows = [
        row for row in manual_rows
        if row.get("access_level") == "private_analytics" and not row.get("ready_to_import")
    ]
    ready_rows = [row for row in rows if row.get("ready_to_import")]
    for row in rows:
        platform = row["platform"]
        group = by_platform.setdefault(platform, {
            "platform": platform,
            "source_hint": row.get("source_hint") or SOURCE_HINTS.get(platform, "Manual platform export"),
            "collection_url": row.get("collection_url") or "",
            "reason": row.get("reason") or "",
            "fields": [],
            "field_count": 0,
            "pending_assignments": [],
            "collection_packets": [],
            "live_import_available_count": 0,
            "manual_collection_required_count": 0,
            "ready_to_import_count": 0,
            "platform_update_command": row.get("platform_update_command") or "",
            "live_import_preview_command": LIVE_IMPORT_PREVIEW_COMMAND,
            "live_import_command": LIVE_IMPORT_COMMAND,
            "worksheet_import_preview_command": WORKSHEET_IMPORT_PREVIEW_COMMAND,
            "worksheet_import_command": WORKSHEET_IMPORT_COMMAND,
            "entry_csv_path": str(OUT_ENTRY_CSV.relative_to(ROOT)),
            "entry_import_preview_command": ENTRY_IMPORT_PREVIEW_COMMAND,
            "entry_import_command": ENTRY_IMPORT_COMMAND,
        })
        group["fields"].append({
                "field": row["field"],
                "current_value": row.get("current_value") or "",
                "new_value": row.get("new_value") or "",
                "evidence_note": row.get("evidence_note") or "",
                "live_value": row.get("live_value") or "",
                "collection_mode": row.get("collection_mode") or "manual_collection_required",
                "collection_priority": row.get("collection_priority") or 4,
                "metric_category": row.get("metric_category") or "",
                "access_level": row.get("access_level") or "",
                "value_type": row.get("value_type") or "nonnegative_number",
                "example_value": row.get("example_value") or "",
                "collection_instruction": row.get("collection_instruction") or "",
                "evidence_hint": row.get("evidence_hint") or "",
                "public_capture_status": row.get("public_capture_status") or "",
                "adapter_blocker": row.get("adapter_blocker") or "",
                "update_assignment": row.get("update_assignment") or "",
                "import_effect": row.get("import_effect") or "",
                "csv_row": row.get("csv_row"),
                "ready_to_import": bool(row.get("ready_to_import")),
            })
        group["collection_packets"].append({
            "csv_row": row.get("csv_row"),
            "field": row["field"],
            "current_value": row.get("current_value") or "",
            "new_value": row.get("new_value") or "",
            "evidence_note": row.get("evidence_note") or "",
            "ready_to_import": bool(row.get("ready_to_import")),
            "collection_mode": row.get("collection_mode") or "manual_collection_required",
            "collection_priority": row.get("collection_priority") or 4,
            "metric_category": row.get("metric_category") or "",
            "access_level": row.get("access_level") or "",
            "source_hint": row.get("source_hint") or "",
            "collection_url": row.get("collection_url") or "",
            "collection_instruction": row.get("collection_instruction") or "",
            "evidence_hint": row.get("evidence_hint") or "",
            "public_capture_status": row.get("public_capture_status") or "",
            "adapter_blocker": row.get("adapter_blocker") or "",
            "update_assignment": row.get("update_assignment") or "",
            "import_effect": row.get("import_effect") or "",
        })
        group["pending_assignments"].append(row.get("update_assignment") or "")
        group["field_count"] = len(group["fields"])
        if row.get("collection_mode") == "live_import_available":
            group["live_import_available_count"] += 1
        else:
            group["manual_collection_required_count"] += 1
        if row.get("ready_to_import"):
            group["ready_to_import_count"] += 1
    platforms = list(by_platform.values())
    docket = build_collection_docket(platforms, ready_rows)
    priority_batches = build_priority_batches(rows)
    return {
        "generated_at": generated_at,
        "safe_mode": True,
        "source": {
            "promo_engine_status": str(PROMO_STATUS.relative_to(ROOT)),
            "manual_social_stats": str(MANUAL_STATS.relative_to(ROOT)),
            "live_metrics": str(LIVE_METRICS.relative_to(ROOT)),
            "csv": str(OUT_CSV.relative_to(ROOT)),
            "entry_csv": str(OUT_ENTRY_CSV.relative_to(ROOT)),
            "report": str(OUT_MD.relative_to(ROOT)),
        },
        "summary": {
            "pending_field_count": len(rows),
            "live_import_available_count": len(live_import_rows),
            "manual_collection_required_count": len(manual_rows),
            "public_profile_manual_required_count": len(public_manual_rows),
            "private_analytics_manual_required_count": len(private_manual_rows),
            "ready_to_import_count": len(ready_rows),
            "preserved_new_value_count": len(ready_rows),
            "platform_count": len(platforms),
            "priority_batch_count": len(priority_batches),
            "public_profile_field_count": len([row for row in rows if row.get("access_level") == "public_profile"]),
            "private_analytics_field_count": len([row for row in rows if row.get("access_level") == "private_analytics"]),
            "csv_path": str(OUT_CSV.relative_to(ROOT)),
            "entry_csv_path": str(OUT_ENTRY_CSV.relative_to(ROOT)),
            "report_path": str(OUT_MD.relative_to(ROOT)),
            "live_import_preview_command": LIVE_IMPORT_PREVIEW_COMMAND,
            "live_import_command": LIVE_IMPORT_COMMAND,
            "worksheet_import_preview_command": WORKSHEET_IMPORT_PREVIEW_COMMAND,
            "worksheet_import_command": WORKSHEET_IMPORT_COMMAND,
            "entry_import_preview_command": ENTRY_IMPORT_PREVIEW_COMMAND,
            "entry_import_command": ENTRY_IMPORT_COMMAND,
        },
        "metric_collection_docket": docket,
        "worksheet_import_manifest": build_import_manifest(rows),
        "public_metric_capture_backlog": build_public_metric_capture_backlog(public_manual_rows),
        "priority_batches": priority_batches,
        "platforms": platforms,
        "rows": rows,
    }


def build_public_metric_capture_backlog(rows: list[dict]) -> dict:
    return {
        "status": "needs_capture_adapter" if rows else "clear",
        "field_count": len(rows),
        "fields": [
            {
                "platform": row.get("platform") or "",
                "field": row.get("field") or "",
                "csv_row": row.get("csv_row"),
                "collection_url": row.get("collection_url") or "",
                "source_hint": row.get("source_hint") or "",
                "evidence_hint": row.get("evidence_hint") or "",
                "public_capture_status": row.get("public_capture_status") or "",
                "adapter_blocker": row.get("adapter_blocker") or "",
                "update_assignment": row.get("update_assignment") or "",
            }
            for row in rows
        ],
        "recommended_engine_work": (
            "Add safe public profile capture adapters for these public fields, then route them through "
            "data/live_social_metrics.json and scripts/update_manual_social_stats.py --from-live."
            if rows else ""
        ),
        "guardrail": "Do not treat private analytics fields as public-capture candidates.",
    }


def build_priority_batches(rows: list[dict]) -> list[dict]:
    batches = {}
    for row in rows:
        priority = int(row.get("collection_priority") or 4)
        category = row.get("metric_category") or "Other manual metrics"
        key = (priority, category)
        batch = batches.setdefault(key, {
            "priority": priority,
            "label": category,
            "status": "needs_values",
            "field_count": 0,
            "waiting_count": 0,
            "ready_to_import_count": 0,
            "platforms": [],
            "access_levels": [],
            "csv_rows": [],
            "fields": [],
            "worksheet_import_preview_command": WORKSHEET_IMPORT_PREVIEW_COMMAND,
            "worksheet_import_command": WORKSHEET_IMPORT_COMMAND,
            "entry_import_preview_command": ENTRY_IMPORT_PREVIEW_COMMAND,
            "entry_import_command": ENTRY_IMPORT_COMMAND,
        })
        batch["field_count"] += 1
        batch["csv_rows"].append(row.get("csv_row"))
        if row.get("platform") not in batch["platforms"]:
            batch["platforms"].append(row.get("platform"))
        if row.get("access_level") not in batch["access_levels"]:
            batch["access_levels"].append(row.get("access_level"))
        field_payload = {
            "platform": row.get("platform") or "",
            "field": row.get("field") or "",
            "csv_row": row.get("csv_row"),
            "ready_to_import": bool(row.get("ready_to_import")),
            "collection_url": row.get("collection_url") or "",
            "collection_instruction": row.get("collection_instruction") or "",
            "evidence_hint": row.get("evidence_hint") or "",
            "evidence_note": row.get("evidence_note") or "",
            "update_assignment": row.get("update_assignment") or "",
        }
        batch["fields"].append(field_payload)
        if row.get("ready_to_import"):
            batch["ready_to_import_count"] += 1
        else:
            batch["waiting_count"] += 1
    ordered = []
    for (_priority, _category), batch in sorted(batches.items()):
        if batch["ready_to_import_count"] and not batch["waiting_count"]:
            batch["status"] = "ready_to_import"
        elif batch["ready_to_import_count"]:
            batch["status"] = "partial"
        ordered.append(batch)
    return ordered


def build_collection_docket(platforms: list[dict], ready_rows: list[dict]) -> dict:
    platform_groups = []
    for platform in platforms:
        fields = platform.get("fields") or []
        waiting_fields = [field for field in fields if not field.get("ready_to_import")]
        ready_fields = [field for field in fields if field.get("ready_to_import")]
        platform_groups.append({
            "platform": platform.get("platform") or "",
            "status": "ready_to_import" if ready_fields and not waiting_fields else ("partial" if ready_fields else "needs_values"),
            "field_count": len(fields),
            "waiting_count": len(waiting_fields),
            "ready_to_import_count": len(ready_fields),
            "source_hint": platform.get("source_hint") or "",
            "collection_url": platform.get("collection_url") or "",
            "reason": platform.get("reason") or "",
            "priority_summary": sorted({field.get("metric_category") for field in fields if field.get("metric_category")}),
            "fields": fields,
            "collection_packets": platform.get("collection_packets") or [],
            "pending_assignments": platform.get("pending_assignments") or [],
            "platform_update_command": platform.get("platform_update_command") or "",
            "worksheet_import_preview_command": platform.get("worksheet_import_preview_command") or WORKSHEET_IMPORT_PREVIEW_COMMAND,
            "worksheet_import_command": platform.get("worksheet_import_command") or WORKSHEET_IMPORT_COMMAND,
            "entry_import_preview_command": platform.get("entry_import_preview_command") or ENTRY_IMPORT_PREVIEW_COMMAND,
            "entry_import_command": platform.get("entry_import_command") or ENTRY_IMPORT_COMMAND,
        })
    return {
        "status": "ready_to_import" if ready_rows else "needs_values",
        "platform_count": len(platforms),
        "ready_to_import_count": len(ready_rows),
        "waiting_field_count": sum(group["waiting_count"] for group in platform_groups),
        "platform_groups": platform_groups,
        "csv_path": str(OUT_CSV.relative_to(ROOT)),
        "entry_csv_path": str(OUT_ENTRY_CSV.relative_to(ROOT)),
        "worksheet_import_preview_command": WORKSHEET_IMPORT_PREVIEW_COMMAND,
        "worksheet_import_command": WORKSHEET_IMPORT_COMMAND,
        "entry_import_preview_command": ENTRY_IMPORT_PREVIEW_COMMAND,
        "entry_import_command": ENTRY_IMPORT_COMMAND,
        "guardrails": [
            "Fill only new_value cells in the CSVs; generated context columns are overwritten on refresh.",
            "Run the worksheet import preview before applying metric updates.",
            "Keep metric values nonnegative and source them from the linked platform analytics surfaces.",
        ],
    }


def build_import_manifest(rows: list[dict]) -> dict:
    ready_rows = [row for row in rows if row.get("ready_to_import")]
    waiting_rows = [row for row in rows if not row.get("ready_to_import")]
    return {
        "status": "ready_to_import" if ready_rows and not waiting_rows else ("partial" if ready_rows else "needs_values"),
        "csv_path": str(OUT_CSV.relative_to(ROOT)),
        "entry_csv_path": str(OUT_ENTRY_CSV.relative_to(ROOT)),
        "ready_row_count": len(ready_rows),
        "waiting_row_count": len(waiting_rows),
        "ready_csv_rows": [row.get("csv_row") for row in ready_rows],
        "waiting_csv_rows": [row.get("csv_row") for row in waiting_rows],
        "ready_assignments": [row.get("update_assignment") for row in ready_rows if row.get("update_assignment")],
        "waiting_assignments": [row.get("update_assignment") for row in waiting_rows if row.get("update_assignment")],
        "preview_command": WORKSHEET_IMPORT_PREVIEW_COMMAND,
        "apply_command": WORKSHEET_IMPORT_COMMAND if ready_rows else "",
        "entry_preview_command": ENTRY_IMPORT_PREVIEW_COMMAND,
        "entry_apply_command": ENTRY_IMPORT_COMMAND if ready_rows else "",
        "apply_gate": "ready_rows_available" if ready_rows else "blocked_until_new_values_filled",
        "rows": [
            {
                "csv_row": row.get("csv_row"),
                "platform": row.get("platform") or "",
                "field": row.get("field") or "",
                "ready_to_import": bool(row.get("ready_to_import")),
                "new_value": row.get("new_value") or "",
                "evidence_note": row.get("evidence_note") or "",
                "value_type": row.get("value_type") or "",
                "collection_priority": row.get("collection_priority") or 4,
                "metric_category": row.get("metric_category") or "",
                "access_level": row.get("access_level") or "",
                "source_hint": row.get("source_hint") or "",
                "collection_url": row.get("collection_url") or "",
                "evidence_hint": row.get("evidence_hint") or "",
                "update_assignment": row.get("update_assignment") or "",
                "import_effect": row.get("import_effect") or "",
            }
            for row in rows
        ],
        "guardrail": "Import only filled nonnegative numeric new_value cells; leave unknown rows blank.",
    }


def build_markdown(rows: list[dict], generated_at: str, packet: dict) -> str:
    lines = [
        "# Manual Metric Collection - Lily Roo",
        "",
        f"Generated: {generated_at}",
        "",
        f"Pending fields: **{len(rows)}**",
        "",
        f"Live-importable fields: **{len([row for row in rows if row.get('collection_mode') == 'live_import_available'])}**",
        f"Manual collection required: **{len([row for row in rows if row.get('collection_mode') != 'live_import_available'])}**",
        "",
        "Fill `new_value` in `data/manual_metric_entry_template.csv` for the short entry workflow, then run:",
        "",
        f"`{ENTRY_IMPORT_PREVIEW_COMMAND}`",
        "",
        "If the preview looks right, run:",
        "",
        f"`{ENTRY_IMPORT_COMMAND}`",
        "",
        "The detailed worksheet remains available at `data/manual_metric_collection_template.csv`:",
        "",
        f"`{WORKSHEET_IMPORT_PREVIEW_COMMAND}`",
        "",
        "If the preview looks right, run:",
        "",
        f"`{WORKSHEET_IMPORT_COMMAND}`",
        "",
        "To sync metrics already covered by `data/live_social_metrics.json`, run:",
        "",
        f"`{LIVE_IMPORT_PREVIEW_COMMAND}`",
        "",
        "If the preview looks right, run:",
        "",
        f"`{LIVE_IMPORT_COMMAND}`",
        "",
        "You can still run a platform update command directly if you only collect one platform.",
        "",
        "## Metric Collection Docket",
        "",
    ]
    docket = packet.get("metric_collection_docket") or {}
    lines.extend([
        f"- Status: **{docket.get('status', 'unknown')}**",
        f"- Platforms: **{docket.get('platform_count', 0)}**",
        f"- Waiting fields: **{docket.get('waiting_field_count', 0)}**",
        f"- Ready to import: **{docket.get('ready_to_import_count', 0)}**",
        f"- CSV: `{docket.get('csv_path') or str(OUT_CSV.relative_to(ROOT))}`",
        f"- Short entry CSV: `{docket.get('entry_csv_path') or str(OUT_ENTRY_CSV.relative_to(ROOT))}`",
        f"- Preview worksheet import: `{docket.get('worksheet_import_preview_command') or WORKSHEET_IMPORT_PREVIEW_COMMAND}`",
        f"- Apply worksheet import after review: `{docket.get('worksheet_import_command') or WORKSHEET_IMPORT_COMMAND}`",
        f"- Preview short entry import: `{docket.get('entry_import_preview_command') or ENTRY_IMPORT_PREVIEW_COMMAND}`",
        f"- Apply short entry import after review: `{docket.get('entry_import_command') or ENTRY_IMPORT_COMMAND}`",
        "",
    ])
    public_backlog = packet.get("public_metric_capture_backlog") or {}
    if public_backlog.get("field_count"):
        lines.extend([
            "## Public Metric Capture Backlog",
            "",
            f"- Fields: **{public_backlog.get('field_count', 0)}**",
            f"- Status: **{public_backlog.get('status', 'unknown')}**",
            f"- Engine work: {public_backlog.get('recommended_engine_work')}",
            f"- Guardrail: {public_backlog.get('guardrail')}",
            "",
        ])
        for field in public_backlog.get("fields") or []:
            lines.append(f"- CSV row `{field.get('csv_row')}` `{field.get('platform')}.{field.get('field')}`")
            if field.get("collection_url"):
                lines.append(f"  - Public/source URL: {field['collection_url']}")
            if field.get("evidence_hint"):
                lines.append(f"  - Evidence: {field['evidence_hint']}")
        lines.append("")
    for batch in packet.get("priority_batches") or []:
        lines.append(f"### Priority {batch.get('priority')}: {batch.get('label')}")
        lines.append(f"- Status: `{batch.get('status')}`; waiting: **{batch.get('waiting_count', 0)}**; ready: **{batch.get('ready_to_import_count', 0)}**")
        lines.append(f"- Platforms: `{', '.join(batch.get('platforms') or [])}`")
        lines.append(f"- Access: `{', '.join(batch.get('access_levels') or [])}`")
        lines.append(f"- CSV rows: `{', '.join(str(item) for item in batch.get('csv_rows') or [])}`")
        for field in batch.get("fields") or []:
            lines.append(f"- Row `{field.get('csv_row')}` `{field.get('platform')}.{field.get('field')}`")
            if field.get("collection_instruction"):
                lines.append(f"  - {field['collection_instruction']}")
            if field.get("evidence_hint"):
                lines.append(f"  - Evidence: {field['evidence_hint']}")
        lines.append("")
    manifest = packet.get("worksheet_import_manifest") or {}
    lines.extend([
        "## Worksheet Import Manifest",
        "",
        f"- Status: **{manifest.get('status', 'unknown')}**",
        f"- Ready rows: **{manifest.get('ready_row_count', 0)}**",
        f"- Waiting rows: **{manifest.get('waiting_row_count', 0)}**",
        f"- Preview: `{manifest.get('preview_command') or WORKSHEET_IMPORT_PREVIEW_COMMAND}`",
        f"- Apply after review: `{manifest.get('apply_command') or 'blocked until new_value cells are filled'}`",
        f"- Short entry preview: `{manifest.get('entry_preview_command') or ENTRY_IMPORT_PREVIEW_COMMAND}`",
        f"- Short entry apply after review: `{manifest.get('entry_apply_command') or 'blocked until new_value cells are filled'}`",
        f"- Apply gate: **{manifest.get('apply_gate', 'unknown')}**",
        f"- Guardrail: {manifest.get('guardrail') or 'Import only collected values.'}",
        "",
    ])
    for group in docket.get("platform_groups") or []:
        lines.append(f"### {group.get('platform')}")
        lines.append(f"- Status: `{group.get('status')}`; waiting: **{group.get('waiting_count', 0)}**; ready: **{group.get('ready_to_import_count', 0)}**")
        if group.get("collection_url"):
            lines.append(f"- Open: {group['collection_url']}")
        if group.get("reason"):
            lines.append(f"- Why: {group['reason']}")
        for field in group.get("fields") or []:
            target = field.get("new_value") if field.get("ready_to_import") else f"{field.get('value_type', 'value')} e.g. {field.get('example_value', '')}".strip()
            lines.append(f"- CSV row `{field.get('csv_row')}` `{field.get('field')}` current `{field.get('current_value')}` -> `{target}`")
            if field.get("collection_instruction"):
                lines.append(f"  - {field['collection_instruction']}")
            if field.get("evidence_hint"):
                lines.append(f"  - Evidence: {field['evidence_hint']}")
        if group.get("platform_update_command"):
            lines.append(f"- Platform command: `{group['platform_update_command']}`")
        lines.append("")
    by_platform = {}
    for row in rows:
        by_platform.setdefault(row["platform"], []).append(row)
    for platform, platform_rows in by_platform.items():
        lines.append(f"## {platform}")
        lines.append("")
        lines.append(f"Source: {SOURCE_HINTS.get(platform, 'Manual platform export')}")
        url = platform_rows[0].get("collection_url")
        if url:
            lines.append(f"Open: {url}")
        reason = platform_rows[0].get("reason")
        if reason:
            lines.append(f"Why: {reason}")
        lines.append("")
        for row in platform_rows:
            if row.get("collection_mode") == "live_import_available":
                lines.append(f"- CSV row `{row.get('csv_row')}` `{row['field']}` current `{row['current_value']}` -> live `{row['live_value']}`")
            else:
                target = row.get("new_value") or "VALUE"
                lines.append(f"- CSV row `{row.get('csv_row')}` `{row['field']}` current `{row['current_value']}` -> `{target}` ({row.get('value_type')}; example `{row.get('example_value')}`)")
            if row.get("ready_to_import"):
                lines.append("  - Ready to import from worksheet new_value.")
            if row.get("collection_instruction"):
                lines.append(f"  - {row['collection_instruction']}")
            if row.get("import_effect"):
                lines.append(f"  - Import effect: {row['import_effect']}")
        command = platform_rows[0].get("platform_update_command")
        if command:
            lines.append("")
            lines.append(f"Command: `{command}`")
        lines.append("")
    if not rows:
        lines.append("No pending manual metric fields.")
        lines.append("")
    return "\n".join(lines)


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


def sync_admin(markdown: str, packet: dict) -> None:
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    html = replace_text_embed(html, "embedded-manual-metric-collection", markdown)
    html = replace_json_embed(html, "embedded-manual-metric-collection-packet", packet)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    status = read_json(PROMO_STATUS, {})
    manual = read_json(MANUAL_STATS, {})
    live = read_json(LIVE_METRICS, {})
    rows = build_rows(status, manual, live, existing_new_values(), existing_entry_notes())
    write_csv(rows)
    write_entry_csv(rows)
    packet = build_packet(rows, generated_at)
    OUT_JSON.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(rows, generated_at, packet)
    OUT_MD.write_text(markdown, encoding="utf-8")
    sync_admin(markdown, packet)
    print(json.dumps({
        "csv": str(OUT_CSV.relative_to(ROOT)),
        "entry_csv": str(OUT_ENTRY_CSV.relative_to(ROOT)),
        "json": str(OUT_JSON.relative_to(ROOT)),
        "report": str(OUT_MD.relative_to(ROOT)),
        "pending_fields": len(rows),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
