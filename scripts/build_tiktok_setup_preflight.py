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
API_STRATEGY = ROOT / "data" / "tiktok_api_strategy.json"
WRANGLER_CONFIG = ROOT / "workers" / "social-executor" / "wrangler.jsonc"
HANDOFF_TEMPLATE = ROOT / "data" / "tiktok_secret_handoff_template.env"
OAUTH_HANDOFF_SCRIPT = ROOT / "scripts" / "tiktok_oauth_handoff.py"
LOCAL_POST_SCRIPT = ROOT / "scripts" / "post_tiktok_from_queue.py"
OUT = ROOT / "data" / "tiktok_setup_preflight.json"
REPORT = ROOT / "admin" / "reports" / "tiktok-setup-preflight.md"
ADMIN_INDEX = ROOT / "admin" / "index.html"

REQUIRED_REFRESH_SECRETS = ["TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REFRESH_TOKEN"]
OPTIONAL_ACCESS_TOKEN = "TIKTOK_ACCESS_TOKEN"
PUBLIC_POSTING_APPROVAL = "TIKTOK_PUBLIC_POSTING_APPROVED"
BRAND_CONTENT = "TIKTOK_BRAND_CONTENT"
BRAND_ORGANIC = "TIKTOK_BRAND_ORGANIC"
AIGC_LABEL = "TIKTOK_IS_AIGC"
POSTING_MODE = "TIKTOK_POSTING_MODE"
PUBLIC_POSTING_PREVIEW = "python3 scripts/set_tiktok_public_posting_approval.py --approved"
PUBLIC_POSTING_APPLY = "python3 scripts/set_tiktok_public_posting_approval.py --approved --apply"
PUBLIC_POSTING_DEPLOY = "python3 scripts/set_tiktok_public_posting_approval.py --approved --apply --deploy"


def write_handoff_template() -> None:
    lines = [
        "# Lily Roo TikTok secret handoff template",
        "# Posting mode selected: API integration.",
        "# OAuth scopes should include user.info.basic, video.upload, and video.publish.",
        "# Fill values locally in secrets/social_api.env, not in this generated file.",
        "# Keep TIKTOK_PUBLIC_POSTING_APPROVED=false until public posting approval is confirmed.",
        "TIKTOK_CLIENT_KEY=",
        "TIKTOK_CLIENT_SECRET=",
        "TIKTOK_REDIRECT_URI=",
        "TIKTOK_REFRESH_TOKEN=",
        "TIKTOK_ACCESS_TOKEN=",
        "TIKTOK_BRAND_CONTENT=false",
        "TIKTOK_BRAND_ORGANIC=true",
        "TIKTOK_IS_AIGC=true",
        "TIKTOK_POSTING_MODE=upload",
        "TIKTOK_PUBLIC_POSTING_APPROVED=false",
        "TIKTOK_DEFAULT_PRIVACY=PUBLIC_TO_EVERYONE",
        "",
    ]
    HANDOFF_TEMPLATE.write_text("\n".join(lines), encoding="utf-8")


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


