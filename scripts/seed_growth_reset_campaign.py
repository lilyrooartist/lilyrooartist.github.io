#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import urllib.parse
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data" / "scheduled_posts.csv"
CLIPS = ROOT / "data" / "growth_reset_clips.json"
READINESS = ROOT / "data" / "executor_readiness_snapshot.json"
OUT = ROOT / "data" / "growth_reset_campaign.json"
ARCHIVE = ROOT / "data" / "retired_growth_static_posts.csv"
REPORT = ROOT / "admin" / "reports" / "growth-reset-campaign.md"

TZ = ZoneInfo("America/New_York")
PREFIX = "FP-GROWTH-RESET"
LEGACY_PREFIX = "FP-BRAND-AM"
DEFAULT_START = date(2026, 7, 13)
STATIC_CYCLE_END = date(2026, 7, 11)
TRACKING_BASE = "https://www.lilyroo.com/go/am.html"
PUBLIC_CLIP_BASE = "https://www.lilyroo.com/assets/campaigns/analog-myth-growth-reset"
SPOTIFY_URL = "https://open.spotify.com/album/"
DESTINATIONS = ("spotify", "album", "video", "echo")

CONCEPT_COPY = {
    "lyric_punch_line": {
        "label": "Lyric punch line",
        "destination": "spotify",
        "hooks": {
            "Slow Walk": "What is the rush to the same place? Slow Walk keeps its own time.",
            "Spilling the Tea": "Some truths arrive with a little steam. Spilling the Tea is already in the room.",
            "No Mortgage": "Tiny house. One light. No Mortgage. That is the whole escape plan.",
        },
    },
    "relatable_situation": {
        "label": "Relatable situation",
        "destination": "album",
        "hooks": {
            "Slow Walk": "When everyone says you are behind, but you are the only one still arriving.",
            "Spilling the Tea": "When the group chat says we need to talk and you already know.",
            "No Mortgage": "When your dream home is mostly somewhere nobody can find you.",
        },
    },
    "visual_story": {
        "label": "Visual story",
        "destination": "video",
        "hooks": {
            "Slow Walk": "A quiet walk through the pressure until the pressure learns your pace.",
            "Spilling the Tea": "One cup. One secret. A whole room changing temperature.",
            "No Mortgage": "Trade the noise for a wide sky. Keep the signal. Lose the debt.",
        },
    },
    "echo_thread_setup_song_payoff": {
        "label": "Echo Thread setup and song payoff",
        "destination": "echo",
        "hooks": {
            "Slow Walk": "What did you stop rushing? Slow Walk answers without speeding up.",
            "Spilling the Tea": "What truth are you ready to say out loud? Spilling the Tea lets it pour.",
            "No Mortgage": "What would you keep if you needed less? No Mortgage has a short list.",
        },
    },
}

TRACK_NUMBERS = {"Spilling the Tea": "04", "No Mortgage": "05", "Slow Walk": "07"}
TRACK_VIDEO_URLS = {
    "Spilling the Tea": "https://youtu.be/AfnuwBYViKw",
    "No Mortgage": "https://youtu.be/-r7khqOLpjQ",
    "Slow Walk": "https://youtu.be/nPuGjQf7lKY",
}


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def read_queue() -> tuple[list[dict], list[str]]:
    with QUEUE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_datetime(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value or ""))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=TZ)
    return parsed.astimezone(TZ)


def tracked_url(destination: str, post_id: str, track: str, concept: str) -> str:
    query = urllib.parse.urlencode({
        "p": post_id.lower(),
        "to": destination,
        "utm_wave": "video-reset",
        "utm_term": f"{slug(track)}-{slug(concept)}",
    })
    return f"{TRACKING_BASE}?{query}"


def platform_ready(platform: str) -> bool:
    readiness = read_json(READINESS, {})
    return bool(((readiness.get("summary") or {}).get("platforms") or {}).get(platform))


def schedule_at(day: date, platform: str) -> str:
    slots = {"YouTube": time(10, 15), "Facebook": time(11, 20), "X": time(14, 5)}
    return datetime.combine(day, slots[platform], tzinfo=TZ).isoformat()


