"""Scene renderers S0-S5. Each `sN(t, sc)` returns a 1920x1080 RGB frame for
scene-local time t (seconds; may be slightly <0 or >dur during crossfades).
`sc` is the scene's entry from timing.json; sc["cues"] are VO line onsets.
"""
from __future__ import annotations

import csv
import math
import re
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image

from common import (AMBER, BG, BLUE, BORDER, FAINT, GREEN, MAGENTA, MUTED, PANEL, PANEL2, PURPLE,
                    RED, TEXT, YELLOW, Canvas, appear, back, clamp, ease, ease_io, mix, prog)

REPO = Path(__file__).resolve().parents[2]
BUILD = REPO / "video" / "build"


@lru_cache(maxsize=4)
def turn(name: str) -> np.ndarray:
    return np.load(BUILD / f"turn_{name}.npz")["frames"]


def turn_frame(name: str, t: float) -> Image.Image:
    fr = turn(name)
    return Image.fromarray(fr[int(t * 30) % len(fr)])


def cue(sc, i, default=0.0):
    c = sc.get("cues") or []
    return c[i] if i < len(c) else default


def capsule(cv, p0, p1, w, color, a=1.0, under=None):
    cv.line([p0, p1], color, w, a, under)
    cv.circle(p0[0], p0[1], w / 2, fill=color, a=a, under=under)
    cv.circle(p1[0], p1[1], w / 2, fill=color, a=a, under=under)


def xchrom(cv, cx, cy, s, color, a=1.0, under=None, spread=0.0):
    """X-shaped replicated chromosome; `spread` pulls sisters apart."""
    for sgn in (-1, 1):
        ox = sgn * spread
        capsule(cv, (cx + ox - s * .32, cy - s * .5), (cx + ox + s * .32, cy + s * .5), s * .28, color, a, under) \
            if sgn < 0 else \
            capsule(cv, (cx + ox + s * .32, cy - s * .5), (cx + ox - s * .32, cy + s * .5), s * .28, color, a, under)


# =============================================================== S0 title ====
def s0(t, sc):
    cv = Canvas()
    # metaphase plate -> anaphase with one non-disjunction (abstract motif)
    k = ease_io(prog(t, 0.5, 1.9))
    lp, rp = (700, 330), (1220, 330)
    a0 = ease(prog(t, 0.0, 0.6))
    for p in (lp, rp):
        cv.circle(p[0], p[1], 9, fill=MUTED, a=0.8 * a0)
    n = 7
    arrivals = {-1: [], 1: []}
    for i in range(n):
        for side in (-1, 1):
            dest = 1 if (i == 2 or side > 0) else -1
            arrivals[dest].append((i, side))
    for dest, lst in arrivals.items():
        pole = rp if dest > 0 else lp
        m = len(lst)
        for r, (i, side) in enumerate(lst):
            y0 = 190 + i * 47
            x0 = 960 + side * 9
            fx = pole[0] - dest * (70 + 14 * (r % 2))
            fy = pole[1] + (r - (m - 1) / 2) * 34
            x = x0 + (fx - x0) * k
            yy = y0 + (fy - y0) * k
            cv.line([pole, (x, yy)], BORDER, 1.5, a=0.7 * a0)
            col = RED if i == 2 else (BLUE if i % 2 else PURPLE)
            capsule(cv, (x, yy - 12), (x, yy + 12), 11, col, a=a0)
    if k >= 0.99:
        cv.text((rp[0] + 40, rp[1] - 120), "+1", 26, "Bold", RED, ease(prog(t, 2.4, 0.4)))
        cv.text((lp[0] - 40, lp[1] - 120), "−1", 26, "Bold", RED, ease(prog(t, 2.4, 0.4)), anchor="ra")
    a, dy = appear(t, 0.9, 0.7, 26)
    cv.text((960, 590), "Rare Disease, Real Kid", 84, "Bold", TEXT, a, anchor="mm", dy=dy)
    a, dy = appear(t, 1.3, 0.7, 20)
    cv.text((960, 672), "Upstream-first therapy hypotheses for BUB1B mosaic variegated aneuploidy",
            32, "Medium", MUTED, a, anchor="mm", dy=dy)
    a, dy = appear(t, 1.7, 0.7, 16)
    cv.text((960, 742), "MVA Hackathon 2026  ·  Track 2  ·  Ryukijano", 28, "SemiBold", BLUE, a,
            anchor="mm", dy=dy)
    return cv.done()


# ================================================================ S1 case ====
BX0, BX1, BY = 720, 1800, 300


def rx(res):
    return BX0 + (res - 1) / 1049 * (BX1 - BX0)


