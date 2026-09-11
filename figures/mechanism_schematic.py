import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mp
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np

fig, ax = plt.subplots(figsize=(16, 9), dpi=160)
ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.axis("off")

def box(x, y, w, h, text, fc, ec="k", fs=11, tc="k", bold=False, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.12",
                 fc=fc, ec=ec, lw=1.4, ls=ls))
    ax.text(x+w/2, y+h/2, text, ha="center", va="center", fontsize=fs, color=tc,
            weight="bold" if bold else "normal")

def arrow(x1, y1, x2, y2, col="k", lw=2.2, style="-|>", ls="-"):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2), arrowstyle=style, mutation_scale=22,
                 color=col, lw=lw, linestyle=ls))

# Title
ax.text(8, 8.55, "BUB1B p.Leu737Ter + p.Asn1002Lys — mechanism and therapeutic gating",
        ha="center", fontsize=15, weight="bold")

# LEFT: the allele diagram (transcript)
ax.text(2.6, 7.9, "The two alleles", ha="center", fontsize=12, weight="bold")
# transcript line
ax.plot([0.5, 5.0], [7.0, 7.0], color="#666", lw=2)
for x, lab, col in [(1.0, "KEN/ABBA\n(SAC motifs)", "#4c78a8"),
                    (2.2, "TPR·GLEBS\nKARD", "#4c78a8"),
                    (3.3, "pseudokinase", "#4c78a8")]:
    box(x-0.35, 6.75, 0.85, 0.5, lab, col, fs=8, tc="white")
ax.plot([4.0,4.0],[7.35,7.65], color="red", lw=3)
ax.text(4.0, 7.75, "L737Ter\n(UGA stop)", ha="center", fontsize=9, color="red", weight="bold")
ax.plot([4.55,4.55],[7.35,7.65], color="orange", lw=3)
ax.text(4.55, 7.75, "N1002K", ha="center", fontsize=9, color="orange", weight="bold")
box(0.5, 6.1, 4.5, 0.45, "mRNA: PTC at codon 737, 742 nt upstream of last exon junction",
    "#f0f0f0", fs=9)

# NMD gate (center top)
box(6.0, 6.6, 3.2, 1.0, "NMD GATE\nPTC >50 nt upstream of last EJC\n→ transcript degraded", "#f4a9a9", fs=10, bold=True)
arrow(5.0, 6.95, 6.0, 7.05)
box(10.0, 6.6, 3.0, 1.0, "AMLEXANOX\nPTC readthrough + NMD inhibition\n(FDA-approved topical paste)", "#b8e0b8", fs=9, bold=True)
arrow(9.2, 7.05, 10.0, 7.1)
box(13.6, 6.6, 2.2, 1.0, "→ full-length\nBUBR1 rescue?", "#dfeaf6", fs=10)
arrow(13.0, 7.1, 13.6, 7.1)

# MIDDLE: cascade of pathology
ax.text(8, 5.6, "Weak SAC → mosaic aneuploidy → downstream pathology", ha="center", fontsize=12, weight="bold")
cascade = [
    (0.7,  "weak SAC\n(BUBR1 ~11%)", "#dfeaf6"),
    (3.3,  "mosaic\naneuploidy", "#f6d9a8"),
    (5.9,  "proteotoxic +\nlysosomal stress", "#f4c4c4"),
    (8.5,  "ROS /\nmicronuclei", "#f4c4c4"),
    (11.1, "cGAS–STING\nIFN / IL-6", "#f4c4c4"),
]
for i,(x,t,c) in enumerate(cascade):
    box(x, 4.3, 2.2, 0.9, t, c, fs=9)
    if i < len(cascade)-1:
        arrow(x+2.2, 4.75, cascade[i+1][0], 4.75)

# BOTTOM: therapeutic tiers
ax.text(8, 3.4, "Candidate interventions (evidence tier ↓)", ha="center", fontsize=12, weight="bold")
tiers = [
    (0.6, "Tier 1a — NMD+readthrough", "amlexanox (approved paste)\nataluren (UK-cond.) | ELX-02 (invest.)", "#b8e0b8"),
    (5.1, "Tier 2 — proteostasis", "glycerol phenylbutyrate (Ravicti)\narimoclomol (FDA, NPC)", "#cfe3f4"),
    (9.6, "Tier 2c — autophagy", "metformin / rilmenidine (approved)\n(trehalose/spermidine = supplements)", "#cfe3f4"),
    (14.1,"Tier 3 — gated", "JAK/IL-6 only if IFN/IL-6 signature", "#f4e3c1"),
]
for x, head, body, c in tiers:
    box(x, 1.7, 4.0, 1.2, head, c, fs=10, bold=True)
    ax.text(x+2.0, 1.95, body, ha="center", va="center", fontsize=8)
    # connector to pathology
    arrow(x+2.0, 2.9, x+2.0, 4.3, col="#888", lw=1.3, style="-")

# anti-targets
box(0.6, 0.3, 6.0, 0.9, "ANTI-TARGETS (excluded): TTK/MPS1 inhibitors, Aurora B inhibitors,\nSTING agonists — would worsen missegregation / fuel cGAS–STING", "#f4a9a9", fs=9)
box(7.0, 0.3, 8.8, 0.9, "Safety gates: micronucleus/missegregation assays · oncology surveillance ·\npaediatric feasibility · biomarker-gated immunomodulation · NMD-first (transcript rescue before readthrough)", "#eeeeee", fs=9)

plt.tight_layout()
plt.savefig("/tmp/mva_figs/out/mechanism_schematic.png", dpi=160, bbox_inches="tight", facecolor="white")
print("saved")
