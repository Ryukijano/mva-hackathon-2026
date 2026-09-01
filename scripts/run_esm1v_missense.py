#!/usr/bin/env python3
"""GPU: ESM-1v ensemble LLR on UniProt O60566 (BUBR1)."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import torch

from mva_hackathon.drug.targets import AA20, MVA_MISSENSE_CONTROLS
from mva_hackathon.research.esm1v import ensemble_llr, load_sequence


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fasta", type=Path, default=Path("track2/data/O60566.fasta"))
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/2026-08-31_bub1b_computational/outputs"),
    )
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--full-protein", action="store_true", help="Score every residue (slow).")
    ap.add_argument("--named-only", action="store_true", help="Score MVA_MISSENSE_CONTROLS only.")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    seq = load_sequence(str(args.fasta))
    expected = {668: "K", 737: "L", 814: "R", 1002: "N", 1012: "L"}
    for pos, aa in expected.items():
        if seq[pos - 1] != aa:
            raise SystemExit(f"Residue mismatch at {pos}: expected {aa}, found {seq[pos - 1]}")

    if args.full_protein:
        positions = list(range(1, len(seq) + 1))
    elif args.named_only:
        positions = sorted({pos for _, _, pos in MVA_MISSENSE_CONTROLS.values()})
    else:
        positions = sorted({pos for _, _, pos in MVA_MISSENSE_CONTROLS.values()})
        # C-lobe window around N1002 / L1012
        positions.extend(range(990, 1031))
        positions = sorted(set(positions))

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"device={device} n_positions={len(positions)} len(seq)={len(seq)}")
    scores = ensemble_llr(seq, positions, device=device, batch_size=args.batch_size)

    long_rows = []
    for pos, by_aa in sorted(scores.items()):
        wt = seq[pos - 1]
        for aa in AA20:
            long_rows.append(
                {
                    "uniprot": "O60566",
                    "pos": pos,
                    "wt": wt,
                    "mut": aa,
                    "llr_ensemble_mean": f"{by_aa[aa]:.6f}",
                    "is_wt": aa == wt,
                }
            )
    long_path = args.out_dir / "esm1v_bub1b_llr.csv"
    with long_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(long_rows[0].keys()))
        writer.writeheader()
        writer.writerows(long_rows)

    named = []
    for label, (wt, mut, pos) in MVA_MISSENSE_CONTROLS.items():
        named.append(
            {
                "label": label,
                "pos": pos,
                "wt": wt,
                "mut": mut,
                "llr": scores[pos][mut],
            }
        )
    (args.out_dir / "esm1v_named_missenses.json").write_text(json.dumps(named, indent=2))
    print(f"wrote {long_path}")
    for row in named:
        print(f"  {row['label']}: LLR={row['llr']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
