#!/usr/bin/env python3
from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT = REPO_ROOT / "data" / "hyperfollow_store_links_snapshot.json"
HYPERFOLLOW_URL = "https://distrokid.com/hyperfollow/lilyroo/i-learned-it-all-in-fifteen-seconds"


class StoreLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        data = {key.lower(): value or "" for key, value in attrs}
        store = data.get("data-hyperfollow-store", "").strip()
        href = data.get("href", "").strip()
        if store and href:
            self.links.append({"store": store, "url": unescape(href)})


def main() -> int:
    request = urllib.request.Request(HYPERFOLLOW_URL, headers={
        "Accept": "text/html",
        "User-Agent": "LilyRooHyperFollowStoreCapture/1.0",
    })
    with urllib.request.urlopen(request, timeout=25) as response:
        html = response.read().decode("utf-8", errors="replace")
        status = response.status
    parser = StoreLinkParser()
    parser.feed(html)
    stores = sorted({link["store"] for link in parser.links})
    snapshot = {
        "ok": status == 200 and bool(parser.links),
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": "distrokid-hyperfollow-public-html",
        "hyperfollow_url": HYPERFOLLOW_URL,
        "stores": stores,
        "links": parser.links,
        "amazon_music_available": any("amazon" in store.lower() for store in stores),
        "youtube_music_available": any("youtube" in store.lower() for store in stores),
        "http_status": status,
        "note": "HyperFollow currently exposes only these public store links; use direct verified URLs for stores not listed here.",
    }
    OUT.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": snapshot["ok"],
        "stores": snapshot["stores"],
        "amazon_music_available": snapshot["amazon_music_available"],
        "output": str(OUT.relative_to(REPO_ROOT)),
    }, indent=2))
    return 0 if snapshot["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
