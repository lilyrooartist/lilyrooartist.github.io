#!/usr/bin/env python3
"""Copy new AOL inbox messages into Gmail over IMAP.

This is intentionally small and dependency-free so it can run from cron,
launchd, or a Codex automation without a virtualenv.
"""

from __future__ import annotations

import argparse
import email.utils
import hashlib
import imaplib
import json
import re
import ssl
import sys
import time
from dataclasses import dataclass
from email import policy
from email.parser import BytesParser
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = REPO_ROOT.parent
DEFAULT_ENV = WORKSPACE_ROOT / "secrets" / "aol-gmail-bridge.env"
DEFAULT_STATE = WORKSPACE_ROOT / "secrets" / "aol-gmail-bridge-state.json"


@dataclass(frozen=True)
class BridgeConfig:
    aol_email: str
    aol_password: str
    aol_host: str
    aol_port: int
    aol_mailbox: str
    gmail_email: str
    gmail_password: str
    gmail_host: str
    gmail_port: int
    gmail_mailbox: str
    state_path: Path


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def config_from_env(env_path: Path) -> BridgeConfig:
    values = load_env(env_path)
    missing = [
        name
        for name in ("AOL_APP_PASSWORD", "GMAIL_APP_PASSWORD")
        if not values.get(name)
    ]
    if missing:
        raise SystemExit(
            "Missing required secrets in "
            f"{env_path}: {', '.join(missing)}. "
            "Create app passwords and add them before running the bridge."
        )

    state_path = Path(values.get("STATE_PATH", str(DEFAULT_STATE))).expanduser()
    if not state_path.is_absolute():
        state_path = (REPO_ROOT / state_path).resolve()

    return BridgeConfig(
        aol_email=values.get("AOL_EMAIL", "lilyroo.artist@aol.com"),
        aol_password=values["AOL_APP_PASSWORD"],
        aol_host=values.get("AOL_IMAP_HOST", "imap.aol.com"),
        aol_port=int(values.get("AOL_IMAP_PORT", "993")),
        aol_mailbox=values.get("AOL_MAILBOX", "INBOX"),
        gmail_email=values.get("GMAIL_EMAIL", "lilyroo.artist@gmail.com"),
        gmail_password=values["GMAIL_APP_PASSWORD"],
        gmail_host=values.get("GMAIL_IMAP_HOST", "imap.gmail.com"),
        gmail_port=int(values.get("GMAIL_IMAP_PORT", "993")),
        gmail_mailbox=values.get("GMAIL_MAILBOX", "INBOX"),
        state_path=state_path,
    )


def ssl_context() -> ssl.SSLContext:
    return ssl.create_default_context()


def connect(host: str, port: int, username: str, password: str) -> imaplib.IMAP4_SSL:
    client = imaplib.IMAP4_SSL(host, port, ssl_context=ssl_context())
    typ, data = client.login(username, password)
    if typ != "OK":
        raise RuntimeError(f"IMAP login failed for {username}: {data!r}")
    return client


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"version": 1, "mailboxes": {}}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"State file is not valid JSON: {path}") from exc
    if not isinstance(state, dict):
        raise RuntimeError(f"State file root must be an object: {path}")
    state.setdefault("version", 1)
    state.setdefault("mailboxes", {})
    return state


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass


def selected_uidvalidity(client: imaplib.IMAP4_SSL) -> str:
    typ, data = client.response("UIDVALIDITY")
    if typ == "OK" and data:
        return data[-1].decode("ascii", errors="ignore")
    return ""


def select_mailbox(client: imaplib.IMAP4_SSL, mailbox: str) -> tuple[int, str]:
    typ, data = client.select(mailbox, readonly=True)
    if typ != "OK":
        raise RuntimeError(f"Could not select AOL mailbox {mailbox!r}: {data!r}")
    count = int(data[0] or 0)
    return count, selected_uidvalidity(client)


