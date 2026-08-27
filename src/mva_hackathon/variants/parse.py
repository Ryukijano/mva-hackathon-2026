"""Parse VEP-annotated VCFs into flat records for the MVA pipeline."""
from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any


def split_csq_format(header_line: str) -> list[str]:
    """Extract the CSQ column names from a VEP VCF header line."""
    m = re.search(r'Format: (.*?)"', header_line)
    if not m:
        raise ValueError("Could not parse CSQ Format header")
    return [x.strip() for x in m.group(1).split("|")]


def _as_float(value: str | None) -> float | None:
    if value is None or value == "" or value == "-":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_vep_vcf(vcf_path: str | Path) -> Iterator[dict[str, Any]]:
    """Yield one dict per CSQ block per VCF row.

    Requires cyvcf2 or pysam; falls back to a simple VCF reader.
    """
    try:
        from cyvcf2 import VCF
    except ImportError as exc:
        raise ImportError("cyvcf2 is required to parse VCFs; install with conda/pip.") from exc

    vcf = VCF(str(vcf_path))

    # Find CSQ header
    csq_header = None
    for line in vcf.raw_header.split("\n"):
        if line.startswith("##INFO=<ID=CSQ,"):
            csq_header = split_csq_format(line)
            break

    if not csq_header:
        raise ValueError(f"No VEP CSQ header found in {vcf_path}")

    chrom_col = csq_header.index("CHROM") if "CHROM" in csq_header else None
    pos_col = csq_header.index("POS") if "POS" in csq_header else None
    # VEP CSQ does not include CHROM/POS; we add them from the variant

    for variant in vcf:
        csq = variant.INFO.get("CSQ")
        if not csq:
            continue
        for transcript in csq.split(","):
            parts = transcript.split("|")
            if len(parts) != len(csq_header):
                continue
            record = dict(zip(csq_header, parts))
            record["CHROM"] = variant.CHROM
            record["POS"] = variant.POS
            record["REF"] = variant.REF
            record["ALT"] = str(variant.ALT[0]) if variant.ALT else ""
            record["ID"] = variant.ID or "."
            record["QUAL"] = variant.QUAL
            record["FILTER"] = variant.FILTER

            # Type-cast numeric scores
            record["popEVE"] = _as_float(record.get("popEVE"))
            record["am_pathogenicity"] = _as_float(record.get("am_pathogenicity"))
            record["gnomadg_AF"] = _as_float(record.get("gnomadg_AF"))
            record["gnomADe_AF"] = _as_float(record.get("gnomADe_AF"))

            yield record
