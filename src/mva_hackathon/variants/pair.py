"""Compound-heterozygote pairing logic for MVA Track 1."""
from __future__ import annotations

import itertools
from collections import defaultdict
from typing import Any


def group_variants_by_gene(variants: list[dict[str, Any]], gene_key: str = "SYMBOL") -> dict[str, list[dict]]:
    """Group scored variants by their gene symbol."""
    by_gene = defaultdict(list)
    for v in variants:
        gene = v.get(gene_key) or v.get("gene")
        if gene:
            by_gene[gene].append(v)
    return dict(by_gene)


def top_pairs(
    by_gene: dict[str, list[dict]],
    pair_fn,
    score_key: str = "pathogenicity",
    max_pairs_per_gene: int = 1,
) -> list[dict]:
    """For each gene, return the top-scoring variant pairs.

    `pair_fn(variant1, variant2) -> dict` must add keys like `chrom_1`,
    `pos_1`, etc. and `epcr`/`score`.
    """
    rows = []
    for gene, variants in by_gene.items():
        if len(variants) < 2:
            continue
        # Sort so the strongest variant is first
        variants = sorted(variants, key=lambda x: x.get(score_key, 0.0), reverse=True)
        # Try all combinations, score, and keep top per gene
        candidates = []
        for a, b in itertools.combinations(variants, 2):
            row = pair_fn(a, b)
            if row:
                row["gene"] = gene
                candidates.append(row)
        candidates.sort(key=lambda r: r.get("epcr", 0.0), reverse=True)
        rows.extend(candidates[:max_pairs_per_gene])
    return rows


def pair_variants(a: dict, b: dict) -> dict[str, Any] | None:
    """Build a CSV row from two scored variants.

    Variants are expected to carry keys: chrom, pos, ref, alt, pathogenicity.
    """
    from mva_hackathon.variants.score import epcr_from_pair, pair_score

    s1 = float(a.get("pathogenicity", 0.0))
    s2 = float(b.get("pathogenicity", 0.0))
    ps = pair_score(s1, s2)

    row = {
        "chrom_1": a.get("chrom"),
        "pos_1": a.get("pos"),
        "ref_1": a.get("ref"),
        "alt_1": a.get("alt"),
        "chrom_2": b.get("chrom"),
        "pos_2": b.get("pos"),
        "ref_2": b.get("ref"),
        "alt_2": b.get("alt"),
        "pathogenicity": ps,
    }
    return row
