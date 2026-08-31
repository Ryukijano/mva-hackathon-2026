#!/bin/bash
#SBATCH --job-name=mva_bootstrap
#SBATCH --output=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/bootstrap_%j.out
#SBATCH --error=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/bootstrap_%j.err
#SBATCH --time=06:00:00
#SBATCH --partition=nodes
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G

set -euo pipefail

# Use $SCRATCH for the env/package cache; $HOME is at its 65 GB quota.
export CONDA_PKGS_DIRS="/mnt/scratch/kcwp264/.conda_pkgs"
export CONDA_ENVS_DIRS="/mnt/scratch/kcwp264/.conda_envs"

module load miniforge/24.7.1
source /scratch/kcwp264/.aire_scratch_env.sh

ENV_PATH="/mnt/scratch/kcwp264/.conda_envs/mva-hackathon"

# Create or update the conda environment
if [[ -d "${ENV_PATH}" ]]; then
  echo "Updating existing ${ENV_PATH}..."
  conda env update -p "${ENV_PATH}" -f /mnt/scratch/kcwp264/mva-hackathon-2026/environment.yaml --prune
else
  echo "Creating ${ENV_PATH}..."
  conda env create -p "${ENV_PATH}" -f /mnt/scratch/kcwp264/mva-hackathon-2026/environment.yaml
fi

# Verify key tools
"${ENV_PATH}/bin/python" -c "import cyvcf2, pysam, pandas; print('Python packages OK')"
"${ENV_PATH}/bin/vep" --help | head -n 1 || true
"${ENV_PATH}/bin/spliceai" -h | head -n 1 || true

# Activate for the tool checks below
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "${ENV_PATH}"

# Verify VEP perl deps are resolvable and SpliceAI can run
"${ENV_PATH}/bin/vep" --help | head -n 1 || true
"${ENV_PATH}/bin/spliceai" -h | head -n 1 || true

echo "Bootstrap complete. Environment: ${ENV_PATH}"
