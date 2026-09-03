#!/usr/bin/env python3
"""Fetch all ChEMBL max_phase=4 molecules and cache as a lookup CSV."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import requests


def fetch_all() -> list[dict]:
    base = "https://www.ebi.ac.uk/chembl/api/data/molecule"
    molecules = []
    offset = 0
    limit = 1000
    while True:
        r = requests.get(
            base,
            params={
                "max_phase": 4,
                "format": "json",
                "limit": limit,
                "offset": offset,
                "fields": "pref_name,molecule_chembl_id,molecule_type,first_approval,usAN_stem",
            },
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
        page = data.get("molecules", [])
        if not page:
            break
        molecules.extend(page)
        offset += len(page)
        print(f"fetched {len(molecules)} / {data['page_meta']['total_count']}")
        if len(molecules) >= data["page_meta"]["total_count"]:
            break
    return molecules


def main():
    out = Path("track2/lincs/data/chembl_all_approved_drugs.csv")
    if out.exists():
        print(f"{out} already exists, reloading")
        df = pd.read_csv(out)
    else:
        molecules = fetch_all()
        df = pd.DataFrame(molecules)
        out.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out, index=False)
        print(f"Wrote {out} ({len(df)} rows)")

    # Print some stats
    print(df["molecule_type"].value_counts().head())


if __name__ == "__main__":
    main()
