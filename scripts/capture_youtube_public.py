#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT = REPO_ROOT / "data" / "youtube_public_snapshot.json"
DEFAULT_CHANNEL_ID = "UCtPCfU8Pnfy0Sdui3UEvvBg"
FEED_URL = "https://www.youtube.com/feeds/videos.xml"
ATOM = "{http://www.w3.org/2005/Atom}"
YT = "{http://www.youtube.com/xml/schemas/2015}"
MEDIA = "{http://search.yahoo.com/mrss/}"


def fetch_feed(channel_id: str) -> bytes:
    url = f"{FEED_URL}?channel_id={channel_id}"
    request = urllib.request.Request(url, headers={
        "Accept": "application/atom+xml, application/xml",
        "User-Agent": "LilyRooYouTubePublicCapture/1.0",
    })
    with urllib.request.urlopen(request, timeout=25) as response:
        return response.read()


def text(node: ET.Element | None, default: str = "") -> str:
    return (node.text or "").strip() if node is not None else default


def int_attr(node: ET.Element | None, attr: str) -> int | None:
    if node is None:
        return None
    raw = node.attrib.get(attr, "").strip()
    try:
        return int(raw)
    except ValueError:
        return None


def href(node: ET.Element | None) -> str:
    return node.attrib.get("href", "").strip() if node is not None else ""


def parse_feed(raw: bytes, channel_id: str) -> dict:
    root = ET.fromstring(raw)
    entries = []
    for entry in root.findall(f"{ATOM}entry"):
        group = entry.find(f"{MEDIA}group")
        community = group.find(f"{MEDIA}community") if group is not None else None
        stats = community.find(f"{MEDIA}statistics") if community is not None else None
        rating = community.find(f"{MEDIA}starRating") if community is not None else None
        video_id = text(entry.find(f"{YT}videoId"))
        alternate_url = href(entry.find(f"{ATOM}link"))
        views = int_attr(stats, "views")
        rating_count = int_attr(rating, "count")
        entries.append({
            "video_id": video_id,
            "title": text(entry.find(f"{ATOM}title")),
            "url": alternate_url or (f"https://www.youtube.com/watch?v={video_id}" if video_id else ""),
            "published": text(entry.find(f"{ATOM}published")),
            "updated": text(entry.find(f"{ATOM}updated")),
            "views": views,
            "rating_count": rating_count,
        })

    view_values = [entry["views"] for entry in entries if isinstance(entry.get("views"), int)]
    return {
        "ok": True,
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": "youtube-public-rss",
        "channel_id": channel_id,
        "channel_title": text(root.find(f"{ATOM}title")),
        "channel_url": href(root.find(f"{ATOM}link[@rel='alternate']")),
        "feed_url": f"{FEED_URL}?channel_id={channel_id}",
        "recent_video_count": len(entries),
        "recent_public_views_total": sum(view_values),
        "latest_video": entries[0] if entries else {},
        "videos": entries,
        "limitations": "Public RSS exposes recent uploaded videos and public view counts, not subscriber count or private 28-day analytics.",
    }


def main() -> int:
    channel_id = os.environ.get("YOUTUBE_CHANNEL_ID", DEFAULT_CHANNEL_ID).strip() or DEFAULT_CHANNEL_ID
    snapshot = parse_feed(fetch_feed(channel_id), channel_id)
    OUT.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": snapshot["ok"],
        "channel_title": snapshot["channel_title"],
        "recent_video_count": snapshot["recent_video_count"],
        "recent_public_views_total": snapshot["recent_public_views_total"],
        "latest_video": snapshot["latest_video"].get("title", ""),
        "output": str(OUT.relative_to(REPO_ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
