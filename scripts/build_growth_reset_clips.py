#!/usr/bin/env python3
"""Build the deterministic 9:16 Analog Myth growth-reset clip set.

The only runtime requirements are Python's standard library, ffmpeg/ffprobe,
and the repository's existing ``make_text_overlay.py`` helper (Pillow is
already used by that helper). Captions are rendered into a transparent PNG so
this works with ffmpeg builds that do not include drawtext or libass.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "data/growth_reset_clips.json"
DEFAULT_OUTPUT = ROOT / "assets/campaigns/analog-myth-growth-reset"
OVERLAY_HELPER = ROOT / "scripts/make_text_overlay.py"


def run(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, check=True)


def probe(path: Path) -> dict:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=index,codec_type,codec_name,width,height", "-of", "json", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def verify_clip(path: Path, expected: dict, fmt: dict) -> None:
    info = probe(path)
    streams = info.get("streams", [])
    video = next((stream for stream in streams if stream.get("codec_type") == "video"), None)
    audio = next((stream for stream in streams if stream.get("codec_type") == "audio"), None)
    duration = float(info.get("format", {}).get("duration", 0))
    errors = []
    if not video or video.get("codec_name") != fmt["video_codec"]:
        errors.append("video codec is not h264")
    if not video or video.get("width") != fmt["width"] or video.get("height") != fmt["height"]:
        errors.append(f"dimensions are not {fmt['width']}x{fmt['height']}")
    if not audio or audio.get("codec_name") != fmt["audio_codec"]:
        errors.append("audio codec is not aac")
    if not fmt["min_duration_seconds"] <= duration <= fmt["max_duration_seconds"]:
        errors.append(f"duration {duration:.3f}s is outside the allowed range")
    if abs(duration - float(expected["duration"])) > 0.35:
        errors.append(f"duration {duration:.3f}s differs from manifest {expected['duration']}s")
    if errors:
        raise RuntimeError(f"{path.name}: " + "; ".join(errors))
    print(f"verified {path.name}: {video['width']}x{video['height']} {duration:.3f}s h264/aac")


def build_clip(spec: dict, output_dir: Path, temp_dir: Path) -> Path:
    source = ROOT / spec["source"]
    if not source.exists():
        raise FileNotFoundError(source)
    overlay = temp_dir / f"{spec['id']}.png"
    run([
        sys.executable,
        str(OVERLAY_HELPER),
        "--title", spec["track"],
        "--caption", spec["caption"],
        "--site", "lilyroo.com",
        "--out", str(overlay),
    ])
    output = output_dir / f"{spec['id']}.mp4"
    # The moving crop keeps the source video active in a vertical frame while
    # retaining the original audio/video timing and starting on the song.
    video_filter = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920:x='(iw-1080)*(0.5+0.22*sin(t/3.0))':y=0,"
        "eq=contrast=1.05:brightness=-0.02:saturation=1.03,fps=30[base];"
        "[1:v]format=rgba[caption];[base][caption]overlay=0:0:format=auto[v]"
    )
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-ss", str(spec["start"]), "-t", str(spec["duration"]), "-i", str(source),
        "-loop", "1", "-t", str(spec["duration"]), "-i", str(overlay),
        "-filter_complex", video_filter,
        "-map", "[v]", "-map", "0:a:0", "-t", str(spec["duration"]),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart", str(output),
    ])
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    fmt = manifest["format"]
    clips = manifest["clips"]
    if len(clips) != 12:
        raise ValueError(f"expected 12 clips, found {len(clips)}")
    if not args.verify_only:
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            raise RuntimeError("ffmpeg and ffprobe must be installed")
        args.output_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="lilyroo-growth-reset-") as temp:
            for spec in clips:
                output = build_clip(spec, args.output_dir, Path(temp))
                verify_clip(output, spec, fmt)
    else:
        for spec in clips:
            verify_clip(args.output_dir / f"{spec['id']}.mp4", spec, fmt)
    print(f"built and verified {len(clips)} clips in {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
