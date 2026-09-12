---
name: mva-hackathon
description: >-
  MVA Hackathon 2026 agent for SageBio Rare Disease, Real Kid. Loads the three
  AlphaGenome skills plus the BUB1B variant contract. Use when working in
  mva-hackathon-2026, scoring BUB1B/MVA1 alleles, building Atlas links, drafting
  Track 1/2 reports, or the user mentions MVA, BUB1B, L737Ter, N1002K, or
  /alphagenome in this campaign.
---

# MVA Hackathon 2026

Repo: `/scratch/kcwp264/mva-hackathon-2026` (GitHub `Ryukijano/mva-hackathon-2026`).
Close: **24 Oct 2026 23:59 UTC**. Envs: `mva-hackathon` (VEP 116), `cjepa` (ESM-1v), `mva-hackathon-lincs`.

## Mandatory first reads

Before any AlphaGenome, AVI, Atlas, splice, or variant-effect work, **Read** these in full:

1. `/users/kcwp264/.cursor/skills/alphagenome_variant_impact_score/SKILL.md`
2. `/users/kcwp264/.cursor/skills/alphagenome_single_variant_analysis/SKILL.md`
3. `/users/kcwp264/.cursor/skills/alphagenome_atlas_website_links/SKILL.md`
4. [bub1b-contract.md](bub1b-contract.md)

Then follow those skills (uv run, credentials protocol, Atlas deep-links, research-only framing).
Verify `ALPHAGENOME_API_KEY` with `grep -sq "^ALPHAGENOME_API_KEY=" ~/.env` — never print the value.
Source `/scratch/kcwp264/.aire_scratch_env.sh` before uv/HF. Prefer `--project` on the skill dir.

If `.licenses/alphagenome_single_variant_analysis_LICENSE.txt` is missing in the repo root, notify the user to check https://deepmind.google.com/science/alphagenome/ and create the file.

## Do not re-run unless asked

Canonical AVI is `supplement/track1/bub1b_avi_scores.json` (2026-09-10):

| Variant | Call | AVI Phred | Top modality |
|---|---|---|---|
| `chr15:40209701:T>G` | p.Leu737Ter | 33.76 | Protein Termination |
| `chr15:40220612:T>G` | p.Asn1002Lys | 25.61 | AlphaMissense |

AVI is **not** independent of AlphaMissense. Do not treat it as a clinical classification.
When discussing these scores, still emit Atlas deep-links (links skill).

## Hard rules

- Never paste genome / VCF / FASTQ / BAM into LLM APIs. Do not open Space ground truth.
- Never claim N1002K is L1012P-class (ESM-1v −0.110 vs −1.801).
- Never claim NMN produced the +58%/+123% lifespan (that is SIRT2-tg in *BubR1^H/H*).
- Never claim graph/AI/TxGNN discovered a therapy. TxGNN was never trained.
- Never call C-GQE / other campaigns a win here.
- Sirolimus is a **potential anti-target** (Bonatti 1998 aneugen; Baker 2013 diet note negative), not a rescue lead.
- Phasing is **UNRESOLVED** (WhatsHap). Submit as *presumed* compound-het. Do not re-run the 84 GB WGS pipeline.
- Track 1 Space upload and Track 2 video URL are **user decisions**. Do not upload.

## New AlphaGenome work

1. Use 1-based `chr15:40209701:T>G` and `chr15:40220612:T>G`.
2. Prefer biosamples fibroblasts / LCL / Whole_Blood over K562 unless asked.
3. For splicing views, always co-plot RNA-seq with splice tracks.
4. Write new artifacts under `supplement/track1/`; do not overwrite the canonical AVI JSON.
5. Frame outputs as predicted molecular/functional effects only.

## Pointers

- Status: `WHAT_WE_DID.md`, `docs/next_plan.md`, `docs/PROJECT_RECORD.md`
- Track 1 CSV/report: `submissions/Ryukijano_bub1b-compoundhet.csv`, `submissions/Ryukijano_track1_report.md`
- Track 2: `track2/track2_report.md`, `track2/pitch_storyboard.md`
- Tests: `pytest tests/` in env `mva-hackathon` (39 tests)
