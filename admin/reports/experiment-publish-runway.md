# Experiment Publish Runway - Lily Roo

Generated: 2026-06-22T06:02:36.977989Z

## Summary
- Manual rows ready for review: **2**
- Postable now: **1**
- Public URLs needed: **3**
- Pending result fields: **18**
- Winner-ready formats: **0 / 3**
- Blocked platform rows: **4**

## Next Publish Action
- Review and approve manual YouTube Community experiment rows.

## Manual Review Rows
- `FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY` Twelve Dollars on YouTube Community
  - Preview: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --dry-run`
  - Apply after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --refresh-admin`
- `FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY` Analog Myth on YouTube Community
  - Preview: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --dry-run`
  - Apply after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --refresh-admin`

## Runway Steps
- **review_manual_youtube_community** - `ready_for_review`
  - Preview: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --dry-run`
  - Apply after review: `python3 scripts/approve_promo_queue_plan.py --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --refresh-admin`
  - Guardrail: Manual-only approvals do not auto-post; posting and public URL logging remain separate.
- **queue_approved_manual_rows** - `ready_after_approval`
  - Preview: `python3 scripts/apply_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY `
  - Apply after review: `python3 scripts/apply_promo_queue_plan.py --id FP-PLAN-TWELVE-DOLLARS-YOUTUBE-COMMUNITY --id FP-PLAN-ANALOG-MYTH-YOUTUBE-COMMUNITY --apply --refresh-admin`
  - Guardrail: Apply only after the matching promo plan rows have approved=yes.
- **post_manual_youtube_community** - `postable_now`
  - Guardrail: Post manually using the reviewed copy and local asset evidence; do not log placeholder URLs.
- **log_public_urls** - `ready_after_manual_post`
  - Preview: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv`
  - Apply after review: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --apply --refresh-admin`
  - Guardrail: Every CSV row must contain a real public_url before apply.
- **collect_results** - `waiting_for_measurement_window`
  - Preview: `python3 scripts/update_experiment_results.py --from-csv data/experiment_result_entry_template.csv --dry-run`
  - Guardrail: Fill only visible platform analytics values with evidence notes.

## Blocked Platform Rows
- `FP-AUTO-263` Instagram - max_attempts_exceeded
- `FP-PLAN-TWELVE-DOLLARS-INSTAGRAM` Instagram - max_attempts_exceeded
- `FP-AUTO-265` Facebook - failed
- `FP-AUTO-264` TikTok - tiktok_credentials_missing
