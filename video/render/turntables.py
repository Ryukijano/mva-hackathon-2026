# /// script
# requires-python = ">=3.10, <3.13"
# dependencies = ["pymol-open-source-whl", "numpy<2", "pillow"]
# ///
"""Dark-theme PyMOL turntables for the pitch video, packed one .npz per movie.

PNG frames go to a temp dir (not scratch: inode cap) and are packed into
video/build/turn_<name>.npz as a uint8 (N, H, W, 3) array.

    UV_CACHE_DIR=$HOME/.cache/uv-mva-video uv run video/render/turntables.py
"""
import os
import sys
import tempfile
from pathlib import Path

os.environ["PYOPENGL_PLATFORM"] = "osmesa"
import numpy as np
import pymol
from PIL import Image

pymol.pymol_argv = ["pymol", "-cq"]
pymol.finish_launching()
from pymol import cmd

REPO = Path(__file__).resolve().parents[2]
STRUCT = REPO / "figures" / "structures"
BUILD = REPO / "video" / "build"
FRAMES, STEP = 120, 3          # 360 deg, 4 s loop at 30 fps
W, H = 760, 600


def style():
    cmd.set_color("vbg", [13 / 255, 17 / 255, 23 / 255])
    cmd.bg_color("vbg")
    cmd.set("ray_opaque_background", 1)
    cmd.set("antialias", 2)
    cmd.set("cartoon_fancy_helices", 1)
    cmd.set("ambient", 0.35)
    cmd.set("specular", 0.25)
    cmd.set("ray_shadow", 0)
    cmd.set("depth_cue", 1)
    cmd.set("fog_start", 0.55)


def spin(name, axis="y"):
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        for i in range(FRAMES):
            fn = f"{tmp}/{i:03d}.png"
            cmd.png(fn, width=W, height=H, dpi=150, ray=1)
            out.append(np.asarray(Image.open(fn).convert("RGB")))
            cmd.turn(axis, STEP)
            if i % 20 == 0:
                print(name, i, flush=True)
    BUILD.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(BUILD / f"turn_{name}.npz", frames=np.stack(out))
    print(name, "packed", len(out), flush=True)


def apcc_mcc():
    cmd.reinitialize()
    style()
    cmd.load(str(STRUCT / "6TLJ.cif"), "m")
    cmd.hide("everything")
    cmd.show("cartoon", "m")
    cmd.set_color("apc", [0.32, 0.36, 0.42])
    cmd.color("apc", "m")
    cmd.set_color("bubr1", [0.97, 0.32, 0.29])   # #f85149
    cmd.set_color("cdc20", [0.82, 0.60, 0.13])   # #d29922
    cmd.set_color("mad2", [0.35, 0.65, 1.00])    # #58a6ff
    cmd.color("bubr1", "m and chain S")
    cmd.color("cdc20", "m and chain Q+R")
    cmd.color("mad2", "m and chain Z")
    cmd.orient("m")
    cmd.zoom("m", buffer=-8)
    spin("apcc_mcc")


def bubr1_trunc():
    cmd.reinitialize()
    style()
    cmd.load(str(STRUCT / "AF-O60566-F1-model_v6.cif"), "bub")
    cmd.hide("everything")
    # ordered parts only (pLDDT in B-factor) keeps the turntable readable
    cmd.show("cartoon", "bub and b > 50")
    cmd.set_color("kept", [0.35, 0.65, 1.00])
    cmd.set_color("lost", [0.97, 0.32, 0.29])
    cmd.color("kept", "resi 1-736")
    cmd.color("lost", "resi 737-1050")
    cmd.set("cartoon_transparency", 0.35, "resi 737-1050")
    cmd.show("spheres", "resi 737 and name CA")
    cmd.set_color("stop", [0.86, 0.38, 0.64])
    cmd.color("stop", "resi 737")
    cmd.show("spheres", "resi 1002 and name CA")
    cmd.set_color("mis", [0.98, 0.80, 0.30])
    cmd.color("mis", "resi 1002")
    cmd.set("sphere_scale", 2.2)
    cmd.orient("bub and b > 50")
    cmd.zoom("bub and b > 50", buffer=2)
    spin("bubr1_trunc")


if __name__ == "__main__":
    which = sys.argv[1:] or ["apcc_mcc", "bubr1_trunc"]
    for w in which:
        globals()[w]()
    cmd.quit()
