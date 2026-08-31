# Track 2 — Drug Repurposing Proposal for BUB1B-Hypomorphic Mosaic Variegated Aneuploidy (MVA1)

**Team / HF user:** Ryukijano
**Date:** 2026-08-31
**Code:** https://github.com/Ryukijano/mva-hackathon-2026 (private during the hackathon; CC BY 4.0 at close)
**AI assistance disclosure (required by hackathon update 28 Aug 2026):** Cursor agents (Grok 4.6, Claude) on a commercial plan; earlier Anthropic API / Claude Sonnet sessions. Commercial terms, no training on customer content. Genome-scale files were not pasted into third-party LLM APIs. Literature claims below were checked against primary sources (North et al. 2014 *EMBO J* 33:1438–1453; González-Blanco et al. 2026 *Nat Commun* 17:3829).

---

## Executive Summary

PROBAND01 carries compound-heterozygous *BUB1B* variants — `chr15:40209701:T>G` (`c.2210T>G`, `p.Leu737Ter`, ClinVar **Pathogenic/Likely pathogenic** for MVA1, VCV000533901) and `chr15:40220612:T>G` (`c.3006T>G`, `p.Asn1002Lys`, novel, AlphaMissense 0.9229 likely-pathogenic, kinase-like C-lobe) — a truncating + hypomorphic-missense architecture. Residual BUBR1 protein in this child has **not** been measured; the ~5–10% figure is the *BubR1^H/H* mouse literature (Baker et al., 2004), used here only as the closest hypomorph class. Because the disease is **hypomorphism, not gain of function**, therapy cannot silence the gene; it must (a) **stabilize remaining BUBR1 protein**, (b) **rescue proteotoxic/mitochondrial damage** from chronic mis-segregation, and (c) **suppress the secondary inflammatory cascade** (micronuclei → cGAS–STING → type-I IFN). We propose a three-tier stack, ranked by evidence **and stated at the strength the papers actually support**:

1. **Tier 1 (upstream):** **NMN / nicotinamide riboside** — NAD+ precursors that **raise BUBR1 protein in vivo** via SIRT2 deacetylation of K668 (North et al., 2014). The **+58% median lifespan (males +123%)** is from **SIRT2 transgenic overexpression** in *BubR1^H/H* mice, **not** from NMN lifespan experiments. NMN restored BUBR1 abundance in young and aged wild-type mice (testes) and in MEFs in a largely SIRT2-dependent manner; it was not the longevity arm.
2. **Tier 2 (organelle):** **Rapamycin/everolimus** (pharmacological TORC1 inhibition by analogy to fly **TOR depletion / larval rapamycin**, which rescued **neuroblast counts but not larval brain size or Pros+ progeny** — González-Blanco et al., 2026), **NAC / MitoQ** (proposed pharmacological ROS scavengers; the fly brain-size rescue was **genetic overexpression of Sod2 and GTPx-1**, not NAC), **omaveloxolone** (Nrf2 activator, FDA-approved for Friedreich ataxia), senolytics as adjunct.
3. **Tier 3 (systemic, biomarker-guided adjunct):** **Baricitinib / ruxolitinib** (JAK1/2; pediatric evidence in Aicardi–Goutières/SAVI/CANDLE), **tocilizumab** (IL-6R; CIN cells depend on cGAS–STING→IL-6/STAT3).

**Explicitly excluded (wrong direction):** TTK/MPS1 inhibitors, Aurora B inhibitors, STING agonists — all *weaken* the SAC or *amplify* the inflammatory cascade and would worsen aneuploidy in a BUB1B-hypomorphic patient.

---

## 1. Variant Mechanism Characterization (Basis for Repurposing)

### 1.1 Genotype
| Variant | HGVS (NM_001211.6) | Consequence | Population AF | In-silico | Clinical |
|---|---|---|---|---|---|
| chr15:40209701 T>G | c.2210T>G p.Leu737Ter | stop-gained (PTV) | gnomAD e/g ≈ 7.9e-5 / 3.3e-5 | — | ClinVar VCV000533901: **Pathogenic/Likely pathogenic** (2 submitters, MVA1); PGV with somatic LOH in glioblastoma (npj Genomic Medicine 2025) |
| chr15:40220612 T>G | c.3006T>G p.Asn1002Lys | missense (pseudokinase C-lobe) | absent from gnomAD | AlphaMissense **0.9229 likely_pathogenic**; popEVE −3.657 (moderate, not severe) | novel (no ClinVar entry) |

