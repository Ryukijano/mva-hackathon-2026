# /// script
# requires-python = ">=3.10, <3.13"
# dependencies = ["pymol-open-source-whl"]
# ///
"""Render the SAC reaction structures: APC/C + MCC (6TLJ) and PP2A-B56/BubR1 (5JJA)."""
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

# ---------- Fig 4: APC/C + MCC checkpoint complex (6TLJ) ----------
cmd.reinitialize()
cmd.load(f"{BASE}/structures/6TLJ.cif", "mcc")
n = cmd.count_atoms("mcc")
print("6TLJ atoms:", n)
cmd.hide("everything")
cmd.show("cartoon", "mcc")
cmd.util.cbc("mcc")
for ch in cmd.get_chains("mcc"):
    nres = cmd.count_atoms(f"mcc and chain {ch} and name CA")
    print(f"  chain {ch}: {nres} CA")
cmd.orient()
cmd.png(f"{OUT}/apcc_mcc_complex.png", width=1400, height=1000, dpi=200)
cmd.save(f"{OUT}/apcc_mcc_complex.pse")

# ---------- Fig 5: PP2A-B56gamma / BubR1 KARD complex (5JJA) ----------
cmd.reinitialize()
cmd.load(f"{BASE}/structures/5JJA.cif", "pp2a")
n = cmd.count_atoms("pp2a")
print("5JJA atoms:", n)
cmd.hide("everything")
cmd.show("cartoon", "pp2a")
cmd.util.cbc("pp2a")
for ch in cmd.get_chains("pp2a"):
    nres = cmd.count_atoms(f"pp2a and chain {ch} and name CA")
    print(f"  chain {ch}: {nres} CA")
cmd.orient()
cmd.png(f"{OUT}/pp2a_b56_bubr1.png", width=1400, height=1000, dpi=200)
cmd.save(f"{OUT}/pp2a_b56_bubr1.pse")

# ---------- Fig 6: N-term BubR1 TPR + Blinkin (3SI5: kinetochore docking) ----------
cmd.reinitialize()
cmd.load(f"{BASE}/structures/3SI5.cif", "kin")
n = cmd.count_atoms("kin")
print("3SI5 atoms:", n)
cmd.hide("everything")
cmd.show("cartoon", "kin")
cmd.util.cbc("kin")
for ch in cmd.get_chains("kin"):
    nres = cmd.count_atoms(f"kin and chain {ch} and name CA")
    print(f"  chain {ch}: {nres} CA")
cmd.orient()
cmd.png(f"{OUT}/bubr1_kinetochore_complex.png", width=1400, height=1000, dpi=200)
cmd.save(f"{OUT}/bubr1_kinetochore_complex.pse")

cmd.quit()
print("done: complexes")
