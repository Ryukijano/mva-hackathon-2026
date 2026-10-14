"""Stage 4: QA gate for out/track2_pitch.mp4. Exits non-zero on any failure.

Checks: both streams <=180 s and in sync; 1080p30 h264/yuv420p + AAC;
disclaimer present on screen and in VO; must-keep claims present; no genomic
coordinates / nucleotide HGVS / sequence / rsIDs anywhere in rendered text,
the VO script, or timing.json; no "ataluren approved" style regressions.

    ~/.venvs/mva-video/bin/python video/qa.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

VIDEO = Path(__file__).resolve().parent
MP4 = VIDEO / "out" / "track2_pitch.mp4"
FFPROBE = "/scratch/kcwp264/conda/envs/endofm-lv/bin/ffprobe"
BUDGET = 180.0

FORBIDDEN = {
    "chrom coordinate": r"\bchr[\w]*:",
    "nucleotide HGVS": r"\b[cgmn]\.[-*]?\d",
    "assembly name": r"GRCh\d|hg19|hg38",
    "nucleotide run": r"[ACGTN]{8,}",
    "rsID": r"\brs\d{4,}",
    "comma coordinate": r"\d{1,3},\d{3},\d{3}",
    "long integer": r"\b\d{7,}\b",
    "proband identifier": r"\bEX\d{6,}",
    "WGS prefix": r"WGS_",
    "DNAnexus": r"DNAnexus",
    "GATK": r"GATK",
}
DISCLAIMER = ["Preclinical N-of-1 research proposal", "not clinical advice or a treatment recommendation"]
MUST_SHOW = ["p.Leu737Ter", "p.Asn1002Lys", "Amlexanox", "NMD", "Ataluren", "Ravicti", "2  Arimoclomol",
             "3  Metformin / rilmenidine", "Sirolimus", "674", "CC BY 4.0", "AlphaFold DB AF-O60566",
             "replayed from committed CSVs", "comparator", "single-donor", "Kokoro", "9 Oct 2026"]
BAD_CLAIMS = {
    "ataluren as FDA/EMA approved": r"(?i)ataluren[^.\n]{0,40}(fda|ema)[- /]*(approved)",
    "AI/graph discovered therapy": r"(?i)(ai|graph|model)[^.\n]{0,20}discover",
    "NMN lifespan claim": r"(?i)nmn[^.\n]{0,40}(lifespan|58%|123%)(?![^.\n]{0,40}not NMN)",
    "every lead": r"(?i)every lead",
    "classic viable": r"(?i)classic viable",
    "almost certainly": r"(?i)almost certainly",
    "outperformed": r"(?i)outperformed",
    "proven in trans": r"(?i)proven in trans",
    "resolved in trans": r"(?i)resolved in trans",
    "no decay activity": r"(?i)no decay activity",
    "EMA refused": r"(?i)EMA refus",
    "classic/known MVA1": r"(?i)(classic|known)[^.\n]{0,12}MVA1",
    "repo link on screen": r"github\.com/Ryukijano",
}


def probe():
    out = subprocess.run([FFPROBE, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(MP4)],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def main() -> int:
    fails, notes = [], []
    info = probe()
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next(s for s in info["streams"] if s["codec_type"] == "audio")
    dur_f, dur_v, dur_a = float(info["format"]["duration"]), float(v["duration"]), float(a["duration"])
    notes.append(f"duration format {dur_f:.3f} / video {dur_v:.3f} / audio {dur_a:.3f} s")
    for name, d in [("format", dur_f), ("video", dur_v), ("audio", dur_a)]:
        if d > BUDGET:
            fails.append(f"{name} duration {d:.3f} > {BUDGET}")
    if abs(dur_v - dur_a) > 0.1:
        fails.append(f"A/V length mismatch {dur_v - dur_a:+.3f} s")
    if (v["width"], v["height"]) != (1920, 1080):
        fails.append(f"resolution {v['width']}x{v['height']}")
    if v["codec_name"] != "h264" or v["pix_fmt"] != "yuv420p":
        fails.append(f"video codec {v['codec_name']}/{v['pix_fmt']}")
    if v["r_frame_rate"] != "30/1":
        fails.append(f"frame rate {v['r_frame_rate']}")
    if a["codec_name"] != "aac":
        fails.append(f"audio codec {a['codec_name']}")

    manifest = json.loads((VIDEO / "build" / "text_manifest.json").read_text())
    shown = "\n".join(manifest)
    script = (VIDEO / "script_vo.md").read_text()
    timing = (VIDEO / "timing.json").read_text()
    spoken = "\n".join(re.findall(r"```spoken\n(.*?)```", script, re.S))
    notes.append(f"{len(manifest)} distinct on-screen strings scanned")

    for label, pat in FORBIDDEN.items():
        for src_name, src in [("screen", shown), ("script", script), ("timing", timing)]:
            hits = sorted(set(m.group(0) for m in re.finditer(pat, src)))
            if hits:
                fails.append(f"forbidden {label} in {src_name}: {hits[:5]}")
    for label, pat in BAD_CLAIMS.items():
        for src_name, src in [("screen", shown), ("spoken", spoken)]:
            m = re.search(pat, src)
            if m:
                fails.append(f"claim regression '{label}' in {src_name}: {m.group(0)!r}")
    bad_glyphs = sorted({c for c in shown if ord(c) > 127 and c not in "µ·–—…−→≤"})
    if bad_glyphs:
        fails.append(f"glyphs missing from render font: {bad_glyphs}")
    for s in DISCLAIMER:
        if s not in shown:
            fails.append(f"disclaimer missing on screen: {s!r}")
    if "preclinical N-of-one research proposal, not clinical advice or a treatment recommendation" not in spoken:
        fails.append("disclaimer missing from VO")
    for s in MUST_SHOW:
        if not any(s in m for m in manifest):
            fails.append(f"must-show text missing: {s!r}")

    report = {"file": str(MP4.relative_to(VIDEO.parent)), "pass": not fails, "fails": fails, "notes": notes}
    (VIDEO / "build" / "qa_report.json").write_text(json.dumps(report, indent=2) + "\n")
    for n in notes:
        print("  ·", n)
    for f in fails:
        print("  FAIL", f)
    print("QA", "PASS" if not fails else f"FAIL ({len(fails)})")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
