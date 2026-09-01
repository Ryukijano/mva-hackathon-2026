#!/bin/bash
#SBATCH --job-name=mva_esm_cpu
#SBATCH --output=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/esm_cpu_%j.out
#SBATCH --error=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/esm_cpu_%j.err
#SBATCH --time=02:00:00
#SBATCH --partition=nodes
#SBATCH --cpus-per-task=16
#SBATCH --mem=48G

set -euo pipefail

source /scratch/kcwp264/.aire_scratch_env.sh
module load miniforge/24.7.1
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate /mnt/scratch/kcwp264/.conda_envs/cjepa

export PYTHONPATH="/mnt/scratch/kcwp264/mva-hackathon-2026/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-16}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK:-16}"

PROJECT="/mnt/scratch/kcwp264/mva-hackathon-2026"
OUT="${PROJECT}/experiments/2026-08-31_bub1b_computational/outputs/esm1v_cpu_named"
mkdir -p "${OUT}" "${PROJECT}/logs"

python -c "import torch; print('cuda', torch.cuda.is_available(), 'threads', torch.get_num_threads())"

python "${PROJECT}/scripts/run_esm1v_missense.py" \
  --fasta "${PROJECT}/track2/data/O60566.fasta" \
  --out-dir "${OUT}" \
  --batch-size 4 \
  --named-only
