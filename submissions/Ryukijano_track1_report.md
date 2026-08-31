# Track 1 methods — causal compound-het call in *BUB1B*

**Challenge:** Rare Disease, Real Kid: MVA Hackathon 2026
**Hugging Face user / team:** Ryukijano
**Date:** 2026-08-31
**Submission CSV:** `submissions/Ryukijano_bub1b-compoundhet.csv`
**Code:** https://github.com/Ryukijano/mva-hackathon-2026 (private during the hackathon; CC BY 4.0 at close)
**Hub mirror:** https://huggingface.co/Ryukijano/mva-hackathon-2026

**AI assistance disclosure (28 Aug 2026 update):** Cursor agents — Grok 4.6 and Claude — on a commercial Cursor plan; Anthropic API / Claude used in earlier coding sessions. Provider terms: no training on customer content. Genome-scale files were not pasted into third-party LLM APIs. Literature claims below were checked against primary sources (ClinVar VCV000533901; North et al. 2014 *EMBO J*; González-Blanco et al. 2026 *Nat Commun*).

---

## 1. Question and short answer

PROBAND01’s causal genotype is a **compound-heterozygous pair in *BUB1B*** (MVA1):

| Allele | GRCh38 | HGVS (NM_001211.6) | Class |
|---|---|---|---|
| 1 | `chr15:40209701 T>G` | `c.2210T>G` `p.Leu737Ter` | ClinVar **Pathogenic/Likely pathogenic** for mosaic variegated aneuploidy syndrome 1 ([VCV000533901](https://www.ncbi.nlm.nih.gov/clinvar/variation/533901/)) |
| 2 | `chr15:40220612 T>G` | `c.3006T>G` `p.Asn1002Lys` | Novel missense in the kinase-like C-lobe; AlphaMissense **0.9229** (likely_pathogenic); absent from gnomAD |

Submitted EPCR `0.95`, `finding_type=primary`. Only this pair is submitted (one row). Architecture matches the canonical viable MVA1 pattern: truncating allele + hypomorphic missense (Hanks et al., 2004).

**What this is not:** `p.Glu756*` (a different historical alias); AlphaMissense 0.9229 is **not** popEVE; residual ~5–10% BUBR1 is the *BubR1^H/H* mouse literature value, **not** a measurement in this child; parental phasing is unproven (both alleles heterozygous in the proband VCF).

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
5. **SpliceAI** on the tiny candidate VCF only (`-D 500`; 10000 exceeds the tool maximum of 4999). Neither *BUB1B* allele is splice-driven.

After these filters, **only *BUB1B* carried two rare functional alleles**. That uniqueness, not a machine-learning ranker, is why the CSV is one row.

---

## 4. Scoring (how EPCR was produced)

Per-variant pathogenicity in `(0, 1]` (`src/mva_hackathon/variants/score.py`):

- **PTV** (stop-gained / frameshift / essential splice): `0.99`
- **Missense:** `0.7 × popEVE_sigmoid + 0.3 × AlphaMissense`. popEVE maps through a sigmoid centred at the published severe cutoff `−5.056`. If popEVE is missing, AlphaMissense is used as the population-weighted term as well.
- **Splice-region:** max SpliceAI `DS_*` if > 0
- **Pair score:** product of the two allele scores (both alleles must be damaging)
- **EPCR:** `max(primary_floor, pair_score)` with `primary_epcr: 0.95` in `configs/config.yaml`

For this pair: p.Leu737Ter → 0.99; p.Asn1002Lys is AlphaMissense-dominated (popEVE only moderate, `−3.657`). Pair product ≈ 0.91, then floored to **0.95** as the primary call. A local clone of the published rank-points / F-max contract lives in `src/mva_hackathon/eval/scorer.py` (`pytest tests/test_scorer.py`).

Chromosomes in the VCF/VEP output are `15` (no `chr` prefix); the writer adds `chr` for the official CSV.

---

## 5. Why this pair is the causal genotype

1. **Gene:** biallelic *BUB1B* is the founding MVA1 locus (Hanks et al., 2004). The phenotype (MVA + childhood embryonal tumour) points at SAC-core genes, not the centrosomal MVA subset.
2. **Allele 1** is a known MVA1 pathogenic stop-gain at the exact GRCh38 coordinate in ClinVar (VCV000533901; two submitters, Pathogenic / Likely pathogenic). It truncates before the kinase-like domain and C-terminal KEN/ABBA motifs used in MCC.
3. **Allele 2** is absent from gnomAD, sits in the C-lobe of the human BUBR1 **pseudokinase**, and is scored likely_pathogenic by AlphaMissense. Neighbouring MVA missenses (human L1012P / mouse L1002P, R814H) reduce protein and SAC activity (Suijkerbuijk et al., 2010; Sieben et al., 2020). N1002K is nearby, not identical; we do not claim it is L1012P.
4. **Architecture:** nonsense + kinase-like-domain missense is the textbook viable MVA1 genotype (Hanks 2004; Sieben 2020: “typically a nonsense mutation in combination with a missense mutation in the kinase domain”). Two PTVs would more often be embryonic lethal; two mild missenses would not explain the tumour-predisposed, microcephalic presentation as cleanly.
5. **No competing compound-het** in the 15-gene panel after AF-key-corrected filtering.

---

## 6. Limitations (stated for judges)

- **Phasing:** both variants are heterozygous (VAF ≈ 0.5). In *trans* is the genetic inference from disease architecture, not a parental BAM proof.
- **Residual protein:** ~5–10% is the *BubR1^H/H* mouse hypomorph, not an immunoblot from this child.
- **popEVE vs AlphaMissense:** the missense is not a popEVE-severe allele; the call leans on ClinVar + AlphaMissense + gene-level uniqueness.
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
2. Suijkerbuijk SJE, et al. *Cancer Res* 2010;70:7981–91.
3. Sieben CJ, et al. *J Clin Invest* 2020;130:411–25. doi:10.1172/JCI126863.
4. Malumbres M, Villarroya-Beltri C. *Nat Rev Genet* 2024. doi:10.1038/s41576-024-00762-6.
5. ClinVar VCV000533901.9. NM_001211.6(*BUB1B*):c.2210T>G (p.Leu737Ter). https://www.ncbi.nlm.nih.gov/clinvar/variation/533901/
6. Cheng J, et al. AlphaMissense. *Science* 2023.
7. Official Track 1 scoring contract (rank points + F-max; compound-het; GRCh38; `PROBAND01`).