def s1(t, sc):
    cv = Canvas()
    c0, c1, c2, c3, c4 = (cue(sc, i) for i in range(5))
    cv.header("01", "The case", ease(prog(t, 0, .5)))
    cv.footer(ease(prog(t, 0, .5)))

    # phenotype card
    a = ease(prog(t, c0, .5))
    cv.rect((100, 170, 640, 590), fill=PANEL, outline=BORDER, a=a)
    cv.text((132, 204), "PROBAND · PHENOTYPE", 20, "Bold", MUTED, a, under=PANEL)
    for i, (lab, col, at) in enumerate([("Embryonal rhabdomyosarcoma", RED, c0 + .5),
                                        ("Growth restriction", AMBER, c0 + 2.3),
                                        ("Microcephaly", PURPLE, c0 + 3.6)]):
        aa, dy = appear(t, at, .45, 14)
        cv.chip((132, 250 + i * 64 + dy), lab, 26, TEXT, PANEL2, None, aa, under=PANEL, dot=col)
    aa, dy = appear(t, c1, .5, 14)
    cv.text((132, 470 + dy), "Whole-genome sequencing →", 24, "SemiBold", BLUE, aa, under=PANEL)
    cv.text((132, 506 + dy), "two ultra-rare BUB1B variants", 24, "Medium", TEXT, aa, under=PANEL)

    # BUBR1 domain bar
    a, dy = appear(t, c1 + .4, .5, 14)
    cv.text((BX0, 196 + dy), "BUB1B  →  BUBR1", 34, "Bold", TEXT, a)
    cv.text((BX0 + cv.textw("BUB1B  →  BUBR1", 34, "Bold") + 18, 205 + dy), "mitotic checkpoint protein · 1,050 aa",
            22, "Medium", MUTED, a)
    k = ease_io(prog(t, c1 + .8, 1.4))
    if k > 0:
        xe = BX0 + (BX1 - BX0) * k
        cv.rect((BX0, BY, xe, BY + 44), fill=PANEL2, outline=BORDER, r=10)
        for r0, r1, col, lab in [(62, 226, BLUE, "N-terminal TPR"), (766, 1050, PURPLE, "pseudokinase")]:
            x0, x1 = rx(r0), min(rx(r1), xe)
            if x1 > x0:
                cv.rect((x0, BY + 3, x1, BY + 41), fill=col, r=8, a=.85)
                cv.text(((rx(r0) + rx(r1)) / 2, BY + 66), lab, 20, "SemiBold", col, ease(prog(t, c1 + 2.0, .4)),
                        anchor="mm")
        cv.text((rx(495), BY + 66), "KEN · GLEBS · ABBA · KARD motifs", 20, "Medium", MUTED,
                ease(prog(t, c1 + 2.2, .4)), anchor="mm")
        for res in (1, 1050):
            cv.text((rx(res), BY - 14), str(res), 18, "Medium", FAINT, ease(prog(t, c1 + 2.0, .4)), anchor="mb")

    # stop-gain L737Ter
    def variant(res, col, at, name, l1, l2, box):
        p = prog(t, at, .5)
        if p <= 0:
            return
        s = back(p)
        x = rx(res)
        cv.line([(x, BY - 4), (x, BY - 34)], col, 3, a=clamp(p * 2))
        cv.star(x, BY - 52, 20 * s, col)
        cv.text((x, BY - 80), str(res), 20, "Bold", col, clamp(p * 2), anchor="mb")
        aa, dy = appear(t, at + .4, .5, 14)
        cv.rect(box, fill=PANEL, outline=col, a=aa)
        cv.text((box[0] + 24, box[1] + 22 + dy), name, 30, "Bold", col, aa, under=PANEL)
        cv.text((box[0] + 24, box[1] + 66 + dy), l1, 22, "SemiBold", TEXT, aa, under=PANEL)
        cv.text((box[0] + 24, box[1] + 98 + dy), l2, 22, "Medium", MUTED, aa, under=PANEL)

    variant(737, MAGENTA, c2, "p.Leu737Ter", "stop-gain · ClinVar P/LP for MVA1",
            "removes the pseudokinase · NMD substrate", (720, 420, 1240, 560))
    lost = ease(prog(t, c2 + 2.2, .8))
    if lost > 0:
        x0 = rx(737)
        for xx in np.arange(x0 + 6, BX1 - 4, 14):
            cv.line([(xx, BY + 40), (min(xx + 16, BX1 - 4), BY + 4)], BG, 3, a=.55 * lost, under=PURPLE)
    variant(1002, YELLOW, c3, "p.Asn1002Lys", "C-lobe missense · ultra-rare (gnomAD)",
            "10 residues from the known MVA1 L1012P", (1280, 420, 1800, 560))
    for i, (lab, col) in enumerate([("AlphaMissense 0.9229 · likely pathogenic", RED),
                                    ("ESM-1v LLR −0.110 · mild", AMBER)]):
        aa, dy = appear(t, c3 + 1.6 + i * .7, .45, 12)
        cv.chip((1280, 580 + i * 52 + dy), lab, 22, TEXT, PANEL2, col, aa, dot=col)

    # allele architecture + Track 1
    aa, dy = appear(t, c4, .5, 16)
    y = 760 + dy
    w1 = cv.chip((100, y), "Allele 1 · p.Leu737Ter · null", 26, TEXT, PANEL2, MAGENTA, aa, dot=MAGENTA)
    cv.text((100 + w1 + 22, y + 21), "+", 34, "Bold", MUTED, aa, anchor="mm")
    w2 = cv.chip((100 + w1 + 44, y), "Allele 2 · p.Asn1002Lys · hypomorph", 26, TEXT, PANEL2, YELLOW, aa, dot=YELLOW)
    aa2, _ = appear(t, c4 + 1.2, .5)
    cv.text((100 + w1 + w2 + 70, y + 21), "→  classic viable MVA1 architecture", 26, "SemiBold", TEXT, aa2,
            anchor="lm")
    p = prog(t, c4 + 3.2, .5)
    if p > 0:
        s = back(p, 1.2)
        box = (100, 870, 100 + 820 * min(1, s), 950)
        cv.rect(box, fill=(18, 44, 28), outline=GREEN, a=clamp(p * 2))
        if p > .5:
            cv.circle(140, 910, 22, fill=GREEN)
            cv.check(140, 912, 22, BG)
            cv.text((180, 910), "Track 1: full match · rank 1 · 100 / 100 · F-max 1.0", 28, "Bold", GREEN,
                    ease(prog(t, c4 + 3.5, .4)), anchor="lm", under=(18, 44, 28))
    return cv.done()


