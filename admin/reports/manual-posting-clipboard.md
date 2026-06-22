# Manual Posting Clipboard - Lily Roo

Generated: 2026-06-22T06:02:36.331191Z

## Summary
- Status: **ready_to_post**
- Posting surface: **YouTube Studio Community**
- Public Community URL: https://www.youtube.com/@lilyroo.artist/community
- Postable cards: **1**
- Waiting public URLs: **3**
- URL worksheet: `data/manual_distribution_url_template.csv`
- Batch log preview: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv`
- Batch log apply after posting: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --apply --refresh-admin`
- Partial batch apply after first URL: `python3 scripts/log_manual_distribution.py --from-csv data/manual_distribution_url_template.csv --allow-partial --apply --refresh-admin`
- Public URL reconciliation: `python3 scripts/reconcile_youtube_community_urls.py`
- Reconciliation status: **waiting_for_public_posts** (0 match(es))
- Reconciliation apply if matches exist: `not available`
- Next action: Post each card in YouTube Community, copy the real public URL, then log it.

## Cards
### 1. I Learned It All in Fifteen Seconds - YouTube Community
- ID: `FP-AUTO-261`
- Status: `ready_for_manual_post`
- Open: https://www.youtube.com/@lilyroo.artist/community
- Paste text:
```text
New transmission: I Learned It All in Fifteen Seconds is live. Remastered cover art, same suspicious amount of feeling.

Stream: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi | Apple Music: https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249 | YouTube: https://www.youtube.com/@lilyroo.artist | YouTube Music: https://music.youtube.com/watch?v=vK0mDIW65o4
```
- Asset: https://www.lilyroo.com/assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg
- Asset evidence: `local_asset_present` assets/albums/i-learned-it-all-in-fifteen-seconds/art/01-i-learned-it-all-in-fifteen-seconds.jpg
- Destination links: https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi, https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249, https://www.youtube.com/@lilyroo.artist, https://music.youtube.com/watch?v=vK0mDIW65o4
- Destination evidence:
  - `needs_manual_review` https://open.spotify.com/album/5TBsbgE68DTPlAFsPsLEhi: no local evidence
  - `needs_manual_review` https://music.apple.com/us/album/i-learned-it-all-in-fifteen-seconds-single/6768918249: no local evidence
  - `needs_manual_review` https://www.youtube.com/@lilyroo.artist: no local evidence
  - `needs_manual_review` https://music.youtube.com/watch?v=vK0mDIW65o4: no local evidence
- Public URL slot: `PUBLIC_URL`
- Log preview after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url PUBLIC_URL`
- Log apply after posting: `python3 scripts/log_manual_distribution.py --id FP-AUTO-261 --url PUBLIC_URL --apply --refresh-admin`
- Log notes: `manual_distribution_id=FP-AUTO-261; source=data/manual_distribution_packet.json`

## Operator Steps
- Open the YouTube Community surface.
- For each card, paste the text exactly as shown.
- Attach the listed asset URL or download/open the local asset path if needed.
- Publish manually in YouTube Studio Community.
- Copy the real public post URL.
- Run the preview logging command with the real URL, then run the apply command.
- Or rerun the public URL reconciliation command after posting to auto-detect confident public URLs.
- If only one public URL is ready, use the partial batch apply command so that post can start accumulating measurable evidence immediately.

## Guardrails
- This clipboard does not approve, schedule, publish, or log posts.
- Do not use PUBLIC_URL in an apply command.
- Use --allow-partial only after at least one worksheet row has a real public_url; blank rows remain waiting.
- Do not mark a row complete until a real public YouTube Community URL is logged.
