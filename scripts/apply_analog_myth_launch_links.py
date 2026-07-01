#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from email.utils import format_datetime
import html
from html.parser import HTMLParser
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE_HUB_URL = "https://distrokid.com/hyperfollow/lilyroo/analog-myth"
YOUTUBE_PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0"
ALBUM_PAGE_URL = "https://www.lilyroo.com/analog-myth.html"
EXPECTED_SPOTIFY_TITLE = "Analog Myth"
EXPECTED_SPOTIFY_ARTIST = "Lily Roo"
EXPECTED_RELEASE_TITLE = "Analog Myth"
EXPECTED_ARTIST = "Lily Roo"
SPOTIFY_OEMBED_URL = "https://open.spotify.com/oembed"
KNOWN_ANALOG_MYTH_SPOTIFY_URLS = {
    "https://open.spotify.com/album/6Ujyp8tXa5UxheJJC2B6kL",
}
EXPECTED_FILES = {
    "index.html",
    "analog-myth.html",
    "music.html",
    "press.html",
    "podcasts/index.html",
    "podcasts/analog-myth.html",
    "podcasts/feed.xml",
    "404.html",
    "social/analog_myth_launch_posts.md",
}


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def snapshot_release_url(path: Path) -> str:
    payload = read_json(path)
    if payload.get("ok") and payload.get("release_url"):
        return str(payload["release_url"])
    return ""


def hyperfollow_release_url(verification_root: Path, store: str) -> str:
    payload = read_json(verification_root / "hyperfollow_store_links_snapshot.json")
    if not payload.get("ok"):
        return ""
    for link in payload.get("links") or []:
        if link.get("store") == store and link.get("url"):
            return str(link["url"])
    return ""


def validate_url(label: str, url: str, pattern: str) -> None:
    if url and not re.match(pattern, url):
        raise ValueError(f"{label} does not look like an expected URL: {url}")


def normalize_title(value: str) -> str:
    return " ".join(str(value or "").casefold().split())


def fetch_spotify_oembed_title(url: str) -> str:
    endpoint = SPOTIFY_OEMBED_URL + "?" + urllib.parse.urlencode({"url": url})
    request = urllib.request.Request(endpoint, headers={
        "Accept": "application/json",
        "User-Agent": "LilyRooAnalogMythLaunchLinks/1.0",
    })
    with urllib.request.urlopen(request, timeout=25) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return str(payload.get("title", ""))


class MetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.meta: dict[str, str] = {}
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "title":
            self._in_title = True
            return
        if tag.lower() != "meta":
            return
        values = {key.lower(): value or "" for key, value in attrs}
        key = values.get("property") or values.get("name")
        value = values.get("content")
        if key and value:
            self.meta[key] = html.unescape(value)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data


def fetch_html_metadata(url: str) -> dict[str, str]:
    request = urllib.request.Request(url, headers={
        "Accept": "text/html",
        "User-Agent": "LilyRooAnalogMythLaunchLinks/1.0",
    })
    with urllib.request.urlopen(request, timeout=25) as response:
        body = response.read().decode("utf-8", errors="replace")
    parser = MetaParser()
    parser.feed(body)
    return {
        "title": parser.title.strip(),
        "og_title": parser.meta.get("og:title", "").strip(),
        "description": (parser.meta.get("og:description") or parser.meta.get("description") or "").strip(),
    }


def validate_manual_spotify_url(url: str) -> dict:
    title = fetch_spotify_oembed_title(url)
    if normalize_title(title) != normalize_title(EXPECTED_SPOTIFY_TITLE):
        raise ValueError(f"Manual Spotify URL title mismatch: expected {EXPECTED_SPOTIFY_TITLE}, got {title or 'empty title'}.")
    page_title = fetch_html_metadata(url)["title"]
    expected_artist_phrase = f" by {EXPECTED_SPOTIFY_ARTIST} | Spotify"
    if expected_artist_phrase not in page_title:
        raise ValueError(
            f"Manual Spotify URL artist mismatch: expected {EXPECTED_SPOTIFY_ARTIST} in Spotify page title, got {page_title or 'empty title'}."
        )
    return {
        "ok": True,
        "source": "spotify-oembed-public",
        "title": title,
        "expected_title": EXPECTED_SPOTIFY_TITLE,
        "page_title": page_title,
        "expected_artist": EXPECTED_SPOTIFY_ARTIST,
    }


