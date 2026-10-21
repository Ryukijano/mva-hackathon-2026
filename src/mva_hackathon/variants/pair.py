"""Compound-heterozygote pairing logic for MVA Track 1."""
from __future__ import annotations

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
