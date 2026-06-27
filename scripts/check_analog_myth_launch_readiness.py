#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_BASE_URL = "https://www.lilyroo.com"
RELEASE_HUB_URL = "https://distrokid.com/hyperfollow/lilyroo/analog-myth"
PODCAST_AUDIO = ROOT / "assets/podcasts/analog-myth/analog-myth-the-clock-cannot-explain-this.m4a"
PODCAST_POSTER = ROOT / "assets/podcasts/analog-myth/analog-myth-podcast-poster.jpg"
PODCAST_FEED_ART = ROOT / "assets/podcasts/analog-myth/analog-myth-podcast-directory-art-3000.jpg"
ALBUM_COVER = ROOT / "assets/albums/analog-myth/art/03-analog-myth.jpg"
STORE_RUN = ROOT / "output/launch-audit/analog-myth-store-verification-run.json"
STORE_SNAPSHOT_ROOT = ROOT / "output/launch-audit/store-verification/analog-myth"
ITUNES_NS = "{http://www.itunes.com/dtds/podcast-1.0.dtd}"

HTML_PAGES = [
    "index.html",
    "album.html",
    "album/index.html",
    "analog-myth.html",
    "music.html",
    "press.html",
    "podcast.html",
    "podcast/index.html",
    "podcasts/index.html",
    "podcasts/analog-myth.html",
    "404.html",
]
XML_FILES = ["sitemap.xml", "podcasts/feed.xml"]
JSON_LD_REQUIRED = {"index.html", "analog-myth.html", "podcasts/index.html", "podcasts/analog-myth.html"}
LIVE_URLS = [
    "https://www.lilyroo.com/",
    "https://www.lilyroo.com/album.html",
    "https://www.lilyroo.com/album/",
    "https://www.lilyroo.com/analog-myth.html",
    "https://www.lilyroo.com/music.html",
    "https://www.lilyroo.com/press.html",
    "https://www.lilyroo.com/podcast.html",
    "https://www.lilyroo.com/podcast/",
    "https://www.lilyroo.com/podcasts/",
    "https://www.lilyroo.com/podcasts/analog-myth.html",
    "https://www.lilyroo.com/podcasts/feed.xml",
]
LIVE_HTML_MARKERS = {
    "https://www.lilyroo.com/": (
        ("Homepage launch stylesheet", "style.css?v=20260627-analog-myth-launch"),
        ("Homepage album CTA", "/analog-myth.html"),
        ("Homepage podcast CTA", "/podcasts/analog-myth.html"),
        ("Homepage podcast audio", "assets/podcasts/analog-myth/analog-myth-the-clock-cannot-explain-this.m4a"),
    ),
    "https://www.lilyroo.com/analog-myth.html": (
        ("Album page launch stylesheet", "style.css?v=20260627-analog-myth-launch"),
        ("Album page release hub", "https://distrokid.com/hyperfollow/lilyroo/analog-myth"),
        ("Album page podcast CTA", "/podcasts/analog-myth.html"),
        ("Album page podcast audio", "assets/podcasts/analog-myth/analog-myth-the-clock-cannot-explain-this.m4a"),
    ),
    "https://www.lilyroo.com/podcasts/": (
        ("Podcast hub title", "Echo Thread Podcast"),
        ("Podcast hub RSS link", "/podcasts/feed.xml"),
        ("Podcast hub episode link", "/podcasts/analog-myth.html"),
        ("Podcast hub directory art metadata", "analog-myth-podcast-directory-art-3000.jpg"),
    ),
    "https://www.lilyroo.com/podcasts/analog-myth.html": (
        ("Podcast episode JSON-LD type", '"@type": "PodcastEpisode"'),
        ("Podcast episode media URL", "analog-myth-the-clock-cannot-explain-this.m4a"),
        ("Podcast episode RSS link", "/podcasts/feed.xml"),
        ("Podcast episode directory art metadata", "analog-myth-podcast-directory-art-3000.jpg"),
    ),
}
LIVE_ASSETS = [
    (
        "Live podcast audio",
        "https://www.lilyroo.com/assets/podcasts/analog-myth/analog-myth-the-clock-cannot-explain-this.m4a",
        PODCAST_AUDIO,
        "audio/",
    ),
    (
        "Live podcast poster",
        "https://www.lilyroo.com/assets/podcasts/analog-myth/analog-myth-podcast-poster.jpg",
        PODCAST_POSTER,
        "image/",
    ),
    (
        "Live podcast feed art",
        "https://www.lilyroo.com/assets/podcasts/analog-myth/analog-myth-podcast-directory-art-3000.jpg",
        PODCAST_FEED_ART,
        "image/",
    ),
    (
        "Live Analog Myth cover",
        "https://www.lilyroo.com/assets/albums/analog-myth/art/03-analog-myth.jpg",
        ALBUM_COVER,
        "image/",
    ),
]
REQUIRED_SITEMAP_URLS = {
    "https://www.lilyroo.com/",
    "https://www.lilyroo.com/analog-myth.html",
    "https://www.lilyroo.com/music.html",
    "https://www.lilyroo.com/press.html",
    "https://www.lilyroo.com/podcasts/",
    "https://www.lilyroo.com/podcasts/analog-myth.html",
    "https://www.lilyroo.com/podcasts/feed.xml",
}
PRELAUNCH_PHRASES = (
    "arrives July 1",
    "arriving July 1",
    "Store links will be added",
    "release propagates",
)
SPOTIFY_LINK_FILES = [
    "index.html",
    "analog-myth.html",
    "music.html",
    "press.html",
    "podcasts/index.html",
    "podcasts/analog-myth.html",
    "podcasts/feed.xml",
    "404.html",
]
OPTIONAL_STORE_LINK_FILES = [
    "index.html",
    "analog-myth.html",
    "music.html",
    "press.html",
    "podcasts/feed.xml",
]


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[str, str, str]] = []
        self.scripts: list[tuple[str, str]] = []
        self._script_type = ""
        self._script_chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key: value or "" for key, value in attrs}
        for key in ("href", "src"):
            value = attr_map.get(key, "")
            if value:
                self.refs.append((tag, key, value))
        if tag == "script":
            self._script_type = attr_map.get("type", "")
            self._script_chunks = []

    def handle_data(self, data: str) -> None:
        if self._script_type:
            self._script_chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._script_type:
            self.scripts.append((self._script_type, "".join(self._script_chunks).strip()))
            self._script_type = ""
            self._script_chunks = []


