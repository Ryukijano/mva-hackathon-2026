"""MVA gene panel loader and helpers."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import yaml

DEFAULT_PANEL = Path(__file__).parents[2] / "configs" / "panel.yaml"


def load_panel(path: str | Path | None = None) -> dict:
    """Load the MVA gene panel YAML."""
    with open(path or DEFAULT_PANEL) as fh:
        return yaml.safe_load(fh)


def all_panel_genes(panel: dict | None = None) -> set[str]:
    """Return the union of all MVA panel genes."""
    panel = panel or load_panel()
    genes = set()
    for category, value in panel.get("mva_panel", {}).items():
        if isinstance(value, dict) and "genes" in value:
            genes.update(value["genes"])
        elif isinstance(value, list):
            genes.update(value)
    return set(g for g in genes if isinstance(g, str))


def categorize_gene(gene: str, panel: dict | None = None) -> str | None:
    """Return the panel category of a gene, or None if not in the panel."""
    panel = panel or load_panel()
    for category, value in panel.get("mva_panel", {}).items():
        if isinstance(value, dict) and gene in value.get("genes", []):
            return category
        if isinstance(value, list) and gene in value:
            return category
    return None


def is_cancer_associated(gene: str, panel: dict | None = None) -> bool:
    """Return True if the gene is in the tumour-predisposed list."""
    panel = panel or load_panel()
    return gene in panel.get("cancer_associated_genes", [])


def iter_consequences(panel: dict | None = None) -> Iterable[str]:
    """Return the VEP consequence terms we consider functionally relevant."""
    panel = panel or load_panel()
    return panel.get("relevant_consequences", [])
