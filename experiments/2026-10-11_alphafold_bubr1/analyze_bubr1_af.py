#!/usr/bin/env python3
"""pLDDT + CA-neighbourhood analysis of AlphaFold DB model AF-O60566-F1 (BUBR1, v6).

Protein-level only. No genome/VCF/FASTQ content is read or sent anywhere.
Inputs : AF-O60566-F1-model_v6.pdb (AlphaFold DB, public), api.json (AF API metadata)
Outputs: plddt_per_residue.csv, region_summary.txt (printed to stdout as well)
"""
import json
import os
import urllib.request

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PDB = os.path.join(HERE, "AF-O60566-F1-model_v6.pdb")
API = os.path.join(HERE, "api.json")
PAE_JSON = os.path.join(HERE, "..", "..", "figures", "structures", "AF-O60566-F1-predicted_aligned_error_v6.json")
AM_CSV = os.path.join(HERE, "AF-O60566-F1-aa-substitutions.csv")
CSV = os.path.join(HERE, "plddt_per_residue.csv")
AM_SUMMARY_CSV = os.path.join(HERE, "alphamissense_key_residues.csv")
CONTACTS_CSV = os.path.join(HERE, "n1002_l1012_atomic_contacts.csv")
PARTNERS_CSV = os.path.join(HERE, "pathway_partners_af_v6.csv")
SUMMARY = os.path.join(HERE, "region_summary.txt")

# ---- parse CA atoms from PDB (fixed columns) ------------------------------
rows = []
with open(PDB) as fh:
    for line in fh:
        if line.startswith("ATOM") and line[12:16].strip() == "CA":
            rows.append(
                dict(
                    resnum=int(line[22:26]),
                    resname=line[17:20].strip(),
                    x=float(line[30:38]),
                    y=float(line[38:46]),
                    z=float(line[46:54]),
                    plddt=float(line[60:66]),
                )
            )
df = pd.DataFrame(rows).sort_values("resnum").reset_index(drop=True)
assert len(df) == 1050, len(df)
assert list(df.resnum) == list(range(1, 1051))

# one-letter code
three2one = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q",
    "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K",
    "MET": "M", "PHE": "F", "PRO": "P", "SER": "S", "THR": "T", "TRP": "W",
    "TYR": "Y", "VAL": "V",
}
df["aa"] = df.resname.map(three2one)

# ---- neighbour count (CA within 10 A, excluding self) and CA-CA distance ---
xyz = df[["x", "y", "z"]].to_numpy()
d = np.sqrt(((xyz[:, None, :] - xyz[None, :, :]) ** 2).sum(-1))
np.fill_diagonal(d, np.inf)
df["ca_neighbours_10A"] = (d <= 10.0).sum(axis=1)
# per-residue CA-based burial proxy: neighbours within 10 A
# (simple neighbour count as requested; not SASA)

# ---- sequence check of variant positions -----------------------------------
seq = "".join(df.aa)
api = json.load(open(API))[0]
af_seq = api["sequence"]
seq_match = seq == af_seq

