# MVA Hackathon 2026 — Track 2: A Mutation-Specific, Stabilise-and-De-Stress Stack for BUB1B-MVA1

**Proband:** EX2312012 (MVA1; c.2210T>G p.Leu737Ter / c.3006T>G p.Asn1002Lys, BUB1B compound het)

**Team:** Ryukijano

**Date (revised):** 2026-09-04

**Code:** https://github.com/Ryukijano/mva-hackathon-2026 (scripts: `track2/drug_screen.py`, `track2/data/track2_candidates.csv`, `track2/pitch_storyboard.md`, `track2/lincs/`)

**License:** CC BY 4.0

**AI assistance disclosure (28 Aug 2026 hackathon requirement):** Cursor / Devin agent sessions on commercial plans; Anthropic API / Claude Sonnet / Grok. Commercial terms, no training on customer content. The patient genome remained on scratch storage and was never pasted into third-party LLM APIs. Literature claims were verified against primary sources.

---

## Executive summary

The therapeutic hypothesis remains **two-pronged upstream**: direct rescue of the stop-gain allele and stabilisation of the residual BUBR1 pool. However, the regulatory audit described below forces an honest re-ranking.

1. **Direct rescue of the stop-gain allele** (`p.Leu737Ter`, `UGA`) with translational readthrough. **Ataluren** has a conditional marketing authorisation in the **UK/MHRA** for nonsense-mutation DMD; it is **not FDA-approved** and the **EMA conditional authorisation was not renewed (March 2025)**. Other non-US markets listed by the company or Alliance are not individually verified from primary regulatory sources in this repository. **ELX-02 is an investigational eukaryotic ribosome-selective glycoside** and is therefore placed in a **future-research tier**, not in the main Track 2 stack.
2. **Stabilisation of the residual BUBR1 pool** through the SIRT2/NAD+ axis is supported mechanistically, but **NMN and NR are dietary-supplement / food-use articles, not approved medications**, and are retained only as mechanistic comparators.

Downstream, the **approved-medication** leads are **glycerol phenylbutyrate (Ravicti)**, an FDA/EMA-approved sodium-free 4-PBA prodrug for urea-cycle disorders, and **arimoclomol (Miplyffa)**, FDA-approved in 2024 for Niemann-Pick C in patients >=2 years (EMA refused marketing authorisation in July 2026). Trehalose, spermidine, MitoQ and quercetin are supplements/food ingredients and are not leading Track 2 nominations. Rapamycin, everolimus, NAC and omaveloxolone are approved medications with paediatric labels, but are positioned as supportive or adjunctive only because of the MVA1 oncogenic-risk context. Systemic JAK/IL-6 blockade (baricitinib, ruxolitinib, tocilizumab) remains biomarker-gated and under oncology surveillance.

---

## Regulatory eligibility constraints

Track 2 of this hackathon is explicitly restricted to **existing, market-approved medications**. This constraint has direct consequences for the candidate list:

- An agent is eligible for the main proposed stack only when it is a currently approved medication in at least one named jurisdiction (FDA, EMA, MHRA, PMDA, national regulators, etc.).
- **Investigational agents** (e.g., ELX-02) and **supplements / food-GRAS articles** (e.g., NMN, NR, trehalose, spermidine, MitoQ, quercetin) are retained as mechanistic comparators or future-research options, but they are not leading Track 2 nominations.
- **Ataluren** is not FDA-approved and is no longer EMA-approved (conditional authorisation not renewed, March 2025). It therefore cannot be described as "FDA/EMA-approved". The only primary-source conditional marketing authorisation we verified is the **UK/MHRA** for nonsense-mutation DMD; other listed non-US jurisdictions are not individually confirmed here.
- **Arimoclomol** is FDA-approved for Niemann-Pick C in children >=2 years; the EMA refused marketing authorisation in July 2026, so it is no longer listed as FDA/EMA-approved.
- The anti-target rows (TTK/MPS1 inhibitors, Aurora B inhibitors, STING agonists) are retained but are categorised as `ANTI_TARGET` and are ineligible for any therapeutic stack.

The scientific rationale (readthrough of the UGA stop allele, SIRT2/BUBR1 K668 stabilisation, proteostasis/autophagy/ROS/inflammation de-stressing) and the two-pronged strategy are preserved; only the regulatory framing and eligibility claims have been corrected.

---

## LINCS L2S2 + L1000CDS2 transcriptomic-reversal screen and false-rescue firewall

As an exploratory consistency check beyond target matching, we queried 9 contrast/gene-list definitions across 3 GEO series representing human MVA and mouse *BubR1* hypomorphic models. These are **not 9 independent biological datasets**: the 100/150/250-gene lists from the same contrast are correlated, and the different GEO series represent distinct biological contexts.
1. **Human MVA (GSE22206):** primary fibroblasts, lymphoblastoid cell lines (LCLs), and pooled case vs control (microarray, GPL6104).
2. **Early mouse hypomorph (GSE134781):** gastrocnemius muscle from 3-month-old `+/L1002P` and `+/X753` vs WT (RNA-seq).
3. **Late mouse hypomorph (GSE134780):** 10-month-old `H/L1002P` and `H/H` vs WT in skeletal muscle and intra-abdominal adipose tissue (RNA-seq).

