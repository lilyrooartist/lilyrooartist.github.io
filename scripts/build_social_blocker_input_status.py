#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from social_exec_common import REPO_ROOT, SOCIAL_ENV, load_env


OUT = REPO_ROOT / "data" / "social_blocker_input_status.json"
REPORT = REPO_ROOT / "admin" / "reports" / "social-blocker-input-status.md"
TEMPLATE = REPO_ROOT / "data" / "social_blocker_secret_template.env"
GITHUB_SECRET_PRESENCE = REPO_ROOT / "data" / "github_actions_secret_presence.json"
ADMIN_INDEX = REPO_ROOT / "admin" / "index.html"


GROUPS = [
    {
        "id": "scheduler_auth",
        "label": "Scheduler and executor auth",
        "required_any": ["LILYROO_EXECUTOR_BEARER_TOKEN", "EXECUTOR_BEARER_TOKEN", "LILYROO_ADMIN_PASSWORD", "ADMIN_PASSWORD"],
        "required_all": [],
        "github_actions_secrets": ["LILYROO_EXECUTOR_BEARER_TOKEN", "LILYROO_ADMIN_PASSWORD"],
        "unblocks": "Scheduler dry-run, executor readiness capture, and execution history capture.",
        "verify": "python3 scripts/capture_scheduler_dry_run.py && python3 scripts/capture_social_executions.py",
    },
    {
        "id": "instagram_business",
        "label": "Instagram business account",
        "required_any": [],
        "required_all": ["IG_BUSINESS_ACCOUNT_ID"],
        "github_actions_secrets": [],
        "unblocks": "Instagram executor rows after the Worker secret is pushed and readiness is recaptured.",
        "verify": "python3 scripts/check_social_executor_dry_run.py --post-id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM",
    },
    {
        "id": "tiktok_oauth_base",
        "label": "TikTok OAuth app values",
        "required_any": [],
        "required_all": ["TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REDIRECT_URI"],
        "github_actions_secrets": [],
        "unblocks": "TikTok OAuth authorization URL generation and authorization-code exchange.",
        "verify": "python3 scripts/tiktok_oauth_handoff.py --print-auth-url --posting-mode upload",
    },
    {
        "id": "tiktok_upload_tokens",
        "label": "TikTok upload-mode worker secrets",
        "required_any": [],
        "required_all": ["TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REFRESH_TOKEN"],
        "github_actions_secrets": [],
        "unblocks": "TikTok upload-draft automation for the first ready TikTok asset.",
        "verify": "python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN",
    },
    {
        "id": "facebook_identity",
        "label": "Facebook Page identity checkpoint",
        "required_any": [],
        "required_all": [],
        "external_only": True,
        "github_actions_secrets": [],
        "unblocks": "The Facebook executor row blocked by Meta identity confirmation.",
        "verify": "python3 scripts/check_facebook_publishing.py --post-id 'FP-AUTO-265' --check-worker-dry-run",
    },
]


TEMPLATE_KEYS = [
    ("# Scheduler/admin capture auth. At least one auth path must be filled locally and in GitHub Actions secrets.", ""),
    ("LILYROO_EXECUTOR_BEARER_TOKEN", ""),
    ("EXECUTOR_BEARER_TOKEN", ""),
    ("LILYROO_ADMIN_PASSWORD", ""),
    ("ADMIN_PASSWORD", ""),
    ("", ""),
    ("# Instagram/Meta.", ""),
    ("IG_BUSINESS_ACCOUNT_ID", ""),
    ("FB_PAGE_ID", ""),
    ("META_LONG_LIVED_TOKEN", ""),
    ("", ""),
    ("# TikTok upload-mode OAuth.", ""),
    ("TIKTOK_CLIENT_KEY", ""),
    ("TIKTOK_CLIENT_SECRET", ""),
    ("TIKTOK_REDIRECT_URI", ""),
    ("TIKTOK_REFRESH_TOKEN", ""),
    ("TIKTOK_ACCESS_TOKEN", ""),
    ("", ""),
    ("# Direct public TikTok posting stays disabled unless approval is explicit.", ""),
    ("TIKTOK_PUBLIC_POSTING_APPROVED", "false"),
    ("TIKTOK_DEFAULT_PRIVACY", "PUBLIC_TO_EVERYONE"),
]


def write_template() -> None:
    lines = [
        "# Lily Roo social blocker secret template.",
        "# Copy selected values into ../secrets/social_api.env. Do not commit real secret values.",
        "# Generated file is intentionally blank/redacted.",
        "",
    ]
    for key, default in TEMPLATE_KEYS:
        if not key:
            lines.append("")
        elif key.startswith("#"):
            lines.append(key)
        else:
            lines.append(f"{key}={default}")
    TEMPLATE.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def present(env: dict[str, str], name: str) -> bool:
    return bool(str(env.get(name) or "").strip())


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def github_secret_status(secret_names: list[str], github_presence: dict) -> dict:
    presence = github_presence.get("presence") or {}
    if not secret_names:
        return {"status": "not_required", "presence": {}, "missing": []}
    if not github_presence:
        return {"status": "unknown", "presence": {name: False for name in secret_names}, "missing": secret_names}
    result = {name: bool(presence.get(name)) for name in secret_names}
    missing = [name for name, is_present in result.items() if not is_present]
    return {
        "status": "ready" if not missing else "missing",
        "presence": result,
        "missing": missing,
        "source_status": (github_presence.get("summary") or {}).get("status") or "unknown",
    }


