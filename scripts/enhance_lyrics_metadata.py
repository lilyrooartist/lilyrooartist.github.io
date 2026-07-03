#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LYRICS_DIR = ROOT / "lyrics"
SITE = "https://www.lilyroo.com"
ARTIST = {
    "@type": "MusicGroup",
    "name": "Lily Roo",
    "url": f"{SITE}/",
}

ALBUM_IMAGES = {
    "Analog Myth": "/assets/albums/analog-myth/art/03-analog-myth.jpg",
    "12 Dollars": "/assets/albums/twelve-dollars/art/album-cover.jpg",
    "Twelve Dollars": "/assets/albums/twelve-dollars/art/album-cover.jpg",
    "I Learned It All in Fifteen Seconds": "/assets/albums/i-learned-it-all-in-fifteen-seconds/art/album-cover.jpg",
}

TRACK_IMAGES = {
    "13": "/assets/albums/analog-myth/art/01-13.jpg",
    "Girls Camp": "/assets/albums/analog-myth/art/02-girls-camp.jpg",
    "Analog Myth": "/assets/albums/analog-myth/art/03-analog-myth.jpg",
    "Spilling the Tea": "/assets/albums/analog-myth/art/04-spilling-the-tea.jpg",
    "No Mortgage": "/assets/albums/analog-myth/art/05-no-mortgage.jpg",
    "Guards Down": "/assets/albums/analog-myth/art/06-guards-down.jpg",
    "Slow Walk": "/assets/albums/analog-myth/art/07-slow-walk.jpg",
    "The Power of Light": "/assets/albums/analog-myth/art/08-the-power-of-light.png",
    "I Learned It All in Fifteen Seconds": "/assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg",
    "Second Serve": "/assets/albums/i-learned-it-all-in-fifteen-seconds/art/02-second-serve.jpg",
    "My Second Room Has No Light Switch": "/assets/albums/i-learned-it-all-in-fifteen-seconds/art/03-my-second-room-has-no-light-switch.jpg",
    "The Importance of Bearing Witness": "/assets/albums/i-learned-it-all-in-fifteen-seconds/art/04-the-importance-of-bearing-witness.jpg",
    "Sliding Out of Bed": "/assets/albums/i-learned-it-all-in-fifteen-seconds/art/05-sliding-out-of-bed.jpg",
    "Dinner Table Tilt": "/assets/albums/i-learned-it-all-in-fifteen-seconds/art/06-dinner-table-tilt.jpg",
    "Yeah, I Play the Violin": "/assets/albums/i-learned-it-all-in-fifteen-seconds/art/07-yeah-i-play-the-violin.jpg",
    "More Difference (Reprise)": "/assets/albums/i-learned-it-all-in-fifteen-seconds/art/08-more-difference-reprise.jpg",
    "Brain Rot": "/assets/albums/twelve-dollars/art/01-brain-rot-youtube-thumbnail.jpg",
    "Every Pearl in Carmel": "/assets/albums/twelve-dollars/art/02-every-pearl-in-carmel-youtube-thumbnail.jpg",
    "The Other One's Charging": "/assets/albums/twelve-dollars/art/03-the-other-ones-charging-youtube-thumbnail.jpg",
    "Twelve Dollars": "/assets/albums/twelve-dollars/art/04-twelve-dollars.jpg",
    "William and Dander": "/assets/albums/twelve-dollars/art/05-william-and-dander-youtube-thumbnail.jpg",
    "Just Don't Talk About It": "/assets/albums/twelve-dollars/art/06-just-dont-talk-about-it-youtube-thumbnail.jpg",
    "Gluten Free Bread": "/assets/albums/twelve-dollars/art/07-gluten-free-bread-youtube-thumbnail.jpg",
    "When Lily Talks": "/assets/albums/twelve-dollars/art/08-when-lily-talks-youtube-thumbnail.jpg",
}

START = "  <!-- lyrics-discovery-meta:start -->"
END = "  <!-- lyrics-discovery-meta:end -->"


def text_match(pattern: str, source: str, default: str = "") -> str:
    match = re.search(pattern, source, re.S)
    if not match:
        return default
    return html.unescape(re.sub(r"\s+", " ", match.group(1)).strip())


def attr_escape(value: str) -> str:
    return html.escape(value, quote=True)


def absolute(path_or_url: str) -> str:
    if path_or_url.startswith("http"):
        return path_or_url
    return f"{SITE}{path_or_url}"


def remove_existing_block(source: str) -> str:
    pattern = re.compile(rf"\n?{re.escape(START)}.*?{re.escape(END)}\n?", re.S)
    return pattern.sub("\n", source)


def insert_after_description(source: str, block: str) -> str:
    source = remove_existing_block(source)
    match = re.search(r'  <meta name="description" content="[^"]*" />\n', source)
    if not match:
        raise RuntimeError("description meta tag not found")
    return source[:match.end()] + block + "\n" + source[match.end():]


