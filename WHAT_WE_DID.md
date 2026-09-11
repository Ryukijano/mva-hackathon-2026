# What we did — Rare Disease, Real Kid: MVA Hackathon 2026

**Team / HF user:** [Ryukijano](https://huggingface.co/Ryukijano)  
**Dates:** 27 Aug – 3 Sep 2026  
**Cluster:** University of Leeds AIRE  
**GitHub (submit-form URL, private until close):** https://github.com/Ryukijano/mva-hackathon-2026  
**Hub mirror:** https://huggingface.co/Ryukijano/mva-hackathon-2026  

This is the campaign wrap-up for the whole repo. Numbers and job IDs for the protein-LM / graph work live in `experiments/2026-08-31_bub1b_computational/outputs/RESULTS.md`. LINCS tables live in `track2/lincs/results/`.

---

## 1. The challenge, in one paragraph

SageBio’s [Rare Disease, Real Kid: MVA Hackathon 2026](https://huggingface.co/spaces/SageBio/rare-disease-real-kid-mva-hackathon-2026) is an N-of-1 case for a child with mosaic variegated aneuploidy. **Track 1** is a ranked CSV of the causal genotype (six shots; best CSV counts; rank points + F-max). **Track 2** is a written drug-repurposing dossier plus GitHub URL plus a 3-minute video (three shots; panel reviews the latest). Close is **24 Oct 2026, 23:59 UTC**. Submissions are CC BY 4.0. The gated genome never left AIRE scratch and was never pasted into third-party LLM APIs.

MVA is a mitotic **rate** problem, not a “gene for microcephaly.” Unattached kinetochores keep APC/C off via the mitotic checkpoint complex (MCC). BUBR1 (`BUB1B`) is an MCC subunit. If the latch opens early, random chromosomes are gained or lost; multi-subunit machines are poisoned by unpaired subunits; leftover proteotoxic and mitochondrial load collapses neural stem cells. Childhood tumours track **core SAC** genes, not centrosome scaffolds, in the human series.

---

## 2. Track 1 — the call we still stand on

After Ensembl VEP **116** (GRCh38), a 15-gene mitotic panel, gnomAD AF ≤ 0.001, and SpliceAI on a tiny candidate VCF (`-D 500`), **only *BUB1B* had two rare functional alleles**. That uniqueness is why the CSV is one row.

| Allele | GRCh38 | NM_001211.6 | Role |
|---|---|---|---|
| 1 | `chr15:40209701 T>G` | `c.2210T>G` `p.Leu737Ter` | ClinVar Pathogenic/LP for MVA1 ([VCV000533901](https://www.ncbi.nlm.nih.gov/clinvar/variation/533901/)) |
| 2 | `chr15:40220612 T>G` | `c.3006T>G` `p.Asn1002Lys` | C-lobe **pseudokinase** missense; AlphaMissense **0.9229**; ESM-1v mild (3rd-mildest of 19); protein change in ClinVar as VUS (VCV004600147.1, via `c.3006T>A`, last evaluated 19 Sep 2025); our `T>G` allele absent from ClinVar and gnomAD genomes (1 allele in gnomAD v4 exomes, AF 6.8e-07) |

Submitted EPCR **0.95**, `finding_type=primary`. Architecture is truncating + hypomorphic missense ([Hanks et al., 2004](https://doi.org/10.1038/ng1449)). Human BUBR1’s C-terminus is a **pseudokinase**, not a working kinase. Phasing is inferred (both heterozygous in the VCF), not parental. Residual ~11% ± 3% BUBR1 is the *BubR1^H/H* mouse literature (Baker 2004), **not** measured in this child.

**Pipeline bugs that had to be fixed before the CSV was recoverable**

- AF filter read a non-existent `gnomad_af` key and kept common KNL1/CEP192 haplotypes (AF 30–80%).
- SpliceAI `-D 10000` exceeds the CLI max of 4999 (job `7537559`). Working distance is 500.
- A cancer-gene EPCR bonus could push EPCR past 1.0; it is dead code and is **not** applied.
- The 0.9229 on N1002K is **AlphaMissense**, not popEVE. popEVE is missing for this codon change.

Files: `submissions/Ryukijano_bub1b-compoundhet.csv`, `submissions/Ryukijano_track1_report.md`. Track 1 has **not** been uploaded to the Space (six-shot quota).

---

## 3. Track 2 — mechanism first, then a regulatory audit, then transcriptomics

Because the disease is **hypomorphism, not gain of function**, we cannot silence *BUB1B*. The scientific stack is dual-pronged:

1. Restore full-length protein from the UGA stop (`p.Leu737Ter`) if a licensed readthrough drug exists.
2. Stabilise residual BUBR1 (SIRT2 / K668 / NAD+), then blunt proteotoxic, lysosomal, mitochondrial, and IFN/IL-6 load.

**What the papers actually show (do not blur this in a pitch)**

- [North et al., 2014, *EMBO J*](https://doi.org/10.15252/embj.201386907): NMN **raises BUBR1 protein**. The **+58% / +123% lifespan** result is **SIRT2 transgenic overexpression** in *BubR1^H/H* mice, not NMN.
- [González-Blanco et al., 2026, *Nat Commun*](https://doi.org/10.1038/s41467-026-70521-0): larval rapamycin rescued **neuroblast counts, not brain size**. Brain-size rescue was **Sod2 / GTPx-1 overexpression**, not NAC as a drug.

**Regulatory eligibility (hackathon: currently approved medications)**

Ataluren is not FDA/EMA-approved (EMA non-renewal March 2025). ELX-02 is investigational. NMN/NR, trehalose, spermidine, MitoQ, quercetin are supplements/food, not leading nominations. Arimoclomol is FDA-approved for NPC (EMA refused July 2026). ChEMBL must query **FKBP1A (P62942)** to retrieve rapalogs; a direct MTOR kinase query does not return sirolimus.

**Excluded (wrong direction):** TTK/MPS1 inhibitors, Aurora B inhibitors, STING agonists.

**Regulatory audit refresh (10 Sep 2026):** ataluren has no live FDA application — PTC withdrew its 2024 NDA resubmission in early 2026; its UK/MHRA authorisation is under active review post-EU-non-renewal, not settled long-term; arimoclomol's EU product is branded Meplyffa (not Miplyffa) and this July 2026 refusal was Zevra's *second* EU attempt (first withdrawn 2022), re-examination pending. Ravicti, ELX-02, and the "no newer readthrough drug approved since 2025" claim were re-checked and hold. Detail: `track2/track2_report.md` §Regulatory audit refresh.

Files: `track2/track2_report.md`, `track2/data/track2_candidates.csv`, `track2/pitch_storyboard.md`. Track 2 is still **blocked on the 3-minute YouTube/Vimeo pitch**.

---

## 4. Pre-registered computation (this is not TxGNN)

Protocol: `experiments/2026-08-31_bub1b_computational/protocol.md`.  
Narrative: `experiments/2026-08-31_bub1b_computational/SUMMARY.md`.

Two hypotheses were written **before** looking at the new scores. Both failed as written.

### H1 — is N1002K an L1012P-class missense? **No.**

ESM-1v ensemble (five `facebook/esm1v_t33_650M_UR90S_{1–5}` models), masked LLR on UniProt **O60566**. No patient sequence on GPUs. First GPU job died because ESM-1v only accepts **1022 amino acids**; BUBR1 is 1050. Windowed scoring: residues 29–1050 (job `7619146`).

| Allele | Ensemble LLR (nats) |
|---|---|
| **N1002K** (this child) | **−0.110** |
| L1012P (literature MVA) | **−1.801** |
| R814H (literature MVA) | **−1.444** |
| K668Q (acetylation mimic, not MVA) | −0.309 |

Pre-registered: N1002K within **0.5 nats** of L1012P. Observed gap **1.69 nats** → **falsified**.

ClinVar B/LB control (A5; 34 unique NM_001211.6 missenses, job `7648413`): B/LB median **−0.161**. N1002K is rank **18/34** (weaker than that median) → second falsifier **also met**. L1012P sits below the entire B/LB cloud.

AlphaMissense **0.9229** remains the stronger allele-level pathogenic *in silico*. ESM-1v does not agree. Do **not** say N1002K “is” L1012P (ten residues away). Nearby literature missenses mainly **destabilise protein**, not catalysis.

### H2 — does PrimeKG put sirolimus next to MVA? **No.**

Skip-gram embeddings (dim 64, 50 epochs, seeds 0/1/2) on a 1-hop PrimeKG neighbourhood.

| Setting | Drugs | Sirolimus mean rank | What ranked top |
|---|---|---|---|
| E2 (pre-registered) | 37 | **22.0** | JAK inhibitors. TTK inhibitor BOS172722 **20.7** (above sirolimus). |
| E2b (anti-target seeds dropped) | 31 | **16.7** | Sarilumab / ruxolitinib / tocilizumab. Same qualitative result. |

H2 **falsified**. Honest use of the graph: a **JAK/IL-6 neighbourhood prior**, not evidence that the graph “found” rapamycin. Open Targets 26.06 recovered JAK inhibitors and tocilizumab; **sirolimus is not on the MTOR drug list** (FKBP1A annotation). ChEMBL stays the rapalog source.

---

## 5. LINCS L2S2 + L1000CDS2 firewall (Track 2, later)

Independent transcriptomic-reversal screen: reverse-query GEO BUB1B/MVA signatures through L2S2 (primary) and L1000CDS2 (secondary), then reject hits that are unapproved, cytotoxic, broad cancer-kinase, anti-target, or single-signature. The firewall gates on **directional reverse FDR** (`adj_pvalue_down < 0.05`), penalizes **MIXED** directionality (both reverse and mimic → WEAK), thresholds L1000CDS2 on positive scores, and flags signatures containing nominal (non-FDR) genes.

Signatures: GSE22206 (human MVA fibroblasts/LCLs), GSE134781 (early mouse *BubR1* hypomorph), GSE134780 (late mouse hypomorph, muscle/fat). GSE247267 (isogenic RPE1 aneuploidy) produced **no DEGs** under the same pipeline and was not queried.

Firewall on unique drugs: **ACCEPT 0 / WEAK 2 / REJECT 674**.

| Drug | Engines | Total signatures | Status | Direction | How to use it |
|---|---|---|---|---|---|
| **Sirolimus** | 2 | 4 | **WEAK** | MIXED | 1 FDR reverse in GSE22206 100-gene (`adj_pvalue_down = 9.14e-05`); 4 FDR mimic signatures. Reverse signal not robust to gene-list size (mimic at 150/250). Down-list contains 14 nominal genes. |
| **Dasatinib** | 2 | 2 | **WEAK** | MIXED | 1 FDR reverse in GSE22206 100-gene (`adj_pvalue_down = 1.51e-05`); 2 mimic signatures. Broad kinase/senolytic; oncology-supervised adjunct. |

Everolimus was rejected (general FDR only, no reverse signal). Perhexiline maleate was an L1000CDS2-only false-positive and was **rejected** by the pediatric-safety firewall.

**Post-hoc mechanism check (sirolimus):** independent of the transcriptomic signal, rapamycin is itself aneugenic — it induces chromosome malsegregation and CREST-positive micronuclei in human lymphocytes/lymphoblasts and rodent cells via p70S6K (Bonatti et al. 1998, *Chromosoma* 107:498–506, doi:10.1007/s004120050335), and an unpublished rapamycin-diet note in *BubR1^H/H* mice was not positive (Baker 2013, *Cell Rep*). The WEAK sirolimus signal is a context-specific transcriptomic observation with a mechanism-based anti-target concern in MVA1 — not a rescue lead; any further consideration requires micronucleus/missegregation assays in patient cells.

**Known retrieval limitation:** The current L2S2 data was retrieved with the server's default mimic-sorted sort order. The query script has been corrected to use `sortby=adj_pvalue_down` for future re-queries, but the server was unavailable (504) during this analysis.

**Absence of a LINCS hit is not evidence against** Ataluren, Ravicti, arimoclomol, NMN, JAK inhibitors, or Nrf2 drugs. No LINCS result establishes BUBR1 rescue, SAC correction, or patient benefit.

Method: `track2/lincs/README.md`. Tables: `track2/lincs/results/lincs_firewall_decisions.csv`, `track2/lincs/results/lincs_candidate_ranking.csv`, `track2/lincs/results/signature_composition.csv`.

---

## 6. What we built (engineering)

| Piece | Where |
|---|---|
| Track 1 CLI (VEP → filter → SpliceAI → score → pair → CSV) | `scripts/run_track1.py`, `src/mva_hackathon/variants/` |
| Local clone of the official scorer | `src/mva_hackathon/eval/scorer.py`, `tests/test_scorer.py` |
| ChEMBL axis screen (must include FKBP1A) | `track2/drug_screen.py` |
| ESM-1v / PrimeKG / Open Targets / ClinVar B/LB | `src/mva_hackathon/research/`, `scripts/slurm/run_research.sh` |
| LINCS GEO → DE → L2S2/L1000CDS2 → firewall | `track2/lincs/` |
| AIRE env | `/mnt/scratch/kcwp264/.conda_envs/mva-hackathon` (VEP 116); `cjepa` for ESM; `mva-hackathon-lincs` for GEO/LINCS |

**Never on GitHub / Hub:** `data/` genome, `refs/` VEP cache and PrimeKG `kg.csv`, `.cache/`, phenotype `.docx`, `MVA Track 1 Debugging (1).md`.

---

## 7. How to read this against a submission

| Claim | After this campaign |
|---|---|
| Compound-het *BUB1B* is the Track 1 genotype | **Unchanged.** Panel uniqueness + ClinVar PTV + architecture. |
| N1002K is AlphaMissense likely-pathogenic | **Unchanged**, and now **opposed** by ESM-1v / ClinVar B/LB LLRs. Report both. |
| N1002K is “like L1012P” | **Do not say this.** |
| Rapalogs / NAD+ / proteostasis / JAK as the stack | Mechanism-first ranking **stands**. PrimeKG does **not** recover rapalogs; LINCS yields only a **context-specific WEAK/MIXED** sirolimus signal after the false-rescue firewall — and rapamycin is itself aneugenic (see §5), so this is not a rescue lead. |
| Graph/AI discovered the therapy | **Do not say this.** |
| NMN is the +58% lifespan result; NAC rescued fly brain size | **Do not say this.** |
| TxGNN/PrimeKG GNN was trained | **Never built.** README no longer claims it. |

---

## 8. Still open

1. **Track 2 3-minute pitch** (YouTube/Vimeo) — required for the Track 2 form. Storyboard: `track2/pitch_storyboard.md`.
2. **Track 1 Space upload** — CSV + methods + GitHub URL; only if we spend 1 of 6 shots.
3. Optional science we did not run: parental phasing, FASTQ mosaic/VAF sweep, deep-intronic SpliceAI, patient-cell BUBR1 immunoblot, ClinVar *benign-only* (exclude single-submitter LB).

That is the campaign: a defensible one-row MVA1 call, an honest hypomorph drug stack with a regulatory audit, two pre-registered computational tests that **failed as written**, and an exploratory LINCS screen that generates a context-specific mTORC1/FKBP rapalog signal for sirolimus without pretending the graph or an unbiased screen independently validated a therapy.
