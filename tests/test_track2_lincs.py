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


def test_firewall_accepted_hits():
    path = REPO / "track2" / "lincs" / "results" / "lincs_firewall_decisions.csv"
    df = pd.read_csv(path)
    accepted = df[df["firewall_status"] == "ACCEPT"]
    assert len(accepted) >= 1
    names = {clean.lower() for clean in accepted["drug"].astype(str).str.lower().str.strip()}
    assert any(n in names for n in {"perhexiline", "sirolimus"}), f"No expected accepted hits in {names}"


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
    ]:
        assert col in df.columns, f"Missing column {col}"


def test_candidate_csv_sirolimus_accepted():
    path = REPO / "track2" / "data" / "track2_candidates.csv"
    df = pd.read_csv(path)
    row = df[df["drug"].str.contains("sirolimus", case=False, na=False)]
    assert len(row) == 1
    assert row.iloc[0]["lincs_firewall_status"] in ("ACCEPT", "NO_L1000CDS2_HIT")


def test_report_has_lincs_section():
    path = REPO / "track2" / "track2_report.md"
    assert path.exists()
    text = path.read_text()
    assert "LINCS L2S2 + L1000CDS2" in text
    assert "false-rescue firewall" in text.lower()
    assert "perhexiline" in text.lower() and "sirolimus" in text.lower()
