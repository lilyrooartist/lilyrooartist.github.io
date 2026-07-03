#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data" / "scheduled_posts.csv"
PLAYLIST = ROOT / "data" / "youtube_analog_myth_playlist.json"
EXECUTOR_READINESS = ROOT / "data" / "executor_readiness_snapshot.json"
OUT = ROOT / "data" / "brand_growth_campaign.json"
REPORT = ROOT / "admin" / "reports" / "brand-growth-campaign.md"
REPORT_INDEX = ROOT / "admin" / "reports" / "index.html"

TZ = ZoneInfo("America/New_York")
MIN_START_DATE = date(2026, 7, 4)
SUPPORTED_PLATFORMS = ("X", "Facebook")
DISABLED_PLATFORMS = {
    "Instagram": "executor readiness is blocked",
    "TikTok": "executor readiness is blocked",
    "YouTube": "queue rows upload new videos; this campaign should point at the existing album videos instead",
    "YouTube Community": "manual-only posting is out of scope",
}

QUEUE_FIELDS = [
    "id",
    "scheduled_at",
    "platform",
    "song",
    "imagery",
    "imagery_url",
    "clip_url",
    "text",
    "drafts",
    "reply_text",
    "x_media_key",
    "media_key",
    "approved",
    "execution_mode",
    "post_type",
    "desired_privacy",
]

TRACK_HOOKS = {
    "13": "opens like a calendar with a loose wire. Odd numbers, warm tape, big signal.",
    "Girls Camp": "sounds like a sleepaway myth told under fluorescent lights.",
    "Analog Myth": "is the title track: broken clocks, warm tape, exact little lies.",
    "Spilling the Tea": "keeps the gossip cinematic and the receipt drawer open.",
    "No Mortgage": "turns domestic anxiety into a bright little dare.",
    "Guards Down": "is the moment the armor starts making noise on the floor.",
    "Slow Walk": "refuses the sprint. The song takes its time and still gets there first.",
    "The Power of Light": "closes the room with a switch you can almost hear.",
}


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def read_queue() -> tuple[list[dict[str, str]], list[str]]:
    with QUEUE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or QUEUE_FIELDS)
        return list(reader), fieldnames


