#!/usr/bin/env bash
# Full pitch build: VO -> timing -> frames -> mux -> QA.  Turntables (video/render/turntables.py)
# are built once separately (PyMOL; run on Slurm `nodes`).  Run render on a compute node:
#   srun -p nodes -c 16 --mem 32G -t 30 video/make.sh
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-$HOME/.venvs/mva-video/bin/python}
"$PY" video/tts.py --speed "${SPEED:-1.05}" --voice "${VOICE:-af_heart}"
"$PY" video/render/render.py --workers "${WORKERS:-14}"
video/assemble.sh
"$PY" video/qa.py
