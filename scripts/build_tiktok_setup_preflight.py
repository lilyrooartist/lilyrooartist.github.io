#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from social_exec_common import REPO_ROOT, SOCIAL_ENV, load_env


ROOT = REPO_ROOT
READINESS = ROOT / "data" / "executor_readiness_snapshot.json"
PLATFORM_REPAIR = ROOT / "data" / "platform_repair_status.json"
WRANGLER_CONFIG = ROOT / "workers" / "social-executor" / "wrangler.jsonc"
OUT = ROOT / "data" / "tiktok_setup_preflight.json"
REPORT = ROOT / "admin" / "reports" / "tiktok-setup-preflight.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"

REQUIRED_REFRESH_SECRETS = ["TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REFRESH_TOKEN"]
OPTIONAL_ACCESS_TOKEN = "TIKTOK_ACCESS_TOKEN"


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def wrangler_var(name: str) -> str:
    if not WRANGLER_CONFIG.exists():
        return ""
    text = WRANGLER_CONFIG.read_text(encoding="utf-8")
    match = re.search(rf'"{re.escape(name)}"\s*:\s*"([^"]*)"', text)
    return match.group(1).strip() if match else ""


def check(name: str, status: str, detail: str, command: str = "") -> dict:
    return {
        "name": name,
        "status": status,
        "detail": detail,
        "command": command,
    }


def local_secret_presence() -> dict:
    env = load_env(SOCIAL_ENV)
    names = REQUIRED_REFRESH_SECRETS + [OPTIONAL_ACCESS_TOKEN]
    return {name: bool(str(env.get(name) or "").strip()) for name in names}


