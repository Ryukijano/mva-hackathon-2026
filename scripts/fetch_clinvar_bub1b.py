#!/usr/bin/env python3
"""Build the ClinVar BUB1B missense table (public FTP extract; no patient data)."""
from __future__ import annotations

import argparse
import json
import urllib.request
from collections import Counter
from pathlib import Path

from mva_hackathon.research.clinvar import (
    VARIANT_SUMMARY_URL,
    iter_bub1b_canonical_missense,
    write_table,
)
from mva_hackathon.research.esm1v import load_sequence


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return
    tmp = dest.with_suffix(dest.suffix + ".partial")
    urllib.request.urlretrieve(url, tmp)
    tmp.replace(dest)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--summary-gz",
        type=Path,
        default=Path("refs/clinvar/variant_summary.txt.gz"),
    )
    ap.add_argument(
        "--fasta",
        type=Path,
        default=Path("track2/data/O60566.fasta"),
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/2026-08-31_bub1b_computational/outputs/e1c_clinvar"),
    )
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    _download(VARIANT_SUMMARY_URL, args.summary_gz)

    seq = load_sequence(str(args.fasta))
    rows = []
    skipped_wt = 0
    for row in iter_bub1b_canonical_missense(args.summary_gz):
        pos = int(row["uniprot_pos"])
        if pos < 1 or pos > len(seq):
            skipped_wt += 1
            continue
        if seq[pos - 1] != row["wt"]:
            skipped_wt += 1
            continue
        rows.append(row)

    write_table(rows, args.out_dir / "clinvar_bub1b_canonical_missense.csv")
    blb = [r for r in rows if r["bucket"] == "B/LB"]
    write_table(blb, args.out_dir / "clinvar_bub1b_blb_missense.csv")

    buckets = Counter(r["bucket"] for r in rows)
    meta = {
        "n_canonical_missense_wt_checked": len(rows),
        "n_blb": len(blb),
        "n_blb_unique_alleles": len({r["label"] for r in blb}),
        "skipped_wt_mismatch_or_oob": skipped_wt,
        "buckets": dict(buckets),
        "transcript": "NM_001211.6",
        "uniprot": "O60566",
        "source": VARIANT_SUMMARY_URL,
    }
    (args.out_dir / "clinvar_bub1b_meta.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
