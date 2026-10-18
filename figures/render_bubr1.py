# /// script
# requires-python = ">=3.10, <3.15"
# dependencies = ["pymol-open-source-whl", "pillow", "matplotlib", "numpy"]
# ///
"""Render BUBR1 (AF-O60566-F1 model_v6) variant figures with publication-grade legends and annotations."""
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
AF = f"{BASE}/structures/AF-O60566-F1-model_v6.cif"
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


# ---------- Fig 1: full-length, pLDDT colours, variants marked ----------
setup_scene()
cmd.load(AF, "bubr1")
assert cmd.count_atoms("all") > 0, "load failed"
cmd.hide("everything")
cmd.show("cartoon")
cmd.spectrum("b", "red_orange_yellow_green_cyan_blue", "bubr1", minimum=30, maximum=95)
for sel, col in [("resi 668", "deepteal"), ("resi 737", "magenta"), ("resi 814", "purple"), ("resi 1002", "tv_red"), ("resi 1012", "orange")]:
    cmd.show("spheres", sel + " and name CA")
    cmd.set("sphere_scale", 1.35, sel + " and name CA")
    cmd.show("sticks", sel)
    cmd.color(col, sel)
    cmd.set("stick_radius", 0.45, sel)
cmd.orient()
raw1 = "/tmp/bubr1_plddt_raw.png"
cmd.png(raw1, width=1600, height=1100, dpi=200)
cmd.save(f"{OUT}/bubr1_plddt_overview.pse")
frame_with_legend(
    raw1,
    f"{OUT}/bubr1_plddt_overview.png",
    "AlphaFold DB v6 Monomer of Human BUBR1 (UniProt O60566, 1,050 aa) — Per-Residue pLDDT & Key Loci",
    "Global mean pLDDT = 63.59 · Retained N-terminal 1–736 mean = 55.74 · Lost C-terminal 737–1050 mean = 82.05 (85.7% > 70)",
    [
        ("#1f77b4", "pLDDT > 90 (Very High: TPR & Pseudokinase)"),
        ("#2ca02c", "pLDDT 70–90 (Confident)"),
        ("#ff7f0e", "pLDDT < 50 (Flexible Inter-Domain Linkers)"),
        ("#d62728", "p.Asn1002Lys (pLDDT 91.1, C-lobe α-helix C-cap)"),
        ("#ff9800", "p.Leu1012Pro (pLDDT 95.3, MVA1 Comparator)"),
        ("#c51b8a", "p.Leu737Ter (pLDDT 73.6, UGA Stop-Gain)"),
    ],
    "Source: AlphaFold DB AF-O60566-F1-model_v6. Monomer structure does not model BUB3/CDC20/KNL1 complexes, phasing, splicing, or NMD.",
)

# ---------- Fig 2: truncation map — retained vs lost ----------
setup_scene()
cmd.load(AF, "bubr1")
cmd.hide("everything")
cmd.show("cartoon")
cmd.color("deepteal", "resi 1-736")
cmd.color("salmon", "resi 737-1050")
cmd.color("marine", "resi 62-226")
cmd.color("gold", "resi 665-682")
for sel, col in [("resi 668", "gold"), ("resi 737", "magenta"), ("resi 1002", "tv_red"), ("resi 1012", "orange")]:
    cmd.show("spheres", sel + " and name CA")
    cmd.set("sphere_scale", 1.4, sel + " and name CA")
    cmd.show("sticks", sel)
    cmd.color(col, sel)
    cmd.set("stick_radius", 0.5, sel)
cmd.orient()
raw2 = "/tmp/bubr1_trunc_raw.png"
cmd.png(raw2, width=1600, height=1100, dpi=200)
cmd.save(f"{OUT}/bubr1_L737Ter_truncation.pse")
frame_with_legend(
    raw2,
    f"{OUT}/bubr1_L737Ter_truncation.png",
    "BUBR1 p.Leu737Ter Truncation Map — Retained N-Terminal Scaffold vs Amputated Pseudokinase Domain",
    "Allele 1 (c.2210T>G, p.Leu737Ter) introduces a UGA stop 747 nt (mRNA) / ~10.9 kb (genomic) upstream of the last EJC (canonical NMD substrate)",
    [
        ("#005f73", "Residues 1–736 Retained (KEN1/2, D-box, ABBA, GLEBS)"),
        ("#1d3557", "Residues 62–226 TPR Kinetochore-Docking Domain (PDB 3SI5)"),
        ("#eab308", "Residues 665–682 KARD + K668 SIRT2 Deacetylation Site (PDB 5JJA)"),
        ("#c51b8a", "p.Leu737Ter Stop Site (UGA; L737W/R/C Readthrough All LBen)"),
        ("#f28482", "Residues 737–1050 Lost (Entire Folded Pseudokinase, pLDDT 82.1)"),
        ("#d62728", "p.Asn1002Lys & p.Leu1012Pro inside C-Lobe (Allele 2 Context)"),
    ],
    "In trans architecture: Allele 1 loses transcript/C-terminal domain via NMD; Allele 2 (p.Asn1002Lys) supplies full-length hypomorphic BUBR1.",
)

