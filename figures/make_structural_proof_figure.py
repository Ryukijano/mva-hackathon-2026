#!/usr/bin/env python3
"""Generate publication-grade 4-panel AlphaFold v6 + PAE + AlphaMissense + Interactome figure.

Panels:
  (a) BUBR1 (O60566, 1,050 aa) domain map, per-residue AlphaFold v6 pLDDT, and per-residue mean AlphaMissense score.
  (b) AlphaFold v6 1050x1050 Predicted Aligned Error (PAE) matrix showing the 3 rigid domains (D1: 47-211, D2: 406-463, D3: 755-1043),
      PDB 6TLJ resolved region (19-345), and p.Leu737Ter truncation boundary (737-1050).
  (c) Saturation AlphaMissense profiles (all 19 substitutions) at K668 (SIRT2 site), L737 (proband UGA stop; L737W/R/C Likely Benign),
      R814 (MVA1 ref), N1002 (proband missense; 18/19 LPath), N1004 (2 aa away; 0/19 LPath, ClinVar Benign N1004S), and L1012 (MVA1 ref).
  (d) Predictor comparison (AlphaMissense vs ESM-1v 29-1050 and 1-1022 windows) & Track 1/2 pathway interactome AlphaFold v6 confidence.
"""
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Rectangle, Patch
import numpy as np
import pandas as pd

ROOT = "/scratch/kcwp264/mva-hackathon-2026"
AF_DIR = f"{ROOT}/experiments/2026-10-11_alphafold_bubr1"
PAE_JSON = f"{ROOT}/figures/structures/AF-O60566-F1-predicted_aligned_error_v6.json"
OUT_PNG = f"{ROOT}/figures/out/bubr1_alphafold_structural_proof.png"
OUT_PDF = f"{ROOT}/figures/out/bubr1_alphafold_structural_proof.pdf"