def spotify_album_id(url: str) -> str:
    match = re.search(r"open\.spotify\.com/album/([A-Za-z0-9]+)", url)
    return match.group(1) if match else ""


def write_manual_spotify_snapshot(verification_root: Path, spotify_url: str, validation: dict) -> dict:
    snapshot = {
        "ok": True,
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": "manual-spotify-url-plus-oembed",
        "release_url": spotify_url,
        "album_id": spotify_album_id(spotify_url),
        "title": validation.get("title", EXPECTED_SPOTIFY_TITLE),
        "query_artist": EXPECTED_ARTIST,
        "query_title": EXPECTED_RELEASE_TITLE,
        "manual_validation": validation,
        "candidate_urls": [spotify_url],
        "candidate_count": 1,
        "action_needed": "",
    }
    targets = [
        verification_root / "spotify_release_snapshot.json",
        ROOT / "data/store-verification/analog-myth/spotify_release_snapshot.json",
    ]
    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"written": [str(target.relative_to(ROOT)) for target in targets], "snapshot": snapshot}


def validate_manual_apple_music_url(url: str) -> dict:
    metadata = fetch_html_metadata(url)
    page_title = metadata["title"]
    normalized = normalize_title(page_title)
    if normalize_title(EXPECTED_RELEASE_TITLE) not in normalized or normalize_title(EXPECTED_ARTIST) not in normalized:
        raise ValueError(
            f"Manual Apple Music URL mismatch: expected {EXPECTED_RELEASE_TITLE} by {EXPECTED_ARTIST}, got {page_title or 'empty title'}."
        )
    return {
        "ok": True,
        "source": "apple-music-public-html",
        "page_title": page_title,
        "expected_title": EXPECTED_RELEASE_TITLE,
        "expected_artist": EXPECTED_ARTIST,
    }


def validate_manual_youtube_music_url(url: str) -> dict:
    metadata = fetch_html_metadata(url)
    public_title = metadata["og_title"] or metadata["title"]
    description = metadata["description"]
    normalized_title = normalize_title(public_title)
    valid_titles = {
        normalize_title(EXPECTED_RELEASE_TITLE),
        normalize_title(f"{EXPECTED_RELEASE_TITLE} - {EXPECTED_ARTIST}"),
    }
    artist_seen = normalize_title(EXPECTED_ARTIST) in normalize_title(description) or normalize_title(EXPECTED_ARTIST) in normalized_title
    if normalized_title not in valid_titles or not artist_seen:
        raise ValueError(
            f"Manual YouTube Music URL mismatch: expected {EXPECTED_RELEASE_TITLE} by {EXPECTED_ARTIST}, got title {public_title or 'empty title'}."
        )
    return {
        "ok": True,
        "source": "youtube-music-public-html",
        "public_title": public_title,
        "description_mentions_artist": artist_seen,
        "expected_title": EXPECTED_RELEASE_TITLE,
        "expected_artist": EXPECTED_ARTIST,
    }


def html_store_buttons(spotify_url: str, apple_music_url: str, youtube_music_url: str, *, solid_spotify: bool = False) -> str:
    spotify_class = "btn btn-solid" if solid_spotify else "btn btn-ghost"
    buttons = [
        f'<a class="{spotify_class}" href="{spotify_url}" target="_blank" rel="noopener">Listen on Spotify</a>',
    ]
    if apple_music_url:
        buttons.append(f'<a class="btn btn-ghost" href="{apple_music_url}" target="_blank" rel="noopener">Apple Music</a>')
    if youtube_music_url:
        buttons.append(f'<a class="btn btn-ghost" href="{youtube_music_url}" target="_blank" rel="noopener">YouTube Music</a>')
    return "\n".join(buttons)


def same_as_block(spotify_url: str, apple_music_url: str, youtube_music_url: str) -> str:
    urls = [RELEASE_HUB_URL, spotify_url]
    if apple_music_url:
        urls.append(apple_music_url)
    if youtube_music_url:
        urls.append(youtube_music_url)
    urls.append(YOUTUBE_PLAYLIST_URL)
    rendered = ",\n".join(f'        "{url}"' for url in urls)
    return f'"sameAs": [\n{rendered}\n      ]'