Both variants are heterozygous in the proband (VAF ≈ 0.5). Parental phasing is not available; the PTV + kinase-domain-missense architecture is the canonical biallelic MVA1 pattern (Hanks et al., 2004; Sieben et al., 2020 — "biallelic alterations typically involving a nonsense mutation in combination with a missense mutation in the kinase domain").

### 1.2 Loss-of-function mechanism
- **p.Leu737Ter** truncates BUBR1 before the kinase domain (residues 750–1045); the truncated protein is degraded or non-functional → haploinsufficiency for the PTV allele.
- **p.Asn1002Lys** sits in the C-lobe of the human BUBR1 **pseudokinase** (not a catalytically active kinase). Known MVA missenses nearby (human L1012P = mouse L1002P, ten residues away; R814H) reduce BUBR1 abundance and SAC function (Suijkerbuijk et al., 2010). N1002K is predicted likely-pathogenic by AlphaMissense and is absent from gnomAD; we do **not** claim it is L1012P.
- Net effect: inferred **BUBR1 hypomorphism**. ~5–10% residual protein is the *BubR1^H/H* mouse value (Baker et al., 2004), **not** measured here. The closest genotype-class mice are *BubR1^X753/L1002P* and *BubR1^H/L1002P* (Sieben et al., 2020, JCI) — parallel architecture, not the identical missense.

### 1.3 Downstream biological cascade (the three therapeutic axes)
1. **Mitotic checkpoint weakness** → premature anaphase onset → lagging chromosomes → **complex aneuploidy** in neural stem cells and other progenitors.
2. **Aneuploidy-induced proteotoxic stress**: stoichiometric protein imbalance saturates UPS/autophagy, stalls mitophagy, and drives mitochondrial ROS → loss of neural stemness and microcephaly in SAC-depleted fly NSCs (González-Blanco et al., 2026); senescence phenotypes in *BubR1^H/H* mice (Baker et al., 2004/2011).
3. **Micronuclei → cGAS–STING → chronic type-I IFN / IL-6**: ruptured micronuclei expose genomic dsDNA to cGAS, driving chronic interferon and IL-6/STAT3 signalling (Harding et al., 2017; Mackenzie et al., 2017; Bakhoum et al., 2018; Hong et al., 2022) — a systemic inflammatory burden consistent with the "chronic immune response" noted in MVA patients (Malumbres & Villarroya-Beltri, 2024).

---

## 2. Target Identification — Three-Tier Repurposing Stack

