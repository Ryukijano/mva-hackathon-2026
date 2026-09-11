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


def test_rescue_firewall_exists_and_confirms_zero_accept():
    """The rescue-sorted firewall must exist and also show 0 ACCEPT."""
    path = REPO / "track2" / "lincs" / "results" / "rescue_firewall" / "lincs_firewall_decisions.csv"
    assert path.exists(), "Rescue-sorted firewall decisions CSV not found"
    df = pd.read_csv(path)
    accepted = df[df["firewall_status"] == "ACCEPT"]
    assert len(accepted) == 0, (
        f"Rescue firewall should have 0 ACCEPT, found {len(accepted)}"
    )
    weak = df[df["firewall_status"] == "WEAK"]
    assert len(weak) == 2, f"Rescue firewall should have 2 WEAK, found {len(weak)}"


def test_rescue_firewall_comparison_summary_exists():
    """The rescue vs original firewall comparison summary must exist."""
    path = REPO / "track2" / "lincs" / "results" / "rescue_firewall" / "comparison_summary.md"
    assert path.exists()
    text = path.read_text()
    assert "ACCEPT=0" in text
    assert "WEAK=2" in text


def test_report_has_rescue_sorted_validation():
    """The Track 2 report must mention the rescue-sorted re-query validation."""
    path = REPO / "track2" / "track2_report.md"
    text = path.read_text()
    assert "rescue-sorted" in text.lower() or "adj_pvalue_down" in text.lower(), (
        "Report should mention the rescue-sorted re-query"
    )
    assert "ACCEPT=0" in text or "ACCEPT | 0" in text, (
        "Report should state the zero-ACCEPT result explicitly"
    )


def test_report_has_denominator_explanation():
    """The report must explain the n_total_signatures vs per-engine denominators."""
    path = REPO / "track2" / "track2_report.md"
    text = path.read_text()
    assert "Denominator note" in text or "denominator" in text.lower(), (
        "Report should explain the denominator"
    )


def test_report_has_preclinical_disclaimer():
    """The report must include a preclinical N-of-1 research disclaimer."""
    path = REPO / "track2" / "track2_report.md"
    text = path.read_text().lower()
    assert "preclinical" in text or "n-of-1" in text or "n of 1" in text, (
        "Report should contain a preclinical N-of-1 disclaimer"
    )
    assert "not clinical advice" in text or "not a treatment recommendation" in text, (
        "Report should explicitly state it is not clinical advice"
    )


def test_report_arimoclomol_combination_with_miglustat():
    """Arimoclomol must be described as FDA-approved 'in combination with miglustat'."""
    path = REPO / "track2" / "track2_report.md"
    text = path.read_text().lower()
    assert "in combination with miglustat" in text, (
        "Arimoclomol should be described as 'in combination with miglustat'"
    )


def test_report_baricitinib_jia_status():
    """Baricitinib must mention EMA approval for juvenile idiopathic arthritis."""
    path = REPO / "track2" / "track2_report.md"
    text = path.read_text().lower()
    assert "juvenile idiopathic arthritis" in text, (
        "Baricitinib should mention EMA JIA approval"
    )


def test_candidate_csv_arimoclomol_combination():
    """The candidate CSV must mention 'in combination with miglustat' for arimoclomol."""
    path = REPO / "track2" / "data" / "track2_candidates.csv"
    df = pd.read_csv(path)
    row = df[df["drug"].str.contains("arimoclomol", case=False, na=False)]
    assert len(row) == 1
    # Check across the relevant text columns
    text_cols = ["pediatric_status", "pediatric_indication", "mechanism", "evidence_source"]
    combined = " ".join(str(row.iloc[0].get(c, "")) for c in text_cols).lower()
    assert "in combination with miglustat" in combined, (
        "Arimoclomol should mention 'in combination with miglustat' in CSV text columns"
    )


def test_candidate_csv_baricitinib_jia():
    """The candidate CSV must mention EMA JIA for baricitinib."""
    path = REPO / "track2" / "data" / "track2_candidates.csv"
    df = pd.read_csv(path)
    row = df[df["drug"].str.contains("baricitinib", case=False, na=False)]
    assert len(row) == 1
    pediatric_status = str(row.iloc[0].get("pediatric_status", "")).lower()
    assert "juvenile idiopathic arthritis" in pediatric_status, (
        "Baricitinib pediatric_status should mention EMA JIA approval"
    )


def test_pitch_storyboard_has_firewall_count():
    """The pitch storyboard must include the firewall ACCEPT=0/WEAK=2/REJECT=674 result."""
    path = REPO / "track2" / "pitch_storyboard.md"
    text = path.read_text()
    assert "ACCEPT=0" in text, "Storyboard should state ACCEPT=0"
    assert "WEAK=2" in text, "Storyboard should state WEAK=2"
    assert "REJECT=674" in text, "Storyboard should state REJECT=674"


def test_pitch_storyboard_no_esm1v_mild_unqualified():
    """The storyboard must not say 'ESM-1v says mild' without qualification."""
    path = REPO / "track2" / "pitch_storyboard.md"
    text = path.read_text()
    assert "ESM-1v says mild" not in text, (
        "Storyboard should not have unqualified 'ESM-1v says mild'"
    )


def test_pitch_storyboard_target_screen_not_leads():
    """The storyboard must distinguish target-screen rows from final therapeutic leads."""
    path = REPO / "track2" / "pitch_storyboard.md"
    text = path.read_text().lower()
    assert "target-screen rows" in text or "target screen rows" in text, (
        "Storyboard should clarify 32 rows are target-screen rows, not final leads"
    )
