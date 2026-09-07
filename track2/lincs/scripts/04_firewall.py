#!/usr/bin/env python3
"""
LINCS L2S2 + L1000CDS2 false-rescue firewall and candidate ranking.

Reads all *_l2s2_consensus.csv and *_l1000cds2.csv outputs, aggregates
by drug across signatures, maps to the Track 2 candidate list /
ChEMBL axis-approved list, applies safety/mechanism filters, and
produces a combined L2S2-first ranking.
"""

from __future__ import annotations

import argparse
import csv
import math
import re
import sys
from pathlib import Path

import pandas as pd


# L1000CDS2 scores range from -1 (mimic) to +1 (reverse).
# Only positive-scoring signatures indicate reversal direction.
L1000CDS2_SCORE_THRESHOLD = 0.0

# The current saved L2S2 data was retrieved with the server's default sort
# (pvalue_up / mimic ascending). Re-queries should use adj_pvalue_down.
L2S2_RETRIEVAL_SORT = "pvalue_up (mimic-sorted, default)"


# -------------------- safety / mechanism keyword sets --------------------

# Specific anti-target keywords (mechanisms that worsen SAC hypomorphism or trigger micronuclei inflammation)
ANTI_TARGET_KEYWORDS = {
    "ttk inhibitor", "mps1 inhibitor", "aurora kinase", "aurora b inhibitor",
    "aurkb inhibitor", "sting agonist", "adu-s100", "ad-s100", "bay-1161909",
    "bay-1217389", "cfi-402257", "barasertib", "gsk-1070916", "plk1 inhibitor",
    "polo-like kinase inhibitor", "cdk1 inhibitor",
}

# Drugs explicitly contraindicated, unsafe, or lacking any pediatric rationale/dosing
PEDIATRIC_SAFETY_FAIL = {
    "perhexiline", "thalidomide", "lenalidomide"
}

CYTOTOXIC_CANCER_KEYWORDS = {
    "hsp90", "geldanamycin", "radicicol", "17-aag", "tanespimycin",
    "proteasome inhibitor", "bortezomib", "carfilzomib", "ixazomib",
    "topoisomerase", "doxorubicin", "etoposide", "irinotecan", "topotecan",
    "tubulin", "microtubule", "paclitaxel", "docetaxel", "vincristine", "vinblastine",
    "alkylating", "cisplatin", "carboplatin", "oxaliplatin", "cyclophosphamide",
    "parp", "olaparib", "niraparib", "rucaparib",
    "anthracycline", "bleomycin", "mitomycin",
    "dna damage", "dna-damage", "dna damaging", "dna-damaging",
    "chaetocin", "staurosporine", "aza-c", "decitabine", "azacitidine",
    "abemaciclib", "ribociclib", "palbociclib",
}

MVA_AXIS_KEYWORDS = {
    "mtor", "mtorc1", "fkbp1a", "autophagy", "hsf1", "hsp", "proteostasis",
    "nrf2", "nfe2l2", "jak", "stat", "il-6", "il6", "il6r", "interleukin 6",
    "readthrough", "ataluren", "ptc124", "4-pba", "phenylbutyrate",
    "sirt", "nad", "senolytic", "rapalog",
}

BROAD_CANCER_KINASE_KEYWORDS = {
    "egfr", "her2", "fgfr", "vegfr", "pdgfr", "c-kit", "ret", "braf",
    "mek", "erk", "mapk", "pi3k", "akt", "cdk", "cyclin dependent kinase",
    "parp", "bcr-abl", "src", "abl1", "abl",
}

GENERIC_STRESS_MARKERS = {
    "hsp", "hsp90", "hsp70", "hsp27", "hspa", "hspb", "hspd", "hspe",
    "hmox1", "hif1a", "jun", "fos", "atf3", "ddit3", "chop",
    "socs", "irf", "stat1", "ifi", "isg", "mx", "oas", "ifit",
    "dnaja", "dnajb", "dnajc",
}


