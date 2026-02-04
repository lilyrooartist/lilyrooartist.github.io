#!/usr/bin/env python3
"""Create a transparent 1080x1920 PNG overlay with title/caption/site.

We avoid ffmpeg drawtext (not available in current build).

Usage:
  source .venv-shorts/bin/activate
  python scripts/make_text_overlay.py --title "..." --caption "line1\nline2" --out /tmp/overlay.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def load_font(size: int) -> ImageFont.FreeTypeFont:
    # Try common macOS fonts
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size=size)
            except Exception:
                pass
    return ImageFont.load_default()


def draw_text_with_shadow(draw: ImageDraw.ImageDraw, xy, text, font, fill, shadow_fill=(0, 0, 0, 180), shadow_offset=(2, 2), spacing=10):
    x, y = xy
    sx, sy = shadow_offset
    draw.multiline_text((x + sx, y + sy), text, font=font, fill=shadow_fill, spacing=spacing)
    draw.multiline_text((x, y), text, font=font, fill=fill, spacing=spacing)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--caption", required=True)
    ap.add_argument("--site", default="lilyroo.com")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    W, H = 1080, 1920
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    title_font = load_font(52)
    cap_font = load_font(44)
    site_font = load_font(40)

    # Title + caption block
    left = 60
    draw_text_with_shadow(draw, (left, 560), args.title, title_font, fill=(255, 255, 255, 235))
    draw_text_with_shadow(draw, (left, 650), args.caption, cap_font, fill=(255, 255, 255, 240))

    # Site bottom center
    site_w = draw.textlength(args.site, font=site_font)
    draw_text_with_shadow(draw, ((W - site_w) / 2, 1840), args.site, site_font, fill=(255, 255, 255, 220))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)


if __name__ == "__main__":
    main()
