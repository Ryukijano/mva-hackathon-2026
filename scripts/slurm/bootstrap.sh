#!/bin/bash
#SBATCH --job-name=mva_bootstrap
#SBATCH --output=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/bootstrap_%j.out
#SBATCH --error=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/bootstrap_%j.err
#SBATCH --time=06:00:00
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G

set -euo pipefail

module load miniforge/24.7.1
source /scratch/kcwp264/.aire_scratch_env.sh

ENV_NAME="mva-hackathon"

# Create or update the conda environment
if conda env list | grep -q "^${ENV_NAME} "; then
  echo "Updating existing ${ENV_NAME} env..."
  conda env update -f /mnt/scratch/kcwp264/mva-hackathon-2026/environment.yaml --prune
else
  echo "Creating ${ENV_NAME} env..."
  conda env create -f /mnt/scratch/kcwp264/mva-hackathon-2026/environment.yaml
fi

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "${ENV_NAME}"

# Verify key tools
python -c "import cyvcf2, pysam, pandas; print('Python packages OK')"
vep --help | head -n 1 || true
spliceai -h | head -n 1 || true

# Stage reference files
bash /mnt/scratch/kcwp264/mva-hackathon-2026/scripts/setup_references.sh

echo "Bootstrap complete. Environment: ${ENV_NAME}"
