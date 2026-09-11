# /// script
# requires-python = ">=3.10, <3.13"
# dependencies = ["pymol-open-source-whl"]
# ///
"""Render BUBR1 (AF-O60566) variant figures for the MVA hackathon."""
import os, sys
os.environ["PYOPENGL_PLATFORM"] = "osmesa"
import pymol
pymol.pymol_argv = ["pymol", "-cq"]
pymol.finish_launching()
from pymol import cmd

BASE = "/scratch/kcwp264/mva-hackathon-2026/figures"
AF = f"{BASE}/structures/AF-O60566-F1-model_v6.cif"
OUT = f"{BASE}/out"
os.makedirs(OUT, exist_ok=True)

cmd.bg_color("white")
cmd.set("ray_opaque_background", 1)

# ---------- Fig 1: full-length, pLDDT colours, variants marked ----------
cmd.reinitialize()
cmd.load(AF, "bubr1")
assert cmd.count_atoms("all") > 0, "load failed"
cmd.hide("everything")
cmd.show("cartoon")
# pLDDT colouring: b-factor column
cmd.spectrum("b", "blue cyan green yellow orange red", "bubr1", minimum=30, maximum=95)
# variants
for sel, col in [("resi 737", "magenta"), ("resi 1002", "red"), ("resi 1012", "orange")]:
    cmd.show("sticks", sel)
    cmd.color(col, sel)
    cmd.set("stick_radius", 0.5, sel)
    cmd.label(sel + " and name CA", '"%s%s" % (resn,resi)')
cmd.set("label_size", 18)
cmd.set("label_color", "black")
cmd.orient()
cmd.png(f"{OUT}/bubr1_plddt_overview.png", width=1400, height=1000, dpi=200)
cmd.save(f"{OUT}/bubr1_plddt_overview.pse")

# ---------- Fig 2: truncation map — retained vs lost ----------
cmd.reinitialize()
cmd.load(AF, "bubr1")
cmd.hide("everything")
cmd.show("cartoon")
cmd.color("palecyan", "resi 1-736")          # retained
cmd.color("salmon", "resi 737-1050")       # lost to p.Leu737Ter
cmd.show("sticks", "resi 737")
cmd.color("magenta", "resi 737")
cmd.set("stick_radius", 0.55, "resi 737")
cmd.label("resi 737 and name CA", '"p.Leu737Ter"')
cmd.set("label_size", 20)
cmd.set("label_color", "black")
cmd.orient()
cmd.png(f"{OUT}/bubr1_L737Ter_truncation.png", width=1400, height=1000, dpi=200)
cmd.save(f"{OUT}/bubr1_L737Ter_truncation.pse")

# ---------- Fig 3: C-lobe zoom — N1002K vs L1012P ----------
cmd.reinitialize()
cmd.load(AF, "bubr1")
cmd.hide("everything")
cmd.show("cartoon", "resi 940-1050")
cmd.color("grey80", "resi 940-1050")
for sel, col, tag in [("resi 1002", "red", "p.Asn1002Lys (our variant)"),
                      ("resi 1012", "orange", "p.Leu1012Pro (known MVA1)")]:
    cmd.show("sticks", sel)
    cmd.color(col, sel)
    cmd.set("stick_radius", 0.6, sel)
    cmd.label(sel + " and name CA", '"%s"' % tag)
cmd.set("label_size", 18)
cmd.set("label_color", "black")
cmd.zoom("resi 980-1040", buffer=8)
cmd.png(f"{OUT}/bubr1_clobe_N1002_L1012.png", width=1400, height=1000, dpi=200)
cmd.save(f"{OUT}/bubr1_clobe_N1002_L1012.pse")

cmd.quit()
print("done: overview, truncation, clobe")