def uid_search(client: imaplib.IMAP4_SSL, query: Iterable[str]) -> list[int]:
    typ, data = client.uid("SEARCH", None, *query)
    if typ != "OK":
        raise RuntimeError(f"AOL UID search failed: {data!r}")
    raw = data[0] or b""
    return [int(uid) for uid in raw.split() if uid.isdigit()]


def fetch_message(client: imaplib.IMAP4_SSL, uid: int) -> tuple[bytes, str]:
    typ, data = client.uid("FETCH", str(uid), "(RFC822 INTERNALDATE FLAGS)")
    if typ != "OK":
        raise RuntimeError(f"Fetch failed for AOL UID {uid}: {data!r}")

    message = b""
    fetch_meta = ""
    for part in data:
        if isinstance(part, tuple):
            fetch_meta = part[0].decode("utf-8", errors="ignore")
            message = part[1]
            break
    if not message:
        raise RuntimeError(f"Fetch returned no message bytes for AOL UID {uid}")
    return message, fetch_meta


def parse_internaldate(fetch_meta: str) -> str | None:
    match = re.search(r'INTERNALDATE "([^"]+)"', fetch_meta)
    if not match:
        return None
    return f'"{match.group(1)}"'


def parse_flags(fetch_meta: str) -> str | None:
    flags_match = re.search(r"FLAGS \(([^)]*)\)", fetch_meta)
    if not flags_match:
        return None
    flags = [flag for flag in flags_match.group(1).split() if flag == r"\Seen"]
    return " ".join(flags) if flags else None


def message_digest(raw_message: bytes) -> str:
    return hashlib.sha256(raw_message).hexdigest()


def message_summary(raw_message: bytes) -> dict[str, str]:
    msg = BytesParser(policy=policy.default).parsebytes(raw_message)
    parsed_date = email.utils.parsedate_to_datetime(msg.get("Date", "")) if msg.get("Date") else None
    return {
        "from": str(msg.get("From", ""))[:160],
        "subject": str(msg.get("Subject", ""))[:200],
        "date": parsed_date.isoformat() if parsed_date else str(msg.get("Date", ""))[:80],
        "message_id": str(msg.get("Message-ID", ""))[:200],
    }


def append_to_gmail(
    client: imaplib.IMAP4_SSL,
    mailbox: str,
    raw_message: bytes,
    flags: str | None,
    internal_date: str | None,
) -> None:
    typ, data = client.append(mailbox, flags, internal_date, raw_message)
    if typ != "OK":
        raise RuntimeError(f"Gmail append failed for {mailbox!r}: {data!r}")


def mailbox_state_key(cfg: BridgeConfig, uidvalidity: str) -> str:
    return f"{cfg.aol_email}:{cfg.aol_mailbox}:uidvalidity={uidvalidity or 'unknown'}"


def trim_seen_hashes(box_state: dict, keep: int = 5000) -> None:
    hashes = box_state.get("copied_hashes", [])
    if isinstance(hashes, list) and len(hashes) > keep:
        box_state["copied_hashes"] = hashes[-keep:]


