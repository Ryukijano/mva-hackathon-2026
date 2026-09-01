#!/usr/bin/env python3
"""Train skip-gram embeddings on the PrimeKG BUB1B/MVA1 neighbourhood."""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import torch

from mva_hackathon.research.primekg_embed import (
    SEED_DISEASE_SUBSTR,
    extract_axis_subgraph,
    rank_drugs,
    train_embeddings,
)


def pick_query_nodes(nodes: dict[int, tuple[str, str]]) -> dict[str, int]:
    queries: dict[str, int] = {}
    for gid, (name, ntype) in nodes.items():
        key = name.strip().upper()
        t = ntype.lower()
        if key == "BUB1B" and "gene" in t:
            queries.setdefault("BUB1B", gid)
        if "disease" in t and name.lower() == "mosaic variegated aneuploidy syndrome 1":
            queries.setdefault("MVA1", gid)
        if "disease" in t and SEED_DISEASE_SUBSTR in name.lower() and "MVA" not in queries:
            queries.setdefault("MVA", gid)
    return queries


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kg", type=Path, default=Path("refs/primekg/kg.csv"))
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/2026-08-31_bub1b_computational/outputs"),
    )
    ap.add_argument("--epochs", type=int, default=50)
    ap.add_argument("--dim", type=int, default=64)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument(
        "--exclude-anti-targets",
        action="store_true",
        help="Drop TTK/AURKB/TMEM173 from the seed set (E2b ablation).",
    )
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    if not args.kg.exists():
        raise SystemExit(f"PrimeKG not found: {args.kg}")

    nodes, edges = extract_axis_subgraph(
        args.kg,
        exclude_anti_targets=args.exclude_anti_targets,
    )
    global_ids = sorted(nodes)
    id_to_local = {gid: i for i, gid in enumerate(global_ids)}
    mapped = [(id_to_local[a], id_to_local[b]) for a, b in edges]
    queries = pick_query_nodes(nodes)
    meta = {
        "n_nodes": len(nodes),
        "n_edges": len(edges),
        "exclude_anti_targets": args.exclude_anti_targets,
        "queries": {k: {"id": v, "name": nodes[v][0], "type": nodes[v][1]} for k, v in queries.items()},
        "n_drugs": sum(1 for _, t in nodes.values() if "drug" in t.lower()),
    }
    (args.out_dir / "primekg_subgraph_meta.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))
    if "BUB1B" not in queries:
        raise SystemExit("BUB1B node not found in subgraph")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    query_key = "MVA1" if "MVA1" in queries else ("MVA" if "MVA" in queries else "BUB1B")
    query_gid = queries[query_key]

    all_ranks: dict[str, list[dict]] = defaultdict(list)
    for seed in args.seeds:
        emb = train_embeddings(
            n_nodes=len(global_ids),
            mapped_edges=mapped,
            seed=seed,
            device=device,
            dim=args.dim,
            epochs=args.epochs,
        )
        ranked = rank_drugs(nodes, id_to_local, emb, query_gid)
        out_csv = args.out_dir / f"primekg_drug_ranks_seed{seed}.csv"
        with out_csv.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=["rank", "pct", "cosine", "name", "type", "node_id"])
            writer.writeheader()
            writer.writerows(ranked)
        for row in ranked:
            all_ranks[str(row["name"])].append(row)
        print(f"seed={seed} top5={[r['name'] for r in ranked[:5]]} n_drugs={len(ranked)}")

    # Mean rank across seeds
    summary = []
    n_seeds = len(args.seeds)
    for name, rows in all_ranks.items():
        mean_rank = sum(r["rank"] for r in rows) / n_seeds
        mean_cos = sum(r["cosine"] for r in rows) / n_seeds
        summary.append(
            {
                "name": name,
                "type": rows[0]["type"],
                "mean_rank": mean_rank,
                "mean_cosine": mean_cos,
                "n_seeds": n_seeds,
            }
        )
    summary.sort(key=lambda r: r["mean_rank"])
    with (args.out_dir / "primekg_drug_ranks_mean.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["mean_rank", "mean_cosine", "n_seeds", "name", "type"]
        )
        writer.writeheader()
        writer.writerows(summary)
    print(f"query={query_key} wrote {args.out_dir / 'primekg_drug_ranks_mean.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
