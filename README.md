---
license: cc-by-4.0
pretty_name: MVA Hackathon 2026 Track 1/2 pipelines
tags:
  - genomics
  - rare-disease
  - hackathon
  - variant-interpretation
  - drug-repurposing
library_name: mva_hackathon
---

# Rare Disease, Real Kid: MVA Hackathon 2026

Code for [SageBio/rare-disease-real-kid-mva-hackathon-2026](https://huggingface.co/spaces/SageBio/rare-disease-real-kid-mva-hackathon-2026).

- **HF user:** [Ryukijano](https://huggingface.co/Ryukijano)
- **GitHub (submit-form URL, private during the hackathon):** https://github.com/Ryukijano/mva-hackathon-2026
- **Track 1:** causal compound-het call in *BUB1B* — methods in `submissions/Ryukijano_track1_report.md`
- **Track 2:** mechanism-guided approved-drug repurposing (ChEMBL target-first screen, not TxGNN)
- **Campaign wrap-up:** [`WHAT_WE_DID.md`](WHAT_WE_DID.md)

This Hub repo contains **code, configs, tests, ranked findings, and the Track 2 dossier**. It does **not** contain the gated genome, FASTQs, VEP caches, or the clinical phenotype source file.

**AI assistance disclosure (28 Aug 2026 update):** Anthropic API / Cursor agents (Claude, Grok), commercial terms, no training on customer content.

## Track 1 finding

`submissions/Ryukijano_bub1b-compoundhet.csv`

| Allele | GRCh38 | HGVS (NM_001211.6) | Evidence |
|---|---|---|---|
| 1 | `chr15:40209701 T>G` | `c.2210T>G` `p.Leu737Ter` | ClinVar [VCV000533901](https://www.ncbi.nlm.nih.gov/clinvar/variation/533901/) Pathogenic for MVA1 |
| 2 | `chr15:40220612 T>G` | `c.3006T>G` `p.Asn1002Lys` | Novel C-lobe **pseudokinase** missense; AlphaMissense 0.9229 likely_pathogenic; ESM-1v predicts a mild, chemically conservative substitution; absent from gnomAD; located near the L1012P literature position — nearby MVA1 pseudokinase missenses destabilise BUBR1 (Suijkerbuijk 2010) — but not shown to destabilise itself and not functionally equivalent to L1012P |

EPCR `0.95`, `finding_type=primary`. Architecture is the classic viable MVA1 pattern (truncating + hypomorphic missense). *In trans* is inferred from the biallelic MVA1 architecture, not from a parental BAM.

## Project layout

```
configs/                 # Gene panel, scoring thresholds, AIRE paths
src/mva_hackathon/
  data/                  # Gated HF download helper + phenotype parser
  variants/              # VEP parse, rare/panel filter, score, pair, CSV writer
  eval/                  # Local clone of the published Track 1 scorer
scripts/                 # CLI + AIRE Slurm wrappers
experiments/             # ESM-1v, PrimeKG skip-gram, ClinVar B/LB — start at experiments/2026-08-31_bub1b_computational/SUMMARY.md
track2/                  # ChEMBL screen, ranked candidates, report, pitch storyboard
submissions/             # Track 1 CSV (findings only; no genome)
tests/
```

## Pipeline (Track 1)

1. Download only the WGS VCF + TBI + phenotype docx from `SageBio/mva-hackathon-2026-data` (gated).
2. Annotate with Ensembl VEP **116** (GRCh38, offline) + AlphaMissense + popEVE plugins.
3. Filter to the 15-gene MVA SAC/centrosome panel, relevant SO terms, gnomAD AF ≤ 0.001 or absent.
4. SpliceAI on the tiny candidate VCF (`-D 500`).
5. Score: PTV ≈ 0.99; missense = 0.7·popEVE-sigmoid + 0.3·AlphaMissense (AM fallback if popEVE missing, e.g. novel N1002K); splice = max SpliceAI Δ. The VEP popEVE field is now `popEVE_SCORE` with `popEVE`/`popEVE_pop_adjusted_EVE` fallbacks; the sigmoid has been corrected so more-negative scores map to higher pathogenicity.
6. Pair all combinations of alleles in the same gene; pair score = product; write ≤10 CSV rows with EPCR in (0, 1].
7. Local scorer clone (`pytest tests/test_scorer.py`) before burning Track 1 quota (max 6).

## Pipeline (Track 2)

Target-first ChEMBL screen (`track2/drug_screen.py`) on the BUB1B-hypomorph axis (SIRT2/NAD+, FKBP1A/mTOR, Nrf2/ROS, JAK/IL-6, plus anti-targets TTK/AURKB/STING). Use `track2/drug_screen.py --approved-only` to retrieve only approved drugs (ChEMBL `max_phase=4`). Ranked proposal in `track2/track2_report.md`; pitch storyboard in `track2/pitch_storyboard.md`.

Because the disease is **hypomorphic residual BUBR1**, the strategy is dual-pronged: **(1) restore full-length protein from the stop-gain allele**, **(2) stabilise residual BUBR1**, then blunt downstream proteotoxic / lysosomal / mito / IFN load without rescuing aneuploid cells. TTK, Aurora B, and STING **agonists** are excluded (wrong direction). The revised lead stack is:

1. **Tier 1a:** Ataluren (PTC124) — UGA stop-codon readthrough of `p.Leu737Ter`; conditional UK/MHRA authorisation for nonsense DMD, not FDA or EMA approved. ELX-02 is investigational/future.
2. **Tier 1b:** NMN / nicotinamide riboside — SIRT2/BUBR1 K668 protein-stabilisation hypothesis; supplements, not approved medications.
3. **Tier 2a:** Glycerol phenylbutyrate (Ravicti; sodium-free 4-PBA prodrug) — proteostasis chaperone extrapolated from 4-PBA in trisomy iPSC neurons; FDA/EMA approved for urea-cycle disorders.
4. **Tier 2b:** Arimoclomol — HSF1/HSP and lysosomal function (cancer caveat); FDA-approved for Niemann-Pick C, EMA refused.
5. **Tier 2c:** Trehalose / spermidine — mTORC1-independent TFEB/autophagy-lysosome induction hypotheses; supplements/food, not approved medications.
6. **Tier 2d:** Rapamycin (sirolimus) — exploratory mTORC1/FKBP supportive hit from the L2S2/L1000CDS2 screen (one FDR-significant reverse signature, but a mimic in several other MVA contexts); everolimus had no significant reverse signal. NAC/MitoQ/omaveloxolone are hypothesis-only, with explicit cancer/metastasis warnings.
7. **Tier 3:** Baricitinib / ruxolitinib / tocilizumab — biomarker-gated JAK/IL-6 blockade with oncology surveillance.

## Setup (AIRE / local)

```bash
# AIRE
source /scratch/kcwp264/.aire_scratch_env.sh
module load miniforge/24.7.1
conda env create -f environment.yaml
conda activate mva-hackathon   # or: conda activate /mnt/scratch/kcwp264/.conda_envs/mva-hackathon
pip install -e .
```

Challenge data is gated. After accepting the DTA:

```bash
export HF_TOKEN=...
python scripts/download_data.py
bash scripts/setup_references.sh
python scripts/run_track1.py \
  --vcf data/WGS_EX2312012_HGWCNDSX7.vcf.gz \
  --pheno data/Challenge_Clinical_Phenotype_1.docx \
  -o submissions/Ryukijano_bub1b-compoundhet.csv
python -m pytest tests/test_scorer.py
```

## Data handling

- Genome / BAM / VCF / genotype-scale tables stay off this repo and must be deleted within 30 days of hackathon close.
- Ranked variant list, gene rankings, code, and reports may remain (CC BY 4.0).
- Do not paste genome-scale files into third-party LLM APIs unless the provider is a processor (no training on inputs). See [discussion #2](https://huggingface.co/spaces/SageBio/rare-disease-real-kid-mva-hackathon-2026/discussions/2).

## Licence

Code and reports: [CC BY 4.0](LICENSE). Underlying patient data: gated; not redistributable.
