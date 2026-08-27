"""Parse the clinical phenotype docx and extract HPO / cancer priors."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def parse_docx(docx_path: str | Path) -> dict[str, Any]:
    """Return plain text and extracted entities from the phenotype docx."""
    try:
        import docx
    except ImportError as exc:
        raise ImportError("python-docx is required; install with conda/pip.") from exc

    doc = docx.Document(str(docx_path))
    text = "\n".join(p.text for p in doc.paragraphs)

    hpo_terms = re.findall(r"HP:\d+", text)
    cancer_mentions = any(
        kw in text.lower()
        for kw in ("cancer", "tumor", "tumour", "neoplasm", "malignancy", "wilms", "rhabdomyosarcoma")
    )

    return {
        "text": text,
        "hpo_terms": list(set(hpo_terms)),
        "cancer_mentioned": cancer_mentions,
    }
