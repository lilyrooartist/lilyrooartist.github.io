# Human Handoff Resolution Preview - Lily Roo

Generated: 2026-07-07T01:30:06.577795Z

## Summary
- Worksheet rows: **3**
- Executed previews: **3**
- Skipped previews: **0**
- Status counts: `{"input_missing": 2, "preview_ok": 1}`
- Policy: Only python3 scripts/* commands with --dry-run, or reschedule previews without --apply, are executed.
- Guardrail: This preview runner never executes apply, refresh-admin, PUBLIC_URL placeholder, non-python, or unsupported commands.

## Previews
- **platform-setup-tiktok-preflight** (`preview_ok`)
  - Phase: `Platform setup`; input needed: `local_secret_presence_and_public_posting_approval`
  - Safety: `safe_preview` (dry_run_command)
  - Command: `python3 scripts/post_tiktok_from_queue.py --post-id FP-AUTO-264 --mode direct --dry-run`
  - Output: {"ok": true, "platform": "TikTok", "dry_run": true, "mode": "direct", "endpoint": "https://open.tiktokapis.com/v2/post/publish/video/init/", "required_scope": "video.publish", "media_key": "i-learned-60s", "media_ready": true, "public_video_url": "https://www.lilyroo.com/assets/media/01_i_learned_it_all_60s_tiktok.mp4?fresh=6cb3941d2", "media_path": "", "token_path_ready": false, "token_source": "", "missing_refresh_credentials": ["TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REFRESH_TOKEN"], "public_posting_approved": false, "default_privacy": "PUBLIC_TO_EVERYONE", "brand_content_toggle": false, "brand_organic_toggle": true, "aigc_label_enabled": true, "title": "Swipe away before the pain sets in. Cute system we built. Streaming now."}
  - Guardrail: Keep TikTok upload-draft/manual-finish posting out of the active plan; only direct public API publishing can become an automated TikTok lane.
- **manual-metrics-priority-2** (`input_missing`)
  - Phase: `Manual metrics`; input needed: `private_metric_values`
  - Safety: `safe_preview` (dry_run_command)
  - Command: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Output: No metric assignments supplied. Add platform.metric=value args or fill new_value cells and use --from-csv.
  - Guardrail: Only import nonnegative numeric values copied from the named source; leave unknown values blank instead of guessing.
- **manual-metrics-priority-3** (`input_missing`)
  - Phase: `Manual metrics`; input needed: `private_metric_values`
  - Safety: `safe_preview` (dry_run_command)
  - Command: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Output: No metric assignments supplied. Add platform.metric=value args or fill new_value cells and use --from-csv.
  - Guardrail: Only import nonnegative numeric values copied from the named source; leave unknown values blank instead of guessing.

## Guardrails
- This preview does not approve, post, publish, push secrets, log URLs, import metrics, or refresh admin state.
- Missing values and blocked platform setup are reported as input_missing, not repaired automatically.
