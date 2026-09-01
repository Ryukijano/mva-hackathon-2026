#!/bin/bash
#SBATCH --job-name=mva_e2b
#SBATCH --output=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/primekg_e2b_%j.out
#SBATCH --error=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/primekg_e2b_%j.err
#SBATCH --time=01:00:00
#SBATCH --partition=nodes
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G

set -euo pipefail
source /scratch/kcwp264/.aire_scratch_env.sh
module load miniforge/24.7.1
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate /mnt/scratch/kcwp264/.conda_envs/cjepa

export PYTHONPATH="/mnt/scratch/kcwp264/mva-hackathon-2026/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1

PROJECT="/mnt/scratch/kcwp264/mva-hackathon-2026"
OUT="${PROJECT}/experiments/2026-08-31_bub1b_computational/outputs/e2b_no_antitarget"
mkdir -p "${OUT}"

python "${PROJECT}/scripts/train_primekg_ranker.py" \
  --kg "${PROJECT}/refs/primekg/kg.csv" \
  --out-dir "${OUT}" \
  --epochs 50 \
  --dim 64 \
  --seeds 0 1 2 \
  --exclude-anti-targets