For each contrast, differential expression was performed using `limma` / `edgeR` with Benjamini-Hochberg (BH) correction. In mature tissues with robust chronic stress (GSE22206 and GSE134780 adipose), thousands of genes reached FDR < 0.05. In young or mildly affected muscle contrasts (GSE134781 and GSE134780 muscle), fewer genes passed genome-wide FDR, so top nominally differentially expressed genes (P < 0.01) were used for exploratory connectivity mapping across 100, 150, and 250 gene thresholds.

**Dual-engine querying & false-rescue firewall:**
- **Primary engine (L2S2):** Ma'ayan Lab GraphQL `pairedEnrich` consensus query against the public LINCS background. L2S2 returns three separate Fisher/BH results for each drug: `adj_pvalue` (non-directional enrichment), `adj_pvalue_up` (mimic: drug amplifies the disease signature), and `adj_pvalue_down` (reverse/rescue: drug opposes the disease signature). For repurposing we gate on **reverse** FDR (`adj_pvalue_down < 0.05`).
- **Secondary engine (L1000CDS2):** legacy CMap gene-set reverse search returning candidate perturbations with overlap scores. L1000CDS2 does not provide FDR-corrected p-values; scores are search/overlap metrics, not clinical efficacy scores. Only signatures with positive scores (reversal direction) count toward the engine count.
- **Firewall criteria:** All 676 unique drugs retrieved across both engines were evaluated against a multi-stage firewall:
  1. *Regulatory gate:* Current marketing approval in a recognized jurisdiction (FDA, EMA, MHRA, PMDA).
  2. *Pediatric safety gate:* Rejection of drugs explicitly contraindicated, unsafe, or lacking pediatric feasibility (e.g. perhexiline rejected due to severe concentration-dependent hepatotoxicity, peripheral neuropathy, and lack of pediatric indication).
  3. *Mechanism firewall:* Rejection of anti-targets (TTK/MPS1 inhibitors, Aurora B inhibitors, STING agonists) and non-specific cytotoxics (alkylators, topoisomerase poisons, broad cancer kinases).
  4. *Statistical reproducibility & directionality:* L2S2 rescue significance requires FDR-corrected reverse-pair enrichment (`adj_pvalue_down < 0.05`). The non-directional `adj_pvalue` is reported for transparency but does not, by itself, establish reversal. **Drugs with both reverse and mimic FDR-significant signatures (MIXED direction) are downgraded from ACCEPT to WEAK**, because inconsistent directionality means the transcriptomic signal is not robustly rescue-oriented.
  5. *Signature provenance:* Signatures are flagged when they contain nominal (P < 0.01) genes rather than FDR-significant genes. The GSE22206 pooled down-list at 100 genes contains 86 FDR + 14 nominal genes; at 150/250 genes the down-list is increasingly nominal-dominated.

**Known retrieval limitation:** The current saved L2S2 data was retrieved with the server's default sort order (`pvalue_up`, mimic ascending), which biases retrieval toward drugs that mimic the disease signature. Strong rescue candidates that are weak mimics may not appear in the top 100. The query script has been corrected to use `sortby=adj_pvalue_down` for future re-queries, but the L2S2 server was unavailable (504) during this analysis, so the current results are based on the existing mimic-sorted data.

| firewall_status | n (unique drugs) | interpretation |
|---|---|---|
| ACCEPT | 0 | no drug has a clean, consistent reverse-only L2S2 signal |
| WEAK | 2 | FDR-significant L2S2 reverse signal in one context, but MIXED directionality (also mimic in other contexts) |
| REJECT | 674 | failed regulatory, pediatric safety, anti-target, cytotoxic, directionality, or significance filters |

| drug | n_engines | n_total_signatures | L2S2 reverse (FDR / total) | L2S2 mimic (FDR / total) | min L2S2 reverse p (raw / adj) | L1000CDS2 (unique / total, mean score) | firewall_status | l2s2_direction | notes |
|---|---|---|---|---|---|---|---|---|---|
| **sirolimus (rapamycin)** | 2 | 4 | 1 / 5 | 4 / 5 | 6.69e-07 / 9.14e-05 | 3 / 5, 0.045 | **WEAK** | MIXED | Reverse signal only in GSE22206 pooled 100-gene (86 FDR + 14 nominal down-genes); mimic at 150/250 genes and in LCL/fibroblast sub-strata |
| **dasatinib (Sprycel)** | 2 | 2 | 1 / 4 | 2 / 4 | 9.69e-08 / 1.51e-05 | 1 / 3, 0.150 | **WEAK** | MIXED | Reverse only in GSE22206 pooled 100-gene; broad kinase/senolytic; oncology-supervised adjunct |

