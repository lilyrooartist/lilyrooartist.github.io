#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data" / "scheduled_posts.csv"
FUTURE = ROOT / "admin" / "future-posts.json"
REDIRECT = ROOT / "go" / "am.html"
HOME_PAGE = ROOT / "index.html"
PODCAST_PAGE = ROOT / "podcasts" / "analog-myth.html"
MUSIC_PAGE = ROOT / "music.html"
ANALOG_MYTH_PAGE = ROOT / "analog-myth.html"
OUT = ROOT / "data" / "brand_click_tracking_health.json"
REPORT = ROOT / "admin" / "reports" / "brand-click-tracking-health.md"
REPORT_INDEX = ROOT / "admin" / "reports" / "index.html"
ADMIN_INDEX = ROOT / "admin" / "index.html"

CAMPAIGN_PREFIX = "FP-BRAND-AM"
TRACKING_HOST = "www.lilyroo.com"
TRACKING_PATH = "/go/am.html"
EXPECTED_DESTINATIONS = {"album", "echo", "video"}
SITE_SHARE_EXPECTED = {
    "site-share-album": {"destination": "album"},
    "site-share-echo": {"destination": "echo"},
    "site-share-video": {"destination": "video"},
    "site-share-track-01-13": {"destination": "album", "anchor": "track-13"},
    "site-share-track-02-girls-camp": {"destination": "album", "anchor": "track-girls-camp"},
    "site-share-track-03-analog-myth": {"destination": "album", "anchor": "track-analog-myth"},
    "site-share-track-04-spilling-the-tea": {"destination": "album", "anchor": "track-spilling-the-tea"},
    "site-share-track-05-no-mortgage": {"destination": "album", "anchor": "track-no-mortgage"},
    "site-share-track-06-guards-down": {"destination": "album", "anchor": "track-guards-down"},
    "site-share-track-07-slow-walk": {"destination": "album", "anchor": "track-slow-walk"},
    "site-share-track-08-the-power-of-light": {"destination": "album", "anchor": "track-the-power-of-light"},
}
SITE_HOME_EXPECTED = {
    "site-home-hero-album": {"destination": "album"},
    "site-home-hero-echo": {"destination": "echo"},
    "site-home-hero-playlist": {"destination": "playlist"},
    "site-home-starter-album": {"destination": "album"},
    "site-home-starter-playlist": {"destination": "playlist"},
    "site-home-starter-echo": {"destination": "echo"},
    "site-home-launch-album": {"destination": "album"},
    "site-home-launch-listen": {"destination": "listen"},
    "site-home-launch-playlist": {"destination": "playlist"},
    "site-home-launch-echo": {"destination": "echo"},
    "site-home-podcast-echo": {"destination": "echo"},
}
SITE_PODCAST_EXPECTED = {
    "site-podcast-hero-album": {"destination": "album"},
    "site-podcast-hero-episode": {"destination": "episode"},
    "site-podcast-hero-listen": {"destination": "listen"},
    "site-podcast-hero-playlist": {"destination": "playlist"},
    "site-podcast-hero-rss": {"destination": "rss"},
    "site-podcast-player-download": {"destination": "download"},
    "site-podcast-player-episode": {"destination": "episode"},
    "site-podcast-share-echo": {"destination": "echo"},
    "site-podcast-share-album": {"destination": "album"},
    "site-podcast-share-playlist": {"destination": "playlist"},
}
SITE_MUSIC_EXPECTED = {
    "site-music-album-page": {"destination": "album"},
    "site-music-listen-links": {"destination": "listen"},
    "site-music-spotify": {"destination": "spotify"},
    "site-music-apple": {"destination": "apple"},
    "site-music-playlist": {"destination": "playlist"},
    "site-music-podcast-episode": {"destination": "episode"},
}
CLICK_DRY_RUN_BASE = "https://www.lilyroo.com/api/social/click"
CLICK_DRY_RUN_USER_AGENT = "LilyRooClickDryRun/1.0"


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def post_parts(post_id: str) -> dict:
    normalized = str(post_id or "").strip().lower()
    site_home = re.match(r"^site-home-(hero|starter|launch|podcast)-(album|echo|listen|playlist|video)$", normalized)
    if site_home:
        return {"post_id": normalized, "wave": "site-home", "track": "", "platform": "site"}
    site_podcast = re.match(r"^site-podcast-(hero|player|share)-(album|echo|episode|listen|playlist|rss|download)$", normalized)
    if site_podcast:
        return {"post_id": normalized, "wave": "site-podcast", "track": "", "platform": "site"}
    site_music = re.match(r"^site-music-(album-page|listen-links|spotify|apple|playlist|podcast-episode)$", normalized)
    if site_music:
        return {"post_id": normalized, "wave": "site-music", "track": "", "platform": "site"}
    site_share = re.match(r"^site-share-(album|echo|video|track-(\d{2})-[a-z0-9-]+)$", normalized)
    if site_share:
        return {"post_id": normalized, "wave": "site-share", "track": site_share.group(2) or "", "platform": "site"}
    match = re.match(r"^fp-brand-am(?:-w(\d+))?-(\d{2})-.+-(x|facebook)$", normalized)
    if not match:
        return {"post_id": normalized, "wave": "unknown", "track": "", "platform": ""}
    return {
        "post_id": normalized,
        "wave": f"w{match.group(1)}" if match.group(1) else "track-moments",
        "track": match.group(2),
        "platform": match.group(3),
    }