def add_optional_button(anchor: str, button_html: str, text: str) -> str:
    if not button_html or button_html in text:
        return text
    return text.replace(anchor, f"{button_html}\n{anchor}", 1)


def replace_all(text: str, replacements: list[tuple[str, str]]) -> str:
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def rfc2822_now() -> str:
    return format_datetime(datetime.now(timezone.utc), usegmt=True)


def update_index(text: str, spotify_url: str, apple_music_url: str, youtube_music_url: str) -> str:
    text = replace_all(text, [
        (
            'content="Analog Myth, the new Lily Roo album, arrives July 1, 2026. Listen to the podcast and watch the remastered album playlist now."',
            'content="Analog Myth, the new Lily Roo album, is live now. Listen on Spotify, hear the podcast, and watch the remastered album playlist."',
        ),
        (
            'content="Analog Myth arrives July 1, 2026. Listen to the podcast and watch the remastered album playlist now."',
            'content="Analog Myth is live now. Listen on Spotify, hear the podcast, and watch the remastered album playlist."',
        ),
        ("<h2>Analog Myth arrives July 1</h2>", "<h2>Analog Myth is live</h2>"),
    ])
    text = text.replace(
        '"sameAs": [\n        "https://distrokid.com/hyperfollow/lilyroo/analog-myth",\n        "https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0"\n      ]',
        same_as_block(spotify_url, apple_music_url, youtube_music_url),
    )
    text = text.replace(
        f'<a href="{RELEASE_HUB_URL}" target="_blank" rel="noopener" aria-label="Open the Analog Myth release hub">',
        f'<a href="{spotify_url}" target="_blank" rel="noopener" aria-label="Listen to Analog Myth on Spotify">',
    )
    text = text.replace(
        "DistroKid delivered the album to stores on June 8. The release date is July 1, 2026; until store links propagate, the release hub and remastered YouTube playlist carry the signal.",
        "Analog Myth is live on July 1, 2026. Spotify is the primary listening link, with the remastered YouTube playlist still available for the full visual sequence.",
    )
    text = text.replace(
        f'<a class="btn btn-ghost" href="{RELEASE_HUB_URL}" target="_blank" rel="noopener">Release Hub</a>',
        f'<a class="btn btn-ghost" href="{spotify_url}" target="_blank" rel="noopener">Listen on Spotify</a>',
        1,
    )
    if apple_music_url:
        text = add_optional_button(
            f'          <a class="btn btn-ghost" href="{YOUTUBE_PLAYLIST_URL}" target="_blank" rel="noopener">Watch Playlist</a>',
            f'          <a class="btn btn-ghost" href="{apple_music_url}" target="_blank" rel="noopener">Apple Music</a>',
            text,
        )
    if youtube_music_url:
        text = add_optional_button(
            f'          <a class="btn btn-ghost" href="{YOUTUBE_PLAYLIST_URL}" target="_blank" rel="noopener">Watch Playlist</a>',
            f'          <a class="btn btn-ghost" href="{youtube_music_url}" target="_blank" rel="noopener">YouTube Music</a>',
            text,
        )
    return text


