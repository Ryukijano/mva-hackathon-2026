"""Stage 2: timing.json -> build/video.mp4 + build/vo_mix.wav + build/text_manifest.json.

Frames are piped as raw RGB into ffmpeg (no PNGs on disk: scratch inode cap).
The timeline is rendered in parallel chunks, then concatenated losslessly.

    ~/.venvs/mva-video/bin/python video/render/render.py [--workers 12]
    ~/.venvs/mva-video/bin/python video/render/render.py --stills S1:5,S1:30   # preview PNGs
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from scenes import SCENES  # noqa: E402

VIDEO = Path(__file__).resolve().parents[1]
BUILD = VIDEO / "build"
FFMPEG = os.environ.get("FFMPEG", "/scratch/kcwp264/conda/envs/endofm-lv/bin/ffmpeg")
TIMING = json.loads((VIDEO / "timing.json").read_text())
FPS = TIMING["fps"]
SC = TIMING["scenes"]
XF = TIMING["xfade"]
TOTAL = TIMING["total"]
NFRAMES = int(round(TOTAL * FPS))


def scene_img(i: int, T: float) -> Image.Image:
    sc = SC[i]
    return SCENES[sc["id"]](T - sc["start"], sc)


def frame(f: int) -> Image.Image:
    T = f / FPS
    i = max(k for k, s in enumerate(SC) if s["start"] <= T + 1e-9)
    im = scene_img(i, T)
    # crossfade centred on each cut
    if i + 1 < len(SC) and T > SC[i + 1]["start"] - XF / 2:
        a = (T - (SC[i + 1]["start"] - XF / 2)) / XF
        im = Image.blend(im, scene_img(i + 1, T), common.ease_io(a))
    elif i > 0 and T < SC[i]["start"] + XF / 2:
        a = (T - (SC[i]["start"] - XF / 2)) / XF
        im = Image.blend(scene_img(i - 1, T), im, common.ease_io(a))
    # global fade in/out
    g = min(common.clamp(T / 0.5), common.clamp((TOTAL - T) / 0.6))
    if g < 1:
        im = Image.blend(Image.new("RGB", im.size, common.BG), im, g)
    # progress hairline
    d = ImageDraw.Draw(im)
    d.rectangle([0, 1076, int(1920 * T / TOTAL), 1079], fill=common.mix(common.BG, common.BLUE, 0.7))
    return im


def render_chunk(args):
    k, f0, f1 = args
    out = BUILD / f"chunk_{k:03d}.mp4"
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-tune", "animation",
           "-pix_fmt", "yuv420p", "-threads", "2", "-g", str(FPS * 2), str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(f0, f1):
        p.stdin.write(frame(f).tobytes())
    p.stdin.close()
    assert p.wait() == 0, f"ffmpeg failed on chunk {k}"
    return k, sorted(common.MANIFEST)


def mix_audio():
    n = int(round(NFRAMES / FPS * TIMING["sr"]))
    buf = np.zeros(n, dtype=np.float32)
    for s in SC:
        if not s["wav"]:
            continue
        x, sr = sf.read(VIDEO / s["wav"], dtype="float32")
        assert sr == TIMING["sr"]
        o = int(round(s["vo_start"] * sr))
        buf[o:o + len(x)] += x[: max(0, n - o)]
    sf.write(BUILD / "vo_mix.wav", buf, TIMING["sr"], subtype="PCM_16")
    return len(buf) / TIMING["sr"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--chunk", type=int, default=180)
    ap.add_argument("--until", type=float, default=None, help="render only the first N seconds (smoke test)")
    ap.add_argument("--stills", default="", help="comma list of SCENE:seconds -> build/still_*.png")
    args = ap.parse_args()
    BUILD.mkdir(exist_ok=True)

    if args.stills:
        for spec in args.stills.split(","):
            sid, ts = spec.split(":")
            i = next(k for k, s in enumerate(SC) if s["id"] == sid)
            SCENES[sid](float(ts), SC[i]).save(BUILD / f"still_{sid}_{float(ts):05.1f}.png")
        print("stills ->", BUILD)
        return

    global NFRAMES
    if args.until:
        NFRAMES = min(NFRAMES, int(round(args.until * FPS)))
    jobs = [(k, f0, min(f0 + args.chunk, NFRAMES)) for k, f0 in enumerate(range(0, NFRAMES, args.chunk))]
    manifest = set()
    with Pool(args.workers) as pool:
        for k, strings in tqdm(pool.imap_unordered(render_chunk, jobs), total=len(jobs), desc="render chunks"):
            manifest.update(strings)
    lst = BUILD / "chunks.txt"
    lst.write_text("".join(f"file 'chunk_{k:03d}.mp4'\n" for k, _, _ in jobs))
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    str(BUILD / "video.mp4")], check=True)
    for k, _, _ in jobs:
        (BUILD / f"chunk_{k:03d}.mp4").unlink()
    lst.unlink()
    adur = mix_audio()
    (BUILD / "text_manifest.json").write_text(json.dumps(sorted(manifest), indent=1, ensure_ascii=False) + "\n")
    print(f"video {NFRAMES} frames = {NFRAMES / FPS:.3f} s · audio {adur:.3f} s · {len(manifest)} strings")


if __name__ == "__main__":
    main()
