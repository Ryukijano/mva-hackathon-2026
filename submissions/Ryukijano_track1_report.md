# Track 1 methods — BUB1B compound-het call (phasing inferred)

**Challenge:** Rare Disease, Real Kid: MVA Hackathon 2026
**Hugging Face user / team:** Ryukijano
**Date:** 2026-08-31 (revised 2026-09-10)
**Submission CSV:** `submissions/Ryukijano_bub1b-compoundhet.csv`
**Code:** https://github.com/Ryukijano/mva-hackathon-2026 (private during the hackathon; CC BY 4.0 at close)
**Hub mirror:** https://huggingface.co/Ryukijano/mva-hackathon-2026

**AI assistance disclosure (10 Sep 2026 update):** Cursor agents — Grok 4.6 and Claude — on a commercial Cursor plan; Anthropic API / Claude Sonnet and Cognition Devin (SWE-2 Max) used in coding, literature-verification, and database-check sessions. Provider terms: no training on customer content (processor, not recipient, per the challenge's third-party-LLM guidance in discussion #2). Genome-scale files were not pasted into third-party LLM APIs. Literature claims below were checked against primary sources (ClinVar VCV000533901/VCV004600147; gnomAD v4; dbSNP; North et al. 2014 *EMBO J*; González-Blanco et al. 2026 *Nat Commun*; Frontiers Endo 2026 doi:10.3389/fendo.2026.1838559).

---

## 1. Question and short answer

PROBAND01’s **best-supported** genotype is a **presumed** compound-heterozygous pair in *BUB1B* (MVA1):

| Allele | GRCh38 | HGVS (NM_001211.6) | Class |
|---|---|---|---|
| 1 | `chr15:40209701 T>G` | `c.2210T>G` `p.Leu737Ter` | ClinVar **Pathogenic/Likely pathogenic** for mosaic variegated aneuploidy syndrome 1 ([VCV000533901](https://www.ncbi.nlm.nih.gov/clinvar/variation/533901/)) |
| 2 | `chr15:40220612 T>G` | `c.3006T>G` `p.Asn1002Lys` | C-lobe **pseudokinase** missense; AlphaMissense **0.9229** (likely_pathogenic); ESM-1v predicts a mild substitution (3rd-mildest of 19 at this residue); the **protein change** N1002K is in ClinVar as VUS (VCV004600147.1, single submitter SCV007198955, last evaluated 19 Sep 2025, trait "Inborn genetic diseases", via the alternative `c.3006T>A` nucleotide change); our exact `c.3006T>G` allele is absent from ClinVar and from gnomAD genomes (single allele in gnomAD v4 exomes, AF ≈ 6.8e-07) |

Submitted EPCR `0.95`, `finding_type=primary`. Only this pair is submitted (one row). Architecture matches the canonical viable MVA1 pattern: truncating/null allele + hypomorphic missense (Hanks et al., 2004). A viable MVA1 proband must retain some residual BUBR1 protein, since complete BUB1B loss is embryonic lethal.

**What this is not:** `p.Glu756*` (a different historical alias); AlphaMissense 0.9229 is **not** a popEVE log-odds score; popEVE is missing for this c.3006T>G (the protein change exists in ClinVar only as VCV004600147.1 VUS via `c.3006T>A`, trait "Inborn genetic diseases", last evaluated 19 Sep 2025); ESM-1v does **not** make N1002K equivalent to L1012P; the p.Leu737Ter UGA stop is suppressible in principle but untested in this child; residual ~11% BUBR1 is the *BubR1^H/H* mouse literature value (Baker 2004: 11% ±3%), **not** a measurement in this child; parental phasing is unproven (both alleles heterozygous in the proband VCF).

---

## 2. Data used

- Official gated WGS VCF `WGS_EX2312012_HGWCNDSX7.vcf.gz` + TBI from `SageBio/mva-hackathon-2026-data` (GRCh38).
- Challenge phenotype document, used only to confirm an MVA-consistent presentation (growth restriction, microcephaly, childhood solid tumour) and to keep the search inside mitotic/SAC genes. Automated HPO regex extraction from the docx returned no terms; it was **not** used as a scoring feature.
- **Not used for this shot:** FASTQ remapping, joint calling, or long-read data. The supplied VCF was treated as the variant source.

Genome / VCF / FASTQ files are **not** in the public code repos. Ranked findings, code, and this report may remain (CC BY 4.0). Genome-scale files will be deleted within 30 days of close, per the DTA.

---

## 3. Annotation and filters

1. **Ensembl VEP 116**, GRCh38, offline cache, with AlphaMissense and popEVE/EVE plugins (`scripts/run_track1.py`, `src/mva_hackathon/variants/vep.py`).
2. **Panel** (`configs/panel.yaml`): 15 mitotic genes — SAC core (*BUB1B, BUB1, MAD1L1, TRIP13, MAD2L1BP*), centrosome (*CEP57, CEP192*), minor spliceosome (*CENATAC*), plus extended SAC/kinetochore neighbours (*CDC20, TTK, MAD2L1, BUB3, KNL1, AURKA, PLK1*). Childhood tumours in MVA track core SAC genes, not CEP57/CEP192, in human series (Malumbres & Villarroya-Beltri, 2024).
3. **Rarity:** keep if all of `gnomADg_AF`, `gnomADe_AF`, `AF` are missing or ≤ 0.001. An earlier bug read a non-existent `gnomad_af` key and let common panel SNPs through; that is fixed in `filter.py` / `parse.py`.
4. **Consequence:** SO terms in `configs/panel.yaml` (`stop_gained`, `missense_variant`, canonical splice, frameshift, etc.).
5. **SpliceAI** on the tiny candidate VCF (`-D 500`) and a subsequent deep sweep across the full BUB1B gene region (`-D 4999`; see §5b). Neither *BUB1B* allele is splice-driven.

After these filters, **only *BUB1B* carried two rare functional alleles**. That uniqueness, not a machine-learning ranker, is why the CSV is one row.

---

## 4. Scoring (how EPCR was produced)

Per-variant pathogenicity in `(0, 1]` (`src/mva_hackathon/variants/score.py`):

- **PTV** (stop-gained / frameshift / essential splice): `0.99`
- **Missense:** `0.7 × popEVE_sigmoid + 0.3 × AlphaMissense`. popEVE maps through a sigmoid centred at the published severe cutoff `−5.056`. If popEVE is missing, AlphaMissense is used as the population-weighted term as well.
- **Splice-region:** max SpliceAI `DS_*` if > 0
- **Pair score:** product of the two allele scores (both alleles must be damaging)
- **EPCR:** `max(primary_floor, pair_score)` with `primary_epcr: 0.95` in `configs/config.yaml`

For this pair: p.Leu737Ter → 0.99; p.Asn1002Lys is AlphaMissense-dominated (popEVE is not available for this novel variant, so the population-evidence term falls back to AlphaMissense). Pair product ≈ 0.91, then floored to **0.95** as the primary call. A local clone of the published rank-points / F-max contract lives in `src/mva_hackathon/eval/scorer.py` (`pytest tests/test_scorer.py`).

Chromosomes in the VCF/VEP output are `15` (no `chr` prefix); the writer adds `chr` for the official CSV.

---

## 5. Why this pair is the best-supported genotype

1. **Gene:** biallelic *BUB1B* is the founding MVA1 locus (Hanks et al., 2004). The phenotype (MVA + childhood embryonal tumour) points at SAC-core genes, not the centrosomal MVA subset.
2. **Allele 1** is a known MVA1 pathogenic stop-gain at the exact GRCh38 coordinate in ClinVar (VCV000533901; two submitters, Pathogenic / Likely pathogenic). It truncates before the C-terminal pseudokinase domain; the N-terminal KEN boxes and ABBA motifs are retained, but the premature-stop transcript/protein is expected to be degraded by NMD and/or instability.
3. **Allele 2** sits in the **C-lobe of the BUBR1 pseudokinase domain** and is scored likely_pathogenic by AlphaMissense (0.9229, well above the 0.564 threshold). ESM-1v predicts it to be the **third-mildest** of 19 amino-acid substitutions at residue 1002 and milder than the ClinVar benign/likely-benign median, so the *in silico* predictors conflict; AlphaMissense, which incorporates AlphaFold-derived structural context, is the stronger pathogenic signal here. Residue 1002 is 10 amino acids from the classic MVA1 missense **L1012P** (*Suijkerbuijk et al., 2010*), which was shown to destabilise BUBR1 protein and increase proteasomal degradation rather than ablate intrinsic SAC kinase activity. N1002K is therefore biologically predicted to act as a destabilising hypomorphic allele, not as a null. **External databases (checked Sep 2026 via NCBI ClinVar API):** the protein change is registered in ClinVar as **VCV004600147.1 — Uncertain significance** (single submitter SCV007198955, last evaluated 19 Sep 2025, trait "Inborn genetic diseases", submitted as the alternative nucleotide change `c.3006T>A`); our exact `c.3006T>G` allele is absent from ClinVar and from gnomAD genomes, with a single allele in gnomAD v4 exomes (AF ≈ 6.8e-07, far below the 0.001 rarity threshold). Allele 1 (`c.2210T>G`) also appears in gnomAD v4 at AF ≈ 7.9e-05 (exomes) / 3.3e-05 (genomes) — expected carrier-level frequency for a recessive loss-of-function allele and still passing the rarity filter.
4. **Architecture:** nonsense/null + pseudokinase C-lobe missense is the textbook viable MVA1 genotype (Hanks 2004; Sieben 2020: typically a nonsense mutation in combination with a missense mutation in the kinase/pseudokinase domain). Two PTVs would more often be embryonic lethal; two mild missenses would not explain the tumour-predisposed, microcephalic presentation as cleanly.
5. **No competing compound-het** in the 15-gene panel after AF-key-corrected filtering.
6. **Independent functional support for the 737–739 linker region:** a 2026 study of two heterozygous *BUB1B* variants including **p.Ala739Ser** (c.2215G>T, two residues from p.Leu737Ter) reported significantly elevated premature chromatid separation and a trend toward reduced BUB1B mRNA/BUBR1 protein by RT-PCR/Western blot (Frontiers in Endocrinology 2026, doi:10.3389/fendo.2026.1838559). This reinforces that the Leu737–Ala739 truncation-proximal region is dosage-sensitive; our stop-gain removes the entire C-lobe from codon 737 onward.

### 5a. AlphaGenome AVI scores

Google DeepMind's AlphaGenome Aggregate Variant Impact (AVI) score was queried for both variants (2026-09-10; `supplement/track1/bub1b_avi_scores.json`). AVI is a Phred-scaled aggregate pathogenicity score integrating sequence, conservation, splicing, chromatin, and protein modalities. Higher Phred = more pathogenic.

| Variant | AVI Phred | AVI quantile (top %) | Top modality | Top feature importance | Splicing FI | Conservation (PhastCons) |
|---|---|---|---|---|---|---|
| `chr15:40209701 T>G` (p.Leu737Ter) | **33.76** | 0.042% | Protein Termination | 1.484 | 0.027 | 0.221 |
| `chr15:40220612 T>G` (p.Asn1002Lys) | **25.61** | 0.275% | AlphaMissense | 0.761 | 0.015 | 0.235 |

**Interpretation:**
- **p.Leu737Ter** has the higher AVI Phred (33.76), with the top contributing modality being **Protein Termination** (FI = 1.484), consistent with its nonsense consequence. Splicing contribution is negligible (FI = 0.027), supporting the SpliceAI finding that this is not a cryptic-splice allele.
- **p.Asn1002Lys** has a lower but still elevated AVI Phred (25.61, top 0.275%), with the top modality being **AlphaMissense** (FI = 0.761), consistent with the AlphaMissense 0.9229 likely-pathogenic call. The splicing contribution is negligible (FI = 0.015).
- AlphaGenome AVI is an additional computational pathogenicity signal; it is not independent of AlphaMissense (which is one of its input modalities) and does not establish functional consequence. It is reported here as supportive evidence, not as a standalone clinical classification.

### 5b. SpliceAI deep-intronic sweep

A deep SpliceAI sweep (SpliceAI 1.3.1, `-D 4999` maximum distance) was run across the full BUB1B gene region (chr15:40,180,000–40,300,000; 120 kb; 135 variants; `supplement/track1/bub1b_full_gene_spliceai.vcf` and `supplement/track1/spliceai_summary.md`).

| Variant | SpliceAI gene | DS_AG | DS_AL | DS_DG | DS_DL | Max DS | Verdict |
|---|---|---|---|---|---|---|---|
| p.Leu737Ter (`chr15:40209701 T>G`) | BUB1B | 0.03 | 0.00 | 0.00 | 0.01 | **0.03** | No splice impact (< 0.2) |
| p.Asn1002Lys (`chr15:40220612 T>G`) | BUB1B | 0.02 | 0.00 | 0.00 | 0.00 | **0.02** | No splice impact (< 0.2) |

No BUB1B-annotated variant in the 120 kb region exceeds DS = 0.03. The commonly used 0.2 threshold for splice impact is not approached by either target variant. This closes the "cryptic splice third hit" falsifier: neither variant is predicted to create or disrupt a splice site. This does not establish functional neutrality for p.Leu737Ter (which remains a nonsense allele) or p.Asn1002Lys (which may affect protein structure/function), but it rules out cryptic splicing as a contributing mechanism.

---

## 6. Limitations (stated for judges)

- **Phasing:** both variants are heterozygous (VAF ≈ 0.5). The two sites are 10,911 bp apart. WhatsHap read-backed phasing returned **UNRESOLVED**: the maximum observed library fragment length is ~1,348 bp, no read pair spans >9 kb on chr15, and no chain of read-connected heterozygous sites bridges the 10.9 kb gap (only one intervening het SNV at 15:40216470, with both sub-gaps exceeding the insert size). The variants are therefore **presumed compound heterozygous** based on: (i) the autosomal-recessive MVA1 phenotype; (ii) the canonical truncating + hypomorphic missense architecture (Hanks et al. 2004); (iii) the absence of a third *BUB1B* coding/splice candidate in the scanned 250 kb region; (iv) the exclusion of obvious *CEP57*/*TRIP13* pathogenic variants. Population-based statistical phasing (SHAPEIT5) is unlikely to be informative for p.Asn1002Lys (AC=1 in gnomAD v4 exomes; effectively singleton) and would not constitute definitive confirmation. **Parental genotyping or targeted long-range PCR followed by long-read sequencing is recommended for definitive phase confirmation** (see `docs/phasing_validation_plan.md`). In silico long-range PCR primers have been designed: an ~11.1 kb amplicon (chr15:40209640–40220748) spanning both variants and the intervening het SNV (`scripts/design_lrpcr_primers.py`).
- **Residual protein:** ~11% ± 3% is the *BubR1^H/H* mouse hypomorph (Baker 2004), not an immunoblot from this child.
- **ACMG status of p.Asn1002Lys:** formal automated classification is a **Variant of Uncertain Significance (VUS) leaning Likely Pathogenic** (PM2_Supporting [absent from gnomAD genomes; single allele in gnomAD v4 exomes, AF ≈ 6.8e-07] + PP3 [AlphaMissense pathogenic, downweighted by ESM-1v discordance]). An independent single-submitter ClinVar record for the same protein change (`c.3006T>A`, VCV004600147.1, VUS, last evaluated 19 Sep 2025, trait "Inborn genetic diseases") confirms it is a real, observed, unclassified missense — not an artefact. The call is strengthened by the biallelic MVA1 architecture and the absence of any competing candidate gene.
- **popEVE vs AlphaMissense:** popEVE is not available for this novel missense; the call leans on ClinVar + AlphaMissense + gene-level uniqueness.
- **Cryptic second-hit / non-coding caveat:** short-read WGS cannot fully exclude a deep-intronic or regulatory second hit in *BUB1B*. MVA1 cases with a single coding allele are documented to carry a second cryptic hit — a 44 kb upstream regulatory G>A (Matsuura 2006; ss804270619), or deep-intronic Alu/SVA insertions causing aberrant splicing (PMID 28611924; PMID 38102195), or a compound-het coding + upstream-regulatory pair (Shandong fetus paper 2025, doi:10.3760/cma.j.cn511374-20240716-00393). Our 250 kb region scan found no coding or plausibly regulatory candidate, but it was not a structural-variant / repeat-element screen. This residual uncertainty is disclosed rather than resolved.
- **No FASTQ remap** in this submission. A second shot could re-align if the supplied VCF were suspected incomplete; nothing in the current call requires that.
- **Cancer `priority_bonus` in `run_track1.py` is dead code** and was **not** added to EPCR (that would have allowed EPCR > 1).
- Coordinates and alleles were checked against ClinVar for allele 1; allele 2 has no ClinVar record.

---

## 7. Reproducibility

```bash
# after accepting the gated dataset DTA
python scripts/run_track1.py \
  --vcf data/WGS_EX2312012_HGWCNDSX7.vcf.gz \
  --pheno data/Challenge_Clinical_Phenotype_1.docx \
  -o submissions/Ryukijano_bub1b-compoundhet.csv
python -m pytest tests/test_scorer.py
```

Environment: `environment.yaml` (Python 3.11, Ensembl VEP **116**). AIRE paths: `configs/paths/aire.yaml`. The submitted one-row CSV is the curated primary call after confirming panel uniqueness; the CLI can emit up to 10 ranked rows (`max_submission_rows`).

---

## 8. References

1. Hanks S, et al. *Nat Genet* 2004;36:1159–61. PMID 15475955.
2. Suijkerbuijk SJE, et al. *Cancer Res* 2010;70:7981–91. (pseudokinase missense L1012P causes BUBR1 destabilisation, not catalytic loss.)
3. Sieben CJ, et al. *J Clin Invest* 2020;130:411–25. doi:10.1172/JCI126863.
4. Malumbres M, Villarroya-Beltri C. *Nat Rev Genet* 2024. doi:10.1038/s41576-024-00762-6.
5. ClinVar VCV000533901.9. NM_001211.6(*BUB1B*):c.2210T>G (p.Leu737Ter). https://www.ncbi.nlm.nih.gov/clinvar/variation/533901/ — re-verified 10 Sep 2026: P/LP, multiple submitters, last evaluated 2024/10/09; dbSNP rs759242053.
6. ClinVar VCV004600147.1. NM_001211.6(*BUB1B*):c.3006T>A (p.Asn1002Lys). https://www.ncbi.nlm.nih.gov/clinvar/variation/4600147/ — re-verified 10 Sep 2026: VUS, single submitter SCV007198955, last evaluated 19 Sep 2025, trait "Inborn genetic diseases"; our exact c.3006T>G allele is ClinVar-absent; dbSNP rs2542593804.
7. Frontiers in Endocrinology 2026, doi:10.3389/fendo.2026.1838559 — p.Ala739Ser (c.2215G>T) functional evidence: premature chromatid separation + reduced BUB1B mRNA/protein, 2 residues from p.Leu737Ter.
8. Miyamoto T, et al. *Hum Genome Var* 2017;4:17021 (PMID 28611924); *J Hum Genet* 2024 (PMID 38102195) — deep-intronic BUB1B Alu/SVA insertions as cryptic MVA1 second hits.
9. Shandong fetus paper 2025 (PMID 40555658, doi:10.3760/cma.j.cn511374-20240716-00393) — compound-het BUB1B + upstream regulatory second hit.
10. gnomAD v4 (queried 10 Sep 2026): L737Ter exome AC=115 (AF 7.87e-05), genome AC=5 (AF 3.29e-05); N1002K exome AC=1 (AF 6.84e-07), genomes absent.
11. Cheng J, et al. AlphaMissense. *Science* 2023.
12. Official Track 1 scoring contract (rank points + F-max; compound-het; GRCh38; `PROBAND01`; Space `evaluation.py` re-fetched and matched 11 Sep 2026).