def future_ids() -> set[str]:
    payload = read_json(FUTURE, {})
    return {
        str(post.get("id") or "").strip()
        for post in payload.get("posts") or []
        if str(post.get("id") or "").strip().startswith(CAMPAIGN_PREFIX)
    }


def tracking_urls(reply_text: str) -> list[str]:
    return re.findall(r"https://www\.lilyroo\.com/go/am\.html\?[^\s]+", reply_text or "")


def site_share_urls() -> list[str]:
    if not ANALOG_MYTH_PAGE.exists():
        return []
    text = ANALOG_MYTH_PAGE.read_text(encoding="utf-8")
    return [
        url.replace("&amp;", "&")
        for url in re.findall(r'data-share-url="(https://www\.lilyroo\.com/go/am\.html\?[^"]+)"', text)
    ]


def site_home_urls() -> list[str]:
    if not HOME_PAGE.exists():
        return []
    text = HOME_PAGE.read_text(encoding="utf-8")
    urls = [
        url.replace("&amp;", "&")
        for url in re.findall(r'href="(/go/am\.html\?[^"]+)"', text)
    ]
    return [f"https://www.lilyroo.com{url}" for url in urls]


def site_podcast_urls() -> list[str]:
    if not PODCAST_PAGE.exists():
        return []
    text = PODCAST_PAGE.read_text(encoding="utf-8")
    hrefs = [
        url.replace("&amp;", "&")
        for url in re.findall(r'href="(/go/am\.html\?[^"]+)"', text)
    ]
    share_urls = [
        url.replace("&amp;", "&")
        for url in re.findall(r'data-share-url="(https://www\.lilyroo\.com/go/am\.html\?[^"]+)"', text)
    ]
    return [f"https://www.lilyroo.com{url}" for url in hrefs] + share_urls


def site_music_urls() -> list[str]:
    if not MUSIC_PAGE.exists():
        return []
    text = MUSIC_PAGE.read_text(encoding="utf-8")
    hrefs = [
        url.replace("&amp;", "&")
        for url in re.findall(r'href="(/go/am\.html\?[^"]+)"', text)
    ]
    return [f"https://www.lilyroo.com{url}" for url in hrefs]


def visible_surface_text(row: dict) -> str:
    pieces = [
        str(row.get("text") or "").strip(),
        str(row.get("reply_text") or "").strip(),
    ]
    return "\n\n".join(piece for piece in pieces if piece)


def validate_url(url: str, post_id: str) -> tuple[dict, list[str]]:
    issues: list[str] = []
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    destination = (query.get("to") or [""])[0]
    p_value = (query.get("p") or [""])[0]
    expected_post = post_id.lower()

    if parsed.scheme != "https":
        issues.append("tracking_url_not_https")
    if parsed.netloc != TRACKING_HOST:
        issues.append("tracking_url_wrong_host")
    if parsed.path != TRACKING_PATH:
        issues.append("tracking_url_wrong_path")
    if p_value != expected_post:
        issues.append("tracking_url_post_id_mismatch")
    if destination not in EXPECTED_DESTINATIONS:
        issues.append("tracking_url_unknown_destination")

    return {
        "url": url,
        "destination": destination,
        "post_id_param": p_value,
        "expected_post_id_param": expected_post,
        "ok": not issues,
        "issues": issues,
    }, issues


