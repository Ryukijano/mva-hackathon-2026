#!/bin/bash
#SBATCH --job-name=mva_wgs_align
#SBATCH --output=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/wgs_align_%A_%a.out
#SBATCH --error=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/wgs_align_%A_%a.err
#SBATCH --time=16:00:00
#SBATCH --partition=nodes
#SBATCH --cpus-per-task=12
#SBATCH --mem=48G
#SBATCH --array=0-3

# Per-lane alignment: bwa-mem2 mem | samtools sort, one array task per lane.
# Read group IDs encode the lane so duplicates can be marked across lanes
# after merging.

set -euo pipefail

source /scratch/kcwp264/.aire_scratch_env.sh
module load miniforge/24.7.1
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate /mnt/scratch/kcwp264/.conda_envs/mva-hackathon

PROJECT="/mnt/scratch/kcwp264/mva-hackathon-2026"
REF="${PROJECT}/refs/Homo_sapiens.GRCh38.dna.primary_assembly.fa"
FQDIR="${PROJECT}/data/fastq"
OUTDIR="${PROJECT}/data/bam/lanes"
mkdir -p "${OUTDIR}" "${PROJECT}/logs"

LANES=(L001 L002 L003 L004)
LANE="${LANES[$SLURM_ARRAY_TASK_ID]}"
SAMPLE="WGS_EX2312012_HGWCNDSX7_S16"
R1="${FQDIR}/${SAMPLE}_${LANE}_R1_001.fastq.gz"
R2="${FQDIR}/${SAMPLE}_${LANE}_R2_001.fastq.gz"
OUT="${OUTDIR}/${SAMPLE}_${LANE}.sorted.bam"

echo "lane=${LANE} r1=${R1}"
[ -f "${R1}" ] && [ -f "${R2}" ]

if [ -f "${OUT}" ]; then
  echo "output exists, skipping: ${OUT}"
  exit 0
fi

bwa-mem2 mem \
  -t "${SLURM_CPUS_PER_TASK}" \
  -R "@RG\tID:${LANE}\tSM:WGS_EX2312012\tPL:ILLUMINA\tLB:${SAMPLE}" \
  "${REF}" "${R1}" "${R2}" \
  | samtools sort -@ 8 -m 3G -o "${OUT}.tmp" -

mv "${OUT}.tmp" "${OUT}"
samtools index -@ 8 "${OUT}"
samtools flagstat "${OUT}" > "${OUT}.flagstat.txt"
echo "LANE_DONE ${LANE}"
