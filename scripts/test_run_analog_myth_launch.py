#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import json
import shlex
import sys
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().with_name("run_analog_myth_launch.py")
SPEC = importlib.util.spec_from_file_location("run_analog_myth_launch", SCRIPT)
assert SPEC and SPEC.loader
launch_runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(launch_runner)


class AnalogMythLaunchRunnerTest(unittest.TestCase):
    def test_run_step_shell_quotes_logged_command(self) -> None:
        class FakeCompleted:
            returncode = 0
            stdout = ""
            stderr = ""

        with mock.patch.object(launch_runner.subprocess, "run", return_value=FakeCompleted()):
            step = launch_runner.run_step("quoted_command", [
                "python3",
                "script.py",
                "--youtube-music-url",
                "https://music.youtube.com/watch?v=AnalogMyth123&list=Launch",
            ])

        self.assertEqual(
            shlex.split(step["command"]),
            [
                "python3",
                "script.py",
                "--youtube-music-url",
                "https://music.youtube.com/watch?v=AnalogMyth123&list=Launch",
            ],
        )
        self.assertIn("'https://music.youtube.com/watch?v=AnalogMyth123&list=Launch'", step["command"])

    def test_apply_live_defers_live_final_readiness_until_after_deploy(self) -> None:
        steps: list[dict] = []

        def fake_run_step(name: str, command: list[str]) -> dict:
            step = {
                "name": name,
                "command": " ".join(command),
                "returncode": 0,
                "stderr": "",
            }
            if name == "dry_run_apply_links":
                step["stdout_summary"] = {"ok": True, "changed_files": ["index.html"]}
            steps.append(step)
            return step

        with (
            mock.patch.object(sys, "argv", ["run_analog_myth_launch.py", "--apply", "--live"]),
            mock.patch.object(launch_runner, "run_step", side_effect=fake_run_step),
            mock.patch.object(launch_runner, "store_summary", return_value={"checked": 4, "verified": 4, "all_public_links_verified": True}),
            mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            code = launch_runner.main()

        output = json.loads(stdout.getvalue())
        self.assertEqual(code, 0)
        self.assertTrue(output["launch_ready"])
        self.assertTrue(output["local_launch_ready"])
        self.assertFalse(output["public_launch_ready"])
        self.assertIn("GitHub Pages", output["public_launch_ready_reason"])
        verify_store = next(step for step in steps if step["name"] == "verify_store_links")
        self.assertIn("--snapshot-root output/launch-audit/store-verification", verify_store["command"])
        dry_run_apply = next(step for step in steps if step["name"] == "dry_run_apply_links")
        self.assertIn("--verification-root output/launch-audit/store-verification/analog-myth", dry_run_apply["command"])
        apply_links = next(step for step in steps if step["name"] == "apply_links")
        self.assertIn("--verification-root output/launch-audit/store-verification/analog-myth", apply_links["command"])
        final_readiness = next(step for step in steps if step["name"] == "final_readiness")
        self.assertEqual(final_readiness["command"], "python3 scripts/check_analog_myth_launch_readiness.py --require-store-links")
        self.assertEqual(output["post_deploy_live_check"], "python3 scripts/check_analog_myth_launch_readiness.py --require-store-links --live")
        self.assertEqual(output["next_commands"], ["python3 scripts/check_analog_myth_launch_readiness.py --require-store-links --live"])

    def test_apply_without_live_still_points_to_post_deploy_live_check(self) -> None:
        def fake_run_step(name: str, command: list[str]) -> dict:
            step = {
                "name": name,
                "command": " ".join(command),
                "returncode": 0,
                "stderr": "",
            }
            if name == "dry_run_apply_links":
                step["stdout_summary"] = {"ok": True, "changed_files": ["index.html"]}
            return step

        with (
            mock.patch.object(sys, "argv", ["run_analog_myth_launch.py", "--apply"]),
            mock.patch.object(launch_runner, "run_step", side_effect=fake_run_step),
            mock.patch.object(launch_runner, "store_summary", return_value={"checked": 4, "verified": 4, "all_public_links_verified": True}),
            mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            code = launch_runner.main()

        output = json.loads(stdout.getvalue())
        self.assertEqual(code, 0)
        self.assertTrue(output["launch_ready"])
        self.assertTrue(output["local_launch_ready"])
        self.assertFalse(output["public_launch_ready"])
        self.assertIn("GitHub Pages", output["public_launch_ready_reason"])
        self.assertEqual(output["post_deploy_live_check"], "python3 scripts/check_analog_myth_launch_readiness.py --require-store-links --live")
        self.assertEqual(output["next_commands"], ["python3 scripts/check_analog_myth_launch_readiness.py --require-store-links --live"])

    def test_manual_verified_urls_are_forwarded_and_preserved_in_next_command(self) -> None:
        steps: list[dict] = []
        spotify_url = "https://open.spotify.com/album/AnalogMythManual123"
        apple_music_url = "https://music.apple.com/us/album/analog-myth/123456789"
        youtube_music_url = "https://music.youtube.com/watch?v=AnalogMyth123"

        def fake_run_step(name: str, command: list[str]) -> dict:
            step = {
                "name": name,
                "command": " ".join(command),
                "returncode": 0,
                "stderr": "",
            }
            if name == "dry_run_apply_links":
                step["stdout_summary"] = {"ok": True, "changed_files": ["index.html"]}
            steps.append(step)
            return step

        with (
            mock.patch.object(sys, "argv", [
                "run_analog_myth_launch.py",
                "--live",
                "--spotify-url",
                spotify_url,
                "--apple-music-url",
                apple_music_url,
                "--youtube-music-url",
                youtube_music_url,
            ]),
            mock.patch.object(launch_runner, "run_step", side_effect=fake_run_step),
            mock.patch.object(launch_runner, "store_summary", return_value={"checked": 4, "verified": 0, "all_public_links_verified": False}),
            mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            code = launch_runner.main()

        output = json.loads(stdout.getvalue())
        self.assertEqual(code, 0)
        self.assertTrue(output["launch_ready"])
        self.assertEqual(output["manual_url_fallback_commands"], [])
        self.assertEqual(output["manual_url_args"], [
            "--spotify-url",
            spotify_url,
            "--apple-music-url",
            apple_music_url,
            "--youtube-music-url",
            youtube_music_url,
        ])
        dry_run_apply = next(step for step in steps if step["name"] == "dry_run_apply_links")
        self.assertIn(f"--spotify-url {spotify_url}", dry_run_apply["command"])
        self.assertIn(f"--apple-music-url {apple_music_url}", dry_run_apply["command"])
        self.assertIn(f"--youtube-music-url {youtube_music_url}", dry_run_apply["command"])
        next_command = output["next_commands"][0]
        self.assertIn("--apply --live", next_command)
        self.assertEqual(shlex.split(next_command), [
            "python3",
            "scripts/run_analog_myth_launch.py",
            "--apply",
            "--live",
            "--spotify-url",
            spotify_url,
            "--apple-music-url",
            apple_music_url,
            "--youtube-music-url",
            youtube_music_url,
        ])

    def test_prelaunch_output_includes_next_store_check_command(self) -> None:
        def fake_run_step(name: str, command: list[str]) -> dict:
            step = {
                "name": name,
                "command": " ".join(command),
                "returncode": 0,
                "stderr": "",
            }
            if name == "dry_run_apply_links":
                step["returncode"] = 1
                step["stdout_summary"] = {"ok": False, "error": "No verified Spotify album URL found."}
            return step

        with (
            mock.patch.object(sys, "argv", ["run_analog_myth_launch.py", "--allow-prelaunch", "--live"]),
            mock.patch.object(launch_runner, "run_step", side_effect=fake_run_step),
            mock.patch.object(launch_runner, "store_summary", return_value={"checked": 4, "verified": 0, "all_public_links_verified": False}),
            mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            code = launch_runner.main()

        output = json.loads(stdout.getvalue())
        self.assertEqual(code, 0)
        self.assertFalse(output["launch_ready"])
        self.assertFalse(output["public_launch_ready"])
        self.assertEqual(output["public_launch_ready_reason"], "No verified Spotify album URL found.")
        self.assertEqual(output["next_commands"], ["python3 scripts/run_analog_myth_launch.py --live"])
        self.assertEqual(output["manual_url_fallback_commands"], [
            "python3 scripts/run_analog_myth_launch.py --live --spotify-url VERIFIED_SPOTIFY_ALBUM_URL",
            "python3 scripts/run_analog_myth_launch.py --apply --live --spotify-url VERIFIED_SPOTIFY_ALBUM_URL",
        ])

    def test_apply_before_store_links_does_not_emit_post_deploy_check(self) -> None:
        def fake_run_step(name: str, command: list[str]) -> dict:
            step = {
                "name": name,
                "command": " ".join(command),
                "returncode": 0,
                "stderr": "",
            }
            if name == "dry_run_apply_links":
                step["returncode"] = 1
                step["stdout_summary"] = {"ok": False, "error": "No verified Spotify album URL found."}
            return step

        with (
            mock.patch.object(sys, "argv", ["run_analog_myth_launch.py", "--apply", "--allow-prelaunch", "--live"]),
            mock.patch.object(launch_runner, "run_step", side_effect=fake_run_step),
            mock.patch.object(launch_runner, "store_summary", return_value={"checked": 4, "verified": 0, "all_public_links_verified": False}),
            mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            code = launch_runner.main()

        output = json.loads(stdout.getvalue())
        self.assertEqual(code, 0)
        self.assertFalse(output["launch_ready"])
        self.assertFalse(output["applied"])
        self.assertFalse(output["public_launch_ready"])
        self.assertIsNone(output["post_deploy_live_check"])
        self.assertIn("No launch-link changes were applied", output["public_launch_ready_reason"])
        self.assertEqual(output["next_commands"], ["python3 scripts/run_analog_myth_launch.py --live"])


if __name__ == "__main__":
    unittest.main()