def redirect_health() -> dict:
    text = REDIRECT.read_text(encoding="utf-8") if REDIRECT.exists() else ""
    checks = {
        "exists": REDIRECT.exists(),
        "records_click": "/api/social/click" in text,
        "uses_send_beacon": "navigator.sendBeacon" in text,
        "has_fetch_fallback": 'fetch("/api/social/click"' in text,
        "adds_utm_source": "utm_source" in text,
        "adds_utm_campaign": "analog_myth_brand_growth" in text,
        "supports_album": "album:" in text,
        "supports_echo": "echo:" in text,
        "supports_spotify": 'spotify: "https://open.spotify.com/album/6Ujyp8tXa5UxheJJC2B6kL"' in text,
        "supports_apple": 'apple: "https://music.apple.com/us/album/analog-myth/6777905789"' in text,
        "supports_episode": "episode:" in text and "https://youtu.be/xX2-Xf161js" in text,
        "supports_rss": "rss:" in text,
        "supports_download": "download:" in text,
        "supports_video": 'destination === "video"' in text,
        "has_noindex_guard": 'name="robots" content="noindex"' in text,
        "canonical_points_to_album": 'rel="canonical" href="https://www.lilyroo.com/analog-myth.html"' in text,
        "has_open_graph_title": 'property="og:title" content="Analog Myth - Lily Roo"' in text,
        "has_open_graph_image": 'property="og:image" content="https://www.lilyroo.com/assets/albums/analog-myth/art/03-analog-myth.jpg"' in text,
        "has_twitter_card": 'name="twitter:card" content="summary_large_image"' in text,
        "has_twitter_image": 'name="twitter:image" content="https://www.lilyroo.com/assets/albums/analog-myth/art/03-analog-myth.jpg"' in text,
    }
    return {
        "path": rel(REDIRECT),
        "status": "ready" if all(checks.values()) else "attention",
        "checks": checks,
    }


def click_endpoint_dry_run(post_id: str | None, destination: str = "album") -> dict:
    expected_post = str(post_id or "").strip().lower()
    result = {
        "status": "attention",
        "safe_mode": True,
        "dry_run": False,
        "expected_post_id": expected_post,
        "url": "",
    }
    if not expected_post:
        return {**result, "error": "missing_campaign_id"}

    url = f"{CLICK_DRY_RUN_BASE}?dry_run=1&p={quote(expected_post)}&to={quote(destination)}"
    result["url"] = url
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "Origin": "https://www.lilyroo.com",
            "User-Agent": CLICK_DRY_RUN_USER_AGENT,
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8")
            http_status = response.status
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        return {
            **result,
            "http_status": error.code,
            "error": f"http_error:{error.code}",
            "body_preview": body[:500],
        }
    except Exception as error:
        return {**result, "error": f"{type(error).__name__}: {error}"}

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as error:
        return {
            **result,
            "http_status": http_status,
            "error": f"json_error:{error}",
            "body_preview": body[:500],
        }

    event = payload.get("event") or {}
    reported_post = str(event.get("post_id") or "").strip().lower()
    dry_run = payload.get("dry_run") is True
    ok = (
        http_status == 200
        and payload.get("ok") is True
        and dry_run
        and reported_post == expected_post
        and event.get("type") == "brand_campaign_click"
        and event.get("destination") == destination
    )
    return {
        **result,
        "status": "ready" if ok else "attention",
        "http_status": http_status,
        "ok": payload.get("ok") is True,
        "dry_run": dry_run,
        "reported_post_id": reported_post,
        "platform": event.get("platform") or "",
        "wave": event.get("wave") or "",
        "track": event.get("track") or "",
        "destination": event.get("destination") or "",
        "recorded_at": event.get("recorded_at") or "",
    }


def site_share_health() -> dict:
    urls = site_share_urls()
    rows = []
    issue_counts = Counter()
    seen_ids = set()
    for url in urls:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        post_id = (query.get("p") or [""])[0]
        destination = (query.get("to") or [""])[0]
        anchor = (query.get("anchor") or [""])[0]
        expected = SITE_SHARE_EXPECTED.get(post_id)
        issues = []
        if parsed.scheme != "https":
            issues.append("share_url_not_https")
        if parsed.netloc != TRACKING_HOST:
            issues.append("share_url_wrong_host")
        if parsed.path != TRACKING_PATH:
            issues.append("share_url_wrong_path")
        if not expected:
            issues.append("unknown_site_share_id")
        else:
            seen_ids.add(post_id)
            if destination != expected["destination"]:
                issues.append("site_share_destination_mismatch")
            expected_anchor = expected.get("anchor") or ""
            if anchor != expected_anchor:
                issues.append("site_share_anchor_mismatch")
        for issue in sorted(set(issues)):
            issue_counts[issue] += 1
        rows.append({
            "id": post_id,
            "url": url,
            "destination": destination,
            "anchor": anchor,
            "ok": not issues,
            "issues": sorted(set(issues)),
        })
    missing_ids = sorted(set(SITE_SHARE_EXPECTED) - seen_ids)
    for _ in missing_ids:
        issue_counts["missing_site_share_url"] += 1
    title_video_fallback = False
    redirect_text = REDIRECT.read_text(encoding="utf-8") if REDIRECT.exists() else ""
    if 'const TITLE_TRACK_VIDEO = "https://youtu.be/_rtioKYbCFM";' in redirect_text and "TRACKS[track]?.video || TITLE_TRACK_VIDEO" in redirect_text:
        title_video_fallback = True
    else:
        issue_counts["missing_site_share_video_fallback"] += 1
    endpoint = click_endpoint_dry_run("site-share-album", "album")
    if endpoint.get("status") != "ready":
        issue_counts["site_share_endpoint_not_ready"] += 1
    return {
        "status": "ready" if not issue_counts and len(rows) == len(SITE_SHARE_EXPECTED) else "attention",
        "expected_url_count": len(SITE_SHARE_EXPECTED),
        "url_count": len(rows),
        "ready_url_count": sum(1 for row in rows if row["ok"]),
        "missing_ids": missing_ids,
        "issue_counts": dict(sorted(issue_counts.items())),
        "title_video_fallback": title_video_fallback,
        "click_endpoint": endpoint,
        "rows": rows,
    }


