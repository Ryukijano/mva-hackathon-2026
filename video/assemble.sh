#!/usr/bin/env bash
# Stage 3: build/video.mp4 + build/vo_mix.wav -> out/track2_pitch.mp4
# (EBU R128 loudnorm, AAC 48 kHz, h264 stream copied, faststart). Never -shortest:
# the mixdown is already exactly the video length; qa.py checks both streams.
set -euo pipefail
cd "$(dirname "$0")"
FFMPEG=${FFMPEG:-/scratch/kcwp264/conda/envs/endofm-lv/bin/ffmpeg}
mkdir -p out
"$FFMPEG" -y -loglevel error -i build/video.mp4 -i build/vo_mix.wav \
  -map 0:v:0 -map 1:a:0 -c:v copy \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11" -ar 48000 -c:a aac -b:a 192k \
  -metadata title="Rare Disease, Real Kid — MVA Hackathon 2026 Track 2 (Ryukijano)" \
  -metadata copyright="CC BY 4.0" -movflags +faststart out/track2_pitch.mp4
echo "wrote video/out/track2_pitch.mp4"
