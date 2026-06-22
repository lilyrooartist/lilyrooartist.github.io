#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from social_exec_common import REPO_ROOT, SOCIAL_ENV, get_row, load_env


ROOT = REPO_ROOT
READINESS = ROOT / "data" / "executor_readiness_snapshot.json"
PLATFORM_REPAIR = ROOT / "data" / "platform_repair_status.json"
API_STRATEGY = ROOT / "data" / "tiktok_api_strategy.json"
HANDOFF_STATUS = ROOT / "data" / "tiktok_local_handoff_status.json"
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
FIRST_TIKTOK_POST_ID = "FP-AUTO-264"
PUBLIC_POSTING_PREVIEW = "python3 scripts/set_tiktok_public_posting_approval.py --approved"
PUBLIC_POSTING_APPLY = "python3 scripts/set_tiktok_public_posting_approval.py --approved --apply"
PUBLIC_POSTING_DEPLOY = "python3 scripts/set_tiktok_public_posting_approval.py --approved --apply --deploy"
INIT_LOCAL_SECRET_ENV = (
    "mkdir -p ../secrets && "
    "test -f ../secrets/social_api.env || "
    "cp data/tiktok_secret_handoff_template.env ../secrets/social_api.env"
)


def write_handoff_template() -> None:
    lines = [
        "# Lily Roo TikTok secret handoff template",
        "# Posting mode selected: API integration.",
        "# OAuth scopes for the first connector pass should include user.info.basic and video.upload.",
        "# Add video.publish only after direct public posting approval is confirmed.",
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


def is_http_url(value: str) -> bool:
    return value.startswith("https://") or value.startswith("http://")


def is_video_url(value: str) -> bool:
    return bool(re.search(r"\.(mp4|mov|m4v|webm)(\?|$)", value, re.IGNORECASE))


def first_tiktok_asset_readiness() -> dict:
    try:
        row = get_row(FIRST_TIKTOK_POST_ID)
    except Exception as exc:
        return {
            "post_id": FIRST_TIKTOK_POST_ID,
            "status": "missing_queue_row",
            "ready_for_upload_mode": False,
            "reason": str(exc),
        }
    clip_url = (row.get("clip_url") or "").strip()
    text = (row.get("text") or "").strip()
    platform = (row.get("platform") or "").strip()
    post_type = (row.get("post_type") or "").strip()
    approved = (row.get("approved") or "").strip().lower() == "yes"
    media_ready = is_http_url(clip_url) and is_video_url(clip_url)
    text_ready = bool(text)
    ready = bool(platform.lower() == "tiktok" and post_type == "video" and approved and media_ready and text_ready)
    blockers = []
    if platform.lower() != "tiktok":
        blockers.append("platform_not_tiktok")
    if post_type != "video":
        blockers.append("post_type_not_video")
    if not approved:
        blockers.append("row_not_approved")
    if not media_ready:
        blockers.append("public_video_url_missing_or_unsupported")
    if not text_ready:
        blockers.append("text_missing")
    return {
        "post_id": FIRST_TIKTOK_POST_ID,
        "status": "ready_for_upload_mode" if ready else "blocked",
        "ready_for_upload_mode": ready,
        "platform": platform,
        "song": row.get("song") or "",
        "post_type": post_type,
        "approved": approved,
        "clip_url": clip_url,
        "media_ready": media_ready,
        "text_ready": text_ready,
        "media_key": row.get("media_key") or "",
        "dry_run_command": f"python3 scripts/post_tiktok_from_queue.py --post-id {FIRST_TIKTOK_POST_ID} --mode upload --dry-run",
        "blockers": blockers,
        "credential_blockers": REQUIRED_REFRESH_SECRETS,
        "next_after_credentials": f"python3 scripts/post_tiktok_from_queue.py --post-id {FIRST_TIKTOK_POST_ID} --mode upload --dry-run",
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


def owner_handoff(summary: dict, credential_handoff: dict) -> dict:
    needed_inputs = []
    local_missing = credential_handoff.get("local_missing_secrets") or []
    auth_url_missing = credential_handoff.get("oauth_authorization_url_missing") or []
    token_exchange_missing = credential_handoff.get("oauth_token_exchange_missing") or []
    public_posting_approved = summary.get("public_posting_approved") is True
    local_public_approval = summary.get("local_public_posting_approval_confirmed") is True

    if local_missing or auth_url_missing or token_exchange_missing:
        needed_inputs.append({
            "id": "tiktok_developer_app_credentials",
            "owner": "tod",
            "status": "needed",
            "request": "Add Lily Roo TikTok developer app values locally.",
            "values_needed": sorted(set(local_missing + auth_url_missing + token_exchange_missing + ["TIKTOK_REDIRECT_URI"])),
            "safe_storage": credential_handoff.get("local_secret_source") or "secrets/social_api.env",
            "why": "The connector cannot generate an OAuth URL, exchange a code, or refresh TikTok access without these app values.",
            "next_command_after_input": credential_handoff.get("oauth_authorization_url_command") or "python3 scripts/tiktok_oauth_handoff.py --print-auth-url",
        })

    if "TIKTOK_REFRESH_TOKEN" in local_missing:
        needed_inputs.append({
            "id": "authorize_lily_roo_tiktok_account",
            "owner": "tod",
            "status": "needed",
            "request": "Authorize the Lily Roo TikTok account after the OAuth URL is generated.",
            "values_needed": ["short-lived TikTok authorization code"],
            "safe_storage": credential_handoff.get("local_secret_source") or "secrets/social_api.env",
            "why": "The refresh token is created only after the Lily Roo account authorizes the app with the requested scopes.",
            "next_command_after_input": credential_handoff.get("oauth_exchange_command") or "python3 scripts/tiktok_oauth_handoff.py --exchange-code CODE --apply",
        })

    if not public_posting_approved:
        needed_inputs.append({
            "id": "public_posting_approval",
            "owner": "tod",
            "status": "needed" if not local_public_approval else "ready_to_deploy",
            "request": "Confirm whether Lily Roo TikTok has public Content Posting API approval and PUBLIC_TO_EVERYONE posting is allowed.",
            "values_needed": ["TIKTOK_PUBLIC_POSTING_APPROVED=true confirmation"],
            "safe_storage": "Worker variable via guarded approval helper",
            "why": "Direct public TikTok publishing must stay blocked until this approval is explicit.",
            "next_command_after_input": credential_handoff.get("public_posting_deploy_command") or credential_handoff.get("public_posting_preview_command") or "python3 scripts/set_tiktok_public_posting_approval.py --approved",
        })

    if local_missing:
        next_safe_action = summary.get("oauth_preview_command") or "python3 scripts/tiktok_oauth_handoff.py"
    elif credential_handoff.get("worker_missing_secrets"):
        next_safe_action = credential_handoff.get("dry_run_first_command") or summary.get("push_preview_command") or "python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN"
    elif summary.get("ready_to_upload_drafts"):
        next_safe_action = summary.get("local_upload_preview_command") or "python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --mode upload --dry-run"
    elif not public_posting_approved:
        next_safe_action = summary.get("public_posting_preview_command") or "python3 scripts/set_tiktok_public_posting_approval.py --approved"
    else:
        next_safe_action = summary.get("push_preview_command") or "python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN"

    upload_lane = credential_handoff.get("upload_mode_lane") or {}
    direct_lane = credential_handoff.get("direct_public_lane") or {}
    after_input_sequence = credential_handoff.get("after_input_command_sequence") or []
    return {
        "status": "blocked_until_user_input" if needed_inputs else "ready_for_secret_push_preview",
        "question_answer": "Yes, fix the TikTok connector after the current manual YouTube evidence loop; it unlocks the short-video growth format.",
        "next_safe_action": next_safe_action,
        "needed_input_count": len(needed_inputs),
        "needed_inputs": needed_inputs,
        "immediate_upload_path": upload_lane,
        "deferred_direct_public_path": direct_lane,
        "after_input_command_sequence": after_input_sequence,
        "codex_can_do_without_more_input": [
            "Keep TikTok blockers visible in admin/status output.",
            "Run safe preflight and dry-run helpers.",
            "Push upload-mode connector secrets after local TikTok values exist and the dry-run is reviewed.",
            "Refresh admin and validation after the connector state changes.",
        ],
        "unlock_sequence": [
            "Add TikTok app credentials and redirect URI locally.",
            "Generate the OAuth URL and authorize the Lily Roo TikTok account.",
            "Exchange the authorization code for a refresh token.",
            "Dry-run the Worker secret push.",
            "Push Worker secrets for upload-draft mode after review.",
            "Refresh Admin, then retry or reschedule the TikTok row as an inbox draft upload.",
            "Confirm and deploy public-posting approval only after direct public posting is actually approved.",
        ],
        "first_growth_row_unblocked": "FP-AUTO-264",
        "format_unblocked": "Short video clip + platform-native CTA",
        "guardrail": "This handoff never includes secret values and does not approve or publish TikTok posts.",
    }


def build_payload() -> dict:
    write_handoff_template()
    readiness = read_json(READINESS, {})
    platform_repair = read_json(PLATFORM_REPAIR, {})
    strategy = read_json(API_STRATEGY, {})
    handoff_status = read_json(HANDOFF_STATUS, {})
    tiktok_readiness = (((readiness.get("payload") or {}).get("platforms") or {}).get("tiktok") or {})
    posting_mode = strategy.get("posting_mode") or "api"
    presence = local_secret_presence()
    local_secret_dir_exists = SOCIAL_ENV.parent.exists()
    runtime_local_secret_env_exists = SOCIAL_ENV.exists()
    local_secret_handoff_prepared = bool(
        runtime_local_secret_env_exists
        or (
            handoff_status.get("safe_mode") is True
            and handoff_status.get("local_secret_env_initialized") is True
            and handoff_status.get("local_secret_source") == str(SOCIAL_ENV.relative_to(ROOT.parent))
        )
    )
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
    worker_posting_mode = tiktok_readiness.get("posting_mode") or wrangler_var(POSTING_MODE) or "upload"
    refresh_config_present = bool(tiktok_readiness.get("refresh_config_present"))
    access_token_present = bool(tiktok_readiness.get("access_token_present"))
    local_access_token_present = bool(presence.get(OPTIONAL_ACCESS_TOKEN))
    local_refresh_config_present = not local_missing
    oauth_url_missing = [name for name in ["TIKTOK_CLIENT_KEY", "TIKTOK_REDIRECT_URI"] if not presence.get(name)]
    oauth_exchange_missing = [name for name in ["TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REDIRECT_URI"] if not presence.get(name)]
    preflight_checks = [
        check(
            "local_secret_env_file",
            "pass" if local_secret_handoff_prepared else "waiting",
            f"Local secret env exists at {SOCIAL_ENV.relative_to(ROOT.parent)}."
            if runtime_local_secret_env_exists
            else f"Local secret env handoff is initialized at {SOCIAL_ENV.relative_to(ROOT.parent)}; this runtime cannot inspect the local file."
            if local_secret_handoff_prepared
            else f"Initialize {SOCIAL_ENV.relative_to(ROOT.parent)} from the blank handoff template before adding TikTok app values.",
            "" if local_secret_handoff_prepared else INIT_LOCAL_SECRET_ENV,
        ),
        check(
            "oauth_authorization_url",
            "pass" if not oauth_url_missing else "blocked",
            "TikTok OAuth authorization URL can be generated locally."
            if not oauth_url_missing
            else f"{SOCIAL_ENV.relative_to(ROOT.parent)} is missing auth URL values: {', '.join(oauth_url_missing)}.",
            "python3 scripts/tiktok_oauth_handoff.py --print-auth-url --posting-mode upload",
        ),
        check(
            "oauth_token_exchange",
            "pass" if not oauth_exchange_missing else "blocked",
            "TikTok OAuth authorization codes can be exchanged locally."
            if not oauth_exchange_missing
            else f"{SOCIAL_ENV.relative_to(ROOT.parent)} is missing token exchange values: {', '.join(oauth_exchange_missing)}.",
            "python3 scripts/tiktok_oauth_handoff.py --exchange-code CODE --apply --posting-mode upload",
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
    ready_to_upload_drafts = ready_to_push and not worker_missing and worker_posting_mode == "upload"
    ready_to_post = not blocked
    repair_rows = [
        row for row in platform_repair.get("rows") or []
        if str(row.get("platform") or "").lower() == "tiktok"
    ]
    first_tiktok_asset = first_tiktok_asset_readiness()
    push_preview = "python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN"
    push_apply = "python3 scripts/push_social_worker_secrets.py TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN && python3 scripts/refresh_promo_admin.py"
    oauth_preview = "python3 scripts/tiktok_oauth_handoff.py"
    oauth_url_command = "python3 scripts/tiktok_oauth_handoff.py --print-auth-url --posting-mode upload"
    oauth_exchange_command = "python3 scripts/tiktok_oauth_handoff.py --exchange-code CODE --apply --posting-mode upload"
    refresh_command = "python3 scripts/refresh_promo_admin.py"
    local_post_preview = "python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --dry-run"
    local_upload_preview = "python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --mode upload --dry-run"
    upload_mode_lane = {
        "status": "ready_after_credentials" if first_tiktok_asset.get("ready_for_upload_mode") else "asset_blocked",
        "posting_mode": "upload",
        "oauth_scopes": ["user.info.basic", "video.upload"],
        "first_post_id": first_tiktok_asset.get("post_id") or FIRST_TIKTOK_POST_ID,
        "first_asset_ready": bool(first_tiktok_asset.get("ready_for_upload_mode")),
        "credential_names_needed": REQUIRED_REFRESH_SECRETS,
        "public_posting_approval_required": False,
        "human_finish_required": True,
        "post_publish_handoff": "TikTok API creates an inbox draft; Lily Roo reviews/publishes in TikTok, then the public URL is logged back into the promo engine.",
        "dry_run_command": local_upload_preview,
        "completion_evidence": "data/tiktok_setup_preflight.json ready_to_upload_drafts=true and FP-AUTO-264 upload dry-run succeeds before backlog apply.",
    }
    direct_public_lane = {
        "status": "deferred_until_tiktok_approval",
        "posting_mode": "direct",
        "oauth_scopes": ["user.info.basic", "video.upload", "video.publish"],
        "public_posting_approval_required": True,
        "approval_flag": PUBLIC_POSTING_APPROVAL,
        "guardrail": "Do not treat direct public TikTok publishing as ready until TikTok approval is explicit and the guarded Worker flag is deployed.",
        "preview_command": PUBLIC_POSTING_PREVIEW,
        "apply_command": PUBLIC_POSTING_APPLY if local_public_approval else "",
        "deploy_command": PUBLIC_POSTING_DEPLOY if local_public_approval else "",
    }
    after_input_command_sequence = [
        {
            "step": "generate_oauth_url",
            "when": "after TIKTOK_CLIENT_KEY and TIKTOK_REDIRECT_URI are present locally",
            "command": oauth_url_command,
        },
        {
            "step": "exchange_authorization_code",
            "when": "immediately after Lily Roo authorizes the TikTok OAuth URL",
            "command": oauth_exchange_command,
        },
        {
            "step": "preview_worker_secret_push",
            "when": "after local refresh credentials exist",
            "command": push_preview,
        },
        {
            "step": "preview_first_upload_draft",
            "when": "after the secret push dry-run is reviewed and credentials are available to the helper",
            "command": local_upload_preview,
        },
        {
            "step": "refresh_admin_evidence",
            "when": "after credentials or Worker state changes",
            "command": refresh_command,
        },
    ]
    credential_handoff = {
        "status": "ready_to_push" if ready_to_push else "needs_local_values",
        "required_secret_names": REQUIRED_REFRESH_SECRETS,
        "optional_secret_names": [OPTIONAL_ACCESS_TOKEN],
        "local_secret_source": str(SOCIAL_ENV.relative_to(ROOT.parent)),
        "local_secret_dir_path": str(SOCIAL_ENV.parent.relative_to(ROOT.parent)),
        "local_secret_dir_exists": local_secret_dir_exists,
        "local_secret_env_exists": local_secret_handoff_prepared,
        "local_secret_env_runtime_exists": runtime_local_secret_env_exists,
        "local_secret_handoff_prepared": local_secret_handoff_prepared,
        "local_secret_handoff_status_path": str(HANDOFF_STATUS.relative_to(ROOT)),
        "local_secret_handoff_status": handoff_status,
        "initialize_local_secret_env_command": INIT_LOCAL_SECRET_ENV if not local_secret_handoff_prepared else "",
        "handoff_template_path": str(HANDOFF_TEMPLATE.relative_to(ROOT)),
        "handoff_template_required_names": REQUIRED_REFRESH_SECRETS + ["TIKTOK_REDIRECT_URI", "TIKTOK_PUBLIC_POSTING_APPROVED", "TIKTOK_DEFAULT_PRIVACY"],
        "local_missing_secrets": local_missing,
        "oauth_authorization_url_missing": oauth_url_missing,
        "oauth_token_exchange_missing": oauth_exchange_missing,
        "worker_missing_secrets": worker_missing,
        "oauth_handoff_script": str(OAUTH_HANDOFF_SCRIPT.relative_to(ROOT)),
        "requested_oauth_scopes": ["user.info.basic", "video.upload"],
        "direct_post_oauth_scopes": ["user.info.basic", "video.upload", "video.publish"],
        "scope_strategy": "Request only video.upload for the first inbox-draft connector path; add video.publish only after direct public posting approval exists.",
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
        "upload_mode_lane": upload_mode_lane,
        "direct_public_lane": direct_public_lane,
        "after_input_command_sequence": after_input_command_sequence,
        "completion_evidence": [
            "data/tiktok_setup_preflight.json reports ready_to_push_worker_secrets true.",
            "data/executor_readiness_snapshot.json reports TikTok refresh configuration present.",
            "data/tiktok_setup_preflight.json reports first_tiktok_asset.ready_for_upload_mode true.",
            "data/tiktok_setup_preflight.json reports ready_to_upload_drafts true for the upload-mode connector path.",
            "data/platform_repair_status.json no longer lists TikTok as blocked by missing credentials.",
        ],
        "redaction": "Secret values are never written here; only required names, missing names, and presence booleans are recorded.",
    }
    summary = {
        "status": "ready" if ready_to_post else "blocked",
        "posting_mode": posting_mode,
        "api_strategy_confirmed": posting_mode == "api",
        "check_count": len(preflight_checks),
        "blocked_count": len(blocked),
        "ready_to_push_worker_secrets": ready_to_push,
        "ready_to_upload_drafts": ready_to_upload_drafts,
        "ready_to_post_publicly": ready_to_post,
        "local_posting_helper_uses_refresh_token": True,
        "first_tiktok_asset": first_tiktok_asset,
        "local_post_preview_command": local_post_preview,
        "local_upload_preview_command": local_upload_preview,
        "earliest_tiktok_api_path": "video.upload inbox draft; final public URL still requires human publish and URL logging.",
        "upload_mode_lane": upload_mode_lane,
        "direct_public_lane": direct_public_lane,
        "after_input_command_sequence": after_input_command_sequence,
        "local_missing_secrets": local_missing,
        "local_secret_dir_exists": local_secret_dir_exists,
        "local_secret_env_exists": local_secret_handoff_prepared,
        "local_secret_env_runtime_exists": runtime_local_secret_env_exists,
        "local_secret_handoff_prepared": local_secret_handoff_prepared,
        "local_secret_handoff_status_path": str(HANDOFF_STATUS.relative_to(ROOT)),
        "initialize_local_secret_env_command": INIT_LOCAL_SECRET_ENV if not local_secret_handoff_prepared else "",
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
    }
    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "safe_mode": True,
        "source": {
            "local_secret_source": str(SOCIAL_ENV.relative_to(ROOT.parent)),
            "api_strategy": str(API_STRATEGY.relative_to(ROOT)),
            "local_secret_handoff_status": str(HANDOFF_STATUS.relative_to(ROOT)),
            "handoff_template": str(HANDOFF_TEMPLATE.relative_to(ROOT)),
            "oauth_handoff_script": str(OAUTH_HANDOFF_SCRIPT.relative_to(ROOT)),
            "local_posting_helper": str(LOCAL_POST_SCRIPT.relative_to(ROOT)),
            "executor_readiness": str(READINESS.relative_to(ROOT)),
            "platform_repair_status": str(PLATFORM_REPAIR.relative_to(ROOT)),
            "wrangler_config": str(WRANGLER_CONFIG.relative_to(ROOT)),
        },
        "summary": summary,
        "credential_handoff": credential_handoff,
        "owner_handoff": owner_handoff(summary, credential_handoff),
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
        f"- Ready to upload inbox drafts: **{summary['ready_to_upload_drafts']}**",
        f"- Ready to post publicly: **{summary['ready_to_post_publicly']}**",
        f"- Local posting helper uses refresh token: **{summary['local_posting_helper_uses_refresh_token']}**",
        f"- First TikTok asset ready for upload mode: **{summary['first_tiktok_asset']['ready_for_upload_mode']}** (`{summary['first_tiktok_asset']['post_id']}`)",
        f"- Local post preview: `{summary['local_post_preview_command']}`",
        f"- Local draft upload preview: `{summary['local_upload_preview_command']}`",
        f"- Earliest TikTok API path: {summary['earliest_tiktok_api_path']}",
        f"- Upload-mode lane: **{summary['upload_mode_lane']['status']}**; public approval required: **{summary['upload_mode_lane']['public_posting_approval_required']}**",
        f"- Direct public lane: **{summary['direct_public_lane']['status']}**; public approval required: **{summary['direct_public_lane']['public_posting_approval_required']}**",
        f"- Local public posting approval confirmed: **{summary['local_public_posting_approval_confirmed']}**",
        f"- Public posting approved: **{summary['public_posting_approved']}**",
        f"- Default privacy: **{summary['default_privacy']}**",
        f"- Worker posting mode: **{summary['worker_posting_mode']}**",
        f"- Brand content disclosure: **{summary['brand_content_toggle']}**",
        f"- Brand organic disclosure: **{summary['brand_organic_toggle']}**",
        f"- AIGC label enabled: **{summary['aigc_label_enabled']}**",
        "",
        "## What We Need From Tod",
        f"- Status: **{payload['owner_handoff']['status']}**",
        f"- Answer: {payload['owner_handoff']['question_answer']}",
        f"- Needed inputs: **{payload['owner_handoff']['needed_input_count']}**",
        f"- Next safe action: `{payload['owner_handoff']['next_safe_action']}`",
        f"- First growth row unblocked: `{payload['owner_handoff']['first_growth_row_unblocked']}`",
        f"- Format unblocked: {payload['owner_handoff']['format_unblocked']}",
    ]
    for item in payload["owner_handoff"]["needed_inputs"]:
        lines.append(f"- **{item['request']}** (`{item['id']}`)")
        lines.append(f"  - Values needed: `{', '.join(item['values_needed'])}`")
        lines.append(f"  - Safe storage: `{item['safe_storage']}`")
        lines.append(f"  - Why: {item['why']}")
        lines.append(f"  - Next command: `{item['next_command_after_input']}`")
    lines.extend([
        "- Codex can do now:",
    ])
    lines.extend(f"  - {item}" for item in payload["owner_handoff"]["codex_can_do_without_more_input"])
    lines.extend([
        "",
        "## Upload-Mode Repair Ladder",
        f"- Immediate lane status: **{payload['owner_handoff']['immediate_upload_path']['status']}**",
        f"- First post ID: `{payload['owner_handoff']['immediate_upload_path']['first_post_id']}`",
        f"- Scopes: `{', '.join(payload['owner_handoff']['immediate_upload_path']['oauth_scopes'])}`",
        f"- Public posting approval required now: **{payload['owner_handoff']['immediate_upload_path']['public_posting_approval_required']}**",
        f"- Human finish required: **{payload['owner_handoff']['immediate_upload_path']['human_finish_required']}**",
        f"- Handoff: {payload['owner_handoff']['immediate_upload_path']['post_publish_handoff']}",
        f"- Direct public lane: **{payload['owner_handoff']['deferred_direct_public_path']['status']}**",
        f"- Direct public guardrail: {payload['owner_handoff']['deferred_direct_public_path']['guardrail']}",
        "- After-input command sequence:",
    ])
    lines.extend(
        f"  - `{item['step']}`: {item['when']} -> `{item['command']}`"
        for item in payload["owner_handoff"]["after_input_command_sequence"]
    )
    lines.extend([
        "",
        "## Credential Handoff",
        f"- Status: **{payload['credential_handoff']['status']}**",
        f"- Required names: `{', '.join(payload['credential_handoff']['required_secret_names'])}`",
        f"- Handoff template: `{payload['credential_handoff']['handoff_template_path']}`",
        f"- OAuth helper: `{payload['credential_handoff']['oauth_handoff_script']}`",
        f"- Requested OAuth scopes: `{', '.join(payload['credential_handoff']['requested_oauth_scopes'])}`",
        f"- Direct post OAuth scopes: `{', '.join(payload['credential_handoff']['direct_post_oauth_scopes'])}`",
        f"- Scope strategy: {payload['credential_handoff']['scope_strategy']}",
        f"- Local secret env: `{payload['credential_handoff']['local_secret_source']}`",
        f"- Local secret env prepared: **{payload['credential_handoff']['local_secret_handoff_prepared']}**",
        f"- Runtime local env file exists: **{payload['credential_handoff']['local_secret_env_runtime_exists']}**",
        f"- Local handoff marker: `{payload['credential_handoff']['local_secret_handoff_status_path']}`",
        f"- Initialize local secret env: `{payload['credential_handoff']['initialize_local_secret_env_command'] or 'not needed'}`",
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
        f"- Apply upload-mode secrets after review: `{payload['credential_handoff']['apply_command'] or 'not available until local secrets exist'}`",
        f"- Public posting approval preview: `{payload['credential_handoff']['public_posting_preview_command']}`",
        f"- Public posting approval apply: `{payload['credential_handoff']['public_posting_apply_command'] or 'not available until local approval is confirmed'}`",
        f"- Public posting approval deploy: `{payload['credential_handoff']['public_posting_deploy_command'] or 'not available until local approval is confirmed'}`",
        "- Post-apply verification:",
    ])
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
        "- Public posting approval must be confirmed before direct public TikTok posting is treated as ready.",
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
