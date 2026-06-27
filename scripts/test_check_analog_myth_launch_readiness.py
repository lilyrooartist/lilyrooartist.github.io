#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().with_name("check_analog_myth_launch_readiness.py")
SPEC = importlib.util.spec_from_file_location("check_analog_myth_launch_readiness", SCRIPT)
assert SPEC and SPEC.loader
readiness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(readiness)


SPOTIFY_URL = "https://open.spotify.com/album/4Al5eYOqGFMKEES5fDWIfI"
APPLE_MUSIC_URL = "https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds/6777735762"
YOUTUBE_MUSIC_URL = "https://music.youtube.com/watch?v=vK0mDIW65o4"


def write_snapshot(root: Path, name: str, url: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / name).write_text(json.dumps({"ok": True, "release_url": url}), encoding="utf-8")


def write_pages(root: Path, *, omit_spotify_from: str = "") -> None:
    for relative in readiness.SPOTIFY_LINK_FILES:
        page = root / relative
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text("" if relative == omit_spotify_from else SPOTIFY_URL, encoding="utf-8")
    for relative in readiness.OPTIONAL_STORE_LINK_FILES:
        page = root / relative
        existing = page.read_text(encoding="utf-8") if page.exists() else ""
        page.write_text(f"{existing}\n{APPLE_MUSIC_URL}\n{YOUTUBE_MUSIC_URL}", encoding="utf-8")


def write_social_pack(path: Path, spotify_text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join([
            "Album page: https://www.lilyroo.com/analog-myth.html",
            "Podcast episode: https://www.lilyroo.com/podcasts/analog-myth.html",
            "Podcast RSS: https://www.lilyroo.com/podcasts/feed.xml",
            "Do not publish a Spotify-specific CTA until verified.",
            "python3 scripts/run_analog_myth_launch.py --apply --live",
            "post_deploy_live_check",
            "local_launch_ready",
            "public_launch_ready",
            "python3 scripts/check_analog_myth_launch_readiness.py --require-store-links --live",
            spotify_text,
        ]),
        encoding="utf-8",
    )


class AnalogMythReadinessTest(unittest.TestCase):
    def test_live_text_reads_utf8_response(self) -> None:
        class Response:
            status = 200

            def __enter__(self) -> "Response":
                return self

            def __exit__(self, *_args: object) -> None:
                return None

            def geturl(self) -> str:
                return "https://www.lilyroo.com/podcasts/feed.xml"

            def read(self) -> bytes:
                return "Echo Thread".encode("utf-8")

        with mock.patch.object(readiness.urllib.request, "urlopen", return_value=Response()):
            status, final_url, text = readiness.live_text("https://example.test/feed.xml", 5)
        self.assertEqual(status, 200)
        self.assertEqual(final_url, "https://www.lilyroo.com/podcasts/feed.xml")
        self.assertEqual(text, "Echo Thread")

    def test_live_text_reports_http_error(self) -> None:
        error = urllib.error.HTTPError("https://example.test/feed.xml", 404, "Not Found", hdrs=None, fp=None)
        with mock.patch.object(readiness.urllib.request, "urlopen", side_effect=error):
            status, final_url, text = readiness.live_text("https://example.test/feed.xml", 5)
        self.assertEqual(status, 404)
        self.assertEqual(final_url, "https://example.test/feed.xml")
        self.assertEqual(text, "")

    def test_itunes_duration_parser_accepts_common_formats(self) -> None:
        self.assertEqual(readiness.itunes_duration_seconds("12:11"), 731)
        self.assertEqual(readiness.itunes_duration_seconds("01:02:03"), 3723)
        self.assertEqual(readiness.itunes_duration_seconds("731"), 731)
        self.assertIsNone(readiness.itunes_duration_seconds("12 minutes"))

    def test_podcast_audio_duration_matches_feed_tolerance(self) -> None:
        actual_seconds = readiness.mp4_duration_seconds(readiness.PODCAST_AUDIO)
        feed_seconds = readiness.itunes_duration_seconds("12:11")
        self.assertIsNotNone(feed_seconds)
        self.assertGreater(actual_seconds, 0)
        self.assertLessEqual(abs(actual_seconds - feed_seconds), 2)

    def test_analog_myth_pretty_route_is_checked(self) -> None:
        self.assertIn("analog-myth/index.html", readiness.HTML_PAGES)
        self.assertIn("https://www.lilyroo.com/analog-myth/", readiness.LIVE_URLS)
        self.assertIn("https://www.lilyroo.com/analog-myth/", readiness.LIVE_HTML_MARKERS)

    def test_social_launch_pack_allows_prelaunch_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            pack = tmp_root / "social/analog_myth_launch_posts.md"
            write_social_pack(pack, "TBD_VERIFIED_SPOTIFY_ALBUM_URL")
            with mock.patch.object(readiness, "ROOT", tmp_root), mock.patch.object(readiness, "SOCIAL_LAUNCH_PACK", pack):
                results: list[dict] = []
                readiness.check_social_launch_pack(results, require_store_links=False)
        self.assertTrue(all(result["ok"] for result in results), results)

    def test_social_launch_pack_requires_verified_spotify_after_launch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            pack = tmp_root / "social/analog_myth_launch_posts.md"
            snapshot_root = tmp_root / "snapshots"
            write_social_pack(pack, SPOTIFY_URL)
            write_snapshot(snapshot_root, "spotify_release_snapshot.json", SPOTIFY_URL)
            with (
                mock.patch.object(readiness, "ROOT", tmp_root),
                mock.patch.object(readiness, "SOCIAL_LAUNCH_PACK", pack),
                mock.patch.object(readiness, "STORE_SNAPSHOT_ROOT", snapshot_root),
            ):
                results: list[dict] = []
                readiness.check_social_launch_pack(results, require_store_links=True)
        self.assertTrue(all(result["ok"] for result in results), results)

    def test_applied_store_links_pass_when_urls_are_in_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            snapshot_root = tmp_root / "snapshots"
            write_pages(tmp_root)
            write_snapshot(snapshot_root, "spotify_release_snapshot.json", SPOTIFY_URL)
            write_snapshot(snapshot_root, "apple_music_release_snapshot.json", APPLE_MUSIC_URL)
            write_snapshot(snapshot_root, "youtube_music_release_snapshot.json", YOUTUBE_MUSIC_URL)
            with mock.patch.object(readiness, "ROOT", tmp_root), mock.patch.object(readiness, "STORE_SNAPSHOT_ROOT", snapshot_root):
                results: list[dict] = []
                readiness.check_applied_store_links(results)
        self.assertTrue(all(result["ok"] for result in results), results)

    def test_applied_store_links_report_missing_spotify_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            snapshot_root = tmp_root / "snapshots"
            write_pages(tmp_root, omit_spotify_from="404.html")
            write_snapshot(snapshot_root, "spotify_release_snapshot.json", SPOTIFY_URL)
            with mock.patch.object(readiness, "ROOT", tmp_root), mock.patch.object(readiness, "STORE_SNAPSHOT_ROOT", snapshot_root):
                results: list[dict] = []
                readiness.check_applied_store_links(results)
        self.assertFalse(results[0]["ok"])
        self.assertIn("404.html", results[0]["detail"])


if __name__ == "__main__":
    unittest.main()
