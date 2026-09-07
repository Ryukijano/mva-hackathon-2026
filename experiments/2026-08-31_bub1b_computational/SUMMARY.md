# What we did — ESM-1v / PrimeKG / ClinVar campaign

**Folder:** `experiments/2026-08-31_bub1b_computational/`  
**Dates:** 31 Aug – 1 Sep 2026  
**Whole-repo wrap-up (Track 1 + Track 2 + LINCS):** [`../../WHAT_WE_DID.md`](../../WHAT_WE_DID.md)

This note is the wrap-up of the **pre-registered protein-LM and knowledge-graph campaign only**. Pre-registration lives in `protocol.md`. Tables and job IDs live in `outputs/RESULTS.md`. Figures are in `outputs/figures/`.

---

## 1. The challenge, in one paragraph

**Rare Disease, Real Kid: MVA Hackathon 2026** (SageBio Space) asks two things of one child, PROBAND01. Track 1: name the causal genotype from a gated WGS VCF (six CSV submissions, ranked). Track 2: propose a therapy, with a written dossier, GitHub URL, and a 3-minute video. The genome never left AIRE scratch and was never sent to third-party LLM APIs. Ranked findings and code may be public; FASTQ/VCF/phenotype source files are not in the repos.

We built a reproducible Track 1/2 pipeline, made a compound-het call in *BUB1B*, wrote an honest Track 2 stack, then **pre-registered and ran** two extra experiments (protein language model + knowledge-graph ranking) so the missense and the drug neighbourhood could be tested independently of the original screen.

---

## 2. Track 1 — the call we still stand on

After Ensembl VEP **116** (GRCh38), a 15-gene mitotic panel, gnomAD AF ≤ 0.001, and SpliceAI on the tiny candidate VCF, **only *BUB1B* had two rare functional alleles**. That uniqueness is why the CSV is one row, not a learned ranker.