# ---------- Fig 3: C-lobe zoom — N1002K H-bond network vs L1012P ----------
setup_scene()
cmd.load(AF, "bubr1")
cmd.hide("everything")
cmd.show("cartoon", "resi 850-1050")
cmd.color("grey85", "resi 850-1050")
cmd.color("lightblue", "resi 990-1001")
cmd.color("wheat", "resi 1008-1020")
cmd.color("palegreen", "resi 976-982")

# Show H-bond/packing partners of N1002
for r in [977, 978, 998, 999, 1004]:
    cmd.show("sticks", f"resi {r}")
    cmd.color("marine", f"resi {r}")
    cmd.set("stick_radius", 0.25, f"resi {r}")

for sel, col in [("resi 1002", "tv_red"), ("resi 1012", "orange")]:
    cmd.show("sticks", sel)
    cmd.color(col, sel)
    cmd.set("stick_radius", 0.55, sel)
    cmd.show("spheres", sel + " and name CA")
    cmd.set("sphere_scale", 0.7, sel + " and name CA")

# Distance dashes: C-alpha 1002 to 1012 (12.32 A) and N1002 H-bonds
cmd.distance("d_ca", "resi 1002 and name CA", "resi 1012 and name CA")
cmd.color("black", "d_ca")
cmd.distance("hb1", "resi 1002 and name OD1", "resi 978 and name N")
cmd.distance("hb2", "resi 1002 and name ND2", "resi 998 and name O")
cmd.distance("hb3", "resi 1002 and name ND2", "resi 1004 and name O")
cmd.color("deepteal", "hb1")
cmd.color("deepteal", "hb2")
cmd.color("deepteal", "hb3")
cmd.hide("labels", "hb1")
cmd.hide("labels", "hb2")
cmd.hide("labels", "hb3")
cmd.set("dash_width", 3.0)
cmd.set("label_size", 22)
cmd.set("label_color", "black")
cmd.orient("resi 975-1022")
cmd.zoom("resi 975-1022", buffer=5)
raw3 = "/tmp/bubr1_clobe_raw.png"
cmd.png(raw3, width=1600, height=1100, dpi=200)
cmd.save(f"{OUT}/bubr1_clobe_N1002_L1012.pse")
frame_with_legend(
    raw3,
    f"{OUT}/bubr1_clobe_N1002_L1012.png",
    "Pseudokinase C-Lobe Atomic Environment: Buried Helix C-Cap p.Asn1002Lys vs Core p.Leu1012Pro",
    "Cα–Cα distance = 12.32 Å (PAE = 2–3 Å) · Asn1002 forms 3 intramolecular H-bonds (Trp978:N 2.83 Å, Val998:O 2.83 Å, Asn1004:O 3.14 Å)",
    [
        ("#d62728", "Asn1002 (Proband N1002K: AM 0.923 LPath, 18/19 LPath at site)"),
        ("#ff9800", "Leu1012 (MVA1 Comparator L1012P: AM 0.872 LPath, ESM-1v −1.801)"),
        ("#90caf9", "α-Helix 990–1001 (C-capped by Asn1002)"),
        ("#ffe0b2", "α-Helix 1008–1020 (Contains Leu1012 Hydrophobic Core)"),
        ("#00796b", "Asn1002 3-H-Bond Staple to Trp978 / Val998 / Asn1004"),
        ("#111111", "12.32 Å Cα–Cα Separation (Same C-Lobe, Non-Contacting)"),
    ],
    "Why AlphaMissense (0.9229) & ESM-1v (−0.110) diverge: N→K is evolutionarily mild in 1D sequence but breaks the 3-bond C-cap & clashes near Arg999 (3.62 Å).",
)

cmd.quit()
print("done: overview, truncation, clobe")
