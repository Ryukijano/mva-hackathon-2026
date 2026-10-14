#!/bin/bash
# Rerun ESM-1v ensemble LLR with the fixed residue_window (1-1022 for pos<=1022, 29-1050 otherwise)
# and ensemble size assert. Named residues (N1002K, L1012P, R814H, K668Q) + ClinVar B/LB control set.
# NOT SUBMITTED. Submit with:
#   sbatch /mnt/scratch/kcwp264/mva-hackathon-2026/experiments/2026-10-11_esm1v_fixed/run_esm1v_fixed.sbatch
# No API keys in this file; credentials come from the sourced scratch env only.
#SBATCH --job-name=mva_esm_fixed
#SBATCH --output=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/esm_fixed_%j.out
#SBATCH --error=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/esm_fixed_%j.err
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:00:00

set -euo pipefail

source /mnt/scratch/kcwp264/.aire_scratch_env.sh
module load miniforge/24.7.1
source "$(conda info --base)/etc/profile.d/conda.sh"
# Same env as the original ESM-1v GPU job (scripts/slurm/run_esm1v_clinvar.sh)
conda activate /mnt/scratch/kcwp264/.conda_envs/cjepa

export PYTHONPATH="/mnt/scratch/kcwp264/mva-hackathon-2026/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1

PROJECT="/mnt/scratch/kcwp264/mva-hackathon-2026"
NEW="${PROJECT}/experiments/2026-10-11_esm1v_fixed"
OLD_CLINVAR="${PROJECT}/experiments/2026-08-31_bub1b_computational/outputs/e1c_clinvar"
mkdir -p "${NEW}/named" "${NEW}/clinvar_blb" "${PROJECT}/logs"

python -c "import torch; print('cuda', torch.cuda.is_available())"

# 1) Named residues (driver scores all MVA_MISSENSE_CONTROLS: N1002K, L1012P, R814H, K668Q)
python "${PROJECT}/scripts/run_esm1v_missense.py" \
  --fasta "${PROJECT}/track2/data/O60566.fasta" \
  --out-dir "${NEW}/named" \
  --batch-size 8 \
  --named-only

# 2) ClinVar B/LB control set (same input CSV as the 2026-08-31 e1c job; read-only)
python "${PROJECT}/scripts/score_clinvar_missense.py" \
  --fasta "${PROJECT}/track2/data/O60566.fasta" \
  --variants-csv "${OLD_CLINVAR}/clinvar_bub1b_blb_missense.csv" \
  --out-dir "${NEW}/clinvar_blb" \
  --batch-size 8
