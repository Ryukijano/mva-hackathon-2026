"""Run Ensembl VEP with AlphaMissense and popEVE plugins."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from typing import Iterable


FIELDS = [
    "Allele",
    "Consequence",
    "IMPACT",
    "SYMBOL",
    "Gene",
    "Feature",
    "BIOTYPE",
    "EXON",
    "INTRON",
    "HGVSc",
    "HGVSp",
    "cDNA_position",
    "CDS_position",
    "Protein_position",
    "Amino_acids",
    "Codons",
    "Existing_variation",
    "DISTANCE",
    "STRAND",
    "FLAGS",
    "SYMBOL_SOURCE",
    "HGNC_ID",
    "CANONICAL",
    "MANE",
    "TSL",
    "APPRIS",
    "CCDS",
    "ENSP",
    "SWISSPROT",
    "TREMBL",
    "UNIPARC",
    "UNIPROT_ISOFORM",
    "GENE_PHENO",
    "SIFT",
    "PolyPhen",
    "DOMAINS",
    "miRNA",
    "AF",
    "AFR_AF",
    "AMR_AF",
    "EAS_AF",
    "EUR_AF",
    "SAS_AF",
    "gnomADg_AF",
    "gnomADg_AFR_AF",
    "gnomADg_AMR_AF",
    "gnomADg_ASJ_AF",
    "gnomADg_EAS_AF",
    "gnomADg_FIN_AF",
    "gnomADg_NFE_AF",
    "gnomADg_OTH_AF",
    "gnomADg_SAS_AF",
    "gnomADe_AF",
    "CLIN_SIG",
    "SOMATIC",
    "PHENO",
    "PUBMED",
    "MOTIF_NAME",
    "MOTIF_POS",
    "HIGH_INF_POS",
    "MOTIF_SCORE_CHANGE",
    "TRANSCRIPTION_FACTORS",
    "am_pathogenicity",
    "am_class",
    "popEVE",
    "popEVE_SCORE",
    "popEVE_EVE",
    "popEVE_ESM1v",
    "popEVE_pop_adjusted_EVE",
    "popEVE_pop_adjusted_ESM1v",
    "popEVE_gap_frequency",
    "popEVE_gene",
    "popEVE_protein",
    "popEVE_mutant",
]


def build_vep_command(
    input_vcf: str | Path,
    output_vcf: str | Path,
    cache_dir: str | Path,
    fasta: str | Path | None,
    alpha_missense: str | Path,
    popeve: str | Path,
    plugins_dir: str | Path,
    assembly: str = "GRCh38",
    fork: int = 8,
    fields: Iterable[str] | None = None,
) -> list[str]:
    """Build a VEP command with the MVA-relevant plugins and fields."""
    fields = list(fields or FIELDS)
    cmd = [
        "vep",
        "--input_file", str(input_vcf),
        "--output_file", str(output_vcf),
        "--vcf",
        "--cache",
        "--offline",
        "--assembly", assembly,
        "--dir_cache", str(cache_dir),
        "--dir_plugins", str(plugins_dir),
        "--fork", str(fork),
        "--symbol",
        "--canonical",
        "--mane",
        "--biotype",
        "--domains",
        "--af_gnomadg",
        "--af_gnomade",
        "--pick",
        "--fields", ",".join(fields),
        "--plugin", f"AlphaMissense,file={alpha_missense}",
        "--plugin", f"EVE,popeve_file={popeve}",
    ]
    if fasta:
        cmd.extend(["--fasta", str(fasta)])
    return cmd


def run_vep(cmd: list[str]) -> Path:
    """Execute VEP and return the output file path."""
    output = Path(cmd[cmd.index("--output_file") + 1])
    if output.exists():
        return output
    subprocess.run(cmd, check=True)
    if not output.exists():
        raise FileNotFoundError(f"VEP did not produce {output}")
    return output


def split_csq_header(header: str) -> list[str]:
    """Parse the CSQ Format description from a VEP VCF header line."""
    m = re.search(r'Format: (.*?)"', header)
    if not m:
        raise ValueError("Could not parse VEP CSQ header")
    return [x.strip() for x in m.group(1).split("|")]
