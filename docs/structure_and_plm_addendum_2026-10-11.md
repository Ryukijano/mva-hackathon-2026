# Addendum (11 Oct 2026): structure and protein-LM context for BUBR1 p.Leu737Ter, p.Asn1002Lys, p.Leu1012Pro

**Scope.** Protein-level only, for the Track 1 and Track 2 reports. It does not change any submitted CSV, ranking or report. It adds structural and language-model context and states what these analyses cannot show. UniProt O60566 numbering throughout.

## 1. AlphaFold DB monomer (AF-O60566-F1, model_v6)

Source: `experiments/2026-10-11_alphafold_bubr1/` (SUMMARY.md, region_summary.txt, plddt_per_residue.csv).

| Region | Mean pLDDT |
|---|---|
| 1–736 (retained by p.Leu737Ter) | 55.74 |
| 737–1050 (lost by p.Leu737Ter; includes protein kinase domain 766–1050) | 82.05 |
| Residue 1002 (Asn) | 91.06 |
| Residue 1012 (Leu) | 95.31 |

- The lost C-terminal region is predicted with high confidence, so its loss is a loss of structured sequence, not of disorder.
- Cα–Cα distance between 1002 and 1012 is **12.32 Å** in the monomer. The two residues are not in contact in this model. They sit on the same lobe, not on adjacent faces.
- Neighbour counts (Cα within 10 Å) are 20 for 1002 and 25 for 1012, against a mean of 11.6 across the protein. These are a burial proxy, not computed solvent accessibility.
- AlphaFold monomer prediction cannot evaluate phasing, splicing, nonsense-mediated decay (NMD) or pathogenicity. It does not model BUBR1–BUB3, KNL1 or CDC20 complexes.

## 2. ESM-1v ensemble (protein language model)

Source: `experiments/2026-08-31_bub1b_computational/outputs/RESULTS.md` (A4 in `protocol.md`). Masked-marginal log-likelihood ratio (LLR), five `esm1v_t33_650M_UR90S` models, UniProt O60566. More negative means more damaging.

| Substitution | GPU (L40S, bf16) | CPU (fp32) |
|---|---|---|
| N1002K | −0.110 | −0.105 |
| L1012P | −1.801 | −1.802 |
| R814H | −1.444 | −1.468 |
| K668Q | −0.309 | −0.311 |

- **Precision.** bf16 versus fp32 differs by 0.001–0.005 nats for N1002K, L1012P and K668Q. The largest gap is R814H, at 0.024 nats. None of these differences changes any conclusion.
- **ClinVar benign and likely-benign control** (34 unique BUB1B missense alleles): median −0.161, mean −0.033. N1002K (−0.110) sits inside that distribution. L1012P (−1.801) lies below all of them.
- **Status of these numbers.** These scores were computed with the earlier windowing scheme. A corrected rerun is pending. Do not cite the values above as final. The direction of the comparison is the only thing to rely on until the rerun is in.

## 3. Literature (checked against source where stated)

- **Suijkerbuijk et al., Cancer Res 2010;70:4891–900.** Patient cell lines with biallelic MVA mutations show low BUBR1 abundance. Truncating alleles lose transcript, and kinase-domain missense alleles show high protein turnover. In ectopic LAP-BUBR1 expression in HeLa and U2OS cells, kinase-domain substitutions were 5–10-fold lower; in patient lines, 2–6-fold lower. L1012P turnover was tested in U2OS with cycloheximide, geldanamycin and MG132 (Fig. 3C). The abstract was checked; the figure-level numbers were confirmed in the abstract text.
- **Structures.**
  - PDB 6TLJ: cryo-EM of APC/C–MCC (3.8 Å). It contains a full-length BUBR1 chain (1,050 residues). Which BUBR1 residues are modelled was not checked here.
  - PDB 2WVI: crystal structure of the BUBR1 N-terminal (TPR-type) domain, 1.8 Å.
  - PDB 3SI5: crystal structure of a BUBR1–Blinkin complex, 2.2 Å. It is not a kinase-domain structure.
- **Kinase domain.** Human BUBR1 kinase domain has not been crystallised. Huang et al., Cell Res 2019;29:562–578 (PDB 6JKK, Drosophila BubR1 kinase domain, 1.85 Å) is the homology proxy. Human residues map to it only approximately.
- **Not found.** No 2024–2026 study was found that measures BUBR1 protein in patient cells carrying a truncating plus a missense allele.

## 4. Limits

- ESM-1v and AlphaMissense both perform worse in disordered regions. The region near residue 1002 is confidently folded, but this is not a general guarantee.
- The monomer model cannot represent complex interfaces, and pLDDT is not a measure of stability.
- An LLR is not a calibrated probability. It cannot be read as "percent pathogenic."
- AlphaMissense 0.9229 comes from a different model, AlphaMissense, and is not an ESM-1v output. The two methods disagree for N1002K, and both are reported as such.

## 5. What these analyses do NOT show

- They do not show that N1002K is pathogenic, benign, or destabilising.
- They do not show that N1002K behaves like L1012P. ESM-1v does not place it in the same class.
- They do not show that the monomer structure reflects the cellular conformation or any complex.
- They do not show any phasing, splicing or NMD effect, or any readthrough of the truncating allele.
- They do not measure BUBR1 protein or mitotic function in the patient.
- They do not support the claim that a language model or knowledge graph identified any therapy.

## 6. What would change this

- **BUBR1 western blot** in patient-derived lymphoblastoid or fibroblast cells, with cycloheximide and MG132 chase, compared with parental and control lines. A reduction of the Suijkerbuijk size would support a destabilising mechanism for the missense allele.
- **Readthrough and NMD reporter** for the truncating allele, to test whether any full-length BUBR1 is produced. This gates the readthrough arm of Track 2.
- **Micronucleus counts** and mitotic timing in patient-derived cells, to test whether the reduced BUBR1 has a checkpoint consequence.
- **Corrected ESM-1v rerun**, which may move the N1002K and ClinVar numbers. Report the corrected values in place of those above.