def expected_site_url_health(label: str, urls: list[str], expected_map: dict[str, dict], endpoint_probe_id: str, endpoint_destination: str) -> dict:
    rows = []
    issue_counts = Counter()
    seen_ids = set()
    for url in urls:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        post_id = (query.get("p") or [""])[0]
        destination = (query.get("to") or [""])[0]
        anchor = (query.get("anchor") or [""])[0]
        expected = expected_map.get(post_id)
        issues = []
        if parsed.scheme != "https":
            issues.append(f"{label}_url_not_https")
        if parsed.netloc != TRACKING_HOST:
            issues.append(f"{label}_url_wrong_host")
        if parsed.path != TRACKING_PATH:
            issues.append(f"{label}_url_wrong_path")
        if not expected:
            issues.append(f"unknown_{label}_id")
        else:
            seen_ids.add(post_id)
            if destination != expected["destination"]:
                issues.append(f"{label}_destination_mismatch")
            expected_anchor = expected.get("anchor") or ""
            if anchor != expected_anchor:
                issues.append(f"{label}_anchor_mismatch")
        for issue in sorted(set(issues)):
            issue_counts[issue] += 1
        rows.append({
            "id": post_id,
            "url": url,
            "destination": destination,
            "anchor": anchor,
            "ok": not issues,
            "issues": sorted(set(issues)),
        })
    missing_ids = sorted(set(expected_map) - seen_ids)
    for _ in missing_ids:
        issue_counts[f"missing_{label}_url"] += 1
    endpoint = click_endpoint_dry_run(endpoint_probe_id, endpoint_destination)
    if endpoint.get("status") != "ready":
        issue_counts[f"{label}_endpoint_not_ready"] += 1
    return {
        "status": "ready" if not issue_counts and len(rows) == len(expected_map) else "attention",
        "expected_url_count": len(expected_map),
        "url_count": len(rows),
        "ready_url_count": sum(1 for row in rows if row["ok"]),
        "missing_ids": missing_ids,
        "issue_counts": dict(sorted(issue_counts.items())),
        "click_endpoint": endpoint,
        "rows": rows,
    }