# =========================================================== S2 mechanism ===
def cell_division(cv, t, t0, t_mn, ox, oy):
    k = ease_io(prog(t, t0, 2.6))
    a = ease(prog(t, t0, .4))
    r = 150 - 45 * k
    sep = 120 * k
    for side in (-1, 1):
        cv.circle(ox + side * sep, oy, r, fill=(20, 30, 44), outline=BLUE, width=3, a=a, under=BG)
    # chromosomes: 3 left, 5 right (uneven), placed in each daughter
    pos_l = [(-40, -40), (30, 10), (-20, 50)]
    pos_r = [(-40, -50), (30, -30), (-30, 20), (40, 40), (0, 70)]
    for (dx, dy) in pos_l:
        xchrom(cv, ox - sep + dx * (.6 + .4 * k), oy + dy * (.6 + .4 * k), 30, PURPLE, a, PANEL)
    for i, (dx, dy) in enumerate(pos_r):
        xchrom(cv, ox + sep + dx * (.6 + .4 * k), oy + dy * (.6 + .4 * k), 30, RED if i >= 3 else PURPLE, a,
               PANEL)
    if k > .95:
        cv.text((ox - sep, oy + r + 30), "3", 30, "Bold", MUTED, a, anchor="mm", under=BG)
        cv.text((ox + sep, oy + r + 30), "5", 30, "Bold", RED, a, anchor="mm", under=BG)
    pm = prog(t, t_mn, .6)
    if pm > 0:
        pulse = 1 + .15 * math.sin((t - t_mn) * 5) * (1 - prog(t, t_mn + 3, 1))
        mx, my = ox + sep + 40, oy - r - 46
        cv.circle(mx, my, 20 * back(pm) * pulse, fill=(60, 30, 40), outline=RED, width=3, under=BG)
        cv.text((mx + 32, my), "micronucleus", 20, "SemiBold", RED, ease(pm), anchor="lm", under=BG)


