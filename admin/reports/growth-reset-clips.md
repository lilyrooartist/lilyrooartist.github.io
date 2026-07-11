# Analog Myth Growth Reset Clips

Generated campaign set: 12 original vertical clips from the existing full videos for **Slow Walk**, **Spilling the Tea**, and **No Mortgage**. Each track has one lyric punch line, relatable situation, visual story, and Echo Thread setup/song payoff concept.

## Output

All files are under `assets/campaigns/analog-myth-growth-reset/`.

| Track | Concepts | Durations |
| --- | --- | --- |
| Slow Walk | lyric punch line, relatable situation, visual story, Echo Thread | 16s, 16s, 17s, 11s |
| Spilling the Tea | lyric punch line, relatable situation, visual story, Echo Thread | 15s, 16s, 18s, 20s |
| No Mortgage | lyric punch line, relatable situation, visual story, Echo Thread | 16s, 15s, 18s, 22s |

The exact source path, start offset, duration, concept, and caption text are the source of truth in `data/growth_reset_clips.json`.

## Build behavior

- `scripts/build_growth_reset_clips.py` is deterministic and requires only Python's standard library plus the existing `ffmpeg`, `ffprobe`, and `make_text_overlay.py` toolchain.
- The song starts at output time zero by seeking directly to each manifest start offset and mapping the source audio immediately.
- Full-video landscape material is converted to 1080x1920 with a time-based horizontal crop pan, preserving visible motion and avoiding static letterboxing.
- Captions are rendered as high-contrast, shadowed text into a transparent 1080x1920 overlay, then composited by ffmpeg.
- Outputs use H.264 video, AAC audio, 30 fps, yuv420p, and fast-start MP4 packaging.

## Verification

The builder verified every output after encoding, and the independent pass also completed successfully:

```sh
python3 scripts/build_growth_reset_clips.py --verify-only
```

Verified for all 12 clips: 1080x1920, H.264 video, AAC audio, and 11-22 second duration. The output directory contains exactly 12 MP4 files.
