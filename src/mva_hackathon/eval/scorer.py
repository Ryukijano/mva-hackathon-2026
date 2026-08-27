"""Local clone of the MVA Track 1 scorer.

Mirrors the official `evaluation.py` from
`SageBio/rare-disease-real-kid-mva-hackathon-2026`.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any


Variant = tuple[str, int, str, str]

# CAGI6 RGP rank-point tiers, compressed for a single proband with max 10 candidates
RANK_POINT_TIERS = [
    (1, 100),
    (3, 50),
    (5, 25),
    (10, 10),
]


@dataclass
class SubmissionRow:
    variants: frozenset[Variant]
    epcr: float
    rank: int
    finding_type: str = "primary"


@dataclass
class ScoreResult:
    proband_id: str
    full_match_rank: int | None
    partial_match_rank: int | None
    rank_points: float
    f_max: float
    f_max_threshold: float | None
    n_predictions_at_f_max: int


def _parse_variant(chrom: str, pos: str, ref: str, alt: str) -> Variant | None:
    if not chrom or not pos:
        return None
    return (chrom.strip(), int(pos), ref.strip().upper(), alt.strip().upper())


def _ensure_chr(chrom: str) -> str:
    chrom = str(chrom).strip()
    if chrom.lower().startswith("chr"):
        body = chrom[3:]
    else:
        body = chrom
    return f"chr{body}"


def _rank_to_points(rank: int) -> int:
    for max_rank, points in RANK_POINT_TIERS:
        if rank <= max_rank:
            return points
    return 0


def load_submission(csv_path: str | Path) -> dict[str, list[SubmissionRow]]:
    """Load a Track 1 submission CSV and group rows by proband, sorted by EPCR desc."""
    by_proband: dict[str, list[tuple[frozenset[Variant], float, str]]] = {}

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row["proband_id"].strip()
            v1 = _parse_variant(row["chrom_1"], row["pos_1"], row["ref_1"], row["alt_1"])
            v2 = _parse_variant(
                row.get("chrom_2", ""),
                row.get("pos_2", ""),
                row.get("ref_2", ""),
                row.get("alt_2", ""),
            )
            if v1 is None:
                raise ValueError(f"Row missing primary variant for proband {pid}")
            variants = frozenset([v1, v2]) if v2 else frozenset([v1])
            epcr = float(row["epcr"])
            if not (0 < epcr <= 1):
                raise ValueError(f"EPCR {epcr} out of range (0,1] for proband {pid}")
            finding_type = (row.get("finding_type") or "primary").strip().lower()
            if finding_type not in ("primary", "secondary"):
                raise ValueError(
                    f"finding_type must be 'primary' or 'secondary' for proband {pid}, "
                    f"got '{finding_type}'"
                )
            by_proband.setdefault(pid, []).append((variants, epcr, finding_type))

    result: dict[str, list[SubmissionRow]] = {}
    for pid, rows in by_proband.items():
        if len(rows) > 10:
            raise ValueError(f"Proband {pid} has {len(rows)} rows; max is 10")
        # Sort descending by EPCR (ties broken by original order)
        rows_sorted = sorted(enumerate(rows), key=lambda x: (-x[1][1], x[0]))
        result[pid] = [
            SubmissionRow(variants=v, epcr=e, rank=i + 1, finding_type=ft)
            for i, (_, (v, e, ft)) in enumerate(rows_sorted)
        ]
    return result


def load_gold(gold_path: str | Path) -> frozenset[Variant]:
    """Load the ground-truth variant(s) for PROBAND01.

    Supports both:
      - a list of 4-tuples: [["chr1", 100, "A", "G"], ...]
      - { "PROBAND01": { "primary_variants": [{"chrom":...,"pos":...,"ref":...,"alt":...}] } }
    """
    import json

    with open(gold_path) as fh:
        raw = json.load(fh)

    if isinstance(raw, dict) and "primary_variants" in raw:
        variants = raw["primary_variants"]
    elif isinstance(raw, dict) and "PROBAND01" in raw:
        entry = raw["PROBAND01"]
        if isinstance(entry, list):
            variants = [{"chrom": v[0], "pos": v[1], "ref": v[2], "alt": v[3]} for v in entry]
        else:
            variants = entry.get("primary_variants", [])
    elif isinstance(raw, list):
        variants = [{"chrom": v[0], "pos": v[1], "ref": v[2], "alt": v[3]} for v in raw]
    else:
        raise ValueError(f"Unrecognised gold format in {gold_path}")

    return frozenset(
        (_ensure_chr(v["chrom"]), int(v["pos"]), v["ref"].upper(), v["alt"].upper())
        for v in variants
    )


def score_proband(
    proband_id: str,
    submission_rows: list[SubmissionRow],
    true_variants: frozenset[Variant],
) -> ScoreResult:
    """Score a single proband's submission against its known causal variant(s)."""
    is_compound_het = len(true_variants) == 2

    full_match_rank = None
    partial_match_rank = None

    for row in submission_rows:
        if row.variants == true_variants:
            full_match_rank = row.rank
            break

    if is_compound_het and full_match_rank is None:
        for row in submission_rows:
            if row.variants & true_variants:
                partial_match_rank = row.rank
                break

    if full_match_rank is not None:
        rank_points = float(_rank_to_points(full_match_rank))
    elif partial_match_rank is not None:
        rank_points = 0.5 * _rank_to_points(partial_match_rank)
    else:
        rank_points = 0.0

    thresholds = sorted({row.epcr for row in submission_rows}, reverse=True)
    best_f = 0.0
    best_threshold = None
    best_n = 0

    for t in thresholds:
        predicted_variants: set[Variant] = set()
        n_rows = 0
        for row in submission_rows:
            if row.epcr >= t:
                predicted_variants |= row.variants
                n_rows += 1

        tp = len(predicted_variants & true_variants)
        fp = len(predicted_variants - true_variants)
        fn = len(true_variants - predicted_variants)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        if f > best_f:
            best_f = f
            best_threshold = t
            best_n = n_rows

    return ScoreResult(
        proband_id=proband_id,
        full_match_rank=full_match_rank,
        partial_match_rank=partial_match_rank,
        rank_points=rank_points,
        f_max=best_f,
        f_max_threshold=best_threshold,
        n_predictions_at_f_max=best_n,
    )


def evaluate(csv_path: str | Path, gold_path: str | Path) -> dict[str, Any]:
    """Convenience wrapper: score the whole submission CSV against a gold JSON."""
    subs = load_submission(csv_path)
    if not subs:
        raise ValueError("No valid rows found in CSV")
    proband_id = next(iter(subs))
    true_variants = load_gold(gold_path)
    result = score_proband(proband_id, subs[proband_id], true_variants)
    return {
        "proband_id": result.proband_id,
        "full_match_rank": result.full_match_rank,
        "partial_match_rank": result.partial_match_rank,
        "rank_points": result.rank_points,
        "f_max": result.f_max,
        "f_max_threshold": result.f_max_threshold,
        "n_predictions_at_f_max": result.n_predictions_at_f_max,
    }
