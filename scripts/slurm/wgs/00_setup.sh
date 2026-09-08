#!/bin/bash
#SBATCH --job-name=mva_wgs_setup
#SBATCH --output=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/wgs_setup_%j.out
#SBATCH --error=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/wgs_setup_%j.err
#SBATCH --time=04:00:00
#SBATCH --partition=nodes
#SBATCH --cpus-per-task=8
#SBATCH --mem=200G

# One-time setup: add WGS tooling to the mva-hackathon env and build the
# bwa-mem2 index for the GRCh38 primary assembly FASTA.
#
# The VCF reference is
#   GCA_000001405.15_GRCh38_no_alt_analysis_set_plus_hs38d1_maskedGRC_exclusions_v2_no_chr.fasta
# i.e. GRCh38 primary assembly WITHOUT chr prefixes (VCF contigs are `15` etc.).
# The Ensembl primary assembly FASTA in refs/ uses the same bare contig names
# and identical chromosome coordinates, so it is coordinate-compatible for
# chr15 phasing work. Caveat: it lacks the hs38d1 decoy / alt contigs, which
# can slightly raise mismapping in repetitive regions; all downstream
# analyses therefore filter on MAPQ and use coarse (>=100 kb) bins.

set -euo pipefail

source /scratch/kcwp264/.aire_scratch_env.sh
module load miniforge/24.7.1
source "$(conda info --base)/etc/profile.d/conda.sh"

PROJECT="/mnt/scratch/kcwp264/mva-hackathon-2026"
ENV_PREFIX="/mnt/scratch/kcwp264/.conda_envs/mva-hackathon"
REF="${PROJECT}/refs/Homo_sapiens.GRCh38.dna.primary_assembly.fa"

mkdir -p "${PROJECT}/logs"

echo "=== conda env update (bwa-mem2, mosdepth, whatshap) ==="
conda env update --prefix "${ENV_PREFIX}" -f "${PROJECT}/environment.yaml"

conda activate "${ENV_PREFIX}"
# version strings differ between tools; never let a check kill the job
bwa-mem2 version || true
mosdepth --version || true
whatshap --version || true
samtools --version | head -1 || true

echo "=== bwa-mem2 index ==="
# .bwt.2bit.64 is the LAST file bwa-mem2 index writes - check it, not .0123,
# so a killed/killed-mid-build job can't leave a "complete-looking" index.
if [ -f "${REF}.bwt.2bit.64" ]; then
  echo "index already present, skipping"
else
  rm -f "${REF}.0123" "${REF}.amb" "${REF}.ann" "${REF}.pac" "${REF}.bwt.2bit.64"
  bwa-mem2 index "${REF}"
fi
for ext in 0123 amb ann pac bwt.2bit.64; do
  [ -f "${REF}.${ext}" ] || { echo "MISSING index file: ${REF}.${ext}"; exit 1; }
done
ls -la "${REF}".* | head -10

echo "=== sanity: contig naming ==="
head -1 "${REF}"
grep -c "^>" "${REF}" || true

echo "SETUP_DONE"
