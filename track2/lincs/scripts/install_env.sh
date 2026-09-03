#!/bin/bash
#SBATCH --job-name=mva_lincs_env
#SBATCH --output=/mnt/scratch/kcwp264/mva-hackathon-2026/track2/lincs/logs/install_env_%j.out
#SBATCH --error=/mnt/scratch/kcwp264/mva-hackathon-2026/track2/lincs/logs/install_env_%j.err
#SBATCH --partition=nodes
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:00:00

set -e

# AIRE scratch-first environment (caches, HF, etc.)
if [ -f /scratch/kcwp264/.aire_scratch_env.sh ]; then
    source /scratch/kcwp264/.aire_scratch_env.sh
fi

module load miniforge/24.7.1

ENV_PREFIX="/scratch/kcwp264/.conda_envs/mva-hackathon-lincs"
YAML_FILE="/mnt/scratch/kcwp264/mva-hackathon-2026/track2/lincs/environment_lincs.yaml"

# Remove any partially-created environment to avoid "prefix already exists" errors
if [ -d "${ENV_PREFIX}/conda-meta" ]; then
    echo "Existing environment found at ${ENV_PREFIX}; removing before fresh install."
    mamba env remove -p "${ENV_PREFIX}" -y
fi

echo "Creating mva-hackathon-lincs environment at ${ENV_PREFIX}..."
mamba env create -f "${YAML_FILE}" -p "${ENV_PREFIX}" --verbose

echo "Environment created. Verifying core packages..."
{
    echo "=== Python packages ==="
    conda run -p "${ENV_PREFIX}" python - <<'PY'
import importlib, sys
pkgs = ['pandas', 'numpy', 'scipy', 'sklearn', 'requests', 'yaml', 'tqdm', 'matplotlib', 'seaborn', 'openpyxl']
for p in pkgs:
    try:
        importlib.import_module(p)
        print(f'OK: {p}')
    except Exception as e:
        print(f'FAIL: {p}: {e}')
try:
    import pydeseq2
    print('OK: pydeseq2')
except Exception as e:
    print(f'FAIL: pydeseq2: {e}')
try:
    import cmapPy
    print('OK: cmapPy')
except Exception as e:
    print(f'FAIL: cmapPy: {e}')
try:
    import lincs
    print('OK: lincs')
except Exception as e:
    print(f'FAIL: lincs: {e}')
PY

    echo "=== R packages ==="
    conda run -p "${ENV_PREFIX}" Rscript - <<'R'
required <- c('limma', 'edgeR', 'GEOquery', 'ggplot2', 'dplyr', 'readr', 'stringr', 'data.table')
for (pkg in required) {
  loaded <- tryCatch({
    library(pkg, character.only = TRUE, logical.return = TRUE)
  }, error = function(e) {
    message(sprintf('FAIL: %s: %s', pkg, conditionMessage(e)))
    FALSE
  })
  if (isTRUE(loaded)) {
    message(sprintf('OK: %s', pkg))
  }
}
R
} >> /mnt/scratch/kcwp264/mva-hackathon-2026/track2/lincs/logs/install_env_verify.txt

echo "Install and verification complete. See install_env_verify.txt"
