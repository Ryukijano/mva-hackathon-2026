# What we did — Rare Disease, Real Kid: MVA Hackathon 2026

**Team / HF user:** [Ryukijano](https://huggingface.co/Ryukijano)  
**Dates:** 27 Aug – 17 Oct 2026  
**Cluster:** University of Leeds AIRE  
**GitHub (public, CC BY 4.0):** https://github.com/Ryukijano/mva-hackathon-2026  
**Hub mirror:** https://huggingface.co/Ryukijano/mva-hackathon-2026  

This is the campaign wrap-up for the whole repo. Numbers and job IDs for the protein-LM / graph work live in `experiments/2026-08-31_bub1b_computational/outputs/RESULTS.md` and `experiments/2026-10-11_esm1v_fixed/`. Structural and AlphaFold DB v6 / PAE / AlphaMissense analyses live in `experiments/2026-10-11_alphafold_bubr1/SUMMARY.md` and `docs/structure_and_plm_addendum_2026-10-11.md`. LINCS tables live in `track2/lincs/results/`.

---

## 1. The challenge, in one paragraph

SageBio’s [Rare Disease, Real Kid: MVA Hackathon 2026](https://huggingface.co/spaces/SageBio/rare-disease-real-kid-mva-hackathon-2026) is an N-of-1 case for a child with mosaic variegated aneuploidy. **Track 1** is a ranked CSV of the causal genotype (six shots; best CSV counts; rank points + F-max). **Track 2** is a written drug-repurposing dossier plus GitHub URL plus a 3-minute video (three shots; panel reviews the latest). Close is **24 Oct 2026, 23:59 UTC**. Submissions are CC BY 4.0. The gated genome never left AIRE scratch and was never pasted into third-party LLM APIs.

MVA is a mitotic **rate** problem, not a “gene for microcephaly.” Unattached kinetochores keep APC/C off via the mitotic checkpoint complex (MCC). BUBR1 (`BUB1B`) is an MCC subunit. If the latch opens early, random chromosomes are gained or lost; multi-subunit machines are poisoned by unpaired subunits; leftover proteotoxic and mitochondrial load collapses neural stem cells. Childhood tumours track **core SAC** genes, not centrosome scaffolds, in the human series.

---

## 2. Track 1 — the call we still stand on

After Ensembl VEP **116** (GRCh38), a 17-gene mitotic panel (SLF2/SMC5 added Sept 2026), gnomAD AF ≤ 0.001, and SpliceAI on a tiny candidate VCF (`-D 500`), **only *BUB1B* had two rare functional alleles**. That uniqueness is why the CSV is one row.

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

Files: `submissions/Ryukijano_bub1b-compoundhet.csv`, `submissions/Ryukijano_track1_report.md`.

**Submitted 12 Sep 2026 — one shot spent, full match at rank 1: 100.0/100 rank points, F-max 1.000, EPCR threshold 0.95.** The scorer confirms *BUB1B* `chr15:40209701 T>G` + `chr15:40220612 T>G` as the causal compound-heterozygous genotype against the hackathon ground truth (1/6 shots spent). Molecular read-backed phasing on the short-read BAM remains WhatsHap-UNRESOLVED (10.9 kb gap vs ~1.3 kb max insert), and clinically p.Asn1002Lys (`c.3006T>G`) remains a VUS-grade novel nucleotide allele.

---

## 3. Track 2 — mechanism first, then a regulatory audit, then transcriptomics

Because the disease is **hypomorphism, not gain of function**, we cannot silence *BUB1B*. The scientific stack is dual-pronged:

1. Restore full-length protein from the UGA stop (`p.Leu737Ter`) if a licensed readthrough drug exists.
2. Stabilise residual BUBR1 (SIRT2 / K668 / NAD+), then blunt proteotoxic, lysosomal, mitochondrial, and IFN/IL-6 load.

**What the papers actually show (do not blur this in a pitch)**

- [North et al., 2014, *EMBO J*](https://doi.org/10.15252/embj.201386907): NMN **raises BUBR1 protein**. The **+58% / +123% lifespan** result is **SIRT2 transgenic overexpression** in *BubR1^H/H* mice, not NMN.
- [González-Blanco et al., 2026, *Nat Commun*](https://doi.org/10.1038/s41467-026-70521-0): larval rapamycin rescued **neuroblast counts, not brain size**. Brain-size rescue was **Sod2 / GTPx-1 overexpression**, not NAC as a drug.

**Regulatory eligibility (hackathon: currently approved medications)**

Ataluren is not FDA/EMA-approved (EMA non-renewal March 2025; FDA NDA resubmission withdrawn 12 Feb 2026; UK/MHRA conditional only). ELX-02 is investigational. NMN/NR, trehalose, spermidine, MitoQ, quercetin are supplements/food, not leading nominations. Arimoclomol is FDA-approved with miglustat for NPC (US brand Miplyffa; EMA CHMP issued a negative opinion for EU brand Meplyffa on 23 Jul 2026, re-examination requested 5 Aug 2026). ChEMBL must query **FKBP1A (P62942)** to retrieve rapalogs; a direct MTOR kinase query does not return sirolimus.

**Excluded (wrong direction):** TTK/MPS1 inhibitors, Aurora B inhibitors, STING agonists.

**Regulatory audit refresh (10 Sep – 18 Oct 2026):** ataluren has no live FDA application — PTC withdrew its 2024 NDA resubmission on 12 Feb 2026; its UK/MHRA authorisation (`PLGB 44221/0003`, renewed 24 Feb 2026) remains under active review post-EU-non-renewal (SMC 2827 declined routine NHSScotland use on 8 Jun 2026); arimoclomol's EU product is branded Meplyffa (`EMEA/H/C/006736`, distinct from US Miplyffa) and the 23 Jul 2026 CHMP negative opinion was Zevra's *second* EU attempt (first withdrawn 2022) — re-examination started at the 14–17 Sep 2026 CHMP plenary and remained pending on the 12–15 Oct 2026 CHMP agenda (`EMA/CHMP/211366/2026` §3.5.1, no outcome in 16 Oct 2026 highlights). Ravicti, amlexanox, metformin, rilmenidine, ELX-02, and the "no newer readthrough drug approved since 2025" claim were re-checked and hold. Detail: `track2/track2_report.md` §Regulatory audit refresh.

Files: `track2/track2_report.md` (`submissions/Ryukijano_track2_report.md`), `track2/data/track2_candidates.csv`, `track2/pitch_storyboard.md`, and the programmatic 3-minute pitch pipeline in `video/` (rendered pitch: https://github.com/user-attachments/assets/9fbcac33-27c9-40d2-ac94-f2df7fb43884).

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

**Retrieval-sort sensitivity verification:** Because the initial L2S2 data was retrieved with the server's default mimic-sorted order (`pvalue_up`), all L2S2 queries were re-executed with `sortby=adj_pvalue_down` (rescue-first retrieval; `track2/lincs/results/rescue_firewall/comparison_summary.md`). The firewall verdict is unchanged (`ACCEPT = 0 / WEAK = 2 / REJECT = 472`), and the rescue-sorted re-query surfaced additional mimic signatures for both sirolimus and dasatinib, reinforcing the `MIXED` penalty.

**Absence of a LINCS hit is not evidence against** amlexanox, Ataluren, Ravicti, arimoclomol, metformin, rilmenidine, NMN, JAK inhibitors, or Nrf2 drugs. No LINCS result establishes BUBR1 rescue, SAC correction, or patient benefit.

Method: `track2/lincs/README.md`. Tables: `track2/lincs/results/lincs_firewall_decisions.csv`, `track2/lincs/results/lincs_candidate_ranking.csv`, `track2/lincs/results/signature_composition.csv`.

---

## 6. What we built (engineering)

| Piece | Where |
|---|---|
| Track 1 CLI (VEP → filter → SpliceAI → score → pair → CSV) | `scripts/run_track1.py`, `src/mva_hackathon/variants/` |
| Local clone of the official scorer | `src/mva_hackathon/eval/scorer.py`, `tests/test_scorer.py` |
| ChEMBL axis screen (must include FKBP1A) | `track2/drug_screen.py` |
| ESM-1v / PrimeKG / Open Targets / ClinVar B/LB | `src/mva_hackathon/research/`, `scripts/slurm/run_research.sh`, `experiments/2026-10-11_esm1v_fixed/` |
| AlphaFold DB v6 / PAE / Saturation AlphaMissense / PDB complexes | `experiments/2026-10-11_alphafold_bubr1/`, `figures/` |
| LINCS GEO → DE → L2S2/L1000CDS2 → firewall | `track2/lincs/` |
| Programmatic 3-minute Track 2 pitch video + QA | `video/` (`tts.py`, `render/`, `assemble.sh`, `qa.py`) |
| AIRE env | `/mnt/scratch/kcwp264/.conda_envs/mva-hackathon` (VEP 116); `cjepa` for ESM; `mva-hackathon-lincs` for GEO/LINCS |

**Never on GitHub / Hub:** `data/` genome, `refs/` VEP cache and PrimeKG `kg.csv`, `.cache/`, phenotype `.docx`, `MVA Track 1 Debugging (1).md`.

---

## 7. How to read this against a submission

| Claim | After this campaign |
|---|---|
| Compound-het *BUB1B* is the Track 1 genotype | **Confirmed (full match at rank 1, 100/100 pts, F-max 1.000).** Panel uniqueness + ClinVar PTV + architecture. |
| N1002K is AlphaMissense likely-pathogenic | **Unchanged (`0.9229`, 18/19 `LPath` at residue 1002 due to buried 3-H-bond α-helix C-cap)**, and **opposed** by 1D sequence-only ESM-1v (`−0.110` in `29–1050`; `−0.0625` in `1–1022`). Report both. |
| N1002K is “like L1012P” | **Do not say this.** `12.32 Å` `Cα–Cα` separation; ESM-1v gap `1.69–2.10 nats`. |
| Amlexanox / proteostasis / autophagy / gated JAK as the stack | Mechanism-first ranking **stands** (with AlphaMissense showing all three `UGA` readthrough insertions `L737W/R/C` are `Likely Benign`, `0.150–0.322`). PrimeKG does **not** recover rapalogs; LINCS yields only a **context-specific WEAK/MIXED** sirolimus signal after the false-rescue firewall — and rapamycin is itself aneugenic (see §5), so this is not a rescue lead. |
| Graph/AI discovered the therapy | **Do not say this.** |
| NMN is the +58% lifespan result; NAC rescued fly brain size | **Do not say this.** |
| TxGNN/PrimeKG GNN was trained | **Never built.** README no longer claims it. |

---

## 8. Final pre-close checklist (close: 24 Oct 2026 23:59 UTC)

1. **Track 1:** **DONE (12 Sep 2026)** — CSV + report + GitHub URL submitted; full match at rank 1 (`100.0/100` rank points, `F-max 1.000`, 1/6 shots spent).
2. **Track 2 dossier & 3-minute pitch video:** Report (`submissions/Ryukijano_track2_report.md`) and programmatic 3-minute pitch video (`video/`, https://github.com/user-attachments/assets/9fbcac33-27c9-40d2-ac94-f2df7fb43884) are complete and QA-verified; ready for final Track 2 Space upload (user decision).
3. **Post-close data hygiene:** Delete all gated genome/FASTQ/VCF/BAM files from AIRE scratch within 30 days of challenge close per the DTA.

That is the campaign: a scorer-confirmed one-row MVA1 call, an honest hypomorph drug stack with a primary-source regulatory audit and structural proofs. Two pre-registered computational tests **failed as written**, and an exploratory LINCS screen generated only a context-specific `WEAK/MIXED` sirolimus signal without pretending that a graph or an unbiased screen independently validated a therapy.
