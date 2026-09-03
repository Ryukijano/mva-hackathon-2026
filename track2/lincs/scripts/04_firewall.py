#!/usr/bin/env python3
"""
LINCS L1000CDS2 false-rescue firewall and candidate ranking.

Reads all *_l1000cds2.csv outputs, aggregates by drug across signatures,
maps to the Track 2 candidate list / ChEMBL axis-approved list, applies
safety/mechanism filters, and produces ranked outputs.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd


# -------------------- safety / mechanism keyword sets --------------------

ANTI_TARGET_KEYWORDS = {
    "ttk", "mps1", "aurora", "aurkb", "aurora b", "sting", "ad-s100",
    "adu-s100", "plk1", "polo-like kinase 1", "cdk1", "cyclin dependent kinase 1",
    "bub1", "bubr1", "bub1b",
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

# Mechanisms that are relevant to the Track2 hypothesis but still need scrutiny
MVA_AXIS_KEYWORDS = {
    "mtor", "mtorc1", "fkbp1a", "autophagy", "hsf1", "hsp", "proteostasis",
    "nrf2", "nfe2l2", "jak", "stat", "il-6", "il6", "il6r", "interleukin 6",
    "readthrough", "ataluren", "ptc124", "4-pba", "phenylbutyrate",
    "sirt", "nad", "senolytic", "rapalog",
}

# Broad cancer-kinase classes; reject unless the drug is explicitly in Track 2 whitelist
BROAD_CANCER_KINASE_KEYWORDS = {
    "egfr", "her2", "fgfr", "vegfr", "pdgfr", "c-kit", "ret", "braf",
    "mek", "erk", "mapk", "pi3k", "akt", "cdk", "cyclin dependent kinase",
    "parp", "bcr-abl", "src", "abl1", "abl",
}

# Generic stress markers in overlap gene lists that may indicate a non-specific hit
GENERIC_STRESS_MARKERS = {
    "hsp", "hsp90", "hsp70", "hsp27", "hspa", "hspb", "hspd", "hspe",
    "hmox1", "hif1a", "jun", "fos", "atf3", "ddit3", "chop",
    "socs", "irf", "stat1", "ifi", "isg", "mx", "oas", "ifit",
    "dnaja", "dnajb", "dnajc",
}


def clean_name(name: str) -> str:
    """Lower, strip, collapse spaces, remove salt/solvent tokens."""
    if pd.isna(name) or not str(name).strip():
        return ""
    s = str(name).lower().strip()
    s = re.sub(r"[\-_/]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\(\d+\)", "", s)
    s = re.sub(r"\b(dihydrochloride|monohydrate|hemihydrate|maleate|citrate|phosphate|sulfate|hcl|hydrochloride|sodium|mesylate)\b", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def load_l1000cds2(results_dir: Path) -> pd.DataFrame:
    rows = []
    for p in sorted(results_dir.glob("*_l1000cds2.csv")):
        try:
            df = pd.read_csv(p)
        except Exception as e:
            print(f"Warning: could not read {p}: {e}", file=sys.stderr)
            continue
        if df.empty or "drug" not in df.columns:
            continue
        stem = p.stem.replace("_l1000cds2", "")
        m = re.search(r"_(\d+)$", stem)
        if m:
            size = int(m.group(1))
            signature = stem[: stem.rfind("_")]
        else:
            size = 0
            signature = stem
        df["signature"] = signature
        df["size"] = size
        df["drug_clean"] = df["drug"].apply(clean_name)
        df = df[df["drug_clean"] != ""]
        df = df[~df["drug_clean"].str.contains(r"^-?\d+$", regex=True, na=False)]
        rows.append(df)
    if not rows:
        raise FileNotFoundError(f"No *_l1000cds2.csv files found in {results_dir}")
    return pd.concat(rows, ignore_index=True)


def load_approved_names(chembl_path: Path) -> set[str]:
    """Return a set of cleaned approved drug names from a full ChEMBL list (optional)."""
    if not chembl_path.exists():
        return set()
    df = pd.read_csv(chembl_path)
    names = set()
    for c in ("pref_name", "drug_name", "molecule_chembl_id"):
        if c in df.columns:
            names.update(df[c].dropna().astype(str).apply(clean_name).tolist())
    return names


def build_drug_lookup(candidates_path: Path, chembl_axis_path: Path | None) -> dict[str, dict]:
    """
    Build a lookup from cleaned drug name -> metadata row.
    Uses candidate CSV as primary whitelist; ChEMBL axis-approved as secondary.
    """
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
            if not base:
                continue
            if base in lookup:
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
    # exact token-inclusion for short (1-2 word) lookup names
    for name, meta in lookup.items():
        if len(name.split()) <= 2:
            if drug_clean == name or drug_clean.startswith(name + " ") or drug_clean.endswith(" " + name):
                return meta
    # best subset token match
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

    if any(k in text for k in ANTI_TARGET_KEYWORDS):
        tags.append("anti_target")
    if any(k in text for k in CYTOTOXIC_CANCER_KEYWORDS):
        tags.append("cytotoxic_cancer")

    # Track 2 whitelisted candidates are allowed to be in mTOR/JAK/IL-6/Nrf2/HSP/SIRT axes
    is_whitelisted = meta is not None and meta.get("source") == "track2_candidates"
    if not is_whitelisted:
        if any(k in text for k in BROAD_CANCER_KINASE_KEYWORDS):
            tags.append("broad_cancer_kinase")
    else:
        # For whitelisted drugs, only flag if the mechanism is clearly outside the MVA axes
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


def decide(drug: str, hit_summary: dict, meta: dict | None) -> dict:
    n_sig = hit_summary["n_signature"]
    signatures = hit_summary["signatures"]
    cell_lines = hit_summary["cell_lines"]
    up_overlaps = hit_summary["up_overlaps"]
    dn_overlaps = hit_summary["dn_overlaps"]

    result = {
        "drug": drug,
        "n_total": hit_summary["n_total"],
        "n_signatures": n_sig,
        "signatures": ";".join(sorted(signatures)),
        "n_cell_lines": len(cell_lines),
        "cell_lines": ";".join(sorted(cell_lines)),
        "mean_score": round(hit_summary["mean_score"], 5),
        "max_score": round(hit_summary["max_score"], 5),
        "min_score": round(hit_summary["min_score"], 5),
        "score_std": round(hit_summary["score_std"], 5),
        "up_dn_overlap_genes": ",".join(sorted({g.strip() for o in up_overlaps for g in o.split(",") if g.strip()})),
        "dn_up_overlap_genes": ",".join(sorted({g.strip() for o in dn_overlaps for g in o.split(",") if g.strip()})),
        "false_rescue_flag": hit_summary["false_rescue_flag"],
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

    if result["false_rescue_flag"]:
        reasons.append("false_rescue_generic_stress_overlap")
        if status == "ACCEPT":
            status = "REJECT"

    if n_sig < 2:
        reasons.append(f"only_{n_sig}_signature")
        if status == "ACCEPT":
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
    parser.add_argument("--out-dir", default="track2/lincs/results", type=Path)
    args = parser.parse_args()

    results_dir = args.results_dir
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Loading L1000CDS2 results...")
    l1000 = load_l1000cds2(results_dir)
    print(f"Loaded {len(l1000)} rows across {l1000['signature'].nunique()} signatures; {l1000['drug_clean'].nunique()} unique drugs")

    print("Building drug lookup...")
    lookup = build_drug_lookup(args.candidates, args.chembl_axis)
    print(f"Lookup has {len(lookup)} name entries")

    if args.chembl_all:
        approved_all = load_approved_names(args.chembl_all)
    else:
        approved_all = set()
    if approved_all:
        print(f"Loaded {len(approved_all)} additional ChEMBL approved names (for labelling only)")

    # Aggregate
    summaries = []
    for drug_clean, g in l1000.groupby("drug_clean"):
        up_overlaps = g["up_dn_overlap"].dropna().astype(str).tolist()
        dn_overlaps = g["dn_up_overlap"].dropna().astype(str).tolist()
        all_overlap = ",".join(up_overlaps + dn_overlaps)
        s = {
            "n_total": len(g),
            "n_signature": g["signature"].nunique(),
            "signatures": g["signature"].unique().tolist(),
            "n_size": g["size"].nunique(),
            "mean_score": g["score"].mean(),
            "max_score": g["score"].max(),
            "min_score": g["score"].min(),
            "score_std": g["score"].std() if len(g) > 1 else 0.0,
            "cell_lines": g["cell_line"].dropna().unique().tolist(),
            "up_overlaps": up_overlaps,
            "dn_overlaps": dn_overlaps,
            "false_rescue_flag": false_rescue_flag(all_overlap),
        }
        meta = match_drug(drug_clean, lookup)
        if meta is None and drug_clean in approved_all:
            # Label as generic approved, but not lincs_eligible unless whitelisted
            meta = {
                "drug": drug_clean,
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
        d = decide(drug_clean, s, meta)
        d["l1000cds2_drug"] = drug_clean
        summaries.append(d)

    firewall_df = pd.DataFrame(summaries)

    status_order = {"ACCEPT": 0, "WEAK": 1, "REJECT": 2}
    firewall_df["status_rank"] = firewall_df["firewall_status"].map(status_order)
    firewall_df = firewall_df.sort_values(
        by=["status_rank", "n_signatures", "mean_score"], ascending=[True, False, False]
    ).drop(columns=["status_rank"])

    out_firewall = out_dir / "lincs_firewall_decisions.csv"
    firewall_df.to_csv(out_firewall, index=False)
    print(f"Wrote {out_firewall} ({len(firewall_df)} rows)")

    # Candidate-specific summary
    cand = pd.read_csv(args.candidates)
    evidence_rows = []
    for _, r in cand.iterrows():
        base = clean_name(r["drug"])
        hit = firewall_df[firewall_df["l1000cds2_drug"] == base]
        if hit.empty:
            for _, h in firewall_df.iterrows():
                if base in h["l1000cds2_drug"] or h["l1000cds2_drug"] in base:
                    hit = pd.DataFrame([h.to_dict()])
                    break
        if not hit.empty:
            h = hit.iloc[0]
            evidence_rows.append({
                "drug": r["drug"],
                "lincs_n_signatures": int(h["n_signatures"]),
                "lincs_n_total": int(h["n_total"]),
                "lincs_mean_score": round(h["mean_score"], 5),
                "lincs_max_score": round(h["max_score"], 5),
                "lincs_firewall_status": h["firewall_status"],
                "lincs_firewall_reason": h["firewall_reason"],
                "lincs_mechanism_flag": h["mechanism_flag"],
            })
        else:
            evidence_rows.append({
                "drug": r["drug"],
                "lincs_n_signatures": 0,
                "lincs_n_total": 0,
                "lincs_mean_score": None,
                "lincs_max_score": None,
                "lincs_firewall_status": "NO_L1000CDS2_HIT",
                "lincs_firewall_reason": "not_found_in_l1000cds2_top50",
                "lincs_mechanism_flag": "",
            })

    evidence_df = pd.DataFrame(evidence_rows)
    cand_merged = cand.merge(evidence_df, on="drug", how="left")
    cand_out = out_dir / "track2_candidates_with_lincs.csv"
    cand_merged.to_csv(cand_out, index=False)
    print(f"Wrote {cand_out}")

    # Ranked list of accepted/weak hits
    ranked = firewall_df[
        (firewall_df["firewall_status"].isin(["ACCEPT", "WEAK"]))
    ].copy()
    ranked = ranked.sort_values(by=["n_signatures", "mean_score"], ascending=[False, False])
    out_ranked = out_dir / "lincs_candidate_ranking.csv"
    ranked.to_csv(out_ranked, index=False)
    print(f"Wrote {out_ranked} ({len(ranked)} rows)")

    # Console summary
    print("\n=== LINCS firewall summary ===")
    print(firewall_df["firewall_status"].value_counts().to_string())
    print("\nTop accepted/re-purposing hits:")
    print(firewall_df[firewall_df["firewall_status"].isin(["ACCEPT", "WEAK"])]
          [["drug", "n_signatures", "mean_score", "max_score", "firewall_status", "regulatory_status", "mechanism_flag"]]
          .head(20).to_string(index=False))


if __name__ == "__main__":
    main()
