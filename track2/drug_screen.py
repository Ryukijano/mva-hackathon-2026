#!/usr/bin/env python3
"""Track 2 computational drug-repurposing screen.

Target-first screen against the ChEMBL REST API: for each gene in the
BUB1B-hypomorphism axis (SAC, SIRT2/NAD+, autophagy/mitochondria,
cGAS-STING/JAK-STAT), resolve the ChEMBL target and list all molecules with
an annotated mechanism of action, with their max clinical phase.

Usage:
    python track2/drug_screen.py [--out track2/data/chembl_axis_drugs.csv] [--approved-only]
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

CHEMBL = "https://www.ebi.ac.uk/chembl/api/data"

# Axis genes: symbol -> UniProt accession (single protein).
TARGETS = {
    "BUB1B": "O60566",   # BUBR1 (SAC) - direct causal gene
    "SIRT2": "Q8IXJ6",   # deacetylates/stabilises BUBR1 (K668)
    "MTOR": "P42345",    # mTORC1 - autophagy/SASP axis
    "FKBP1A": "P62942",  # FKBP12 - rapalog-binding immunophilin (rapamycin/everolimus/sirolimus)
    "ATG7": "O95352",    # autophagy machinery
    "ATG5": "Q9H1Y0",    # autophagy machinery
    "SOD2": "P04179",    # mitochondrial ROS scavenging
    "NFE2L2": "Q16236",  # Nrf2 - antioxidant response
    "TMEM173": "Q86WV6", # STING1 - micronuclei/cGAS-STING
    "CGAS": "Q8N884",    # cGAS - cytosolic DNA sensor
    "JAK1": "P23458",    # type-I IFN signalling
    "JAK2": "O60674",    # type-I IFN signalling
    "IL6R": "P08887",    # IL-6 survival axis in CIN
    "TTK": "P33981",     # MPS1 - SAC kinase (cancer context)
    "AURKB": "Q96GD4",   # Aurora B - error correction
}


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def resolve_target(uniprot: str) -> tuple[str, str]:
    url = (
        f"{CHEMBL}/target.json?target_components__accession={uniprot}"
        "&target_type=SINGLE%20PROTEIN"
    )
    data = get_json(url)
    for t in data.get("targets", []):
        return t["target_chembl_id"], t.get("pref_name", "")
    return "", ""


def mechanisms_for_target(target_chembl_id: str) -> list[dict]:
    url = f"{CHEMBL}/mechanism.json?target_chembl_id={target_chembl_id}&limit=100"
    return get_json(url).get("mechanisms", [])


def molecule_records(molecule_ids: list[str]) -> dict[str, dict]:
    if not molecule_ids:
        return {}
    url = (
        f"{CHEMBL}/molecule.json?molecule_chembl_id__in={','.join(molecule_ids)}"
        "&limit=100"
    )
    data = get_json(url)
    def _phase(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0.0

    return {
        m["molecule_chembl_id"]: {
            "drug_name": m.get("pref_name", ""),
            "max_phase": _phase(m.get("max_phase")),
        }
        for m in data.get("molecules", [])
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="track2/data/chembl_axis_drugs.csv")
    ap.add_argument(
        "--approved-only",
        action="store_true",
        help="Only keep mechanisms where the molecule has max_phase=4 (approved).",
    )
    args = ap.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for symbol, uniprot in TARGETS.items():
        target_id, target_name = resolve_target(uniprot)
        print(f"{symbol}: {target_id} ({target_name})", file=sys.stderr)
        if not target_id:
            continue
        mechs = mechanisms_for_target(target_id)
        ids = sorted({m["molecule_chembl_id"] for m in mechs if m.get("molecule_chembl_id")})
        records = molecule_records(ids)
        for m in mechs:
            mid = m.get("molecule_chembl_id", "")
            rec = records.get(mid, {"drug_name": "", "max_phase": 0})
            if args.approved_only and rec["max_phase"] != 4:
                continue
            rows.append(
                {
                    "gene": symbol,
                    "uniprot": uniprot,
                    "target_chembl_id": target_id,
                    "target_name": target_name,
                    "molecule_chembl_id": mid,
                    "drug_name": rec["drug_name"],
                    "max_phase": rec["max_phase"],
                    "mechanism_of_action": m.get("mechanism_of_action", ""),
                }
            )
        time.sleep(0.3)

    with out_path.open("w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "gene", "uniprot", "target_chembl_id", "target_name",
                "molecule_chembl_id", "drug_name", "max_phase", "mechanism_of_action",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} drug-target rows to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