def s2(t, sc):
    cv = Canvas()
    c0, c1, c2, c3, c4 = (cue(sc, i) for i in range(5))
    cv.header("02", "Mechanism", ease(prog(t, 0, .5)))
    cv.footer(ease(prog(t, 0, .5)))

    # left inset: 6TLJ -> BUBR1 truncation -> dividing cell
    a = ease(prog(t, c0, .5))
    cv.rect((100, 150, 860, 900), fill=BG, outline=BORDER, a=a)
    ia = a * (1 - ease(prog(t, c1 - .3, .6)))
    ib = ease(prog(t, c1 - .3, .6)) * (1 - ease(prog(t, c2 - .2, .6)))
    ic = ease(prog(t, c2 - .2, .6))
    if ia > 0:
        cv.paste(turn_frame("apcc_mcc", t), (115, 165), ia, size=(730, 576))
        cv.text((130, 800), "APC/C · MCC  (PDB 6TLJ)", 24, "Bold", TEXT, ia, under=BG)
        x = 130
        for lab, col in [("BUBR1", RED), ("CDC20", AMBER), ("MAD2", BLUE), ("APC/C", (82, 92, 107))]:
            x += cv.chip((x, 836), lab, 18, TEXT, PANEL2, None, ia, dot=col, under=BG) + 10
    if ib > 0:
        cv.paste(turn_frame("bubr1_trunc", t - c1), (115, 165), ib, size=(730, 576))
        cv.text((130, 800), "BUBR1  (AlphaFold AF-O60566)", 24, "Bold", TEXT, ib, under=BG)
        x = 130
        for lab, col in [("kept 1–736", BLUE), ("lost after p.Leu737Ter", RED), ("N1002", YELLOW)]:
            x += cv.chip((x, 836), lab, 18, TEXT, PANEL2, None, ib, dot=col, under=BG) + 10
    if ic > 0:
        cell_division(cv, t, c2, c3 + 3.5, 480, 470)
        cv.text((130, 800), "Weak checkpoint → uneven daughters", 24, "Bold", TEXT, ic, under=BG)
        cv.text((130, 840), "mosaic aneuploidy", 20, "Medium", MUTED, ic, under=BG)

    # right cascade
    X0, X1 = 1100, 1820
    nodes = [
        (c0 + .6, "Unattached kinetochore", "signal: not every chromosome is attached", BLUE),
        (c0 + 2.2, "MCC: BUBR1 · BUB3 · MAD2 · CDC20", "the mitotic checkpoint complex", BLUE),
        (c0 + 4.6, "APC/C held → anaphase waits", "the anaphase trigger stays off", GREEN),
        (c1 + .2, "Weak BUBR1 → premature anaphase", "one allele truncated, one weakened", RED),
        (c2 + .2, "Mis-segregation → mosaic aneuploidy", "uneven chromosome sets", RED),
    ]
    y = 150
    ys = []
    for i, (at, title, sub, col) in enumerate(nodes):
        aa, dy = appear(t, at, .5, 14)
        cv.rect((X0, y + dy, X1, y + 100 + dy), fill=PANEL, outline=col, a=aa)
        cv.text((X0 + 24, y + 30 + dy), title, 28, "Bold", TEXT, aa, under=PANEL)
        cv.text((X0 + 24, y + 70 + dy), sub, 20, "Medium", MUTED, aa, under=PANEL)
        if i:
            cv.arrow(((X0 + X1) / 2, y - 30), ((X0 + X1) / 2, y - 3), MUTED, 3, ease(prog(t, at - .2, .4)))
        ys.append(y)
        y += 132
    # downstream fan
    aa, dy = appear(t, c3, .5, 14)
    cv.arrow(((X0 + X1) / 2, y - 30), ((X0 + X1) / 2, y - 3), MUTED, 3, ease(prog(t, c3 - .2, .4)))
    cv.rect((X0, y + dy, X1, y + 200 + dy), fill=PANEL, outline=AMBER, a=aa)
    cv.text((X0 + 24, y + 30 + dy), "Downstream damage", 28, "Bold", TEXT, aa, under=PANEL)
    chips = [(c3 + .3, "Proteotoxic / lysosomal stress", AMBER), (c3 + 2.2, "ROS", AMBER),
             (c3 + 4.0, "Micronuclei", RED), (c3 + 6.4, "cGAS–STING → IFN / IL-6", RED)]
    cx, cy = X0 + 24, y + 66
    for at, lab, col in chips:
        ca, cdy = appear(t, at, .45, 10)
        w = cv.textw(lab, 21, "SemiBold") + 28 + 19
        if cx + w > X1 - 20:
            cx, cy = X0 + 24, cy + 56
        cv.chip((cx, cy + dy + cdy), lab, 21, TEXT, PANEL2, col, ca, under=PANEL, dot=col)
        cx += w + 12

    # c4: upstream vs buffer brackets
    pa = ease(prog(t, c4, .6))
    pb = ease(prog(t, c4 + 2.0, .6))
    for (ya, yb, col, lab, p) in [(ys[0], ys[3] + 100, GREEN, "1  raise BUBR1", pa),
                                  (ys[4], y + 200, BLUE, "2  buffer", pb)]:
        if p <= 0:
            continue
        xb = X0 - 22
        cv.line([(xb + 10, ya + 6), (xb, ya + 6), (xb, ya + 6 + (yb - ya - 12) * p), (xb + 10, ya + 6 + (yb - ya - 12) * p)],
                col, 4)
        cv.text((xb - 14, (ya + yb) / 2), lab, 22, "Bold", col, p, anchor="rm")
    return cv.done()


# =============================================================== S3 stack ====
COLS = [100 + i * 440 for i in range(4)]
CW = 400


def card_h(cv, box, title, lines, title_size=30):
    x0, x1 = box[0], box[2]
    h = 28 + title_size
    for ln in lines:
        h += 44 if isinstance(ln, tuple) else len(cv.wrap(ln, x1 - x0 - 44, 20, "Medium")) * 20 * 1.32 + 4
    return h + 18


