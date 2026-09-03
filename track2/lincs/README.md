# MVA Track 2 — LINCS transcriptomic reversal analysis

**Goal:** Independently validate the Track 2 candidate stack by identifying currently approved medications that reproducibly reverse BUB1B/MVA/aneuploidy transcriptomic signatures, and reject apparent hits that are likely generic cytostasis or checkpoint-inhibition artifacts.

**Method:** Cross-species, multi-signature approved-drug reversal with a false-rescue safety firewall.

## Signatures

1. **Human MVA** — GSE22206 (BUB1B-mutant proband fibroblasts / LCLs).
2. **Early mouse hypomorph** — GSE134781 (`+/X753`, `+/L1002P` vs WT; 3 months).
3. **Late MVA-like mouse** — GSE134780 (`H/L1002P`, `H/H` vs WT; 10 months, muscle and adipose).
4. **Generic human aneuploidy** — GSE247267 (isogenic RPE1).
5. **Human BUB1B CRISPR (acute)** — LINCS knockdown/knockout consensus as a secondary, mechanistic contrast.

## Workflow

1. **Stage data** (`scripts/01_download_geo.R` / `python`)
   - Download from GEO, build sample metadata.
   - For mouse count data, normalise and map one-to-one human orthologues.
   - For human microarray, normalise and produce gene × sample expression matrix.

2. **Differential expression** (`scripts/02_de_analysis.R`)
   - Human microarray: `limma` with BH correction.
   - Mouse counts: `edgeR`/`limma-voom` with BH correction.
   - Generate ranked up/down lists at 100, 150, 250 gene sizes.
   - Leave-one-sample-out sensitivity for datasets with ≥4 samples/group.

3. **LINCS queries** (`scripts/03_query_lincs.py`)
   - Primary: L2S2 (https://l2s2.maayanlab.cloud) paired reverse-enrichment with FDA-approved filter.
   - Secondary: L1000CDS2 consensus (legacy API) as sensitivity check.
   - Freeze all request payloads and JSON responses.

4. **False-rescue firewall** (`scripts/04_firewall.py`)
   - Current market approval verified by regulator (FDA/EMA/MHRA/PMDA/etc.).
   - Reversal in ≥2 independent disease signatures.
   - Rank stability across 100/150/250 gene-list sizes.
   - Mechanism consistent with BUB1B/aneuploidy stress (no TTK/MPS1, Aurora B, STING agonists).
   - Not dominated by cytostatic/proliferation signatures; re-rank after removing Hallmark E2F/G2M genes.
   - Pediatric feasibility and cancer-predisposition safety check.

5. **Integration** (`scripts/05_update_track2.py`)
   - Merge LINCS scores with `track2_candidates.csv`.
   - Update `track2_report.md` and pitch with cross-signature heatmap, rank-stability plot, and a false-rescue example.

## Outputs

- `data/*_expr.csv` — expression matrices
- `data/*_degs.csv` — differential expression results
- `data/*_signature_*.txt` — up/down gene lists for L2S2
- `results/l2s2_*.json` — frozen API responses
- `results/lincs_consensus.csv` — consensus candidate ranking
- `results/firewall_decisions.csv` — accepted / rejected computational hits
- `figures/` — heatmap, rank-stability plot, candidate card

## Environment

Use the dedicated `mva-hackathon-lincs` conda environment:

```bash
module load miniforge/24.7.1
conda activate /scratch/kcwp264/.conda_envs/mva-hackathon-lincs
```

Created from `track2/lincs/environment_lincs.yaml`.

## Citation / provenance

- L2S2: Ma'ayan Lab, 2025.
- GSE22206, GSE134780, GSE134781, GSE247267: GEO.
- LINCS L1000: CLUE / L1000CDS2.
