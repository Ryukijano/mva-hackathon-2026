#!/bin/bash
#SBATCH --job-name=mva_track1
#SBATCH --output=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/track1_%j.out
#SBATCH --error=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/track1_%j.err
#SBATCH --time=06:00:00
#SBATCH --partition=nodes
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G

set -euo pipefail

module load miniforge/24.7.1
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate /mnt/scratch/kcwp264/.conda_envs/mva-hackathon
source /scratch/kcwp264/.aire_scratch_env.sh

export TF_CPP_MIN_LOG_LEVEL=2

PROJECT="/mnt/scratch/kcwp264/mva-hackathon-2026"
mkdir -p "${PROJECT}/results"

python "${PROJECT}/scripts/run_track1.py" \
  --vcf "${PROJECT}/data/WGS_EX2312012_HGWCNDSX7.vcf.gz" \
  --pheno "${PROJECT}/data/Challenge_Clinical_Phenotype_1.docx" \
  -o "${PROJECT}/results/track1_primary.csv"