def card(cv, box, title, lines, col, a, dy=0.0, dim=False, strike=0.0, title_size=30):
    """Card with title + text lines / (text, colour) chips; y1=None -> auto height. Returns y1."""
    x0, y0, x1, y1 = box
    if y1 is None:
        y1 = y0 + card_h(cv, box, title, lines, title_size)
    bottom = y1
    y0, y1 = y0 + dy, y1 + dy
    fill = PANEL if not dim else (17, 21, 27)
    cv.rect((x0, y0, x1, y1), fill=fill, outline=col if not dim else BORDER, a=a, width=3 if not dim else 2)
    tc = col if not dim else MUTED
    cv.text((x0 + 22, y0 + 20), title, title_size, "Bold", tc, a, under=fill)
    if strike > 0:
        tw = cv.textw(title, title_size, "Bold")
        cv.line([(x0 + 16, y0 + 20 + title_size * .62), (x0 + 28 + tw * strike, y0 + 20 + title_size * .62)], RED, 5, a)
    yy = y0 + 28 + title_size
    for ln in lines:
        if isinstance(ln, tuple):           # (text, colour) chip
            cv.chip((x0 + 22, yy + 4), ln[0], 19, TEXT, PANEL2, ln[1], a, under=fill, dot=ln[1])
            yy += 44
        else:
            h = cv.para((x0 + 22, yy + 6), ln, x1 - x0 - 44, 20, "Medium", TEXT if not dim else MUTED, a, under=fill)
            yy += h + 4
    return bottom


def nmd_strip(cv, t, at, x, y):
    a = ease(prog(t, at, .5))
    k = ease(prog(t, at + 2.0, 2.5))
    w = CW - 40
    cv.text((x, y), "UGA stop → mRNA decay", 22, "Bold", TEXT, a)
    yy = y + 62
    # exon blocks; fragments drift apart once decay starts
    for i in range(8):
        ex0 = x + 20 + i * (w / 8)
        drift = (i - 3.5) * 6 * k
        jitter = math.sin(i * 1.7) * 10 * k
        cv.rect((ex0 + drift + 3, yy - 12 + jitter, ex0 + w / 8 + drift - 3, yy + 12 + jitter),
                fill=mix(BLUE, BG, .55 * k), r=5, a=a * (1 - .6 * k))
    xp = x + 20 + w * .62
    cv.line([(xp, yy - 24), (xp, yy + 24)], MAGENTA, 4, a)
    cv.text((xp + 8, yy - 26), "PTC", 18, "Bold", MAGENTA, a, anchor="lt")
    cv.text((x, yy + 40), "NMD", 22, "Bold", RED, ease(prog(t, at + 2.0, .4)))
    cv.text((x + 64, yy + 40), "→ readthrough has nothing to read", 20, "Medium", MUTED, ease(prog(t, at + 2.6, .4)))


