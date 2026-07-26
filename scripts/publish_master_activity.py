#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
READOUT = ROOT / "data" / "brand_growth_readout.json"
DEFAULT_ADMIN_URL = "https://admin.famous.land"


def build_event(readout: dict) -> dict:
    summary = readout.get("summary") or {}
    visibility_attention = int(summary.get("public_visibility_attention_count") or 0)
    status_counts = summary.get("status_counts") or {}
    signature_payload = {
        "status_counts": status_counts,
        "attention_rows": summary.get("attention_rows"),
        "visibility_attention": visibility_attention,
        "next_scheduled_post_id": summary.get("next_scheduled_post_id"),
        "next_scheduled_at": summary.get("next_scheduled_at"),
        "campaign_click_count": summary.get("campaign_click_count"),
    }
    signature = hashlib.sha256(
        json.dumps(signature_payload, sort_keys=True).encode("utf-8")
    ).hexdigest()[:20]
    detail_parts = [
        f"{status_counts.get('ready_for_metric_capture', 0)} ready for metrics",
        f"{status_counts.get('scheduled_future', 0)} scheduled",
        f"{summary.get('campaign_click_count', 0)} tracked clicks",
    ]
    if visibility_attention:
        detail_parts.append(f"{visibility_attention} visibility checks need attention")

    return {
        "sourceEventId": f"brand-growth:{signature}",
        "eventType": "lily_roo.brand_growth_report",
        "severity": "warning" if visibility_attention else "info",
        "title": "Lily Roo report refreshed",
        "detail": " · ".join(detail_parts),
        "occurredAt": readout.get("generated_at"),
        "metadata": signature_payload,
    }


def main() -> int:
    secret = os.environ.get("FAMOUS_ADMIN_ACTIVITY_SECRET", "").strip()
    if not secret or not READOUT.exists():
        print("Master activity skipped: secret or brand-growth readout is unavailable.")
        return 0

    event = build_event(json.loads(READOUT.read_text(encoding="utf-8")))
    if not event.get("occurredAt"):
        print("Master activity skipped: brand-growth readout has no generated timestamp.")
        return 0

    base_url = os.environ.get("FAMOUS_ADMIN_ACTIVITY_URL", DEFAULT_ADMIN_URL).rstrip("/")
    request = urllib.request.Request(
        f"{base_url}/api/activity/ingest/lily-roo",
        data=json.dumps(event).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {secret}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
            print(
                "Master activity published: "
                f"{payload.get('accepted', 0)} accepted, {payload.get('duplicates', 0)} duplicate."
            )
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        print(f"::warning::Master activity could not be published: {error}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
