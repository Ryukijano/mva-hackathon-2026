# /// script
# requires-python = ">=3.10, <3.13"
# dependencies = ["pymol-open-source-whl"]
# ///
"""Render rotating frames for stop-motion GIFs."""
import os
os.environ["PYOPENGL_PLATFORM"] = "osmesa"
import pymol
pymol.pymol_argv = ["pymol", "-cq"]
pymol.finish_launching()
from pymol import cmd

BASE = "/scratch/kcwp264/mva-hackathon-2026/figures"
OUT = "/tmp/mva_figs/frames"
os.makedirs(OUT, exist_ok=True)
cmd.bg_color("white")
cmd.set("ray_opaque_background", 1)

def rotate_series(name, frames=36, step=10, w=900, h=700):
    for i in range(frames):
        cmd.png(f"{OUT}/{name}_{i:03d}.png", width=w, height=h, dpi=120)
        cmd.turn("y", step)
    print(name, "frames:", frames)

# ---- GIF 1: BUBR1 truncation rotate ----
cmd.reinitialize()
cmd.load(f"{BASE}/structures/AF-O60566-F1-model_v6.cif", "bubr1")
cmd.hide("everything")
cmd.show("cartoon")
cmd.color("palecyan", "resi 1-736")
cmd.color("salmon", "resi 737-1050")
cmd.show("sticks", "resi 737")
cmd.color("magenta", "resi 737")
cmd.set("stick_radius", 0.55, "resi 737")
cmd.orient()
rotate_series("bubr1_trunc", frames=36, step=10)

# ---- GIF 2: APC/C + MCC complex rotate ----
cmd.reinitialize()
cmd.load(f"{BASE}/structures/6TLJ.cif", "mcc")
cmd.hide("everything")
cmd.show("cartoon", "mcc")
cmd.color("grey75", "mcc")
cmd.color("tv_red", "mcc and chain S")
cmd.color("orange", "mcc and chain Q+R")
cmd.color("paleyellow", "mcc and chain Z")
cmd.orient()
cmd.zoom("mcc and chain S+Q+R+Z", buffer=15)   # center on the MCC
rotate_series("apcc_mcc", frames=36, step=10)

# ---- GIF 3: C-lobe variant zoom rotate ----
cmd.reinitialize()
cmd.load(f"{BASE}/structures/AF-O60566-F1-model_v6.cif", "bubr1")
cmd.hide("everything")
cmd.show("cartoon", "resi 940-1050")
cmd.color("grey80", "resi 940-1050")
for sel, col in [("resi 1002", "red"), ("resi 1012", "orange")]:
    cmd.show("sticks", sel)
    cmd.color(col, sel)
    cmd.set("stick_radius", 0.6, sel)
cmd.zoom("resi 960-1045", buffer=12)
rotate_series("clobe", frames=36, step=10)

cmd.quit()
print("done")
