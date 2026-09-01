# Experiment: 2026-08-31_bub1b_computational

## Hypothesis & Prediction

**H1 (ESM-1v, Track 1 missense):** p.Asn1002Lys is a destabilising substitution in the BUBR1 pseudokinase C-lobe, comparable to established MVA missenses p.Leu1012Pro and p.Arg814His.

- Primary outcome: ensemble-mean masked log-likelihood ratio (LLR; mutant − WT) at the named residue, average of five ESM-1v 650M models (`facebook/esm1v_t33_650M_UR90S_{1–5}`).
- Prediction: LLR(N1002K) < 0 and within 0.5 nats of LLR(L1012P).
- Falsify H1 if LLR(N1002K) ≥ 0 or weaker (less negative) than the median of a benign/likely-benign BUB1B missense set.

**H2 (PrimeKG embeddings, Track 2):** drugs whose PrimeKG neighbourhood is close to *BUB1B* / MVA1 are enriched for the SIRT2–NAD+, mTOR/autophagy, Nrf2/ROS, and JAK/IL-6 axes, and depleted for TTK/Aurora B (wrong-direction SAC inhibitors).

- Primary outcome: mean rank (3 seeds) of sirolimus among drug nodes by cosine similarity to the MVA1 disease node (fallback: *BUB1B* protein node).
- Prediction: sirolimus ranks in the top 10% of drug nodes; TTK/AURKB inhibitors rank in the bottom 50% or are flagged as anti-targets.
- Falsify H2 if sirolimus is outside the top 50% **and** a TTK inhibitor ranks above it.

## Design

| ID | Description | Seeds | Hardware |
|---|---|---|---|
| E1 | ESM-1v ensemble LLR, UniProt O60566 | models 1–5 (fixed) | 1× L40S, bf16 |
| E2 | Skip-gram embeddings on PrimeKG axis subgraph | 0, 1, 2 | 1× L40S or CPU |

Baseline E1: AlphaMissense 0.9229 (already computed). ESM-1v is an independent protein-LM score, not a replacement.

Baseline E2: ChEMBL mechanism table (`track2/data/chembl_axis_drugs.csv`). Embeddings are complementary graph proximity, not a ChEMBL substitute.

## Controls

- Sequence: canonical UniProt O60566 (1050 aa). Residues 668=K, 737=L, 814=R, 1002=N, 1012=L verified before scoring.
- No patient VCF, FASTQ, or genome on GPUs or third-party APIs.
- Negative results will be reported.

## Data

- UniProt O60566 FASTA (public).
- PrimeKG `kg.csv` (Harvard Dataverse 10.7910/DVN/IXA7BM) at `refs/primekg/kg.csv` (gitignored).
- Open Targets GraphQL API 26.06.

## Stopping Rules

- E1: one forward pass per masked position per ensemble member; no hyperparameter search.
- E2: 50 epochs or 15 min wall, whichever first; embedding dim 64, lr 0.01.

## Pre-registration Status

- [x] Checklist complete (date: 2026-08-31)
- Protocol ID: `2026-08-31_bub1b_computational`
- Author: Ryukijano / kcwp264
- Amendments: see below

## Amendments

**A1 (2026-08-31, after failed job 7618992).** ESM-1v `max_position_embeddings=1026` (1022 amino acids + CLS/EOS). UniProt O60566 is 1050 aa, so a full-length forward is out of range and triggered a CUDA device-side assert. E1 scoring now uses a centered 1022-aa window (C-lobe residues sit in window 29–1050). Primary outcome unchanged. Failed run logged; no partial LLRs were written.

**A2 (2026-08-31, after E2).** H2 as pre-registered is **falsified** on the 1-hop subgraph (37 drugs): sirolimus mean rank 22.0 (outside top 50%) and TTK inhibitor BOS172722 mean rank 20.7 (above sirolimus). Query node was parent *mosaic variegated aneuploidy syndrome*, not MVA1. Seeds included TTK/AURKB/TMEM173 by construction. Open Targets 26.06 `drugAndClinicalCandidates` on MTOR did **not** return sirolimus/everolimus (FKBP1A annotation). E2 CSVs frozen; do not overwrite.

**A3 (2026-08-31, exploratory, not a new H2 claim).** E2b: same skip-gram (50 epochs, dim 64, seeds 0/1/2) with anti-target genes dropped from the seed set. Outputs in `outputs/e2b_no_antitarget/`. Does not reopen H2.

**A5 (2026-09-01, E1c).** ClinVar B/LB missense control (unused H1 falsifier). Source: NCBI `variant_summary.txt.gz`, GRCh38, NM_001211.6, O60566 WT match. n=34 unique alleles. Scored with the same ESM-1v ensemble on CPU (job 7648413; GPU queue StartTime 22:20). Conventional even-n median LLR = **−0.161**. N1002K (−0.110) is weaker than that median (rank 18/34) → second falsifier **met**. H1 remains falsified. Outputs in `outputs/e1c_clinvar/`.