**Key findings & interpretation:**
1. **No drug achieves ACCEPT status.** Both surviving candidates have MIXED L2S2 directionality: each has one FDR-significant reverse signature in the pooled GSE22206 100-gene contrast, but multiple FDR-significant mimic signatures in other contexts. The MIXED penalty is data-driven, not a manual tier-string filter.
2. **The sirolimus reverse signal is not robust to gene-list size.** In the same GSE22206 pooled case-vs-control contrast, sirolimus is reverse at 100 genes (`adj_pvalue_down = 9.14e-05`) but mimic at 150 genes (`adj_pvalue_up ≈ 1.08e-13`) and 250 genes (`adj_pvalue_up ≈ 5.76e-08`). The 100-gene down-list contains 14 nominal genes (86 FDR + 14 nominal); at larger sizes the down-list is increasingly nominal-dominated. This direction flip means the rescue signal is not stable to analysis choice.
3. **The GSE22206 pooled signature has structural limitations.** It combines 4 cases (2 LCL, 2 fibroblast) and 6 controls (4 LCL, 2 fibroblast) from a single affected donor with repeated samples. Tissue is included as a covariate, but the unbalanced design and single-donor structure mean the signature is not a replicated disease signature.
4. **Dasatinib has a stronger single-signature reverse p-value but is an adjunct hypothesis.** Its best FDR-corrected reverse p-value (`adj_pvalue_down = 1.51e-05`) is lower than sirolimus's, but it is a broad tyrosine-kinase inhibitor and the senolytic hypothesis is a Tier 2 adjunct. It is retained only as an oncology-supervised conditional candidate.
5. **Everolimus does not show a reverse L2S2 signal.** It has a general FDR-significant enrichment (`adj_pvalue = 7.46e-04`) and a mimic signature in GSE22206, but no FDR-significant reverse (`adj_pvalue_down > 0.05`) and no L1000CDS2 support. It is therefore not promoted by the firewall.
6. **Rejection of in-silico artifacts:** Perhexiline maleate appeared in L1000CDS2 signatures but had zero L2S2 rescue signal. Although flagged in ChEMBL under mTOR, perhexiline is an anti-anginal CPT1 inhibitor with severe concentration-dependent hepatotoxicity, narrow therapeutic index, and an explicit Medsafe warning: *"Not recommended for use in children."* The pediatric safety firewall appropriately rejected perhexiline.
7. **Mechanism-based caveat on the sirolimus signal.** Rapamycin is itself aneugenic — it induces chromosome malsegregation and CREST-positive micronuclei in human and rodent cells (Bonatti et al. 1998, *Chromosoma* 107:498–506, doi:10.1007/s004120050335), and an unpublished rapamycin-diet note in *BubR1^H/H* mice was not positive (Baker 2013, *Cell Rep*). The WEAK/MIXED sirolimus signal is therefore best read as a context-specific transcriptomic observation with a potential anti-target profile in MVA1 — not a rescue lead. Any further consideration requires micronucleus/missegregation assays in patient cells.
7. **Biological scope of transcriptomic screens:** L2S2/L1000CDS2 evaluate steady-state mRNA perturbation in transformed cell lines. They cannot detect translational readthrough of nonsense codons (Ataluren) or post-translational protein stabilization (SIRT2 deacetylation of BUBR1 K668). The absence of a LINCS signature for Ataluren, NMN/NR, arimoclomol, or Ravicti reflects the platform's biological boundaries, not evidence against their disease-modifying mechanism.
---

## 1. Why this stack, and why not a single drug

Biallelic *BUB1B* loss produces a **hypomorphic SAC**. In human MVA1, homozygous null mutations are embryonic lethal; surviving patients therefore always carry at least one allele that retains **some residual BUBR1 protein** (~5–15%). Our proband’s two alleles have **different druggability**:

- **Allele 1 (p.Leu737Ter)** is a `TGA` (UGA) premature stop codon. UGA stops are the most suppressible class of nonsense codon; translational readthrough can insert a near-cognate amino acid (commonly Trp, Arg, or Cys) and allow translation of the entire wild-type C-terminal pseudokinase domain.
- **Allele 2 (p.Asn1002Lys)** is a C-lobe pseudokinase missense. AlphaMissense 0.9229 predicts it to be pathogenic, and it sits 10 residues from the classic MVA1 missense **L1012P** (*Suijkerbuijk 2010*), which was shown to impair BUBR1 structural stability and proteasomal degradation rather than intrinsic catalytic function. AlphaMissense predicts pathogenicity, not a specific biophysical stability change; proximity to L1012P is a hypothesis-generating clue, not proof of equivalent mechanism. Direct CRISPR knock-in, stability, localisation and SAC-complementation assays are required.

Because the disease is a lack of functional BUBR1, the **only disease-modifying** strategies are (a) restore full-length protein from the stop codon and (b) stabilise the residual hypomorphic protein. Everything else is downstream damage control.

---

## 2. Tier 1a — Direct rescue: UGA translational readthrough

### Lead: Ataluren (PTC124 / Translarna)
Ataluren is an orally bioavailable small molecule that binds to the ribosome and promotes insertion of near-cognate tRNAs at premature stop codons. Importantly, it has a **preference for UGA stop codons**, inserting Trp, Arg, or Cys, while showing little or no activity at normal termination codons (*Keeling 2014; PMC5098639*).

