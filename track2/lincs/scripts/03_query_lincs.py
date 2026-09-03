#!/usr/bin/env python3
"""Query L2S2 (primary) and L1000CDS2 (secondary) with MVA/BUB1B signatures.

Usage:
    python track2/lincs/scripts/03_query_lincs.py \
        --up track2/lincs/data/GSE22206_up_150.txt \
        --down track2/lincs/data/GSE22206_down_150.txt \
        --name GSE22206_150 \
        --out track2/lincs/results/l2s2

The script freezes the full JSON response and writes a consensus CSV.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import requests

L2S2_URL = "https://l2s2.maayanlab.cloud/graphql"
L1000CDS2_URL = "https://maayanlab.cloud/L1000CDS2/query"

L2S2_QUERY = """
query PairEnrichmentQueryConsensus(
  $backgroundId: UUID!,
  $genesUp: [String]!,
  $genesDown: [String]!,
  $filterFda: Boolean = false,
  $filterKo: Boolean = false,
  $first: Int = 100,
  $topN: Int = 10000,
  $pvalueLe: Float = 0.05
) {
  background(id: $backgroundId) {
    pairedEnrich(
      filterTerm: ""
      offset: 0
      first: $first
      filterFda: $filterFda
      sortby: ""
      filterKo: $filterKo
      topN: $topN
      pvalueLe: $pvalueLe
      genesDown: $genesDown
      genesUp: $genesUp
    ) {
      consensusCount
      consensus {
        drug
        oddsRatio
        pvalue
        adjPvalue
        approved
        countSignificant
        countInsignificant
        countUpSignificant
        pvalueUp
        adjPvalueUp
        oddsRatioUp
        pvalueDown
        adjPvalueDown
        oddsRatioDown
      }
    }
  }
}
"""


def read_gene_list(path: Path) -> list[str]:
    genes: list[str] = []
    for line in path.read_text().splitlines():
        g = line.strip().upper()
        if g and not g.startswith("#"):
            genes.append(g)
    # Remove duplicates while preserving order
    return list(dict.fromkeys(genes))


def get_l2s2_background_id(retries: int = 3, sleep: float = 1.0) -> str:
    """Fetch the first public L2S2 background ID (there is usually only one)."""
    query = """
    {
      backgrounds(first: 5) {
        nodes {
          id
        }
        totalCount
      }
    }
    """
    for attempt in range(retries):
        try:
            resp = requests.post(L2S2_URL, json={"query": query}, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            nodes = data.get("data", {}).get("backgrounds", {}).get("nodes", [])
            if not nodes:
                raise RuntimeError("L2S2 returned no backgrounds")
            return nodes[0]["id"]
        except requests.RequestException as e:
            print(f"L2S2 background lookup attempt {attempt + 1}/{retries} failed: {e}", file=sys.stderr)
            if attempt < retries - 1:
                time.sleep(sleep * (attempt + 1))
            else:
                raise
    return ""


def query_l2s2(
    background_id: str,
    up_genes: list[str],
    down_genes: list[str],
    fda_only: bool = True,
    first: int = 100,
    retries: int = 3,
    sleep: float = 1.0,
) -> dict:
    payload = {
        "operationName": "PairEnrichmentQueryConsensus",
        "query": L2S2_QUERY,
        "variables": {
            "backgroundId": background_id,
            "genesUp": up_genes,
            "genesDown": down_genes,
            "filterFda": fda_only,
            "filterKo": True,
            "first": first,
            "topN": 10000,
            "pvalueLe": 0.05,
        },
    }
    for attempt in range(retries):
        try:
            resp = requests.post(L2S2_URL, json=payload, timeout=60)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"L2S2 attempt {attempt + 1}/{retries} failed: {e}", file=sys.stderr)
            if attempt < retries - 1:
                time.sleep(sleep * (attempt + 1))
            else:
                raise
    return {}


def query_l1000cds2(
    up_genes: list[str],
    down_genes: list[str],
    aggravate: bool = False,
    retries: int = 3,
    sleep: float = 1.0,
) -> dict:
    """Query legacy L1000CDS2 POST endpoint as a secondary/sensitivity check."""
    payload = {
        "data": {"upGenes": up_genes, "dnGenes": down_genes},
        "config": {
            "aggravate": aggravate,
            "searchMethod": "geneSet",
            "share": True,
            "combination": False,
            "db-version": "latest",
        },
        "metadata": [],
    }
    for attempt in range(retries):
        try:
            resp = requests.post(L1000CDS2_URL, json=payload, timeout=60)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"L1000CDS2 attempt {attempt + 1}/{retries} failed: {e}", file=sys.stderr)
            if attempt < retries - 1:
                time.sleep(sleep * (attempt + 1))
            else:
                raise
    return {}


def parse_l2s2_consensus(result: dict) -> list[dict]:
    data = result.get("data", {})
    background = data.get("background", {})
    if background is None:
        background = data.get("currentBackground", {}) or {}
    paired = background.get("pairedEnrich", {})
    consensus = paired.get("consensus", [])
    rows = []
    for c in consensus:
        rows.append(
            {
                "drug": c.get("drug"),
                "approved": c.get("approved"),
                "odds_ratio": c.get("oddsRatio"),
                "pvalue": c.get("pvalue"),
                "adj_pvalue": c.get("adjPvalue"),
                "pvalue_up": c.get("pvalueUp"),
                "adj_pvalue_up": c.get("adjPvalueUp"),
                "pvalue_down": c.get("pvalueDown"),
                "adj_pvalue_down": c.get("adjPvalueDown"),
                "count_significant": c.get("countSignificant"),
                "count_insignificant": c.get("countInsignificant"),
                "count_up_significant": c.get("countUpSignificant"),
            }
        )
    return rows


def parse_l1000cds2(result: dict) -> list[dict]:
    rows = []
    top = result.get("topMeta", result if isinstance(result, list) else [])
    for sig in top:
        overlap = sig.get("overlap", {}) or {}
        rows.append(
            {
                "drug": sig.get("pert_desc", ""),
                "pert_id": sig.get("pert_id", ""),
                "cell_line": sig.get("cell_id", ""),
                "dose": sig.get("pert_dose", ""),
                "time": sig.get("pert_time", ""),
                "score": sig.get("score", None),
                "deg_count": sig.get("DEGcount", None),
                "pubchem_id": sig.get("pubchem_id", ""),
                "drugbank_id": sig.get("drugbank_id", ""),
                "up_dn_overlap": ",".join(overlap.get("up/dn", [])),
                "dn_up_overlap": ",".join(overlap.get("dn/up", [])),
            }
        )
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description="Query L2S2 and L1000CDS2 with a gene signature.")
    ap.add_argument("--up", required=True, type=Path, help="Path to up-regulated gene list.")
    ap.add_argument("--down", required=True, type=Path, help="Path to down-regulated gene list.")
    ap.add_argument("--name", required=True, help="Signature name used for output files.")
    ap.add_argument("--out", default="track2/lincs/results/l2s2", help="Output directory.")
    ap.add_argument("--fda-only", action="store_true", default=True, help="L2S2 FDA-approved filter.")
    ap.add_argument("--first", type=int, default=100, help="Number of L2S2 consensus hits to return.")
    ap.add_argument("--background-id", help="L2S2 background UUID (auto-detected if omitted).")
    ap.add_argument("--l1000cds2", action="store_true", help="Also query L1000CDS2.")
    ap.add_argument("--sleep", type=float, default=0.5, help="Seconds to sleep between queries.")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    background_id = args.background_id or get_l2s2_background_id()
    print(f"L2S2 background id: {background_id}")

    up_genes = read_gene_list(args.up)
    down_genes = read_gene_list(args.down)

    print(f"{args.name}: {len(up_genes)} up, {len(down_genes)} down genes")

    l2s2_result = query_l2s2(
        background_id,
        up_genes,
        down_genes,
        fda_only=args.fda_only,
        first=args.first,
    )
    raw_path = out_dir / f"{args.name}_l2s2_raw.json"
    raw_path.write_text(json.dumps(l2s2_result, indent=2))
    print(f"wrote L2S2 raw response to {raw_path}")

    consensus_rows = parse_l2s2_consensus(l2s2_result)
    csv_path = out_dir / f"{args.name}_l2s2_consensus.csv"
    with csv_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=consensus_rows[0].keys() if consensus_rows else [])
        writer.writeheader()
        writer.writerows(consensus_rows)
    print(f"wrote {len(consensus_rows)} L2S2 consensus rows to {csv_path}")

    if args.l1000cds2:
        time.sleep(args.sleep)
        l1k_result = query_l1000cds2(up_genes, down_genes, aggravate=False)
        l1k_raw = out_dir / f"{args.name}_l1000cds2_raw.json"
        l1k_raw.write_text(json.dumps(l1k_result, indent=2))
        l1k_rows = parse_l1000cds2(l1k_result)
        l1k_csv = out_dir / f"{args.name}_l1000cds2.csv"
        with l1k_csv.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=l1k_rows[0].keys() if l1k_rows else [])
            writer.writeheader()
            writer.writerows(l1k_rows)
        print(f"wrote {len(l1k_rows)} L1000CDS2 rows to {l1k_csv}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
