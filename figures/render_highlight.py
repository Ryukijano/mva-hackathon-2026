# /// script
# requires-python = ">=3.10, <3.15"
# dependencies = ["pymol-open-source-whl", "pillow", "matplotlib", "numpy"]
# ///
"""Render the SAC experimental complex structures (PDB 6TLJ, 5JJA, 3SI5) with crisp white backgrounds and bold legends."""
import os
os.environ["PYOPENGL_PLATFORM"] = "osmesa"
import pymol
pymol.pymol_argv = ["pymol", "-cq"]
pymol.finish_launching()
from pymol import cmd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from PIL import Image, ImageOps

BASE = "/scratch/kcwp264/mva-hackathon-2026/figures"
OUT = f"{BASE}/out"
os.makedirs(OUT, exist_ok=True)


def setup_scene():
    cmd.reinitialize()
    cmd.bg_color("white")
    cmd.set("ray_opaque_background", 1)
    cmd.set("antialias", 2)
    cmd.set("orthoscopic", 1)
    cmd.set("cartoon_fancy_helices", 1)
    cmd.set("depth_cue", 0)
    cmd.set("specular", 0.25)


def crop_white(im, pad=24):
    rgb = im.convert("RGB")
    inv = ImageOps.invert(rgb)
    bbox = inv.getbbox()
    if not bbox:
        return rgb
    x0, y0, x1, y1 = bbox
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(rgb.width, x1 + pad)
    y1 = min(rgb.height, y1 + pad)
    return rgb.crop((x0, y0, x1, y1))


def frame_with_legend(raw_png, out_png, title, subtitle, legend_items, footer_note):
    im = crop_white(Image.open(raw_png), pad=28)
    fig = plt.figure(figsize=(12.0, 8.6), dpi=200, facecolor="white")
    ax = fig.add_axes([0.03, 0.15, 0.94, 0.74])
    ax.imshow(im)
    ax.axis("off")
    fig.text(0.5, 0.955, title, ha="center", va="top", fontsize=13.5, fontweight="bold", color="#111111")
    fig.text(0.5, 0.912, subtitle, ha="center", va="top", fontsize=10.0, color="#333333")
    handles = [Patch(facecolor=c, edgecolor="#222222", label=lab) for c, lab in legend_items]
    fig.legend(
        handles=handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.045),
        ncol=min(len(handles), 2),
        frameon=True,
        facecolor="#f8f9fa",
        edgecolor="#bbbbbb",
        prop={"weight": "bold", "size": 9.2},
    )
    fig.text(0.5, 0.012, footer_note, ha="center", va="bottom", fontsize=8.5, color="#444444", style="italic")
    plt.savefig(out_png, dpi=200, facecolor="white")
    plt.close(fig)


# ---------- 1. 6TLJ: APC/C (grey) + MCC highlighted ----------
setup_scene()
cmd.load(f"{BASE}/structures/6TLJ.cif", "mcc")
cmd.hide("everything")
cmd.show("cartoon", "mcc")
cmd.color("grey80", "mcc")
cmd.color("tv_red", "mcc and chain S")          # BUBR1 (resolved res 19-345)
cmd.color("orange", "mcc and chain Q+R")        # CDC20 (2 copies: MCC + APC/C coactivator)
cmd.color("gold", "mcc and chain Z")            # MAD2L1 (closed C-Mad2)
cmd.show("sticks", "mcc and chain S and resi 224-232")  # D-box motif gripping CDC20-R
cmd.orient()
raw_6tlj_hi = "/tmp/apcc_mcc_highlight_raw.png"
cmd.png(raw_6tlj_hi, width=1600, height=1100, dpi=200)
cmd.save(f"{OUT}/apcc_mcc_highlight.pse")
frame_with_legend(
    raw_6tlj_hi,
    f"{OUT}/apcc_mcc_highlight.png",
    "Cryo-EM Structure of Human APC/C Inhibited by the Mitotic Checkpoint Complex (PDB 6TLJ, 3.8 Å)",
    "BUBR1 (Chain S, Red, Resolved Residues 19–345) Threads KEN1/TPR/D-box/ABBA Motifs Across Both CDC20 Propellers",
    [
        ("#d62728", "BUBR1 Chain S (Res 19–345: KEN1, TPR, D-box 224–232, KEN2, ABBA)"),
        ("#ff9800", "Two CDC20 WD40 Propellers (Chains Q & R: Locked by BUBR1)"),
        ("#eab308", "Closed MAD2L1 (Chain Z: Contacts BUBR1 Res 19–38 at 3.6 Å)"),
        ("#bdbdbd", "APC/C E3 Ligase Holoenzyme (APC1–APC16 Scaffold; Anaphase Trigger)"),
    ],
    "Note: BUBR1 residues 346–1050 (including the 766–1050 pseudokinase lost in p.Leu737Ter) are flexibly tethered (PAE ~28 Å) and unmodelled in 6TLJ.",
)

