#!/usr/bin/env bash
set -euo pipefail

# Per-track artwork should match the YouTube video thumbnail.
OUTDIR="exports/shorts"
mkdir -p "$OUTDIR" ".tmp/shorts_overlays"

source .venv-shorts/bin/activate

render_one () {
  local title="$1"; local audio="$2"; local start="$3"; local dur="$4"; local caption="$5"; local art="$6"; local out="$7"; local overlay_png="$8"

  python scripts/make_text_overlay.py --title "$title" --caption "$caption" --out "$overlay_png"

  /usr/local/bin/ffmpeg -y \
    -ss "$start" -t "$dur" -i "$audio" \
    -loop 1 -t "$dur" -i "$art" \
    -loop 1 -t "$dur" -i "$overlay_png" \
    -filter_complex "\
      [1:v]scale=1080:1920:force_original_aspect_ratio=increase,\
           crop=1080:1920,\
           eq=contrast=1.05:brightness=-0.02:saturation=0.90,\
           gblur=sigma=10,\
           noise=alls=6:allf=t+u,\
           format=rgba[bg];\
      [bg][2:v]overlay=0:0:format=auto,fps=30[v]" \
    -map "[v]" -map 0:a \
    -c:v libx264 -preset ultrafast -crf 20 -pix_fmt yuv420p \
    -c:a aac -b:a 192k \
    -shortest \
    "$out"
}

# --- Track 1: I Learned it all in Fifteen Seconds
ART1="assets/yt/Hve5drBlN58-hq.jpg"
A1=$'I learned it all in fifteen seconds\nSwipe away before the pain sets in'
A2=$'I keep a charger by my bed\nLike a Bible for the walking dead'
A3=$'A world of strangers in my phone\nBut I\xE2\x80\x99ve lived a thousand lives alone'

render_one "I Learned it all in Fifteen Seconds" \
  "assets/drive/extracted/I Learned it all in Fifteen Seconds/I Learned it all in Fifteen Seconds.wav" \
  "00:00:22" "00:00:22" "$A1" "$ART1" "$OUTDIR/fifteen-seconds_01.mp4" ".tmp/shorts_overlays/fifteen-seconds_01.png"

render_one "I Learned it all in Fifteen Seconds" \
  "assets/drive/extracted/I Learned it all in Fifteen Seconds/I Learned it all in Fifteen Seconds.wav" \
  "00:00:58" "00:00:22" "$A2" "$ART1" "$OUTDIR/fifteen-seconds_02.mp4" ".tmp/shorts_overlays/fifteen-seconds_02.png"

render_one "I Learned it all in Fifteen Seconds" \
  "assets/drive/extracted/I Learned it all in Fifteen Seconds/I Learned it all in Fifteen Seconds.wav" \
  "00:01:20" "00:00:22" "$A3" "$ART1" "$OUTDIR/fifteen-seconds_03.mp4" ".tmp/shorts_overlays/fifteen-seconds_03.png"

# --- Track 2: Second Serve
ART2="assets/yt/_nxa0D-gqns-hq.jpg"
B1=$'Underhand serve, yeah that\xE2\x80\x99s my call\nNot fast, not tricky \xE2\x80\x94 but it beats them all'
B2=$'Crocs squeak loud in the quiet of it all\nJust one more serve, Crocs and all'
B3=$'I\xE2\x80\x99m not great \xE2\x80\x94 but I don\xE2\x80\x99t stall\nSecond serve, Crocs and all'

render_one "Second Serve" \
  "assets/drive/extracted/I Learned it all in Fifteen Seconds/Second Serve.wav" \
  "00:00:28" "00:00:20" "$B1" "$ART2" "$OUTDIR/second-serve_01.mp4" ".tmp/shorts_overlays/second-serve_01.png"

render_one "Second Serve" \
  "assets/drive/extracted/I Learned it all in Fifteen Seconds/Second Serve.wav" \
  "00:01:00" "00:00:20" "$B2" "$ART2" "$OUTDIR/second-serve_02.mp4" ".tmp/shorts_overlays/second-serve_02.png"

render_one "Second Serve" \
  "assets/drive/extracted/I Learned it all in Fifteen Seconds/Second Serve.wav" \
  "00:01:28" "00:00:20" "$B3" "$ART2" "$OUTDIR/second-serve_03.mp4" ".tmp/shorts_overlays/second-serve_03.png"

# --- Track 3: The Importance of Bearing Witness
ART3="assets/yt/cVuK20aaJb8-hq.jpg"
C1=$'The importance of bearing witness\xE2\x80\x94\nTo show you saw, to say you knew'
C2=$'To echo cries that fade too fast\nTo be the mirror, not the mask'
C3=$'Bearing witness, it\xE2\x80\x99s a vow\xE2\x80\x94\nTo mark the then, to name the now'

render_one "The Importance of Bearing Witness" \
  "assets/drive/extracted/I Learned it all in Fifteen Seconds/The Importance of Bearing Witness.wav" \
  "00:00:26" "00:00:24" "$C1" "$ART3" "$OUTDIR/bearing-witness_01.mp4" ".tmp/shorts_overlays/bearing-witness_01.png"

render_one "The Importance of Bearing Witness" \
  "assets/drive/extracted/I Learned it all in Fifteen Seconds/The Importance of Bearing Witness.wav" \
  "00:01:18" "00:00:24" "$C2" "$ART3" "$OUTDIR/bearing-witness_02.mp4" ".tmp/shorts_overlays/bearing-witness_02.png"

render_one "The Importance of Bearing Witness" \
  "assets/drive/extracted/I Learned it all in Fifteen Seconds/The Importance of Bearing Witness.wav" \
  "00:02:08" "00:00:24" "$C3" "$ART3" "$OUTDIR/bearing-witness_03.mp4" ".tmp/shorts_overlays/bearing-witness_03.png"

echo "Rendered shorts to $OUTDIR"