def update_album_page(text: str, spotify_url: str, apple_music_url: str, youtube_music_url: str) -> str:
    text = text.replace(
        'content="Analog Myth, the eight-track Lily Roo album, arrives July 1, 2026. Listen through the release hub, album playlist, and Echo Thread podcast."',
        'content="Analog Myth, the eight-track Lily Roo album, is live now. Listen on Spotify, watch the album playlist, and hear the Echo Thread podcast."',
    )
    text = text.replace(
        '"sameAs": [\n        "https://distrokid.com/hyperfollow/lilyroo/analog-myth",\n        "https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0"\n      ]',
        same_as_block(spotify_url, apple_music_url, youtube_music_url),
    )
    text = text.replace(
        f'<a class="btn btn-solid" href="{RELEASE_HUB_URL}" target="_blank" rel="noopener">Release Hub</a>',
        f'<a class="btn btn-solid" href="{spotify_url}" target="_blank" rel="noopener">Listen on Spotify</a>',
    )
    store_links = html_store_buttons(spotify_url, apple_music_url, youtube_music_url)
    prelaunch_copy = """        <p>
          The title track is public now on YouTube. Store links will be added here
          after the July 1 release propagates.
        </p>"""
    launch_copy = """        <p>
          Analog Myth is live on July 1. Start with Spotify, or keep the title-track video and full remastered playlist close by.
        </p>"""
    block = f'        <div class="panel-actions launch-store-links">\n          {store_links.replace(chr(10), chr(10) + "          ")}\n        </div>\n'
    if "launch-store-links" not in text:
        text = text.replace(prelaunch_copy, f"{launch_copy}\n{block}", 1)
    else:
        anchor = f'          <a class="btn btn-ghost" href="{spotify_url}" target="_blank" rel="noopener">Listen on Spotify</a>'
        if apple_music_url:
            text = add_optional_button(anchor, f'          <a class="btn btn-ghost" href="{apple_music_url}" target="_blank" rel="noopener">Apple Music</a>', text)
        if youtube_music_url:
            text = add_optional_button(anchor, f'          <a class="btn btn-ghost" href="{youtube_music_url}" target="_blank" rel="noopener">YouTube Music</a>', text)
    return text


def update_music(text: str, spotify_url: str, apple_music_url: str, youtube_music_url: str) -> str:
    text = text.replace(
        '<p class="album-sub">Album launch: July 1, 2026</p>',
        '<p class="album-sub">Album released: July 1, 2026</p>',
    )
    text = text.replace(
        f'<a class="btn btn-ghost" href="{RELEASE_HUB_URL}" target="_blank" rel="noreferrer">Release hub</a>',
        f'<a class="btn btn-ghost" href="{spotify_url}" target="_blank" rel="noreferrer">Listen on Spotify</a>',
    )
    anchor = f'            <a class="btn btn-ghost" href="{YOUTUBE_PLAYLIST_URL}" target="_blank" rel="noreferrer">Full album playlist</a>'
    if apple_music_url:
        text = add_optional_button(anchor, f'            <a class="btn btn-ghost" href="{apple_music_url}" target="_blank" rel="noreferrer">Apple Music</a>', text)
    if youtube_music_url:
        text = add_optional_button(anchor, f'            <a class="btn btn-ghost" href="{youtube_music_url}" target="_blank" rel="noreferrer">YouTube Music</a>', text)
    return text


def update_press(text: str, spotify_url: str, apple_music_url: str, youtube_music_url: str) -> str:
    text = text.replace(
        f'<a class="btn" href="{RELEASE_HUB_URL}" target="_blank" rel="noreferrer">Analog Myth release hub</a>',
        f'<a class="btn" href="{spotify_url}" target="_blank" rel="noreferrer">Analog Myth on Spotify</a>',
    )
    anchor = f'        <a class="btn" href="{YOUTUBE_PLAYLIST_URL}" target="_blank" rel="noreferrer">Analog Myth playlist</a>'
    if apple_music_url:
        text = add_optional_button(anchor, f'        <a class="btn" href="{apple_music_url}" target="_blank" rel="noreferrer">Analog Myth on Apple Music</a>', text)
    if youtube_music_url:
        text = add_optional_button(anchor, f'        <a class="btn" href="{youtube_music_url}" target="_blank" rel="noreferrer">Analog Myth on YouTube Music</a>', text)
    return text


def update_podcast_pages(text: str, spotify_url: str) -> str:
    text = replace_all(text, [
        (
            "Jasper Fields sits down with Lily Roo for a track-by-track talk-through of Analog Myth, the eight-song album arriving July 1, 2026.",
            "Jasper Fields sits down with Lily Roo for a full album play-through of Analog Myth, with the songs in the room.",
        ),
        (
            "<em>Analog Myth</em>, the eight-song album arriving July 1, 2026.",
            "<em>Analog Myth</em>, with the songs in the room.",
        ),
        (
            "album arriving July 1, 2026.",
            "album that is live now.",
        ),
    ])
    return text.replace(
        f'<a class="btn btn-ghost" href="{RELEASE_HUB_URL}" target="_blank" rel="noopener">Release Hub</a>',
        f'<a class="btn btn-ghost" href="{spotify_url}" target="_blank" rel="noopener">Listen on Spotify</a>',
    )


