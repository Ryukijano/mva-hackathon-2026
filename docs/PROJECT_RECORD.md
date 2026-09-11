# MVA Hackathon 2026 — Comprehensive Project Record

**Team:** Ryukijano | **Challenge:** Rare Disease, Real Kid — MVA Hackathon 2026 (SageBio / Hugging Face)
**Repository:** `/mnt/scratch/kcwp264/mva-hackathon-2026` → GitHub `Ryukijano/mva-hackathon-2026` (private during hackathon; CC BY 4.0 at close) → HF Hub mirror `Ryukijano/mva-hackathon-2026`
**Deadline:** 24 Oct 2026, 23:59 UTC. Judging ~2–3 months after close.
**Record compiled:** 11 Sep 2026, from the full conversation history and repository state.

> **Scope note:** This is a consolidated record of everything done, found, corrected, and decided across the entire project — Track 1 (causal genotype), Track 2 (drug repurposing), the WGS phasing campaign, and the audit trail. It is written to be the single document someone can read to understand the full submission without opening every file.

---

## Table of contents

1. [Project context and rules](#1-project-context-and-rules)
2. [The proband and the causal genotype](#2-the-proband-and-the-causal-genotype)
3. [Track 1: variant evidence](#3-track-1-variant-evidence)
4. [The phasing problem (central scientific issue)](#4-the-phasing-problem)
5. [Molecular phasing validation plan](#5-molecular-phasing-validation-plan)
6. [Track 2: therapeutic hypothesis](#6-track-2-therapeutic-hypothesis)
7. [Track 2: candidate table with regulatory status](#7-track-2-candidate-table)
8. [LINCS transcriptomic screen and firewall](#8-lincs-transcriptomic-screen-and-firewall)
9. [ChEMBL target-first screen](#9-chembl-target-first-screen)
10. [Chronological history of the work](#10-chronological-history)
11. [Major errors found and corrected](#11-major-errors-found-and-corrected)
12. [Tools, databases, and code](#12-tools-databases-and-code)
13. [Scoring code and configuration](#13-scoring-code-and-configuration)
14. [Test suite](#14-test-suite)
15. [Repository structure and privacy](#15-repository-structure-and-privacy)
16. [Key numbers — consolidated reference](#16-key-numbers)
17. [Outstanding items](#17-outstanding-items)

---

## 1. Project context and rules

- **Track 1:** Ranked causal-genotype CSV. Max **6 submissions** (`MAX_TRACK1_SUBMISSIONS`).
- **Track 2:** Drug-repurposing dossier + GitHub URL + **3-minute pitch video**. Max **3 submissions** (`MAX_TRACK2_SUBMISSIONS`); the panel reviews the latest.
- **Scoring contract:** full match at rank 1 = 100 rank points + F-max 1.0; one-allele-wrong = 50 points + F-max 0.5; hedging rows do not help. Perfect Track 1 scores already exist on the leaderboard — the differentiator is the **methods write-up**, so the strategy is one clean upload with the report attached.
- **Privacy rules (binding):** gated genome/FASTQ/VCF/clinical files never leave AIRE scratch; never committed to GitHub/Hub; deleted within 30 days of close; never pasted into third-party LLM APIs. Only derived findings, code, reports, and permitted summaries are published.
- **AI assistance disclosure (required 28 Aug 2026):** Cursor / Devin agent sessions on commercial plans; Anthropic API / Claude / Grok; commercial terms, no training on customer content.

### Infrastructure

- **HPC:** University of Leeds AIRE cluster (`nodes`/`gpu` Slurm partitions).
- **Scratch root:** `/scratch/kcwp264` ≡ `/mnt/scratch/kcwp264`.
- **Conda envs:** `mva-hackathon` (VEP/Track 1), `cjepa` (ESM-1v GPU), `mva-hackathon-lincs` (GEO/LINCS, R-based DE).
- **Test suite:** `pytest tests/` — **39/39 pass** as of 11 Sep 2026.

---

## 2. The proband and the causal genotype

**Proband EX2312012** (submitted as `PROBAND01`): child with embryonal rhabdomyosarcoma, intrauterine growth restriction, short stature, microcephaly — consistent with **MVA1** (Mosaic Variegated Aneuploidy syndrome 1, OMIM 257300).

### The submitted call (one row, `finding_type=primary`, EPCR 0.95)

| | Variant 1 | Variant 2 |
|---|---|---|
| GRCh38 | `chr15:40209701 T>G` | `chr15:40220612 T>G` |
| HGVS (NM_001211.6) | `c.2210T>G` | `c.3006T>G` |
| Protein | **p.Leu737Ter** (stop-gain) | **p.Asn1002Lys** (missense) |
| Class | Nonsense, C-terminal truncation | C-lobe pseudokinase missense |
| ClinVar | **VCV000533901.9**, Pathogenic/Likely pathogenic for MVA1, multiple submitters, last eval 2024/10/09 | Protein change exists as **VCV004600147.1** VUS via `c.3006T>A` (single submitter SCV007198955, last eval 19 Sep 2025, generic trait); our exact `c.3006T>G` allele is ClinVar-absent |
| dbSNP | rs759242053 | rs2542593804 |
| gnomAD v4 | exomes AC=115 (AF 7.87e-05), genomes AC=5 (AF 3.29e-05) — recessive-carrier compatible | 1 exome allele (AF 6.84e-07); genomes absent — effectively singleton |
| VAF | ≈0.5 (het); VCF AD 21/25; BAM DP 47–48 | ≈0.5 (het); VCF AD 15/13; BAM DP 27–29 |

### Why this pair

1. **Gene:** biallelic *BUB1B* is the founding MVA1 locus (Hanks et al. 2004). Phenotype points at SAC-core genes, not centrosomal MVA genes.
2. **Architecture:** nonsense/null + hypomorphic pseudokinase missense is the textbook viable MVA1 genotype. Two PTVs would more often be embryonic lethal; homozygous null is lethal. Surviving patients retain residual BUBR1 (**11% ± 3%** in *BubR1^H/H* mice, Baker 2004 — a mouse value, not measured in the proband).
3. **Allele 1** is a known pathogenic MVA1 stop-gain, functionally in the same class as the canonical `c.2211insGTTA` (one codon away). KEN/ABBA motifs retained but NMD/instability expected.
4. **Allele 2** sits in the BUBR1 pseudokinase C-lobe, 10 residues from the documented destabilising MVA1 missense **L1012P** (Suijkerbuijk 2010; AF2 PAE distance N1002–L1012 = 3 Å). Predicted to act as a destabilising hypomorph, not a null. AlphaMissense 0.9229 (likely pathogenic); ESM-1v LLR −0.110 (mild) — predictors conflict, and both are reported honestly.
5. **Uniqueness:** after AF-key-corrected filtering of the 15-gene panel, only *BUB1B* carried two rare functional alleles. That uniqueness — not an ML ranker — is why the CSV has one row.
6. **Cancer context:** BUB1B-MVA carries ~37% cancer frequency (early-childhood rhabdomyosarcoma, Wilms, leukaemia) — consistent with the proband's presentation.

---

## 3. Track 1: variant evidence

### Computational predictor summary

| Predictor | p.Leu737Ter | p.Asn1002Lys | Notes |
|---|---|---|---|
| Consequence | PTV (stop_gained) → score 0.99 | Missense → 0.7·popEVE + 0.3·AM | popEVE missing → AM doubly weighted (≈0.92) |
| AlphaMissense | — | **0.9229** (likely pathogenic; threshold 0.564) | Structure-aware; the stronger signal |
| popEVE | — | **absent** (novel codon change) | — |
| ESM-1v (5-model ensemble, masked LLR, residues 29–1050) | — | **−0.110** | 3rd-mildest of 19 substitutions at residue 1002; less damaging than ClinVar B/LB median (−0.161); **18/34** in B/LB ranking; **falsified** the pre-registered hypothesis "N1002K ≈ L1012P" (gap to L1012P −1.801 = 1.69 nats > 0.5 threshold) |
| SpliceAI (-D 500 candidate run; -D 4999 deep sweep) | max DS **0.03** | max DS **0.02** | Below 0.2 threshold; no BUB1B-annotated variant in 120 kb sweep exceeds 0.03; closes the "cryptic splice third hit" falsifier |
| AlphaGenome AVI | Phred **33.76**, top 0.042%, top modality Protein Termination (FI 1.484), splicing FI 0.027 | Phred **25.61**, top 0.275%, top modality AlphaMissense (FI 0.761), splicing FI 0.015 | Supportive only; not independent of AlphaMissense; not a functional readout |
| ClinVar | VCV000533901.9 P/LP (MVA1) | VCV004600147.1 VUS (generic trait, `c.3006T>A`) | Our `c.3006T>G` absent from ClinVar |
| gnomAD v4 | AF 7.87e-05 exomes / 3.29e-05 genomes | AF 6.84e-07 exomes; absent genomes | Both pass AF ≤ 0.001 rarity gate |

### Scoring path to EPCR 0.95

`pair_score = 0.99 × ~0.92 ≈ 0.91` → floored to `primary_epcr: 0.95`. Submitted as the single primary row. The local scorer clone (`src/mva_hackathon/eval/scorer.py`) mirrors the official rank-points/F-max contract; ground truth was never opened.

### What the report explicitly does NOT claim

- p.Asn1002Lys is **not** claimed equivalent to L1012P (ESM-1v falsified this).
- Phase is **not** molecularly confirmed (see §4).
- The ~11% residual BUBR1 is a mouse literature value, not a proband measurement.
- The UGA stop is suppressible *in principle* but untested in this child.
- `p.Glu756*` is a different historical alias — not used.
- `priority_bonus` code is dead code and was not added to EPCR.

---

## 4. The phasing problem

This is the central scientific limitation of the submission and the most carefully-worded part of the dossier.

### Read-backed phasing (WhatsHap on realigned WGS BAM)

The 8 gated FASTQs (~84 GB) were downloaded and realigned (bwa-mem2, name-sort + fixmate + markdup; 939 M read pairs, 99.5% mapped, 98.2% proper pairs), then WhatsHap phased the chr15 window:

| Statistic | Value |
|---|---|
| Heterozygous SNVs in window | 41 |
| Phased | 30 (73.2%) |
| Blocks | 8 |
| Longest block | 2,822 bp (10 variants) |
| Mean/median block length | 938 / 691 bp |
| Distance between target variants | **10,911 bp** |
| Intervening het SNV | `15:40216470 A>G` (exactly one) — BUB1B intron 20/22, absent from gnomAD v4/dbSNP/ClinVar (rare deep-intronic; SpliceAI DS 0.00) |
| Sub-gaps around intervening SNV | 6.77 kb and 4.14 kb |
| Max observed fragment length (TLEN) | **~1,348 bp** |
| Phased het sites connecting targets | **0** |
| Target phase sets | `15:40209701 GT=0/1 PS=` — empty; `15:40220612 GT=0/1 PS=` — empty |

**Verdict: UNRESOLVED.** No read pair spans >9 kb; no chain of read-connected heterozygous sites bridges the 10.9 kb interval. This is a **structural limitation of the short-read library**, not evidence against trans.

### Statistical phasing (SHAPEIT5) — evaluated and rejected as definitive

- `phase_common` can use an external reference panel; `phase_rare` phases rare variants onto a common scaffold and is recommended for cohorts **>2,000 samples**.
- `phase_rare` has no external-panel argument; a singleton (AC=1 in gnomAD) cannot be learned from a panel.
- `FORMAT/PP` is per-site confidence, not pairwise P(trans). A claim like "P(trans)=0.99" from this setup would be unsupported.
- SHAPEIT5 may be run only as an exploratory sensitivity analysis, never as definitive confirmation.

### The calibrated conclusion (language used consistently across all docs)

> The two *BUB1B* variants are **presumed compound heterozygous** based on: (i) the autosomal-recessive MVA1 phenotype; (ii) the canonical truncating + hypomorphic missense architecture (Hanks et al. 2004); (iii) the absence of a third *BUB1B* coding/splice candidate in the scanned 250 kb region (88 upstream variants all common/repeat; 3 novel variants in window are the two targets plus the intervening SNV); (iv) exclusion of obvious *CEP57*/*TRIP13* pathogenic variants; (v) a systematic locus falsifier audit (`supplement/track1/locus_falsifier_audit.md`) ruling out all known ClinVar P/LP BUB1B alleles, deep-intronic splice variants, the ~44 kb upstream regulatory variant, CNVs, SVs/Alu-SVA breakpoints, chr15 isodisomy, and hidden homozygous alleles. WhatsHap read-backed phasing is **UNRESOLVED** because the 10,911 bp interval exceeds the library's maximum fragment length and no read-connected chain bridges it. **Parental testing or targeted long-read sequencing is required for definitive phase confirmation.**

Parsimony additionally favors trans: if both coding alleles were cis, the other chromosome would carry no *BUB1B* lesion — inconsistent with MVA1 requiring biallelic impairment.

### Structural evidence supporting the missense allele

- AF2 pLDDT: L737 = 73.6; N1002 = 91.1; L1012 = 95.3.
- PAE distances: N1002–L1012 = 3 Å (same structural neighborhood); L737–N1002 = 17 Å.
- N1002K is in domain 3 (aa 755–1043) — the kinase C-lobe co-localized with L1012P.

---

## 5. Molecular phasing validation plan

`docs/phasing_validation_plan.md` (10 Sep 2026) ranks the confirmation routes:

1. **Parental genotyping** — strongest, simplest confirmation (requires availability/consent).
2. **Long-range PCR spanning both variants + long-read sequencing** (ONT or PacBio) — the preferred direct molecular proof.
3. **Targeted genomic long-read** (Cas9 enrichment / adaptive sampling).
4. **Linked-read/Hi-C-type** approaches — less direct alternatives.

### In silico primers designed (`scripts/design_lrpcr_primers.py`, primer3-py 2.3.1)

| Primer | Sequence (5'→3') | Tm | GC% | Length | Position |
|---|---|---|---|---|---|
| BUB1B-LR-F | `CCTACTCAGTCACCATGGTGTTCAC` | 63.0 °C | 52% | 25 nt | chr15:40209640–40209664 |
| BUB1B-LR-R | `GCAAAGCCCCAGGACTAGTTAACTT` | 63.0 °C | 48% | 25 nt | 3'-end at chr15:40220748 |

- **Expected amplicon: ~11,109 bp** (chr15:40209640–40220748) spanning both target variants and the intervening het SNV.
- Risks documented: allele dropout, PCR failure in GC-rich/repetitive regions, polymerase errors, amplification bias, structural variation; need confirmation of both variant alleles and nearby het markers.
- In silico only — wet-lab validation not performed (and out of scope for a computational submission).

---

## 6. Track 2: therapeutic hypothesis

**Title:** "A Mutation-Specific, Stabilise-and-De-Stress Stack for BUB1B-MVA1"

MVA1 is hypomorphic SAC failure → mosaic aneuploidy → proteotoxic + lysosomal stress → ROS → micronuclei → cGAS-STING → IFN/IL-6. The proposal is **two-pronged upstream**; everything else is downstream damage control:

- **Prong A — direct rescue of the stop-gain allele:** UGA translational readthrough of p.Leu737Ter. UGA is the most suppressible stop class; readthrough inserts near-cognate Trp/Arg/Cys, completing the 1050-aa BUBR1 (with a substitution at 737 that may itself impair folding — a required test).
- **Prong B — stabilisation of residual BUBR1:** SIRT2 deacetylates BUBR1 at K668, blocking ubiquitylation/proteasomal decay (North et al. 2014). NAD+ precursors are the pharmacological handle — but as mechanistic comparators only.
- **Downstream tiers:** proteostasis (Ravicti, arimoclomol) → mTORC1-independent autophagy (trehalose, spermidine) → ROS/Nrf2 (explicit cancer warnings) → senescence adjunct (dasatinib+quercetin) → biomarker-gated JAK/IL-6 blockade.

**Evidence-gating rule:** any therapy that could rescue aneuploid cells or impair tumour surveillance (HSF1, Nrf2, JAK/IL-6, systemic antioxidants, rapalogs) ranks below proteostasis/autophagy and is paired with biomarker gates and oncology surveillance.

### Key literature corrections baked into the dossier

- **North et al. 2014 (EMBO J 33:1438–1453):** the +58% median lifespan extension (males +123%) was **SIRT2 transgenic overexpression** in *BubR1^H/H* — **not NMN**. NMN only raised BUBR1 protein.
- **González-Blanco et al. 2026 (Nat Commun 17:3829):** larval rapamycin and TOR RNAi rescued aneuploid *Drosophila* **neuroblast counts, not brain size**; brain-size rescue was **Sod2 and GTPx-1 overexpression**, not rapamycin and not NAC.
- **Bonatti et al. 1998 (Chromosoma 107:498):** rapamycin itself induces chromosome malsegregation and CREST-positive micronuclei → rapalogs are a mechanistic **anti-target concern** in MVA1, not a rescue lead; gated by micronucleus/missegregation assays.
- **Baker 2013 (Cell Rep):** unpublished rapamycin-diet note in *BubR1^H/H* mice was not positive.

---

## 7. Track 2: candidate table

Track 2 is restricted to **existing, market-approved medications**. Statuses: APPROVED_MEDICATION (stack-eligible), INVESTIGATIONAL / SUPPLEMENT_FOOD_GRAS (comparators only), ANTI_TARGET (excluded).

| # | Tier | Drug | Axis | Regulatory status | Key caveat |
|---|---|---|---|---|---|
| 1 | Tier1-DIRECT-RESCUE | **Ataluren (PTC124/Translarna)** | UGA readthrough of p.Leu737Ter | APPROVED: **UK/MHRA conditional only** (nmDMD ≥2 yr). NOT FDA (NDA resubmission withdrawn 12 Feb 2026); EMA not renewed Mar 2025; MHRA actively reviewing | Allele-specific readthrough untested; needs ≥10% full-length BUBR1 on WB |
| 2 | Tier1-INVESTIGATIONAL | **ELX-02** | ERSG UGA readthrough | INVESTIGATIONAL (Ph2 CF; Alport trials) | Future-research tier only |
| 3–4 | Tier1-STABILISATION | **NMN / NR** | SIRT2/BUBR1 K668 | SUPPLEMENT_FOOD_GRAS (NMN = FDA NDI article; NR = FDA GRAS food letter) | Mechanistic comparators; not approved drugs |
| 5 | Tier2-PROTEOSTASIS | **Glycerol phenylbutyrate (Ravicti)** | ER stress/proteostasis/HDAC | APPROVED: FDA+EMA (UCD incl. infants) | Evidence extrapolated from trisomy iPSC neurons (Fisher 2020), not MVA |
| 6 | Tier2-PROTEOSTASIS | **Arimoclomol** | HSF1/HSP, lysosomal | APPROVED: **FDA only, in combination with miglustat**, NPC ≥2 yr (Miplyffa, 20 Sep 2024); EMA refused Meplyffa 23 Jul 2026 (2nd EU attempt; re-exam requested) | HSF1 amplification could protect aneuploid cancer clones → below Ravicti + oncology monitoring |
| 7–8 | Tier2-AUTOPHAGY | **Trehalose / spermidine** | TFEB, mTORC1-independent autophagy | SUPPLEMENT_FOOD_GRAS | Comparators; no BUBR1 data; bioavailability limits |
| 9 | Tier2-AUTOPHAGY | **Rapamycin (sirolimus)** | mTORC1 via FKBP1A | APPROVED: FDA+EMA | **Potential anti-target** (aneugenic); WEAK MIXED LINCS; micronucleus assay-gated |
| 10 | Tier2-AUTOPHAGY | **Everolimus** | mTORC1 via FKBP1A | APPROVED: FDA+EMA (TSC-SEGA ≥1 yr) | Mimic-only in L2S2; supportive at most |
| 11 | Tier2-ROS | **NAC** | ROS | APPROVED: FDA+EMA | Poor BBB; pro-metastatic in melanoma models (Piskounova 2015) |
| 12 | Tier2-ROS | **MitoQ** | Mito ROS | SUPPLEMENT_FOOD_GRAS | Comparator only |
| 13 | Tier2-ROS/Nrf2 | **Omaveloxolone** | NFE2L2/Nrf2 | APPROVED: FDA+EMA (FA ≥16 yr) | Nrf2 oncogenic risk |
| 14 | Tier2-SENESCENCE | **Dasatinib + quercetin** | Senolytic adjunct | Dasatinib APPROVED (Ph+ CML/ALL ≥1 yr); quercetin = supplement | Oncology-supervised adjunct; WEAK MIXED LINCS |
| 16 | Tier3-SYSTEMIC | **Baricitinib** | JAK1/2 | APPROVED: FDA (RA/alopecia/COVID); **EMA JIA ≥2 yr**; paediatric expanded-access in interferonopathies | Biomarker-gated only (ISG/IL-6); tumour-surveillance risk |
| 17 | Tier3-SYSTEMIC | **Ruxolitinib** | JAK1/2 | APPROVED: FDA+EMA (paediatric GVHD) | Same gating |
| 18 | Tier3-SYSTEMIC | **Tocilizumab** | IL6R | APPROVED: FDA+EMA (sJIA, CRS) | Same gating |
| EXCL | Anti-target | **TTK/MPS1 inhibitors** (BAY-1161909, BAY-1217389, CFI-402257) | SAC override | ANTI_TARGET | Would worsen aneuploidy |
| EXCL | Anti-target | **Aurora B inhibitors** (barasertib, GSK-1070916) | Error correction | ANTI_TARGET | Would worsen mis-segregation |
| EXCL | Anti-target | **STING agonists** (ADU-S100) | TMEM173 | ANTI_TARGET | Would amplify neuroinflammation |

### Regulatory audit refresh (10 Sep 2026)

- Ataluren: PTC withdrew the resubmitted NDA **12 Feb 2026** — no live US application. UK licence under active MHRA review post-EU-non-renewal → treat as time-sensitive.
- Arimoclomol: EU brand is **Meplyffa** (not Miplyffa); CHMP negative opinion Jul 2026 was Zevra's second EU attempt (first MAA withdrawn 2022); re-examination requested within the 15-day window.
- No new stop-codon-readthrough drug approved anywhere since early 2025.

### Biomarker-gated validation plan (assay → go/no-go)

1a. Ataluren → WB full-length BUBR1 ≥10% | 1b. NMN/NR/SIRT2 → BUBR1 protein ≥20% | 2. Ravicti/arimoclomol → aggregate/ER-stress/apoptosis reduction ≥30% | 3. trehalose/spermidine → LC3-II/p62/TFEB (additive only if lysosomal stress shown) | 4. ISG score, IL-6, CRP → JAK/IL-6 only if elevated | 5. oncology surveillance throughout; unexplained cytopenia/mass → hold Tier 3.

---

## 8. LINCS transcriptomic screen and firewall

### Signatures queried (9 contrast×size definitions across 3 GEO series — explicitly NOT 9 independent datasets)

- **GSE22206** (human MVA microarray, GPL6104): pooled case-vs-control, LCL, fibroblast at 100/150/250 genes. Caveat: 4 cases (2 LCL + 2 fibro) and 6 controls from a single affected donor; tissue covariate; not a replicated signature. The 100-gene down-list = 86 FDR + 14 nominal genes; larger lists increasingly nominal-dominated.
- **GSE134781** (early mouse hypomorph, 3-mo muscle RNA-seq): +/L1002P, +/X753 vs WT.
- **GSE134780** (late mouse hypomorph, 10-mo muscle + fat RNA-seq): H/L1002P, H/H vs WT.
- GSE247267 produced no DEGs → not queried.

DE: limma (microarray) / edgeR+limma-voom (RNA-seq), BH correction; nominal P<0.01 fallback where FDR yield was thin (tracked in `signature_composition.csv`).

### Engines

- **L2S2** (Ma'ayan Lab `pairedEnrich` GraphQL, `https://l2s2.maayanlab.cloud/graphql`): three directional Fisher/BH results per drug — `adj_pvalue` (non-directional), `adj_pvalue_up` (**mimic**), `adj_pvalue_down` (**reverse/rescue**). Repurposing gates on `adj_pvalue_down < 0.05`.
- **L1000CDS2** (legacy CMap): overlap scores only; positive score = reversal direction; counts toward the second engine.

### Firewall gates (in order)

1. Not matched to candidate/axis → REJECT
2. Regulatory status ANTI_TARGET / INVESTIGATIONAL / SUPPLEMENT_FOOD_GRAS → REJECT
3. Not LINCS-eligible → REJECT
4. Paediatric safety fail (perhexiline, thalidomide, lenalidomide) → REJECT
5. Anti-target mechanism keywords (TTK/MPS1/Aurora B/STING agonist/PLK1/CDK1 inhibitors) → REJECT
6. Cytotoxic-cancer keywords (HSP90, proteasome, topoisomerase, tubulin, alkylators, PARP, anthracyclines, etc.) → REJECT
7. Broad cancer-kinase off-axis → REJECT
8. L1000CDS2 false-rescue (>25% overlap genes are generic stress markers) → REJECT
9. No significant FDR signal → REJECT
10. Only 1 significant signature total → WEAK
11. **MIXED L2S2 directionality** (FDR-sig reverse AND mimic) → WEAK (data-driven penalty)
12. Supportive/adjunct/caution tier → WEAK

### Result — and the rescue-sort validation

| Run | Universe | ACCEPT | WEAK | REJECT |
|---|---|---|---|---|
| Original (mimic-sorted L2S2 + L1000CDS2) | 676 drugs | **0** | **2** | 674 |
| Rescue-sorted (`sortby=adj_pvalue_down`, L2S2 only) | 474 drugs | **0** | **2** | 472 |

**WEAK hits (both MIXED):**
- **Sirolimus:** 1 FDR reverse in GSE22206 pooled 100-gene (`adj_pvalue_down = 9.14e-05`; rescue-sorted: 1.97e-04) but 4→9 FDR-significant **mimic** signatures. Not robust to gene-list size (mimic at 150/250 genes: adj_p_up ~1e-13/5.8e-08). Plus the Bonatti aneugenicity caveat → context-specific observation with anti-target concern, not a lead.
- **Dasatinib:** 1 FDR reverse (`adj_pvalue_down = 1.51e-05`; rescue-sorted: 8.90e-05), 2→5 mimic. Conditional oncology-supervised senolytic adjunct at most.

**Rejected examples:** everolimus (general+mimic FDR, zero reverse) — REJECT; perhexiline (L1000CDS2-only hits, hepatotoxic, explicit "not for children") — REJECT.

**Key interpretation:** the rescue-sorted re-query retrieved *more* mimic signatures, strengthening the MIXED penalty — the zero-ACCEPT conclusion is not a retrieval-sort artifact. LINCS measures steady-state mRNA in transformed cell lines; it cannot see translational readthrough or post-translational stabilisation, so the absence of Ataluren/NMN/Ravicti/arimoclomol signatures is platform-boundary, not counter-evidence.

---

## 9. ChEMBL target-first screen

`track2/drug_screen.py` queries the ChEMBL mechanism endpoint for 15 axis proteins: BUB1B, SIRT2, MTOR, **FKBP1A**, ATG7, ATG5, SOD2, NFE2L2, TMEM173, CGAS, JAK1, JAK2, IL6R, TTK, AURKB. `--approved-only` filters `max_phase == 4`.

- **Critical retrieval fix:** sirolimus/everolimus/temsirolimus come back under **FKBP1A** (CHEMBL1902), not MTOR — the ternary-complex mechanism. Ridaforolimus is the only direct-MTOR-kinase hit.
- Output: 92 drug-target rows → 32 approved-only **target-screen rows** (mechanistically eligible matches, explicitly *not* final therapeutic leads).
- JAK1/JAK2 → baricitinib, ruxolitinib, fedratinib; IL6R → tocilizumab, sarilumab; NFE2L2 → omaveloxolone.
- Ataluren, ELX-02, Ravicti, trehalose, spermidine are **not** ChEMBL-screenable (ribosomal/general-proteostasis targets) — added by literature curation.
- PrimeKG skip-gram did **not** recover rapalogs near MVA (sirolimus rank 22.0/37, 16.7/31 without anti-target seeds; JAK/IL-6 neighborhood topped the list) — pre-registered H2 falsified. No claim that "graph/AI discovered the therapy"; TxGNN was never trained.

---

## 10. Chronological history

| Phase | Dates | What happened |
|---|---|---|
| 1. Scaffold + Track 1 pipeline | 27 Aug | Repo on AIRE; env w/ VEP 116; 15-gene panel; run_track1.py. Bugs fixed: nonexistent `gnomad_af` key (let common SNPs through), SpliceAI `-D` cap (500 vs max 4999), cancer-bonus dead code, AM-vs-popEVE confusion. First CSV: BUB1B compound-het, EPCR 0.95, one row. |
| 2. Track 2 dossier + first audits | 28–31 Aug | Two-pronged stack drafted. Corrections: North 2014 lifespan is SIRT2-Tg not NMN; ataluren not FDA/EMA (UK/MHRA conditional only). |
| 3. Pre-registered falsification experiments | 31 Aug–1 Sep | ESM-1v 5-model ensemble on O60566 (windowed — ESM-1v caps at 1022 aa, BUBR1 is 1050): H1 "N1002K≈L1012P" **falsified** (−0.110 vs −1.801, gap 1.69 nats). PrimeKG H2 "sirolimus near MVA" **falsified**. ClinVar B/LB control: N1002K 18/34, below B/LB median. |
| 4. LINCS screen + directionality fix | 1–3 Sep | GEO signatures built; L2S2+L1000CDS2 queried. **Corrected:** firewall must gate on `adj_pvalue_down` (reverse), not non-directional `adj_pvalue`; MIXED-direction penalty added. Result 0/2/674. Rapamycin aneugenicity caveat added. |
| 5. First-principles synthesis + WGS phasing | 7–9 Sep | Corrections: "novel missense"→ClinVar VUS via c.3006T>A; "absent from gnomAD"→exact v4 counts; residual→11%±3%. FASTQs realigned (bwa-mem2, 939M pairs); WhatsHap → **UNRESOLVED** (structural); SHAPEIT5 evaluated → not definitive for singletons; LRPCR primers designed (~11.1 kb amplicon). Decision memo: presumed compound het, disclose limitation, recommend parental/long-read. |
| 6. Post-audit pre-submission | 10–11 Sep | Regulatory refresh (ataluren NDA withdrawn Feb 2026; arimoclomol EU Meplyffa refused Jul 2026, re-exam pending). AlphaGenome AVI scored both variants. SpliceAI deep sweep −D 4999 completed. L2S2 rescue-sorted re-query → same 0/2 conclusion. ClinVar API re-verification → accession format `VCV004600147.1`, date 19 Sep 2025, generic trait. Reports/tests updated; repo restructured with `supplement/track1/` + submission xlsx methods files. **39/39 tests pass.** |

---

## 11. Major errors found and corrected

| Error | Correction | Where |
|---|---|---|
| `gnomad_af` key didn't exist → common SNPs passed filter | Read `gnomADg_AF`/`gnomADe_AF`/`AF` | `filter.py`/`parse.py`; WHAT_WE_DID |
| SpliceAI `-D 10000` exceeds max | Working distance 500 (candidates); deep sweep 4999 | `vep.py` |
| Cancer `priority_bonus` could push EPCR >1 | Dead code, never applied | `run_track1.py` |
| 0.9229 misattributed to popEVE | It's AlphaMissense; popEVE absent | report + first-principles |
| North 2014 lifespan credited to NMN | It was SIRT2-Tg overexpression | Track 2 report §3, storyboard |
| Ataluren "FDA/EMA approved" | UK/MHRA conditional only; EMA non-renewed; NDA withdrawn Feb 2026 | Track 2 report throughout |
| LINCS rescue claimed on non-directional `adj_pvalue` | Gate on `adj_pvalue_down`; MIXED penalty; rescue-sort validation | `04_firewall.py`, report §LINCS |
| ESM-1v "mild" stated unqualified | Now: "mild-by-LLR, not L1012P-class; LLR is a relative-stability score, not functional-neutrality proof" | report, README, storyboard |
| "32 candidates" implied final leads | Reframed as "target-screen rows" | storyboard VO |
| "novel missense" for N1002K | ClinVar VUS exists for protein change via c.3006T>A | report + first-principles |
| "absent from gnomAD" | Exact v4 counts now reported | report |
| ClinVar `VCV4600147` (short form) | `VCV004600147.1` | 7 files corrected |
| ClinVar date "Jan 2026" | **19 Sep 2025** (API-verified) | all docs |
| SHAPEIT5 over-claimed as confirmatory | Evaluated → not definitive for singletons; molecular route documented | phasing plan + decision memo |
| L2S2 mimic-sorted retrieval limitation | Rescue-sorted re-query executed; conclusion unchanged | `rescue_firewall/comparison_summary.md` |

---

## 12. Tools, databases, and code

| Tool/DB | Role |
|---|---|
| Ensembl VEP 116 (GRCh38 offline cache) | Variant annotation (AlphaMissense + popEVE/EVE plugins) |
| AlphaMissense | Missense pathogenicity (0.9229 for N1002K) |
| popEVE (sigmoid at −5.056) | Population-weighted missense term (absent for N1002K) |
| ESM-1v ×5 (650M UR90S) | Masked LLR; windowed residues 29–1050 |
| SpliceAI 1.3.1 | Splice deltas (−D 500 candidates; −D 4999 deep sweep) |
| AlphaGenome AVI | Aggregate variant impact (33.76 / 25.61 Phred) |
| ClinVar/dbSNP/gnomAD v4 | Variant records, allele frequencies (API-verified) |
| bwa-mem2 + samtools + mosdepth | FASTQ→BAM realignment, depth/aneuploidy landscape |
| WhatsHap | Read-backed phasing → UNRESOLVED |
| SHAPEIT5 | Statistical phasing — assessed, rejected as definitive |
| primer3-py 2.3.1 + samtools faidx | In silico LRPCR primer design |
| AlphaFold2 (AF-O60566) | pLDDT/PAE structural context |
| ChEMBL REST API | Target-first approved-drug screen (FKBP1A key) |
| PrimeKG skip-gram | KG neighborhood (H2 falsified) |
| Open Targets 26.06 | Target-disease-drug context |
| GEO + limma/edgeR | DE signatures (GSE22206, GSE134781, GSE134780) |
| LINCS L2S2 `pairedEnrich` + L1000CDS2 | Transcriptomic reversal engines + firewall |
| `src/mva_hackathon/` | Package: variants/{parse,filter,score,vep,spliceai,pair,writer}, eval/scorer, research/{clinvar,esm1v,opentargets,primekg_embed} |
| `scripts/` | run_track1, design_lrpcr_primers, ESM-1v/ClinVar/PrimeKG/figures + `slurm/` incl. 4-step WGS pipeline |
| `track2/` | drug_screen.py + lincs/{00 fetch, 02 DE (R), 03/03b queries, 04 firewall} |

---

## 13. Scoring code and configuration

### `configs/config.yaml` (verbatim key values)

```yaml
filter:  gnomad_max_af: 0.001 | spliceai_min_delta: 0.2 | spliceai_high_delta: 0.5
         popeve_severe: -5.056 | alphamissense_benign: 0.34 | alphamissense_likely_pathogenic: 0.564 | cadd_min: 20
scoring: missense_pop_weight: 0.7 | missense_am_weight: 0.3 | ptv_score: 0.99
writer:  primary_epcr: 0.95 | secondary_epcr_max: 0.15
```

### Panel (17 genes — extended Sept 2026)

SAC core: BUB1B, BUB1, MAD1L1, TRIP13, MAD2L1BP · Centrosome: CEP57, CEP192 · Minor spliceosome: CENATAC · **Atelis/MVA5-6: SLF2, SMC5** (added post-audit) · Extended SAC/kinetochore: CDC20, TTK, MAD2L1, BUB3, KNL1, AURKA, PLK1.

### Formulas (verbatim from `score.py`)

```python
popEVE_to_prob(p) = 1 / (1 + exp(p - (-5.056)))          # more negative → higher pathogenicity
variant_pathogenicity: PTV→0.99; missense→0.7·popEVE_sigmoid + 0.3·AM (AM back-fills pop term if absent);
                       splice-region→max DS>0; fallback→min(1, CADD/50)
pair_score(s1,s2) = max(1e-4, min(1, s1·s2))
epcr_from_pair: primary → max(0.95, min(1, pair)); secondary → clamp [0.05, 0.15]
```

Local evaluator (`eval/scorer.py`): rank tiers {1→100, 3→50, 5→25, 10→10}; F-max sweep over EPCR thresholds. Ground truth never opened.

---

## 14. Test suite

**39 tests, all passing** (11 Sep 2026).

- `tests/test_scorer.py` (16): scorer math (rank points, F-max, EPCR clamps, popEVE sigmoid shape, missense weighting) + report-integrity tests (calibrated phasing language incl. UNRESOLVED + no overclaiming phrases, AlphaGenome section present with both Phred values, SpliceAI sweep present with DS values, ClinVar accession `VCV004600147` + `19 Sep 2025` required and `VCV4600147`/`Jan 2026` forbidden, artifact existence checks).
- `tests/test_track2_lincs.py` (23): firewall outputs exist + status enum valid; MIXED never ACCEPT; sirolimus WEAK; zero ACCEPT in both original and rescue-sorted runs; comparison summary exists; candidate CSV LINCS columns; report contains LINCS section, denominator note, preclinical disclaimer, arimoclomol+miglustat, baricitinib JIA, rescue-sort mention, and no overclaiming phrases; storyboard contains ACCEPT=0/WEAK=2/REJECT=674, qualified ESM-1v, and target-screen-vs-leads language.

Run: `pytest tests/` in the `mva-hackathon` conda env.

---

## 15. Repository structure and privacy

```
submissions/   Ryukijano_bub1b-compoundhet.csv · Ryukijano_track1_report.md · Ryukijano_track1_methods.xlsx
               Ryukijano_track2_report.md · Ryukijano_track2_candidates.csv · Ryukijano_track2_methods.xlsx
               Ryukijano_pitch_storyboard.md
supplement/track1/   bub1b_avi_scores.json · bub1b_full_gene_spliceai.vcf · spliceai_summary.md · clinvar_verification.md
docs/          track1_first_principles.md · wgs_phasing_decision_memo.md · phasing_validation_plan.md · next_plan.md
track2/        track2_report.md · pitch_storyboard.md · drug_screen.py · data/ · lincs/{scripts,data,results,results/l2s2_rescue,results/rescue_firewall}
results/       wgs_phasing/{phasing_report.md, decision_memo.md, phasing_blocks.gtf, chr15_phased.vcf, aneuploidy_landscape.*, mosdepth outputs, afdb/}
experiments/   2026-08-31_bub1b_computational/ (ESM-1v, PrimeKG, ClinVar B/LB outputs + SUMMARY.md)
src/mva_hackathon/ · scripts/ · tests/ · configs/ · environment.yaml
```

**Never committed:** `data/` gated genome/FASTQ/VCF, phenotype docx, VEP cache, PrimeKG kg.csv, heavy regenerable LINCS intermediates, local PDFs, `.cache/`. `.licenses/` holds ClinVar/dbSNP/gnomAD licenses.

---

## 16. Key numbers

| Item | Value |
|---|---|
| Variants | `chr15:40209701 T>G` (c.2210T>G, p.Leu737Ter) · `chr15:40220612 T>G` (c.3006T>G, p.Asn1002Lys) |
| Inter-variant distance | 10,911 bp |
| EPCR | 0.95 (single primary row) |
| ClinVar | VCV000533901.9 P/LP MVA1 · VCV004600147.1 VUS (c.3006T>A; our c.3006T>G absent) |
| gnomAD v4 | L737Ter AF 7.87e-05 ex / 3.29e-05 gen · N1002K 1 exome allele (6.84e-07) |
| AlphaMissense / ESM-1v / AVI | 0.9229 · −0.110 · 33.76 / 25.61 Phred |
| SpliceAI max DS (−D 4999, 120 kb, 135 vars) | 0.03 / 0.02 (threshold 0.2) |
| WhatsHap | 41 hets → 30 phased in 8 blocks; longest 2,822 bp; **UNRESOLVED** |
| WGS | 939 M pairs, 99.5% mapped, 98.2% proper; max TLEN ~1,348 bp |
| LRPCR | F `CCTACTCAGTCACCATGGTGTTCAC` / R `GCAAAGCCCCAGGACTAGTTAACTT`; ~11,109 bp amplicon |
| ChEMBL screen | 15 targets → 92 rows → 32 approved-only |
| LINCS firewall | ACCEPT 0 / WEAK 2 (sirolimus, dasatinib — both MIXED) / REJECT 674 · rescue-sorted: 0/2/472 — same conclusion |
| Sirolimus / dasatinib best reverse | adj_p_down 9.14e-05 / 1.51e-05 |
| Tests | 39/39 pass |
| Quota | Track 1: 6 shots (0 spent) · Track 2: 3 shots (0 spent) |

---

## 18. Adversarial quality audit (Sept 2026)

Four independent audits (genotype validation, Track 2 scientific review, competition landscape, pipeline false-negative analysis) plus direct locus-level falsifier checks were run against the submission.

### Track 1 — verdict: unique best-supported pair; one doc error fixed

- **Complete BUB1B het inventory (8 variants)** cross-checked against all ~100 ClinVar P/LP BUB1B alleles: the proband carries **no other known pathogenic allele** — including every deep-intronic splice variant (c.2386-2, c.2535+195, c.2285-2, c.36-1, c.967-2, c.239+2, c.751+1, c.581+1, c.2851-1, c.2009+1) and the ~44 kb upstream regulatory G>A (Ochiai 2014/Matsuura 2006).
- **No CNV** (uniform ~46x depth, no 500-bp window deviates), **no SV** (zero symbolic alleles; soft-clip clusters sequence-heterogeneous), **no chr15 isodisomy** (85k hets, normal per-Mb density), **no hidden homozygous allele** (6 hom calls, all AF 0.32–0.999).
- The intervening SNV `15:40216470 A>G` was reclassified: it is **BUB1B intron 20/22** (not "intergenic" as an earlier memo draft said) and is **absent from gnomAD v4/dbSNP (no rsID)/ClinVar** — a rare deep-intronic variant, SpliceAI DS 0.00, phyloP100way −0.41, ≥884 bp from splice sites. Disclosed as a rare non-coding variant; not a plausible second allele. Full audit: `supplement/track1/locus_falsifier_audit.md`.
- **Panel-completeness fix:** the original 15-gene panel missed **SLF2 and SMC5** (MVA5/MVA6 Atelis genes, Grange 2022). Post-hoc VEP check: only common missense polymorphisms (AF 0.48/0.88); all rare variants intronic/UTR — no causal candidate. Panel now 17 genes (`atelis` group added to `configs/panel.yaml`).
- **External re-verification (live):** L737Ter — ClinVar VCV000533901 P/LP multi-submitter (eval 2024-10-09); gnomAD AC=115 exomes, 0 hom; Loftee HC-LoF, 50_BP_RULE:PASS, DIST_FROM_LAST_EXON 742 (canonical NMD substrate); phyloP 2.91. N1002K — ClinVar VUS VCV004600147 via c.3006T>A (our c.3006T>G ClinVar-absent); gnomAD AC=1 exome; SIFT 0.01/PP 0.997/AM 0.9229; phyloP **4.80**; C-lobe of pseudokinase, 10 residues from L1012P.
- **Upstream regulatory SNP:** exact coordinate chr15:40,117,088 G>A (Ochiai 2014; c.-44133G>A) — no call in proband VCF at 46x depth = homozygous reference. Excluded.
- **Structural (UniProt O60566 / AlphaFold):** L737Ter deletes the whole pseudokinase domain (750–1045) + C-terminal Cdc20 surface; KEN1/2, D-box, ABBA1/2, TPR, GLEBS, KARD all retained. N1002 is in the ordered C-lobe (945–1040), not the catalytic site.
- **Residual disclosed limitation:** a truly novel cryptic mechanism below SNV-caller/≤200-bp resolution (small intronic Alu/SVA insertion, pseudoexon) cannot be fully excluded without long-read/RNA-seq.

### Track 2 — verdict: mechanism correct, lead drug was wrong; fixed

- **The dominant failure mode was under-weighted:** `p.Leu737Ter` is a canonical NMD substrate (PTC ~10 kb upstream of the terminal exon junction), so **ataluren alone has essentially no transcript substrate** — it does not inhibit NMD.
- **Added amlexanox** (Aphthasol; FDA-approved 5% topical oral paste) as the mechanistically matched Tier 1a option — it is the only approved small molecule with **dual PTC-readthrough + NMD-inhibition (UPF1)** activity, addressing the exact failure mode. Honest caveats: approved only as a topical paste; systemic nonsense-suppression use is off-label/investigational.
- **Filled the supplement-only autophagy tier** with two approved mTORC1-independent inducers: **metformin** (deep paediatric experience) and **rilmenidine** (UK/EU-approved; Bitto 2023).
- Added the **aneuploidy-as-vulnerability** counterpoint (Cohen-Sharir 2021; KIF18A dependence) so the anti-target exclusions are framed as mechanism-consistent, not one-sided.
- Candidate CSV gained 3 rows (amlexanox rank 2, metformin, rilmenidine); submission copies synced.

## 17. Outstanding items

1. **Track 2 3-minute pitch video** — the only true blocker. Storyboard ready (`track2/pitch_storyboard.md`); record 1080p, trim to 180 s, upload unlisted (YouTube/Vimeo), include preclinical-disclaimer line, no genomic coordinates on screen.
2. **Track 1 upload** — one clean shot: CSV + report + GitHub URL + LLM-usage statement (methods xlsx prepared).
3. **Submission-day re-verification** — ClinVar VCV000533901/VCV004600147 and gnomAD v4 counts; ataluren UK/MHRA status; arimoclomol EU re-examination outcome (all live, time-sensitive).
4. **Repo public flip** 24–25 Oct; gated data deletion within 30 days of close.
5. **Optional/nice-to-have:** ClinVar benign-only control for ESM-1v B/LB comparison (partially covered by the 34-missense control); L1000CDS2 re-query under rescue-sort symmetry (currently L2S2-only in rescue run); parental/long-read phasing remains the definitive open scientific follow-up.
