#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from email.utils import format_datetime
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE_HUB_URL = "https://distrokid.com/hyperfollow/lilyroo/analog-myth"
YOUTUBE_PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLit3sD3SUfXUJlhtullPqTPWQdTcS1fy0"
ALBUM_PAGE_URL = "https://www.lilyroo.com/analog-myth.html"
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


def validate_url(label: str, url: str, pattern: str) -> None:
    if url and not re.match(pattern, url):
        raise ValueError(f"{label} does not look like an expected URL: {url}")


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
            "Jasper Fields sits down with Lily Roo for a track-by-track talk-through of Analog Myth, the eight-song album that is live now.",
        ),
        (
            "<em>Analog Myth</em>, the eight-song album arriving July 1, 2026.",
            "<em>Analog Myth</em>, the eight-song album that is live now.",
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
            "Jasper Fields sits down with Lily Roo for a track-by-track talk-through of Analog Myth, the eight-song album that is live now.",
        ),
        (
            "Jasper Fields sits down with Lily Roo for a track-by-track talk-through of <em>Analog Myth</em>, the eight-song album arriving July 1, 2026.",
            "Jasper Fields sits down with Lily Roo for a track-by-track talk-through of <em>Analog Myth</em>, the eight-song album that is live now.",
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

    spotify_url = args.spotify_url or snapshot_release_url(verification_root / "spotify_release_snapshot.json")
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

    changed = apply_updates(spotify_url, apple_music_url, youtube_music_url)
    if args.apply:
        for relative, content in changed.items():
            (ROOT / relative).write_text(content, encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "mode": "apply" if args.apply else "dry-run",
        "spotify_url": spotify_url,
        "apple_music_url": apple_music_url,
        "youtube_music_url": youtube_music_url,
        "changed_files": sorted(changed),
    }, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2), file=sys.stderr)
        raise SystemExit(2)
