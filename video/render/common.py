"""Drawing kit for the pitch video: palette, fonts, easing, shapes, logged text.

All public helpers take 1920x1080 coordinates; frames are drawn at SS x that
size and box-reduced, which gives anti-aliased shapes from plain ImageDraw.
Every string drawn goes through `Canvas.text`, which records it in MANIFEST so
qa.py can scan all rendered text for forbidden content.
"""
from __future__ import annotations

import math
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
SS = 2
FPS = 30

BG = (13, 17, 23)          # #0d1117
PANEL = (22, 27, 34)       # #161b22
PANEL2 = (28, 35, 45)
BORDER = (48, 54, 61)      # #30363d
TEXT = (230, 237, 243)     # #e6edf3
MUTED = (139, 148, 158)    # #8b949e
FAINT = (88, 96, 105)
BLUE = (88, 166, 255)      # #58a6ff
GREEN = (63, 185, 80)      # #3fb950
AMBER = (210, 153, 34)     # #d29922
RED = (248, 81, 73)        # #f85149
MAGENTA = (219, 97, 162)   # #db61a2
PURPLE = (163, 113, 247)   # #a371f7
YELLOW = (250, 204, 77)

MONT = "/usr/share/fonts/julietaula-montserrat/Montserrat-{}.otf"
MONO = "/usr/share/fonts/adobe-source-code-pro/SourceCodePro-{}.otf"

MANIFEST: set[str] = set()


