# Human Handoff Packet - Lily Roo

Generated: 2026-06-20T03:17:17.338005Z

## Summary
- Open handoff tasks: **10**
- Tod-owned tasks: **9**
- External/platform-gated tasks: **1**
- High urgency tasks: **3**
- Low urgency tasks: **5**

## Tasks
- **Review and approve checked scheduled batch** (`approve-checked-scheduled-batch`)
  - Phase: `Approval`; owner: `tod`; status: `waiting_for_review`; urgency: `high`
  - Detail: Review the checked rows, then apply the guarded batch command. Failed review rows stay excluded.
  - Preview/check: `python3 scripts/update_scheduled_post_approval.py --checked-batch --dry-run`
  - Apply after review: `python3 scripts/update_scheduled_post_approval.py --checked-batch --refresh-admin`
  - Guardrail: Use --checked-batch so only rows that passed review checks are approved.
- **Repair TikTok executor** (`platform-setup-FP-AUTO-264`)
  - Phase: `Platform setup`; owner: `tod`; status: `blocked`; urgency: `high`
  - Detail: Missing worker secrets: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. TikTok public posting approval is false. Local secret source is also missing: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN. Complete TikTok OAuth/public posting setup locally, then push secrets and refresh Admin.
  - Preview/check: `python3 scripts/push_social_worker_secrets.py --dry-run TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN`
  - Apply after review: `python3 scripts/push_social_worker_secrets.py TIKTOK_CLIENT_KEY TIKTOK_CLIENT_SECRET TIKTOK_REFRESH_TOKEN && python3 scripts/refresh_promo_admin.py`
  - Guardrail: Run the TikTok preflight before pushing secrets; push worker secrets only after local OAuth/public posting setup is complete.
- **Preview approved backlog reschedule** (`backlog-reschedule`)
  - Phase: `Backlog recovery`; owner: `external_platform`; status: `blocked`; urgency: `high`
  - Detail: Known executor/platform blockers must clear before normal apply.
  - Preview/check: `python3 scripts/reschedule_scheduled_posts.py --approved-backlog --start-at '2026-06-21T10:00:00+09:00' --spacing-hours 24`
  - Guardrail: Normal apply stays hidden until known executor/platform blockers clear.
- **Post Analog Myth to YouTube Community** (`manual-distribution-FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY`)
  - Phase: `Manual distribution`; owner: `tod`; status: `waiting_for_review`; urgency: `medium`
  - Detail: Review the packaged copy, approve if appropriate, post manually, then log the public URL.
  - Preview/check: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --dry-run`
  - Apply after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --refresh-admin`
  - asset: https://www.lilyroo.com/assets/albums/analog-myth/art/03-analog-myth.jpg
  - Guardrail: Do not log a manual post until a real public URL exists.
- **Post Twelve Dollars to YouTube Community** (`manual-distribution-FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY`)
  - Phase: `Manual distribution`; owner: `tod`; status: `waiting_for_review`; urgency: `medium`
  - Detail: Review the packaged copy, approve if appropriate, post manually, then log the public URL.
  - Preview/check: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --dry-run`
  - Apply after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --refresh-admin`
  - asset: https://www.lilyroo.com/assets/albums/twelve-dollars/art/04-twelve-dollars.jpg
  - Guardrail: Do not log a manual post until a real public URL exists.
- **Fill facebook manual metrics** (`manual-metrics-facebook`)
  - Phase: `Manual metrics`; owner: `tod`; status: `waiting_for_manual_values`; urgency: `low`
  - Detail: Collect 1 field(s), fill the worksheet, preview import, then refresh Admin.
  - Preview/check: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Apply after review: `python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`
  - metric source: https://www.facebook.com/903693509504290
  - Guardrail: Only import nonnegative numeric values; leave unknown values blank instead of guessing.
- **Fill instagram manual metrics** (`manual-metrics-instagram`)
  - Phase: `Manual metrics`; owner: `tod`; status: `waiting_for_manual_values`; urgency: `low`
  - Detail: Collect 2 field(s), fill the worksheet, preview import, then refresh Admin.
  - Preview/check: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Apply after review: `python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`
  - metric source: https://www.instagram.com/professional_dashboard/
  - Guardrail: Only import nonnegative numeric values; leave unknown values blank instead of guessing.
- **Fill spotify manual metrics** (`manual-metrics-spotify`)
  - Phase: `Manual metrics`; owner: `tod`; status: `waiting_for_manual_values`; urgency: `low`
  - Detail: Collect 4 field(s), fill the worksheet, preview import, then refresh Admin.
  - Preview/check: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Apply after review: `python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`
  - metric source: https://open.spotify.com/artist/4yzWmf64UKLwbAVwnDi49a
  - Guardrail: Only import nonnegative numeric values; leave unknown values blank instead of guessing.
- **Fill tiktok manual metrics** (`manual-metrics-tiktok`)
  - Phase: `Manual metrics`; owner: `tod`; status: `waiting_for_manual_values`; urgency: `low`
  - Detail: Collect 2 field(s), fill the worksheet, preview import, then refresh Admin.
  - Preview/check: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Apply after review: `python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`
  - metric source: https://www.tiktok.com/creator-center/analytics
  - Guardrail: Only import nonnegative numeric values; leave unknown values blank instead of guessing.
- **Fill x manual metrics** (`manual-metrics-x`)
  - Phase: `Manual metrics`; owner: `tod`; status: `waiting_for_manual_values`; urgency: `low`
  - Detail: Collect 2 field(s), fill the worksheet, preview import, then refresh Admin.
  - Preview/check: `python3 scripts/update_manual_social_stats.py --from-csv --dry-run`
  - Apply after review: `python3 scripts/update_manual_social_stats.py --from-csv --refresh-admin`
  - metric source: https://analytics.x.com/
  - Guardrail: Only import nonnegative numeric values; leave unknown values blank instead of guessing.

## Guardrails
- This packet is review-only and does not approve, post, publish, push secrets, or import metrics.
- Preview commands should run before any apply command.
- Manual metrics and public post URLs should come from real platform surfaces, not estimates.