def build_payload() -> dict:
    now = datetime.now(timezone.utc)
    visible_ids = future_ids()
    rows = []
    issue_counts = Counter()
    destination_counts = Counter()
    platform_counts = Counter()
    wave_counts = Counter()
    track_counts = Counter()
    x_main_album_link_count = 0
    expected_x_main_album_link_count = 0
    visible_album_link_count = 0
    visible_full_destination_count = 0
    expected_visible_surface_count = 0

    for row in read_csv(QUEUE):
        post_id = str(row.get("id") or "").strip()
        if not post_id.startswith(CAMPAIGN_PREFIX) or post_id not in visible_ids:
            continue
        if str(row.get("approved") or "").strip().lower() != "yes":
            continue
        if str(row.get("execution_mode") or "").strip().lower() != "auto":
            continue

        parts = post_parts(post_id)
        urls = tracking_urls(row.get("reply_text") or "")
        main_text_urls = tracking_urls(row.get("text") or "")
        surface_urls = tracking_urls(visible_surface_text(row))
        row_issues: list[str] = []
        url_results = []
        main_text_url_results = []
        destinations = set()
        surface_destinations = set()
        for url in urls:
            result, issues = validate_url(url, post_id)
            url_results.append(result)
            row_issues.extend(issues)
            if result["destination"]:
                destinations.add(result["destination"])
                destination_counts[result["destination"]] += 1

        for url in surface_urls:
            result, issues = validate_url(url, post_id)
            row_issues.extend(issues)
            if result["destination"]:
                surface_destinations.add(result["destination"])

        missing_destinations = sorted(EXPECTED_DESTINATIONS - destinations)
        missing_surface_destinations = sorted(EXPECTED_DESTINATIONS - surface_destinations)
        for destination in missing_destinations:
            row_issues.append(f"missing_{destination}_tracking_link")
        for destination in missing_surface_destinations:
            row_issues.append(f"missing_visible_{destination}_tracking_link")
        if len(urls) != len(EXPECTED_DESTINATIONS):
            row_issues.append("unexpected_tracking_link_count")
        expected_visible_surface_count += 1
        if "album" in surface_destinations:
            visible_album_link_count += 1
        if not missing_surface_destinations:
            visible_full_destination_count += 1
        if not row.get("reply_text"):
            row_issues.append("missing_reply_text")

        main_album_link_ok = True
        if parts["platform"] == "x":
            expected_x_main_album_link_count += 1
            main_album_link_ok = False
            for url in main_text_urls:
                result, issues = validate_url(url, post_id)
                main_text_url_results.append(result)
                if not issues and result["destination"] == "album":
                    main_album_link_ok = True
            if main_album_link_ok:
                x_main_album_link_count += 1
            else:
                row_issues.append("missing_x_main_album_link")

        for issue in sorted(set(row_issues)):
            issue_counts[issue] += 1
        platform_counts[parts["platform"] or str(row.get("platform") or "unknown").lower()] += 1
        wave_counts[parts["wave"]] += 1
        if parts["track"]:
            track_counts[parts["track"]] += 1

        rows.append({
            "id": post_id,
            "platform": row.get("platform") or "",
            "scheduled_at": row.get("scheduled_at") or "",
            "wave": parts["wave"],
            "track": parts["track"],
            "tracking_url_count": len(urls),
            "destinations": sorted(destinations),
            "missing_destinations": missing_destinations,
            "ok": not row_issues,
            "issues": sorted(set(row_issues)),
            "tracking_urls": url_results,
            "main_text_album_link_ok": main_album_link_ok,
            "main_text_tracking_urls": main_text_url_results,
            "visible_surface_album_link_ok": "album" in surface_destinations,
            "visible_surface_destinations": sorted(surface_destinations),
            "visible_surface_tracking_url_count": len(surface_urls),
        })

    redirect = redirect_health()
    sample_id = next((row["id"] for row in rows if str(row.get("platform") or "").lower() == "x"), rows[0]["id"] if rows else "")
    click_endpoint = click_endpoint_dry_run(sample_id)
    site_share = site_share_health()
    site_home = expected_site_url_health(
        "site_home",
        site_home_urls(),
        SITE_HOME_EXPECTED,
        "site-home-hero-album",
        "album",
    )
    site_podcast = expected_site_url_health(
        "site_podcast",
        site_podcast_urls(),
        SITE_PODCAST_EXPECTED,
        "site-podcast-hero-album",
        "album",
    )
    site_music = expected_site_url_health(
        "site_music",
        site_music_urls(),
        SITE_MUSIC_EXPECTED,
        "site-music-album-page",
        "album",
    )
    ready_rows = sum(1 for row in rows if row["ok"])
    broken_rows = len(rows) - ready_rows
    total_urls = sum(row["tracking_url_count"] for row in rows)
    expected_urls = len(rows) * len(EXPECTED_DESTINATIONS)
    status = (
        "ready"
        if (
            rows
            and not broken_rows
            and total_urls == expected_urls
            and visible_album_link_count == expected_visible_surface_count
            and visible_full_destination_count == expected_visible_surface_count
            and redirect["status"] == "ready"
            and site_share["status"] == "ready"
            and site_home["status"] == "ready"
            and site_podcast["status"] == "ready"
            and site_music["status"] == "ready"
        )
        else "attention"
    )

    return {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "scheduled_posts": rel(QUEUE),
            "future_posts": rel(FUTURE),
            "redirect_page": rel(REDIRECT),
            "home_page": rel(HOME_PAGE),
            "podcast_page": rel(PODCAST_PAGE),
            "music_page": rel(MUSIC_PAGE),
        },
        "summary": {
            "status": status,
            "future_campaign_rows": len(rows),
            "ready_future_campaign_rows": ready_rows,
            "broken_future_campaign_rows": broken_rows,
            "tracking_url_count": total_urls,
            "expected_tracking_url_count": expected_urls,
            "x_main_album_link_count": x_main_album_link_count,
            "expected_x_main_album_link_count": expected_x_main_album_link_count,
            "visible_surface_album_link_count": visible_album_link_count,
            "expected_visible_surface_album_link_count": expected_visible_surface_count,
            "visible_surface_full_destination_count": visible_full_destination_count,
            "expected_visible_surface_full_destination_count": expected_visible_surface_count,
            "destination_counts": dict(sorted(destination_counts.items())),
            "platform_counts": dict(sorted(platform_counts.items())),
            "wave_counts": dict(sorted(wave_counts.items())),
            "track_counts": dict(sorted(track_counts.items())),
            "issue_counts": dict(sorted(issue_counts.items())),
            "redirect_status": redirect["status"],
            "click_endpoint_status": click_endpoint["status"],
            "click_endpoint_http_status": click_endpoint.get("http_status"),
            "click_endpoint_dry_run": click_endpoint.get("dry_run") is True,
            "site_share_status": site_share["status"],
            "site_share_url_count": site_share["url_count"],
            "expected_site_share_url_count": site_share["expected_url_count"],
            "site_share_endpoint_status": site_share["click_endpoint"].get("status"),
            "site_home_status": site_home["status"],
            "site_home_url_count": site_home["url_count"],
            "expected_site_home_url_count": site_home["expected_url_count"],
            "site_home_endpoint_status": site_home["click_endpoint"].get("status"),
            "site_podcast_status": site_podcast["status"],
            "site_podcast_url_count": site_podcast["url_count"],
            "expected_site_podcast_url_count": site_podcast["expected_url_count"],
            "site_podcast_endpoint_status": site_podcast["click_endpoint"].get("status"),
            "site_music_status": site_music["status"],
            "site_music_url_count": site_music["url_count"],
            "expected_site_music_url_count": site_music["expected_url_count"],
            "site_music_endpoint_status": site_music["click_endpoint"].get("status"),
            "report_path": rel(REPORT),
            "refresh_command": "python3 scripts/build_brand_click_tracking_health.py",
        },
        "redirect": redirect,
        "click_endpoint": click_endpoint,
        "site_share": site_share,
        "site_home": site_home,
        "site_podcast": site_podcast,
        "site_music": site_music,
        "rows": rows,
        "guardrails": [
            "This check is read-only and does not post.",
            "Tracking links use first-party Lily Roo redirect URLs.",
            "Click capture stores campaign metadata only and does not store IP addresses.",
            "Every future Analog Myth auto post should carry album, Echo Thread, and video destinations.",
            "Every future X Analog Myth auto post should carry the album destination in the main post text.",
            "Every future Analog Myth auto post should expose an album link on the visible published surface.",
            "Album-page share buttons should use first-party site-share tracking links.",
            "Homepage Analog Myth CTAs should use first-party site-home tracking links.",
            "Podcast-page Analog Myth CTAs should use first-party site-podcast tracking links.",
            "Music catalog Analog Myth CTAs should use first-party site-music tracking links.",
            "The live click endpoint health probe uses dry_run=1 so it cannot create fake campaign clicks.",
        ],
    }


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Brand Click Tracking Health - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Status: **{summary['status']}**",
        f"- Future campaign rows ready: **{summary['ready_future_campaign_rows']} / {summary['future_campaign_rows']}**",
        f"- Tracking URLs checked: **{summary['tracking_url_count']} / {summary['expected_tracking_url_count']}**",
        f"- X main-post album links: **{summary['x_main_album_link_count']} / {summary['expected_x_main_album_link_count']}**",
        f"- Visible album click paths: **{summary['visible_surface_album_link_count']} / {summary['expected_visible_surface_album_link_count']}**",
        f"- Visible full destination sets: **{summary['visible_surface_full_destination_count']} / {summary['expected_visible_surface_full_destination_count']}**",
        f"- Redirect page: **{summary['redirect_status']}**",
        f"- Live click endpoint dry run: **{summary['click_endpoint_status']}**",
        f"- Album-page share tracking: **{summary['site_share_status']}** ({summary['site_share_url_count']} / {summary['expected_site_share_url_count']})",
        f"- Site-share endpoint dry run: **{summary['site_share_endpoint_status']}**",
        f"- Homepage CTA tracking: **{summary['site_home_status']}** ({summary['site_home_url_count']} / {summary['expected_site_home_url_count']})",
        f"- Homepage endpoint dry run: **{summary['site_home_endpoint_status']}**",
        f"- Podcast CTA tracking: **{summary['site_podcast_status']}** ({summary['site_podcast_url_count']} / {summary['expected_site_podcast_url_count']})",
        f"- Podcast endpoint dry run: **{summary['site_podcast_endpoint_status']}**",
        f"- Music catalog CTA tracking: **{summary['site_music_status']}** ({summary['site_music_url_count']} / {summary['expected_site_music_url_count']})",
        f"- Music catalog endpoint dry run: **{summary['site_music_endpoint_status']}**",
        f"- Destinations: **{', '.join(f'{key}: {value}' for key, value in summary['destination_counts'].items()) or 'none'}**",
        f"- Issues: **{', '.join(f'{key}: {value}' for key, value in summary['issue_counts'].items()) or 'none'}**",
        "",
        "## Live Endpoint Dry Run",
    ]
    endpoint = payload.get("click_endpoint") or {}
    lines.extend([
        f"- Status: **{endpoint.get('status') or 'unknown'}**",
        f"- HTTP status: **{endpoint.get('http_status') or 'n/a'}**",
        f"- Dry run: **{'yes' if endpoint.get('dry_run') is True else 'no'}**",
        f"- Probe campaign id: `{endpoint.get('expected_post_id') or 'n/a'}`",
        f"- Event: **{endpoint.get('platform') or 'unknown'} / {endpoint.get('destination') or 'unknown'} / track {endpoint.get('track') or 'unknown'}**",
        "",
        "## Redirect Checks",
    ])
    for key, value in (payload.get("redirect") or {}).get("checks", {}).items():
        lines.append(f"- {key}: **{'ok' if value else 'attention'}**")
    site_share = payload.get("site_share") or {}
    site_share_endpoint = site_share.get("click_endpoint") or {}
    lines.extend([
        "",
        "## Album Page Share Tracking",
        f"- Status: **{site_share.get('status') or 'unknown'}**",
        f"- Share URLs ready: **{site_share.get('ready_url_count', 0)} / {site_share.get('expected_url_count', 0)}**",
        f"- Title-track video fallback: **{'ok' if site_share.get('title_video_fallback') else 'attention'}**",
        f"- Site-share endpoint dry run: **{site_share_endpoint.get('status') or 'unknown'}**",
        f"- Site-share probe id: `{site_share_endpoint.get('expected_post_id') or 'n/a'}`",
        f"- Site-share issues: **{', '.join(f'{key}: {value}' for key, value in (site_share.get('issue_counts') or {}).items()) or 'none'}**",
    ])
    for row in site_share.get("rows") or []:
        lines.append(
            f"- `{row.get('id') or 'unknown'}` -> `{row.get('destination') or 'unknown'}`"
            f"{'#' + row.get('anchor') if row.get('anchor') else ''}: **{'ready' if row.get('ok') else 'attention'}**"
        )
    site_home = payload.get("site_home") or {}
    site_home_endpoint = site_home.get("click_endpoint") or {}
    lines.extend([
        "",
        "## Homepage CTA Tracking",
        f"- Status: **{site_home.get('status') or 'unknown'}**",
        f"- CTA URLs ready: **{site_home.get('ready_url_count', 0)} / {site_home.get('expected_url_count', 0)}**",
        f"- Homepage endpoint dry run: **{site_home_endpoint.get('status') or 'unknown'}**",
        f"- Homepage probe id: `{site_home_endpoint.get('expected_post_id') or 'n/a'}`",
        f"- Homepage issues: **{', '.join(f'{key}: {value}' for key, value in (site_home.get('issue_counts') or {}).items()) or 'none'}**",
    ])
    for row in site_home.get("rows") or []:
        lines.append(
            f"- `{row.get('id') or 'unknown'}` -> `{row.get('destination') or 'unknown'}`: **{'ready' if row.get('ok') else 'attention'}**"
        )
    site_podcast = payload.get("site_podcast") or {}
    site_podcast_endpoint = site_podcast.get("click_endpoint") or {}
    lines.extend([
        "",
        "## Podcast Page CTA Tracking",
        f"- Status: **{site_podcast.get('status') or 'unknown'}**",
        f"- CTA URLs ready: **{site_podcast.get('ready_url_count', 0)} / {site_podcast.get('expected_url_count', 0)}**",
        f"- Podcast endpoint dry run: **{site_podcast_endpoint.get('status') or 'unknown'}**",
        f"- Podcast probe id: `{site_podcast_endpoint.get('expected_post_id') or 'n/a'}`",
        f"- Podcast issues: **{', '.join(f'{key}: {value}' for key, value in (site_podcast.get('issue_counts') or {}).items()) or 'none'}**",
    ])
    for row in site_podcast.get("rows") or []:
        lines.append(
            f"- `{row.get('id') or 'unknown'}` -> `{row.get('destination') or 'unknown'}`: **{'ready' if row.get('ok') else 'attention'}**"
        )
    site_music = payload.get("site_music") or {}
    site_music_endpoint = site_music.get("click_endpoint") or {}
    lines.extend([
        "",
        "## Music Catalog CTA Tracking",
        f"- Status: **{site_music.get('status') or 'unknown'}**",
        f"- CTA URLs ready: **{site_music.get('ready_url_count', 0)} / {site_music.get('expected_url_count', 0)}**",
        f"- Music catalog endpoint dry run: **{site_music_endpoint.get('status') or 'unknown'}**",
        f"- Music catalog probe id: `{site_music_endpoint.get('expected_post_id') or 'n/a'}`",
        f"- Music catalog issues: **{', '.join(f'{key}: {value}' for key, value in (site_music.get('issue_counts') or {}).items()) or 'none'}**",
    ])
    for row in site_music.get("rows") or []:
        lines.append(
            f"- `{row.get('id') or 'unknown'}` -> `{row.get('destination') or 'unknown'}`: **{'ready' if row.get('ok') else 'attention'}**"
        )
    lines.extend(["", "## Future Rows"])
    for row in payload["rows"]:
        lines.append(
            f"- `{row['id']}` {row['platform']} {row['scheduled_at']} - "
            f"**{'ready' if row['ok'] else 'attention'}** "
            f"({row['tracking_url_count']} link{'s' if row['tracking_url_count'] != 1 else ''})"
        )
        if row.get("issues"):
            lines.append(f"  - Issues: `{', '.join(row['issues'])}`")
        else:
            lines.append(f"  - Destinations: `{', '.join(row['destinations'])}`")
        lines.append(
            f"  - Visible surface: **{'ready' if row.get('visible_surface_album_link_ok') else 'attention'}** "
            f"(`{', '.join(row.get('visible_surface_destinations') or []) or 'none'}`)"
        )
        if row.get("platform") == "X":
            lines.append(f"  - Main-post album link: **{'ready' if row.get('main_text_album_link_ok') else 'attention'}**")
    lines.extend(["", "## Guardrails"])
    for item in payload.get("guardrails") or []:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def replace_json_embed(html: str, block_id: str, payload) -> str:
    marker = f'<script type="application/json" id="{block_id}">'
    end_marker = "</script>"
    encoded = json.dumps(payload, indent=2, ensure_ascii=False)
    start = html.find(marker)
    if start == -1:
        return html.replace("<script>", f"\n{marker}{encoded}{end_marker}\n\n<script>", 1)
    content_start = start + len(marker)
    content_end = html.find(end_marker, content_start)
    if content_end == -1:
        raise RuntimeError(f"Could not find end marker for {block_id}")
    return html[:content_start] + encoded + html[content_end:]


