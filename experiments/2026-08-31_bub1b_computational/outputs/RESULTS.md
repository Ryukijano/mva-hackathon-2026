# Results log — 2026-08-31_bub1b_computational

Do not overwrite `outputs/e2_preregistered/` (frozen E2). GPU ESM writes named+C-lobe LLRs to this directory; CPU named-only writes to `esm1v_cpu_named/`.

## Open Targets 26.06

`drugAndClinicalCandidates` recovered JAK inhibitors, dual PI3K/mTOR compounds, omaveloxolone (NFE2L2, APPROVAL), tocilizumab, and STING agonist ADU-S100 (anti-target). **Sirolimus/everolimus are absent from the MTOR list** (likely FKBP1A annotation). ChEMBL remains the rapalog source. BUB1B and SIRT2 have zero OT drugs.

## E2 (pre-registered) — H2 **falsified**

1-hop PrimeKG skip-gram, 2348 nodes / 4205 edges / **37 drugs**, query = parent MVA disease node. Seeds included TTK/AURKB/TMEM173.

| Drug | Mean rank / 37 |
|---|---|
| Fedratinib | 2.3 |
| Baricitinib | 9.0 |
| Cambinol (SIRT inhibitor, wrong direction) | 11.0 |
| BOS172722 (TTK) | 20.7 |
| Sirolimus | 22.0 |
| Tocilizumab | 23.3 |
| Everolimus | 27.7 |

Sirolimus is outside the top 50%; BOS172722 ranks above it. Cosines are negative (small graph; ranks still order JAK > rapalogs).

## E2b (exploratory; A3) — anti-target seeds dropped

2086 nodes / 3682 edges / **31 drugs**. BOS172722 gone. JAK/IL-6 still dominate; rapalogs still mid-pack.

| Drug | Mean rank / 31 |
|---|---|
| Sarilumab | 2.7 |
| Ruxolitinib | 2.7 |
| Tocilizumab | 3.7 |
| Baricitinib | 8.0 |
| Cambinol | 9.7 |
| Everolimus | 15.7 |
| Sirolimus | 16.7 |
| Temsirolimus | 27.3 |

Top 10% of 31 is rank ≤ 3.1. Sirolimus still fails. Graph proximity supports a **JAK/IL-6 neighbourhood prior**, not a rapalog ranking.

## E1 (ESM-1v) — H1 **falsified** on the L1012P-comparability clause

GPU job **7619146** (L40S, bf16, window 29–1050). CPU named-only **7619147** agrees.

| Allele | GPU LLR (nats) | CPU LLR |
|---|---|---|
| N1002K (this case) | −0.110 | −0.105 |
| L1012P | −1.801 | −1.802 |
| R814H | −1.444 | −1.468 |
| K668Q (acetylation mimic) | −0.309 | −0.311 |

N1002K is 1.69 nats weaker than L1012P (pre-registered window was 0.5). It is the 17th-mildest of 19 substitutions at residue 1002. The **site** is constrained (worst AA W = −3.70, similar to L1012). AlphaMissense 0.9229 remains the stronger allele-level in-silico call; ESM-1v does **not** make N1002K look like L1012P/R814H.

## E1c (ClinVar B/LB missenses) — second H1 falsifier **met**

Public ClinVar `variant_summary` (FTP, GRCh38, NM_001211.6, UniProt O60566 WT-checked). **34 unique** B/LB missense alleles (35 rows; F977L twice). CPU ensemble job **7648413**.

| Statistic | LLR (nats) |
|---|---|
| B/LB median (even-n mean of two central alleles) | **−0.161** |
| B/LB mean | −0.033 |
| N1002K | **−0.110** (rank 18/34, 1 = most damaging) |
| L1012P | −1.801 (below the entire B/LB cloud) |

N1002K is weaker than the B/LB median, so the pre-registered second falsifier fires. It sits in the centre of the ClinVar B/LB distribution; L1012P does not. ClinVar also has a **VUS** for p.Asn1002Lys on a different codon (`c.3006T>A`, VCV004600147.1), not this child's `c.3006T>G`. L1012P is ClinVar VUS; R814H is conflicting — almost no BUB1B missense is P/LP in ClinVar (the exception is Q467H).

## Environment

`environment.lock.json`: torch 2.13.0+cu126, transformers 5.14.1, NVIDIA L40S.

