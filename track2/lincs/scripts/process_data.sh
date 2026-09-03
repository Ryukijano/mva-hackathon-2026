#!/bin/bash
#SBATCH --job-name=mva_lincs_process
#SBATCH --output=/mnt/scratch/kcwp264/mva-hackathon-2026/track2/lincs/logs/process_data_%j.out
#SBATCH --error=/mnt/scratch/kcwp264/mva-hackathon-2026/track2/lincs/logs/process_data_%j.err
#SBATCH --partition=nodes
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:00:00

set -e

# AIRE scratch-first environment
if [ -f /scratch/kcwp264/.aire_scratch_env.sh ]; then
    source /scratch/kcwp264/.aire_scratch_env.sh
fi

module load miniforge/24.7.1
conda activate /scratch/kcwp264/.conda_envs/mva-hackathon-lincs

Rscript /mnt/scratch/kcwp264/mva-hackathon-2026/track2/lincs/scripts/01_download_process_geo.R