plt.rcParams.update({
    "font.family": "sans-serif",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

df_res = pd.read_csv(f"{AF_DIR}/plddt_per_residue.csv")
df_am_key = pd.read_csv(f"{AF_DIR}/alphamissense_key_residues.csv")
df_partners = pd.read_csv(f"{AF_DIR}/pathway_partners_af_v6.csv")
pae_mat = np.array(json.load(open(PAE_JSON))[0]["predicted_aligned_error"], dtype=float)

fig = plt.figure(figsize=(16.8, 11.4), dpi=220)
gs = gridspec.GridSpec(2, 2, width_ratios=[1.32, 1.0], height_ratios=[1.05, 1.0], wspace=0.28, hspace=0.35)

# ==============================================================================
# PANEL (a): Domain architecture + Per-residue pLDDT + Per-residue AlphaMissense
# ==============================================================================
gs_a = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=gs[0, 0], height_ratios=[1.15, 1.0], hspace=0.14)
ax_a1 = fig.add_subplot(gs_a[0])
ax_a2 = fig.add_subplot(gs_a[1], sharex=ax_a1)

x = df_res["residue"].to_numpy()
plddt = df_res["pLDDT"].to_numpy()
am_mean = df_res["am_mean"].rolling(9, center=True, min_periods=1).mean().to_numpy()

# Shaded lost region 737-1050
ax_a1.axvspan(737, 1050, color="#fadbd8", alpha=0.55, label="Lost after p.Leu737Ter (737–1050, mean pLDDT 82.1)")
ax_a2.axvspan(737, 1050, color="#fadbd8", alpha=0.55)

# Domain bars at top of ax_a1 (y = 103..115)
doms = [
    (62, 220, "TPR (62–226, 3SI5)", "#1d3557"),
    (226, 345, "KEN2/ABBA (6TLJ)", "#2b5c8f"),
    (385, 463, "GLEBS", "#457b9d"),
    (665, 682, "KARD", "#eab308"),
    (766, 1050, "C-Terminal Pseudokinase (766–1050)", "#b84b4b"),
]
for d0, d1, dlab, dcol in doms:
    ax_a1.add_patch(Rectangle((d0, 102), d1 - d0, 12, facecolor=dcol, edgecolor="#111111", lw=0.8, clip_on=False))
    if d1 - d0 >= 75:
        ax_a1.text((d0 + d1) / 2, 108, dlab, ha="center", va="center", fontsize=6.7, color="white", fontweight="bold")

ax_a1.plot(x, plddt, color="#1f77b4", lw=1.35, label="Per-residue pLDDT (AF-O60566-F1 v6)")
ax_a1.axhline(70, color="#555555", ls="--", lw=0.9, label="Confident threshold (pLDDT = 70)")

# Key residue markers on pLDDT panel (non-overlapping)
markers = [
    (668, 30.17, "K668 (30.2, PDB 5JJA)", "#00796b", (455, 44)),
    (737, 73.56, "p.Leu737Ter (73.6, UGA)", "#c51b8a", (540, 86)),
    (814, 90.25, "R814H\n(90.3)", "#6c3483", (790, 56)),
    (1002, 91.06, "p.Asn1002Lys\n(91.1)", "#d62728", (875, 58)),
    (1012, 95.31, "L1012P (95.3)", "#e65100", (875, 95)),
]
for rpos, rval, rlab, rcol, (tx, ty) in markers:
    ax_a1.scatter([rpos], [rval], color=rcol, s=36, zorder=5, edgecolor="black", lw=0.6)
    ax_a1.annotate(
        rlab,
        xy=(rpos, rval),
        xytext=(tx, ty),
        fontsize=7.2,
        fontweight="bold",
        color=rcol,
        arrowprops=dict(arrowstyle="->", color=rcol, lw=0.9),
    )

ax_a1.set_ylim(20, 117)
ax_a1.set_xlim(1, 1050)
ax_a1.set_ylabel("AlphaFold v6 pLDDT", fontsize=9.5, fontweight="bold")
ax_a1.set_title("(a) BUBR1 (O60566) Domain Architecture, AlphaFold v6 pLDDT & AlphaMissense Landscape", loc="left", fontsize=11, fontweight="bold", pad=8)
ax_a1.legend(loc="lower left", fontsize=7.6, frameon=True, ncol=2, prop={"weight": "bold", "size": 7.5})
plt.setp(ax_a1.get_xticklabels(), visible=False)

# Bottom subpanel: AlphaMissense per-residue mean + N1002K / L1012P / L737W points
ax_a2.fill_between(x, 0, am_mean, color="#d95f02", alpha=0.25)
ax_a2.plot(x, am_mean, color="#d95f02", lw=1.35, label="9-aa rolling mean AlphaMissense (19,950 substitutions)")
ax_a2.axhline(0.564, color="#b03a2e", ls="--", lw=0.9, label="AlphaMissense Likely Pathogenic cutoff (0.564)")
ax_a2.scatter([1002, 1012, 737, 1004], [0.9229, 0.8720, 0.1503, 0.0477],
              c=["#d62728", "#ff9800", "#1e8449", "#2b5c8f"], s=44, zorder=6, edgecolor="black", lw=0.7)
ax_a2.annotate("N1002K (0.923 LPath)", xy=(1002, 0.9229), xytext=(805, 0.90), fontsize=7.5, fontweight="bold", color="#d62728",
               arrowprops=dict(arrowstyle="->", color="#d62728", lw=0.9))
ax_a2.annotate("L1012P (0.872)", xy=(1012, 0.8720), xytext=(875, 0.72), fontsize=7.5, fontweight="bold", color="#e65100",
               arrowprops=dict(arrowstyle="->", color="#e65100", lw=0.9))
ax_a2.annotate("L737W UGA readthrough (0.150 LBen)", xy=(737, 0.1503), xytext=(455, 0.10), fontsize=7.5, fontweight="bold", color="#1e8449",
               arrowprops=dict(arrowstyle="->", color="#1e8449", lw=0.9))
ax_a2.annotate("N1004S ClinVar Ben (0.048)", xy=(1004, 0.0477), xytext=(785, 0.05), fontsize=7.3, fontweight="bold", color="#2b5c8f",
               arrowprops=dict(arrowstyle="->", color="#2b5c8f", lw=0.9))
ax_a2.set_ylim(0, 1.05)
ax_a2.set_ylabel("AlphaMissense", fontsize=9.5, fontweight="bold")
ax_a2.set_xlabel("BUBR1 (UniProt O60566) Residue Position", fontsize=9.5, fontweight="bold")
ax_a2.legend(loc="upper left", fontsize=7.6, frameon=True, prop={"weight": "bold", "size": 7.5})

# ==============================================================================
# PANEL (b): 1050x1050 PAE Matrix Heatmap
# ==============================================================================
ax_b = fig.add_subplot(gs[0, 1])
ax_b.spines["top"].set_visible(True)
ax_b.spines["right"].set_visible(True)
im_b = ax_b.imshow(pae_mat, cmap="Greens_r", vmin=0, vmax=31.75, origin="upper")
cbar = plt.colorbar(im_b, ax=ax_b, fraction=0.045, pad=0.03)
cbar.set_label("Predicted Aligned Error (Å)", fontsize=9, fontweight="bold")

# Draw rigid domain boxes
for d0, d1, dname, col in [
    (47, 211, "D1: TPR\n(47–211, PAE 7.2 Å)", "#1d3557"),
    (406, 463, "D2: GLEBS", "#00796b"),
    (755, 1043, "D3: Pseudokinase\n(755–1043, PAE 7.7 Å)", "#d62728"),
]:
    ax_b.add_patch(Rectangle((d0, d0), d1 - d0, d1 - d0, fill=False, edgecolor=col, lw=1.8, ls="-"))

# Draw PDB 6TLJ span (19-345) and L737Ter truncation line (737)
ax_b.axhline(737, color="#c51b8a", ls="--", lw=1.3)
ax_b.axvline(737, color="#c51b8a", ls="--", lw=1.3)
ax_b.text(45, 625, "p.Leu737Ter cut (res 737)\nCross-domain PAE = 28–29 Å\n(flexibly tethered C-term)", fontsize=7.4, fontweight="bold", color="#900c3f",
          bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#c51b8a", alpha=0.92))
ax_b.text(45, 935, "D3 Pseudokinase (755–1043)\nIntra-domain PAE = 7.7 Å\nPAE(1002,1012) = 2–3 Å\nCα–Cα(1002,1012) = 12.32 Å", fontsize=7.4, fontweight="bold", color="#b71c1c",
          bbox=dict(boxstyle="round,pad=0.22", fc="white", ec="#d62728", alpha=0.92))
ax_b.text(235, 185, "Resolved in PDB 6TLJ\n(res 19–345 only)", fontsize=7.4, fontweight="bold", color="#1d3557",
          bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#1d3557", alpha=0.92))

ax_b.set_title("(b) AlphaFold v6 PAE Matrix (1,050 × 1,050): 3 Rigid Domains", loc="left", fontsize=11, fontweight="bold", pad=8)
ax_b.set_xlabel("Scored Residue", fontsize=9.5, fontweight="bold")
ax_b.set_ylabel("Aligned Residue", fontsize=9.5, fontweight="bold")

# ==============================================================================
# PANEL (c): Saturation AlphaMissense across all 19 substitutions at key sites
# ==============================================================================
ax_c = fig.add_subplot(gs[1, 0])
sites = [
    (737, "Leu737\n(UGA stop)\n0/19 LPath"),
    (739, "Ala739\n(A739S ref)\n0/19 LPath"),
    (1004, "Asn1004\n(2 aa away)\n0/19 LPath"),
    (814, "Arg814\n(MVA1 R814H)\n10/19 LPath"),
    (668, "Lys668\n(SIRT2 site)\n13/19 LPath"),
    (1012, "Leu1012\n(MVA1 L1012P)\n16/19 LPath"),
    (1002, "Asn1002\n(Proband N1002K)\n18/19 LPath"),
]
rng = np.random.default_rng(42)
ax_c.axhspan(0.564, 1.02, color="#fdedec", alpha=0.45, label="AlphaMissense Likely Pathogenic (>0.564)")
ax_c.axhspan(0.0, 0.34, color="#eafaf1", alpha=0.45, label="AlphaMissense Likely Benign (<0.340)")
ax_c.axhline(0.564, color="#b03a2e", ls="--", lw=1.0)
ax_c.axhline(0.340, color="#1e8449", ls=":", lw=1.0)

for idx, (spos, slabel) in enumerate(sites):
    sub = df_am_key[df_am_key["residue"] == spos]
    vals = sub["am_pathogenicity"].to_numpy()
    jitter = rng.uniform(-0.16, 0.16, size=len(vals))
    cols = ["#d62728" if c == "LPath" else ("#f39c12" if c == "Amb" else "#27ae60") for c in sub["am_class"]]
    ax_c.scatter(np.full_like(vals, idx, dtype=float) + jitter, vals, c=cols, s=34, alpha=0.82, edgecolors="#222222", lw=0.5, zorder=3)
    ax_c.hlines(vals.mean(), idx - 0.26, idx + 0.26, colors="#111111", lw=2.4, zorder=4)

# Highlight specific substitutions of interest
highlights = [
    (0, 0.1503, "L737W (0.150)", "#1e8449", (-0.38, 0.42)),
    (0, 0.1888, "L737R (0.189)", "#1e8449", (0.05, 0.50)),
    (0, 0.3217, "L737C (0.322)\nUGA readthrough", "#1e8449", (-0.30, 0.62)),
    (2, 0.0477, "N1004S (0.048)\nClinVar Benign", "#1d3557", (-0.35, 0.43)),
    (3, 0.2205, "R814H (0.221)", "#6c3483", (-0.30, 0.06)),
    (4, 0.3167, "K668Q (0.317)", "#00796b", (-0.32, 0.14)),
    (5, 0.8720, "L1012P (0.872)", "#d35400", (-0.42, 0.76)),
    (6, 0.9229, "N1002K (0.923)\nProband Allele 2", "#b71c1c", (-0.72, 0.94)),
]
for x_i, y_v, h_lab, h_col, (tx, ty) in highlights:
    ax_c.scatter([x_i], [y_v], color=h_col, s=75, marker="*", zorder=6, edgecolor="black", lw=0.6)
    ax_c.annotate(
        h_lab,
        xy=(x_i, y_v),
        xytext=(x_i + tx, ty),
        fontsize=7.3,
        fontweight="bold",
        color=h_col,
        arrowprops=dict(arrowstyle="->", color=h_col, lw=0.9),
    )

ax_c.set_xticks(range(len(sites)))
ax_c.set_xticklabels([s[1] for s in sites], fontsize=7.3, fontweight="bold")
ax_c.set_ylim(0, 1.04)
ax_c.set_xlim(-0.55, len(sites) - 0.35)
ax_c.set_ylabel("AlphaMissense Pathogenicity (19 AAs / site)", fontsize=9.5, fontweight="bold")
ax_c.set_title("(c) Saturation Mutagenesis: L737 Readthrough Tolerance & N1002 Constraint", loc="left", fontsize=10.4, fontweight="bold", pad=8)
ax_c.legend(loc="lower right", fontsize=7.6, frameon=True, prop={"weight": "bold", "size": 7.5})

# ==============================================================================
# PANEL (d): Pathway Interactome AlphaFold v6 Confidence + ESM-1v Window Check
# ==============================================================================
ax_d = fig.add_subplot(gs[1, 1])
p_df = df_partners.sort_values("global_plddt", ascending=True).reset_index(drop=True)
y_pos = np.arange(len(p_df))
bars = ax_d.barh(
    y_pos,
    p_df["global_plddt"],
    height=0.62,
    color=["#b84b4b" if u == "O60566" else "#2b5c8f" for u in p_df["uniprot"]],
    edgecolor="#111111",
    lw=0.9,
)
ax_d.axvline(70, color="#555555", ls="--", lw=1.0, label="Confident fold threshold (pLDDT = 70)")
for idx, row in p_df.iterrows():
    ax_d.text(
        row["global_plddt"] + 1.2,
        idx,
        f"{row['global_plddt']:.1f}  (PAE {row['mean_pae_A']:.1f} Å · {row['length_aa']} aa)",
        va="center",
        fontsize=7.8,
        fontweight="bold",
        color="#111111",
    )

ax_d.set_yticks(y_pos)
ax_d.set_yticklabels([f"{r.gene_protein}\n({r.uniprot})" for _, r in p_df.iterrows()], fontsize=8.2, fontweight="bold")
ax_d.set_xlim(0, 125)
ax_d.set_xlabel("AlphaFold DB v6 Global Mean pLDDT (with Mean PAE & Length)", fontsize=9.2, fontweight="bold")
ax_d.set_title("(d) Track 1/2 Pathway Interactome (AlphaFold DB API v6)", loc="left", fontsize=11, fontweight="bold", pad=8)

# Inset box showing ESM-1v window concordance (29-1050 vs 1-1022)
inset_txt = (
    "ESM-1v 5-Model Ensemble Window Verification:\n"
    "• Window 29–1050 (canonical): N1002K = −0.110 vs L1012P = −1.801 (gap 1.69 nats; B/LB med −0.161)\n"
    "• Window 1–1022 (fixed 2026-10-11): N1002K = −0.063 vs L1012P = −2.158 (gap 2.10 nats; B/LB med −0.177)\n"
    "→ Both windows falsify H1 (N1002K ≠ L1012P in 1D sequence); AlphaMissense 0.9229 captures 3D C-cap H-bonds."
)
ax_d.text(
    0.02,
    -0.31,
    inset_txt,
    transform=ax_d.transAxes,
    fontsize=7.3,
    fontweight="bold",
    color="#1b2631",
    bbox=dict(boxstyle="round,pad=0.3", fc="#f8f9f9", ec="#566573", lw=1.0),
)

plt.savefig(OUT_PNG, dpi=220, bbox_inches="tight", facecolor="white")
plt.savefig(OUT_PDF, bbox_inches="tight", facecolor="white")
print("Saved:", OUT_PNG, "and", OUT_PDF)