# ---------- 2. 6TLJ: Chain-coloured full complex ----------
setup_scene()
cmd.load(f"{BASE}/structures/6TLJ.cif", "mcc")
cmd.hide("everything")
cmd.show("cartoon", "mcc")
cmd.util.cbc("mcc")
cmd.color("tv_red", "mcc and chain S")
cmd.orient()
raw_6tlj_cbc = "/tmp/apcc_mcc_complex_raw.png"
cmd.png(raw_6tlj_cbc, width=1600, height=1100, dpi=200)
cmd.save(f"{OUT}/apcc_mcc_complex.pse")
frame_with_legend(
    raw_6tlj_cbc,
    f"{OUT}/apcc_mcc_complex.png",
    "Subunit Architecture of the 18-Chain APC/C–MCC Checkpoint Complex (PDB 6TLJ)",
    "Multi-Subunit Stoichiometry Guarded by the Spindle Assembly Checkpoint (72,305 Atoms)",
    [
        ("#d62728", "BUBR1 Effector Core (Chain S, Red)"),
        ("#2ca02c", "APC/C Catalytic & TPR Subunits (APC2/APC10/APC11/APC3/APC6/APC8)"),
        ("#1f77b4", "CDC20 Co-Activators & MAD2L1 Checkpoint Subunits"),
    ],
    "Premature release of this complex causes random whole-chromosome missegregation (mosaic variegated aneuploidy).",
)

# ---------- 3. 5JJA: PP2A-B56gamma (teal) + BubR1 KARD (red, K668 shown) ----------
setup_scene()
cmd.load(f"{BASE}/structures/5JJA.cif", "pp2a")
cmd.hide("everything")
cmd.show("cartoon", "pp2a")
cmd.color("deepteal", "pp2a and chain A+B")     # PP2A-B56gamma HEAT repeats
cmd.color("tv_red", "pp2a and chain C+D")       # BubR1 KARD peptide (668-675)
cmd.show("sticks", "pp2a and chain C+D")
cmd.color("gold", "pp2a and chain C+D and resi 668")
cmd.show("spheres", "pp2a and chain C+D and resi 668 and name CA")
cmd.set("sphere_scale", 1.1, "pp2a and chain C+D and resi 668 and name CA")
cmd.orient()
raw_5jja = "/tmp/pp2a_b56_bubr1_raw.png"
cmd.png(raw_5jja, width=1600, height=1100, dpi=200)
cmd.save(f"{OUT}/pp2a_b56_bubr1.pse")
frame_with_legend(
    raw_5jja,
    f"{OUT}/pp2a_b56_bubr1.png",
    "Crystal Structure of PP2A-B56γ Bound to the BUBR1 KARD LxxIxE Motif (PDB 5JJA, 2.5 Å)",
    "Residues 668–675 (KLDPIIED) Dock Directly into B56γ · Lys668 (Gold) is the SIRT2 Deacetylation Target (Track 2 Prong 1b)",
    [
        ("#00796b", "PP2A-B56γ Subunit (Chains A & B, HEAT Groove)"),
        ("#d62728", "BUBR1 KARD Peptide (Res 668–675; Retained)"),
        ("#eab308", "Lys668 (SIRT2 Deacetylation Switch; AM 13/19 LPath)"),
    ],
    "Although disordered in the uncomplexed monomer (pLDDT 30.2), K668–D675 folds upon binding PP2A-B56γ to stabilise kinetochore-microtubule attachments.",
)

# ---------- 4. 3SI5: BUBR1 TPR + KNL1/Blinkin (kinetochore docking) ----------
setup_scene()
cmd.load(f"{BASE}/structures/3SI5.cif", "kin")
cmd.hide("everything")
cmd.show("cartoon", "kin")
cmd.color("marine", "kin and chain A")
cmd.color("deepsalmon", "kin and chain B")
cmd.color("gold", "kin and chain X+Y")
cmd.show("sticks", "kin and chain X+Y")
cmd.orient()
raw_3si5 = "/tmp/bubr1_kinetochore_raw.png"
cmd.png(raw_3si5, width=1600, height=1100, dpi=200)
cmd.save(f"{OUT}/bubr1_kinetochore_complex.pse")
frame_with_legend(
    raw_3si5,
    f"{OUT}/bubr1_kinetochore_complex.png",
    "Crystal Structure of the BUBR1 N-Terminal TPR Domain Bound to KNL1 / Blinkin (PDB 3SI5, 2.2 Å)",
    "High-Confidence N-Terminal Module (UNP Res 64–215, AF v6 KNL1-Binding Region pLDDT = 94.1) Retained by p.Leu737Ter",
    [
        ("#1d3557", "BUBR1 TPR Domain Copy A (UNP Res 64–215; α-Helical Groove)"),
        ("#e07a5f", "BUBR1 TPR Domain Copy B (Asymmetric Unit Dimer)"),
        ("#eab308", "KNL1 (CASC5) Kinetochore-Docking Peptide (UNP Res 234–252)"),
    ],
    "Demonstrates that the N-terminal kinetochore-recruitment module is structurally intact up to codon 737, provided the mRNA escapes NMD.",
)

cmd.quit()
print("done: all complexes and highlights")
