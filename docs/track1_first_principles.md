# Track 1 from first principles — what we called, why, and how it stands against the literature

**Status:** synthesis for the Track 1 methods write-up and submission decision (7 Sep 2026).
**Scope:** challenge mechanics (verified from the Space's public source), SAC/BUBR1 biology, both alleles, the published MVA1 record, and an honest accounting of what we have actually done.
**Integrity note:** we read the Space's public `evaluation.py`/`config.py`/tabs for scoring mechanics. We deliberately did **not** open `groundtruth.py` or the private `SageBio/mva-hackathon-2026-gt` answer key — reverse-engineering the answer would invalidate the exercise.

---

## 1. What Track 1 actually asks (verified from the Space source)

One proband. Submit a ranked CSV (`proband_id, chrom_1, pos_1, ref_1, alt_1, chrom_2, pos_2, ref_2, alt_2, epcr`, optional `finding_type`/`notes`), ≤10 rows, EPCR in (0,1]. Two automated metrics, adapted from the CAGI6 Rare Genomes Project Challenge (Stenton et al. 2024, *Hum Genomics* — local copy `research_papers/s40246-024-00604-w.pdf`):

- **Rank points:** full match (both true variants in one row) at rank 1 → **100**; ≤3 → 50; ≤5 → 25; ≤10 → 10. If the truth is a compound het and you recover only one variant, you get **half** the tier points of your best partial row.
- **F-max:** variant-level precision/recall swept over your EPCR thresholds. A single row containing exactly the true pair at EPCR 0.95 → precision 2/2, recall 2/2 → **F = 1.0**.

Scoring arithmetic for our submission:

| Scenario | Rank points | F-max |
|---|---|---|
| Our pair is exactly right (rank 1) | **100** | **1.0** |
| One allele right, one wrong | 0.5 × 100 = **50** | 0.5 (tp=1, fp=1, fn=1 at the 0.95 threshold) |
| Both wrong | 0 | 0 |

Hedging does not help: extra secondary rows cannot raise F-max above the primary row's value in the partial-match scenario, and the FAQ confirms secondary/incidental rows "won't hurt" but also cannot help the automated score. The FAQ also states that **perfect scores already exist on the leaderboard** — Track 1 is a foundational track, and the differentiator is the **methods write-up**, judged for scientific rigor. That is what this document feeds.

---

## 2. First principles: why a SAC dose problem produces MVA

**The spindle assembly checkpoint (SAC)** delays anaphase until every kinetochore is attached. Unattached kinetochores catalyse formation of the **mitotic checkpoint complex (MCC)** — Mad2–BubR1–Bub3 bound to Cdc20 — which inhibits the APC/C, blocking cyclin-B/securin degradation. When the last kinetochore attaches, the MCC dissolves, APC/C fires, anaphase begins.

**BUBR1 (BUB1B, O60566, 1050 aa)** is the Mad3 paralogue and the MCC's effector core:

- **N-terminal region (≈1–350):** KEN-box/ABBA-motif cassette that binds Cdc20 and blocks APC/C substrate recruitment (structures: Chao et al. 2012, *Nature* 484:208; Alfieri et al. 2016, *Nature* 528:217 — both in `research_papers/`).
- **GLEBS motif (≈385–400):** binds BUB3; required for kinetochore recruitment.
- **KARD/PP2A-B56 docking region (≈660–680):** recruits PP2A-B56 to protect kinetochore substrates from Aurora B; contains **K668**, the SIRT2 deacetylation site (North et al. 2014, *EMBO J* 33:1438).
- **C-terminal pseudokinase (≈720–1050):** retains the catalytic triad but is **catalytically dispensable** (Suijkerbuijk et al. 2012); its role is conformational stability. MVA missenses here (R814H, L1012P) **destabilise the protein** rather than abolish catalysis.

**The dosage ladder (Baker et al. 2004, *Nat Genet* 36:744):**

| Residual BubR1 protein (MEFs) | Genotype | Outcome |
|---|---|---|
| 0% | *Bub1b −/−* | embryonic lethal |
| 4% ± 2% | *Bub1b −/H* | death within hours of birth |
| **11% ± 3%** | *Bub1b H/H* | viable, progeroid, aneuploid, infertile |
| 100% | WT | normal |

**Why this predicts the human architecture.** A viable MVA1 patient needs *some* BUBR1 function: enough to build, occasionally, but not enough to checkpoint reliably. That is exactly what **one null allele + one destabilising missense allele in trans** provides — the missense allele's residual protein (~2–6-fold reduced in patient cells, Suijkerbuijk 2010) is the only source of BUBR1. Hanks et al. 2004 found precisely this pattern in 5/8 MVA families ("inherited from different parents, indicating that they were on separate alleles"), and Suijkerbuijk et al. 2010 summarise: "a missense mutation pairs with a truncating mutation." Two null alleles are not observed in live births.

**Why the phenotype is mosaic and variegated.** The genotype is germline and constitutional; the aneuploidy is not. Each mitosis in the embryo is a coin flip with bad odds: the SAC sometimes holds, sometimes releases early, so different lineages acquire different whole-chromosome gains/losses — mosaic, variegated aneuploidy. The same failure keeps generating micronuclei (cGAS–STING, Harding/Mackenzie 2017), interferon/IL-6 signalling, proteotoxic load (Ben-David & Amon 2019), and — in the germline-relevant tissues — the progeroid features shared with *BubR1^H/H* mice.

**Why cancer.** Chronic CIN plus checkpoint failure is oncogenic (Davoli et al. 2017): ~37% of BUB1B-MVA patients develop cancer, mostly early-childhood rhabdomyosarcoma, Wilms tumour, and leukemia (Hanks 2004; Malumbres & Villarroya-Beltri 2024 — local PDF).

---

## 3. The call, allele by allele

### Allele 1 — `chr15:40209701 T>G`, `c.2210T>G`, `p.Leu737Ter`

- **ClinVar VCV000533901** (verified 7 Sep 2026 via NCBI): `NM_001211.6(BUB1B):c.2210T>G (p.Leu737Ter)`, **Pathogenic/Likely pathogenic, criteria provided, multiple submitters, no conflicts**; condition **Mosaic variegated aneuploidy syndrome 1** (RCV000641226.9, Pathogenic, Oct 2024).
- **Functional class:** UGA stop one codon before the classic Hanks 2004 frameshift `c.2211insGTTA` (`p.Ser738Valfs*753`, historically "753X"). Both truncate the same region: everything from the pseudokinase C-lobe onward is lost, while the N-terminal KEN/ABBA cassette, GLEBS, and the KARD/PP2A region are retained. Our allele is therefore in the **same truncation class as the canonical MVA1 truncating allele**, one codon apart.
- **NMD:** truncating BUB1B alleles show absent/reduced transcript in patient cells (Suijkerbuijk 2010) — the dominant loss mechanism is mRNA decay, so this allele is expected to contribute ≈0 protein. (Relevant to Track 2: readthrough first requires NMD escape.)
- **Population frequency (gnomAD v4, checked 7 Sep 2026):** exomes ac=115 (AF ≈ 7.9e-05), genomes ac=5 (AF ≈ 3.3e-05). Passes our ≤0.001 rarity filter. This is **expected, not concerning**, for a recessive LoF allele: heterozygous carriers are the unaffected parents seen in Hanks 2004.
- **Provenance:** not among the historical MVA1 patient alleles (Hanks 2004 lists `2211insGTTA`, not `c.2210T>G`); the exact `c.2210T>G` independently appears in a 2025 germline glioblastoma-predisposition series as a recessive BUB1B LoF allele with a somatic second hit (npj Genomic Medicine, 2025, Table 1) — external recurrence of the exact nucleotide change, in a tumour-predisposition context.

### Allele 2 — `chr15:40220612 T>G`, `c.3006T>G`, `p.Asn1002Lys`

- **Location:** pseudokinase C-lobe, 10 residues from the established MVA1 missense **L1012P** (Hanks 2004) and in the same lobe as R814H. The pseudokinase's disease mechanism is **protein destabilisation**, not catalysis (Suijkerbuijk 2012).
- **Predictors conflict, and we say so:** AlphaMissense **0.9229** (likely_pathogenic) vs ESM-1v ensemble LLR **−0.110** — the **3rd-mildest of 19 substitutions** at residue 1002 (verified against `esm1v_bub1b_llr.csv`; only Q and S are milder) and milder than the ClinVar B/LB median (−0.161, rank 18/34). AlphaMissense is the stronger pathogenic signal; ESM-1v argues the site tolerates conservative charge preservation.
- **External databases (checked 7 Sep 2026):**
  - **ClinVar VCV4600147**: `c.3006T>A (p.Asn1002Lys)` — **same protein change, different nucleotide** — Uncertain significance, criteria provided, single submitter, last evaluated 11 Jan 2026. Our exact `c.3006T>G` allele: **0 ClinVar records**.
  - **gnomAD v4**: absent from genomes; **one allele in exomes** (AF ≈ 6.8e-07). The earlier "absent from gnomAD" claim was true for the VEP-cache annotation used at run time but is **not true of current gnomAD v4** — corrected in the report.
- **Interpretation:** a rare, observed, unclassified C-lobe missense. As a single variant it is a VUS; its weight comes from the **architecture** — it is the only partner allele available for the ClinVar-pathogenic truncation in the only panel gene with two rare functional alleles.

### Why compound heterozygous *BUB1B* is the answer

1. **Panel uniqueness:** after VEP 116 + 15-gene MVA panel + AF ≤ 0.001 + relevant consequences, *BUB1B* was the only gene carrying two rare functional alleles.
2. **Architecture match:** truncating + missense is the canonical viable MVA1 pattern (Hanks 2004; Suijkerbuijk 2010); two truncations are not viable (mouse: −/− lethal, −/H perinatal lethal, X753/L1002P lethal).
3. **Allele-level evidence:** one allele is ClinVar P/LP for MVA1 specifically; the other is a rare pseudokinase-lobe missense consistent with the destabilising-hypomorph class.
4. **In trans is inferred, not proven:** both alleles are heterozygous in the proband VCF; no parental sample exists in the challenge data. This is stated as a limitation everywhere it matters.

---

## 4. What is out there vs what we did

| Question | Published record | Our position |
|---|---|---|
| Is biallelic *BUB1B* the MVA1 gene? | Yes — Hanks 2004, Suijkerbuijk 2010, GenCC/OMIM | Called, with panel-uniqueness argument |
| Typical viable genotype? | truncating + missense **in trans** | Same architecture; phasing inferred |
| Is `p.Leu737Ter` an MVA1 allele? | Not in the historical patient series; ClinVar P/LP for MVA1 (multiple submitters); exact T>G recurs in a 2025 GBM-predisposition study | Used as allele 1 on ClinVar + truncation-class equivalence to `2211insGTTA` |
| Is `p.Asn1002Lys` known? | Protein change: ClinVar **VUS** (VCV4600147, `c.3006T>A`, single submitter, Jan 2026). Our `T>G` nucleotide allele: not in ClinVar; 1 gnomAD v4 exome allele | Reported honestly as VUS-class; not claimed as novel at the protein level |
| Is N1002K like L1012P? | 10 residues apart; no functional data for N1002K | **No** — pre-registered ESM-1v test falsified the equivalence (gap 1.69 nats); ClinVar B/LB control agrees |
| Residual BUBR1 in the child? | Never measured; mouse *H/H* = 11% ± 3% | Quoted as mouse value only |
| Could anything else be causal? | MVA2 = CEP57 (Snape 2011), MVA3 = TRIP13; centromere/centrosome genes in the panel | Filtered out by rarity/consequence; no competing pair |

**Corrections applied today (before submission):** "novel missense" → ClinVar VUS via `c.3006T>A` (VCV4600147); "absent from gnomAD" → gnomAD v4 counts for both alleles (1 exome allele for N1002K; ~120 alleles for L737Ter, recessive-compatible); residual "~5–10%" → "11% ± 3% (Baker 2004, mouse)". All three changes make the write-up *more* defensible — a judge checking ClinVar or gnomAD will find exactly what we now state.

---

## 5. What we have actually done (the honest ledger)

**Built:** a reproducible Track 1 CLI (VEP 116 offline + AlphaMissense + popEVE → 15-gene panel → rarity filter → SpliceAI `-D 500` → score → pair → CSV), a local clone of the official scorer, and AIRE Slurm wrappers. The submitted CSV is one row, EPCR 0.95, `finding_type=primary`.

**Ran and reported honestly:** two pre-registered computational hypotheses, both **falsified as written** — H1 (N1002K ≈ L1012P; ESM-1v gap 1.69 nats; B/LB median −0.161, rank 18/34) and H2 (PrimeKG does not rank rapalogs near MVA). Neither changed the CSV; both changed what we claim.

**Known limitations (all stated in the report):** no parental phasing; no FASTQ-level mosaic/VAF analysis; no functional validation; phenotype parsed but not used as a scoring feature; the 10-row intermediate run (job 7548994) was superseded by the curated 1-row call after the AF-filter fix.

**Pipeline bugs found and fixed during the campaign:** AF filter key (`gnomad_af` → `gnomADg/e_AF`), SpliceAI `-D` cap (4999; we use 500), popEVE field fallbacks (`popEVE_SCORE` → `popEVE` → `popEVE_pop_adjusted_EVE`), dead cancer-EPCR bonus removed.

**Known code nits (non-blocking, issue #4):** popEVE `or`-fallback skips a legitimate 0.0; in-frame indels fall through to score 0.0; several config thresholds unenforced.

---

## 6. Submission readiness

- [x] CSV format matches the official 10+2-column contract; EPCR 0.95 in (0,1]; single primary row.
- [x] Local scorer says a full match yields 100 rank points / F-max 1.0 (`pytest tests/test_scorer.py`, 20/20 pass).
- [x] Methods write-up (`submissions/Ryukijano_track1_report.md`) corrected against ClinVar (7 Sep 2026), gnomAD v4, and the published MVA1 record.
- [x] Honest limitations: phasing inferred; N1002K is VUS-class with discordant predictors; residual % is mouse literature.
- [ ] **Decision: spend 1 of 6 shots.** Rationale for spending one now: the call is stable, the write-up is now externally cross-checked, and the FAQ confirms the write-up is judged — earlier submission leaves time for a second shot only if the panel-facing materials change. There is no automated-score reason to wait.
- [ ] Optional before upload: re-verify ClinVar/gnomAD pages on submission day (both are live databases; VCV4600147 could be reclassified).

**What would change our mind (falsifiers):** parental phasing showing the two variants in cis; a credible second rare pair in another panel gene (none exists in the current filtered output); N1002K reclassified benign in ClinVar (would downgrade allele 2 to a modifier, not overturn the *BUB1B* gene call, since the architecture argument would then rest on L737Ter + an unclassified partner).

---

## 7. Key references

1. Hanks S, et al. *Nat Genet* 2004;36:1159–61 — biallelic *BUB1B* in MVA; truncating + missense in trans; L1012P.
2. Baker DJ, et al. *Nat Genet* 2004;36:744–9 — *BubR1^H/H* = 11% ± 3% residual protein; dosage ladder.
3. Suijkerbuijk SJE, et al. *Cancer Res* 2010;70:7981–91 — patient genotypes; missense pairs with truncating; NMD dominates; 2–6-fold reduced BUBR1.
4. Suijkerbuijk SJE, et al. 2012 — pseudokinase catalysis dispensable; stability role.
5. Rio-Frio T, et al. *NEJM* 2010;363:2628–37 — homozygous hypomorphic splice in adult MVA with GI neoplasia.
6. Snape K, et al. *Nat Genet* 2011;43:527–9 — CEP57/MVA2 (genetic heterogeneity).
7. Chao WCH, et al. *Nature* 2012;484:208–13; Alfieri C, et al. *Nature* 2016;528:217–22 — MCC structure; KEN/ABBA cassette.
8. North BJ, et al. *EMBO J* 2014;33:1438–53 — SIRT2/K668; SIRT2-Tg lifespan in *BubR1^H/H*.
9. Malumbres M, Villarroya-Beltri C. *Nat Rev Genet* 2024 — MVA genetics; ~37% cancer frequency; SAC-core tumour spectrum.
10. Stenton SL, et al. *Hum Genomics* 2024 — CAGI6 RGP Challenge scoring (basis of the official Track 1 metrics).
11. ClinVar VCV000533901.9 (`c.2210T>G` p.Leu737Ter, P/LP, MVA1, multiple submitters); ClinVar VCV4600147 (`c.3006T>A` p.Asn1002Lys, VUS, single submitter, Jan 2026).
12. gnomAD v4: 15-40220612-T-G (exome ac=1, AF 6.8e-07; genomes absent); 15-40209701-T-G (exome ac=115, AF 7.9e-05; genomes ac=5).
