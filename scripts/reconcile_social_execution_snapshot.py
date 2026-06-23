#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from social_exec_common import current_execution_rows, queue_index


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data" / "social_execution_snapshot.json"


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def dedupe(rows: list[dict]) -> list[dict]:
    seen = set()
    result = []
    for row in rows:
        key = (row.get("post_id") or "", row.get("platform") or "", row.get("status") or "", row.get("reason") or "")
        if key in seen:
            continue
        seen.add(key)
        result.append(row)
    return result


def reconcile(snapshot: dict) -> tuple[dict, dict]:
    summary = dict(snapshot.get("summary") or {})
    scheduled = queue_index()
    categories = [
        "latest_posted",
        "approval_needed",
        "platform_fix_needed",
        "manual_handoff_needed",
        "latest_attention",
    ]
    superseded = []
    current_by_category = {}
    for category in categories:
        current, stale = current_execution_rows(summary.get(category) or [], scheduled)
        current_by_category[category] = current
        superseded.extend(stale)
    superseded = dedupe(superseded)

    current_rows = dedupe(
        current_by_category["latest_posted"]
        + current_by_category["approval_needed"]
        + current_by_category["platform_fix_needed"]
        + current_by_category["manual_handoff_needed"]
        + current_by_category["latest_attention"]
    )
    status_counts = Counter(row.get("status") or "unknown" for row in current_rows)
    platform_counts = Counter(row.get("platform") or "Unknown" for row in current_rows)

    summary.update(current_by_category)
    summary["posted_count"] = len(current_by_category["latest_posted"])
    summary["attention_count"] = len(dedupe(
        current_by_category["approval_needed"]
        + current_by_category["platform_fix_needed"]
        + current_by_category["manual_handoff_needed"]
        + current_by_category["latest_attention"]
    ))
    summary["approval_needed_count"] = len(current_by_category["approval_needed"])
    summary["platform_fix_needed_count"] = len(current_by_category["platform_fix_needed"])
    summary["manual_handoff_needed_count"] = len(current_by_category["manual_handoff_needed"])
    summary["current_execution_count"] = len(current_rows)
    summary["superseded_execution_count"] = len(superseded)
    summary["superseded_executions"] = superseded[:10]
    summary["status_counts"] = dict(sorted(status_counts.items()))
    summary["platform_counts"] = dict(sorted(platform_counts.items()))

    output = dict(snapshot)
    output["summary"] = summary
    output["reconciled_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    output["reconciliation"] = {
        "source": "current scheduled_posts.csv",
        "superseded_execution_count": len(superseded),
        "guardrail": "Rows are only removed from active attention lists when their post_id is gone from the queue or the queue platform/type has superseded the captured execution.",
    }
    report = {
        "superseded_execution_count": len(superseded),
        "manual_handoff_needed_count": summary["manual_handoff_needed_count"],
        "platform_fix_needed_count": summary["platform_fix_needed_count"],
        "superseded_post_ids": [row.get("post_id") for row in superseded],
    }
    return output, report


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile captured social execution history against the current queue without contacting APIs.")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--write-snapshot", action="store_true")
    args = parser.parse_args()

    snapshot = read_json(SNAPSHOT, {})
    output, report = reconcile(snapshot)
    should_write = bool(args.apply or args.write_snapshot)
    report["apply"] = bool(args.apply)
    report["write_snapshot"] = bool(args.write_snapshot)
    if should_write:
        SNAPSHOT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        report["output"] = str(SNAPSHOT.relative_to(ROOT))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