@lru_cache(maxsize=256)
def font(size: float, weight: str = "Medium", mono: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype((MONO if mono else MONT).format(weight), int(round(size * SS)))


# ---------------------------------------------------------------- timing ----
def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if x < lo else hi if x > hi else x


def prog(t: float, t0: float, dur: float = 0.6) -> float:
    return clamp((t - t0) / dur) if dur > 0 else float(t >= t0)


def ease(x: float) -> float:            # ease-out cubic
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_io(x: float) -> float:         # ease-in-out cubic
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def back(x: float, s: float = 1.6) -> float:   # overshoot pop
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def mix(a, b, k: float):
    k = clamp(k)
    return tuple(int(round(a[i] + (b[i] - a[i]) * k)) for i in range(3))


# ---------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, bg=BG):
        self.bg = bg
        self.im = Image.new("RGB", (W * SS, H * SS), bg)
        self.d = ImageDraw.Draw(self.im)

    @staticmethod
    def s(v):
        return v * SS

    def col(self, c, a: float, under=None):
        return mix(under or self.bg, c, a)

    def rect(self, box, fill=None, outline=None, width=2, r=14, a=1.0, under=None):
        if a <= 0:
            return
        x0, y0, x1, y1 = box
        self.d.rounded_rectangle(
            [x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=r * SS,
            fill=None if fill is None else self.col(fill, a, under),
            outline=None if outline is None else self.col(outline, a, under),
            width=int(width * SS))

    def line(self, pts, color, width=3, a=1.0, under=None):
        if a <= 0:
            return
        self.d.line([(x * SS, y * SS) for x, y in pts], fill=self.col(color, a, under),
                    width=int(width * SS), joint="curve")

    def circle(self, cx, cy, r, fill=None, outline=None, width=2, a=1.0, under=None):
        if a <= 0 or r <= 0:
            return
        self.d.ellipse([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS],
                       fill=None if fill is None else self.col(fill, a, under),
                       outline=None if outline is None else self.col(outline, a, under),
                       width=int(width * SS))

    def poly(self, pts, fill, a=1.0, under=None):
        if a <= 0:
            return
        self.d.polygon([(x * SS, y * SS) for x, y in pts], fill=self.col(fill, a, under))

    def text(self, xy, s: str, size=28, weight="Medium", color=TEXT, a=1.0, anchor="la",
             mono=False, under=None, dy=0.0) -> float:
        """Draw text; returns its width in 1080p px. Logged to MANIFEST."""
        if not s:
            return 0.0
        MANIFEST.add(s)
        f = font(size, weight, mono)
        if a > 0:
            self.d.text((xy[0] * SS, (xy[1] + dy) * SS), s, font=f, fill=self.col(color, a, under),
                        anchor=anchor)
        return self.d.textlength(s, font=f) / SS

    def textw(self, s, size=28, weight="Medium", mono=False) -> float:
        return self.d.textlength(s, font=font(size, weight, mono)) / SS

    def wrap(self, s, maxw, size=28, weight="Medium"):
        out, cur = [], ""
        for w in s.split():
            trial = (cur + " " + w).strip()
            if self.textw(trial, size, weight) <= maxw or not cur:
                cur = trial
            else:
                out.append(cur)
                cur = w
        return out + ([cur] if cur else [])

    def para(self, xy, s, maxw, size=26, weight="Medium", color=TEXT, a=1.0, lh=1.32, under=None):
        x, y = xy
        for i, ln in enumerate(self.wrap(s, maxw, size, weight)):
            self.text((x, y + i * size * lh), ln, size, weight, color, a, under=under)
        return len(self.wrap(s, maxw, size, weight)) * size * lh

    def paste(self, img: Image.Image, xy, a=1.0, size=None):
        """Paste an RGB image (1080p units) with uniform opacity."""
        if a <= 0:
            return
        sz = size or img.size
        im = img.resize((int(sz[0] * SS), int(sz[1] * SS)), Image.BILINEAR)
        x, y = int(xy[0] * SS), int(xy[1] * SS)
        if a >= 1:
            self.im.paste(im, (x, y))
        else:
            base = self.im.crop((x, y, x + im.width, y + im.height))
            self.im.paste(Image.blend(base, im, a), (x, y))

    # -------------------------------------------------------- components ----
    def arrow(self, p0, p1, color=MUTED, width=3, k=1.0, head=13, a=1.0, under=None):
        if k <= 0 or a <= 0:
            return
        x0, y0 = p0
        x1 = x0 + (p1[0] - x0) * k
        y1 = y0 + (p1[1] - y0) * k
        ang = math.atan2(y1 - y0, x1 - x0)
        hx, hy = x1 - head * 0.8 * math.cos(ang), y1 - head * 0.8 * math.sin(ang)
        self.line([(x0, y0), (hx, hy)], color, width, a, under)
        self.poly([(x1, y1),
                   (x1 - head * math.cos(ang - 0.45), y1 - head * math.sin(ang - 0.45)),
                   (x1 - head * math.cos(ang + 0.45), y1 - head * math.sin(ang + 0.45))],
                  color, a, under)

    def star(self, cx, cy, r, color, a=1.0, under=None, rot=0.0):
        pts = []
        for i in range(10):
            rr = r if i % 2 == 0 else r * 0.45
            th = -math.pi / 2 + i * math.pi / 5 + rot
            pts.append((cx + rr * math.cos(th), cy + rr * math.sin(th)))
        self.poly(pts, color, a, under)

    def check(self, cx, cy, r, color, a=1.0, under=None):
        self.line([(cx - r * 0.55, cy), (cx - r * 0.12, cy + r * 0.45), (cx + r * 0.6, cy - r * 0.5)],
                  color, max(3, r * 0.28), a, under)

    def cross(self, cx, cy, r, color, a=1.0, under=None):
        w = max(3, r * 0.26)
        self.line([(cx - r * .5, cy - r * .5), (cx + r * .5, cy + r * .5)], color, w, a, under)
        self.line([(cx - r * .5, cy + r * .5), (cx + r * .5, cy - r * .5)], color, w, a, under)

    def badge(self, cx, cy, n, color, r=20, a=1.0, under=None):
        self.circle(cx, cy, r, fill=color, a=a, under=under)
        self.text((cx, cy + 1), str(n), r * 1.15, "Bold", BG, a, anchor="mm", under=color if a >= 1 else under)

    def chip(self, xy, s, size=22, fg=TEXT, fill=PANEL2, outline=None, a=1.0, pad=(14, 8),
             weight="SemiBold", under=None, dot=None) -> float:
        """Rounded pill; returns its width."""
        tw = self.textw(s, size, weight)
        dx = (size * 0.9 if dot else 0)
        w = tw + 2 * pad[0] + dx
        h = size + 2 * pad[1]
        x, y = xy
        self.rect((x, y, x + w, y + h), fill=fill, outline=outline, width=2, r=h / 2, a=a, under=under)
        if dot:
            self.circle(x + pad[0] + size * 0.3, y + h / 2, size * 0.24, fill=dot, a=a, under=fill)
        self.text((x + pad[0] + dx, y + h / 2), s, size, weight, fg, a, anchor="lm", under=fill)
        return w

    def header(self, num: str, title: str, a=1.0, accent=BLUE):
        self.rect((100, 62, 106, 104), fill=accent, r=3, a=a)
        self.text((124, 83), num, 24, "Bold", accent, a, anchor="lm")
        self.text((124 + self.textw(num, 24, "Bold") + 16, 83), title.upper(), 24, "SemiBold", MUTED, a,
                  anchor="lm")

    def footer(self, a=1.0):
        self.text((1820, 1032), "MVA Hackathon 2026 · Track 2 · Ryukijano", 18, "Medium", FAINT, a,
                  anchor="rm")

    def done(self) -> Image.Image:
        return self.im.reduce(SS)


def appear(t, t0, dur=0.5, rise=18):
    """(alpha, y-offset) for a fade-up entrance starting at t0."""
    k = ease(prog(t, t0, dur))
    return k, (1 - k) * rise
