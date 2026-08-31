#!/bin/bash
#SBATCH --job-name=mva_update_env
#SBATCH --output=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/update_env_%j.out
#SBATCH --error=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/update_env_%j.err
#SBATCH --time=04:00:00
#SBATCH --partition=nodes
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G

set -euo pipefail

export CONDA_PKGS_DIRS="/mnt/scratch/kcwp264/.conda_pkgs"
export CONDA_ENVS_DIRS="/mnt/scratch/kcwp264/.conda_envs"

module load miniforge/24.7.1
source /scratch/kcwp264/.aire_scratch_env.sh

ENV_PATH="/mnt/scratch/kcwp264/.conda_envs/mva-hackathon"

conda env update -p "${ENV_PATH}" -f /mnt/scratch/kcwp264/mva-hackathon-2026/environment.yaml --prune

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "${ENV_PATH}"
PIP_CACHE_DIR=/mnt/scratch/kcwp264/.pip_cache pip install --no-cache-dir -e /mnt/scratch/kcwp264/mva-hackathon-2026

vep --help | head -n 1 || true

echo "Env update complete."