def clean_name(name: str) -> str:
    if pd.isna(name) or not str(name).strip():
        return ""
    s = str(name).lower().strip()
    s = re.sub(r"[\-_/]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\(\d+\)", "", s)
    s = re.sub(r"\b(dihydrochloride|monohydrate|hemihydrate|maleate|citrate|phosphate|sulfate|hcl|hydrochloride|sodium|mesylate)\b", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def parse_signature_name(stem: str, suffix: str) -> tuple[str, int]:
    stem = stem.replace(suffix, "")
    m = re.search(r"_(\d+)$", stem)
    if m:
        size = int(m.group(1))
        signature = stem[: stem.rfind("_")]
    else:
        size = 0
        signature = stem
    return signature, size


def load_l1000cds2(results_dir: Path) -> pd.DataFrame:
    rows = []
    for p in sorted(results_dir.glob("*_l1000cds2.csv")):
        if p.stat().st_size < 50:
            continue
        try:
            df = pd.read_csv(p)
        except Exception as e:
            print(f"Warning: could not read {p}: {e}", file=sys.stderr)
            continue
        if df.empty or "drug" not in df.columns:
            continue
        signature, size = parse_signature_name(p.stem, "_l1000cds2")
        df["signature"] = signature
        df["size"] = size
        df["drug_clean"] = df["drug"].apply(clean_name)
        df = df[df["drug_clean"] != ""]
        df = df[~df["drug_clean"].str.contains(r"^-?\d+$", regex=True, na=False)]
        rows.append(df)
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


def load_l2s2(results_dir: Path) -> pd.DataFrame:
    rows = []
    for p in sorted(results_dir.glob("*_l2s2_consensus.csv")):
        if p.stat().st_size < 50:
            continue
        try:
            df = pd.read_csv(p)
        except Exception as e:
            print(f"Warning: could not read {p}: {e}", file=sys.stderr)
            continue
        if df.empty or "drug" not in df.columns:
            continue
        signature, size = parse_signature_name(p.stem, "_l2s2_consensus")
        df["signature"] = signature
        df["size"] = size
        df["drug_clean"] = df["drug"].apply(clean_name)
        df = df[df["drug_clean"] != ""]
        rows.append(df)
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


def load_approved_names(chembl_path: Path) -> set[str]:
    if not chembl_path.exists():
        return set()
    df = pd.read_csv(chembl_path)
    names = set()
    for c in ("pref_name", "drug_name", "molecule_chembl_id"):
        if c in df.columns:
            names.update(df[c].dropna().astype(str).apply(clean_name).tolist())
    return names


def load_signature_composition(results_dir: Path) -> dict[str, dict]:
    """Load signature_composition.csv from the results directory.

    Returns a dict keyed by '{signature}_{size}' with FDR/nominal gene counts
    and a has_nominal_genes flag.
    """
    comp_path = results_dir.parent / "signature_composition.csv"
    if not comp_path.exists():
        return {}
    out: dict[str, dict] = {}
    with comp_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = f"{row['signature']}_{row['size']}"
            out[key] = {
                "up_fdr": int(row["up_fdr"]),
                "up_nominal": int(row["up_nominal"]),
                "down_fdr": int(row["down_fdr"]),
                "down_nominal": int(row["down_nominal"]),
                "has_nominal_genes": row["has_nominal_genes"].lower() == "true",
            }
    return out


def build_drug_lookup(candidates_path: Path, chembl_axis_path: Path | None) -> dict[str, dict]:
    lookup: dict[str, dict] = {}

    cand = pd.read_csv(candidates_path)
    for _, r in cand.iterrows():
        base = clean_name(r["drug"])
        if not base:
            continue
        entry = {
            "drug": r["drug"],
            "tier": str(r.get("tier", "")),
            "target_axis": str(r.get("target_axis", "")),
            "mechanism": str(r.get("mechanism", "")),
            "evidence_level": str(r.get("evidence_level", "")),
            "regulatory_status": str(r.get("regulatory_status", "")),
            "approved_jurisdiction": str(r.get("approved_jurisdiction", "")),
            "pediatric_indication": str(r.get("pediatric_indication", "")),
            "lincs_eligible": str(r.get("lincs_eligible", "false")).lower() == "true",
            "source": "track2_candidates",
        }
        lookup[base] = entry
        for token in base.replace(",", " ").replace("(", " ").replace(")", " ").split():
            if len(token) > 3 and token not in ("maleate", "sodium", "hcl"):
                lookup.setdefault(token, entry)

    if chembl_axis_path and chembl_axis_path.exists():
        chem = pd.read_csv(chembl_axis_path)
        for _, r in chem.iterrows():
            base = clean_name(r.get("drug_name"))
            if not base or base in lookup:
                continue
            entry = {
                "drug": r["drug_name"],
                "tier": "",
                "target_axis": str(r.get("mechanism_of_action", "")),
                "mechanism": str(r.get("mechanism_of_action", "")),
                "evidence_level": "ChEMBL axis max_phase=4",
                "regulatory_status": "APPROVED_MEDICATION",
                "approved_jurisdiction": "",
                "pediatric_indication": "",
                "lincs_eligible": True,
                "source": "chembl_axis_approved",
            }
            lookup[base] = entry

    return lookup


def match_drug(drug_clean: str, lookup: dict) -> dict | None:
    if drug_clean in lookup:
        return lookup[drug_clean]
    for name, meta in lookup.items():
        if len(name.split()) <= 2:
            if drug_clean == name or drug_clean.startswith(name + " ") or drug_clean.endswith(" " + name):
                return meta
    tokens = set(drug_clean.split())
    best = None
    best_score = 0
    for name, meta in lookup.items():
        name_toks = set(name.split())
        if name_toks and name_toks.issubset(tokens):
            if len(name_toks) > best_score:
                best = meta
                best_score = len(name_toks)
    return best


def label_mechanism(mechanism: str, target_axis: str, drug: str, meta: dict | None) -> tuple[str, list[str]]:
    text = " ".join([mechanism, target_axis, drug]).lower()
    tags = []

    # Check if specifically marked as anti-target
    if meta and meta.get("regulatory_status") == "ANTI_TARGET":
        tags.append("anti_target")
    elif any(k in text for k in ANTI_TARGET_KEYWORDS):
        tags.append("anti_target")

    if any(k in text for k in CYTOTOXIC_CANCER_KEYWORDS):
        tags.append("cytotoxic_cancer")

    is_whitelisted = meta is not None and meta.get("source") == "track2_candidates"
    if not is_whitelisted:
        if any(k in text for k in BROAD_CANCER_KINASE_KEYWORDS):
            tags.append("broad_cancer_kinase")
    else:
        if any(k in text for k in BROAD_CANCER_KINASE_KEYWORDS):
            if not any(k in text for k in MVA_AXIS_KEYWORDS):
                tags.append("broad_cancer_kinase")

    if not tags:
        tags.append("mechanism_ok")
    return "; ".join(tags), tags


def false_rescue_flag(overlap: str) -> bool:
    if not isinstance(overlap, str):
        return False
    genes = {g.strip().lower() for g in overlap.split(",") if g.strip()}
    if not genes:
        return False
    stress = {g for g in genes if any(m in g for m in GENERIC_STRESS_MARKERS)}
    return (len(stress) / len(genes)) > 0.25


def safe_neglog10(p: float) -> float:
    if pd.isna(p) or p <= 0:
        return 0.0
    return -math.log10(p)


def aggregate_l1000cds2(df: pd.DataFrame, score_threshold: float = L1000CDS2_SCORE_THRESHOLD) -> dict[str, dict]:
    """Aggregate L1000CDS2 results.

    Only signatures with score > score_threshold (i.e., positive/reversal
    direction) count toward l1k_n_signature and n_engines. L1000CDS2 scores
    range from -1 (mimic) to +1 (reverse); without a threshold, every returned
    row counts regardless of direction, inflating the engine count.
    """
    out: dict[str, dict] = {}
    for drug_clean, g in df.groupby("drug_clean"):
        up_overlaps = g["up_dn_overlap"].dropna().astype(str).tolist()
        dn_overlaps = g["dn_up_overlap"].dropna().astype(str).tolist()
        all_overlap = ",".join(up_overlaps + dn_overlaps)
        # Filter to positive-scoring (reversal) signatures
        g_pos = g[g["score"].notna() & (g["score"] > score_threshold)]
        out[drug_clean] = {
            "l1k_n_total": len(g),
            "l1k_n_signature": g_pos["signature"].nunique(),
            "l1k_signatures": sorted(g_pos["signature"].unique().tolist()),
            "l1k_mean_score": g["score"].mean(),
            "l1k_max_score": g["score"].max(),
            "l1k_min_score": g["score"].min(),
            "l1k_score_std": g["score"].std() if len(g) > 1 else 0.0,
            "l1k_cell_lines": sorted(g["cell_line"].dropna().unique().tolist()),
            "l1k_false_rescue": false_rescue_flag(all_overlap),
        }
    return out


def aggregate_l2s2(df: pd.DataFrame, adj_pvalue_thr: float = 0.05, pvalue_thr: float = 0.05) -> dict[str, dict]:
    """Aggregate L2S2 consensus results, gating rescue/repurposing candidates on
    directional reverse-pair enrichment (adj_pvalue_down / pvalue_down).

    L2S2 semantics (from the pairedEnrich GraphQL schema and consensus computation):
    - genesUp / genesDown are the disease signature.
    - pvalue_up / adj_pvalue_up test whether the drug MIMICS the disease.
    - pvalue_down / adj_pvalue_down test whether the drug REVERSES the disease.
    - pvalue / adj_pvalue are non-directional (drug over-represented among
      significant pair results).
    For repurposing we therefore require a significant reverse (rescue) signal.
    """
    out: dict[str, dict] = {}
    for drug_clean, g in df.groupby("drug_clean"):
        g = g.copy()
        # Rescue direction is the biologically relevant p-value for ranking
        g["neglog10_p"] = g["pvalue_down"].apply(safe_neglog10)
        g["neglog10_p_up"] = g["pvalue_up"].apply(safe_neglog10)
        g["neglog10_p_general"] = g["pvalue"].apply(safe_neglog10)

        # For rescue/repurposing we need drugs whose perturbation REVERSES the disease signature
        sig_fdr_reverse = g[g["adj_pvalue_down"] <= adj_pvalue_thr]
        sig_nom_reverse = g[g["pvalue_down"] <= pvalue_thr]
        sig_fdr_mimic = g[g["adj_pvalue_up"] <= adj_pvalue_thr]
        sig_fdr_general = g[g["adj_pvalue"] <= adj_pvalue_thr]

        n_rev = int(sig_fdr_reverse["signature"].nunique())
        n_mim = int(sig_fdr_mimic["signature"].nunique())
        n_gen = int(sig_fdr_general["signature"].nunique())
        if n_rev > 0 and n_mim > 0:
            direction = "MIXED"
        elif n_rev > 0:
            direction = "REVERSE"
        elif n_mim > 0:
            direction = "MIMIC"
        else:
            direction = "NOT_SIGNIFICANT"

        out[drug_clean] = {
            "l2s2_n_total": len(g),
            "l2s2_n_signature": g["signature"].nunique(),
            "l2s2_n_significant": n_rev,
            "l2s2_n_significant_mimic": n_mim,
            "l2s2_n_significant_general": n_gen,
            "l2s2_n_sig_pval": int(sig_nom_reverse["signature"].nunique()),
            "l2s2_signatures": sorted(sig_fdr_reverse["signature"].unique().tolist()) if not sig_fdr_reverse.empty else sorted(sig_nom_reverse["signature"].unique().tolist()),
            "l2s2_mimic_signatures": sorted(sig_fdr_mimic["signature"].unique().tolist()),
            "l2s2_general_signatures": sorted(sig_fdr_general["signature"].unique().tolist()),
            "l2s2_all_signatures": sorted(g["signature"].unique().tolist()),
            "l2s2_mean_neglog10p": g["neglog10_p"].mean(),
            "l2s2_max_neglog10p": g["neglog10_p"].max(),
            "l2s2_min_pvalue": g["pvalue_down"].min(),
            "l2s2_min_adj_pvalue": g["adj_pvalue_down"].min(),
            "l2s2_min_pvalue_general": g["pvalue"].min(),
            "l2s2_min_adj_pvalue_general": g["adj_pvalue"].min(),
            "l2s2_min_pvalue_up": g["pvalue_up"].min(),
            "l2s2_min_adj_pvalue_up": g["adj_pvalue_up"].min(),
            "l2s2_mean_odds_ratio": g["odds_ratio"].mean(),
            "l2s2_max_odds_ratio": g["odds_ratio"].max(),
            "l2s2_approved_any": bool(g["approved"].any()) if "approved" in g.columns else False,
            "l2s2_direction": direction,
        }
    return out


def decide(drug: str, l2s2: dict | None, l1k: dict | None, meta: dict | None) -> dict:
    l2s2_n_sig = l2s2["l2s2_n_significant"] if l2s2 else 0
    l2s2_n_all = l2s2["l2s2_n_signature"] if l2s2 else 0
    l1k_n_sig = l1k["l1k_n_signature"] if l1k else 0
    n_engines = (1 if (l2s2 and l2s2_n_sig > 0) else 0) + (1 if (l1k and l1k_n_sig > 0) else 0)
    n_total_sig = l2s2_n_sig + l1k_n_sig
    l2s2_direction = l2s2["l2s2_direction"] if l2s2 else "NO_LINCS_HIT"

    result = {
        "drug": drug,
        "l2s2_n_total": l2s2["l2s2_n_total"] if l2s2 else 0,
        "l2s2_n_signatures": l2s2_n_all,
        "l2s2_n_significant": l2s2_n_sig,
        "l2s2_n_significant_mimic": l2s2["l2s2_n_significant_mimic"] if l2s2 else 0,
        "l2s2_n_significant_general": l2s2["l2s2_n_significant_general"] if l2s2 else 0,
        "l2s2_signatures": ";".join(l2s2["l2s2_signatures"]) if l2s2 else "",
        "l2s2_mimic_signatures": ";".join(l2s2["l2s2_mimic_signatures"]) if l2s2 else "",
        "l2s2_general_signatures": ";".join(l2s2["l2s2_general_signatures"]) if l2s2 else "",
        "l2s2_n_sig_pval": l2s2["l2s2_n_sig_pval"] if l2s2 else 0,
        "l2s2_min_pvalue": l2s2["l2s2_min_pvalue"] if l2s2 else None,
        "l2s2_min_adj_pvalue": l2s2["l2s2_min_adj_pvalue"] if l2s2 else None,
        "l2s2_min_pvalue_general": l2s2["l2s2_min_pvalue_general"] if l2s2 else None,
        "l2s2_min_adj_pvalue_general": l2s2["l2s2_min_adj_pvalue_general"] if l2s2 else None,
        "l2s2_min_pvalue_up": l2s2["l2s2_min_pvalue_up"] if l2s2 else None,
        "l2s2_min_adj_pvalue_up": l2s2["l2s2_min_adj_pvalue_up"] if l2s2 else None,
        "l2s2_mean_neglog10p": round(l2s2["l2s2_mean_neglog10p"], 3) if l2s2 else None,
        "l2s2_max_neglog10p": round(l2s2["l2s2_max_neglog10p"], 3) if l2s2 else None,
        "l2s2_mean_odds_ratio": round(l2s2["l2s2_mean_odds_ratio"], 3) if l2s2 else None,
        "l2s2_max_odds_ratio": round(l2s2["l2s2_max_odds_ratio"], 3) if l2s2 else None,
        "l2s2_direction": l2s2_direction,
        "l2s2_retrieval_sort": L2S2_RETRIEVAL_SORT,
        "l1k_n_total": l1k["l1k_n_total"] if l1k else 0,
        "l1k_n_signatures": l1k_n_sig,
        "l1k_signatures": ";".join(l1k["l1k_signatures"]) if l1k else "",
        "l1k_mean_score": round(l1k["l1k_mean_score"], 5) if l1k else None,
        "l1k_max_score": round(l1k["l1k_max_score"], 5) if l1k else None,
        "l1k_false_rescue": l1k["l1k_false_rescue"] if l1k else False,
        "n_engines": n_engines,
        "n_total_signatures": n_total_sig,
        "regulatory_status": meta["regulatory_status"] if meta else "UNKNOWN",
        "approved_jurisdiction": meta["approved_jurisdiction"] if meta else "",
        "mechanism": meta["mechanism"] if meta else "",
        "target_axis": meta["target_axis"] if meta else "",
        "candidate_tier": meta["tier"] if meta else "",
        "lincs_eligible": meta["lincs_eligible"] if meta else False,
        "lookup_source": meta["source"] if meta else "none",
    }

    mech_label, mech_tags = label_mechanism(
        result["mechanism"], result["target_axis"], result["drug"], meta
    )
    result["mechanism_flag"] = mech_label

    reasons = []
    status = "ACCEPT"

    if meta is None:
        reasons.append("not_matched_to_candidate_or_axis")
        status = "REJECT"
    elif result["regulatory_status"] in (
        "ANTI_TARGET", "INVESTIGATIONAL", "SUPPLEMENT_FOOD_GRAS", "SUPPLIMENT_FOOD_GRAS"
    ):
        reasons.append(f"regulatory_status={result['regulatory_status']}")
        status = "REJECT"
    elif not result["lincs_eligible"]:
        reasons.append("not_lincs_eligible")
        status = "REJECT"

    if drug in PEDIATRIC_SAFETY_FAIL:
        reasons.append("pediatric_safety_contraindication")
        status = "REJECT"

    if "anti_target" in mech_tags:
        reasons.append("anti_target_mechanism")
        status = "REJECT"
    if "cytotoxic_cancer" in mech_tags:
        reasons.append("cytotoxic_or_cancer_mechanism")
        if status == "ACCEPT":
            status = "REJECT"
    if "broad_cancer_kinase" in mech_tags:
        reasons.append("broad_cancer_kinase_not_MVA_axis")
        if status == "ACCEPT":
            status = "REJECT"

    if l1k and l1k["l1k_false_rescue"]:
        reasons.append("l1000cds2_false_rescue_generic_stress_overlap")
        if status == "ACCEPT":
            status = "REJECT"

    if n_total_sig == 0:
        reasons.append("no_significant_fdr_lincs_signal")
        status = "REJECT"
    elif n_total_sig < 2:
        reasons.append(f"only_{n_total_sig}_signature_total")
        if status == "ACCEPT":
            status = "WEAK"

    # MIXED direction penalty: a drug with both FDR-significant reverse and
    # mimic signatures has inconsistent transcriptomic directionality and
    # cannot be positioned as a primary rescue candidate. This is a data-driven
    # penalty, separate from the tier-based biological downgrade below.
    if l2s2_direction == "MIXED":
        reasons.append("mixed_l2s2_directionality_reverse_and_mimic")
        if status == "ACCEPT":
            status = "WEAK"

    # Tier-based biological downgrade: supportive/adjunct/caution tiers are not
    # positioned as primary rescue/stabilisation leads, even when a LINCS signal
    # is present. They remain WEAK/conditional candidates.
    tier = (meta.get("tier") or "").lower() if meta else ""
    if any(k in tier for k in ("adjunct", "supportive", "caution")):
        if status == "ACCEPT":
            reasons.append("tier_is_supportive_or_adjunct_not_primary_rescue")
            status = "WEAK"

    result["firewall_status"] = status
    result["firewall_reason"] = "; ".join(reasons) if reasons else "passed_all_filters"
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", default="track2/lincs/results/l2s2", type=Path)
    parser.add_argument("--candidates", default="track2/data/track2_candidates.csv", type=Path)
    parser.add_argument("--chembl-axis", default="track2/data/chembl_axis_drugs_approved.csv", type=Path)
    parser.add_argument("--chembl-all", default=None, type=Path)
    parser.add_argument("--pvalue-thr", default=0.05, type=float)
    parser.add_argument("--out-dir", default="track2/lincs/results", type=Path)
    args = parser.parse_args()

    results_dir = args.results_dir
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    l1000 = load_l1000cds2(results_dir)
    l2s2 = load_l2s2(results_dir)
    composition = load_signature_composition(results_dir)
    print(f"Loaded {len(l1000)} L1000CDS2 rows across {l1000['signature'].nunique() if not l1000.empty else 0} signatures; {l1000['drug_clean'].nunique() if not l1000.empty else 0} unique drugs")
    print(f"Loaded {len(l2s2)} L2S2 rows across {l2s2['signature'].nunique() if not l2s2.empty else 0} signatures; {l2s2['drug_clean'].nunique() if not l2s2.empty else 0} unique drugs")
    if composition:
        n_nominal = sum(1 for v in composition.values() if v["has_nominal_genes"])
        print(f"Loaded {len(composition)} signature compositions ({n_nominal} contain nominal genes)")

    lookup = build_drug_lookup(args.candidates, args.chembl_axis)
    print(f"Drug lookup has {len(lookup)} name entries")

    if args.chembl_all:
        approved_all = load_approved_names(args.chembl_all)
    else:
        approved_all = set()
    if approved_all:
        print(f"Loaded {len(approved_all)} ChEMBL all-approved names for labelling")

    l1000_agg = aggregate_l1000cds2(l1000) if not l1000.empty else {}
    l2s2_agg = aggregate_l2s2(l2s2, pvalue_thr=args.pvalue_thr) if not l2s2.empty else {}

    all_drugs = set(l1000_agg.keys()) | set(l2s2_agg.keys())
    summaries = []
    for drug in sorted(all_drugs):
        l2 = l2s2_agg.get(drug)
        l1 = l1000_agg.get(drug)
        meta = match_drug(drug, lookup)
        if meta is None and drug in approved_all:
            meta = {
                "drug": drug,
                "tier": "",
                "target_axis": "",
                "mechanism": "",
                "evidence_level": "ChEMBL max_phase=4 (not in Track 2 axis)",
                "regulatory_status": "APPROVED_MEDICATION",
                "approved_jurisdiction": "",
                "pediatric_indication": "",
                "lincs_eligible": False,
                "source": "chembl_all_approved",
            }
        d = decide(drug, l2, l1, meta)
        d["lincs_drug"] = drug
        # Flag whether any of the drug's L2S2 reverse signatures contain nominal genes
        if l2 and composition:
            sig_keys = [f"{s}_{sz}" for s in l2.get("l2s2_signatures", []) for sz in [l2.get("l2s2_n_total", 0)]]
            # Check all signatures this drug appears in
            drug_sigs = l2.get("l2s2_all_signatures", [])
            has_nominal = any(
                composition.get(f"{s}_{sz}", {}).get("has_nominal_genes", False)
                for s in drug_sigs
                for sz in [100, 150, 250]
                if f"{s}_{sz}" in composition
            )
            d["signature_has_nominal_genes"] = has_nominal
        else:
            d["signature_has_nominal_genes"] = False
        summaries.append(d)

    firewall_df = pd.DataFrame(summaries)

    status_order = {"ACCEPT": 0, "WEAK": 1, "REJECT": 2}
    firewall_df["status_rank"] = firewall_df["firewall_status"].map(status_order)
    # Combined ranking: engines desc, total signatures desc, l2s2 min pvalue asc, l1k mean score desc
    firewall_df["l2s2_min_pvalue_rank"] = firewall_df["l2s2_min_pvalue"].fillna(1.0)
    firewall_df = firewall_df.sort_values(
        by=["status_rank", "n_engines", "n_total_signatures", "l2s2_max_neglog10p", "l1k_mean_score"],
        ascending=[True, False, False, False, False],
    ).drop(columns=["status_rank", "l2s2_min_pvalue_rank"])

    out_firewall = out_dir / "lincs_firewall_decisions.csv"
    firewall_df.to_csv(out_firewall, index=False)
    print(f"Wrote {out_firewall} ({len(firewall_df)} rows)")

    # Candidate-specific summary
    cand = pd.read_csv(args.candidates)
    evidence_rows = []
    for _, r in cand.iterrows():
        base = clean_name(r["drug"])
        hit = firewall_df[firewall_df["lincs_drug"] == base]
        if hit.empty:
            for _, h in firewall_df.iterrows():
                if base in h["lincs_drug"] or h["lincs_drug"] in base:
                    hit = pd.DataFrame([h.to_dict()])
                    break
        if not hit.empty:
            h = hit.iloc[0]
            evidence_rows.append({
                "drug": r["drug"],
                "l2s2_n_signatures": int(h["l2s2_n_significant"]),
                "l2s2_n_significant_mimic": int(h["l2s2_n_significant_mimic"]),
                "l2s2_n_significant_general": int(h["l2s2_n_significant_general"]),
                "l2s2_n_total": int(h["l2s2_n_total"]),
                "l2s2_min_pvalue": h["l2s2_min_pvalue"],
                "l2s2_min_adj_pvalue": h["l2s2_min_adj_pvalue"],
                "l2s2_min_pvalue_general": h["l2s2_min_pvalue_general"],
                "l2s2_min_adj_pvalue_general": h["l2s2_min_adj_pvalue_general"],
                "l2s2_min_pvalue_up": h["l2s2_min_pvalue_up"],
                "l2s2_min_adj_pvalue_up": h["l2s2_min_adj_pvalue_up"],
                "l2s2_mean_neglog10p": h["l2s2_mean_neglog10p"],
                "l2s2_mean_odds_ratio": h["l2s2_mean_odds_ratio"],
                "l1k_n_signatures": int(h["l1k_n_signatures"]),
                "l1k_n_total": int(h["l1k_n_total"]),
                "l1k_mean_score": h["l1k_mean_score"],
                "l1k_max_score": h["l1k_max_score"],
                "n_engines": int(h["n_engines"]),
                "n_total_signatures": int(h["n_total_signatures"]),
                "lincs_firewall_status": h["firewall_status"],
                "lincs_firewall_reason": h["firewall_reason"],
                "lincs_mechanism_flag": h["mechanism_flag"],
                "l2s2_direction": h["l2s2_direction"],
                "l2s2_retrieval_sort": h.get("l2s2_retrieval_sort", ""),
                "signature_has_nominal_genes": bool(h.get("signature_has_nominal_genes", False)),
            })
        else:
            evidence_rows.append({
                "drug": r["drug"],
                "l2s2_n_signatures": 0,
                "l2s2_n_significant_mimic": 0,
                "l2s2_n_significant_general": 0,
                "l2s2_n_total": 0,
                "l2s2_min_pvalue": None,
                "l2s2_min_adj_pvalue": None,
                "l2s2_min_pvalue_general": None,
                "l2s2_min_adj_pvalue_general": None,
                "l2s2_min_pvalue_up": None,
                "l2s2_min_adj_pvalue_up": None,
                "l2s2_mean_neglog10p": None,
                "l2s2_mean_odds_ratio": None,
                "l1k_n_signatures": 0,
                "l1k_n_total": 0,
                "l1k_mean_score": None,
                "l1k_max_score": None,
                "n_engines": 0,
                "n_total_signatures": 0,
                "lincs_firewall_status": "NO_LINCS_HIT",
                "lincs_firewall_reason": "not_found_in_l2s2_or_l1000cds2",
                "lincs_mechanism_flag": "",
                "l2s2_direction": "NO_LINCS_HIT",
                "l2s2_retrieval_sort": "",
                "signature_has_nominal_genes": False,
            })

    evidence_df = pd.DataFrame(evidence_rows)
    # Keep only base columns in cand before merging to avoid duplicate _x/_y suffixes
    base_cols = [
        "rank", "tier", "drug", "target_axis", "mechanism", "evidence_level",
        "evidence_source", "pediatric_status", "risk_notes", "regulatory_status",
        "approved_jurisdiction", "pediatric_indication", "lincs_eligible", "regulatory_evidence_url"
    ]
    cand = cand[[c for c in base_cols if c in cand.columns]]
    cand_merged = cand.merge(evidence_df, on="drug", how="left")
    cand_out = out_dir / "track2_candidates_with_lincs.csv"
    cand_merged.to_csv(cand_out, index=False)
    print(f"Wrote {cand_out}")

    # Ranked list
    ranked = firewall_df[firewall_df["firewall_status"].isin(["ACCEPT", "WEAK"])].copy()
    ranked = ranked.sort_values(
        by=["n_engines", "n_total_signatures", "l2s2_max_neglog10p", "l1k_mean_score"],
        ascending=[False, False, False, False],
    )
    out_ranked = out_dir / "lincs_candidate_ranking.csv"
    ranked.to_csv(out_ranked, index=False)
    print(f"Wrote {out_ranked} ({len(ranked)} rows)")

    # Console summary
    print("\n=== LINCS firewall summary ===")
    print(firewall_df["firewall_status"].value_counts().to_string())
    print("\nTop accepted/re-purposing hits:")
    print(firewall_df[firewall_df["firewall_status"].isin(["ACCEPT", "WEAK"])]
          [["drug", "l2s2_direction", "n_engines", "n_total_signatures", "l2s2_n_significant",
            "l2s2_n_significant_mimic", "l2s2_n_significant_general", "l2s2_min_pvalue",
            "l2s2_min_adj_pvalue", "l2s2_mean_neglog10p", "l1k_n_signatures", "l1k_mean_score",
            "firewall_status", "mechanism_flag"]]
          .head(30).to_string(index=False))


if __name__ == "__main__":
    main()
