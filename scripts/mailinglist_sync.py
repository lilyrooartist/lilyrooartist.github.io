#!/usr/bin/env python3
"""Mailing list sync: raw Google Form responses sheet -> local deduped master -> Clean sheet.

Auth: Google Service Account JSON.

Reads the raw responses tab (by gid), dedupes by email, writes:
- Google Sheet tab "Clean" (or configured title)
- local data/mailinglist/master_deduped.csv + .json + state.json

Usage:
  source .venv-mailingsync/bin/activate
  python scripts/mailinglist_sync.py --config mailinglist_sync_config.json
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from dateutil import parser as dateparser
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def sheets_service(sa_path: str):
    creds = service_account.Credentials.from_service_account_file(sa_path, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def get_spreadsheet(service, spreadsheet_id: str) -> dict:
    return service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()


def gid_to_title(meta: dict, gid: int) -> str:
    for s in meta.get("sheets", []):
        props = s.get("properties", {})
        if int(props.get("sheetId")) == int(gid):
            return props.get("title")
    raise RuntimeError(f"Could not find sheet with gid={gid}")


def ensure_sheet(service, spreadsheet_id: str, title: str) -> int:
    meta = get_spreadsheet(service, spreadsheet_id)
    for s in meta.get("sheets", []):
        props = s.get("properties", {})
        if props.get("title") == title:
            return int(props.get("sheetId"))

    resp = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "requests": [
                {
                    "addSheet": {
                        "properties": {
                            "title": title,
                            "gridProperties": {"frozenRowCount": 1},
                        }
                    }
                }
            ]
        },
    ).execute()

    return int(resp["replies"][0]["addSheet"]["properties"]["sheetId"])


def a1_range(title: str, rng: str) -> str:
    safe = title.replace("'", "''")
    return f"'{safe}'!{rng}"


def read_values(service, spreadsheet_id: str, sheet_title: str) -> List[List[str]]:
    resp = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=a1_range(sheet_title, "A:ZZ"))
        .execute()
    )
    return resp.get("values", [])


def normalize_header(h: str) -> str:
    h = (h or "").strip()
    h = re.sub(r"\s+", " ", h)
    return h


def find_col(headers: List[str], candidates: List[str]) -> Optional[int]:
    lowered = [h.strip().lower() for h in headers]
    for cand in candidates:
        c = cand.lower()
        if c in lowered:
            return lowered.index(c)
    for i, h in enumerate(lowered):
        for cand in candidates:
            if cand.lower() in h:
                return i
    return None


def parse_dt_maybe(s: str) -> Optional[dt.datetime]:
    if not s:
        return None
    try:
        d = dateparser.parse(s)
        if d is None:
            return None
        if d.tzinfo is not None:
            d = d.astimezone(dt.timezone.utc).replace(tzinfo=None)
        return d
    except Exception:
        return None


def dedupe_rows(values: List[List[str]]) -> Tuple[List[str], List[List[str]], dict]:
    if not values:
        return [], [], {"total_rows": 0, "unique": 0, "dropped": 0}

    headers = [normalize_header(x) for x in values[0]]
    rows = values[1:]

    email_idx = find_col(headers, ["email", "email address", "e-mail", "e-mail address"])
    if email_idx is None:
        raise RuntimeError(
            "Couldn't find an Email column in the header row. "
            f"Headers seen: {headers}"
        )

    ts_idx = find_col(headers, ["timestamp", "submitted at", "submission time", "date"])

    best_by_email: Dict[str, Tuple[int, Optional[dt.datetime], List[str]]] = {}

    for i, r in enumerate(rows):
        if len(r) < len(headers):
            r = r + [""] * (len(headers) - len(r))

        email = (r[email_idx] or "").strip().lower()
        if not email:
            continue

        tsv = None
        if ts_idx is not None and ts_idx < len(r):
            tsv = parse_dt_maybe(r[ts_idx])

        prev = best_by_email.get(email)
        if prev is None:
            best_by_email[email] = (i, tsv, r)
            continue

        prev_i, prev_ts, _prev_row = prev

        if tsv and prev_ts:
            if tsv > prev_ts:
                best_by_email[email] = (i, tsv, r)
        elif tsv and not prev_ts:
            best_by_email[email] = (i, tsv, r)
        elif (not tsv) and (not prev_ts) and i > prev_i:
            best_by_email[email] = (i, tsv, r)

    items = list(best_by_email.items())

    def sort_key(kv):
        _email, (_i, _ts, _r) = kv
        return (_ts or dt.datetime.min, _i)

    items.sort(key=sort_key)

    out_rows = [kv[1][2] for kv in items]
    stats = {"total_rows": len(rows), "unique": len(out_rows), "dropped": len(rows) - len(out_rows)}
    return headers, out_rows, stats


def write_clean_sheet(service, spreadsheet_id: str, clean_title: str, headers: List[str], rows: List[List[str]]):
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id, range=a1_range(clean_title, "A:ZZ"), body={}
    ).execute()

    body = {"values": [headers] + rows}
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=a1_range(clean_title, "A1"),
        valueInputOption="RAW",
        body=body,
    ).execute()


def write_local_artifacts(base_dir: Path, headers: List[str], rows: List[List[str]], stats: dict):
    base_dir.mkdir(parents=True, exist_ok=True)

    csv_path = base_dir / "master_deduped.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)

    json_path = base_dir / "master_deduped.json"
    records = []
    for r in rows:
        rr = r + [""] * (len(headers) - len(r))
        records.append({headers[i]: rr[i] for i in range(len(headers))})
    json_path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")

    state = {"updatedAt": dt.datetime.utcnow().isoformat() + "Z", **stats}
    (base_dir / "state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()

    cfg = load_config(args.config)
    spreadsheet_id = cfg["spreadsheet_id"]
    raw_gid = int(cfg["raw_gid"])
    clean_title = cfg.get("clean_sheet_title", "Clean")
    sa_path = cfg["secrets_path"]

    repo_root = Path(__file__).resolve().parents[1]
    sa_abs = repo_root / sa_path

    service = sheets_service(str(sa_abs))

    meta = get_spreadsheet(service, spreadsheet_id)
    raw_title = gid_to_title(meta, raw_gid)

    ensure_sheet(service, spreadsheet_id, clean_title)

    values = read_values(service, spreadsheet_id, raw_title)
    headers, rows, stats = dedupe_rows(values)

    write_clean_sheet(service, spreadsheet_id, clean_title, headers, rows)

    out_dir = repo_root / "data/mailinglist"
    write_local_artifacts(out_dir, headers, rows, stats)

    print(json.dumps({
        "spreadsheet_id": spreadsheet_id,
        "raw_sheet": raw_title,
        "clean_sheet": clean_title,
        **stats,
        "local_dir": str(out_dir)
    }, indent=2))


if __name__ == "__main__":
    main()