def s3(t, sc):
    cv = Canvas()
    c = [cue(sc, i) for i in range(7)]
    cv.header("03", "The stack", ease(prog(t, 0, .5)))
    cv.footer(ease(prog(t, 0, .5)))
    heads = [("UGA rescue", MAGENTA), ("BUBR1 stabilisation", BLUE), ("Approved proteostasis", GREEN),
             ("Anti-target", RED)]
    for i, (lab, col) in enumerate(heads):
        aa, dy = appear(t, c[0] + .15 + i * .25, .5, 14)
        x = COLS[i]
        cv.rect((x, 140 + dy, x + CW, 210 + dy), fill=PANEL, outline=col, a=aa)
        cv.badge(x + 38, 175 + dy, i + 1, col, 18, aa)
        cv.text((x + 68, 175 + dy), lab, 26, "Bold", TEXT, aa, anchor="lm", under=PANEL)
    ra = ease(prog(t, c[0] + 1.2, .6))
    cv.arrow((COLS[0] + 20, 236), (COLS[2] + CW - 20, 236), FAINT, 2, ra, head=10)
    cv.text((COLS[0] + 20, 250), "upstream", 17, "SemiBold", FAINT, ra)
    cv.text((COLS[2] + CW - 20, 250), "downstream", 17, "SemiBold", FAINT, ra, anchor="ra")

    # column 1
    x = COLS[0]
    nmd_strip(cv, t, c[1], x, 282)
    aa, dy = appear(t, c[2], .55, 18)
    yb = card(cv, (x, 420, x + CW, None), "Amlexanox",
              ["NMD inhibition + readthrough", ("FDA: topical oral paste only", AMBER),
               "Systemic use needs reformulation + patient-cell proof"], GREEN, aa, dy)
    aa, dy = appear(t, c[3], .55, 18)
    yb = card(cv, (x, yb + 16, x + CW, None), "Ataluren",
              ["Readthrough only · no NMD activity", ("UK/MHRA conditional only", MUTED),
               ("FDA NDA withdrawn", MUTED), ("EMA not renewed", MUTED)], MUTED, aa, dy, dim=True, title_size=26)
    aa, dy = appear(t, c[3] + 3.2, .5, 14)
    card(cv, (x, yb + 16, x + CW, yb + 86), "ELX-02 · investigational", [], MUTED, aa, dy, dim=True, title_size=22)

    # column 2
    x = COLS[1]
    aa, dy = appear(t, c[4], .55, 18)
    yb = card(cv, (x, 282, x + CW, None), "SIRT2 / NAD+ axis",
         ["SIRT2 deacetylates BUBR1 (K668) and stabilises the residual protein"], BLUE, aa, dy)
    aa, dy = appear(t, c[4] + 2.6, .55, 18)
    card(cv, (x, yb + 16, x + CW, None), "NMN · NR",
         [("supplements → comparators only", AMBER),
          "Lifespan gain in BubR1-hypomorph mice came from SIRT2 overexpression, not NMN"], MUTED, aa, dy, dim=True)

    # column 3
    x = COLS[2]
    items = [("1  Ravicti", "sodium-free 4-PBA prodrug", [("FDA/EMA · urea-cycle disorders", GREEN)]),
             ("2  Arimoclomol", "HSF1 / lysosomal amplifier", [("FDA + miglustat (NPC)", GREEN),
                                                                ("EMA refused (2026)", AMBER)]),
             ("3  Metformin / rilmenidine", "mTORC1-independent autophagy",
              [("metformin FDA/EMA", GREEN), ("rilmenidine UK/EU · not FDA", AMBER)])]
    y = 282
    for i, (title, sub, chips) in enumerate(items):
        aa, dy = appear(t, c[5] + 1.0 + i * 1.6, .5, 16)
        y = card(cv, (x, y, x + CW, None), title, [sub] + chips, GREEN if i == 0 else mix(GREEN, MUTED, .35), aa,
                 dy, title_size=26) + 16
    aa, _ = appear(t, c[5] + 5.0, .5)
    cv.para((x, y + 4), "Approved for other indications: extrapolated, assay-gated", CW, 19, "Medium", FAINT, aa)

    # column 4
    x = COLS[3]
    aa, dy = appear(t, c[6], .5, 18)
    yb = card(cv, (x, 282, x + CW, None), "Sirolimus",
         ["Rapamycin itself is aneugenic: chromosome mis-segregation + micronuclei (Bonatti 1998)",
          ("LINCS signal WEAK / MIXED", AMBER)], RED, aa, dy, strike=ease(prog(t, c[6] + 1.6, .6)))
    aa, dy = appear(t, c[6] + 3.0, .5, 14)
    card(cv, (x, yb + 16, x + CW, None), "Antioxidants / Nrf2",
         ["flagged: may aid tumour progression in an MVA1 child"], RED, aa, dy, dim=True, title_size=24)
    return cv.done()


# ============================================================ S4 evidence ===
@lru_cache(maxsize=1)
def screen_stats():
    def rows(p):
        with open(REPO / p) as fh:
            return list(csv.DictReader(fh))
    allr = rows("track2/data/chembl_axis_drugs.csv")
    appr = rows("track2/data/chembl_axis_drugs_approved.csv")
    src = (REPO / "track2/drug_screen.py").read_text()
    block = src.split("TARGETS = {", 1)[1].split("}", 1)[0]
    targets = re.findall(r'"([A-Z0-9]+)":\s*"', block)
    by = {}
    for r in appr:
        by[r["gene"]] = by.get(r["gene"], 0) + 1
    return len(allr), len(appr), targets, sorted(by.items(), key=lambda kv: -kv[1])


