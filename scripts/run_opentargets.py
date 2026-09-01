#!/usr/bin/env python3
"""CPU research: Open Targets known drugs + MVA1 disease IDs."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from mva_hackathon.research.opentargets import fetch_axis_known_drugs, search_mva_diseases


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/2026-08-31_bub1b_computational/outputs"),
    )
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    hits = search_mva_diseases()
    (args.out_dir / "opentargets_mva_diseases.json").write_text(json.dumps(hits, indent=2))

    rows = fetch_axis_known_drugs()
    csv_path = args.out_dir / "opentargets_axis_known_drugs.csv"
    fields = [
        "gene",
        "ensembl_id",
        "drug_id",
        "drug_name",
        "disease_id",
        "disease_name",
        "phase",
        "mechanism_of_action",
    ]
    with csv_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    # Keep a copy next to the Track 2 dossier.
    dossier = Path("track2/data/opentargets_known_drugs.csv")
    dossier.parent.mkdir(parents=True, exist_ok=True)
    with dossier.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(hits)} MVA disease hits -> {args.out_dir / 'opentargets_mva_diseases.json'}")
    print(f"wrote {len(rows)} known-drug rows -> {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
