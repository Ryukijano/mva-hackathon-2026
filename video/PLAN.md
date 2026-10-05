# Track 2 pitch video — production plan (2026-10-05)

Deliverable: 1080p, ≤180 s, unlisted YouTube/Vimeo URL for `submit_track2.py`
(required field). Submissions are CC BY 4.0. Deadline 24 Oct 2026 23:59 UTC;
record-lock target **17 Oct** so the 17–21 Oct regulatory re-check lands before
submission.

## Style decision

Programmatic motion graphics ("sick" = precision-animated, not stock-footage):
dark theme (#0d1117), kinetic typography, animated diagrams, PyMOL turntable
inserts, terminal capture. Fully reproducible from `video/` scripts — every
frame is generated, nothing hand-edited, so any claim text can be re-rendered
after the regulatory re-check.

**Audio-first pipeline.** TTS is generated first; scene durations are locked to
measured audio length + 0.4 s pad. Visuals are then rendered to fill each
segment exactly. This makes the 180 s budget a compile-time property.

## Hard constraint found: the VO script is too long

Current storyboard VO = **554 words ≈ 222–237 s @ ~140 wpm** — over budget.
Target script: **≤400 words** (~170 s) leaving ~8–10 s of visual breathing
room. Trimmed draft lives in `video/script_vo.md` (to be written; must keep:
the two-variant call, the NMD-gate rationale for amlexanox over ataluren, the
proteostasis tier order, the LINCS 0/2/674 firewall result, the anti-target
flag on sirolimus, and the disclaimer).

## Scene plan (~180 s)

| # | Time | Scene | Visuals (generated) | VO content |
|---|------|-------|--------------------|-----------|
| S0 | 0:00–0:06 | Title | "Rare Disease, Real Kid — MVA Hackathon 2026 · Ryukijano" + animated aneuploid motif (chromosomes splitting unevenly, abstract — no coordinates) | title only / music-free |
| S1 | 0:06–0:36 | The case | HPO phenotype card → BUBR1 domain bar draws in, star at L737Ter + star at C-lobe N1002K → stat chips (ClinVar P/LP, AlphaMissense 0.9229, ESM-1v LLR −0.110 "mild") | ~75 w: child phenotype, two ultra-rare alleles, viable-MVA1 architecture (null + hypomorph) |
| S2 | 0:36–1:18 | Mechanism | Animated SAC cascade: kinetochore → MCC latches APC/C (6TLJ turntable inset) → weak BUBR1 → premature release → aneuploid cell division → proteotoxic/ROS/micronuclei → cGAS-STING → IFN/IL-6; BUBR1 truncation turntable inset | ~110 w |
| S3 | 1:18–2:05 | The stack | Four-tier diagram assembles left→right: (1) UGA rescue — **amlexanox** highlighted, ataluren greyed "UK-conditional/not FDA", ELX-02 "investigational"; (2) SIRT2/NAD+ — NMN/NR tagged "supplement comparators"; (3) approved proteostasis — Ravicti, arimoclomol, metformin/rilmenidine; (4) red "anti-target" column — sirolimus struck through (aneugen note) | ~120 w |
| S4 | 2:05–2:45 | Evidence | Terminal window types `python track2/drug_screen.py --approved-only`; ChEMBL 92→32 funnel animates; LINCS firewall bar ACCEPT 0 / WEAK 2 / REJECT 674; ESM-1v LLR bar (N1002K −0.110 vs L1012P −1.801) | ~85 w |
| S5 | 2:45–3:00 | Close | Assay-gated validation flowchart pulses once → disclaimer card + repo URL + CC BY 4.0 | ~25 w: "assay-gated next steps" + disclaimer line |

Every scene gets a generated .wav first; scene length = wav length + pad.

## Assets

**Reuse (already committed):**
- `figures/out/*.png` — domain map, C-lobe zoom, complexes, mechanism schematic
- `experiments/.../figures/fig1..5` — ESM-1v/PrimeKG charts (restyle dark for video)
- `figures/structures/` — AF-O60566, 6TLJ, 5JJA, 3SI5 cifs

**Generate (new, under `video/`):**
- `video/tts/*.wav` — Kokoro-82M (Apache-2.0, HF `hexgrad/Kokoro-82M`) via a
  `mva-video` uv venv; fallback piper. Per-scene wavs, silence-trimmed,
  durations measured → `video/timing.json`.
- `video/render/*.py` — scene renderers writing 1920×1080 PNG frames at 30 fps
  (PIL + matplotlib; EasingCurves lib-free). PyMOL turntables re-rendered as
  PNG sequences via existing `render_gif_frames.py` pattern (uv run,
  pymol-open-source-whl; 96–144 frames each, mild ray or flat cartoon).
- `video/assemble.sh` — ffmpeg: per-scene concat → xfade transitions (0.4 s
  fades) → VO mux → `loudnorm` → h264/yuv420p/1080p30 → `out/track2_pitch.mp4`.
- `video/qa.py` — asserts: duration ≤180 s, resolution, disclaimer text present
  in last scene, and **no genomic coordinate strings** in any rendered text
  layer (scan a per-scene text manifest; also no `chr15:` strings in assets).

## Content rules baked in

- No genomic coordinates, FASTQ/VCF content, or sequence in any frame —
  variants shown as protein-level only (`p.Leu737Ter`, `p.Asn1002Lys`, domain
  positions 737/1002 on the domain bar are protein residues, which is fine).
- Disclaimer on closing card + VO: "Preclinical N-of-1 research proposal, not
  clinical advice or a treatment recommendation."
- Claims to keep verbatim-true: NMD gate before readthrough; ataluren not
  FDA/EMA-approved; NMN ≠ the +58%/+123% lifespan result (SIRT2-tg); LINCS
  sirolimus = exploratory WEAK/MIXED + aneugen flag, not a rescue lead; no
  "AI/graph discovered the therapy".

## Compute/env

- Everything CPU-feasible; PyMOL turntable renders ~minutes each — run under
  Slurm `nodes` partition or login-node-safe since they are short.
- New env `mva-video` (uv venv on scratch): kokoro, onnxruntime or torch,
  pillow, matplotlib, numpy; ffmpeg reused from `cjepa`.
- `video/` committed (scripts + script_vo.md); `video/render/frames/`,
  `video/tts/*.wav`, and `out/*.mp4` gitignored (binary artifacts).

## Risks / open questions

1. **Kokoro voice quality** — acceptable but synthetic; if it reads badly we
   swap to your recorded VO without pipeline changes (audio-first means the
   timing just re-locks).
2. **TTS install size** (~300–500 MB model + voices on scratch) — fine.
3. **Manim not used** — cairo exists but matplotlib/PIL frame-gen is more
   predictable headless; same visual family.
4. Optional ambient pad — skipped unless you want it (keeps licensing simple).

## Sequence to ship

1. `script_vo.md` (≤400 w) — your sign-off
2. TTS wavs → `timing.json` → adjust scene beats
3. Scene renderers S0–S5 → assemble → QA → first full draft mp4
4. Your review pass on the draft (text accuracy, pacing)
5. 17–21 Oct: regulatory re-check → re-render affected text if needed →
   upload unlisted → `video_url` into Track 2 submission

## Build status (2026-10-05) — first draft pipeline implemented

How to rebuild (all scripts in `video/`, outputs gitignored):

```bash
# once: dark-theme PyMOL turntables -> video/build/turn_*.npz (Slurm nodes; ~10 min for 6TLJ)
srun -p nodes -c 16 --mem 24G -t 40 bash -c 'UV_CACHE_DIR=$HOME/.cache/uv-mva-video uv run video/render/turntables.py'
# every edit: TTS -> timing.json -> frames -> mux -> QA (~2 min)
video/make.sh            # SPEED=1.05 VOICE=af_heart WORKERS=14 overridable
```

| Stage | File | Output |
|---|---|---|
| VO | `tts.py` (Kokoro-82M ONNX, `af_heart`, speed 1.05) | `tts/S*.wav`, `timing.json` (scene start/dur + per-line cue onsets) |
| Frames | `render/{common,scenes,render}.py` | raw RGB piped to x264 in parallel chunks → `build/video.mp4`; numpy VO mixdown → `build/vo_mix.wav`; `build/text_manifest.json` |
| Mux | `assemble.sh` | `out/track2_pitch.mp4` (loudnorm −16 LUFS, AAC 48 kHz, faststart) |
| QA | `qa.py` | `build/qa_report.json`; fails on >180 s, A/V drift, non-1080p30, missing disclaimer/claims, any coordinate/HGVS/sequence/rsID string |

Deviations from the plan above (deliberate):
- **Env lives in `$HOME/.venvs/mva-video`**, not scratch: scratch hit its 1.5M inode
  hard cap on 2026-10-05. Kokoro model files in `~/.cache/kokoro/`; uv cache for this env in `~/.cache/uv-mva-video`.
- **ffmpeg = `endofm-lv`** build (has libx264); the `cjepa` build has no libx264.
- **No PNG frame dirs**: frames are streamed to ffmpeg (inode cap). Crossfades are done in Python on a single
  global timeline, so there is no ffmpeg `xfade` and no `-shortest`.
- **Pronunciation**: Kokoro spells out ALL-CAPS syllables, so the spoken text uses plain/lowercase respellings
  (`am-lexanox`, `chembl`, `en-ay-dee`, `bub-R-one`).
- **Script accuracy fixes vs storyboard**: N1002K is not called "novel" (the same protein change is a ClinVar VUS
  via a different nucleotide change); the LINCS 0/2/674 result is over human MVA *and* BubR1-hypomorph mouse
  contrasts, not "the human signature"; "recurrent miscarriage" dropped from the phenotype card (it is not a
  phenotype of the child; source docx not in repo).

Still open: user review of `script_vo.md` + draft mp4 · 17–21 Oct regulatory re-check
(ataluren/MHRA, arimoclomol/EMA re-examination) · upload unlisted · `video_url`.
