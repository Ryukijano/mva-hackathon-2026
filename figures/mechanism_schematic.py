import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

fig, ax = plt.subplots(figsize=(16, 9.6), dpi=160)
ax.set_xlim(0, 16); ax.set_ylim(0, 9.6); ax.axis("off")

def box(x, y, w, h, text, fc, ec="k", fs=11, tc="k", bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.12",
                 fc=fc, ec=ec, lw=1.4))
    ax.text(x+w/2, y+h/2, text, ha="center", va="center", fontsize=fs, color=tc,
            weight="bold" if bold else "normal")

def arrow(x1, y1, x2, y2, col="k", lw=2.2, style="-|>", ls="-"):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2), arrowstyle=style, mutation_scale=22,
                 color=col, lw=lw, linestyle=ls))

ax.text(8, 9.25, "BUB1B p.Leu737Ter + p.Asn1002Lys — mechanism and therapeutic gating",
        ha="center", fontsize=15, weight="bold")

# LEFT: the allele diagram
ax.text(2.75, 8.55, "The two alleles", ha="center", fontsize=12, weight="bold")
ax.plot([0.5, 5.2], [7.35, 7.35], color="#666", lw=2)
for x, lab in [(1.0, "KEN/ABBA\n(SAC motifs)"), (2.35, "TPR·GLEBS\nKARD"), (3.7, "pseudokinase")]:
    box(x-0.42, 7.1, 0.9, 0.55, lab, "#4c78a8", fs=8, tc="white")
# variant markers — separated labels
ax.plot([4.45,4.45],[7.62,7.95], color="red", lw=3)
ax.annotate("L737Ter\n(UGA stop)", xy=(4.45,7.62), xytext=(3.6,8.15), fontsize=9,
            color="red", weight="bold", ha="center",
            arrowprops=dict(arrowstyle="-", color="red", lw=1))
ax.plot([4.95,4.95],[7.62,7.95], color="orange", lw=3)
ax.annotate("N1002K", xy=(4.95,7.62), xytext=(5.35,8.15), fontsize=9,
            color="darkorange", weight="bold", ha="center",
            arrowprops=dict(arrowstyle="-", color="orange", lw=1))
box(0.5, 6.35, 4.7, 0.45, "mRNA: PTC at codon 737, 742 nt upstream of last exon junction",
    "#f0f0f0", fs=9)

# NMD gate
box(6.1, 6.75, 3.2, 1.05, "NMD GATE\nPTC >50 nt upstream of last EJC\n→ transcript degraded", "#f4a9a9", fs=10, bold=True)
arrow(5.2, 7.35, 6.1, 7.25)
box(10.1, 6.75, 3.0, 1.05, "AMLEXANOX\nPTC readthrough + NMD inhibition\n(FDA-approved topical paste)", "#b8e0b8", fs=9, bold=True)
arrow(9.3, 7.25, 10.1, 7.3)
box(13.7, 6.75, 2.1, 1.05, "→ full-length\nBUBR1 rescue?", "#dfeaf6", fs=10)
arrow(13.1, 7.3, 13.7, 7.3)

# MIDDLE: cascade
ax.text(8, 6.0, "Weak SAC → mosaic aneuploidy → downstream pathology", ha="center", fontsize=12, weight="bold")
cascade = [
    (0.7,  "weak SAC\n(BUBR1 ~11%)", "#dfeaf6"),
    (3.3,  "mosaic\naneuploidy", "#f6d9a8"),
    (5.9,  "proteotoxic +\nlysosomal stress", "#f4c4c4"),
    (8.5,  "ROS /\nmicronuclei", "#f4c4c4"),
    (11.1, "cGAS–STING\nIFN / IL-6", "#f4c4c4"),
]
for i,(x,t,c) in enumerate(cascade):
    box(x, 4.5, 2.2, 0.9, t, c, fs=9)
    if i < len(cascade)-1:
        arrow(x+2.2, 4.95, cascade[i+1][0], 4.95)

# BOTTOM: tiers — connectors end at box tops, offset to avoid text
ax.text(8, 3.6, "Candidate interventions (evidence tier ↓)", ha="center", fontsize=12, weight="bold")
tiers = [
    (0.6, "Tier 1a — NMD + readthrough", "amlexanox (approved paste)\nataluren (UK-cond.) | ELX-02 (invest.)", "#b8e0b8", 0.7),
    (5.1, "Tier 2 — proteostasis", "glycerol phenylbutyrate (Ravicti)\narimoclomol (FDA, NPC)", "#cfe3f4", 5.9),
    (9.6, "Tier 2c — autophagy", "metformin / rilmenidine (approved)\n(trehalose/spermidine = supplements)", "#cfe3f4", 11.1),
    (14.1,"Tier 3 — gated", "JAK/IL-6 only if\nIFN/IL-6 signature", "#f4e3c1", 11.1),
]
for x, head, body, c, cx in tiers:
    box(x, 1.85, 4.0 if x<14 else 1.7, 1.35, "", c)
    ax.text(x+(2.0 if x<14 else 0.85), 2.9, head, ha="center", va="center", fontsize=9.5, weight="bold")
    ax.text(x+(2.0 if x<14 else 0.85), 2.25, body, ha="center", va="center", fontsize=8)
    if x < 14:
        arrow(cx, 3.2, cx, 4.5, col="#888", lw=1.3, style="-")

# anti-targets + safety gates
box(0.6, 0.35, 6.6, 1.0, "ANTI-TARGETS (excluded): TTK/MPS1 inhibitors, Aurora B inhibitors,\nSTING agonists — would worsen missegregation / fuel cGAS–STING", "#f4a9a9", fs=9)
box(7.6, 0.35, 8.2, 1.0, "Safety gates: micronucleus/missegregation assays · oncology surveillance ·\npaediatric feasibility · biomarker-gated immunomodulation ·\nNMD-first (transcript rescue before readthrough)", "#eeeeee", fs=9)

plt.tight_layout()
plt.savefig("/tmp/mva_figs/out/mechanism_schematic.png", dpi=160, bbox_inches="tight", facecolor="white")
print("saved")
