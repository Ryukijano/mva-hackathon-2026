"""Unit tests for the local MVA Track 1 scorer (mirrors official evaluation.py)."""
import csv
import json
import math
import tempfile
from pathlib import Path

import pytest

from mva_hackathon.eval.scorer import evaluate, load_gold, load_submission
from mva_hackathon.variants.score import (
    epcr_from_pair,
    pair_score,
    popEVE_to_prob,
    variant_pathogenicity,
)


def _make_csv(rows, path: Path):
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "proband_id",
                "chrom_1",
                "pos_1",
                "ref_1",
                "alt_1",
                "chrom_2",
                "pos_2",
                "ref_2",
                "alt_2",
                "epcr",
                "finding_type",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def _make_gold(path: Path, variant1=None, variant2=None):
    if variant1 is None:
        variant1 = ("chr15", 100, "A", "G")
    if variant2 is None:
        variant2 = ("chr15", 200, "C", "T")
    gold = {
        "PROBAND01": {
            "primary_variants": [
                {"chrom": variant1[0], "pos": variant1[1], "ref": variant1[2], "alt": variant1[3]},
                {"chrom": variant2[0], "pos": variant2[1], "ref": variant2[2], "alt": variant2[3]},
            ]
        }
    }
    with open(path, "w") as fh:
        json.dump(gold, fh)


def test_full_match_rank1():
    with tempfile.TemporaryDirectory() as td:
        csv_path = Path(td) / "sub.csv"
        gold_path = Path(td) / "gold.json"
        _make_gold(gold_path)
        _make_csv(
            [
                {
                    "proband_id": "PROBAND01",
                    "chrom_1": "chr15",
                    "pos_1": 100,
                    "ref_1": "A",
                    "alt_1": "G",
                    "chrom_2": "chr15",
                    "pos_2": 200,
                    "ref_2": "C",
                    "alt_2": "T",
                    "epcr": 0.95,
                    "finding_type": "primary",
                    "notes": "",
                }
            ],
            csv_path,
        )
        result = evaluate(csv_path, gold_path)
        assert result["rank_points"] == 100.0
        assert result["f_max"] == 1.0


def test_one_allele_match():
    with tempfile.TemporaryDirectory() as td:
        csv_path = Path(td) / "sub.csv"
        gold_path = Path(td) / "gold.json"
        _make_gold(gold_path)
        _make_csv(
            [
                {
                    "proband_id": "PROBAND01",
                    "chrom_1": "chr15",
                    "pos_1": 100,
                    "ref_1": "A",
                    "alt_1": "G",
                    "chrom_2": "",
                    "pos_2": "",
                    "ref_2": "",
                    "alt_2": "",
                    "epcr": 0.95,
                    "finding_type": "primary",
                    "notes": "",
                }
            ],
            csv_path,
        )
        result = evaluate(csv_path, gold_path)
        assert result["rank_points"] == 50.0


def test_fmax_sweep_keeps_secondaries_low():
    with tempfile.TemporaryDirectory() as td:
        csv_path = Path(td) / "sub.csv"
        gold_path = Path(td) / "gold.json"
        _make_gold(gold_path)
        # primary full match high; incidental at low EPCR
        _make_csv(
            [
                {
                    "proband_id": "PROBAND01",
                    "chrom_1": "chr15",
                    "pos_1": 100,
                    "ref_1": "A",
                    "alt_1": "G",
                    "chrom_2": "chr15",
                    "pos_2": 200,
                    "ref_2": "C",
                    "alt_2": "T",
                    "epcr": 0.95,
                    "finding_type": "primary",
                    "notes": "",
                },
                {
                    "proband_id": "PROBAND01",
                    "chrom_1": "chr1",
                    "pos_1": 1,
                    "ref_1": "A",
                    "alt_1": "T",
                    "chrom_2": "chr1",
                    "pos_2": 2,
                    "ref_2": "G",
                    "alt_2": "C",
                    "epcr": 0.05,
                    "finding_type": "secondary",
                    "notes": "",
                },
            ],
            csv_path,
        )
        result = evaluate(csv_path, gold_path)
        assert result["rank_points"] == 100.0
        assert result["f_max"] == 1.0


