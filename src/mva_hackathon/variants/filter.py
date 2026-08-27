"""Filter VEP-annotated variants to the MVA panel and rare allele frequency."""
from __future__ import annotations

from collections.abc import Iterable

from mva_hackathon.panel import all_panel_genes, iter_consequences, load_panel


def is_rare(
    gnomad_af: float | str | None,
    max_af: float = 0.001,
) -> bool:
    """Return True if gnomAD AF is missing or below max_af."""
    if gnomad_af is None or gnomad_af == "" or gnomad_af == ".":
        return True
    try:
        return float(gnomad_af) <= max_af
    except (ValueError, TypeError):
        return True


def has_relevant_consequence(consequence: str, panel: dict | None = None) -> bool:
    """Return True if any VEP consequence term is in the panel's relevant list."""
    panel = panel or load_panel()
    relevant = {c.lower() for c in iter_consequences(panel)}
    terms = {t.strip().lower() for t in (consequence or "").split(",")}
    return bool(terms & relevant)


def is_panel_gene(gene_symbol: str, panel: dict | None = None) -> bool:
    """Return True if the gene is in the MVA panel."""
    return gene_symbol and gene_symbol in all_panel_genes(panel)


def passes_basic_filter(
    record: dict,
    max_gnomad_af: float = 0.001,
    panel: dict | None = None,
) -> bool:
    """Return True if a VEP-parsed record passes panel/rare/consequence filters."""
    if not is_panel_gene(record.get("SYMBOL", record.get("gene")), panel):
        return False
    if not is_rare(record.get("gnomad_af", record.get("af")), max_gnomad_af):
        return False
    if not has_relevant_consequence(record.get("Consequence", record.get("consequence")), panel):
        return False
    return True


def keep_candidate(
    record: dict,
    max_gnomad_af: float = 0.001,
    panel: dict | None = None,
) -> bool:
    """Convenience alias for the basic filter."""
    return passes_basic_filter(record, max_gnomad_af, panel)