def destination_label(destination: str) -> str:
    return {
        "spotify": "Hear the song",
        "album": "Enter the album room",
        "video": "Watch the full track",
        "echo": "Hear the Echo Thread",
    }[destination]


def video_row(clip: dict, index: int, day: date, platform: str) -> dict:
    track = str(clip["track"])
    concept = str(clip["concept"])
    spec = CONCEPT_COPY[concept]
    destination = spec["destination"]
    creative_id = f"{PREFIX}-{index:02d}-{slug(track).upper()}-{slug(concept).upper()}"
    post_id = f"{creative_id}-{platform.upper()}"
    hook = spec["hooks"][track]
    cta_url = tracked_url(destination, post_id, track, concept)
    is_youtube = platform == "YouTube"
    text = f"{hook} #Shorts" if is_youtube else hook
    reply = f"{destination_label(destination)}: {cta_url}"
    clip_id = str(clip["id"])
    public_clip = f"{PUBLIC_CLIP_BASE}/{clip_id}.mp4"
    return {
        "id": post_id,
        "scheduled_at": schedule_at(day, platform),
        "platform": platform,
        "song": track,
        "imagery": f"{track} - {spec['label']}",
        "imagery_url": "",
        "clip_url": public_clip,
        "text": text,
        "drafts": text,
        "reply_text": reply,
        "x_media_key": "",
        "media_key": clip_id,
        "approved": "yes" if platform_ready(platform) else "no",
        "execution_mode": "auto",
        "post_type": "video",
        "desired_privacy": "public",
        "creative_id": creative_id,
        "clip_id": clip_id,
        "concept": concept,
        "destination": destination,
    }


def x_voice_rows(start: date) -> list[dict]:
    notes = [
        ("Slow Walk", "Pace is not a race result. Slow Walk knows the room will catch up.", "album"),
        ("Spilling the Tea", "A receipt drawer is just an archive with better timing.", "video"),
        ("No Mortgage", "The fantasy is not the house. It is finally hearing yourself think.", "spotify"),
        ("Slow Walk", "Some songs arrive late on purpose and still get there first.", "echo"),
        ("Spilling the Tea", "Side-eye becomes cinema when the soundtrack keeps the receipts.", "album"),
        ("No Mortgage", "Put the keys down. Keep the wide sky.", "video"),
        ("Slow Walk", "The shortcut looked suspicious, so the song kept walking.", "spotify"),
        ("Spilling the Tea", "Truth sounds different after the cup hits the table.", "echo"),
    ]
    rows = []
    for index, (track, text, destination) in enumerate(notes, start=1):
        week = (index - 1) // 2
        weekday_offset = 0 if index % 2 else 4
        day = start + timedelta(days=week * 7 + weekday_offset)
        post_id = f"{PREFIX}-VOICE-{index:02d}-X"
        cta = tracked_url(destination, post_id, track, "brand_voice")
        rows.append({
            "id": post_id,
            "scheduled_at": schedule_at(day, "X"),
            "platform": "X",
            "song": track,
            "imagery": "Brand voice note",
            "imagery_url": "",
            "clip_url": "",
            "text": text,
            "drafts": text,
            "reply_text": f"{destination_label(destination)}: {cta}",
            "x_media_key": "",
            "media_key": "",
            "approved": "yes" if platform_ready("X") else "no",
            "execution_mode": "auto",
            "post_type": "text",
            "desired_privacy": "",
            "creative_id": f"{PREFIX}-VOICE-{index:02d}",
            "clip_id": "",
            "concept": "brand_voice",
            "destination": destination,
        })
    return rows


def build_rows(start: date) -> list[dict]:
    manifest = read_json(CLIPS, {})
    clips = manifest.get("clips") or []
    if len(clips) != 12:
        raise SystemExit(f"Expected 12 growth-reset clips in {CLIPS}, found {len(clips)}")
    rows = []
    for index, clip in enumerate(clips, start=1):
        day = start + timedelta(days=(index - 1) * 2)
        rows.append(video_row(clip, index, day, "YouTube"))
        rows.append(video_row(clip, index, day, "Facebook"))
    rows.extend(x_voice_rows(start))
    return sorted(rows, key=lambda row: row["scheduled_at"])


