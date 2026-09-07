#!/bin/bash
#SBATCH --job-name=mva_wgs_dl
#SBATCH --output=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/wgs_dl_%j.out
#SBATCH --error=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/wgs_dl_%j.err
#SBATCH --time=06:00:00
#SBATCH --partition=nodes
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G

# Download the 8 gated WGS FASTQs (~84 GB) from the SageBio HF dataset.
# Token is picked up automatically from HF_HOME (no keys in this script).

set -euo pipefail

source /scratch/kcwp264/.aire_scratch_env.sh
module load miniforge/24.7.1
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate /mnt/scratch/kcwp264/.conda_envs/mva-hackathon

PROJECT="/mnt/scratch/kcwp264/mva-hackathon-2026"
DEST="${PROJECT}/data/fastq"
mkdir -p "${DEST}" "${PROJECT}/logs"

python - <<'PY'
from huggingface_hub import snapshot_download
from pathlib import Path

dest = Path("/mnt/scratch/kcwp264/mva-hackathon-2026/data/fastq")
snapshot_download(
    repo_id="SageBio/mva-hackathon-2026-data",
    repo_type="dataset",
    allow_patterns=["*.fastq.gz"],
    local_dir=str(dest),
    max_workers=4,
)
PY

echo "=== downloaded ==="
ls -la "${DEST}"
echo "=== gzip integrity check ==="
for f in "${DEST}"/*.fastq.gz; do
  gzip -t "$f" && echo "OK $(basename "$f")"
done
echo "DOWNLOAD_DONE"
