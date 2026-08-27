# Rare Disease, Real Kid: MVA Hackathon 2026

Track 1 (causal variant / compound-het hunt) and Track 2 (computational drug repurposing) pipeline for the Mosaic Variegated Aneuploidy (MVA) hackathon.

## Project layout

```
/mnt/scratch/kcwp264/mva-hackathon-2026/
├── configs/                 # Gene panel and AIRE paths
├── data/                    # Challenge data (gated HF data)
├── refs/                    # Reference annotations and caches
├── src/mva_hackathon/       # Python modules
│   ├── data/                # HF download + phenotype parsing
│   ├── variants/            # VCF filter, scoring, pairing, CSV writer
│   ├── eval/                # Local CAGI6/MVA scorer clone
│   └── drug/                # Track 2 repurposing (TxGNN/PrimeKG)
├── scripts/                 # CLI entrypoints
├── scripts/slurm/           # AIRE batch scripts
└── tests/
```

## Strategy summary

### Track 1: causal variant / compound-het

1. Download only `WGS_EX2312012_HGWCNDSX7.vcf.gz` + `.tbi` and the clinical docx from `SageBio/mva-hackathon-2026-data` (gated; needs HF token + rules acceptance).
2. Annotate with Ensembl VEP (GRCh38, offline cache) + plugins:
   - `AlphaMissense` (precomputed TSV)
   - `EVE`/`popEVE` (precomputed VCF)
3. Run SpliceAI locally on the filtered candidate set (MVA panel only) with a GRCh38 FASTA.
4. Filter to rare variants (gnomAD AF < 0.001 or absent) in the MVA mitotic/centrosomal/SAC gene panel.
5. Score and pair:
   - missense: popEVE (severe < -5.056) + AlphaMissense pathogenicity
   - splice: SpliceAI delta (max of DS_*)
   - PTV: near-1 pathogenicity
   - compound-het rows = top two damaging variants in the same gene
6. Convert to EPCR in (0,1] and write the official CSV template.
7. Validate with a local scorer clone before each of the 6 quota submissions.

### Track 2: drug repurposing

1. Use the Track 1 causal gene and HPO phenotype pool to condition a knowledge-graph model.
2. Restrict to biologically plausible rescue axes from the 2026 *Nat. Commun.* proteostasis paper (ROS scavengers, mitochondrial/heat-shock chaperones, autophagy/mTOR, apoptosis blockade).
3. Query TxGNN/PrimeKG for approved drugs and produce mechanistic GraphMask-style explanations.

## AIRE setup

```bash
source /scratch/kcwp264/.aire_scratch_env.sh
module load miniforge/24.7.1
conda env create -f environment.yaml
conda activate mva-hackathon
pip install -e .
```

Reference data (VEP cache, GRCh38 FASTA, AlphaMissense, popEVE, SpliceAI model) is staged under `refs/` on `$SCRATCH`.

## Track 1 quick run (after HF access)

```bash
export HF_TOKEN=...
python scripts/download_data.py
bash scripts/setup_references.sh
python scripts/run_track1.py --vcf data/WGS_EX2312012_HGWCNDSX7.vcf.gz --pheno data/Challenge_Clinical_Phenotype_1.docx -o results/track1_primary.csv
```

## Track 1 local scoring test

```bash
python -m pytest tests/test_scorer.py
```

## Notes / status

- The 9 MVA review/foundational PDFs were not found in the local scratch/home tree; open-access versions will be pulled to `refs/papers/` for gene-prior extraction.
- The official `evaluation.py` / gold standard is private; the local scorer in `src/mva_hackathon/eval/scorer.py` is implemented from the published scoring contract (compound-het, GRCh38, `PROBAND01`, rank points, F-max over EPCR).
