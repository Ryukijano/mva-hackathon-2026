# MVA Track 2 — LINCS transcriptomic reversal analysis

**Goal:** Perform an exploratory consistency check on the Track 2 candidate stack by identifying approved medications whose transcriptional perturbation pattern opposes BUB1B/MVA/aneuploidy signatures, and reject apparent hits that are likely generic cytostasis, mimic the disease state, or are inconsistent with the biology.

**Method:** Multi-contrast, multi-gene-list L2S2/L1000CDS2 query with a false-rescue firewall.

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
   - Primary: L2S2 (https://l2s2.maayanlab.cloud) paired enrichment with FDA-approved filter. L2S2 returns three p-values per drug: non-directional, mimic (`adj_pvalue_up`), and reverse (`adj_pvalue_down`).
   - Secondary: L1000CDS2 consensus (legacy API) as sensitivity check.
   - Freeze all request payloads and JSON responses.

4. **False-rescue firewall** (`scripts/04_firewall.py`)
   - Current market approval verified by regulator (FDA/EMA/MHRA/PMDA/etc.).
   - Gate L2S2 rescue on **directional reverse FDR** (`adj_pvalue_down < 0.05`). Non-directional enrichment and mimic (`adj_pvalue_up`) signals are reported but do not, by themselves, establish rescue.
   - Report reverse/mimic/general counts per signature; the same drug can be a reverse in one contrast and a mimic in another, which is flagged as `MIXED`.
   - Mechanism consistent with BUB1B/aneuploidy stress (no TTK/MPS1, Aurora B, STING agonists).
   - Not dominated by cytostatic/proliferation signatures; re-rank after removing Hallmark E2F/G2M genes.
   - Pediatric feasibility and cancer-predisposition safety check; supportive/adjunct candidates are downgraded to `WEAK` even if a reverse signal is present.

5. **Integration**
   - The firewall writes `results/track2_candidates_with_lincs.csv`; the merged
     LINCS status was folded back into `track2/data/track2_candidates.csv`, and
     `track2_report.md` / the pitch storyboard were updated by hand.

## Outputs

- `data/*_expr.csv` — expression matrices (local only; not committed)
- `data/*_degs.csv` — differential expression results (local only; not committed)
- `data/*_{up,down}_{100,150,250}.txt` — up/down gene lists for L2S2
- `data/raw/` — GEO downloads (local only; not committed)
- `results/l2s2/*_raw.json` — frozen API responses
- `results/l2s2/query_summary.csv` — per-signature query counts
- `results/de_summary.csv` — DEG counts per contrast
- `results/signature_composition.csv` — FDR vs nominal genes per signature
- `results/lincs_firewall_decisions.csv` — accepted / rejected computational hits
- `results/lincs_candidate_ranking.csv` — surviving (WEAK) candidates
- `results/track2_candidates_with_lincs.csv` — candidate list + LINCS status

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
