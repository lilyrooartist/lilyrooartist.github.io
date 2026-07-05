# Posting Automation Status - Lily Roo

Generated: 2026-07-05T21:34:00.139547Z

## Summary
- Status: **blocked**
- Active campaign ready: **False**
- Lanes ready: **5 / 9**
- Blocked lanes: **2**
- Deferred optional lanes: **1**
- Needs attention: **1**
- Story posts tracked: **6**
- Help-needed items: **0**
- Next action: Direct TikTok public posting is not in the active plan until platform approval is explicit; upload-draft/manual-finish posting is excluded.

## Automation Lanes
- **Active Analog Myth brand campaign** - `needs_attention`
  - Detail: 64 approved auto posts; next=FP-BRAND-AM-03-ANALOG-MYTH-X at 2026-07-06T10:15:00-04:00; preflight=ready
  - Evidence: data/brand_growth_preflight.json
  - Next: Refresh brand growth readout and preflight.
- **Scheduled refresh workflow** - `ready`
  - Detail: 17 */6 * * *, 05 16 * * *; latest run completed / success
  - Evidence: https://github.com/lilyrooartist/lilyrooartist.github.io/actions/runs/28752623545
- **Safe admin refresh** - `ready`
  - Detail: 17 refresh commands captured at 2026-07-05T21:33:58.450383Z
  - Evidence: data/promo_admin_refresh_run.json
- **Scheduler dry-run authentication** - `ready`
  - Detail: HTTP 200 using bearer auth; due=0 would_post=0
  - Evidence: data/social_scheduler_dry_run.json
- **Execution capture** - `ready`
  - Detail: posted=34 attention=0 platform_fix_needed=0
  - Evidence: data/social_execution_snapshot.json
- **Platform readiness** - `deferred`
  - Detail: ready=X, Facebook, YouTube; blocked=Instagram, TikTok
  - Evidence: data/executor_readiness_snapshot.json
  - Next: Optional expansion only; the active Analog Myth campaign uses ready X/Facebook lanes.
- **TikTok API lane** - `blocked`
  - Detail: blocked; upload_ready=False; public_ready=False
  - Evidence: data/tiktok_setup_preflight.json
  - Next: Direct TikTok public posting is not in the active plan until platform approval is explicit; upload-draft/manual-finish posting is excluded.
- **Blocker input readiness** - `blocked`
  - Detail: 3 ready; 3 missing local input; 1 external action needed
  - Evidence: data/social_blocker_input_status.json
  - Next: Add X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET to /Users/tod.famous/Documents/New project/secrets/social_api.env.
- **Story throughput** - `ready`
  - Detail: 6 tracked; 0 queued; 0 past due without URL
  - Evidence: data/story_throughput_tracking.json
  - Next: Export social executions after scheduled post times, then log public URLs and results.

## Help Needed
- No active campaign help needed.

## Optional Expansion Inputs
- **Instagram business account ID**
  - Need: Provide Meta Page credentials so the resolver can write IG_BUSINESS_ACCOUNT_ID for the Instagram account connected to the Lily Roo Facebook Page.
  - Unblocks: Optional automated Instagram expansion after the secret is pushed and readiness is recaptured.
  - Verify: `python3 scripts/check_social_executor_dry_run.py --post-id FP-PLAN-TWELVE-DOLLARS-INSTAGRAM`
- **TikTok public-posting approval**
  - Need: Confirm whether TikTok has approved direct public posting for Lily Roo.
  - Unblocks: Optional direct public TikTok posting; inbox-draft upload is not part of the active no-manual-posting plan.
  - Verify: `python3 scripts/set_tiktok_public_posting_approval.py --approved`

## Guardrails
- This packet is read-only; it does not publish posts, approve posts, or push secrets.
- A scheduled workflow is not full automation unless scheduler auth, execution capture, platform readiness, and URL/result logging are also healthy.
- TikTok direct public posting remains blocked until credentials and public-posting approval are explicit.