def update_feed(text: str, spotify_url: str, apple_music_url: str, youtube_music_url: str, build_date: str | None = None) -> str:
    text = replace_all(text, [
        (
            "Jasper Fields sits down with Lily Roo for a track-by-track talk-through of Analog Myth, the eight-song album arriving July 1, 2026.",
            "Jasper Fields sits down with Lily Roo for a full album play-through of Analog Myth, with the songs in the room.",
        ),
        (
            "Jasper Fields sits down with Lily Roo for a track-by-track talk-through of <em>Analog Myth</em>, the eight-song album arriving July 1, 2026.",
            "Jasper Fields sits down with Lily Roo for a full album play-through of <em>Analog Myth</em>, with the songs in the room.",
        ),
    ])
    text = re.sub(
        r"<lastBuildDate>[^<]+</lastBuildDate>",
        f"<lastBuildDate>{build_date or rfc2822_now()}</lastBuildDate>",
        text,
        count=1,
    )
    if "Spotify: <a" in text:
        return text
    lines = [f'        <p>Spotify: <a href="{spotify_url}">{spotify_url}</a></p>']
    if apple_music_url:
        lines.append(f'        <p>Apple Music: <a href="{apple_music_url}">{apple_music_url}</a></p>')
    if youtube_music_url:
        lines.append(f'        <p>YouTube Music: <a href="{youtube_music_url}">{youtube_music_url}</a></p>')
    return text.replace(
        f'        <p>Album page: <a href="{ALBUM_PAGE_URL}">{ALBUM_PAGE_URL}</a></p>',
        f'        <p>Album page: <a href="{ALBUM_PAGE_URL}">{ALBUM_PAGE_URL}</a></p>\n' + "\n".join(lines),
    )


def update_404(text: str, spotify_url: str) -> str:
    return text.replace(
        f'<a class="btn btn-ghost" href="{RELEASE_HUB_URL}" target="_blank" rel="noopener">Release Hub</a>',
        f'<a class="btn btn-ghost" href="{spotify_url}" target="_blank" rel="noopener">Listen on Spotify</a>',
    )


def update_social_launch_pack(text: str, spotify_url: str) -> str:
    text = replace_all(text, [
        (
            "Primary streaming CTA: add the verified Spotify album URL with `python3 scripts/run_analog_myth_launch.py --apply --live`; publish Spotify-specific copy only after the post-deploy live check passes.",
            f"Primary streaming CTA: {spotify_url}",
        ),
        (
            "Use these only after the verified Spotify URL replaces `TBD_VERIFIED_SPOTIFY_ALBUM_URL`.",
            "Use these after the verified Spotify URL has been applied by the launch runner.",
        ),
        (
            "Analog Myth goes live July 1",
            "Analog Myth is live",
        ),
        (
            "Analog Myth arrives July 1",
            "Analog Myth is live",
        ),
        (
            "Analog Myth is live July 1",
            "Analog Myth is live",
        ),
        (
            "goes live July 1",
            "is live",
        ),
        (
            "arrives July 1",
            "is live",
        ),
        (
            "8. Replace `TBD_VERIFIED_SPOTIFY_ALBUM_URL` in any copied captions before using Spotify-specific variants.",
            f"8. Confirm Spotify-specific variants contain `{spotify_url}` before posting.",
        ),
    ])
    return text.replace("TBD_VERIFIED_SPOTIFY_ALBUM_URL", spotify_url)