def add_result(results: list[dict], name: str, ok: bool, detail: str = "") -> None:
    results.append({"name": name, "ok": ok, "detail": detail})


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def verified_release_url(snapshot_name: str) -> str:
    payload = read_json(STORE_SNAPSHOT_ROOT / snapshot_name)
    if payload.get("ok") and payload.get("release_url"):
        return str(payload["release_url"])
    return ""


def jpeg_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    index = 2
    while index < len(data):
        if data[index] != 0xFF:
            index += 1
            continue
        marker = data[index + 1]
        index += 2
        if marker in {0xD8, 0xD9}:
            continue
        if index + 2 > len(data):
            break
        segment_length = int.from_bytes(data[index:index + 2], "big")
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            height = int.from_bytes(data[index + 3:index + 5], "big")
            width = int.from_bytes(data[index + 5:index + 7], "big")
            return width, height
        index += segment_length
    return 0, 0


def itunes_duration_seconds(value: str) -> int | None:
    if not value:
        return None
    parts = value.strip().split(":")
    if not all(part.isdigit() for part in parts):
        return None
    numbers = [int(part) for part in parts]
    if len(numbers) == 1:
        return numbers[0]
    if len(numbers) == 2:
        minutes, seconds = numbers
        return minutes * 60 + seconds
    if len(numbers) == 3:
        hours, minutes, seconds = numbers
        return hours * 3600 + minutes * 60 + seconds
    return None


