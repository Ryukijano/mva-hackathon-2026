import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

BASE = "/scratch/kcwp264/mva-hackathon-2026/figures"
OUT = os.path.join(BASE, "out")
os.makedirs(OUT, exist_ok=True)

fig, ax = plt.subplots(figsize=(16.5, 9.8), dpi=200)
ax.set_xlim(0, 16.5)
ax.set_ylim(0, 9.8)
ax.axis("off")


def box(x, y, w, h, text, fc, ec="#222222", fs=10, tc="#111111", bold=False, lw=1.4):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.06,rounding_size=0.12",
            fc=fc,
            ec=ec,
            lw=lw,
        )
    )
    if text:
        ax.text(
            x + w / 2,
            y + h / 2,
            text,
            ha="center",
            va="center",
            fontsize=fs,
            color=tc,
            weight="bold" if bold else "normal",
            linespacing=1.25,
        )


def arrow(x1, y1, x2, y2, col="#222222", lw=2.0, style="-|>", ls="-"):
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle=style,
            mutation_scale=18,
            color=col,
            lw=lw,
            linestyle=ls,
        )
    )


# Title
ax.text(
    8.25,
    9.42,
    "BUB1B p.Leu737Ter + p.Asn1002Lys (MVA1) — Molecular Mechanism & Evidence-Gated Therapeutic Stack",
    ha="center",
    va="center",
    fontsize=14.5,
    weight="bold",
    color="#111111",
)

# TOP ROW: Left = BUBR1 domain bar with variants properly positioned; Right = NMD gate -> Amlexanox -> Readthrough
ax.text(3.0, 8.82, "1. BUBR1 (O60566, 1,050 aa) & Proband Alleles", ha="center", fontsize=11.5, weight="bold")

# Backbone line for protein
ax.plot([0.4, 5.65], [7.48, 7.48], color="#444444", lw=2.5, zorder=1)
domains = [
    (0.45, 1.15, "TPR / KEN1\n(62–226)\nPDB 3SI5", "#2b5c8f"),
    (1.70, 1.05, "D-box·ABBA\nKEN2 (224–345)\nPDB 6TLJ", "#2b5c8f"),
    (2.85, 1.15, "GLEBS · KARD\n(K668, 665–682)\nPDB 5JJA", "#3878a8"),
    (4.15, 1.45, "Pseudokinase\n(766–1050)\nAF v6 pLDDT 82.1", "#b84b4b"),
]
for dx, dw, dlab, dcol in domains:
    box(dx, 7.12, dw, 0.72, dlab, dcol, ec="#1b365d", fs=7.8, tc="white", bold=True)

# Variant callouts staggered vertically with zero overlap
# K668 (SIRT2 site) at x=3.65 -> label at x=2.25, y=8.28
ax.plot([3.55, 3.55, 2.25], [7.84, 8.05, 8.12], color="#00796b", lw=1.6)
ax.text(2.25, 8.32, "K668 (SIRT2 site)\nPDB 5JJA motif", ha="center", va="center", fontsize=7.8, color="#00695c", weight="bold")

# L737Ter at x=4.12 (boundary before pseudokinase) -> label higher at x=4.05, y=8.55
ax.plot([4.12, 4.12], [7.84, 8.34], color="#c62828", lw=2.4)
ax.text(4.05, 8.55, "p.Leu737Ter (UGA)\nClinVar P/LP · AVI 33.8", ha="center", va="center", fontsize=8.0, color="#b71c1c", weight="bold")

# N1002K at x=5.32 (inside C-lobe) -> label at x=5.45, y=8.18
ax.plot([5.32, 5.32], [7.84, 7.98], color="#e65100", lw=2.4)
ax.text(5.40, 8.18, "p.Asn1002Lys\nAM 0.923 · C-cap", ha="center", va="center", fontsize=8.0, color="#d84315", weight="bold")

box(
    0.45,
    6.32,
    5.15,
    0.64,
    "Exon 17/23 PTC: 747 nt (spliced mRNA) / ~10.9 kb (genomic) upstream of last EJC (LOFTEE PASS)\n"
    "AlphaMissense at codon 737: 0/19 pathogenic; UGA readthrough insertions\n"
    "L737W (0.15), L737R (0.19), and L737C (0.32) are all predicted Likely Benign",
    "#f5f7fa",
    ec="#888888",
    fs=7.3,
)