For `p.Leu737Ter` (`TGA` → UGA in mRNA), ataluren could theoretically allow ribosomes to read through codon 737 and complete the full 1050-amino-acid BUBR1 protein. However, readthrough inserts a near-cognate amino acid (commonly Trp, Arg, or Cys), not the original leucine, so the product would contain an amino-acid substitution at position 737 and may not fold, localise, or function correctly. Nonsense-mediated decay may also reduce the mutant transcript available for readthrough. These gates must be tested in patient cells before any therapeutic claim.

**Regulatory status:** Ataluren is **not FDA-approved** and the **EMA conditional marketing authorisation was not renewed in March 2025**. The only primary-source conditional marketing authorisation we verified is the **United Kingdom/MHRA** for nonsense-mutation DMD in ambulatory patients aged two years and older. A broader list of non-US jurisdictions has been published by the company and its Alliance partners, but those markets are not individually verified from primary regulatory evidence in this repository.

### Future tier: ELX-02
ELX-02 is a eukaryotic ribosome-selective glycoside (ERSG) engineered for improved UGA readthrough with reduced aminoglycoside-type ototoxicity and nephrotoxicity. In G542X CFTR patient-derived organoids, ELX-02 restored full-length CFTR protein and increased CFTR mRNA approximately 5-fold (*JCF 2021; NCT04135495*). It is **investigational** and has **no regulatory approval**.

Because Track 2 is limited to existing, market-approved medications, **ELX-02 is not in the main proposed stack**. It is retained as a **future-research readthrough candidate** once it achieves regulatory approval and BUB1B/MVA proof-of-concept.

**Evidence level:** Ataluren has strong mechanism-of-action data; ELX-02 has organoid proof-of-concept. **Neither has been tested in MVA1/BUB1B patient cells**, so restoration must first be confirmed by Western blot for full-length BUBR1 in the proband’s fibroblasts/iPSCs.

**Paediatric status:** Ataluren has paediatric dosing experience in DMD in approved jurisdictions; ELX-02 reached Phase 2 in adults/adolescents with CF.

**Safety:** Readthrough drugs do not rescue all nonsense alleles equally; efficiency depends on the surrounding mRNA sequence. There is a theoretical risk of producing a C-terminally elongated protein or off-target readthrough of other transcripts.

---

## 3. Tier 1b — Upstream protein stabilisation: SIRT2 / NAD+ axis

### NMN (and NR as alternative) — supplements / mechanistic comparators

North et al. (2014) showed that **SIRT2 deacetylates BUBR1 at K668**, blocking its ubiquitylation and proteasomal degradation. In *BubR1^H/H* mice and MEFs, **NMN raised BUBR1 protein levels**. However, the reported **+58% median lifespan extension** (males +123%) was from **SIRT2 transgenic overexpression**, not NMN.

**Regulatory status:** **NMN and NR are not approved medications**. They are marketed as dietary supplements / food-use ingredients (NMN is an FDA new-dietary-ingredient article; NR has an FDA GRAS no-questions letter for food use). They are retained as **mechanistic comparators** that validate the SIRT2/BUBR1 K668 axis, but they do **not** qualify as leading Track 2 nominations.

---

## 4. Tier 2a — Proteostasis: sodium-free chemical chaperone

### Glycerol phenylbutyrate (Ravicti)
4-Phenylbutyrate (4-PBA) is a low-molecular-weight chemical chaperone that reduces ER stress and protein-aggregate formation. Human trisomy 21 and trisomy 13 iPSC-derived neurons treated with **sodium 4-PBA** showed **decreased protein aggregates and prevention of apoptosis** (*Fisher et al. 2020, Sci Rep*). 4-PBA crosses the BBB via monocarboxylate transporters (MCTs) with a CSF:plasma ratio of ~0.20–0.30.

**Caveat — the evidence is extrapolated.** Fisher et al. 2020 treated trisomy iPSC-derived neurons with sodium 4-PBA; the study did not test *BUB1B* mutations, MVA, or the glycerol phenylbutyrate (Ravicti) formulation. Its inclusion here is as a sodium-free, approved prodrug of 4-PBA with paediatric UCD dosing, not as a demonstrated MVA/BUBR1 therapy.

The problem with **sodium 4-phenylbutyrate (Buphenyl)** is the massive sodium load: 1 g of sodium phenylbutyrate delivers ~124 mg of elemental sodium, and chaperone doses (9–13 g/m²/day) can cause hypertension, fluid retention, hypokalemia, and poor palatability.

**Ravicti (glycerol phenylbutyrate)** is a sodium-free, triglyceride-conjugated oral liquid prodrug of 4-PBA, FDA/EMA-approved for urea-cycle disorders (including infants and young children). It delivers phenylbutyric acid without the sodium burden and has better palatability (formal bioequivalence to sodium 4-PBA is a label claim we have not independently verified).

**Caveats:**
- No direct BUBR1/MVA rescue data.
- Anti-proliferative/HDAC-modulating effects could be double-edged in a cancer-predisposed child.
- Requires functional validation in aneuploid MVA1 cells.