def build_payload() -> dict:
    readiness = read_json(READINESS, {})
    platform_repair = read_json(PLATFORM_REPAIR, {})
    tiktok_readiness = (((readiness.get("payload") or {}).get("platforms") or {}).get("tiktok") or {})
    presence = local_secret_presence()
    local_missing = [name for name in REQUIRED_REFRESH_SECRETS if not presence.get(name)]
    worker_missing = tiktok_readiness.get("missing_secrets") or []
    public_posting = tiktok_readiness.get("public_posting_approved")
    if public_posting is None:
        public_posting = wrangler_var("TIKTOK_PUBLIC_POSTING_APPROVED") == "true"
    default_privacy = tiktok_readiness.get("default_privacy") or wrangler_var("TIKTOK_DEFAULT_PRIVACY") or "PUBLIC_TO_EVERYONE"
    refresh_config_present = bool(tiktok_readiness.get("refresh_config_present"))
    access_token_present = bool(tiktok_readiness.get("access_token_present"))
    preflight_checks = [
        check(
            "local_refresh_credentials",
            "pass" if not local_missing else "blocked",
            "Local refresh credentials are present." if not local_missing else f"{SOCIAL_ENV.relative_to(ROOT.parent)} is missing: {', '.join(local_missing)}.",
            "python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN",
        ),
        check(
            "worker_refresh_credentials",
            "pass" if not worker_missing else "blocked",
            "Worker readiness reports TikTok refresh credentials present." if not worker_missing else f"Worker readiness reports missing secrets: {', '.join(worker_missing)}.",
            "python3 scripts/capture_executor_readiness.py",
        ),
        check(
            "worker_token_path",
            "pass" if access_token_present or refresh_config_present else "blocked",
            "Worker has either an access token or refresh credentials available." if access_token_present or refresh_config_present else "Worker has neither access token nor refresh credentials.",
            "python3 scripts/capture_executor_readiness.py",
        ),
        check(
            "public_posting_approval",
            "pass" if public_posting is True else "blocked",
            "TikTok public posting approval is enabled." if public_posting is True else "TikTok public posting approval is not enabled.",
            "",
        ),
        check(
            "default_privacy",
            "pass" if default_privacy else "review",
            f"TikTok default privacy is {default_privacy}.",
            "",
        ),
        check(
            "admin_refresh_after_repair",
            "waiting",
            "After credentials and public posting approval are fixed, refresh Admin to recapture readiness, execution, blocker, handoff, and consistency state.",
            "python3 scripts/refresh_promo_admin.py",
        ),
    ]
    blocked = [item for item in preflight_checks if item["status"] == "blocked"]
    ready_to_push = not local_missing
    ready_to_post = not blocked
    repair_rows = [
        row for row in platform_repair.get("rows") or []
        if str(row.get("platform") or "").lower() == "tiktok"
    ]
    push_preview = "python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN"
    push_apply = "python3 scripts/push_social_worker_secrets.py TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN && python3 scripts/refresh_promo_admin.py"
    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "local_secret_source": str(SOCIAL_ENV.relative_to(ROOT.parent)),
            "executor_readiness": str(READINESS.relative_to(ROOT)),
            "platform_repair_status": str(PLATFORM_REPAIR.relative_to(ROOT)),
            "wrangler_config": str(WRANGLER_CONFIG.relative_to(ROOT)),
        },
        "summary": {
            "status": "ready" if ready_to_post else "blocked",
            "check_count": len(preflight_checks),
            "blocked_count": len(blocked),
            "ready_to_push_worker_secrets": ready_to_push,
            "ready_to_post_publicly": ready_to_post,
            "local_missing_secrets": local_missing,
            "worker_missing_secrets": worker_missing,
            "public_posting_approved": public_posting,
            "default_privacy": default_privacy,
            "push_preview_command": push_preview,
            "push_apply_command": push_apply if ready_to_push else "",
            "refresh_command": "python3 scripts/refresh_promo_admin.py",
            "platform_repair_rows": len(repair_rows),
        },
        "checks": preflight_checks,
        "redaction": "Secret values are never written to this preflight; only presence booleans are recorded.",
    }


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# TikTok Setup Preflight - Lily Roo",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Status: **{summary['status']}**",
        f"- Checks: **{summary['check_count']}**",
        f"- Blocked checks: **{summary['blocked_count']}**",
        f"- Ready to push worker secrets: **{summary['ready_to_push_worker_secrets']}**",
        f"- Ready to post publicly: **{summary['ready_to_post_publicly']}**",
        f"- Public posting approved: **{summary['public_posting_approved']}**",
        f"- Default privacy: **{summary['default_privacy']}**",
        "",
        "## Checks",
    ]
    for item in payload["checks"]:
        lines.append(f"- **{item['name']}**: `{item['status']}`")
        lines.append(f"  - {item['detail']}")
        if item.get("command"):
            lines.append(f"  - Command: `{item['command']}`")
    lines.extend([
        "",
        "## Commands",
        f"- Preview local secrets: `{summary['push_preview_command']}`",
        f"- Push after local credentials are present: `{summary['push_apply_command'] or 'not available until local secrets exist'}`",
        f"- Refresh after repair: `{summary['refresh_command']}`",
        "",
        "## Guardrails",
        "- This preflight does not push secrets, approve posts, publish posts, or write credentials.",
        "- Secret values are redacted; only presence and readiness booleans are recorded.",
        "- Public posting approval must be confirmed before TikTok auto-posting is treated as ready.",
        "",
    ])
    return "\n".join(lines)


def replace_json_embed(html: str, block_id: str, payload) -> str:
    marker = f'<script type="application/json" id="{block_id}">'
    end_marker = "</script>"
    encoded = json.dumps(payload, indent=2, ensure_ascii=False)
    start = html.find(marker)
    if start == -1:
        return html.replace("<script>", f"\n{marker}{encoded}{end_marker}\n\n<script>", 1)
    start_content = start + len(marker)
    end = html.find(end_marker, start_content)
    if end == -1:
        raise RuntimeError(f"Could not find end marker for {block_id}")
    return html[:start_content] + encoded + html[end:]


def replace_text_embed(html: str, block_id: str, content: str) -> str:
    marker = f'<script type="text/plain" id="{block_id}">'
    end_marker = "</script>"
    start = html.find(marker)
    if start == -1:
        return html.replace("<script>", f"\n{marker}{content.rstrip()}{end_marker}\n\n<script>", 1)
    start_content = start + len(marker)
    end = html.find(end_marker, start_content)
    if end == -1:
        raise RuntimeError(f"Could not find end marker for {block_id}")
    return html[:start_content] + content.rstrip() + html[end:]


def sync_admin(payload: dict, markdown: str) -> None:
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    html = replace_json_embed(html, "embedded-tiktok-setup-preflight", payload)
    html = replace_text_embed(html, "embedded-tiktok-setup-preflight-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    payload = build_payload()
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(payload)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(payload, markdown)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), **payload["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
