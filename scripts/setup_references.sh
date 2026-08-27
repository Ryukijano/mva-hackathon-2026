#!/usr/bin/env bash
# Stage public reference files for Track 1 on $SCRATCH.
set -euo pipefail

PROJECT="/mnt/scratch/kcwp264/mva-hackathon-2026"
REFS="${PROJECT}/refs"
CACHE="${PROJECT}/.cache"
mkdir -p "${REFS}" "${CACHE}/vep/Plugins"

source /scratch/kcwp264/.aire_scratch_env.sh || true

# AlphaMissense
if [[ ! -f "${REFS}/AlphaMissense_hg38.tsv.gz" ]]; then
  echo "Downloading AlphaMissense GRCh38..."
  wget -q --show-progress -O "${REFS}/AlphaMissense_hg38.tsv.gz" \
    "https://zenodo.org/records/10813168/files/AlphaMissense_hg38.tsv.gz"
fi
if [[ ! -f "${REFS}/AlphaMissense_hg38.tsv.gz.tbi" ]]; then
  tabix -s 1 -b 2 -e 2 -f -S 1 "${REFS}/AlphaMissense_hg38.tsv.gz"
fi

# popEVE
if [[ ! -f "${REFS}/grch38_popEVE_ukbb_20250715.vcf.gz" ]]; then
  echo "Downloading popEVE GRCh38..."
  wget -q --show-progress -O "${REFS}/grch38_popEVE_ukbb_20250715.vcf.gz" \
    "https://data.evemodel.org/popeve/v1.1/downloads/grch38_popEVE_ukbb_20250715.vcf.gz"
fi
if [[ ! -f "${REFS}/grch38_popEVE_ukbb_20250715.vcf.gz.tbi" ]]; then
  tabix -p vcf -f "${REFS}/grch38_popEVE_ukbb_20250715.vcf.gz"
fi

# Ensembl VEP cache (version 116, GRCh38). ~15 GB.
if [[ ! -d "${CACHE}/vep/homo_sapiens/" ]]; then
  echo "Downloading VEP cache..."
  VEP_DIR="${CACHE}/vep"
  mkdir -p "${VEP_DIR}"
  cd "${VEP_DIR}"
  wget -q --show-progress \
    "https://ftp.ensembl.org/pub/release-116/variation/indexed_vep_cache/homo_sapiens_vep_116_GRCh38.tar.gz"
  tar xzf "homo_sapiens_vep_116_GRCh38.tar.gz"
  rm -f "homo_sapiens_vep_116_GRCh38.tar.gz"
fi

# GRCh38 FASTA for SpliceAI / VEP
FASTA="${REFS}/Homo_sapiens.GRCh38.dna.primary_assembly.fa"
if [[ ! -f "${FASTA}" ]]; then
  if [[ ! -f "${FASTA}.gz" ]]; then
    echo "Downloading GRCh38 primary assembly FASTA..."
    wget -q --show-progress -O "${FASTA}.gz" \
      "https://ftp.ensembl.org/pub/release-116/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz"
  fi
  echo "Uncompressing FASTA (~25 GB)..."
  gunzip -c "${FASTA}.gz" > "${FASTA}"
fi

# Ensembl plugins
for plugin in AlphaMissense SpliceAI EVE; do
  if [[ ! -f "${CACHE}/vep/Plugins/${plugin}.pm" ]]; then
    wget -q -O "${CACHE}/vep/Plugins/${plugin}.pm" \
      "https://raw.githubusercontent.com/Ensembl/VEP_plugins/release/116/${plugin}.pm"
  fi
done

echo "References staged in ${REFS} and ${CACHE}/vep"