### Arimoclomol
Arimoclomol (Miplyffa) was **FDA-approved in September 2024** for Niemann-Pick disease type C in adults and children ≥2 years. It **crosses the blood-brain barrier** and amplifies HSF1/heat-shock/lysosomal CLEAR network function. It is **not EMA-approved**; the EMA refused marketing authorisation for Miplyffa in July 2026.

**Caveat — significant:** Aneuploid cancer cells are known to be **addicted to HSF1** for proteostasis (*Donnelly & Amon 2014; Whitesell & Lindquist 2005*). Amplifying HSF1 could protect pre-malignant aneuploid clones from proteotoxicity-induced apoptosis. It is therefore ranked below Ravicti and must be paired with oncology monitoring.

---

## 5. Tier 2b — mTORC1-independent autophagy/lysosome induction

### Trehalose — food/GRAS comparator
Aneuploid cells activate **TFEB**, the master regulator of autophagy-lysosome biogenesis, because lysosomes become saturated with misfolded protein cargo (*Santaguida & Amon 2015, Genes Dev*). Trehalose induces **mTORC1-independent TFEB nuclear translocation** and lysosomal biogenesis, enhances clearance of protein aggregates, and has shown benefit in Batten disease and other neurodegenerative storage models (*Sidransky 2021; DeBosch 2016*).

**Regulatory status:** Trehalose is a **food ingredient / GRAS article** (FDA GRN 45, 2000), not an approved medication. It is retained as a **mechanistic comparator** for TFEB/autophagy induction, not as a leading Track 2 drug.

**Advantage over rapamycin:** Trehalose does **not** shut down mTORC1-driven growth and protein synthesis, so it is less likely to worsen microcephaly or growth failure.

**Caveats:** Oral trehalose is rapidly hydrolysed by intestinal trehalase; specialised delayed-release formulations may be needed. It has no direct BUBR1/MVA data and limited paediatric autophagy-trial experience.

### Spermidine — supplement comparator
Spermidine is a natural polyamine that promotes autophagy and TFEB activation through mTORC1-independent pathways. Spermidine-rich wheat-germ extract has EU novel-food authorisation and is marketed as a supplement. It has limited paediatric safety, bioavailability, and CNS-penetration data. It is included as a **mechanistic comparator**, not a prime candidate.

---

## 6. Tier 2c — Rapamycin / everolimus (supportive only)

González-Blanco et al. (2026) depleted **TOR** in *Drosophila* neural stem cells with aneuploidy caused by SAC impairment. **Larval rapamycin and TOR RNAi rescued neuroblast numbers, but not brain size.** Brain-size rescue came from **Sod2 and GTPx-1 overexpression**, not rapamycin. An unpublished note in *BubR1^H/H* mice on rapamycin-containing diet was not positive (*Baker 2013, Cell Rep*).

**Mechanism-based anti-target concern:** independently of any transcriptomic signal, rapamycin itself induces chromosome malsegregation and CREST-positive micronuclei in human lymphocytes/lymphoblasts and rodent cells via the p70S6K pathway (*Bonatti et al., 1998, Chromosoma* 107:498–506). In a disease defined by chromosome mis-segregation, this makes rapalogs a mechanistic worry, not just a weak signal: sirolimus is therefore treated as a context-specific transcriptomic observation with a potential anti-target profile, gated by micronucleus/missegregation assays in patient cells before any further consideration.

Everolimus is FDA/EMA-approved for TSC-SEGA in children ≥1 year (and TSC-associated seizures from age 2 years); sirolimus is FDA/EMA-approved for transplant immunosuppression and lymphangioleiomyomatosis. Rapalogs are therefore **immunosuppressive and growth-delaying**, so they are positioned as **specialist-supervised, non-monotherapy options**, not primary MVA1 therapy.

**ChEMBL note:** Rapalogs are retrieved by the target-first screen through **FKBP1A** (P62942; CHEMBL1902), not the MTOR kinase target. Sirolimus, everolimus, and temsirolimus are `FKBP1A inhibitors` in the ChEMBL mechanism file; ridaforolimus appears under `MTOR` as a direct kinase inhibitor. This distinction matters because the *in vivo* mechanism of mTORC1 inhibition by rapalogs is the FKBP1A–rapamycin–mTOR ternary complex.

---

## 7. Tier 2d — Oxidative-stress analogues (hypothesis only; high oncogenic risk)

NAC, MitoQ, and omaveloxolone are **pharmacological analogues** of the Sod2/GTPx-1 genetic rescue observed in flies. They are not proven MVA therapies and carry important cancer risks in an MVA1 patient.

- **NAC** is an FDA/EMA-approved mucolytic and paracetamol (acetaminophen) antidote with established paediatric use, but it has **poor BBB penetration**. In mouse melanoma, NAC and Trolox increased lymph-node metastases without affecting primary tumour growth (*Piskounova et al., 2015, Nature; Sayin et al., 2014, Sci Transl Med*).
- **Omaveloxolone** is an Nrf2 activator **FDA-approved in 2023 and EMA-authorised in 2024** for Friedreich ataxia in patients >=16 years. Nrf2 hyperactivation can promote chemoresistance and tumour survival (*Taguchi et al., 2011, Cancer Res; DeNicola et al., 2011, Nature*).
- **MitoQ** is a **dietary supplement / self-affirmed GRAS mitochondria-targeted antioxidant** with limited CNS data. It is not an approved medication.

