# BUB1B variant contract (MVA Hackathon 2026)

Do not contradict these facts in reports, pitches, or AlphaGenome write-ups.

## Alleles (GRCh38, NM_001211.6)

| Role | Variant | HGVS | Evidence |
|---|---|---|---|
| Allele 1 | `chr15:40209701 T>G` | `c.2210T>G` `p.Leu737Ter` | ClinVar P/LP MVA1 [VCV000533901](https://www.ncbi.nlm.nih.gov/clinvar/variation/533901/); dbSNP rs759242053; gnomAD v4 exome AC≈115 AF≈7.9e-05 (recessive-carrier compatible) |
| Allele 2 | `chr15:40220612 T>G` | `c.3006T>G` `p.Asn1002Lys` | AlphaMissense **0.9229**; ESM-1v ensemble LLR **−0.110** (mild; **not** L1012P −1.801); popEVE **absent**; our `T>G` ClinVar-absent; same protein via `c.3006T>A` is VUS **VCV004600147.1** (SCV007198955, 19 Sep 2025, "Inborn genetic diseases"); dbSNP rs2542593804; gnomAD v4 1 exome allele AF≈6.8e-07 |

CSV: `PROBAND01`, EPCR `0.950000`, `finding_type=primary`, one row.
`submissions/Ryukijano_bub1b-compoundhet.csv`.

## Architecture

Canonical viable MVA1: truncating/null + hypomorphic missense (Hanks 2004). Biallelic null is embryonic lethal. L737Ter removes the C-terminal **pseudokinase**; KEN/ABBA motifs are retained. Residual BUBR1 **11% ± 3%** is *BubR1^H/H* (Baker 2004), **not** measured in this child.

Phasing: WhatsHap **UNRESOLVED** (10.9 kb gap, ~1.3 kb max insert, 1 intervening het SNV, PGT absent). Submit as **presumed** compound-het. LR-PCR primers: `scripts/design_lrpcr_primers.py` (~11.1 kb). Plan: `docs/phasing_validation_plan.md`.

## In-silico already done

- SpliceAI `-D 4999` full-gene: max DS 0.03 / 0.02 — not splice-driven (`supplement/track1/`)
- AlphaGenome AVI: Phred **33.76** (Protein Termination) / **25.61** (AlphaMissense) — supportive only
- Falsifier audit: `supplement/track1/locus_falsifier_audit.md` (17-gene panel incl. SLF2/SMC5; no competing compound-het)

## Scoring (do not invent a new EPCR)

PTV 0.99; missense `0.7 × popEVE_sigmoid + 0.3 × AlphaMissense`; popEVE missing → AlphaMissense for both terms; pair product floored to `primary_epcr: 0.95`. Space scorer: full match rank 1 = 100 + F-max 1.0; one allele wrong = 50 + F-max 0.5. Hedging rows do not help. Do not open ground truth.

## Track 2 stack (do not blur)

1. **Stop-gain rescue:** Amlexanox (approved topical; NMD + readthrough) is the mechanistically matched approved option. Ataluren = UK/MHRA conditional only; FDA NDA withdrawn 12 Feb 2026; EMA non-renewal 28 Mar 2025. ELX-02 investigational → future-research.
2. **Stabilise residual BUBR1:** SIRT2/K668/NAD+ is mechanistic. NMN/NR are supplements, not leading nominations. +58%/+123% lifespan = SIRT2-tg, not NMN.
3. **Approved proteostasis / autophagy:** Ravicti; arimoclomol (FDA Miplyffa + miglustat; EMA Meplyffa refused 23 Jul 2026); metformin / rilmenidine.
4. **Gated / anti-target:** JAK/IL-6, Nrf2, systemic antioxidants, HSP — biomarker + oncology surveillance. Sirolimus: one FDR reverse in GSE22206 (`adj_pvalue_down = 9.14e-05`) but MIXED mimic elsewhere **and** aneugenic (Bonatti 1998) — not a rescue lead. ChEMBL must query **FKBP1A (P62942)** for rapalogs.

LINCS firewall: ACCEPT 0 / WEAK 2 (sirolimus, dasatinib) / REJECT rest. Absence of a LINCS hit is not evidence against the mechanism-first stack.

## Forbidden claims

- N1002K “is” L1012P
- Graph/AI discovered the therapy; TxGNN trained
- NAC rescued fly brain size (Sod2/GTPx-1 did)
- Ataluren is FDA/EMA-approved
- AVI or AlphaMissense is a clinical diagnosis
- Phasing is proven *in trans*