def mp4_duration_seconds(path: Path) -> float:
    data = path.read_bytes()
    marker = data.find(b"mvhd")
    if marker < 4:
        return 0.0
    version = data[marker + 4]
    if version == 0:
        timescale = int.from_bytes(data[marker + 16:marker + 20], "big")
        duration = int.from_bytes(data[marker + 20:marker + 24], "big")
    elif version == 1:
        timescale = int.from_bytes(data[marker + 28:marker + 32], "big")
        duration = int.from_bytes(data[marker + 32:marker + 40], "big")
    else:
        return 0.0
    if not timescale:
        return 0.0
    return duration / timescale


def local_path_for_url(url: str, page: Path) -> Path | None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme in {"http", "https"}:
        if parsed.netloc != "www.lilyroo.com":
            return None
        candidate = parsed.path
    elif parsed.scheme or url.startswith(("mailto:", "tel:", "#")):
        return None
    else:
        candidate = parsed.path or url
    if not candidate or candidate == "/":
        return ROOT / "index.html"
    if candidate.startswith("/"):
        relative = candidate.lstrip("/")
        if relative.endswith("/"):
            relative += "index.html"
        return ROOT / relative
    relative_url = candidate
    if relative_url.endswith("/"):
        relative_url += "index.html"
    return (page.parent / relative_url).resolve()


def parse_html_page(relative: str, results: list[dict]) -> LinkCollector:
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    parser = LinkCollector()
    parser.feed(text)
    add_result(results, f"{relative} parses as HTML", True)
    broken = []
    for tag, attr, value in parser.refs:
        target = local_path_for_url(value, path)
        if target and not target.exists():
            broken.append(f"{tag}[{attr}]={value}")
    add_result(results, f"{relative} local links/assets exist", not broken, "; ".join(broken[:10]))
    return parser


def parse_xml_file(relative: str, results: list[dict]) -> ET.ElementTree:
    path = ROOT / relative
    tree = ET.parse(path)
    add_result(results, f"{relative} parses as XML", True)
    return tree


def check_json_ld(relative: str, parser: LinkCollector, results: list[dict]) -> None:
    payloads = []
    for script_type, body in parser.scripts:
        if script_type == "application/ld+json" and body:
            payloads.append(json.loads(body))
    if relative not in JSON_LD_REQUIRED:
        return
    add_result(results, f"{relative} has JSON-LD", bool(payloads))
    if relative == "analog-myth.html":
        album_payload = next((item for item in payloads if item.get("@type") == "MusicAlbum"), {})
        add_result(results, "Analog Myth JSON-LD release date is July 1", album_payload.get("datePublished") == "2026-07-01", str(album_payload.get("datePublished", "")))
        add_result(results, "Analog Myth JSON-LD includes UPC", album_payload.get("identifier") == "UPC 883306680431", str(album_payload.get("identifier", "")))
        same_as = album_payload.get("sameAs") or []
        add_result(results, "Analog Myth JSON-LD includes release hub", RELEASE_HUB_URL in same_as)
    if relative == "podcasts/index.html":
        series_payload = next((item for item in payloads if item.get("@type") == "PodcastSeries"), {})
        series_image = series_payload.get("image") or {}
        add_result(results, "Podcast series JSON-LD includes feed", series_payload.get("webFeed") == "https://www.lilyroo.com/podcasts/feed.xml", str(series_payload.get("webFeed", "")))
        add_result(results, "Podcast series JSON-LD uses directory art", series_image.get("url") == "https://www.lilyroo.com/assets/podcasts/analog-myth/analog-myth-podcast-directory-art-3000.jpg", str(series_image.get("url", "")))
        add_result(results, "Podcast series JSON-LD image is square", series_image.get("width") == 3000 and series_image.get("height") == 3000, f"{series_image.get('width')}x{series_image.get('height')}")
    if relative == "podcasts/analog-myth.html":
        episode_payload = next((item for item in payloads if item.get("@type") == "PodcastEpisode"), {})
        associated_media = episode_payload.get("associatedMedia") or {}
        part_of_series = episode_payload.get("partOfSeries") or {}
        series_image = part_of_series.get("image") or {}
        add_result(results, "Podcast episode JSON-LD duration is set", episode_payload.get("duration") == "PT12M11S", str(episode_payload.get("duration", "")))
        add_result(results, "Podcast episode JSON-LD media points to audio", associated_media.get("contentUrl") == "https://www.lilyroo.com/assets/podcasts/analog-myth/analog-myth-the-clock-cannot-explain-this.m4a", str(associated_media.get("contentUrl", "")))
        add_result(results, "Podcast episode JSON-LD series includes feed", part_of_series.get("webFeed") == "https://www.lilyroo.com/podcasts/feed.xml", str(part_of_series.get("webFeed", "")))
        add_result(results, "Podcast episode JSON-LD series uses directory art", series_image.get("url") == "https://www.lilyroo.com/assets/podcasts/analog-myth/analog-myth-podcast-directory-art-3000.jpg", str(series_image.get("url", "")))