# ---- UniProt feature check (public protein annotation) --------------------
uni_feats = []
try:
    req = urllib.request.Request(
        "https://rest.uniprot.org/uniprotkb/O60566.json",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    uj = json.load(urllib.request.urlopen(req, timeout=60))
    for f in uj.get("features", []):
        if f.get("type") in ("Region", "Motif", "Domain", "Disordered region", "Compositional bias", "Repeat", "Domain"):
            loc = f["location"]
            uni_feats.append(
                (f["type"], loc["start"]["value"], loc["end"]["value"], f.get("description", ""))
            )
except Exception as e:  # network optional
    uni_feats = [("UNIPROT_FETCH_FAILED", None, None, str(e))]

# ---- region means -----------------------------------------------------------
def mean_plddt(a, b):
    sub = df[(df.resnum >= a) & (df.resnum <= b)]
    return sub.plddt.mean(), len(sub)

def window(center, half=10):
    a, b = max(1, center - half), min(1050, center + half)
    return a, b

regions = [
    ("residues 1-736 (retained by L737Ter)", 1, 736),
    ("residues 737-1050 (lost by L737Ter)", 737, 1050),
    ("D-box 224-232", 224, 232),
    ("KNL1-binding region 152-185", 152, 185),
    ("disordered 368-393 (as given)", 368, 393),
    ("disordered 456-480 (as given)", 456, 480),
    ("window +/-10 around 737 (727-747)", *window(737)),
    ("window +/-10 around 1002 (992-1012)", *window(1002)),
    ("window +/-10 around 1012 (1002-1022)", *window(1012)),
]
lines = []
lines.append("AlphaFold DB model: %s  version: AlphaFold Monomer v2.0 pipeline, model_v%d" % (api["modelEntityId"], api["latestVersion"]))
lines.append("model created: %s  global mean pLDDT (API): %s" % (api["modelCreatedDate"], api["globalMetricValue"]))
lines.append("sequence identical to AF API sequence: %s  (length %d)" % (seq_match, len(seq)))
lines.append("")
lines.append("Residue identity checks:")
for pos in (737, 1002, 1012):
    lines.append("  %d = %s (pLDDT %.2f, CA neighbours<=10A %d)" % (
        pos, df.loc[pos - 1, "aa"], df.loc[pos - 1, "plddt"], df.loc[pos - 1, "ca_neighbours_10A"]))
lines.append("")
lines.append("Mean pLDDT by region (n residues):")
for name, a, b in regions:
    m, n = mean_plddt(a, b)
    lines.append("  %-42s %7.2f  (n=%d)" % (name, m, n))
lines.append("")
lines.append("Fraction of residues with pLDDT>70 in 1-736: %.3f" % ((df[df.resnum <= 736].plddt > 70).mean()))
lines.append("Fraction of residues with pLDDT>70 in 737-1050: %.3f" % ((df[df.resnum >= 737].plddt > 70).mean()))
lines.append("")
lines.append("Solvent exposure proxy (CA neighbours within 10 A; higher = more buried):")
for pos in (1002, 1012):
    r = df.loc[pos - 1]
    lines.append("  residue %d %s: pLDDT %.2f, CA neighbours<=10A = %d, mean neighbours of all residues = %.1f" % (
        pos, r.aa, r.plddt, r.ca_neighbours_10A, df.ca_neighbours_10A.mean()))
dist = d[1001, 1011]
lines.append("")
lines.append("CA-CA distance 1002-1012: %.2f A -> within 10 A: %s" % (dist, dist <= 10.0))

# ---- PAE matrix analysis ----------------------------------------------------
if os.path.exists(PAE_JSON):
    pae_raw = json.load(open(PAE_JSON))
    pae_mat = np.array(pae_raw[0]["predicted_aligned_error"], dtype=float)
    lines.append("")
    lines.append("PAE matrix analysis (1050x1050, A):")
    lines.append("  Global mean PAE: %.2f A" % pae_mat.mean())
    lines.append("  Intra-domain TPR (62-226) mean PAE: %.2f A" % pae_mat[61:226, 61:226].mean())
    lines.append("  Intra-domain C-term lost (737-1050) mean PAE: %.2f A" % pae_mat[736:1050, 736:1050].mean())
    lines.append("  Intra-domain pseudokinase (766-1050) mean PAE: %.2f A" % pae_mat[765:1050, 765:1050].mean())
    lines.append("  Cross-domain (1-736 -> 737-1050) mean PAE: %.2f A (reverse %.2f A)" % (
        pae_mat[:736, 736:].mean(), pae_mat[736:, :736].mean()))
    for r1, r2 in [(1002, 1012), (814, 1002), (814, 1012), (737, 1002), (668, 737)]:
        lines.append("  Pair (%d, %d): PAE(%d->%d)=%.1f A, PAE(%d->%d)=%.1f A, CA-CA=%.2f A" % (
            r1, r2, r1, r2, pae_mat[r1 - 1, r2 - 1], r2, r1, pae_mat[r2 - 1, r1 - 1], d[r1 - 1, r2 - 1]))

# ---- All-atom contact check for N1002 and L1012 -----------------------------
atom_rows = []
with open(PDB) as fh:
    for line in fh:
        if line.startswith("ATOM"):
            atom_rows.append(dict(
                resnum=int(line[22:26]),
                resname=line[17:20].strip(),
                atom=line[12:16].strip(),
                x=float(line[30:38]),
                y=float(line[38:46]),
                z=float(line[46:54]),
            ))
adf = pd.DataFrame(atom_rows)
adf = adf[~adf.atom.str.startswith("H")].reset_index(drop=True)

contact_records = []
for target_res in (737, 814, 1002, 1004, 1012):
    sub_t = adf[adf.resnum == target_res]
    sub_o = adf[(adf.resnum != target_res) & (adf.resnum.sub(target_res).abs() > 1)]
    tx = sub_t[["x", "y", "z"]].to_numpy()
    ox = sub_o[["x", "y", "z"]].to_numpy()
    dist_mat = np.sqrt(((tx[:, None, :] - ox[None, :, :]) ** 2).sum(-1))
    ti, oi = np.where(dist_mat <= 4.0)
    for i_idx, j_idx in zip(ti, oi):
        t_row = sub_t.iloc[i_idx]
        o_row = sub_o.iloc[j_idx]
        contact_records.append(dict(
            focus_residue=target_res,
            focus_resname=t_row.resname,
            focus_atom=t_row.atom,
            partner_residue=int(o_row.resnum),
            partner_resname=o_row.resname,
            partner_atom=o_row.atom,
            distance_A=round(float(dist_mat[i_idx, j_idx]), 2),
        ))
cdf = pd.DataFrame(contact_records).sort_values(["focus_residue", "distance_A"])
cdf.to_csv(CONTACTS_CSV, index=False)

# ---- AlphaMissense proteome-wide substitutions for O60566 -------------------
if os.path.exists(AM_CSV):
    am = pd.read_csv(AM_CSV)
    am["residue"] = am["protein_variant"].str.extract(r"^[A-Z](\d+)[A-Z]$")[0].astype(int)
    am["wt"] = am["protein_variant"].str[0]
    am["mut"] = am["protein_variant"].str[-1]
    am_per_res = am.groupby("residue").agg(
        am_mean=("am_pathogenicity", "mean"),
        am_max=("am_pathogenicity", "max"),
        am_n_lpath=("am_class", lambda s: int((s == "LPath").sum())),
    ).reset_index()
    df = df.merge(am_per_res, left_on="resnum", right_on="residue", how="left")
    key_am = am[am.residue.isin([668, 737, 739, 814, 1002, 1004, 1012])].copy()
    key_am.to_csv(AM_SUMMARY_CSV, index=False)
    lines.append("")
    lines.append("AlphaFold DB AlphaMissense saturation summary (AF-O60566-F1-aa-substitutions.csv):")
    lines.append("  Residues 1-736 mean AM: %.4f (LPath fraction %.3f)" % (
        am[am.residue <= 736].am_pathogenicity.mean(), (am[am.residue <= 736].am_class == "LPath").mean()))
    lines.append("  Residues 737-1050 mean AM: %.4f (LPath fraction %.3f)" % (
        am[am.residue >= 737].am_pathogenicity.mean(), (am[am.residue >= 737].am_class == "LPath").mean()))
    lines.append("  Residues 766-1050 (pseudokinase) mean AM: %.4f (LPath fraction %.3f)" % (
        am[am.residue >= 766].am_pathogenicity.mean(), (am[am.residue >= 766].am_class == "LPath").mean()))
    for pos in (668, 737, 739, 814, 1002, 1004, 1012):
        sub = am[am.residue == pos]
        lines.append("  Pos %4d (%s): mean AM=%.4f, LPath=%2d/19, LBen=%2d/19" % (
            pos, sub.wt.iloc[0], sub.am_pathogenicity.mean(),
            (sub.am_class == "LPath").sum(), (sub.am_class == "LBen").sum()))
    uga_rt = am[(am.residue == 737) & (am.mut.isin(["W", "R", "C"]))]
    lines.append("  UGA near-cognate readthrough products at L737Ter:")
    for _, r in uga_rt.iterrows():
        lines.append("    %s: AM=%.4f (%s)" % (r.protein_variant, r.am_pathogenicity, r.am_class))

lines.append("")
lines.append("UniProt O60566 region/motif/domain/disorder annotations (live REST check):")
for f in uni_feats:
    lines.append("  %s %s-%s %s" % f)

text = "\n".join(lines)
print(text)
open(SUMMARY, "w").write(text + "\n")

cols = ["resnum", "aa", "plddt", "ca_neighbours_10A"]
rename_map = {"resnum": "residue", "aa": "aa", "plddt": "pLDDT", "ca_neighbours_10A": "CA_neighbours_within_10A"}
if "am_mean" in df.columns:
    cols += ["am_mean", "am_n_lpath"]
out = df[cols].rename(columns=rename_map)
out["confident_gt70"] = out.pLDDT > 70
out.to_csv(CSV, index=False)
print("wrote", CSV, SUMMARY)