These are ranked below proteostasis/autophagy candidates and should only be considered as short-term, carefully monitored adjuncts.

---

## 8. Tier 3 — Systemic inflammation: JAK1/2 and IL-6 blockade

Micronuclei from chromosome mis-segregation activate cGAS-STING and drive a type-I interferon/IL-6 response that promotes survival of aneuploid cells (*Hong et al., 2022, Nature; Bakhoum et al., 2018, Nature*). In preclinical CIN models, blocking this axis is protective.

Paediatric precedents are strong:
- **Baricitinib** in CANDLE/SAVI/AGS (*Montealegre-Sanchez et al., 2018, JCI; Vanderver et al., 2020, NEJM*).
- **Ruxolitinib** in paediatric GVHD and interferonopathies.
- **Tocilizumab** in sJIA and cytokine-release syndrome.

However, **chronic JAK/IL-6 blockade in a cancer-prone child could impair NK-cell and tumour-surveillance function** (*Aguirre-Gamboa & Dranoff reviews on immune checkpoint*). We therefore propose these only **after** demonstrating an elevated interferon signature (e.g. ISG15, MX1, OAS1) or IL-6/CRP, and with oncology surveillance.

---

## 9. ChEMBL target-first screen

`track2/drug_screen.py` queries the ChEMBL mechanism endpoint for each protein target in the causal axis. With **FKBP1A** included, the screen now retrieves:

- `FKBP1A` (CHEMBL1902): temsirolimus, sirolimus, everolimus  
- `MTOR` (CHEMBL2842): ridaforolimus  
- `JAK1` / `JAK2`: baricitinib, ruxolitinib, fedratinib  
- `IL6R` (CHEMBL2364155): tocilizumab, sarilumab  
- `NFE2L2` (CHEMBL1075094): omaveloxolone  
- `SIRT2`, `ATG7`, `SOD2`, `TMEM173`, `CGAS`, `TTK`, `AURKB`: tool compounds and anti-targets

The output is in `track2/data/chembl_axis_drugs.csv`; the `--approved-only` output is in `track2/data/chembl_axis_drugs_approved.csv`.

**Important:** Ataluren, ELX-02, Ravicti, trehalose, and spermidine are **not** discovered by the ChEMBL gene-target screen because their primary targets are the ribosome or general cellular proteostasis pathways. They are added by literature curation.

---

## 10. Safety and paediatric feasibility table

| Candidate | Regulatory status (children) | Key paediatric risk | Cancer-predisposition note |
|---|---|---|---|
| **Ataluren (PTC124)** | Conditional authorisation in the **UK/MHRA** for nmDMD; **not FDA or EMA approved**. Other non-US markets listed by the company are not individually verified. | Generally well tolerated in DMD trials | Off-target readthrough theoretically possible; efficacy allele-specific |
| **ELX-02** | **Investigational** (Phase 2 CF; no approvals) | Subcutaneous/inhaled routes; limited paediatric data | Aminoglycoside-class oto/nephro risk lower but not zero |
| **NMN / NR** | **Dietary supplements / food-GRAS**, not approved medications | Limited paediatric PK/safety data | Theoretical metabolic effects only |
| **Glycerol phenylbutyrate (Ravicti)** | Yes (UCD, including infants/children ≥2 months; FDA and EMA) | None specific; sodium-free | Anti-proliferative/HDAC effects at high doses |
| **Arimoclomol** | Yes (NPC, ≥2 yrs; **FDA only**; EMA refused) | Generally well tolerated | **HSF1/HSP could protect aneuploid cancer cells** |
| **Trehalose** | Food/GRAS; not an approved medication | Osmotic diarrhoea at high doses; trehalase hydrolysis | Does not address BUBR1 directly |
| **Spermidine** | EU novel food / supplement; not an approved medication | Limited safety/BBB data | Polyamine metabolism may alter cancer cell proliferation |
| **Rapamycin (sirolimus)** | Yes (transplant, ≥13 yrs; lymphangioleiomyomatosis) | Immunosuppression; growth delay | Long-term malignancy risk in transplant known |
| **Everolimus** | Yes (TSC-SEGA ≥1 yr; TSC seizures ≥2 yrs) | Stomatitis; growth effects | Same as rapamycin |
| **NAC** | Yes (mucolytic, paracetamol toxicity) | Poor BBB; may promote metastasis (preclinical) | Avoid chronic high-dose |
| **MitoQ** | Dietary supplement / self-affirmed GRAS; not an approved medication | Limited CNS/paediatric data | Does not address the primary BUBR1 defect |
| **Omaveloxolone** | Yes (FA, ≥16 yrs; FDA and EMA) | Hepatotoxicity; fatigue | Nrf2 oncogenic risk |
| **Dasatinib** | Yes (Ph+ CML and Ph+ ALL ≥1 yr; FDA and EMA) | Myelosuppression; infection; QT effects | Senescent-cell clearance may alter tumour microenvironment unpredictably |
| **Quercetin** | Dietary supplement / GRAS; not an approved medication | No approved paediatric indication | Supplement; use only as adjunct |
| **Baricitinib** | Approved in adults (RA, AD); paediatric expanded-access / EUA in interferonopathies only | Infection; thrombosis; cytopenias | Potential impairment of tumour surveillance |
| **Ruxolitinib** | Yes (acute/chronic GVHD ≥12 yrs; FDA and EMA) | Infection; cytopenias | Potential impairment of tumour surveillance |
| **Tocilizumab** | Yes (sJIA, CRS ≥2 yrs; FDA and EMA) | Infection; infusion reactions | Potential impairment of tumour surveillance |