def check_required_assets(results: list[dict]) -> None:
    for label, path in (
        ("Podcast audio", PODCAST_AUDIO),
        ("Podcast poster", PODCAST_POSTER),
        ("Podcast feed art", PODCAST_FEED_ART),
        ("Analog Myth cover", ALBUM_COVER),
    ):
        add_result(results, f"{label} exists", path.exists(), str(path.relative_to(ROOT)))
        add_result(results, f"{label} is nonempty", path.exists() and path.stat().st_size > 0, str(path.stat().st_size if path.exists() else 0))
    if PODCAST_FEED_ART.exists():
        width, height = jpeg_dimensions(PODCAST_FEED_ART)
        add_result(results, "Podcast feed art is square", width == height, f"{width}x{height}")
        add_result(results, "Podcast feed art is directory sized", 1400 <= width <= 3000 and 1400 <= height <= 3000, f"{width}x{height}")


def check_feed(results: list[dict]) -> None:
    tree = parse_xml_file("podcasts/feed.xml", results)
    root = tree.getroot()
    channel = root.find("./channel")
    add_result(results, "Podcast feed has channel", channel is not None)
    if channel is None:
        return
    owner = channel.find(f"{ITUNES_NS}owner")
    owner_email = owner.findtext(f"{ITUNES_NS}email") if owner is not None else ""
    category = channel.find(f"{ITUNES_NS}category")
    channel_image = channel.find(f"{ITUNES_NS}image")
    channel_summary = channel.findtext(f"{ITUNES_NS}summary") or ""
    channel_type = channel.findtext(f"{ITUNES_NS}type") or ""
    add_result(results, "Podcast feed channel title is Echo Thread", channel.findtext("title") == "Echo Thread Podcast", channel.findtext("title") or "")
    add_result(results, "Podcast feed channel description mentions Analog Myth", "Analog Myth" in (channel.findtext("description") or ""), channel.findtext("description") or "")
    add_result(results, "Podcast feed channel summary mentions Analog Myth", "Analog Myth" in channel_summary, channel_summary)
    add_result(results, "Podcast feed channel type is episodic", channel_type == "episodic", channel_type)
    add_result(results, "Podcast feed language is en-us", channel.findtext("language") == "en-us", channel.findtext("language") or "")
    add_result(results, "Podcast feed owner email is present", owner_email == "lilyroo.artist@aol.com", owner_email or "")
    add_result(results, "Podcast feed category is Music", category is not None and category.attrib.get("text") == "Music", category.attrib.get("text", "") if category is not None else "")
    add_result(results, "Podcast feed explicit flag is false", channel.findtext(f"{ITUNES_NS}explicit") == "false", channel.findtext(f"{ITUNES_NS}explicit") or "")
    add_result(
        results,
        "Podcast feed channel image points to feed art",
        channel_image is not None and channel_image.attrib.get("href", "").endswith("/assets/podcasts/analog-myth/analog-myth-podcast-directory-art-3000.jpg"),
        channel_image.attrib.get("href", "") if channel_image is not None else "",
    )
    enclosure = root.find("./channel/item/enclosure")
    add_result(results, "Podcast feed has enclosure", enclosure is not None)
    if enclosure is None:
        return
    item = root.find("./channel/item")
    duration = item.findtext(f"{ITUNES_NS}duration") if item is not None else ""
    episode_type = item.findtext(f"{ITUNES_NS}episodeType") if item is not None else ""
    item_explicit = item.findtext(f"{ITUNES_NS}explicit") if item is not None else ""
    summary = item.findtext(f"{ITUNES_NS}summary") if item is not None else ""
    item_image = item.find(f"{ITUNES_NS}image") if item is not None else None
    add_result(results, "Podcast feed item title is Analog Myth episode", item is not None and item.findtext("title") == "Analog Myth: The Clock Cannot Explain This", item.findtext("title") if item is not None else "")
    add_result(results, "Podcast feed item duration is 12:11", duration == "12:11", duration or "")
    feed_duration_seconds = itunes_duration_seconds(duration)
    audio_duration_seconds = mp4_duration_seconds(PODCAST_AUDIO) if PODCAST_AUDIO.exists() else 0.0
    add_result(
        results,
        "Podcast feed item duration matches audio file",
        feed_duration_seconds is not None and audio_duration_seconds > 0 and abs(audio_duration_seconds - feed_duration_seconds) <= 2,
        f"feed={duration} audio={audio_duration_seconds:.2f}s",
    )
    add_result(results, "Podcast feed item episode type is full", episode_type == "full", episode_type or "")
    add_result(results, "Podcast feed item explicit flag is false", item_explicit == "false", item_explicit or "")
    add_result(results, "Podcast feed item summary mentions Analog Myth", "Analog Myth" in (summary or ""), summary or "")
    add_result(
        results,
        "Podcast feed item image points to feed art",
        item_image is not None and item_image.attrib.get("href", "").endswith("/assets/podcasts/analog-myth/analog-myth-podcast-directory-art-3000.jpg"),
        item_image.attrib.get("href", "") if item_image is not None else "",
    )
    enclosure_url = enclosure.attrib.get("url", "")
    enclosure_length = enclosure.attrib.get("length", "")
    enclosure_type = enclosure.attrib.get("type", "")
    add_result(results, "Podcast feed enclosure points to audio", enclosure_url.endswith("/assets/podcasts/analog-myth/analog-myth-the-clock-cannot-explain-this.m4a"), enclosure_url)
    add_result(results, "Podcast feed enclosure type is audio/mp4", enclosure_type == "audio/mp4", enclosure_type)
    expected_length = str(PODCAST_AUDIO.stat().st_size) if PODCAST_AUDIO.exists() else ""
    add_result(results, "Podcast feed enclosure length matches file", enclosure_length == expected_length, f"feed={enclosure_length} file={expected_length}")


