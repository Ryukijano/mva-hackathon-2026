"""Validation tests for the Track 2 LINCS L1000CDS2 firewall and report."""

from pathlib import Path

import pandas as pd
import pytest


REPO = Path(__file__).resolve().parents[1]


def test_l1000cds2_results_exist():
    results_dir = REPO / "track2" / "lincs" / "results" / "l2s2"
    assert results_dir.exists()
    files = list(results_dir.glob("*_l1000cds2.csv"))
    assert len(files) >= 9, f"Expected >=9 L1000CDS2 result files, found {len(files)}"


def test_firewall_decisions_exist():
    path = REPO / "track2" / "lincs" / "results" / "lincs_firewall_decisions.csv"
    assert path.exists()
    df = pd.read_csv(path)
    assert len(df) > 0
    assert set(df["firewall_status"].unique()).issubset({"ACCEPT", "WEAK", "REJECT"})


def test_firewall_has_retrieval_sort_column():
    """The firewall must document the L2S2 retrieval sort order."""
    path = REPO / "track2" / "lincs" / "results" / "lincs_firewall_decisions.csv"
    df = pd.read_csv(path)
    assert "l2s2_retrieval_sort" in df.columns, "Missing l2s2_retrieval_sort column"
    # All drugs with L2S2 hits should have a non-empty retrieval_sort
    l2s2_drugs = df[df["l2s2_direction"] != "NO_LINCS_HIT"]
    if len(l2s2_drugs) > 0:
        assert l2s2_drugs["l2s2_retrieval_sort"].notna().any(), "No retrieval_sort values set"


def test_firewall_mixed_direction_not_accepted():
    """Drugs with MIXED L2S2 directionality must not be ACCEPT."""
    path = REPO / "track2" / "lincs" / "results" / "lincs_firewall_decisions.csv"
    df = pd.read_csv(path)
    mixed = df[df["l2s2_direction"] == "MIXED"]
    for _, row in mixed.iterrows():
        assert row["firewall_status"] != "ACCEPT", (
            f"{row['drug']} is MIXED but ACCEPT — MIXED penalty not applied"
        )


def test_firewall_sirolimus_is_weak_not_accept():
    """Sirolimus has MIXED directionality and must be WEAK, not ACCEPT."""
    path = REPO / "track2" / "lincs" / "results" / "lincs_firewall_decisions.csv"
    df = pd.read_csv(path)
    sirolimus = df[df["drug"].str.contains("sirolimus", case=False, na=False)]
    assert len(sirolimus) >= 1
    assert sirolimus.iloc[0]["firewall_status"] == "WEAK", (
        f"Sirolimus should be WEAK (MIXED direction), got {sirolimus.iloc[0]['firewall_status']}"
    )
    assert sirolimus.iloc[0]["l2s2_direction"] == "MIXED"


def test_firewall_no_accept_drugs():
    """With the MIXED penalty, no drug should be ACCEPT on the current data."""
    path = REPO / "track2" / "lincs" / "results" / "lincs_firewall_decisions.csv"
    df = pd.read_csv(path)
    accepted = df[df["firewall_status"] == "ACCEPT"]
    assert len(accepted) == 0, (
        f"Expected 0 ACCEPT drugs after MIXED penalty, found {len(accepted)}: "
        f"{accepted['drug'].tolist()}"
    )


def test_candidate_csv_has_lincs_columns():
    path = REPO / "track2" / "data" / "track2_candidates.csv"
    assert path.exists()
    df = pd.read_csv(path)
    for col in [
        "l2s2_n_signatures",
        "l2s2_min_pvalue",
        "l1k_n_signatures",
        "l1k_mean_score",
        "n_engines",
        "n_total_signatures",
        "lincs_firewall_status",
        "lincs_firewall_reason",
        "lincs_mechanism_flag",
        "l2s2_direction",
        "l2s2_retrieval_sort",
        "signature_has_nominal_genes",
    ]:
        assert col in df.columns, f"Missing column {col}"


def test_candidate_csv_sirolimus_weak():
    """Sirolimus must be WEAK in the candidate CSV, not ACCEPT."""
    path = REPO / "track2" / "data" / "track2_candidates.csv"
    df = pd.read_csv(path)
    row = df[df["drug"].str.contains("sirolimus", case=False, na=False)]
    assert len(row) == 1
    assert row.iloc[0]["lincs_firewall_status"] == "WEAK", (
        f"Sirolimus should be WEAK, got {row.iloc[0]['lincs_firewall_status']}"
    )


def test_signature_composition_exists():
    """signature_composition.csv must exist and track FDR vs nominal genes."""
    path = REPO / "track2" / "lincs" / "results" / "signature_composition.csv"
    assert path.exists()
    df = pd.read_csv(path)
    assert len(df) > 0
    for col in ["signature", "size", "up_fdr", "up_nominal", "down_fdr", "down_nominal", "has_nominal_genes"]:
        assert col in df.columns, f"Missing column {col}"


def test_report_has_lincs_section():
    path = REPO / "track2" / "track2_report.md"
    assert path.exists()
    text = path.read_text()
    assert "LINCS L2S2 + L1000CDS2" in text
    assert "false-rescue firewall" in text.lower()
    assert "perhexiline" in text.lower() and "sirolimus" in text.lower()


def test_report_no_overclaiming_language():
    """The report must not use validated/cross-species validation/unbiased language."""
    path = REPO / "track2" / "track2_report.md"
    text = path.read_text().lower()
    forbidden = [
        "cross-species validation",
        "unbiased computational",
        "independent computational validation",
        "validated treatment",
    ]
    for phrase in forbidden:
        assert phrase not in text, f"Report contains forbidden phrase: '{phrase}'"
