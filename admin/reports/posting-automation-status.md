# Posting Automation Status - Lily Roo

Generated: 2026-07-01T21:59:15.000498Z

## Summary
- Status: **blocked**
- Lanes ready: **5 / 8**
- Blocked lanes: **3**
- Needs attention: **0**
- Story posts tracked: **6**
- Help-needed items: **5**
- Next action: Resolve the platform repair checklist before expecting full auto-post coverage.

## Automation Lanes
- **Scheduled refresh workflow** - `ready`
  - Detail: 17 */6 * * *; latest run completed / success
  - Evidence: https://github.com/lilyrooartist/lilyrooartist.github.io/actions/runs/28550104089
- **Safe admin refresh** - `ready`
  - Detail: 11 refresh commands captured at 2026-07-01T21:59:12.673154Z
  - Evidence: data/promo_admin_refresh_run.json
- **Scheduler dry-run authentication** - `ready`
  - Detail: HTTP 200 using bearer auth; due=31 would_post=0
  - Evidence: data/social_scheduler_dry_run.json
- **Execution capture** - `ready`
  - Detail: posted=5 attention=6 platform_fix_needed=5
  - Evidence: data/social_execution_snapshot.json
- **Platform readiness** - `blocked`
  - Detail: ready=X, Facebook, YouTube; blocked=Instagram, TikTok
  - Evidence: data/executor_readiness_snapshot.json
  - Next: Resolve the platform repair checklist before expecting full auto-post coverage.
- **TikTok API lane** - `blocked`
  - Detail: blocked; upload_ready=False; public_ready=False
  - Evidence: data/tiktok_setup_preflight.json
  - Next: Add TikTok OAuth credentials and rerun the upload-mode dry run.
- **Blocker input readiness** - `blocked`
  - Detail: 3 ready; 1 missing local input; 1 external action needed
  - Evidence: data/social_blocker_input_status.json
  - Next: Add META_LONG_LIVED_TOKEN, FB_PAGE_ID to /private/tmp/secrets/social_api.env, then run python3 scripts/resolve_instagram_business_account.py.
- **Story throughput** - `ready`
  - Detail: 6 tracked; 0 queued; 0 past due without URL
  - Evidence: data/story_throughput_tracking.json
  - Next: Export social executions after scheduled post times, then log public URLs and results.

## Help Needed
- **Scheduler and executor auth**
  - Need: Confirm LILYROO_EXECUTOR_BEARER_TOKEN or LILYROO_ADMIN_PASSWORD is available locally and as a GitHub Actions secret.
  - Unblocks: Scheduler dry-run, executor readiness capture, and execution history capture.
  - Verify: `python3 scripts/capture_scheduler_dry_run.py && python3 scripts/capture_social_executions.py`
- **Instagram business account ID**
  - Need: Provide IG_BUSINESS_ACCOUNT_ID for the Instagram account connected to the Lily Roo Facebook Page.
  - Unblocks: Instagram executor rows after the secret is pushed and readiness is recaptured.
  - Verify: `python3 scripts/check_social_executor_dry_run.py --post-id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`
- **TikTok OAuth app values**
  - Need: Provide TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, and TIKTOK_REDIRECT_URI, then authorize the generated TikTok OAuth URL so TIKTOK_REFRESH_TOKEN can be created.
  - Unblocks: TikTok upload-draft automation for the first ready TikTok asset.
  - Verify: `python3 scripts/tiktok_oauth_handoff.py --print-auth-url --posting-mode upload`
- **TikTok public-posting approval**
  - Need: Confirm whether TikTok has approved direct public posting for Lily Roo.
  - Unblocks: Direct public TikTok posting; without approval, upload-draft mode remains the safest automated path.
  - Verify: `python3 scripts/set_tiktok_public_posting_approval.py --approved`
- **Facebook identity confirmation**
  - Need: Confirm identity in Facebook/Meta for Page publishing if Meta still shows the Page publishing checkpoint.
  - Unblocks: The blocked Facebook executor row that hit the identity confirmation checkpoint.
  - Verify: `python3 scripts/check_facebook_publishing.py --post-id 'FP-AUTO-265' --check-worker-dry-run`

## Guardrails
- This packet is read-only; it does not publish posts, approve posts, or push secrets.
- A scheduled workflow is not full automation unless scheduler auth, execution capture, platform readiness, and URL/result logging are also healthy.
- TikTok direct public posting remains blocked until credentials and public-posting approval are explicit.