def check_sitemap(results: list[dict]) -> None:
    tree = parse_xml_file("sitemap.xml", results)
    urls = {element.text or "" for element in tree.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")}
    missing = sorted(REQUIRED_SITEMAP_URLS - urls)
    add_result(results, "Sitemap includes launch URLs", not missing, ", ".join(missing))


def check_store_run(results: list[dict], require_store_links: bool) -> None:
    if not STORE_RUN.exists():
        add_result(results, "Analog Myth store verification snapshot exists", False, str(STORE_RUN.relative_to(ROOT)))
        return
    payload = json.loads(STORE_RUN.read_text(encoding="utf-8"))
    summary = payload.get("summary", {})
    checked = summary.get("checked")
    verified = summary.get("ok")
    all_verified = bool(payload.get("all_public_links_verified"))
    add_result(results, "Analog Myth store verification checked four services", checked == 4, f"checked={checked}")
    add_result(results, "Analog Myth store verification has no timeouts", summary.get("timed_out") == 0, f"timed_out={summary.get('timed_out')}")
    add_result(
        results,
        "Analog Myth public store links verified",
        all_verified or not require_store_links,
        f"verified={verified}/{checked}; required={require_store_links}",
    )


def check_live_state_copy(results: list[dict]) -> None:
    stale = []
    for relative in [*HTML_PAGES, "podcasts/feed.xml"]:
        text = (ROOT / relative).read_text(encoding="utf-8")
        for phrase in PRELAUNCH_PHRASES:
            if phrase in text:
                stale.append(f"{relative}: {phrase}")
    add_result(results, "Launch copy uses live-state language", not stale, "; ".join(stale[:10]))


def check_url_present(results: list[dict], label: str, url: str, files: list[str]) -> None:
    if not url:
        add_result(results, f"{label} verified URL is available", False)
        return
    missing = [relative for relative in files if url not in (ROOT / relative).read_text(encoding="utf-8")]
    add_result(results, f"{label} URL appears in expected launch files", not missing, ", ".join(missing))


def check_applied_store_links(results: list[dict]) -> None:
    spotify_url = verified_release_url("spotify_release_snapshot.json")
    apple_music_url = verified_release_url("apple_music_release_snapshot.json")
    youtube_music_url = verified_release_url("youtube_music_release_snapshot.json")
    check_url_present(results, "Spotify", spotify_url, SPOTIFY_LINK_FILES)
    if apple_music_url:
        check_url_present(results, "Apple Music", apple_music_url, OPTIONAL_STORE_LINK_FILES)
    if youtube_music_url:
        check_url_present(results, "YouTube Music", youtube_music_url, OPTIONAL_STORE_LINK_FILES)


def live_status(url: str, timeout_seconds: int) -> tuple[int, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "LilyRooAnalogMythLaunchReadiness/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return response.status, response.geturl()
    except urllib.error.HTTPError as exc:
        return exc.code, url
    except urllib.error.URLError as exc:
        return 0, str(exc.reason)


def live_asset_status(url: str, timeout_seconds: int) -> tuple[int, str, int | None, str, str]:
    request = urllib.request.Request(
        url,
        method="HEAD",
        headers={"User-Agent": "LilyRooAnalogMythLaunchReadiness/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            content_length = response.headers.get("Content-Length")
            return (
                response.status,
                response.geturl(),
                int(content_length) if content_length else None,
                response.headers.get("Content-Type", ""),
                response.headers.get("Accept-Ranges", ""),
            )
    except urllib.error.HTTPError as exc:
        return exc.code, url, None, "", ""
    except urllib.error.URLError as exc:
        return 0, str(exc.reason), None, "", ""


def live_text(url: str, timeout_seconds: int) -> tuple[int, str, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "LilyRooAnalogMythLaunchReadiness/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return response.status, response.geturl(), response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return exc.code, url, ""
    except urllib.error.URLError as exc:
        return 0, str(exc.reason), ""


def live_range_status(url: str, timeout_seconds: int) -> tuple[int, int, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "LilyRooAnalogMythLaunchReadiness/1.0",
            "Range": "bytes=0-1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return response.status, len(response.read()), response.headers.get("Content-Range", "")
    except urllib.error.HTTPError as exc:
        return exc.code, 0, ""
    except urllib.error.URLError as exc:
        return 0, 0, str(exc.reason)


def check_live_urls(results: list[dict], timeout_seconds: int) -> None:
    for url in LIVE_URLS:
        status, final_url = live_status(url, timeout_seconds)
        add_result(results, f"Live URL returns 200: {url}", status == 200, f"{status} {final_url}")


def check_live_assets(results: list[dict], timeout_seconds: int) -> None:
    for label, url, local_path, content_type_prefix in LIVE_ASSETS:
        status, final_url, content_length, content_type, accept_ranges = live_asset_status(url, timeout_seconds)
        expected_size = local_path.stat().st_size if local_path.exists() else 0
        add_result(results, f"{label} returns 200", status == 200, f"{status} {final_url}")
        add_result(
            results,
            f"{label} content length matches local file",
            content_length == expected_size,
            f"remote={content_length} local={expected_size}",
        )
        add_result(
            results,
            f"{label} content type is expected",
            content_type.startswith(content_type_prefix),
            content_type,
        )
        add_result(results, f"{label} advertises byte ranges", "bytes" in accept_ranges.lower(), accept_ranges)
        range_status, range_length, content_range = live_range_status(url, timeout_seconds)
        add_result(
            results,
            f"{label} supports byte range requests",
            range_status == 206 and range_length == 2,
            f"{range_status} length={range_length} {content_range}",
        )


def check_live_feed_content(results: list[dict], timeout_seconds: int) -> None:
    url = "https://www.lilyroo.com/podcasts/feed.xml"
    status, final_url, text = live_text(url, timeout_seconds)
    local_text = (ROOT / "podcasts/feed.xml").read_text(encoding="utf-8")
    add_result(results, "Live podcast feed content returns 200", status == 200, f"{status} {final_url}")
    if status != 200:
        return
    add_result(results, "Live podcast feed matches local feed", text == local_text, f"remote={len(text)} local={len(local_text)}")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        add_result(results, "Live podcast feed parses as XML", False, str(exc))
        return
    add_result(results, "Live podcast feed parses as XML", True)
    channel = root.find("channel")
    item = root.find("./channel/item")
    enclosure = item.find("enclosure") if item is not None else None
    channel_image = channel.find(f"{ITUNES_NS}image") if channel is not None else None
    item_image = item.find(f"{ITUNES_NS}image") if item is not None else None
    add_result(results, "Live podcast feed title is Echo Thread", channel is not None and channel.findtext("title") == "Echo Thread Podcast")
    add_result(results, "Live podcast feed has Analog Myth episode", item is not None and item.findtext("title") == "Analog Myth: The Clock Cannot Explain This")
    add_result(
        results,
        "Live podcast feed enclosure points to audio",
        enclosure is not None and enclosure.attrib.get("url", "").endswith("/assets/podcasts/analog-myth/analog-myth-the-clock-cannot-explain-this.m4a"),
        enclosure.attrib.get("url", "") if enclosure is not None else "",
    )
    add_result(
        results,
        "Live podcast feed channel image points to directory art",
        channel_image is not None and channel_image.attrib.get("href", "").endswith("/assets/podcasts/analog-myth/analog-myth-podcast-directory-art-3000.jpg"),
        channel_image.attrib.get("href", "") if channel_image is not None else "",
    )
    add_result(
        results,
        "Live podcast feed item image points to directory art",
        item_image is not None and item_image.attrib.get("href", "").endswith("/assets/podcasts/analog-myth/analog-myth-podcast-directory-art-3000.jpg"),
        item_image.attrib.get("href", "") if item_image is not None else "",
    )


def check_live_html_markers(results: list[dict], timeout_seconds: int) -> None:
    for url, markers in LIVE_HTML_MARKERS.items():
        status, final_url, text = live_text(url, timeout_seconds)
        add_result(results, f"Live HTML content returns 200: {url}", status == 200, f"{status} {final_url}")
        if status != 200:
            continue
        for label, marker in markers:
            add_result(results, f"{label} is deployed", marker in text, marker)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the public Analog Myth album and podcast launch package.")
    parser.add_argument("--live", action="store_true", help="Also check live lilyroo.com launch URLs.")
    parser.add_argument("--require-store-links", action="store_true", help="Fail unless public store links have all verified.")
    parser.add_argument("--timeout-seconds", type=int, default=10, help="Timeout for each live URL check.")
    args = parser.parse_args()

    results: list[dict] = []
    check_required_assets(results)
    for relative in HTML_PAGES:
        parser_obj = parse_html_page(relative, results)
        check_json_ld(relative, parser_obj, results)
    check_feed(results)
    check_sitemap(results)
    check_store_run(results, args.require_store_links)
    if args.require_store_links:
        check_live_state_copy(results)
        check_applied_store_links(results)
    if args.live:
        check_live_urls(results, args.timeout_seconds)
        check_live_assets(results, args.timeout_seconds)
        check_live_feed_content(results, args.timeout_seconds)
        check_live_html_markers(results, args.timeout_seconds)

    failures = [result for result in results if not result["ok"]]
    output = {
        "ok": not failures,
        "checked": len(results),
        "failed": len(failures),
        "require_store_links": args.require_store_links,
        "live_checked": args.live,
        "failures": failures,
        "results": results,
    }
    print(json.dumps(output, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
