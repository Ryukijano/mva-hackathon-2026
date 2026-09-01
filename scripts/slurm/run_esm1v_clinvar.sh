#!/bin/bash
#SBATCH --job-name=mva_esm_cv
#SBATCH --output=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/esm_clinvar_%j.out
#SBATCH --error=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/esm_clinvar_%j.err
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
OUT="${PROJECT}/experiments/2026-08-31_bub1b_computational/outputs/e1c_clinvar"
mkdir -p "${OUT}" "${PROJECT}/logs"

python "${PROJECT}/scripts/score_clinvar_missense.py" \
  --fasta "${PROJECT}/track2/data/O60566.fasta" \
  --variants-csv "${OUT}/clinvar_bub1b_blb_missense.csv" \
  --out-dir "${OUT}" \
  --batch-size 8
