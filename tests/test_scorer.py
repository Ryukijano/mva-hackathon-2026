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


def test_track1_report_phasing_language_calibrated():
    """Track 1 report must use calibrated phasing language, not overclaim."""
    from pathlib import Path
    repo = Path(__file__).resolve().parent.parent
    report = repo / "submissions" / "Ryukijano_track1_report.md"
    assert report.exists(), f"Report not found at {report}"
    text = report.read_text()

    # Must state phase is unresolved / presumed, not confirmed
    assert "UNRESOLVED" in text or "unresolved" in text.lower(), \
        "Report must state phasing is unresolved"
    assert "presumed compound heterozygous" in text.lower(), \
        "Report must say 'presumed compound heterozygous'"

    # Must reference the validation plan
    assert "phasing_validation_plan.md" in text, \
        "Report must reference the molecular phasing validation plan"

    # Must not overclaim
    forbidden = [
        "phase was statistically confirmed",
        "definitively confirmed",
        "gold standard",
        "biologically mandated",
        "phase confirmed via SHAPEIT5",
    ]
    text_lower = text.lower()
    for phrase in forbidden:
        assert phrase not in text_lower, \
            f"Report contains overclaiming phrase: '{phrase}'"


def test_track1_report_has_alphagenome_section():
    """Track 1 report must include AlphaGenome AVI scores for both variants."""
    from pathlib import Path
    repo = Path(__file__).resolve().parent.parent
    report = repo / "submissions" / "Ryukijano_track1_report.md"
    text = report.read_text()
    assert "AlphaGenome" in text, "Report should mention AlphaGenome AVI"
    assert "AVI" in text, "Report should mention AVI scores"
    assert "33.76" in text, "Report should include p.Leu737Ter AVI Phred (33.76)"
    assert "25.61" in text, "Report should include p.Asn1002Lys AVI Phred (25.61)"


def test_track1_report_has_spliceai_deep_sweep():
    """Track 1 report must include the SpliceAI deep-intronic sweep results."""
    from pathlib import Path
    repo = Path(__file__).resolve().parent.parent
    report = repo / "submissions" / "Ryukijano_track1_report.md"
    text = report.read_text()
    assert "SpliceAI" in text, "Report should mention SpliceAI"
    assert "4999" in text, "Report should mention the -D 4999 deep sweep"
    assert "0.03" in text, "Report should include p.Leu737Ter max DS (0.03)"
    assert "0.02" in text, "Report should include p.Asn1002Lys max DS (0.02)"


def test_alphagenome_results_file_exists():
    """AlphaGenome AVI scores JSON must exist with both variants."""
    from pathlib import Path
    repo = Path(__file__).resolve().parent.parent
    path = repo / "supplement" / "track1" / "bub1b_avi_scores.json"
    assert path.exists(), f"AlphaGenome results not found at {path}"
    data = json.loads(path.read_text())
    assert len(data) == 2, f"Expected 2 variants, found {len(data)}"
    positions = {v["position"] for v in data}
    assert 40209701 in positions, "Missing p.Leu737Ter position"
    assert 40220612 in positions, "Missing p.Asn1002Lys position"


def test_spliceai_results_exist():
    """SpliceAI deep sweep VCF and summary must exist."""
    from pathlib import Path
    repo = Path(__file__).resolve().parent.parent
    vcf_path = repo / "supplement" / "track1" / "bub1b_full_gene_spliceai.vcf"
    summary_path = repo / "supplement" / "track1" / "spliceai_summary.md"
    assert vcf_path.exists(), f"SpliceAI VCF not found at {vcf_path}"
    assert summary_path.exists(), f"SpliceAI summary not found at {summary_path}"


def test_track1_report_clinvar_accession_correct():
    """Track 1 report must use the correct ClinVar accession VCV004600147.1, not VCV4600147."""
    from pathlib import Path
    repo = Path(__file__).resolve().parent.parent
    report = repo / "submissions" / "Ryukijano_track1_report.md"
    text = report.read_text()
    assert "VCV004600147" in text, "Report should use the correct accession VCV004600147"
    assert "VCV4600147" not in text, "Report should not use the old short form VCV4600147"
    assert "19 Sep 2025" in text, "Report should use the correct date 19 Sep 2025"
    assert "Jan 2026" not in text, "Report should not use the incorrect date Jan 2026"


def test_clinvar_verification_summary_exists():
    """The ClinVar verification summary must exist."""
    from pathlib import Path
    repo = Path(__file__).resolve().parent.parent
    path = repo / "supplement" / "track1" / "clinvar_verification.md"
    assert path.exists(), f"ClinVar verification not found at {path}"
    text = path.read_text()
    assert "VCV000533901" in text
    assert "VCV004600147" in text
    assert "19 Sep 2025" in text or "2025/09/19" in text
