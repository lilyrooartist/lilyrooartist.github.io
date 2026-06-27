#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().with_name("apply_analog_myth_launch_links.py")
SPEC = importlib.util.spec_from_file_location("apply_analog_myth_launch_links", SCRIPT)
assert SPEC and SPEC.loader
launch_links = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(launch_links)


SPOTIFY_URL = "https://open.spotify.com/album/4Al5eYOqGFMKEES5fDWIfI"
APPLE_MUSIC_URL = "https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds/6777735762"
YOUTUBE_MUSIC_URL = "https://music.youtube.com/watch?v=vK0mDIW65o4"
BUILD_DATE = "Wed, 01 Jul 2026 04:05:06 GMT"


class AnalogMythLaunchLinksTest(unittest.TestCase):
    def spotify_response(self, body: str):
        class Response:
            status = 200

            def __enter__(self) -> "Response":
                return self

            def __exit__(self, *args: object) -> None:
                return None

            def read(self) -> bytes:
                return body.encode("utf-8")

        return Response()

    def spotify_oembed_response(self, title: str):
        return self.spotify_response(f'{{"title": "{title}"}}')

    def spotify_page_response(self, page_title: str):
        return self.spotify_response(f"<!doctype html><title>{page_title}</title>")

    def test_dry_run_targets_every_launch_surface(self) -> None:
        changed = launch_links.apply_updates(SPOTIFY_URL, APPLE_MUSIC_URL, YOUTUBE_MUSIC_URL, BUILD_DATE)
        self.assertEqual(set(changed), launch_links.EXPECTED_FILES)
        self.assertIn(SPOTIFY_URL, changed["index.html"])
        social_pack = changed["social/analog_myth_launch_posts.md"]
        self.assertIn(SPOTIFY_URL, social_pack)
        self.assertIn(f"Primary streaming CTA: {SPOTIFY_URL}", social_pack)
        self.assertIn("returns zero failures after the launch-link deploy", social_pack)
        self.assertNotIn("TBD_VERIFIED_SPOTIFY_ALBUM_URL", social_pack)
        self.assertNotIn("add the verified Spotify album URL", social_pack)
        self.assertIn(APPLE_MUSIC_URL, changed["press.html"])
        self.assertIn(YOUTUBE_MUSIC_URL, changed["analog-myth.html"])
        combined = "\n".join(changed.values())
        self.assertIn("Analog Myth is live", changed["index.html"])
        self.assertIn("the eight-song album that is live now", changed["podcasts/feed.xml"])
        self.assertIn(f"<lastBuildDate>{BUILD_DATE}</lastBuildDate>", changed["podcasts/feed.xml"])
        self.assertIn("<pubDate>Sat, 27 Jun 2026 14:35:00 GMT</pubDate>", changed["podcasts/feed.xml"])
        self.assertNotIn("arrives July 1", combined)
        self.assertNotIn("arriving July 1", combined)
        self.assertNotIn("Store links will be added", combined)
        self.assertNotIn("release propagates", combined)

    def test_missing_marker_fails_loudly(self) -> None:
        original = copy.copy(launch_links.ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            for relative in launch_links.EXPECTED_FILES:
                source = original / relative
                target = tmp_root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                content = source.read_text(encoding="utf-8")
                if relative == "press.html":
                    content = content.replace(launch_links.RELEASE_HUB_URL, "https://example.invalid/missing-marker")
                target.write_text(content, encoding="utf-8")

            with mock.patch.object(launch_links, "ROOT", tmp_root):
                with self.assertRaisesRegex(RuntimeError, "press.html"):
                    launch_links.apply_updates(SPOTIFY_URL, "", "")

    def test_invalid_spotify_url_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            launch_links.validate_url("Spotify URL", "https://example.com/not-spotify", r"^https://open\.spotify\.com/album/[A-Za-z0-9]+")

    def test_manual_spotify_url_title_validation_accepts_analog_myth(self) -> None:
        with mock.patch.object(launch_links.urllib.request, "urlopen", side_effect=[
            self.spotify_oembed_response("Analog Myth"),
            self.spotify_page_response("Analog Myth - Album by Lily Roo | Spotify"),
        ]):
            validation = launch_links.validate_manual_spotify_url(SPOTIFY_URL)

        self.assertTrue(validation["ok"])
        self.assertEqual(validation["title"], "Analog Myth")
        self.assertEqual(validation["page_title"], "Analog Myth - Album by Lily Roo | Spotify")
        self.assertEqual(validation["expected_artist"], "Lily Roo")

    def test_manual_spotify_url_title_validation_rejects_wrong_album(self) -> None:
        with mock.patch.object(launch_links.urllib.request, "urlopen", return_value=self.spotify_oembed_response("Another Album")):
            with self.assertRaisesRegex(ValueError, "expected Analog Myth, got Another Album"):
                launch_links.validate_manual_spotify_url(SPOTIFY_URL)

    def test_manual_spotify_url_artist_validation_rejects_wrong_artist(self) -> None:
        with mock.patch.object(launch_links.urllib.request, "urlopen", side_effect=[
            self.spotify_oembed_response("Analog Myth"),
            self.spotify_page_response("Analog Myth - Album by Another Artist | Spotify"),
        ]):
            with self.assertRaisesRegex(ValueError, "expected Lily Roo"):
                launch_links.validate_manual_spotify_url(SPOTIFY_URL)


if __name__ == "__main__":
    unittest.main()
