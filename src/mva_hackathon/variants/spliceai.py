"""Run SpliceAI on a small candidate VCF and parse the results."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def run_spliceai(
    input_vcf: str | Path,
    output_vcf: str | Path,
    fasta: str | Path,
    annotation: str = "grch38",
    distance: int = 500,
    mask: int = 0,
) -> Path:
    """Run the `spliceai` command on a filtered candidate VCF.

    This is intended for a small set of variants in the MVA panel, not a
    whole-genome VCF.
    """
    output = Path(output_vcf)
    if output.exists():
        return output
    cmd = [
        "spliceai",
        "-I", str(input_vcf),
        "-O", str(output),
        "-R", str(fasta),
        "-A", annotation,
        "-D", str(distance),
        "-M", str(mask),
    ]
    subprocess.run(cmd, check=True)
    return output


def parse_spliceai_vcf(vcf_path: str | Path) -> dict[tuple[str, int, str, str], dict[str, Any]]:
    """Return a dict mapping variant (chrom, pos, ref, alt) to SpliceAI fields."""
    try:
        from cyvcf2 import VCF
    except ImportError as exc:
        raise ImportError("cyvcf2 is required") from exc

    results = {}
    vcf = VCF(str(vcf_path))
    for variant in vcf:
        key = (str(variant.CHROM), int(variant.POS), str(variant.REF), str(variant.ALT[0]))
        info = variant.INFO
        # SpliceAI INFO fields: ALLELE|SYMBOL|DS_AG|DS_AL|DS_DG|DS_DL|DP_AG|DP_AL|DP_DG|DP_DL
        pred = info.get("SpliceAI") or info.get("SpliceAI_pred")
        if pred:
            fields = pred.split("|")
            if len(fields) >= 6:
                ds = [float(x) for x in fields[2:6]]
                delta = max(ds)
                results[key] = {
                    "spliceai": pred,
                    "DS_AG": ds[0],
                    "DS_AL": ds[1],
                    "DS_DG": ds[2],
                    "DS_DL": ds[3],
                    "spliceai_delta": delta,
                }
    return results