---

## 11. Biomarker-gated validation plan

| Stage | Assay | Go / no-go |
|---|---|---|
| 1a. Readthrough | Western blot for full-length BUBR1 in patient fibroblasts / iPSCs after Ataluren (ELX-02 remains investigational/future) | ≥10% full-length BUBR1 restoration justifies Tier 1a |
| 1b. Protein stabilisation | BUBR1 protein in patient cells after NMN / NR / SIRT2 activator | ≥20% increase supports Tier 1b |
| 2. Proteostasis | Aggregate load (p62, ubiquitin), ER-stress markers (CHOP, BiP), apoptosis in aneuploid iPSC neurons after Ravicti or arimoclomol | ≥30% reduction supports Tier 2a |
| 3. Autophagy | LC3-II, p62, TFEB nuclear localisation after trehalose / spermidine | Additive only if lysosomal/autophagy stress is demonstrated |
| 4. Inflammation | ISG score, IL-6, CRP in serum / CSF / iPSC microglia | JAK/IL-6 blockade only if elevated |
| 5. Oncology | Baseline tumour screening; serial CBC, LFTs, imaging per MVA1 surveillance | Any unexplained cytopenia/mass → hold Tier 3 and investigate |

---

## 12. Proposed Track 2 stack (regulatory-eligible approved medications)

Track 2 is restricted to existing, market-approved medications. The following agents are the only ones that meet this criterion and are therefore in the main proposed stack:

1. **Ataluren (PTC124)** — UGA readthrough of `p.Leu737Ter`. Conditional marketing authorisation in the **UK/MHRA** for nonsense-mutation DMD; **not FDA or EMA approved**. Other listed non-US jurisdictions are not individually verified from primary regulatory sources.
2. **Glycerol phenylbutyrate (Ravicti)** — sodium-free proteostasis chaperone. **FDA/EMA approved** for urea-cycle disorders in infants and children.
3. **Arimoclomol (Miplyffa)** — HSF1/HSP and lysosomal function. **FDA approved** for Niemann-Pick C in patients ≥2 yrs; **EMA refused marketing authorisation** in 2026.
4. **Everolimus / rapamycin** — mTORC1 (supportive only, with growth/immune/oncology caveats). **FDA/EMA approved** for paediatric TSC-SEGA (everolimus) and transplant (rapamycin).
5. **NAC / omaveloxolone** — ROS/Nrf2 hypotheses with explicit cancer warnings. Both are **FDA/EMA approved** medications, but their oncogenic-risk profiles in an MVA1 child restrict them to short-term, closely monitored adjuncts.
6. **Dasatinib** — approved tyrosine-kinase inhibitor for Ph+ CML/ALL (≥1 yr); **quercetin is a supplement** and the combination is retained only as an oncology-supervised senolytic adjunct.
7. **Baricitinib / ruxolitinib / tocilizumab** — biomarker-gated systemic inflammation control. All are **FDA/EMA approved**; use only after demonstrating an elevated IFN/IL-6 signature and with oncology surveillance.

## 12b. Future research and mechanistic comparators (not in main Track 2 stack)

- **ELX-02** — next-generation UGA readthrough. **Investigational** (Phase 2 CF); moved to the future-research tier.
- **NMN / NR** — SIRT2/BUBR1 K668 protein stabilisation. **Dietary supplements / food-GRAS**, not approved medications; retained as mechanistic comparators.
- **Trehalose / spermidine / MitoQ / quercetin** — **supplements / food ingredients / GRAS**, not approved medications; retained as mechanistic comparators for autophagy, ROS and senescence biology.

---

## 13. Conclusion

The revised Track 2 proposal remains **mechanistically two-pronged**: direct rescue of the stop-gain allele via UGA readthrough and stabilisation of residual BUBR1. The regulatory audit has, however, forced a clear split between **eligible approved medications** and **investigational or supplement comparators**. Ataluren is now honestly described as having a conditional marketing authorisation in the **UK/MHRA** (not FDA or EMA); other listed non-US jurisdictions are not individually verified here. ELX-02 is in a future-research tier; and NMN, NR, trehalose, spermidine, MitoQ and quercetin are classified as supplements/food-GRAS and are not leading Track 2 nominations. The LINCS transcriptomic screen produced an exploratory, context-specific mTORC1/FKBP rapalog signal for sirolimus, not an independent or cross-species-validated result. Downstream, the lead organellar strategy is **proteostasis** (Ravicti, with arimoclomol as a cautious second). mTORC1 inhibitors, antioxidants and Nrf2 activators are explicitly deprioritised and flagged for oncogenic risk in an MVA1 child. Systemic immunomodulation is restricted to a demonstrated IFN/IL-6 signature and oncology surveillance.

