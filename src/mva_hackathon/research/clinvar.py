"""ClinVar BUB1B missense table from NCBI variant_summary (GRCh38, NM_001211)."""
from __future__ import annotations

import csv
import gzip
import re
from collections.abc import Iterator
from pathlib import Path

AA3_TO_1 = {
    "Ala": "A",
    "Cys": "C",
    "Asp": "D",
    "Glu": "E",
    "Phe": "F",
    "Gly": "G",
    "His": "H",
    "Ile": "I",
    "Lys": "K",
    "Leu": "L",
    "Met": "M",
    "Asn": "N",
    "Pro": "P",
    "Gln": "Q",
    "Arg": "R",
    "Ser": "S",
    "Thr": "T",
    "Val": "V",
    "Trp": "W",
    "Tyr": "Y",
}

CANONICAL_NM = "NM_001211"
PROTEIN_HGVS = re.compile(r"p\.([A-Z][a-z]{2})(\d+)([A-Z][a-z]{2})\b")

B_LB = frozenset({"benign", "likely benign", "benign/likely benign"})
P_LP = frozenset({"pathogenic", "likely pathogenic", "pathogenic/likely pathogenic"})

VARIANT_SUMMARY_URL = (
    "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz"
)


def parse_protein_hgvs(name: str) -> tuple[str, int, str] | None:
    """Return (wt, pos, mut) one-letter codes from a ClinVar Name field."""
    match = PROTEIN_HGVS.search(name)
    if match is None:
        return None
    wt3, pos_s, mut3 = match.group(1), match.group(2), match.group(3)
    if wt3 not in AA3_TO_1 or mut3 not in AA3_TO_1:
        return None
    wt, mut = AA3_TO_1[wt3], AA3_TO_1[mut3]
    if wt == mut:
        return None
    return wt, int(pos_s), mut


def significance_bucket(clinical_significance: str) -> str:
    low = clinical_significance.strip().lower()
    if "conflict" in low:
        return "conflicting"
    if low in B_LB:
        return "B/LB"
    if low in P_LP:
        return "P/LP"
    if "uncertain" in low:
        return "VUS"
    return "other"


def iter_bub1b_canonical_missense(summary_gz: Path) -> Iterator[dict[str, str]]:
    """Yield unique GRCh38 NM_001211 missense rows for BUB1B."""
    seen: set[tuple[str, int, str, str]] = set()
    with gzip.open(summary_gz, "rt") as fh:
        header = fh.readline().lstrip("#").rstrip("\n").split("\t")
        idx = {col: i for i, col in enumerate(header)}
        required = (
            "GeneSymbol",
            "Assembly",
            "Name",
            "ClinicalSignificance",
            "ReviewStatus",
            "OriginSimple",
            "VariationID",
            "Type",
            "Chromosome",
            "PositionVCF",
            "ReferenceAlleleVCF",
            "AlternateAlleleVCF",
        )
        missing = [col for col in required if col not in idx]
        if missing:
            raise KeyError(f"variant_summary missing columns: {missing}")
        for line in fh:
            row = line.rstrip("\n").split("\t")
            if row[idx["GeneSymbol"]] != "BUB1B":
                continue
            if row[idx["Assembly"]] != "GRCh38":
                continue
            name = row[idx["Name"]]
            if CANONICAL_NM not in name:
                continue
            parsed = parse_protein_hgvs(name)
            if parsed is None:
                continue
            wt, pos, mut = parsed
            bucket = significance_bucket(row[idx["ClinicalSignificance"]])
            key = (wt, pos, mut, row[idx["VariationID"]])
            if key in seen:
                continue
            seen.add(key)
            yield {
                "variation_id": row[idx["VariationID"]],
                "name": name,
                "type": row[idx["Type"]],
                "clinical_significance": row[idx["ClinicalSignificance"]],
                "bucket": bucket,
                "review_status": row[idx["ReviewStatus"]],
                "origin_simple": row[idx["OriginSimple"]],
                "chrom": row[idx["Chromosome"]],
                "pos_vcf": row[idx["PositionVCF"]],
                "ref": row[idx["ReferenceAlleleVCF"]],
                "alt": row[idx["AlternateAlleleVCF"]],
                "wt": wt,
                "mut": mut,
                "uniprot_pos": str(pos),
                "label": f"{wt}{pos}{mut}",
            }


def write_table(rows: list[dict[str, str]], out_csv: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("no ClinVar rows to write")
    with out_csv.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
