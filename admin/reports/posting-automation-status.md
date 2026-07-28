# Posting Automation Status - Lily Roo

Generated: 2026-07-28T17:36:11.329882Z

## Summary
- Status: **blocked**
- Active campaign ready: **False**
- Lanes ready: **5 / 10**
- Blocked lanes: **3**
- Deferred optional lanes: **0**
- Needs attention: **2**
- Story posts tracked: **6**
- Help-needed items: **0**
- Proof refresh: **ready** at `2026-07-29T15:25:00Z` (4 min)
- Proof export: **needs_attention** via `python3 scripts/export_social_executions.py`
- Next action: Repair the active campaign platform before the next scheduled slot.

## Automation Lanes
- **Active Analog Myth brand campaign** - `needs_attention`
  - Detail: 48 approved auto posts; next=FP-GROWTH-RESET-09-NO-MORTGAGE-LYRIC-PUNCH-LINE-YOUTUBE at 2026-07-29T10:15:00-04:00; preflight=needs_attention
  - Evidence: data/brand_growth_preflight.json
  - Next: Refresh brand growth readout and preflight.
- **Scheduled refresh workflow** - `ready`
  - Detail: 17 */6 * * *, 25 15 * * *, 05 16 * * *, 20 18 * * *; latest run in_progress / pending; proof refresh next fixed refresh 4 minute(s) after proof due
  - Evidence: https://github.com/lilyrooartist/lilyrooartist.github.io/actions/runs/30383569653
- **Published URL export** - `needs_attention`
  - Detail: safe refresh runs python3 scripts/export_social_executions.py; latest export added=0 dry_run=False; next proof refresh=2026-07-29T15:25:00Z
  - Evidence: data/promo_admin_refresh_run.json
  - Next: Ensure refresh_promo_admin.py runs export_social_executions.py without --dry-run during the scheduled proof refresh.
- **Safe admin refresh** - `ready`
  - Detail: 19 refresh commands captured at 2026-07-28T17:36:09.176629Z
  - Evidence: data/promo_admin_refresh_run.json
- **Scheduler dry-run authentication** - `ready`
  - Detail: HTTP 200 using bearer auth; due=12 would_post=0
  - Evidence: data/social_scheduler_dry_run.json
- **Execution capture** - `ready`
  - Detail: posted=55 attention=12 platform_fix_needed=12
  - Evidence: data/social_execution_snapshot.json
- **Platform readiness** - `blocked`
  - Detail: ready=X, Facebook; blocked=Instagram, TikTok, YouTube
  - Evidence: data/executor_readiness_snapshot.json
  - Next: Repair the active campaign platform before the next scheduled slot.
- **TikTok API lane** - `blocked`
  - Detail: blocked; upload_ready=False; public_ready=False
  - Evidence: data/tiktok_setup_preflight.json
  - Next: Direct TikTok public posting is not in the active plan until platform approval is explicit; upload-draft/manual-finish posting is excluded.
- **Blocker input readiness** - `blocked`
  - Detail: 1 ready; 5 missing local input; 1 external action needed
  - Evidence: data/social_blocker_input_status.json
  - Next: Add X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET to secrets/social_api.env.
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