def test_rank_sorts_by_epcr():
    with tempfile.TemporaryDirectory() as td:
        csv_path = Path(td) / "sub.csv"
        gold_path = Path(td) / "gold.json"
        _make_gold(gold_path)
        # True match on row 3 of file but with highest EPCR
        _make_csv(
            [
                {
                    "proband_id": "PROBAND01",
                    "chrom_1": "chr1",
                    "pos_1": 1,
                    "ref_1": "A",
                    "alt_1": "T",
                    "epcr": 0.2,
                    "finding_type": "secondary",
                },
                {
                    "proband_id": "PROBAND01",
                    "chrom_1": "chr1",
                    "pos_1": 2,
                    "ref_1": "G",
                    "alt_1": "C",
                    "epcr": 0.3,
                    "finding_type": "secondary",
                },
                {
                    "proband_id": "PROBAND01",
                    "chrom_1": "chr15",
                    "pos_1": 100,
                    "ref_1": "A",
                    "alt_1": "G",
                    "chrom_2": "chr15",
                    "pos_2": 200,
                    "ref_2": "C",
                    "alt_2": "T",
                    "epcr": 0.9,
                    "finding_type": "primary",
                },
            ],
            csv_path,
        )
        result = evaluate(csv_path, gold_path)
        assert result["full_match_rank"] == 1
        assert result["rank_points"] == 100.0


def test_chr_prefix_normalization():
    with tempfile.TemporaryDirectory() as td:
        gold_path = Path(td) / "gold.json"
        _make_gold(gold_path, ("15", 100, "a", "g"), ("15", 200, "c", "t"))
        gold = load_gold(gold_path)
        assert ("chr15", 100, "A", "G") in gold


def test_load_submission_rejects_bad_epcr():
    with tempfile.TemporaryDirectory() as td:
        csv_path = Path(td) / "sub.csv"
        _make_csv(
            [
                {
                    "proband_id": "PROBAND01",
                    "chrom_1": "chr1",
                    "pos_1": 1,
                    "ref_1": "A",
                    "alt_1": "T",
                    "epcr": 0.0,
                }
            ],
            csv_path,
        )
        with pytest.raises(ValueError):
            load_submission(csv_path)


def test_popEVE_sigmoid_shape():
    """More-negative popEVE scores must map to higher pathogenicity."""
    assert 0.49 < popEVE_to_prob(-5.056) < 0.51
    assert popEVE_to_prob(-8.0) > 0.90
    assert popEVE_to_prob(0.0) < 0.05
    assert popEVE_to_prob(-3.657) < popEVE_to_prob(-5.056)


def test_variant_pathogenicity_uses_popEVE_and_AM():
    """Missense pathogenicity combines popEVE and AlphaMissense."""
    # Strong popEVE, strong AM
    assert variant_pathogenicity(
        "missense_variant",
        popeve=-8.0,
        am_pathogenicity=0.95,
        spliceai_delta=None,
        cadd=None,
    ) > 0.9

    # Missing popEVE falls back to AM and double-weights it correctly
    am_only = variant_pathogenicity(
        "missense_variant",
        popeve=None,
        am_pathogenicity=0.92,
        spliceai_delta=None,
        cadd=None,
    )
    assert math.isclose(am_only, 0.92, rel_tol=1e-6)

    # Mild popEVE (-3.657) should not dominate over strong AM
    mixed = variant_pathogenicity(
        "missense_variant",
        popeve=-3.657,
        am_pathogenicity=0.9229,
        spliceai_delta=None,
        cadd=None,
    )
    assert 0.4 < mixed < 0.6


def test_pair_score_and_epcr():
    assert 0.0001 < pair_score(0.99, 0.92) <= 1.0
    assert epcr_from_pair(0.41, primary=True, primary_floor=0.95) == 0.95
    assert epcr_from_pair(0.41, primary=False, secondary_max=0.15) == 0.15
