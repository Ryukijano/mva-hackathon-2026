# /// script
# requires-python = ">=3.10, <3.15"
# dependencies = ["pymol-open-source-whl", "pillow"]
# ///
"""Render rotating frames and assemble annotated publication-grade GIFs."""
import os
os.environ["PYOPENGL_PLATFORM"] = "osmesa"
import pymol
pymol.pymol_argv = ["pymol", "-cq"]
pymol.finish_launching()
from pymol import cmd
from PIL import Image, ImageDraw, ImageFont

BASE = "/scratch/kcwp264/mva-hackathon-2026/figures"
FRAMES_DIR = "/tmp/mva_figs/frames"
OUT_DIR = f"{BASE}/out"
README_DIR = f"{BASE}/readme"
os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(README_DIR, exist_ok=True)


def setup_scene():
    cmd.reinitialize()
    cmd.bg_color("white")
    cmd.set("ray_opaque_background", 1)
    cmd.set("antialias", 2)
    cmd.set("orthoscopic", 1)
    cmd.set("cartoon_fancy_helices", 1)
    cmd.set("depth_cue", 0)
    cmd.set("specular", 0.25)


def load_font(size, bold=False):
    candidates = [
        "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def annotate_frame(raw_png, title, chips, w_target=None):
    im = Image.open(raw_png).convert("RGB")
    if w_target and im.width != w_target:
        h_target = int(round(im.height * (w_target / im.width)))
        im = im.resize((w_target, h_target), Image.Resampling.LANCZOS)
    W, H = im.size
    top_h = max(38, int(H * 0.065))
    bot_h = max(44, int(H * 0.078))
    canvas = Image.new("RGB", (W, H + top_h + bot_h), (255, 255, 255))
    canvas.paste(im, (0, top_h))
    draw = ImageDraw.Draw(canvas)

    # Top banner
    draw.rectangle([0, 0, W, top_h], fill=(245, 247, 250))
    draw.line([(0, top_h), (W, top_h)], fill=(200, 205, 212), width=1)
    f_title = load_font(max(13, int(W * 0.0185)), bold=True)
    bbox = draw.textbbox((0, 0), title, font=f_title)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((W - tw) // 2, (top_h - th) // 2 - 2), title, fill=(17, 24, 39), font=f_title)

    # Bottom legend bar
    y0 = H + top_h
    draw.rectangle([0, y0, W, y0 + bot_h], fill=(248, 249, 250))
    draw.line([(0, y0), (W, y0)], fill=(200, 205, 212), width=1)
    f_leg = load_font(max(11, int(W * 0.0155)), bold=True)

    # Compute total width of chips
    swatch_w = max(12, int(W * 0.018))
    gap = max(16, int(W * 0.025))
    item_widths = []
    for col_rgb, label in chips:
        lb = draw.textbbox((0, 0), label, font=f_leg)
        item_widths.append(swatch_w + 6 + (lb[2] - lb[0]))
    total_w = sum(item_widths) + gap * (len(chips) - 1)
    cx = max(10, (W - total_w) // 2)
    cy = y0 + bot_h // 2
    for (col_rgb, label), iw in zip(chips, item_widths):
        draw.rectangle([cx, cy - swatch_w // 2, cx + swatch_w, cy + swatch_w // 2], fill=col_rgb, outline=(30, 30, 30))
        lb = draw.textbbox((0, 0), label, font=f_leg)
        lh = lb[3] - lb[1]
        draw.text((cx + swatch_w + 6, cy - lh // 2 - 2), label, fill=(25, 25, 25), font=f_leg)
        cx += iw + gap

    return canvas


def build_gif(name, title, chips, out_gif, readme_gif=None, frames=36, step=10, w=840, h=600):
    imgs_full = []
    imgs_readme = []
    for i in range(frames):
        fp = f"{FRAMES_DIR}/{name}_{i:03d}.png"
        cmd.png(fp, width=w, height=h, dpi=120)
        cmd.turn("y", step)
        imgs_full.append(annotate_frame(fp, title, chips, w_target=760))
        if readme_gif:
            imgs_readme.append(annotate_frame(fp, title, chips, w_target=560))

    imgs_full[0].save(
        out_gif,
        save_all=True,
        append_images=imgs_full[1:],
        duration=85,
        loop=0,
        optimize=True,
    )
    print("Saved GIF:", out_gif)
    if readme_gif:
        imgs_readme[0].save(
            readme_gif,
            save_all=True,
            append_images=imgs_readme[1:],
            duration=85,
            loop=0,
            optimize=True,
        )
        print("Saved README GIF:", readme_gif)


# ---- GIF 1: BUBR1 truncation rotate ----
setup_scene()
cmd.load(f"{BASE}/structures/AF-O60566-F1-model_v6.cif", "bubr1")
cmd.hide("everything")
cmd.show("cartoon")
cmd.color("deepteal", "resi 1-736")
cmd.color("salmon", "resi 737-1050")
cmd.color("marine", "resi 62-226")
cmd.color("gold", "resi 665-682")
for sel, col in [("resi 668", "gold"), ("resi 737", "magenta"), ("resi 1002", "tv_red"), ("resi 1012", "orange")]:
    cmd.show("spheres", sel + " and name CA")
    cmd.set("sphere_scale", 1.35, sel + " and name CA")
    cmd.show("sticks", sel)
    cmd.color(col, sel)
    cmd.set("stick_radius", 0.5, sel)
cmd.orient()
build_gif(
    "bubr1_trunc",
    "BUBR1 (AF-O60566-F1 v6) — p.Leu737Ter Truncation Map",
    [
        ((0, 95, 115), "1–736 Retained (TPR/KARD)"),
        ((234, 179, 8), "K668 (SIRT2)"),
        ((197, 27, 138), "p.Leu737Ter (UGA)"),
        ((242, 132, 130), "737–1050 Lost (Pseudokinase)"),
    ],
    f"{OUT_DIR}/bubr1_trunc_rotate.gif",
)

# ---- GIF 2: C-lobe variant zoom rotate ----
setup_scene()
cmd.load(f"{BASE}/structures/AF-O60566-F1-model_v6.cif", "bubr1")
cmd.hide("everything")
cmd.show("cartoon", "resi 850-1050")
cmd.color("grey85", "resi 850-1050")
cmd.color("lightblue", "resi 990-1001")
cmd.color("wheat", "resi 1008-1020")
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
cmd.distance("d_ca", "resi 1002 and name CA", "resi 1012 and name CA")
cmd.color("black", "d_ca")
cmd.hide("labels", "d_ca")
cmd.distance("hb1", "resi 1002 and name OD1", "resi 978 and name N")
cmd.distance("hb2", "resi 1002 and name ND2", "resi 998 and name O")
cmd.distance("hb3", "resi 1002 and name ND2", "resi 1004 and name O")
cmd.color("deepteal", "hb1")
cmd.color("deepteal", "hb2")
cmd.color("deepteal", "hb3")
cmd.hide("labels", "hb1")
cmd.hide("labels", "hb2")
cmd.hide("labels", "hb3")
cmd.set("dash_width", 2.8)
cmd.orient("resi 970-1025")
cmd.zoom("resi 970-1025", buffer=6)
build_gif(
    "clobe",
    "BUBR1 C-Lobe: p.Asn1002Lys (3-H-Bond C-Cap) vs p.Leu1012Pro (12.32 Å)",
    [
        ((214, 39, 40), "p.Asn1002Lys (AM 0.923)"),
        ((255, 152, 0), "p.Leu1012Pro (MVA1 Ref)"),
        ((0, 121, 107), "N1002 3-H-Bond Staple"),
        ((29, 53, 87), "Trp978/Val998/Asn1004"),
    ],
    f"{OUT_DIR}/clobe_rotate.gif",
    readme_gif=f"{README_DIR}/clobe_rotate_readme.gif",
)

# ---- GIF 3: APC/C + MCC complex rotate ----
setup_scene()
cmd.load(f"{BASE}/structures/6TLJ.cif", "mcc")
cmd.hide("everything")
cmd.show("cartoon", "mcc")
cmd.color("grey80", "mcc")
cmd.color("tv_red", "mcc and chain S")
cmd.color("orange", "mcc and chain Q+R")
cmd.color("gold", "mcc and chain Z")
cmd.orient()
cmd.zoom("mcc and chain S+Q+R+Z", buffer=16)
build_gif(
    "apcc_mcc",
    "PDB 6TLJ Cryo-EM: APC/C Inhibited by MCC (BUBR1 Res 19–345)",
    [
        ((214, 39, 40), "BUBR1 (Chain S, Res 19–345)"),
        ((255, 152, 0), "CDC20 ×2 (Chains Q & R)"),
        ((234, 179, 8), "MAD2L1 (Chain Z)"),
        ((180, 180, 180), "APC/C E3 Ligase"),
    ],
    f"{OUT_DIR}/apcc_mcc_rotate.gif",
    readme_gif=f"{README_DIR}/apcc_mcc_rotate_readme.gif",
)

cmd.quit()
print("done all GIFs")