def retired_static_rows(rows: list[dict]) -> list[dict]:
    retired = []
    for row in rows:
        if not str(row.get("id") or "").startswith(LEGACY_PREFIX):
            continue
        scheduled = parse_datetime(row.get("scheduled_at") or "")
        if scheduled and scheduled.date() > STATIC_CYCLE_END:
            retired.append(row)
    return retired


def write_report(payload: dict) -> None:
    summary = payload["summary"]
    lines = [
        "# Lily Roo Growth Strategy Reset Campaign",
        "",
        f"Generated: {payload['generated_at']}",
        f"Mode: **{payload['mode']}**",
        "",
        "## Campaign",
        f"- Window: **{summary['start_date']} through {summary['end_date']}**",
        f"- Original vertical clips: **{summary['creative_count']}**",
        f"- Native video posts: **{summary['video_post_count']}**",
        f"- X brand-voice posts: **{summary['x_post_count']}**",
        f"- Retired future static repeats: **{summary['retired_static_count']}**",
        f"- Approved automatic posts: **{summary['approved_post_count']}**",
        f"- Waiting for automated platform readiness: **{summary['waiting_post_count']}**",
        "",
        "## Guardrails",
        "- One destination per post.",
        "- No subscriber-count, help, donation, or generic stream-now solicitation.",
        "- No manual posting rows.",
        "- YouTube rows stay unapproved until OAuth is valid.",
        "- Paid spend is planned but not authorized by this campaign file.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Cut over Lily Roo to the 30-day video-first growth reset.")
    parser.add_argument("--start-date", default=DEFAULT_START.isoformat())
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    start = date.fromisoformat(args.start_date)
    existing, fieldnames = read_queue()
    for field in ("creative_id", "clip_id", "concept", "destination"):
        if field not in fieldnames:
            fieldnames.append(field)
    candidates = build_rows(start)
    retired = retired_static_rows(existing)
    existing_ids = {str(row.get("id") or "") for row in existing}
    added = [row for row in candidates if row["id"] not in existing_ids]
    retained = [row for row in existing if row not in retired and not str(row.get("id") or "").startswith(PREFIX)]

    if args.apply:
        if retired:
            write_csv(ARCHIVE, retired, fieldnames)
        write_csv(QUEUE, sorted(retained + candidates, key=lambda row: row.get("scheduled_at") or ""), fieldnames)

    end = start + timedelta(days=29)
    payload = {
        "generated_at": datetime.now(TZ).isoformat(),
        "mode": "applied" if args.apply else "dry_run",
        "objective": "Turn Lily Roo promotion from static publishing volume into measurable native-video audience growth.",
        "summary": {
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "creative_count": 12,
            "candidate_post_count": len(candidates),
            "video_post_count": sum(row["post_type"] == "video" for row in candidates),
            "x_post_count": sum(row["platform"] == "X" for row in candidates),
            "approved_post_count": sum(row["approved"] == "yes" for row in candidates),
            "waiting_post_count": sum(row["approved"] != "yes" for row in candidates),
            "manual_post_count": sum(row["execution_mode"] == "manual" for row in candidates),
            "retired_static_count": len(retired),
            "added_post_count": len(added),
            "platform_counts": {
                platform: sum(row["platform"] == platform for row in candidates)
                for platform in ("YouTube", "Facebook", "X")
            },
        },
        "budget": {
            "planned_usd": 150,
            "authorized": False,
            "phase_one": "Six organic winners may receive up to $10 each after results exist.",
            "phase_two": "The remaining $90 is reserved for the strongest two clips.",
        },
        "retired_static_ids": [row.get("id") for row in retired],
        "added_ids": [row["id"] for row in added],
        "rows": candidates,
        "sources": {
            "clips": str(CLIPS.relative_to(ROOT)),
            "queue": str(QUEUE.relative_to(ROOT)),
            "retired_archive": str(ARCHIVE.relative_to(ROOT)),
        },
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_report(payload)
    print(json.dumps(payload["summary"], indent=2))
    if not args.apply:
        print("Dry run only. Re-run with --apply to cut over the queue.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