def json_script(payload: dict) -> str:
    encoded = json.dumps(payload, indent=4, ensure_ascii=False)
    return "\n".join([
        '  <script type="application/ld+json">',
        *("    " + line if line else "" for line in encoded.splitlines()),
        "  </script>",
    ])


def song_block(path: Path, source: str) -> str:
    title = text_match(r"<h1>(.*?)</h1>", source)
    album = text_match(r'<p class="lyrics-album">(.*?)</p>', source)
    youtube = text_match(r'<a class="btn btn-ghost" href="([^"]+)"', source)
    if not title or not album:
        raise RuntimeError(f"missing song title or album in {path}")
    url = f"{SITE}/lyrics/{path.name}"
    image = absolute(TRACK_IMAGES.get(title) or ALBUM_IMAGES.get(album) or "/assets/avatar.png")
    description = f"Lyrics for {title} by Lily Roo from {album}."
    json_ld = {
        "@context": "https://schema.org",
        "@type": "MusicComposition",
        "name": title,
        "url": url,
        "inLanguage": "en",
        "lyricist": ARTIST,
        "composer": ARTIST,
        "byArtist": ARTIST,
        "isPartOf": {
            "@type": "MusicAlbum",
            "name": album,
            "byArtist": ARTIST,
        },
        "mainEntityOfPage": url,
        "image": image,
    }
    if youtube:
        json_ld["sameAs"] = [youtube]
    lines = [
        START,
        f'  <link rel="canonical" href="{attr_escape(url)}" />',
        '  <meta property="og:type" content="music.song" />',
        '  <meta property="og:site_name" content="Lily Roo" />',
        f'  <meta property="og:title" content="{attr_escape(title + " Lyrics - Lily Roo")}" />',
        f'  <meta property="og:description" content="{attr_escape(description)}" />',
        f'  <meta property="og:url" content="{attr_escape(url)}" />',
        f'  <meta property="og:image" content="{attr_escape(image)}" />',
        f'  <meta property="og:image:alt" content="{attr_escape(title + " art by Lily Roo")}" />',
        '  <meta name="twitter:card" content="summary_large_image" />',
        f'  <meta name="twitter:title" content="{attr_escape(title + " Lyrics - Lily Roo")}" />',
        f'  <meta name="twitter:description" content="{attr_escape(description)}" />',
        f'  <meta name="twitter:image" content="{attr_escape(image)}" />',
        json_script(json_ld),
        END,
    ]
    return "\n".join(lines)


def index_block(path: Path, source: str) -> str:
    url = f"{SITE}/lyrics/"
    image = absolute("/assets/albums/analog-myth/art/03-analog-myth.jpg")
    description = "Lily Roo lyric archive for Analog Myth, Twelve Dollars, and I Learned It All in Fifteen Seconds."
    links = re.findall(r'<li><a href="([^"]+)">(.*?)</a><span>(.*?)</span></li>', source)
    items = []
    for index, (href, raw_title, raw_album) in enumerate(links, start=1):
        title = html.unescape(raw_title)
        album = html.unescape(raw_album)
        items.append({
            "@type": "ListItem",
            "position": index,
            "url": f"{url}{href}",
            "name": title,
            "item": {
                "@type": "MusicComposition",
                "name": title,
                "byArtist": ARTIST,
                "isPartOf": {"@type": "MusicAlbum", "name": album},
            },
        })
    json_ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Lily Roo Lyrics",
        "description": description,
        "url": url,
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(items),
            "itemListElement": items,
        },
    }
    lines = [
        START,
        f'  <link rel="canonical" href="{url}" />',
        '  <meta property="og:type" content="website" />',
        '  <meta property="og:site_name" content="Lily Roo" />',
        '  <meta property="og:title" content="Lily Roo Lyrics" />',
        f'  <meta property="og:description" content="{description}" />',
        f'  <meta property="og:url" content="{url}" />',
        f'  <meta property="og:image" content="{image}" />',
        '  <meta property="og:image:alt" content="Analog Myth cover art by Lily Roo" />',
        '  <meta name="twitter:card" content="summary_large_image" />',
        '  <meta name="twitter:title" content="Lily Roo Lyrics" />',
        f'  <meta name="twitter:description" content="{description}" />',
        f'  <meta name="twitter:image" content="{image}" />',
        json_script(json_ld),
        END,
    ]
    return "\n".join(lines)


def main() -> int:
    changed = []
    for path in sorted(LYRICS_DIR.glob("*.html")):
        source = path.read_text(encoding="utf-8")
        block = index_block(path, source) if path.name == "index.html" else song_block(path, source)
        updated = insert_after_description(source, block)
        if updated != source:
            path.write_text(updated, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    print(json.dumps({"updated_count": len(changed), "updated": changed}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