def build_group(group: dict, env: dict[str, str], github_presence: dict) -> dict:
    required_all = group.get("required_all") or []
    required_any = group.get("required_any") or []
    github_secrets = group.get("github_actions_secrets") or []
    missing_all = [name for name in required_all if not present(env, name)]
    any_present = any(present(env, name) for name in required_any) if required_any else True
    github_status = github_secret_status(github_secrets, github_presence)
    status = "external_action_needed" if group.get("external_only") else "ready"
    if missing_all or not any_present:
        status = "missing_local_input"
    if group.get("external_only"):
        next_action = "Complete the external platform checkpoint, then rerun the verification command."
    elif status == "ready":
        next_action = "Run the verification command and refresh admin evidence."
    elif missing_all:
        next_action = f"Add {', '.join(missing_all)} to {SOCIAL_ENV}."
    else:
        next_action = f"Add one of {', '.join(required_any)} to {SOCIAL_ENV}."
    return {
        "id": group["id"],
        "label": group["label"],
        "status": status,
        "required_all": required_all,
        "required_any": required_any,
        "github_actions_secrets": github_secrets,
        "github_actions_secret_status": github_status,
        "presence": {name: present(env, name) for name in sorted(set(required_all + required_any))},
        "missing_all": missing_all,
        "any_present": any_present,
        "external_only": bool(group.get("external_only")),
        "unblocks": group["unblocks"],
        "verification_command": group["verify"],
        "next_action": next_action,
    }


def build_packet() -> dict:
    write_template()
    env = load_env(SOCIAL_ENV)
    github_presence = read_json(GITHUB_SECRET_PRESENCE)
    groups = [build_group(group, env, github_presence) for group in GROUPS]
    missing = [group for group in groups if group["status"] == "missing_local_input"]
    external = [group for group in groups if group["status"] == "external_action_needed"]
    ready = [group for group in groups if group["status"] == "ready"]
    github_missing = [
        secret
        for group in groups
        for secret in (group.get("github_actions_secret_status") or {}).get("missing", [])
    ]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "redaction": "Only key presence is reported; secret values are never written to generated files.",
        "source": {
            "local_secret_source": str(SOCIAL_ENV.relative_to(REPO_ROOT.parent)),
            "template": str(TEMPLATE.relative_to(REPO_ROOT)),
            "github_actions_secret_presence": str(GITHUB_SECRET_PRESENCE.relative_to(REPO_ROOT)),
        },
        "summary": {
            "status": "missing_local_input" if missing else "external_action_needed" if external else "ready",
            "group_count": len(groups),
            "ready_count": len(ready),
            "missing_local_input_count": len(missing),
            "external_action_needed_count": len(external),
            "github_actions_missing_secret_count": len(set(github_missing)),
            "github_actions_secret_presence_status": (github_presence.get("summary") or {}).get("status") or "unknown",
            "local_secret_env_exists": SOCIAL_ENV.exists(),
            "template_path": str(TEMPLATE.relative_to(REPO_ROOT)),
            "next_action": (missing[0]["next_action"] if missing else external[0]["next_action"] if external else "Run verification commands and refresh the admin dashboard."),
        },
        "groups": groups,
    }


def build_markdown(packet: dict) -> str:
    summary = packet["summary"]
    lines = [
        "# Social Blocker Input Status - Lily Roo",
        "",
        f"Generated: {packet['generated_at']}",
        "",
        "## Summary",
        f"- Status: **{summary['status']}**",
        f"- Ready groups: **{summary['ready_count']} / {summary['group_count']}**",
        f"- Missing local input: **{summary['missing_local_input_count']}**",
        f"- External action needed: **{summary['external_action_needed_count']}**",
        f"- GitHub Actions missing secrets: **{summary['github_actions_missing_secret_count']}**",
        f"- Local secret env exists: **{summary['local_secret_env_exists']}**",
        f"- Template: `{summary['template_path']}`",
        f"- Next action: {summary['next_action']}",
        "",
        "## Groups",
    ]
    for group in packet["groups"]:
        lines.append(f"- **{group['label']}** - `{group['status']}`")
        if group.get("required_all"):
            lines.append(f"  - Required all: {', '.join(group['required_all'])}")
        if group.get("required_any"):
            lines.append(f"  - Required one of: {', '.join(group['required_any'])}")
        if group.get("github_actions_secrets"):
            lines.append(f"  - GitHub Actions secrets: {', '.join(group['github_actions_secrets'])}")
            lines.append(f"  - GitHub Actions status: {group['github_actions_secret_status']['status']}")
        lines.append(f"  - Unblocks: {group['unblocks']}")
        lines.append(f"  - Verify: `{group['verification_command']}`")
        lines.append(f"  - Next: {group['next_action']}")
    lines.extend([
        "",
        "## Guardrails",
        "- Generated files report presence only. They must never contain real secret values.",
        "- Put real values in `../secrets/social_api.env` locally and GitHub Actions secrets where listed.",
        "- Push Worker secrets only after local dry-runs prove the required values are present.",
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


def sync_admin(packet: dict, markdown: str) -> None:
    if not ADMIN_INDEX.exists():
        return
    html = ADMIN_INDEX.read_text(encoding="utf-8")
    html = replace_json_embed(html, "embedded-social-blocker-input-status", packet)
    html = replace_text_embed(html, "embedded-social-blocker-input-status-report", markdown)
    ADMIN_INDEX.write_text(html, encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = build_markdown(packet)
    REPORT.write_text(markdown, encoding="utf-8")
    sync_admin(packet, markdown)
    print(json.dumps({
        "output": str(OUT.relative_to(REPO_ROOT)),
        "status": packet["summary"]["status"],
        "missing_local_input_count": packet["summary"]["missing_local_input_count"],
        "external_action_needed_count": packet["summary"]["external_action_needed_count"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