---

## References

1. Hanks S, et al. *Nat Genet* 2004;36:1159–61 (biallelic BUB1B in MVA; L1012P).
2. Baker DJ, et al. *Nat Genet* 2004;36:744–9 (*BubR1^H/H* hypomorph).
3. Baker DJ, et al. *Nature* 2011;479:232–6 (senescence clearance in *BubR1^H/H*).
4. Baker DJ, et al. *Cell Rep* 2013;3:1164–74 (rapamycin note negative).
5. North BJ, et al. *EMBO J* 2014;33:1438–1453. doi:10.15252/embj.201386907 (SIRT2–BUBR1 K668; NMN raises BUBR1 protein; SIRT2-Tg lifespan extension).
6. Suijkerbuijk SJE, et al. *Cancer Res* 2010;70:7981–91 (pseudokinase missense BUBR1 destabilisation).
7. Harding SM, et al. *Nature* 2017;548:466–70; Mackenzie KJ, et al. *Nature* 2017;548:461–5 (micronuclei → cGAS-STING).
8. Bakhoum SF, et al. *Nature* 2018;553:467–72 (CIN → cGAS-STING → metastasis).
9. Hong C, et al. *Nature* 2022;607:366–73 (cGAS-STING → IL-6 survival; tocilizumab).
10. Sieben CJ, et al. *JCI* 2020;130(1), doi:10.1172/JCI126863 (*BubR1^X753/L1002P*; mTORC1 hyperactivity).
11. Montealegre-Sanchez GA, et al. *JCI* 2018;128:3042–52 (baricitinib in CANDLE/SAVI/AGS).
12. Vanderver A, et al. *NEJM* 2020;383:986–9 (baricitinib in 35 AGS patients).
13. González-Blanco A, et al. *Nat Commun* 2026;17:3829. doi:10.1038/s41467-026-70521-0 (TOR/rapamycin rescue of NB counts, not brain size; Sod2/GTPx-1 rescue brain size).
14. Malumbres M, Villarroya-Beltri C. *Nat Rev Genet* 2024, doi:10.1038/s41576-024-00762-6 (MVA tumour spectrum; SAC genes only).
15. ClinVar VCV000533901.9 (c.2210T>G p.Leu737Ter, Pathogenic/Likely pathogenic, MVA1).
16. Keeling KM, et al. *Nature Commun* 2016;7:10352; PMC5098639 (ataluren ribosomal UGA readthrough mechanism).
17. Peltz SW, Welch EM, Jacobson A. *PNAS* 2008;105:2064–2069; NCT04135495 (ELX-02 CF Phase 2).
18. Brichta L, et al. *J Cyst Fibros* 2021;20:486–497 (ELX-02 in G542X CFTR organoids).
19. Fisher EMC, et al. *Sci Rep* 2020;10:15381. doi:10.1038/s41598-020-70362-x (4-PBA rescues aneuploid iPSC neurons).
20. DailyMed / FDA (Ravicti glycerol phenylbutyrate; paediatric UCD dosing).
21. McKay M, et al. / FDA. *Miplyffa* (arimoclomol) approval 2024; NPC paediatric dosing ≥2 yrs.
22. Donnelly N, et al. *Nature Genet* 2014;46:703–708 (aneuploidy → HSF1 dependence).
23. Whitesell L, Lindquist SL. *Nat Rev Cancer* 2005;5:761–772 (HSP90/HSF1 in cancer).
24. Santaguida S, Amon A. *Genes Dev* 2015;29:2010–2021 (aneuploidy → TFEB lysosomal stress).
25. Sidransky E, et al. *Commun Biol* 2021;4:1134 (trisomy → TFEB; cGAS-STING; autophagy).
26. DeBosch BJ, et al. *Sci Signal* 2016;9:ra21 (trehalose → TFEB/autophagy).
27. Piskounova E, et al. *Nature* 2015;527:186–191. doi:10.1038/nature15726 (antioxidants promote melanoma metastasis).
28. Sayin VI, et al. *Sci Transl Med* 2014;6:221ra15. doi:10.1126/scitranslmed.3007653 (NAC increases melanoma metastasis).
29. Taguchi K, et al. *Cancer Res* 2011;71:3783–3791 (Nrf2 oncogenic functions and chemoresistance).
30. DeNicola GM, et al. *Nature* 2011;475:104–107 (oncogene-induced Nrf2 promotes tumorigenesis).
31. Bonatti S, et al. *Chromosoma* 1998;107:498–506. doi:10.1007/s004120050335 (rapamycin induces chromosome malsegregation and CREST-positive micronuclei in yeast and mammalian cells).
32. Zhu Y, et al. *Aging Cell* 2015;14:644–658. doi:10.1111/acel.12344 (dasatinib + quercetin senolytic origin; Ercc1 progeroid model, not BubR1).