def run_bridge(args: argparse.Namespace) -> dict:
    cfg = config_from_env(Path(args.env).expanduser())
    state = load_state(cfg.state_path)

    aol = connect(cfg.aol_host, cfg.aol_port, cfg.aol_email, cfg.aol_password)
    gmail = None
    try:
        if args.check_logins:
            gmail = connect(cfg.gmail_host, cfg.gmail_port, cfg.gmail_email, cfg.gmail_password)
            try:
                gmail.select(cfg.gmail_mailbox, readonly=True)
            except Exception:
                pass
            return {
                "ok": True,
                "mode": "check_logins",
                "aol_login": "ok",
                "gmail_login": "ok",
                "aol_email": cfg.aol_email,
                "gmail_email": cfg.gmail_email,
            }

        total, uidvalidity = select_mailbox(aol, cfg.aol_mailbox)
        key = mailbox_state_key(cfg, uidvalidity)
        box_state = state["mailboxes"].setdefault(
            key,
            {"last_uid": 0, "copied_hashes": [], "initialized_at": None},
        )
        last_uid = int(box_state.get("last_uid") or 0)
        current_uids = uid_search(aol, ["ALL"])
        current_max = max(current_uids) if current_uids else 0

        if not box_state.get("initialized_at") and args.copy_existing == "none":
            if args.dry_run:
                return {
                    "ok": True,
                    "mode": "would_initialize",
                    "message": (
                        "State is not initialized. A real run would record the current AOL UID "
                        "without copying existing mail."
                    ),
                    "aol_mailbox": cfg.aol_mailbox,
                    "aol_message_count": total,
                    "last_uid": current_max,
                    "state_path": str(cfg.state_path),
                }
            box_state["last_uid"] = current_max
            box_state["initialized_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            save_state(cfg.state_path, state)
            return {
                "ok": True,
                "mode": "initialized",
                "message": "Initialized state without copying existing mail. Future runs copy new AOL messages.",
                "aol_mailbox": cfg.aol_mailbox,
                "aol_message_count": total,
                "last_uid": current_max,
                "state_path": str(cfg.state_path),
            }

        if args.copy_existing == "unread":
            uids = uid_search(aol, ["UNSEEN"])
        elif args.copy_existing == "all":
            uids = current_uids
        else:
            uids = uid_search(aol, [f"UID {last_uid + 1}:*"]) if current_max > last_uid else []

        if args.max_messages:
            uids = uids[: args.max_messages]

        copied_hashes = set(box_state.get("copied_hashes") or [])
        copied = []
        skipped = 0

        if not args.dry_run:
            gmail = connect(cfg.gmail_host, cfg.gmail_port, cfg.gmail_email, cfg.gmail_password)

        for uid in uids:
            raw_message, fetch_meta = fetch_message(aol, uid)
            digest = message_digest(raw_message)
            summary = {"uid": uid, **message_summary(raw_message)}
            if digest in copied_hashes:
                skipped += 1
                continue

            if args.dry_run:
                copied.append({**summary, "dry_run": True})
                continue

            assert gmail is not None
            append_to_gmail(
                gmail,
                cfg.gmail_mailbox,
                raw_message,
                parse_flags(fetch_meta),
                parse_internaldate(fetch_meta),
            )
            copied_hashes.add(digest)
            copied.append(summary)
            box_state["last_uid"] = max(int(box_state.get("last_uid") or 0), uid)
            box_state["copied_hashes"] = sorted(copied_hashes)
            box_state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            trim_seen_hashes(box_state)
            save_state(cfg.state_path, state)

        if not args.dry_run and current_max > int(box_state.get("last_uid") or 0):
            box_state["last_uid"] = current_max
            box_state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            save_state(cfg.state_path, state)

        return {
            "ok": True,
            "mode": "dry_run" if args.dry_run else "copy",
            "aol_mailbox": cfg.aol_mailbox,
            "gmail_mailbox": cfg.gmail_mailbox,
            "candidate_count": len(uids),
            "copied_count": len(copied),
            "skipped_duplicates": skipped,
            "copied": copied,
            "last_uid": box_state.get("last_uid", 0),
            "state_path": str(cfg.state_path),
        }
    finally:
        try:
            aol.logout()
        except Exception:
            pass
        if gmail is not None:
            try:
                gmail.logout()
            except Exception:
                pass


def main() -> int:
    parser = argparse.ArgumentParser(description="Copy new AOL inbox messages into Gmail via IMAP.")
    parser.add_argument("--env", default=str(DEFAULT_ENV), help="Path to bridge env file.")
    parser.add_argument(
        "--copy-existing",
        choices=["none", "unread", "all"],
        default="none",
        help=(
            "First-run behavior. Default 'none' initializes state only. "
            "'unread' copies current unread AOL messages. 'all' copies all current mailbox messages."
        ),
    )
    parser.add_argument("--dry-run", action="store_true", help="List candidate messages without copying.")
    parser.add_argument("--check-logins", action="store_true", help="Verify AOL and Gmail IMAP logins only.")
    parser.add_argument("--max-messages", type=int, default=50, help="Maximum messages to process per run.")
    args = parser.parse_args()

    try:
        print(json.dumps(run_bridge(args), indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
