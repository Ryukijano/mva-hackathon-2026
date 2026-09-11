# /// script
# requires-python = ">=3.10, <3.13"
# dependencies = ["pymol-open-source-whl"]
# ///
import os
os.environ["PYOPENGL_PLATFORM"] = "osmesa"
import pymol
pymol.pymol_argv = ["pymol", "-cq"]
pymol.finish_launching()
from pymol import cmd

BASE = "/scratch/kcwp264/mva-hackathon-2026/figures"
OUT = "/tmp/mva_figs/out"
os.makedirs(OUT, exist_ok=True)
cmd.bg_color("white")
cmd.set("ray_opaque_background", 1)

# ---------- 6TLJ: APC/C (grey) + MCC highlighted (BUBR1=S red, CDC20=Q,R orange, MAD2A=Z yellow) ----------
cmd.reinitialize()
cmd.load(f"{BASE}/structures/6TLJ.cif", "mcc")
cmd.hide("everything")
cmd.show("cartoon", "mcc")
cmd.color("grey75", "mcc")                      # APC/C background
cmd.color("tv_red",    "mcc and chain S")       # BUBR1
cmd.color("orange",    "mcc and chain Q+R")     # CDC20 (checkpoint + substrate copies)
cmd.color("paleyellow","mcc and chain Z")       # MAD2A
cmd.show("sticks", "mcc and chain S and resi 300-320")   # KEN2 region marker
cmd.orient()
cmd.png(f"{OUT}/apcc_mcc_highlight.png", width=1600, height=1100, dpi=200)
cmd.save(f"{OUT}/apcc_mcc_highlight.pse")

# ---------- 5JJA: PP2A-B56gamma (teal) + BubR1 KARD (red) ----------
cmd.reinitialize()
cmd.load(f"{BASE}/structures/5JJA.cif", "pp2a")
cmd.hide("everything")
cmd.show("cartoon", "pp2a")
cmd.color("palecyan", "pp2a and chain A+B")     # PP2A-B56gamma
cmd.color("tv_red",   "pp2a and chain C+D")     # BubR1 KARD peptide
cmd.orient()
cmd.png(f"{OUT}/pp2a_b56_bubr1.png", width=1400, height=1000, dpi=200)
cmd.save(f"{OUT}/pp2a_b56_bubr1.pse")
cmd.quit()
print("done highlights")
