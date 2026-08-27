"""Writer for the official Track 1 submission CSV."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

CSV_COLUMNS = [
    "proband_id",
    "chrom_1",
    "pos_1",
    "ref_1",
    "alt_1",
    "chrom_2",
    "pos_2",
    "ref_2",
    "alt_2",
    "epcr",
    "finding_type",
    "notes",
]


def _norm_field(value, upper: bool = False) -> str:
    if value is None:
        return ""
    s = str(value).strip()
    if upper:
        s = s.upper()
    return s


def write_submission(
    rows: Iterable[dict],
    output: str | Path,
    proband_id: str = "PROBAND01",
):
    """Write a Track 1 submission CSV.

    Normalizes chromosome to `chrN`, uppercases alleles, enforces `primary`/`secondary`
    finding_type, and keeps epcr in (0, 1].
    """
    with open(output, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            out = {col: _norm_field(row.get(col, "")) for col in CSV_COLUMNS}
            out["proband_id"] = proband_id

            for side in ("1", "2"):
                chrom = out[f"chrom_{side}"]
                if chrom and not chrom.lower().startswith("chr"):
                    out[f"chrom_{side}"] = f"chr{chrom}"
                out[f"ref_{side}"] = _norm_field(out[f"ref_{side}"], upper=True)
                out[f"alt_{side}"] = _norm_field(out[f"alt_{side}"], upper=True)

            epcr = float(out["epcr"])
            if not (0 < epcr <= 1):
                raise ValueError(f"EPCR {epcr} out of range (0,1]")
            out["epcr"] = f"{epcr:.6f}"

            finding = (out.get("finding_type") or "primary").strip().lower()
            if finding not in ("primary", "secondary"):
                finding = "primary" if float(epcr) > 0.5 else "secondary"
            out["finding_type"] = finding

            writer.writerow(out)