def s4(t, sc):
    cv = Canvas()
    c = [cue(sc, i) for i in range(6)]
    cv.header("04", "Evidence", ease(prog(t, 0, .5)))
    cv.footer(ease(prog(t, 0, .5)))
    n_all, n_appr, targets, by = screen_stats()

    # terminal
    a = ease(prog(t, c[0], .5))
    TX0, TY0, TX1, TY1 = 100, 140, 1000, 560
    term = (10, 13, 18)
    cv.rect((TX0, TY0, TX1, TY1), fill=term, outline=BORDER, a=a)
    cv.rect((TX0, TY0, TX1, TY0 + 40), fill=PANEL2, r=14, a=a)
    cv.rect((TX0, TY0 + 26, TX1, TY0 + 40), fill=PANEL2, r=0, a=a)
    for i, col in enumerate([RED, AMBER, GREEN]):
        cv.circle(TX0 + 26 + i * 24, TY0 + 20, 7, fill=col, a=a, under=PANEL2)
    cv.text((TX0 + 450, TY0 + 20), "replayed from committed CSVs · no live query", 16, "Medium", MUTED, a,
            anchor="mm", under=PANEL2)
    cmd = "$ python track2/drug_screen.py --approved-only"
    n = int(len(cmd) * clamp((t - c[0] - .3) / 1.6))
    cv.text((TX0 + 24, TY0 + 64), cmd[:n], 22, "Medium", GREEN, a, mono=True, under=term)
    if n < len(cmd) and int(t * 2.5) % 2 == 0 and a > 0:
        cx = TX0 + 24 + cv.textw(cmd[:n], 22, "Medium", True)
        cv.rect((cx + 2, TY0 + 64, cx + 14, TY0 + 90), fill=GREEN, r=0, a=a, under=term)
    out = [
        (c[1] + .2, f"axis targets: {len(targets)}  ({', '.join(targets[:4])}, …)", MUTED),
        (c[1] + .9, f"+ FKBP1A  — needed to retrieve rapalogs", AMBER),
        (c[1] + 1.8, f"all phases ............ {n_all} drug–target rows", TEXT),
        (c[1] + 4.2, f"approved (max_phase 4)  {n_appr} rows", GREEN),
        (c[1] + 5.0, "  " + " · ".join(f"{g} {k}" for g, k in by), MUTED),
        (c[1] + 6.0, f"wrote {n_appr} drug-target rows", MUTED),
    ]
    for i, (at, s, col) in enumerate(out):
        aa = ease(prog(t, at, .25))
        cv.text((TX0 + 24, TY0 + 112 + i * 40), s, 20, "Medium", col, aa, mono=True, under=term)

    # funnel
    FX0, FX1 = 1060, 1820
    aa, dy = appear(t, c[1] + 1.8, .5, 14)
    cv.text((FX0, 160 + dy), "ChEMBL target-first screen", 28, "Bold", TEXT, aa)
    k1 = ease(prog(t, c[1] + 2.0, .8))
    cv.rect((FX0, 220, FX0 + (FX1 - FX0) * k1, 290), fill=mix(BLUE, BG, .35), r=10, a=aa)
    cv.text((FX0 + 20, 255), f"{int(round(n_all * k1))} drug–target rows", 26, "Bold", TEXT, aa, anchor="lm",
            under=mix(BLUE, BG, .35))
    k2 = ease(prog(t, c[1] + 4.2, .8))
    w2 = (FX1 - FX0) * n_appr / n_all
    cv.rect((FX0, 320, FX0 + w2 * k2, 390), fill=mix(GREEN, BG, .3), r=10, a=ease(prog(t, c[1] + 4.2, .3)))
    cv.text((FX0 + w2 + 20, 355), f"{int(round(n_appr * k2))} approved", 26, "Bold", GREEN,
            ease(prog(t, c[1] + 4.2, .3)), anchor="lm")
    aa, dy = appear(t, c[1] + 5.6, .5, 10)
    cv.text((FX0, 420 + dy), "eligible matches — not leads", 24, "SemiBold", AMBER, aa)

    # LINCS firewall
    aa, dy = appear(t, c[2], .5, 14)
    LX0, LY0 = 100, 610
    cv.text((LX0, LY0 + dy), "LINCS firewall", 28, "Bold", TEXT, aa)
    cv.text((LX0, LY0 + 42 + dy), "L2S2 + L1000CDS2 · human MVA + BubR1-mouse signatures · reverse FDR < 0.05", 20, "Medium",
            MUTED, aa)
    tot = 676
    counts = [("ACCEPT", 0, GREEN), ("WEAK", 2, AMBER), ("REJECT", 674, RED)]
    for i, (lab, nv, col) in enumerate(counts):
        at = c[3] + i * 1.0
        p = prog(t, at, .9)
        aa = ease(prog(t, at, .3))
        x = LX0 + i * 300
        cv.text((x, 760), lab, 22, "Bold", col, aa)
        cv.text((x, 790), str(int(round(nv * ease(p)))), 72, "Bold", TEXT, aa)
    kb = ease(prog(t, c[3] + 2.4, .8))
    if kb > 0:
        xs = LX0
        for lab, nv, col in counts:
            w = max(nv / tot * 880, 6 if nv else 0) * kb
            if w:
                cv.rect((xs, 890, xs + w, 914), fill=col, r=4)
            xs += w + (4 if w else 0)
    aa, dy = appear(t, c[4], .5, 12)
    cv.chip((LX0, 940 + dy), "sirolimus: 1 reverse vs 4 mimic FDR signatures → MIXED → WEAK + anti-target", 20, TEXT,
            PANEL2, AMBER, aa, dot=RED)

    # ESM-1v LLR
    aa, dy = appear(t, c[5], .5, 14)
    EX0, EX1 = 1060, 1820
    cv.text((EX0, 610 + dy), "ESM-1v ensemble LLR", 28, "Bold", TEXT, aa)
    cv.text((EX0, 652 + dy), "more negative = more disruptive", 20, "Medium", MUTED, aa)
    zx = EX1 - 20
    scale = (zx - EX0 - 120) / 1.801
    cv.line([(zx, 700), (zx, 910)], MUTED, 2, aa)
    cv.text((zx, 920), "0", 18, "Medium", MUTED, aa, anchor="mt")
    for i, (lab, v, col) in enumerate([("p.Asn1002Lys (ours)", -0.110, YELLOW),
                                       ("p.Leu1012Pro (classic MVA1)", -1.801, RED)]):
        k = ease(prog(t, c[5] + .6 + i * 1.0, .9))
        y = 738 + i * 104
        w = -v * scale * k
        cv.text((EX0, y - 8), lab, 20, "SemiBold", TEXT, aa, anchor="lb")
        cv.rect((zx - w, y, zx, y + 46), fill=col, r=6, a=aa)
        cv.text((zx - w - 14, y + 23), f"{v * k:+.3f}".replace("-", "−"), 24, "Bold", col, aa, anchor="rm")
    aa, dy = appear(t, c[5] + 3.4, .5, 10)
    cv.text((EX0, 950 + dy), "N1002K is not assumed L1012P-equivalent", 22, "SemiBold", AMBER, aa)
    return cv.done()


