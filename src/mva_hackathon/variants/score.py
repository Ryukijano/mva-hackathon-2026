"""Variant scoring for Track 1.

Aggregates popEVE, AlphaMissense, SpliceAI, CADD, and gnomAD AF into a single
per-variant pathogenicity score and then into compound-het pair scores.
"""
from __future__ import annotations

import math


def popEVE_to_prob(popeve: float, severe_threshold: float = -5.056) -> float:
    """Map a popEVE score to a (0,1] probability-like pathogenicity score.

    More negative = more severe. At severe_threshold the sigmoid is at 0.5.
    """
    return float(1.0 / (1.0 + math.exp(popeve + severe_threshold)))


def variant_pathogenicity(
    consequence: str,
    popeve: float | None,
    am_pathogenicity: float | None,
    spliceai_delta: float | None,
    cadd: float | None,
    ptv_score: float = 0.99,
    missense_pop_weight: float = 0.7,
    missense_am_weight: float = 0.3,
) -> float:
    """Return a single pathogenicity score in (0,1] for a variant."""
    consequence = consequence or ""
    terms = {t.strip().lower() for t in consequence.split(",")}

    # Protein-truncating / severe structural variants
    ptv_terms = {
        "frameshift_variant",
        "stop_gained",
        "stop_lost",
        "start_lost",
        "splice_acceptor_variant",
        "splice_donor_variant",
    }
    if terms & ptv_terms:
        return ptv_score

    # Missense: combine popEVE and AlphaMissense
    if "missense_variant" in terms or "protein_altering_variant" in terms:
        scores = []
        if popeve is not None:
            scores.append(missense_pop_weight * popEVE_to_prob(popeve))
        if am_pathogenicity is not None:
            scores.append(missense_am_weight * float(am_pathogenicity))
        if scores:
            return sum(scores)

    # Splice region / cryptic splice
    if terms & {
        "splice_region_variant",
        "splice_donor_5th_base_variant",
        "splice_donor_region_variant",
        "splice_acceptor_region_variant",
        "intron_variant",
    }:
        if spliceai_delta is not None and spliceai_delta > 0:
            return float(spliceai_delta)

    # Fallback: CADD
    if cadd is not None and cadd > 0:
        return min(1.0, cadd / 50.0)

    return 0.0


def pair_score(score1: float, score2: float) -> float:
    """Score a compound-het pair.

    Both alleles need to be damaging; a weak allele drags the pair down.
    """
    return max(0.0001, min(1.0, score1 * score2))


def epcr_from_pair(pair_score: float, primary: bool = True) -> float:
    """Convert a pair score to the final EPCR column value.

    Keep primaries high and secondaries in the 0.05-0.15 range as advised.
    """
    if primary:
        return max(0.5, min(1.0, pair_score))
    return max(0.05, min(0.15, pair_score))
