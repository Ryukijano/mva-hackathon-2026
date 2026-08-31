#!/bin/bash
#SBATCH --job-name=mva_refs
#SBATCH --output=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/setup_refs_%j.out
#SBATCH --error=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/setup_refs_%j.err
#SBATCH --time=12:00:00
#SBATCH --partition=nodes
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G

set -euo pipefail

module load miniforge/24.7.1
source "$(conda info --base)/etc/profile.d/conda.sh"
ENV_PATH="/mnt/scratch/kcwp264/.conda_envs/mva-hackathon"
conda activate "${ENV_PATH}"

source /scratch/kcwp264/.aire_scratch_env.sh

bash /mnt/scratch/kcwp264/mva-hackathon-2026/scripts/setup_references.sh
