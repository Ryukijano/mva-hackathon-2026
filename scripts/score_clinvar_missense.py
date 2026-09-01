#!/usr/bin/env python3
"""Score a ClinVar missense CSV with the ESM-1v ensemble (UniProt O60566)."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import torch

from mva_hackathon.drug.targets import AA20
from mva_hackathon.research.esm1v import ensemble_llr, load_sequence


def _read_variants(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fasta", type=Path, default=Path("track2/data/O60566.fasta"))
    ap.add_argument("--variants-csv", type=Path, required=True)
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/2026-08-31_bub1b_computational/outputs/e1c_clinvar"),
    )
    ap.add_argument("--batch-size", type=int, default=8)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    seq = load_sequence(str(args.fasta))
    variants = _read_variants(args.variants_csv)
    if not variants:
        raise SystemExit(f"no variants in {args.variants_csv}")

    positions = []
    for row in variants:
        pos = int(row["uniprot_pos"])
        wt = row["wt"]
        if seq[pos - 1] != wt:
            raise SystemExit(f"WT mismatch at {pos}: FASTA {seq[pos - 1]} vs CSV {wt}")
        positions.append(pos)
    positions = sorted(set(positions))

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"device={device} n_positions={len(positions)} n_variants={len(variants)}")
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
    long_path = args.out_dir / "esm1v_clinvar_positions_llr.csv"
    with long_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(long_rows[0].keys()))
        writer.writeheader()
        writer.writerows(long_rows)

    scored = []
    for row in variants:
        pos = int(row["uniprot_pos"])
        mut = row["mut"]
        llr = scores[pos][mut]
        item = dict(row)
        item["llr"] = f"{llr:.6f}"
        scored.append(item)
    scored_path = args.out_dir / "esm1v_clinvar_missense_scores.csv"
    with scored_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(scored[0].keys()))
        writer.writeheader()
        writer.writerows(scored)

    blb_unique: dict[str, float] = {}
    for row in scored:
        if row.get("bucket") == "B/LB":
            blb_unique[row["label"]] = float(row["llr"])
    blb = sorted(blb_unique.values())
    n1002k = None
    named = args.out_dir.parent / "esm1v_named_missenses.json"
    if named.exists():
        for item in json.loads(named.read_text()):
            if item.get("label") == "N1002K":
                n1002k = float(item["llr"])
                break
    n = len(blb)
    if n == 0:
        median = None
    elif n % 2:
        median = blb[n // 2]
    else:
        median = 0.5 * (blb[n // 2 - 1] + blb[n // 2])
    summary = {
        "n_scored": len(scored),
        "n_blb_rows": sum(1 for r in scored if r.get("bucket") == "B/LB"),
        "n_blb_unique": len(blb),
        "blb_median_llr": median,
        "blb_mean_llr": sum(blb) / len(blb) if blb else None,
        "n1002k_llr": n1002k,
        "h1_weaker_than_blb_median": (
            None if n1002k is None or median is None else n1002k > median
        ),
        "device": str(device),
    }
    (args.out_dir / "esm1v_clinvar_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
