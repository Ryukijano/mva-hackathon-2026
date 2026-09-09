#!/bin/bash
#SBATCH --job-name=mva_wgs_phase
#SBATCH --output=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/wgs_phase_%j.out
#SBATCH --error=/mnt/scratch/kcwp264/mva-hackathon-2026/logs/wgs_phase_%j.err
#SBATCH --time=10:00:00
#SBATCH --partition=nodes
#SBATCH --cpus-per-task=24
#SBATCH --mem=150G

# Merge lanes, mark duplicates, then run the three analyses that gate the
# Track 1 submission decision:
#   1. base counts at the two BUB1B alleles (VAF sanity)
#   2. WhatsHap read-backed phasing on chr15 het SNVs (in-trans check)
#   3. mosdepth 100 kb depth -> mosaic aneuploidy landscape

set -euo pipefail

source /scratch/kcwp264/.aire_scratch_env.sh
module load miniforge/24.7.1
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate /mnt/scratch/kcwp264/.conda_envs/mva-hackathon

export PYTHONPATH="/mnt/scratch/kcwp264/mva-hackathon-2026/src${PYTHONPATH:+:$PYTHONPATH}"

PROJECT="/mnt/scratch/kcwp264/mva-hackathon-2026"
REF="${PROJECT}/refs/Homo_sapiens.GRCh38.dna.primary_assembly.fa"
LANEDIR="${PROJECT}/data/bam/lanes"
BAMDIR="${PROJECT}/data/bam"
BAM="${BAMDIR}/WGS_EX2312012_HGWCNDSX7.bam"
VCF="${PROJECT}/data/WGS_EX2312012_HGWCNDSX7.vcf.gz"
OUT="${PROJECT}/results/wgs_phasing"
mkdir -p "${BAMDIR}" "${OUT}" "${PROJECT}/logs"

echo "=== merge + fixmate + markdup ==="
if [ ! -f "${BAM}" ]; then
  rm -f "${BAM}.tmp"
  # samtools markdup 1.x requires the 'ms' tag from fixmate -m, and fixmate
  # requires name-sorted input. Use a streaming pipeline: merge -> name-sort
  # -> fixmate -> coordinate-sort -> markdup.
  samtools merge -@ 10 -u - "${LANEDIR}"/*.sorted.bam \
    | samtools sort -n -@ 8 -m 2G -u - \
    | samtools fixmate -m -u - - \
    | samtools sort -@ 8 -m 2G -u - \
    | samtools markdup -r -@ 10 - "${BAM}.tmp"
  mv "${BAM}.tmp" "${BAM}"
fi
samtools index -@ 10 "${BAM}"
samtools flagstat -@ 10 "${BAM}" > "${OUT}/final.flagstat.txt"
samtools coverage "${BAM}" > "${OUT}/per_chrom_coverage.txt"
cat "${OUT}/final.flagstat.txt"

echo "=== base counts at the two BUB1B alleles (bcftools mpileup, all reads) ==="
# 15:40209701 p.Leu737Ter (T>G), 15:40220612 p.Asn1002Lys (T>G)
bcftools mpileup -A -a AD -f "${REF}" -r 15:40209701-40209701 -r 15:40220612-40220612 "${BAM}" \
  > "${OUT}/mpileup_bub1b.vcf" 2>/dev/null
cp "${OUT}/mpileup_bub1b.vcf" "${OUT}/mpileup_bub1b.vcf.bak"
bcftools query -f '%CHROM\t%POS\t%REF\t%ALT\t%DP\t[ %AD]\n' "${OUT}/mpileup_bub1b.vcf" > "${OUT}/mpileup_counts.txt"
cat "${OUT}/mpileup_counts.txt"

echo "=== mosdepth 100 kb bins, MAPQ>=20 ==="
if [ ! -f "${OUT}/wgs_100kb.regions.bed.gz" ]; then
  rm -f "${OUT}/wgs_100kb".*
  mosdepth -t 8 -n --by 100000 --mapq 20 \
    "${OUT}/wgs_100kb" "${BAM}"
fi
head -30 "${OUT}/wgs_100kb.mosdepth.summary.txt"

echo "=== het SNV VCF around BUB1B (phasing input) ==="
HETS="${OUT}/hets_bub1b.vcf.gz"
# BUB1B is around 40.2 Mb on chr15; 100 kb window keeps whatshap fast and focused
bcftools view -i 'GT="het" && TYPE="snp"' -r 15:40150000-40250000 -Oz -o "${HETS}" "${VCF}"
tabix -f "${HETS}"
bcftools view -H "${HETS}" | wc -l

echo "=== whatshap read-backed phasing (chr15) ==="
PHASED="${OUT}/chr15_phased.vcf"
if [ ! -f "${PHASED}" ]; then
  whatshap phase \
    --reference "${REF}" \
    --chromosome 15 \
    -o "${PHASED}" \
    "${HETS}" "${BAM}"
fi
whatshap stats --gtf="${OUT}/phasing_blocks.gtf" "${PHASED}" \
  > "${OUT}/phasing_stats.txt" 2>&1 || true
cat "${OUT}/phasing_stats.txt" | head -40

echo "=== phase of the two target sites ==="
grep -E "^(15)\s+(40209701|40220612)\s" "${PHASED}" || \
  echo "targets not both in phased output - inspect blocks"
grep -B2 -A2 -E "^15\s+40209701\s" "${PHASED}" | head -10

echo "=== aneuploidy landscape + phase report ==="
python "${PROJECT}/scripts/wgs_report.py" \
  --regions "${OUT}/wgs_100kb.regions.bed.gz" \
  --summary "${OUT}/wgs_100kb.mosdepth.summary.txt" \
  --phased-vcf "${PHASED}" \
  --stats "${OUT}/phasing_stats.txt" \
  --out-dir "${OUT}"

echo "PHASE_DEPTH_DONE"
