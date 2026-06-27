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
    def test_dry_run_targets_every_launch_surface(self) -> None:
        changed = launch_links.apply_updates(SPOTIFY_URL, APPLE_MUSIC_URL, YOUTUBE_MUSIC_URL, BUILD_DATE)
        self.assertEqual(set(changed), launch_links.EXPECTED_FILES)
        self.assertIn(SPOTIFY_URL, changed["index.html"])
        self.assertIn(SPOTIFY_URL, changed["social/analog_myth_launch_posts.md"])
        self.assertNotIn("TBD_VERIFIED_SPOTIFY_ALBUM_URL", changed["social/analog_myth_launch_posts.md"])
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


if __name__ == "__main__":
    unittest.main()
