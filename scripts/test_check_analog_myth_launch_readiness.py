#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
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


class AnalogMythReadinessTest(unittest.TestCase):
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