# Right side of top row: NMD gate -> Amlexanox -> Rescue
box(
    6.05,
    6.82,
    3.25,
    1.15,
    "NMD GATE (Dominant Failure Mode)\nPTC 747 nt upstream of terminal EJC\n→ UPF1 degrades c.2210T>G mRNA\n(Ataluren alone lacks mRNA substrate)",
    "#fadbd8",
    ec="#b03a2e",
    fs=8.8,
    bold=True,
)
arrow(5.65, 7.45, 6.05, 7.40)

box(
    9.75,
    6.82,
    3.35,
    1.15,
    "AMLEXANOX (Tier 1a Lead)\nBlocks UPF1 NMD + drives UGA readthrough\n(FDA-approved 5% oral paste; systemic\ndosing off-label, in vitro 0.2–100 µM)",
    "#d4efdf",
    ec="#1e8449",
    fs=8.8,
    bold=True,
)
arrow(9.30, 7.40, 9.75, 7.40)

box(
    13.55,
    6.82,
    2.60,
    1.15,
    "Full-Length BUBR1 Rescue?\nAssay gate: RT-qPCR mRNA\n+ Western blot ≥10% WT\n(L737W/R/C tolerated)",
    "#ebf5fb",
    ec="#2874a6",
    fs=8.8,
    bold=True,
)
arrow(13.10, 7.40, 13.55, 7.40)

# MIDDLE ROW: Pathophysiological cascade
ax.text(
    8.25,
    5.98,
    "2. Disease Cascade: Hypomorphic SAC → Mosaic Variegated Aneuploidy → Organellar & Inflammatory Stress",
    ha="center",
    fontsize=11.5,
    weight="bold",
)
cascade = [
    (0.45, 2.75, "Weak SAC Latch (PDB 6TLJ)\n1 null + 1 C-lobe hypomorph\n(BubR1 H/H mouse ref: 11%±3%)", "#ebf5fb", "#2874a6"),
    (3.65, 2.65, "Premature Anaphase\nRandom whole-chromosome\ngains/losses (mosaic CIN)", "#fef9e7", "#b7950b"),
    (6.75, 2.85, "Proteotoxic & Lysosomal Load\nStoichiometric imbalance,\nTFEB saturation, ER stress", "#fdedec", "#b03a2e"),
    (10.05, 2.75, "Mitochondrial ROS &\nMicronuclei Rupture\n(Sod2/GTPx-1 axis in fly)", "#fdedec", "#b03a2e"),
    (13.25, 2.90, "cGAS–STING Activation\nType-I IFN / IL-6 loop\n(promotes aneuploid survival)", "#f5eef8", "#6c3483"),
]
for i, (cx, cw, ctext, cfc, cec) in enumerate(cascade):
    box(cx, 4.55, cw, 1.12, ctext, cfc, ec=cec, fs=8.6, bold=(i == 0))
    if i < len(cascade) - 1:
        arrow(cx + cw, 5.11, cascade[i + 1][0], 5.11)

# BOTTOM ROW: Evidence-ranked intervention tiers (all 5 fit cleanly inside 0..16.5)
ax.text(
    8.25,
    4.02,
    "3. Evidence-Gated Track 2 Stack (Market-Approved Medications vs Comparators)",
    ha="center",
    fontsize=11.5,
    weight="bold",
)