| Allele | GRCh38 | NM_001211.6 | Role |
|---|---|---|---|
| 1 | `chr15:40209701 T>G` | `c.2210T>G` `p.Leu737Ter` | ClinVar Pathogenic/LP for MVA1 ([VCV000533901](https://www.ncbi.nlm.nih.gov/clinvar/variation/533901/)) |
| 2 | `chr15:40220612 T>G` | `c.3006T>G` `p.Asn1002Lys` | Novel C-lobe **pseudokinase** missense; AlphaMissense **0.9229**; ESM-1v mild; absent from gnomAD |

Submitted EPCR **0.95**, `finding_type=primary`. Architecture is the textbook viable MVA1 pattern: truncating + hypomorphic missense (Hanks et al., 2004). Human BUBR1’s C-terminus is a **pseudokinase**. Phasing is inferred (both het in the VCF), not parental. Residual ~5–10% BUBR1 is the *BubR1^H/H* mouse literature, **not** measured in this child.

**This campaign did not change the Track 1 CSV.** ESM-1v later showed that N1002K is a *mild* protein-LM allele (see §4). The call still rests on gene uniqueness, the ClinVar PTV, AlphaMissense, gnomAD absence, and architecture — not on “N1002K looks like L1012P in ESM-1v,” because it does not.

CSV and methods: `submissions/Ryukijano_bub1b-compoundhet.csv`, `submissions/Ryukijano_track1_report.md`. Track 1 was **not** auto-submitted (six-shot quota).

---

## 3. Track 2 — mechanism-first drugs, stated at paper strength

Disease is **hypomorphism, not gain of function**. Therapy has to stabilize remaining BUBR1, blunt proteotoxic/mitochondrial damage, and damp the micronuclei → cGAS–STING → IFN/IL-6 cascade. We **do not** silence the gene.

| Tier | Proposal | What the papers actually show |
|---|---|---|
| 1a | Ataluren (PTC124) / ELX-02 | UGA stop-codon readthrough for p.Leu737Ter; intended to restore full-length BUBR1, contingent on the nonsense transcript escaping nonsense-mediated decay and on context-dependent readthrough — untested for this allele (Keeling 2016; Peltz 2008; ELX-02 Phase 2 CF). |
| 1b | NMN / nicotinamide riboside | Raise **BUBR1 protein** via SIRT2 deacetylation of K668 (North et al., 2014 *EMBO J* **33:1438–1453**, doi:10.15252/embj.201386907). The **+58% / +123% lifespan** result is **SIRT2-Tg** in *BubR1^H/H*, **not** NMN. |
| 2a | Glycerol phenylbutyrate (Ravicti) / arimoclomol | 4-PBA rescues aneuploidy-associated protein aggregates and apoptosis in human iPSC neurons (Fisher 2020). Ravicti is the sodium-free, paediatric-approved prodrug. Arimoclomol (Miplyffa) is HSF1/HSP and lysosomal amplifier; cancer risk caveat. |
| 2b | Trehalose / spermidine | mTORC1-independent TFEB/autophagy-lysosome inducers; aneuploid cells activate TFEB (Santaguida & Amon 2015). |
| 2c | Rapalogs, ROS/Nrf2 (caution) | Fly TOR depletion / larval rapamycin rescued **neuroblast counts**, not brain size. Brain-size rescue was **Sod2 / GTPx-1 overexpression**, not NAC. NAC/Nrf2 activators carry oncogenic/metastatic risk (Piskounova 2015; Sayin 2014; Taguchi 2011). |
| 3 | JAK/IL-6 (biomarker-guided) | Baricitinib / ruxolitinib / tocilizumab as adjuncts for the IFN/IL-6 arm. |

**Excluded:** TTK/MPS1 inhibitors, Aurora B inhibitors, STING agonists (wrong-direction SAC or inflammation).

ChEMBL was the drug table. Open Targets 26.06 recovered JAK inhibitors, omaveloxolone, tocilizumab, and the STING agonist ADU-S100; **sirolimus/everolimus are not on the MTOR list** (FKBP1A annotation). BUB1B and SIRT2 have zero OT drugs.

Track 2 is still **blocked on the 3-minute YouTube/Vimeo pitch**. Storyboard: `track2/pitch_storyboard.md`.

---

## 4. What we computed (this folder)

Two hypotheses were written down **before** looking at the new scores (`protocol.md`).

### H1 — is N1002K an L1012P-class missense? **No.**

ESM-1v ensemble (five `facebook/esm1v_t33_650M_UR90S_{1–5}` models), masked LLR on UniProt **O60566** (1050 aa). No patient sequence on GPUs. First GPU job died because ESM-1v only accepts **1022 amino acids**; we windowed to residues 29–1050 (A1).

| Allele | Ensemble LLR (nats) |
|---|---|
| **N1002K** (this child) | **−0.110** — third-mildest of 19 substitutions at residue 1002 |
| L1012P (literature MVA) | **−1.801** |
| R814H (literature MVA) | **−1.444** |
| K668Q (acetylation mimic, not MVA) | −0.309 |

Pre-registered: N1002K within **0.5 nats** of L1012P. Observed gap **1.69 nats** → **falsified**. N1002K is the **third-mildest** (or 17th-most-severe) of 19 substitutions *at that residue*. The **site** is constrained (worst AA W = −3.70); this **allele** (Asn→Lys) is chemically mild.

**Interpretation update:** ESM-1v is a sequence-only masked language model and underweights structural destabilisation in non-catalytic pseudokinase scaffolds. AlphaMissense (0.9229), which uses AlphaFold-derived structural context, is the stronger pathogenic signal. The classic MVA1 L1012P allele was shown by *Suijkerbuijk et al., 2010* to impair BUBR1 **protein stability** (increased proteasomal degradation) rather than intrinsic catalytic activity. N1002K, located 10 residues away in the same C-lobe, is biologically consistent with a destabilising hypomorphic allele.

ClinVar B/LB control (A5; 34 unique NM_001211.6 missenses, WT-checked against O60566):

| | LLR |
|---|---|
| B/LB median | **−0.161** |
| N1002K | **−0.110** (rank 18/34) |
| L1012P | −1.801 (below the entire B/LB cloud) |

Second falsifier also **met**: N1002K is less damaging (less negative LLR) than the B/LB median, placing it in the benign/likely-benign cloud. AlphaMissense **0.9229** remains the stronger pathogenic *in silico* for this allele; the two methods disagree.

ClinVar notes, not to mix up: a **VUS** exists for p.Asn1002Lys on **`c.3006T>A`** (VCV4600147), not this child’s **`c.3006T>G`**. L1012P is ClinVar VUS; R814H is conflicting. Almost no BUB1B missense is P/LP in ClinVar (exception Q467H).

### H2 — does PrimeKG put sirolimus next to MVA? **No.**

Skip-gram embeddings (dim 64, 50 epochs, seeds 0/1/2) on a 1-hop PrimeKG neighbourhood of axis genes + MVA disease nodes. Query landed on parent *mosaic variegated aneuploidy syndrome*, not MVA1.

| Setting | Drugs | Sirolimus mean rank | What ranked top |
|---|---|---|---|
| E2 (pre-registered; TTK/AURKB/TMEM173 in seeds) | 37 | **22.0** | JAK inhibitors (Fedratinib 2.3, Baricitinib 9.0). TTK inhibitor BOS172722 **20.7** (above sirolimus). |
| E2b (anti-target seeds dropped) | 31 | **16.7** | Sarilumab / ruxolitinib 2.7, tocilizumab 3.7. Same qualitative result. |

H2 **falsified** (sirolimus outside top 50% **and** a TTK inhibitor above it). Cosines were negative on this small graph; ranks still order JAK > rapalogs. Honest use: a **JAK/IL-6 neighbourhood prior**, not evidence that the graph “found” rapamycin. Mechanism-first ChEMBL ranking stands.

---

## 5. Figures

All under `outputs/figures/` (PDF + 300 dpi PNG, Okabe–Ito colours).

| File | Message |
|---|---|
| `fig1_esm1v_named_llr` | N1002K is far milder than L1012P / R814H |
| `fig2_esm1v_clobe_trace` | C-lobe *sites* are constrained; the N1002K *allele* is not |
| `fig3_primekg_watched_drugs` | E2: JAK on top, rapalogs mid-pack, BOS172722 above sirolimus |
| `fig4_primekg_e2b_no_antitarget` | E2b: same after dropping anti-target seeds |
| `fig5_esm1v_clinvar_blb` | N1002K sits on the ClinVar B/LB cloud; L1012P does not |

---

## 6. What we did *not* do

- Did not train TxGNN from scratch (pretrained weights gated; fetch timed out).
- Did not put genome, VCF, or phenotype `.docx` on GPUs, GitHub, or Hugging Face.
- Did not burn a Track 1 leaderboard submission.
- Did not claim NMN is the +58% lifespan result, NAC as the fly brain-size rescue, or residual 5–10% BUBR1 as a measurement in this child.

---

## 7. How to read this against the submission

| Claim in the dossier | After this campaign |
|---|---|
| Compound-het *BUB1B* is the Track 1 genotype | **Unchanged.** Panel uniqueness + PTV + architecture. |
| N1002K is AlphaMissense likely-pathogenic | **Unchanged**, and now **opposed** by ESM-1v / ClinVar B/LB LLRs. Report both. |
| N1002K is “like L1012P” | **Do not say this.** Ten residues away; ESM gap 1.69 nats. |
| Rapalogs / NAD+ / JAK as the stack | **Unchanged** as mechanism-first ranking. PrimeKG does **not** independently recover rapalogs; it recovers JAK/IL-6. |
| Graph/AI discovered the therapy | **Do not say this.** |

---

## 8. Where the code and data are

| Path | Contents |
|---|---|
| `protocol.md` | Pre-registration + amendments A1–A5 |
| `outputs/RESULTS.md` | Numeric log |
| `outputs/e2_preregistered/` | Frozen H2 ranks (do not overwrite) |
| `outputs/e2b_no_antitarget/` | Exploratory ablation |
| `outputs/e1c_clinvar/` | ClinVar B/LB table + ESM scores |
| `src/mva_hackathon/research/` | ESM-1v, PrimeKG, Open Targets, ClinVar parsers |
| `scripts/slurm/` | AIRE batch scripts (`gpu` / `nodes`; no login-node GPU) |
| `track2/data/O60566.fasta` | Public UniProt sequence (668=K, 737=L, 814=R, 1002=N, 1012=L) |
| `refs/primekg/kg.csv`, `refs/clinvar/variant_summary.txt.gz` | Gitignored source extracts |

Environment for the L40S ESM run: torch 2.13.0+cu126, transformers 5.14.1, `cjepa` env. Track 1 pipeline env is `mva-hackathon` (no torch).

---

## 9. LINCS (not in this folder)

A later Track 2 screen (`track2/lincs/`) queried GEO MVA/*BubR1* signatures through L2S2 + L1000CDS2 and applied a false-rescue firewall. The firewall now gates on L2S2 **directional reverse FDR** (`adj_pvalue_down < 0.05`). Results: **sirolimus WEAK** (2 engines, 4 total signatures, **1** FDR-significant reverse signature in GSE22206 `adj_pvalue_down = 9.14e-05`, but a mimic in 4 other significant L2S2 contexts; 3 L1000CDS2 signatures, mean score 0.045; further caveat: rapamycin itself induces chromosome malsegregation and CREST-positive micronuclei — Bonatti et al. 1998, *Chromosoma* 107:498–506 — so the signal is treated as a context-specific observation with a mechanism-based anti-target concern, not a lead); **dasatinib WEAK** (1 FDR-significant reverse signature `adj_pvalue_down = 1.51e-05`, downgraded to conditional senolytic adjunct); **everolimus REJECTED** (general/mimic FDR but no significant reverse and no L1000CDS2 support); **perhexiline REJECTED** (pediatric safety). The L2S2 signal is context-specific and exploratory, not an independent or cross-species validation. That does **not** reopen H2: PrimeKG still failed to rank rapalogs next to MVA. See `../../WHAT_WE_DID.md` §5.

## 10. Still open (this experiment)

Optional extras we did not run: ClinVar *benign-only* (exclude single-submitter LB), 2-hop PrimeKG, full-protein ESM trace.

H1 and H2 **failed as written** and should be reported that way. The Track 1 CSV is unchanged.