### Tier 1 (Upstream, disease-modifying): stabilize residual BUBR1 protein
**Target: SIRT2 / NAD+ axis.** BUBR1 stability is controlled by acetylation of **lysine 668**: CBP acetylates K668 → ubiquitylation → proteasomal degradation; SIRT2 deacetylates K668 → stabilization ([North et al., 2014, *EMBO J* 33:1438–1453](https://doi.org/10.15252/embj.201386907)). Two results must be kept separate: (i) **NMN** (500 mg/kg/day × 7 d) raised NAD+ and **restored BUBR1 protein** in testes of young and 30-month mice, largely SIRT2-dependent in MEFs; (ii) **SIRT2 transgenic overexpression** in *BubR1^H/H* mice extended **median lifespan +58% (males +123%; females no change)** and did **not** reverse dwarfism, cataracts, or lordokyphosis. NMN was **not** the lifespan arm. This is still the only approved-adjacent class that directly raises the protein encoded by the causal gene (GRAS NAD+ precursors; adult trial data; limited paediatric data).

**Why not MPS1/TTK modulation (original hypothesis — rejected):** TTK/MPS1 inhibitors (CFI-402257, BOS172722, BAY-1161909) are SAC *override* agents that shorten mitotic dwell time and deliberately generate catastrophic aneuploidy — a cancer-killing strategy. In a BUB1B-hypomorphic patient the SAC is already weak; further inhibition would worsen mis-segregation. Aurora B inhibitors are excluded for the same reason (they disable error correction).

### Tier 2 (Organelle rescue): proteostasis, mitophagy, mitochondrial ROS
- **Rapamycin / everolimus (mTORC1):** mild TORC1 inhibition is proposed because fly **Atg1 overexpression, Rheb/TOR depletion, or larval rapamycin** rescued **aneuploid neuroblast counts** in SAC-depleted brains, **without rescuing Pros+ progeny counts or larval brain size** — the authors note that non-physiological autophagy may itself impair proliferation ([González-Blanco et al., 2026, *Nat Commun* 17:3829](https://doi.org/10.1038/s41467-026-70521-0), Fig. 6 and Supplementary Fig. 6C). Independently, monoallelic MVA carriers show **mTORC1 hyperactivity** in muscle (Sieben et al., 2020). **Caveat:** a preliminary unpublished rapamycin diet in *BubR1^H/H* mice showed no rescue (Baker et al., 2013, *Cell Rep* note). Positioned as supportive, not monotherapy, and **not** as a microcephaly-size rescue.
- **NAC / MitoQ (ROS):** the published fly interventions that rescued neuroblast number / brain size were **genetic overexpression of Sod2 and GTPx-1** (and mitochondrial chaperones Hsp60/Hsp60c), **not** NAC or MitoQ. NAC and MitoQ are **pharmacological analogues we propose** on that ROS axis; they were not the 2026 fly drugs. NAC is FDA-approved and paediatric-safe; MitoQ is mitochondria-targeted, phase-2 elsewhere.
- **Omaveloxolone (Nrf2):** identified by our ChEMBL screen (NFE2L2 activator); FDA-approved for Friedreich ataxia (2023); boosts the endogenous antioxidant program (SOD2, GCLC, NQO1) that counteracts aneuploidy-driven ROS.
- **Senolytics (dasatinib+quercetin, navitoclax):** clearing p16+ senescent cells delays lordokyphosis and cataracts in *BubR1^H/H* mice but does **not** extend lifespan (Baker et al., 2011) → adjunct only.

### Tier 3 (Systemic adjunct): cGAS–STING / JAK–STAT suppression
- **Baricitinib / ruxolitinib (JAK1/2):** suppress type-I IFN downstream of micronuclei→cGAS–STING. Strong pediatric precedent: baricitinib in 35 AGS patients (NEJM 2020) and compassionate-use in CANDLE/SAVI (JCI 2018); ruxolitinib is FDA-approved in children (GVHD).
- **Tocilizumab (IL-6R):** CIN cells depend on cGAS–STING→IL-6/STAT3 survival signalling (Hong et al., 2022); IL-6 blockade is pediatric-approved (sJIA, CRS) and could reduce CIN-driven systemic inflammation.
- **Caveats:** the fly model indicates DNA-damage signalling is *not* the primary driver of NSC loss, so Tier 3 is adjunctive; chronic JAK/IL-6 blockade may impair immune surveillance in a cancer-prone MVA1 patient → **biomarker-gated** (IFN score, IL-6, CRP) and lowest priority.

---

## 3. Biophysical Characterization

- **p.Asn1002Lys** maps to the BUBR1 **pseudokinase** C-lobe (residues ~750–1045; AlphaFold AF-O60566-F1). Asn1002 is conserved across vertebrates; N1002K introduces a long basic side chain, predicted to perturb local packing (AlphaMissense 0.9229; popEVE −3.657, not popEVE-severe). Neighbouring pathogenic MVA alleles (L1012P, R814H) reduce abundance and SAC activity — N1002K is expected to be hypomorphic, not dominant-negative, but that is inference.
- **p.Leu737Ter** removes the kinase-like domain and C-terminal KEN/ABBA motifs; consistent with a null allele.
- **Implication for therapy:** remaining protein from the missense allele is the substrate for stabilization (Tier 1), not silencing. Residual fraction in the child is unknown. ChEMBL has no approved BUB1B ligand, so axis-based repurposing is the practical route.

---

## 4. Computational Drug Screening

### 4.1 Methods (reproducible)
1. **Variant annotation:** Ensembl VEP **116** with gnomAD (e/g), AlphaMissense, popEVE plugins on the proband WGS VCF; panel of 15 MVA genes; only *BUB1B* carried ≥2 rare functional variants.
2. **Target-first drug screen:** ChEMBL REST API (`target.json` by UniProt accession → `mechanism.json` → molecule names) for 14 axis genes (BUB1B, SIRT2, MTOR, ATG7, ATG5, SOD2, NFE2L2, TMEM173, CGAS, JAK1, JAK2, IL6R, TTK, AURKB). Output: `track2/data/chembl_axis_drugs.csv` (85 drug–target rows; script `track2/drug_screen.py`).
3. **Literature evidence grading:** each candidate scored on (a) direct evidence in BUBR1-hypomorphic models, (b) pediatric approval status, (c) direction-of-effect safety for a hypomorphic SAC.
4. **Anti-target filtering:** drugs whose mechanism *weakens* the SAC or *amplifies* IFN signalling were explicitly excluded (TTK/MPS1 inhibitors, Aurora B inhibitors, STING agonists).

### 4.2 Screen hits feeding the proposal
| Gene (ChEMBL target) | Screen hits | Role in proposal |
|---|---|---|
| BUB1B (CHEMBL4295998) | none | confirms BUBR1 is not directly druggable → axis strategy |
| SIRT2 (CHEMBL4462) | none approved | NMN/NR act via NAD+ substrate, not a SIRT2 drug |
| MTOR (CHEMBL2842) | sirolimus, everolimus, temsirolimus, ridaforolimus + 30+ | Tier 2 rapamycin/everolimus |
| NFE2L2 (CHEMBL1075094) | **omaveloxolone** (activator) | Tier 2 novel candidate |
| JAK1/JAK2 (CHEMBL2835/2971) | **baricitinib, ruxolitinib**, upadacitinib, filgotinib | Tier 3 |
| IL6R (CHEMBL2364155) | **tocilizumab**, sarilumab | Tier 3 |
| TMEM173 (CHEMBL4523377) | ADU-S100 (agonist) | **excluded** (wrong direction) |
| TTK (CHEMBL3983) / AURKB (CHEMBL2185) | BAY-1161909, BAY-1217389 / barasertib, GSK-1070916 | **excluded** (wrong direction) |
| SOD2, CGAS, ATG7, ATG5 | none | no approved modulators; NAC/MitoQ act biochemically |

### 4.3 Final ranked candidate list
See `track2/data/track2_candidates.csv` (11 ranked candidates + 3 explicit anti-targets).

---

## 5. Safety / Pediatric Feasibility Profile

| Drug | Pediatric status | Key risks | Monitoring |
|---|---|---|---|
| NMN / NR | GRAS supplement; adult trials | theoretical NAD+ metabolism effects | clinical exam, growth |
| Rapamycin / everolimus | approved in children (transplant, TSC-SEGA) | immunosuppression, growth delay, stomatitis, metabolic | trough levels, CBC, lipids, glucose, growth |
| NAC | approved, pediatric-safe | very low | none routine |
| MitoQ | supplement; phase 2 adult | low | none routine |
| Omaveloxolone | approved (FA, adults/adolescents) | transaminitis, fatigue | LFTs |
| Dasatinib+quercetin | dasatinib approved (CML, incl. pediatric) | myelosuppression, infection, QT | CBC, ECG |
| Baricitinib / ruxolitinib | pediatric expanded-access / GVHD approval | infection, lymphopenia, thrombosis; **theoretical tumor-surveillance impairment** | IFN score, CBC, infection surveillance |
| Tocilizumab | approved (sJIA, CRS, pediatric) | infection, infusion reactions | CBC, LFTs, infection surveillance |

**Proposed clinical logic:** Tier 1 (NMN) + Tier 2 (NAC/MitoQ) first — lowest risk, direct mechanistic support; add rapamycin/everolimus under specialist supervision if growth/sarcopenia dominate; Tier 3 only if an IFN/IL-6 biomarker signature is demonstrated, with oncology surveillance (MVA1 carries childhood tumor risk — rhabdomyosarcoma, Wilms).

---

## 6. Future Experimental Validation Plan

1. **Patient-derived cells (LCLs/fibroblasts):** measure BUBR1 protein by immunoblot (do not assume the mouse ~10% value); SAC strength (mitotic timing after nocodazole), micronucleus frequency, ROS (MitoSOX), and IFN signature (qPCR ISGs).
2. **NMN/SIRT2 axis:** treat cells with NMN/NR; quantify BUBR1 protein rescue (K668 acetylation status), SAC recovery, and aneuploidy rate (FISH/cytogenetics).
3. **Fly model (González-Blanco 2026 protocol):** replicate NAC/MitoQ, TOR-depletion, and apoptosis-inhibition rescues; add NMN to test BUBR1-stabilization in vivo.
4. **Mouse model (*BubR1^H/L1002P*, Sieben et al. 2020 — nearest published genotype class, not N1002K):** NMN ± rapamycin ± NAC; endpoints: BUBR1 protein, SAC strength, lifespan, sarcopenia, cataracts, cardiac stress, tumour latency.
5. **Biomarker panel for Tier 3 gating:** serum IFN score, IL-6, CRP, micronucleus assay in PBMCs.

---

## 7. Scalability — Redeploying the N=1 Framework

The end-to-end pipeline is generic and reusable for any N=1 rare disease:
1. **Genotype:** WGS → VEP (gnomAD, AlphaMissense, popEVE) → panel/whole-genome rare-functional-variant screen (only genes with ≥2 rare functional alleles survive).
2. **Mechanism:** map variant to protein domain (AlphaFold/PDB) and pathway; classify LOF/hypomorph vs GOF → determines silencing vs stabilization strategy.
3. **Repurposing:** ChEMBL target-first screen on the causal-gene axis + literature evidence grading + explicit anti-target filtering (direction-of-effect safety).
4. **Tiering:** upstream (protein rescue) → organelle (damage rescue) → systemic (inflammation), each gated by pediatric approval status and biomarkers.
All code is in https://github.com/Ryukijano/mva-hackathon-2026 (`track2/drug_screen.py`, `scripts/run_track1.py`) and is rerunnable after the gated VCF is obtained. The repo may stay private until hackathon close, then CC BY 4.0.

---

## References

1. Hanks S, et al. *Nat Genet* 2004;36:1159–61 (biallelic BUB1B in MVA; 2211insGTTA + L1012P).
2. Baker DJ, et al. *Nat Genet* 2004;36:744–9 (*BubR1^H/H* hypomorph).
3. Baker DJ, et al. *Nature* 2011;479:232–6 (senescence clearance in *BubR1^H/H*).
4. Baker DJ, et al. *Cell Rep* 2013;3:1164–74 (p21; rapamycin preliminary negative note).
5. North BJ, et al. *EMBO J* 2014;33:1438–1453. doi:10.15252/embj.201386907 (SIRT2 deacetylates BUBR1 K668; NMN raises protein; **SIRT2-Tg** +58% median lifespan).
6. Suijkerbuijk SJE, et al. *Cancer Res* 2010;70:7981–91 (kinase-domain missense alleles).
7. Harding SM, et al. *Nature* 2017;548:466–70; Mackenzie KJ, et al. *Nature* 2017;548:461–5 (micronuclei→cGAS).
8. Bakhoum SF, et al. *Nature* 2018;553:467–72 (CIN→cGAS-STING→metastasis).
9. Hong C, et al. *Nature* 2022;607:366–73 (cGAS-STING→IL-6 survival; tocilizumab).
10. Sieben CJ, et al. *JCI* 2020;130(1), doi:10.1172/JCI126863 (*BubR1^X753/L1002P*, *BubR1^H/L1002P*; mTORC1 hyperactivity).
11. Montealegre Sanchez GA, et al. *JCI* 2018;128:3042–52 (baricitinib in CANDLE/SAVI/AGS).
12. Vanderver A, et al. *NEJM* 2020;383:986–9 (baricitinib in 35 AGS patients).
13. González-Blanco A, et al. *Nat Commun* 2026;17:3829. doi:10.1038/s41467-026-70521-0 (SAC loss in fly NSCs; Sod2/GTPx-1 and Hsp60 overexpression rescue brain size; TOR/rapamycin rescue NB counts **not** brain size).
14. Malumbres M, Villarroya-Beltri C. *Nat Rev Genet* 2024, doi:10.1038/s41576-024-00762-6 (MVA tumor spectrum; SAC genes only).
15. *npj Genomic Medicine* 2025, doi:10.1038/s41525-025-00526-z (BUB1B c.2210T>G PGV with somatic LOH in glioblastoma).
16. ClinVar VCV000533901.9 (c.2210T>G p.Leu737Ter, Pathogenic/Likely pathogenic, MVA1).
