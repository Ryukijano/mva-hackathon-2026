"""Stage 1 of the pitch pipeline: script_vo.md -> per-scene WAVs -> timing.json.

Audio-first: scene durations are derived from measured VO length, so the
180 s budget is checked here before any frame is rendered.

Run with the mva-video venv (kokoro-onnx):
    ~/.venvs/mva-video/bin/python video/tts.py [--voice af_heart] [--speed 1.0]
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import soundfile as sf
from tqdm import tqdm

VIDEO = Path(__file__).resolve().parent
SCRIPT = VIDEO / "script_vo.md"
TTS_DIR = VIDEO / "tts"
TIMING = VIDEO / "timing.json"
MODEL_DIR = Path.home() / ".cache" / "kokoro"

SR = 24_000
LINE_GAP = 0.28        # silence between script lines inside a scene
LEAD = 0.35            # scene start -> VO start
TAIL = 0.50            # VO end -> scene end (crossfade 0.4 s centred on the cut)
XFADE = 0.40
TITLE_DUR = 4.0        # S0 has no VO
CLOSE_HOLD = 2.0       # extra hold on the disclaimer card
BUDGET = 180.0

SCENE_RE = re.compile(r"^## (S\d) — (.+?)$(.*?)(?=^## S\d|\Z)", re.M | re.S)
SPOKEN_RE = re.compile(r"```spoken\n(.*?)```", re.S)


def parse_script(path: Path = SCRIPT) -> list[dict]:
    scenes = []
    for sid, title, body in SCENE_RE.findall(path.read_text()):
        m = SPOKEN_RE.search(body)
        lines = [ln.strip() for ln in (m.group(1) if m else "").splitlines() if ln.strip()]
        scenes.append({"id": sid, "title": title.strip(), "lines": lines})
    return scenes


def trim(x: np.ndarray, thresh: float = 0.01, keep: float = 0.03) -> np.ndarray:
    idx = np.flatnonzero(np.abs(x) > thresh)
    if idx.size == 0:
        return x[:0]
    k = int(keep * SR)
    return x[max(idx[0] - k, 0): idx[-1] + k]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default="af_heart")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--lang", default="en-us")
    args = ap.parse_args()

    from kokoro_onnx import Kokoro

    kok = Kokoro(str(MODEL_DIR / "kokoro-v1.0.onnx"), str(MODEL_DIR / "voices-v1.0.bin"))
    TTS_DIR.mkdir(exist_ok=True)
    scenes = parse_script()
    gap = np.zeros(int(LINE_GAP * SR), dtype=np.float32)

    t = 0.0
    out = []
    for sc in tqdm(scenes, desc="tts scenes"):
        if sc["lines"]:
            parts, cues, n = [], [], 0
            for ln in sc["lines"]:
                audio, sr = kok.create(ln, voice=args.voice, speed=args.speed, lang=args.lang)
                assert sr == SR, sr
                seg = trim(audio.astype(np.float32))
                cues.append(round(LEAD + n / SR, 4))   # line onset, scene-local seconds
                n += len(seg) + len(gap)
                parts += [seg, gap]
            wav = np.concatenate(parts[:-1])
            wav_path = TTS_DIR / f"{sc['id']}.wav"
            sf.write(wav_path, wav, SR, subtype="PCM_16")
            vo = len(wav) / SR
            dur = LEAD + vo + TAIL + (CLOSE_HOLD if sc is scenes[-1] else 0.0)
            vo_start = t + LEAD
        else:
            wav_path, vo, dur, vo_start, cues = None, 0.0, TITLE_DUR, None, []
        out.append({
            "id": sc["id"], "title": sc["title"], "start": round(t, 4), "dur": round(dur, 4),
            "vo_start": None if vo_start is None else round(vo_start, 4), "vo_dur": round(vo, 4),
            "wav": None if wav_path is None else str(wav_path.relative_to(VIDEO)),
            "words": sum(len(ln.split()) for ln in sc["lines"]), "cues": cues,
        })
        t += dur

    timing = {"fps": 30, "size": [1920, 1080], "sr": SR, "xfade": XFADE, "voice": args.voice,
              "speed": args.speed, "total": round(t, 4), "budget": BUDGET, "scenes": out}
    TIMING.write_text(json.dumps(timing, indent=2) + "\n")
    for s in out:
        print(f"{s['id']} {s['title']:<14} start {s['start']:7.2f}  dur {s['dur']:6.2f}  vo {s['vo_dur']:6.2f}  words {s['words']}")
    print(f"TOTAL {t:.2f} s (budget {BUDGET}) -> {'OK' if t <= BUDGET else 'OVER BUDGET'}")


if __name__ == "__main__":
    main()