def write_queue(rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with QUEUE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def slug(value: str) -> str:
    out = []
    previous_dash = False
    for char in value.lower():
        if char.isalnum():
            out.append(char)
            previous_dash = False
        elif not previous_dash:
            out.append("-")
            previous_dash = True
    return "".join(out).strip("-") or "track"


def track_art(track: dict) -> str:
    title_slug = slug(track["title"])
    ext = "png" if track["title"] == "The Power of Light" else "jpg"
    return f"https://www.lilyroo.com/assets/albums/analog-myth/art/{int(track['track']):02d}-{title_slug}.{ext}"


def track_video(track: dict) -> str:
    title_slug = slug(track["title"])
    return f"https://www.lilyroo.com/assets/albums/analog-myth/video/{int(track['track']):02d}-{title_slug}-youtube-remaster.mp4"


def campaign_start(args) -> date:
    if args.start_date:
        return date.fromisoformat(args.start_date)
    tomorrow = datetime.now(TZ).date() + timedelta(days=1)
    return max(tomorrow, MIN_START_DATE)


def scheduled_at(day: date, platform: str) -> str:
    slot = time(10, 15) if platform == "X" else time(11, 20)
    return datetime.combine(day, slot, tzinfo=TZ).isoformat()


def reply_text(track: dict, playlist_url: str) -> str:
    track_url = track.get("url") or playlist_url
    return "\n".join([
        "Analog Myth: https://www.lilyroo.com/analog-myth.html",
        "Echo Thread: https://www.lilyroo.com/podcasts/analog-myth.html",
        f"Track: {track_url}",
        f"Playlist: {playlist_url}",
    ])


def sentence_case(value: str) -> str:
    value = str(value or "").strip()
    if not value:
        return value
    return value[0].upper() + value[1:]


def post_text(track: dict, platform: str) -> str:
    title = track["title"]
    hook = TRACK_HOOKS.get(title, "is live in the Lily Roo archive.")
    if platform == "X":
        return f"{title} {hook} Analog Myth is live."
    return (
        f"Analog Myth track {track['track']}: {title} {hook}\n\n"
        "The album page, Echo Thread play-through, and YouTube playlist are up."
    )


def build_rows(start: date, approval: str, platforms: list[str]) -> list[dict[str, str]]:
    playlist = read_json(PLAYLIST, {})
    playlist_url = playlist.get("playlist_url") or "https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0"
    tracks = playlist.get("tracks") or []
    rows: list[dict[str, str]] = []

    for index, track in enumerate(tracks):
        day = start + timedelta(days=index)
        for platform in platforms:
            post_id = f"FP-BRAND-AM-{int(track['track']):02d}-{slug(track['title']).upper()}-{platform.upper()}"
            text = post_text(track, platform)
            if platform == "X" and len(text) > 280:
                raise SystemExit(f"{post_id} text is too long for X: {len(text)}")
            rows.append({
                "id": post_id,
                "scheduled_at": scheduled_at(day, platform),
                "platform": platform,
                "song": "Analog Myth",
                "imagery": f"Analog Myth track {track['track']} cover",
                "imagery_url": track_art(track),
                "clip_url": "",
                "text": text,
                "drafts": "||".join([
                    text,
                    f"Today in the Analog Myth room: {track['title']} {TRACK_HOOKS.get(track['title'], 'is live in the archive.')}",
                ]),
                "reply_text": reply_text(track, playlist_url),
                "x_media_key": "",
                "media_key": f"analog-myth-{int(track['track']):02d}-{slug(track['title'])}-cover",
                "approved": approval,
                "execution_mode": "auto",
                "post_type": "image",
                "desired_privacy": "",
            })
    return rows


def ready_platforms() -> list[str]:
    readiness = read_json(EXECUTOR_READINESS, {})
    summary = readiness.get("summary") or {}
    platforms = summary.get("platforms") or {}
    return sorted([platform for platform, ready in platforms.items() if ready])


def write_report(payload: dict) -> None:
    lines = [
        "# Brand Growth Campaign - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Objective",
        "Grow Lily Roo by keeping Analog Myth in motion with daily track-specific posts that feel like the album, not a solicitation.",
        "",
        "## Guardrails",
    ]
    for item in payload["guardrails"]:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Summary",
        f"- Window: {payload['summary']['start_date']} through {payload['summary']['end_date']}",
        f"- Candidate rows: {payload['summary']['candidate_rows']}",
        f"- Added rows: {payload['summary']['added_rows']}",
        f"- Updated rows: {payload['summary'].get('updated_rows', 0)}",
        f"- Duplicate rows skipped: {payload['summary']['duplicate_rows']}",
        f"- Approved on insert: {payload['summary']['approved_on_insert']}",
        f"- Ready platforms used: {', '.join(payload['summary']['ready_platforms_used']) or 'none'}",
        "",
        "## Disabled Surfaces",
    ])
    for platform, reason in payload["disabled_platforms"].items():
        lines.append(f"- {platform}: {reason}")
    lines.extend(["", "## Rows"])
    for row in payload["rows"]:
        if row["id"] in payload["added_ids"]:
            status = "added"
        elif row["id"] in payload.get("updated_ids", []):
            status = "updated"
        elif row["id"] in payload.get("pending_ids", []):
            status = "pending apply"
        else:
            status = "already present"
        lines.append(f"- {row['scheduled_at']} | {row['platform']} | {row['id']} | {status}")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def sync_report_index() -> None:
    if not REPORT_INDEX.exists():
        return
    html = REPORT_INDEX.read_text(encoding="utf-8")
    link = '<li><a href="/admin/reports/brand-growth-campaign.md" target="_blank">Brand Growth Campaign</a></li>'
    if link in html:
        return
    marker = '<li><a href="/admin/reports/promo-operations-packet.md" target="_blank">Promo Operations Packet</a></li>'
    if marker not in html:
        return
    REPORT_INDEX.write_text(html.replace(marker, marker + "\n        " + link, 1), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed the automated Analog Myth brand-growth campaign.")
    parser.add_argument("--start-date", help="First campaign date, YYYY-MM-DD. Defaults to the next day, no earlier than 2026-07-04.")
    parser.add_argument("--unapproved", action="store_true", help="Insert rows with approved=no instead of approved=yes.")
    parser.add_argument("--apply", action="store_true", help="Append missing rows to data/scheduled_posts.csv. Default is dry-run.")
    parser.add_argument("--update-existing", action="store_true", help="When applying, refresh existing campaign rows with the generated copy and links.")
    args = parser.parse_args()

    start = campaign_start(args)
    approval = "no" if args.unapproved else "yes"
    ready = ready_platforms()
    campaign_platforms = [platform for platform in SUPPORTED_PLATFORMS if platform in ready]
    candidate_rows = build_rows(start, approval, campaign_platforms)
    existing_rows, fieldnames = read_queue()
    existing_ids = {row.get("id") for row in existing_rows}
    candidate_by_id = {row["id"]: row for row in candidate_rows}
    additions = [row for row in candidate_rows if row["id"] not in existing_ids]
    updates = [row for row in candidate_rows if row["id"] in existing_ids]
    added_ids = [row["id"] for row in additions]
    updated_ids = [row["id"] for row in updates] if args.apply and args.update_existing else []
    disabled_platforms = dict(DISABLED_PLATFORMS)
    for platform in SUPPORTED_PLATFORMS:
        if platform not in campaign_platforms:
            disabled_platforms[platform] = "executor readiness is blocked"
    campaign_days = len({row["scheduled_at"].split("T", 1)[0] for row in candidate_rows})

    payload = {
        "generated_at": datetime.now(TZ).isoformat(),
        "objective": "Grow Lily Roo brand with automated Analog Myth track moments.",
        "source": {
            "scheduled_posts": str(QUEUE.relative_to(ROOT)),
            "playlist": str(PLAYLIST.relative_to(ROOT)),
            "executor_readiness": str(EXECUTOR_READINESS.relative_to(ROOT)),
        },
        "mode": "apply" if args.apply else "dry_run",
        "guardrails": [
            "No manual posting rows.",
            "No YouTube Community rows.",
            "No audience-target or help-us solicitation copy.",
            "Only executor-ready X and Facebook rows are inserted.",
            "YouTube is used as the destination for existing public videos, not as a duplicate upload lane.",
        ],
        "disabled_platforms": disabled_platforms,
        "summary": {
            "start_date": start.isoformat(),
            "end_date": (start + timedelta(days=max(campaign_days - 1, 0))).isoformat(),
            "candidate_rows": len(candidate_rows),
            "added_rows": len(additions) if args.apply else 0,
            "updated_rows": len(updated_ids),
            "pending_apply_rows": len(additions),
            "duplicate_rows": len(candidate_rows) - len(additions),
            "approved_on_insert": approval == "yes",
            "ready_platforms": ready,
            "ready_platforms_used": campaign_platforms,
        },
        "added_ids": added_ids if args.apply else [],
        "updated_ids": updated_ids,
        "pending_ids": added_ids if not args.apply else [],
        "candidate_ids": [row["id"] for row in candidate_rows],
        "rows": candidate_rows,
    }

    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_report(payload)
    sync_report_index()

    print(f"Candidate rows: {len(candidate_rows)}")
    print(f"Rows already present: {len(candidate_rows) - len(additions)}")
    print(f"Rows to append: {len(additions)}")
    if args.update_existing:
        print(f"Rows to update: {len(updates)}")
    for row in additions:
        print(f"- {row['id']} {row['scheduled_at']} {row['platform']}")

    if not args.apply:
        print("Dry run only. Re-run with --apply to append rows.")
        return 0

    if args.update_existing:
        existing_rows = [candidate_by_id.get(row.get("id", ""), row) for row in existing_rows]
    write_queue(existing_rows + additions, fieldnames)
    print(f"Appended {len(additions)} row(s) to {QUEUE}")
    if args.update_existing:
        print(f"Updated {len(updates)} existing row(s) in {QUEUE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