def replace_text_embed(html: str, block_id: str, content: str) -> str:
    marker = f'<script type="text/plain" id="{block_id}">'
    end_marker = "</script>"
    start = html.find(marker)
    if start == -1:
        return html.replace("<script>", f"\n{marker}{content.rstrip()}{end_marker}\n\n<script>", 1)
    content_start = start + len(marker)
    content_end = html.find(end_marker, content_start)
    if content_end == -1:
        raise RuntimeError(f"Could not find end marker for {block_id}")
    return html[:content_start] + content.rstrip() + html[content_end:]


def sync_admin(payload: dict, markdown: str) -> None:
    if ADMIN_INDEX.exists():
        html = ADMIN_INDEX.read_text(encoding="utf-8")
        html = replace_json_embed(html, "embedded-brand-click-tracking-health", payload)
        html = replace_text_embed(html, "embedded-brand-click-tracking-health-report", markdown)
        ADMIN_INDEX.write_text(html, encoding="utf-8")
    if REPORT_INDEX.exists():
        html = REPORT_INDEX.read_text(encoding="utf-8")
        link = '<li><a href="/admin/reports/brand-click-tracking-health.md" target="_blank">Brand Click Tracking Health</a></li>'
        if link not in html:
            marker = '<li><a href="/admin/reports/brand-campaign-clicks.md" target="_blank">Brand Campaign Clicks</a></li>'
            if marker in html:
                html = html.replace(marker, marker + "\n        " + link, 1)
            else:
                html = html.replace("</ul>", f"        {link}\n      </ul>", 1)
            REPORT_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    payload = build_payload()
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(payload)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(payload, markdown)
    print(json.dumps({"output": rel(OUT), **payload["summary"]}, indent=2, ensure_ascii=False))
    return 0 if payload["summary"]["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