def apply_updates(spotify_url: str, apple_music_url: str, youtube_music_url: str, build_date: str | None = None) -> dict[str, str]:
    updates = {
        "index.html": update_index,
        "analog-myth.html": update_album_page,
        "music.html": update_music,
        "press.html": update_press,
        "podcasts/index.html": lambda text, spotify, apple, youtube: update_podcast_pages(text, spotify),
        "podcasts/analog-myth.html": lambda text, spotify, apple, youtube: update_podcast_pages(text, spotify),
        "podcasts/feed.xml": lambda text, spotify, apple, youtube: update_feed(text, spotify, apple, youtube, build_date),
        "404.html": lambda text, spotify, apple, youtube: update_404(text, spotify),
        "social/analog_myth_launch_posts.md": lambda text, spotify, apple, youtube: update_social_launch_pack(text, spotify),
    }
    changed = {}
    missing = []
    for relative, updater in updates.items():
        path = ROOT / relative
        before = path.read_text(encoding="utf-8")
        after = updater(before, spotify_url, apple_music_url, youtube_music_url)
        if spotify_url not in after:
            for known_url in KNOWN_ANALOG_MYTH_SPOTIFY_URLS:
                after = after.replace(known_url, spotify_url)
            if before != after:
                after = updater(after, spotify_url, apple_music_url, youtube_music_url)
        if before != after:
            changed[relative] = after
        elif spotify_url not in before:
            missing.append(relative)
    if missing:
        raise RuntimeError("No launch-link update marker found in: " + ", ".join(sorted(missing)))
    if set(updates) != EXPECTED_FILES:
        raise RuntimeError("Launch updater file map does not match EXPECTED_FILES.")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply verified Analog Myth launch store links to public site surfaces.")
    parser.add_argument("--spotify-url", default="", help="Verified Spotify album URL. Required unless the verification snapshot has one.")
    parser.add_argument("--apple-music-url", default="", help="Verified Apple Music album URL.")
    parser.add_argument("--youtube-music-url", default="", help="Verified YouTube Music album URL.")
    parser.add_argument("--verification-root", default="output/launch-audit/store-verification/analog-myth", help="Directory containing per-store verification snapshots.")
    parser.add_argument("--apply", action="store_true", help="Write the launch URL changes. Omit for a dry run.")
    args = parser.parse_args()

    verification_root = Path(args.verification_root)
    if not verification_root.is_absolute():
        verification_root = ROOT / verification_root

    manual_spotify_url = bool(args.spotify_url)
    manual_apple_music_url = bool(args.apple_music_url)
    manual_youtube_music_url = bool(args.youtube_music_url)
    spotify_url = (
        args.spotify_url
        or snapshot_release_url(verification_root / "spotify_release_snapshot.json")
        or hyperfollow_release_url(verification_root, "spotify")
    )
    apple_music_url = args.apple_music_url or snapshot_release_url(verification_root / "apple_music_release_snapshot.json")
    youtube_music_url = args.youtube_music_url or snapshot_release_url(verification_root / "youtube_music_release_snapshot.json")

    validate_url("Spotify URL", spotify_url, r"^https://open\.spotify\.com/album/[A-Za-z0-9]+")
    validate_url("Apple Music URL", apple_music_url, r"^https://music\.apple\.com/.+/album/.+")
    validate_url("YouTube Music URL", youtube_music_url, r"^https://music\.youtube\.com/watch\?v=[A-Za-z0-9_-]+")
    if not spotify_url:
        print(json.dumps({
            "ok": False,
            "error": "No verified Spotify album URL found. Re-run store verification after the July 1 release is public, or pass --spotify-url.",
            "verification_root": str(verification_root.relative_to(ROOT) if verification_root.is_relative_to(ROOT) else verification_root),
        }, indent=2))
        return 1
    manual_spotify_validation = validate_manual_spotify_url(spotify_url) if manual_spotify_url else {}
    manual_apple_music_validation = validate_manual_apple_music_url(apple_music_url) if manual_apple_music_url else {}
    manual_youtube_music_validation = validate_manual_youtube_music_url(youtube_music_url) if manual_youtube_music_url else {}

    changed = apply_updates(spotify_url, apple_music_url, youtube_music_url)
    manual_spotify_snapshot = {}
    if args.apply:
        for relative, content in changed.items():
            (ROOT / relative).write_text(content, encoding="utf-8")
        if manual_spotify_url:
            manual_spotify_snapshot = write_manual_spotify_snapshot(verification_root, spotify_url, manual_spotify_validation)
    print(json.dumps({
        "ok": True,
        "mode": "apply" if args.apply else "dry-run",
        "spotify_url": spotify_url,
        "apple_music_url": apple_music_url,
        "youtube_music_url": youtube_music_url,
        "manual_spotify_validation": manual_spotify_validation,
        "manual_spotify_snapshot": manual_spotify_snapshot,
        "manual_apple_music_validation": manual_apple_music_validation,
        "manual_youtube_music_validation": manual_youtube_music_validation,
        "changed_files": sorted(changed),
    }, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2), file=sys.stderr)
        raise SystemExit(2)