# =============================================================== S5 close ===
def s5(t, sc):
    cv = Canvas()
    c0, c1 = cue(sc, 0), cue(sc, 1)
    fade = 1 - .7 * ease(prog(t, c1 - .2, .7))
    cv.header("05", "Next steps", ease(prog(t, 0, .5)) * fade)
    steps = [("Restore full-length BUBR1", "NMD rescue: RT-qPCR → Western blot", MAGENTA, c0 + .3),
             ("Stabilise what remains", "SIRT2 / NAD+ stabilisation assay", BLUE, c0 + 2.4),
             ("Clear aggregates", "proteostasis + autophagy readouts", GREEN, c0 + 4.0)]
    bw, gap, y0 = 500, 70, 170
    x0 = (1920 - (3 * bw + 2 * gap)) / 2
    for i, (title, sub, col, at) in enumerate(steps):
        aa, dy = appear(t, at, .5, 14)
        aa *= fade
        x = x0 + i * (bw + gap)
        pulse = math.exp(-((t - (c0 + 6.4) - i * .25) / .25) ** 2)
        if pulse > .02:
            cv.rect((x - 8 * pulse, y0 - 8 * pulse, x + bw + 8 * pulse, y0 + 150 + 8 * pulse), outline=col,
                    width=3, a=pulse * fade)
        cv.rect((x, y0 + dy, x + bw, y0 + 150 + dy), fill=PANEL, outline=col, a=aa)
        cv.badge(x + 40, y0 + 42 + dy, i + 1, col, 18, aa)
        cv.text((x + 72, y0 + 42 + dy), title, 27, "Bold", TEXT, aa, anchor="lm", under=PANEL)
        cv.text((x + 30, y0 + 104 + dy), sub, 20, "Medium", MUTED, aa, anchor="lm", under=PANEL)
        if i:
            cv.arrow((x - gap + 10, y0 + 75), (x - 10, y0 + 75), MUTED, 3, ease(prog(t, at - .2, .4)) * fade)
    aa, dy = appear(t, c0 + 5.2, .5, 12)
    aa *= fade
    cv.rect((x0, 360 + dy, x0 + 3 * bw + 2 * gap, 420 + dy), outline=RED, width=2, a=aa)
    cv.text((960, 390 + dy), "Oncology surveillance throughout  ·  every step assay-gated in patient cells", 22,
            "SemiBold", RED, aa, anchor="mm")

    # disclaimer card
    aa, dy = appear(t, c1, .6, 20)
    box = (260, 480 + dy, 1660, 700 + dy)
    cv.rect(box, fill=(33, 27, 14), outline=AMBER, width=3, a=aa)
    cv.text((960, 545 + dy), "Preclinical N-of-1 research proposal", 40, "Bold", AMBER, aa, anchor="mm",
            under=(33, 27, 14))
    cv.text((960, 615 + dy), "not clinical advice or a treatment recommendation", 32, "SemiBold", TEXT, aa,
            anchor="mm", under=(33, 27, 14))
    aa, dy = appear(t, c1 + 1.6, .6, 14)
    cv.text((960, 780 + dy), "github.com/Ryukijano/mva-hackathon-2026", 30, "Medium", BLUE, aa, anchor="mm",
            mono=True)
    w = cv.textw("CC BY 4.0", 22, "Bold") + 40
    cv.chip((960 - w / 2, 830 + dy), "CC BY 4.0", 22, TEXT, PANEL2, BORDER, aa, weight="Bold")
    aa, dy = appear(t, c1 + 2.4, .6, 10)
    cv.text((960, 935 + dy), "Structures: AlphaFold DB AF-O60566 (CC BY 4.0) · PDB 6TLJ  ·  Voice: Kokoro-82M "
            "(Apache-2.0)", 18, "Medium", FAINT, aa, anchor="mm")
    cv.footer(ease(prog(t, 0, .5)))
    return cv.done()


SCENES = {"S0": s0, "S1": s1, "S2": s2, "S3": s3, "S4": s4, "S5": s5}