def flag_value(name: str, default: bool) -> bool:
    env = load_env(SOCIAL_ENV)
    raw = str(env.get(name) or wrangler_var(name) or "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def check(name: str, status: str, detail: str, command: str = "") -> dict:
    return {
        "name": name,
        "status": status,
        "detail": detail,
        "command": command,
    }


def local_secret_presence() -> dict:
    env = load_env(SOCIAL_ENV)
    names = REQUIRED_REFRESH_SECRETS + [
        "TIKTOK_REDIRECT_URI",
        OPTIONAL_ACCESS_TOKEN,
        PUBLIC_POSTING_APPROVAL,
        BRAND_CONTENT,
        BRAND_ORGANIC,
        AIGC_LABEL,
        POSTING_MODE,
    ]
    return {name: bool(str(env.get(name) or "").strip()) for name in names}


def local_public_posting_approved(presence: dict) -> bool:
    if not presence.get(PUBLIC_POSTING_APPROVAL):
        return False
    return str(load_env(SOCIAL_ENV).get(PUBLIC_POSTING_APPROVAL, "")).strip().lower() == "true"


def build_payload() -> dict:
    write_handoff_template()
    readiness = read_json(READINESS, {})
    platform_repair = read_json(PLATFORM_REPAIR, {})
    strategy = read_json(API_STRATEGY, {})
    tiktok_readiness = (((readiness.get("payload") or {}).get("platforms") or {}).get("tiktok") or {})
    posting_mode = strategy.get("posting_mode") or "api"
    presence = local_secret_presence()
    local_public_approval = local_public_posting_approved(presence)
    local_missing = [name for name in REQUIRED_REFRESH_SECRETS if not presence.get(name)]
    worker_missing = tiktok_readiness.get("missing_secrets") or []
    public_posting = tiktok_readiness.get("public_posting_approved")
    if public_posting is None:
        public_posting = wrangler_var("TIKTOK_PUBLIC_POSTING_APPROVED") == "true"
    default_privacy = tiktok_readiness.get("default_privacy") or wrangler_var("TIKTOK_DEFAULT_PRIVACY") or "PUBLIC_TO_EVERYONE"
    brand_content = bool(tiktok_readiness.get("brand_content_toggle")) if "brand_content_toggle" in tiktok_readiness else flag_value(BRAND_CONTENT, False)
    brand_organic = bool(tiktok_readiness.get("brand_organic_toggle")) if "brand_organic_toggle" in tiktok_readiness else flag_value(BRAND_ORGANIC, True)
    aigc_label = bool(tiktok_readiness.get("aigc_label_enabled")) if "aigc_label_enabled" in tiktok_readiness else flag_value(AIGC_LABEL, True)
    worker_posting_mode = tiktok_readiness.get("posting_mode") or wrangler_var(POSTING_MODE) or "direct"
    refresh_config_present = bool(tiktok_readiness.get("refresh_config_present"))
    access_token_present = bool(tiktok_readiness.get("access_token_present"))
    local_access_token_present = bool(presence.get(OPTIONAL_ACCESS_TOKEN))
    local_refresh_config_present = not local_missing
    oauth_url_missing = [name for name in ["TIKTOK_CLIENT_KEY", "TIKTOK_REDIRECT_URI"] if not presence.get(name)]
    oauth_exchange_missing = [name for name in ["TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REDIRECT_URI"] if not presence.get(name)]
    preflight_checks = [
        check(
            "oauth_authorization_url",
            "pass" if not oauth_url_missing else "blocked",
            "TikTok OAuth authorization URL can be generated locally."
            if not oauth_url_missing
            else f"{SOCIAL_ENV.relative_to(ROOT.parent)} is missing auth URL values: {', '.join(oauth_url_missing)}.",
            "python3 scripts/tiktok_oauth_handoff.py --print-auth-url",
        ),
        check(
            "oauth_token_exchange",
            "pass" if not oauth_exchange_missing else "blocked",
            "TikTok OAuth authorization codes can be exchanged locally."
            if not oauth_exchange_missing
            else f"{SOCIAL_ENV.relative_to(ROOT.parent)} is missing token exchange values: {', '.join(oauth_exchange_missing)}.",
            "python3 scripts/tiktok_oauth_handoff.py --exchange-code CODE --apply",
        ),
        check(
            "local_refresh_credentials",
            "pass" if not local_missing else "blocked",
            "Local refresh credentials are present." if not local_missing else f"{SOCIAL_ENV.relative_to(ROOT.parent)} is missing: {', '.join(local_missing)}.",
            "python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN",
        ),
        check(
            "local_posting_token_path",
            "pass" if local_access_token_present or local_refresh_config_present else "blocked",
            "Local TikTok posting helper can obtain an access token from refresh credentials."
            if local_refresh_config_present and not local_access_token_present
            else (
                "Local TikTok posting helper can use an existing access token."
                if local_access_token_present
                else "Local TikTok posting helper needs TIKTOK_ACCESS_TOKEN or refresh credentials."
            ),
            "python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --dry-run",
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
            "TikTok public posting approval is enabled in the Worker."
            if public_posting is True
            else (
                "Local approval is confirmed; run the guarded approval helper and deploy the Worker."
                if local_public_approval
                else "TikTok public posting approval is not enabled."
            ),
            "" if public_posting is True else (PUBLIC_POSTING_APPLY if local_public_approval else PUBLIC_POSTING_PREVIEW),
        ),
        check(
            "default_privacy",
            "pass" if default_privacy else "review",
            f"TikTok default privacy is {default_privacy}.",
            "",
        ),
        check(
            "commercial_disclosure_defaults",
            "pass",
            f"TikTok disclosure defaults are brand_content_toggle={brand_content}, brand_organic_toggle={brand_organic}.",
            "",
        ),
        check(
            "aigc_label_default",
            "pass",
            f"TikTok AI-generated-content label default is {aigc_label}.",
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
    oauth_preview = "python3 scripts/tiktok_oauth_handoff.py"
    oauth_url_command = "python3 scripts/tiktok_oauth_handoff.py --print-auth-url"
    oauth_exchange_command = "python3 scripts/tiktok_oauth_handoff.py --exchange-code CODE --apply"
    refresh_command = "python3 scripts/refresh_promo_admin.py"
    local_post_preview = "python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --dry-run"
    local_upload_preview = "python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --mode upload --dry-run"
    credential_handoff = {
        "status": "ready_to_push" if ready_to_push else "needs_local_values",
        "required_secret_names": REQUIRED_REFRESH_SECRETS,
        "optional_secret_names": [OPTIONAL_ACCESS_TOKEN],
        "local_secret_source": str(SOCIAL_ENV.relative_to(ROOT.parent)),
        "handoff_template_path": str(HANDOFF_TEMPLATE.relative_to(ROOT)),
        "handoff_template_required_names": REQUIRED_REFRESH_SECRETS + ["TIKTOK_REDIRECT_URI", "TIKTOK_PUBLIC_POSTING_APPROVED", "TIKTOK_DEFAULT_PRIVACY"],
        "local_missing_secrets": local_missing,
        "oauth_authorization_url_missing": oauth_url_missing,
        "oauth_token_exchange_missing": oauth_exchange_missing,
        "worker_missing_secrets": worker_missing,
        "oauth_handoff_script": str(OAUTH_HANDOFF_SCRIPT.relative_to(ROOT)),
        "requested_oauth_scopes": ["user.info.basic", "video.upload", "video.publish"],
        "oauth_preview_command": oauth_preview,
        "oauth_authorization_url_command": oauth_url_command,
        "oauth_exchange_command": oauth_exchange_command,
        "local_public_posting_approval_confirmed": local_public_approval,
        "public_posting_approved": public_posting,
        "default_privacy": default_privacy,
        "worker_posting_mode": worker_posting_mode,
        "brand_content_toggle": brand_content,
        "brand_organic_toggle": brand_organic,
        "aigc_label_enabled": aigc_label,
        "dry_run_first_command": push_preview,
        "apply_command": push_apply if ready_to_push else "",
        "public_posting_preview_command": PUBLIC_POSTING_PREVIEW,
        "public_posting_apply_command": PUBLIC_POSTING_APPLY if local_public_approval else "",
        "public_posting_deploy_command": PUBLIC_POSTING_DEPLOY if local_public_approval else "",
        "post_apply_verification_commands": [
            "python3 scripts/capture_executor_readiness.py",
            refresh_command,
            "python3 scripts/validate_content_system.py",
        ],
        "completion_evidence": [
            "data/tiktok_setup_preflight.json reports ready_to_push_worker_secrets true.",
            "data/executor_readiness_snapshot.json reports TikTok refresh configuration present.",
            "data/platform_repair_status.json no longer lists TikTok as blocked by missing credentials.",
        ],
        "redaction": "Secret values are never written here; only required names, missing names, and presence booleans are recorded.",
    }
    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "local_secret_source": str(SOCIAL_ENV.relative_to(ROOT.parent)),
            "api_strategy": str(API_STRATEGY.relative_to(ROOT)),
            "handoff_template": str(HANDOFF_TEMPLATE.relative_to(ROOT)),
            "oauth_handoff_script": str(OAUTH_HANDOFF_SCRIPT.relative_to(ROOT)),
            "local_posting_helper": str(LOCAL_POST_SCRIPT.relative_to(ROOT)),
            "executor_readiness": str(READINESS.relative_to(ROOT)),
            "platform_repair_status": str(PLATFORM_REPAIR.relative_to(ROOT)),
            "wrangler_config": str(WRANGLER_CONFIG.relative_to(ROOT)),
        },
        "summary": {
            "status": "ready" if ready_to_post else "blocked",
            "posting_mode": posting_mode,
            "api_strategy_confirmed": posting_mode == "api",
            "check_count": len(preflight_checks),
            "blocked_count": len(blocked),
            "ready_to_push_worker_secrets": ready_to_push,
            "ready_to_post_publicly": ready_to_post,
            "local_posting_helper_uses_refresh_token": True,
            "local_post_preview_command": local_post_preview,
            "local_upload_preview_command": local_upload_preview,
            "earliest_tiktok_api_path": "video.upload inbox draft; final public URL still requires human publish and URL logging.",
            "local_missing_secrets": local_missing,
            "oauth_authorization_url_missing": oauth_url_missing,
            "oauth_token_exchange_missing": oauth_exchange_missing,
            "worker_missing_secrets": worker_missing,
            "public_posting_approved": public_posting,
            "local_public_posting_approval_confirmed": local_public_approval,
            "default_privacy": default_privacy,
            "worker_posting_mode": worker_posting_mode,
            "brand_content_toggle": brand_content,
            "brand_organic_toggle": brand_organic,
            "aigc_label_enabled": aigc_label,
            "push_preview_command": push_preview,
            "push_apply_command": push_apply if ready_to_push else "",
            "public_posting_preview_command": PUBLIC_POSTING_PREVIEW,
            "public_posting_apply_command": PUBLIC_POSTING_APPLY if local_public_approval else "",
            "public_posting_deploy_command": PUBLIC_POSTING_DEPLOY if local_public_approval else "",
            "refresh_command": refresh_command,
            "oauth_preview_command": oauth_preview,
            "oauth_authorization_url_command": oauth_url_command,
            "oauth_exchange_command": oauth_exchange_command,
            "platform_repair_rows": len(repair_rows),
        },
        "credential_handoff": credential_handoff,
        "api_strategy": strategy,
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
        f"- Posting mode: **{summary['posting_mode']}**",
        f"- API strategy confirmed: **{summary['api_strategy_confirmed']}**",
        f"- Checks: **{summary['check_count']}**",
        f"- Blocked checks: **{summary['blocked_count']}**",
        f"- Ready to push worker secrets: **{summary['ready_to_push_worker_secrets']}**",
        f"- Ready to post publicly: **{summary['ready_to_post_publicly']}**",
        f"- Local posting helper uses refresh token: **{summary['local_posting_helper_uses_refresh_token']}**",
        f"- Local post preview: `{summary['local_post_preview_command']}`",
        f"- Local draft upload preview: `{summary['local_upload_preview_command']}`",
        f"- Earliest TikTok API path: {summary['earliest_tiktok_api_path']}",
        f"- Local public posting approval confirmed: **{summary['local_public_posting_approval_confirmed']}**",
        f"- Public posting approved: **{summary['public_posting_approved']}**",
        f"- Default privacy: **{summary['default_privacy']}**",
        f"- Worker posting mode: **{summary['worker_posting_mode']}**",
        f"- Brand content disclosure: **{summary['brand_content_toggle']}**",
        f"- Brand organic disclosure: **{summary['brand_organic_toggle']}**",
        f"- AIGC label enabled: **{summary['aigc_label_enabled']}**",
        "",
        "## Credential Handoff",
        f"- Status: **{payload['credential_handoff']['status']}**",
        f"- Required names: `{', '.join(payload['credential_handoff']['required_secret_names'])}`",
        f"- Handoff template: `{payload['credential_handoff']['handoff_template_path']}`",
        f"- OAuth helper: `{payload['credential_handoff']['oauth_handoff_script']}`",
        f"- Requested OAuth scopes: `{', '.join(payload['credential_handoff']['requested_oauth_scopes'])}`",
        f"- Missing locally: `{', '.join(payload['credential_handoff']['local_missing_secrets']) or 'none'}`",
        f"- Missing for auth URL: `{', '.join(payload['credential_handoff']['oauth_authorization_url_missing']) or 'none'}`",
        f"- Missing for token exchange: `{', '.join(payload['credential_handoff']['oauth_token_exchange_missing']) or 'none'}`",
        f"- Missing in worker: `{', '.join(payload['credential_handoff']['worker_missing_secrets']) or 'none'}`",
        f"- Brand content disclosure: **{payload['credential_handoff']['brand_content_toggle']}**",
        f"- Worker posting mode: **{payload['credential_handoff']['worker_posting_mode']}**",
        f"- Brand organic disclosure: **{payload['credential_handoff']['brand_organic_toggle']}**",
        f"- AIGC label enabled: **{payload['credential_handoff']['aigc_label_enabled']}**",
        f"- OAuth preview: `{payload['credential_handoff']['oauth_preview_command']}`",
        f"- OAuth auth URL: `{payload['credential_handoff']['oauth_authorization_url_command']}`",
        f"- OAuth code exchange: `{payload['credential_handoff']['oauth_exchange_command']}`",
        f"- Dry-run first: `{payload['credential_handoff']['dry_run_first_command']}`",
        f"- Apply after review: `{payload['credential_handoff']['apply_command'] or 'not available until local secrets exist'}`",
        f"- Public posting approval preview: `{payload['credential_handoff']['public_posting_preview_command']}`",
        f"- Public posting approval apply: `{payload['credential_handoff']['public_posting_apply_command'] or 'not available until local approval is confirmed'}`",
        f"- Public posting approval deploy: `{payload['credential_handoff']['public_posting_deploy_command'] or 'not available until local approval is confirmed'}`",
        "- Post-apply verification:",
    ]
    lines.extend(f"  - `{command}`" for command in payload["credential_handoff"]["post_apply_verification_commands"])
    lines.extend([
        "- Completion evidence:",
    ])
    lines.extend(f"  - {item}" for item in payload["credential_handoff"]["completion_evidence"])
    lines.extend([
        "",
        "## Checks",
    ])
    for item in payload["checks"]:
        lines.append(f"- **{item['name']}**: `{item['status']}`")
        lines.append(f"  - {item['detail']}")
        if item.get("command"):
            lines.append(f"  - Command: `{item['command']}`")
    lines.extend([
        "",
        "## Commands",
        f"- Preview OAuth handoff: `{summary['oauth_preview_command']}`",
        f"- Generate OAuth auth URL: `{summary['oauth_authorization_url_command']}`",
        f"- Exchange OAuth code after authorization: `{summary['oauth_exchange_command']}`",
        f"- Preview local secrets: `{summary['push_preview_command']}`",
        f"- Preview inbox draft upload: `{summary['local_upload_preview_command']}`",
        f"- Push after local credentials are present: `{summary['push_apply_command'] or 'not available until local secrets exist'}`",
        f"- Preview public posting approval flag: `{summary['public_posting_preview_command']}`",
        f"- Apply public posting approval flag: `{summary['public_posting_apply_command'] or 'not available until local approval is confirmed'}`",
        f"- Deploy public posting approval flag: `{summary['public_posting_deploy_command'] or 'not available until local approval is confirmed'}`",
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