tiers = [
    (
        0.45,
        3.05,
        "Tier 1a — UGA Stop Rescue",
        "• Amlexanox (FDA paste; NMD+RT)\n• Ataluren (UK/MHRA cond. only;\n  FDA NDA withdrawn Feb 2026;\n  EMA expired Mar 2025; no NMD)\n• [ELX-02: investigational only]",
        "#d4efdf",
        "#1e8449",
        1.82,
    ),
    (
        3.70,
        2.85,
        "Tier 1b — BUBR1 K668 Axis",
        "• SIRT2 deacetylates K668\n  (North 2014; PDB 5JJA)\n• [NMN / NR: dietary supplements,\n  mechanistic comparators only;\n  +58% lifespan was SIRT2-tg]",
        "#e8f8f5",
        "#117864",
        1.82,
    ),
    (
        6.75,
        3.15,
        "Tier 2a — Approved Proteostasis",
        "• Glycerol phenylbutyrate / Ravicti\n  (FDA/EMA paediatric UCD;\n  sodium-free 4-PBA prodrug)\n• Arimoclomol / Miplyffa (FDA +miglustat;\n  CHMP neg. opinion Jul 2026; HSF1 caveat)",
        "#d6eaf8",
        "#2471a3",
        8.17,
    ),
    (
        10.10,
        3.00,
        "Tier 2b — Approved Autophagy",
        "• Metformin (FDA/EMA ≥10y; AMPK)\n• Rilmenidine (UK/EU; mTOR-indep.)\n• [Trehalose / spermidine: food/supp.]\n• Avoids mTORC1 growth arrest",
        "#d6eaf8",
        "#2471a3",
        8.17,
    ),
    (
        13.30,
        2.85,
        "Tier 3 — Biomarker-Gated",
        "• Baricitinib / Ruxolitinib / Tocilizumab\n• ONLY if elevated ISG / IL-6 / CRP\n• Paired with oncology surveillance\n  (NK/tumour immunosurveillance risk)",
        "#fcf3cf",
        "#b7950b",
        14.70,
    ),
]

for tx, tw, thead, tbody, tfc, tec, target_x in tiers:
    box(tx, 1.85, tw, 1.85, "", tfc, ec=tec, lw=1.6)
    ax.text(tx + tw / 2, 3.45, thead, ha="center", va="center", fontsize=9.2, weight="bold", color="#111111")
    ax.plot([tx + 0.12, tx + tw - 0.12], [3.24, 3.24], color=tec, lw=0.9)
    ax.text(tx + 0.14, 2.52, tbody, ha="left", va="center", fontsize=7.6, color="#111111", linespacing=1.22)
    arrow(tx + tw / 2, 3.70, target_x, 4.55, col=tec, lw=1.4, style="-|>", ls="--")

# FOOTER: Anti-targets & LINCS firewall summary
box(
    0.45,
    0.24,
    7.75,
    1.32,
    "EXCLUDED ANTI-TARGETS & ANEUGEN GATE\n"
    "• TTK/MPS1 & Aurora B inhibitors: ablate SAC / error correction → worsen missegregation\n"
    "• STING agonists: amplify cGAS–STING inflammation · Perhexiline: rejected (paediatric hepatotoxicity)\n"
    "• Sirolimus (rapamycin): induces chromosome malsegregation & CREST+ micronuclei (Bonatti 1998);\n"
    "  BubR1 H/H mouse diet negative (Baker 2013) → gated by patient-cell micronucleus assay",
    "#fadbd8",
    ec="#922b21",
    fs=7.4,
)

box(
    8.45,
    0.24,
    7.70,
    1.32,
    "TRANSCRIPTOMIC FIREWALL & ASSAY-GATED VALIDATION\n"
    "• LINCS L2S2 + L1000CDS2 (676 drugs, reverse FDR < 0.05): 0 ACCEPT / 2 WEAK (MIXED) / 674 REJECT\n"
    "• Pre-registered H1 (ESM-1v N1002K −0.110 vs L1012P −1.801) & H2 (PrimeKG sirolimus 22/37): falsified\n"
    "• Assay gates: (1) RT-qPCR NMD rescue → WB ≥10% full-length BUBR1; (2) K668/BUBR1 half-life;\n"
    "  (3) p62/CHOP aggregate clearance; (4) CREST+ micronucleus / missegregation safety screen",
    "#eaecee",
    ec="#566573",
    fs=7.4,
)

plt.tight_layout()
out_path_1 = os.path.join(OUT, "mechanism_schematic.png")
out_path_2 = os.path.join(BASE, "mechanism_schematic.png")
plt.savefig(out_path_1, dpi=200, bbox_inches="tight", facecolor="white")
plt.savefig(out_path_2, dpi=200, bbox_inches="tight", facecolor="white")
print("Saved:", out_path_1, "and", out_path_2)
