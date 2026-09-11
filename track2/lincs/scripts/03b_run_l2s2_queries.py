#!/usr/bin/env python3
"""Run L2S2 queries for all MVA/BUB1B signatures.

Usage:
    python track2/lincs/scripts/03b_run_l2s2_queries.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
DATA = BASE / "data"
RESULTS = BASE / "results" / "l2s2"
QUERY_SCRIPT = BASE / "scripts" / "03_query_lincs.py"

SIGNATURES = [
    "GSE22206_case_v_control",
    "GSE22206_LCL_case_v_control",
    "GSE22206_fibro_case_v_control",
    "GSE134781_hetL1002P_v_WT",
    "GSE134781_hetX753_v_WT",
    "GSE134780_HL1002P_v_WT_muscle",
    "GSE134780_HL1002P_v_WT_fat",
    "GSE134780_HH_v_WT_muscle",
    "GSE134780_HH_v_WT_fat",
    # GSE247267 is small RNA and not protein-coding; included for completeness but flagged.
    # "GSE247267_aneuploid_v_diploid",
]

SIZES = [100, 150, 250]


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    (BASE / "logs").mkdir(parents=True, exist_ok=True)

    for sig in SIGNATURES:
        for size in SIZES:
            up = DATA / f"{sig}_up_{size}.txt"
            down = DATA / f"{sig}_down_{size}.txt"
            if not up.exists() or not down.exists():
                print(f"missing signature files for {sig} {size}", file=sys.stderr)
                continue

            out_l2s2 = RESULTS / f"{sig}_{size}_l2s2_consensus.csv"
            out_l1k = RESULTS / f"{sig}_{size}_l1000cds2.csv"

            cmd = [
                sys.executable,
                str(QUERY_SCRIPT),
                "--up", str(up),
                "--down", str(down),
                "--name", f"{sig}_{size}",
                "--out", str(RESULTS),
                "--first", "100",
                "--sortby", "adj_pvalue_down",
                "--l1000cds2",
            ]
            print(f"querying L2S2+L1000CDS2: {sig} {size}")
            result = subprocess.run(cmd, capture_output=False, text=True)
            if result.returncode != 0:
                print(f"L2S2/L1000CDS2 query failed for {sig} {size}", file=sys.stderr)

    # Aggregate a simple summary
    summary = []
    for sig in SIGNATURES:
        for size in SIZES:
            out_l2s2 = RESULTS / f"{sig}_{size}_l2s2_consensus.csv"
            out_l1k = RESULTS / f"{sig}_{size}_l1000cds2.csv"
            n_l2s2 = 0
            n_l1k = 0
            if out_l2s2.exists():
                with out_l2s2.open() as f:
                    n_l2s2 = max(0, sum(1 for _ in f) - 1)
            if out_l1k.exists():
                with out_l1k.open() as f:
                    n_l1k = max(0, sum(1 for _ in f) - 1)
            summary.append(f"{sig}_{size},{n_l2s2},{n_l1k}")

    (RESULTS / "query_summary.csv").write_text("signature,n_l2s2_hits,n_l1000cds2_hits\n" + "\n".join(summary))
    print("wrote", RESULTS / "query_summary.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
