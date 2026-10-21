# MVA Hackathon 2026 — agent brief

Use skill **`mva-hackathon`** at `.agents/skills/mva-hackathon/`. On any AlphaGenome / AVI / Atlas / BUB1B-effect request, load that skill first. It always reads the three AlphaGenome skills plus `bub1b-contract.md`.

- Repo: `/scratch/kcwp264/mva-hackathon-2026` → GitHub `Ryukijano/mva-hackathon-2026` (public)
- Close: 24 Oct 2026 23:59 UTC. Track 1: **1/6 shots spent (12 Sep 2026 — full match at rank 1, 100/100 pts, F-max 1.000)**. Track 2: 3 shots, `video_url` required (pitch video rendered in `video/`).
- Envs: `mva-hackathon` (VEP 116), `cjepa` (ESM-1v), `mva-hackathon-lincs`
- Source `/scratch/kcwp264/.aire_scratch_env.sh`. Genome/VCF/FASTQ stay on scratch — never paste into LLM APIs.
- Status: `WHAT_WE_DID.md`, `docs/next_plan.md`, `docs/structure_and_plm_addendum_2026-10-11.md`. Tests: `pytest tests/` (39).
- Do not upload to the Space or record the pitch unless the user asks.
