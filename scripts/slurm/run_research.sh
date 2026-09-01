#!/bin/bash
#SBATCH --job-name=mva_esm1v
#SBATCH --output=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/research_%j.out
#SBATCH --error=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/research_%j.err
#SBATCH --time=00:45:00
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=85G

set -euo pipefail

source /scratch/kcwp264/.aire_scratch_env.sh
module load miniforge/24.7.1
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate /mnt/scratch/kcwp264/.conda_envs/cjepa

export PYTHONPATH="/mnt/scratch/kcwp264/mva-hackathon-2026/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1

PROJECT="/mnt/scratch/kcwp264/mva-hackathon-2026"
OUT="${PROJECT}/experiments/2026-08-31_bub1b_computational/outputs"
mkdir -p "${OUT}" "${PROJECT}/logs"

python -c "import torch; print('cuda', torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu')"

# ESM-1v only. Do not re-run PrimeKG here: E2 CSVs are the pre-registered result.
python "${PROJECT}/scripts/run_esm1v_missense.py" \
  --fasta "${PROJECT}/track2/data/O60566.fasta" \
  --out-dir "${OUT}" \
  --batch-size 8

python "${PROJECT}/scripts/plot_research_figures.py" --out-dir "${OUT}"

python - <<PY
from pathlib import Path
import json, torch, transformers
out = Path("${OUT}") / "environment.lock.json"
out.write_text(json.dumps({
    "torch": torch.__version__,
    "cuda": torch.version.cuda,
    "transformers": transformers.__version__,
    "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
    "job": "esm1v_windowed",
}, indent=2))
print("wrote", out)
PY
