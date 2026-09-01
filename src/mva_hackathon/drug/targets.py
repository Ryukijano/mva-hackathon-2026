"""BUB1B-hypomorph therapeutic axis (UniProt accessions)."""

AXIS_TARGETS: dict[str, str] = {
    "BUB1B": "O60566",
    "SIRT2": "Q8IXJ6",
    "MTOR": "P42345",
    "ATG7": "O95352",
    "ATG5": "Q9H1Y0",
    "SOD2": "P04179",
    "NFE2L2": "Q16236",
    "TMEM173": "Q86WV6",
    "CGAS": "Q8N884",
    "JAK1": "P23458",
    "JAK2": "O60674",
    "IL6R": "P08887",
    "TTK": "P33981",
    "AURKB": "Q96GD4",
}

ANTI_TARGET_GENES = frozenset({"TTK", "AURKB", "TMEM173"})

# Literature MVA missenses (UniProt O60566 numbering) used as ESM-1v controls.
MVA_MISSENSE_CONTROLS: dict[str, tuple[str, str, str]] = {
    "N1002K": ("N", "K", 1002),  # this case
    "L1012P": ("L", "P", 1012),  # Hanks 2004 / mouse L1002P
    "R814H": ("R", "H", 814),  # Suijkerbuijk 2010
    "K668Q": ("K", "Q", 668),  # acetylation-mimic (North 2014), not an MVA allele
}

AA20 = "ACDEFGHIKLMNPQRSTVWY"
