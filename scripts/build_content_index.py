#!/usr/bin/env python3
import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "admin" / "content"
PACKS = CONTENT / "packs"
CATALOG = ROOT / "admin" / "backstory" / "catalog.json"
QUIPS = CONTENT / "20_QUIPS_BANK.csv"
ANECDOTES = CONTENT / "10_ANECDOTE_BANK.md"
QUEUE = ROOT / "data" / "scheduled_posts.csv"
PUBLISHED = CONTENT / "Published_Log.csv"
REPORT = ROOT / "admin" / "reports" / "weekly-social-report.md"
OUT_JSON = CONTENT / "content_index.json"
OUT_MD = CONTENT / "CONTENT_INDEX.md"


def read_json(path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_text(path):
    return path.read_text(encoding="utf-8") if path.exists() else ""


def pack_status(song):
    backstory = ROOT / str(song.get("backstory_file", "")).lstrip("/")
    visual = ROOT / str(song.get("visual_file", "")).lstrip("/")
    return {
        "backstory": str(backstory.relative_to(ROOT)) if backstory.exists() else "",
        "visual": str(visual.relative_to(ROOT)) if visual.exists() else "",
        "complete": backstory.exists() and visual.exists(),
    }


def parse_anecdote_sections(text):
    sections = {}
    current = "Unsorted"
    for line in text.splitlines():
        heading = re.match(r"^##\s+(.+)", line)
        if heading:
            current = heading.group(1).strip()
            sections[current] = []
            continue
        item = re.match(r"- \*\*(LR-ANEC-\d+)\*\*:\s+(.+)", line)
        if item:
            sections.setdefault(current, []).append({"id": item.group(1), "text": item.group(2)})
    return sections


def report_meta(text):
    period = re.search(r"\*\*Period:\*\*\s*(.+)", text)
    updated = re.search(r"\*\*Last updated:\*\*\s*(.+)", text)
    return {
        "period": period.group(1).strip() if period else "",
        "last_updated": updated.group(1).strip() if updated else "",
    }


def build_index():
    catalog = read_json(CATALOG, {"songs": []})
    songs = catalog.get("songs", [])
    queue_rows = read_csv(QUEUE)
    quips = read_csv(QUIPS)
    published_rows = read_csv(PUBLISHED)
    anecdote_sections = parse_anecdote_sections(read_text(ANECDOTES))
    report = report_meta(read_text(REPORT))

    indexed_songs = []
    warnings = []
    for song in songs:
        packs = pack_status(song)
        if not packs["complete"]:
            warnings.append(f"Missing pack pair for {song.get('title', 'Unknown')}")
        indexed_songs.append({
            "id": song.get("id", ""),
            "title": song.get("title", ""),
            "slug": song.get("slug", ""),
            "era": song.get("era", ""),
            "status": song.get("status", ""),
            "url": song.get("url", ""),
            "packs": packs,
        })

    quip_themes = Counter(row.get("theme", "") for row in quips if row.get("theme"))
    queue_platforms = Counter(row.get("platform", "") for row in queue_rows if row.get("platform"))
    queue_songs = Counter(row.get("song", "") for row in queue_rows if row.get("song"))

    if not quips:
        warnings.append("Quips bank is empty")
    if not queue_rows:
        warnings.append("Scheduled queue is empty")
    if not report["last_updated"]:
        warnings.append("Weekly report has no Last updated timestamp")

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "catalog": str(CATALOG.relative_to(ROOT)),
            "quips": str(QUIPS.relative_to(ROOT)),
            "anecdotes": str(ANECDOTES.relative_to(ROOT)),
            "queue": str(QUEUE.relative_to(ROOT)),
            "published_log": str(PUBLISHED.relative_to(ROOT)),
            "weekly_report": str(REPORT.relative_to(ROOT)),
        },
        "counts": {
            "songs": len(indexed_songs),
            "complete_pack_pairs": sum(1 for song in indexed_songs if song["packs"]["complete"]),
            "quips": len(quips),
            "anecdotes": sum(len(items) for items in anecdote_sections.values()),
            "queue_posts": len(queue_rows),
            "published_rows": len(published_rows),
        },
        "song_status": dict(Counter(song.get("status", "") for song in indexed_songs)),
        "song_eras": dict(Counter(song.get("era", "") for song in indexed_songs)),
        "quip_themes": dict(sorted(quip_themes.items())),
        "queue_platforms": dict(sorted(queue_platforms.items())),
        "queue_songs": dict(sorted(queue_songs.items())),
        "weekly_report": report,
        "songs": indexed_songs,
        "anecdote_sections": anecdote_sections,
        "warnings": warnings,
    }


def markdown(index):
    counts = index["counts"]
    lines = [
        "# Lily Roo Content Index",
        "",
        f"Generated: `{index['generated_at']}`",
        "",
        "## Snapshot",
        "",
        f"- Songs: **{counts['songs']}**",
        f"- Complete pack pairs: **{counts['complete_pack_pairs']} / {counts['songs']}**",
        f"- Quips: **{counts['quips']}**",
        f"- Anecdotes: **{counts['anecdotes']}**",
        f"- Queue posts: **{counts['queue_posts']}**",
        f"- Published log rows: **{counts['published_rows']}**",
        f"- Weekly report: **{index['weekly_report'].get('period') or 'pending'}**",
        "",
        "## Queue Mix",
        "",
    ]
    for platform, count in index["queue_platforms"].items():
        lines.append(f"- {platform}: {count}")
    if not index["queue_platforms"]:
        lines.append("- No queued posts")

    lines.extend(["", "## Quip Themes", ""])
    for theme, count in index["quip_themes"].items():
        lines.append(f"- {theme}: {count}")

    lines.extend(["", "## Songs", ""])
    for song in index["songs"]:
        pack = "complete" if song["packs"]["complete"] else "missing pack"
        lines.append(f"- **{song['title']}** (`{song['id']}`): {song['era']} / {song['status']} / {pack}")

    lines.extend(["", "## Warnings", ""])
    if index["warnings"]:
        for warning in index["warnings"]:
            lines.append(f"- {warning}")
    else:
        lines.append("- None")

    lines.append("")
    return "\n".join(lines)


def main():
    index = build_index()
    OUT_JSON.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_MD.write_text(markdown(index), encoding="utf-8")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
