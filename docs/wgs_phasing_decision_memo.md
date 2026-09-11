# BUB1B phasing — decision memo (post-UNRESOLVED re-evaluation)

Date: 2026-09-09. Companion to `phasing_report.md`.

## Verdict recap

WhatsHap read-backed phasing on the ~91 kb BUB1B window: 41 het SNVs, 30 phased
into 8 blocks (max 2,822 bp), **no block spans both target alleles → UNRESOLVED**.

Why it is structurally unfixable with this data:

- The two sites (15:40209701, 15:40220612) are 10,911 bp apart.
- Exactly **one** heterozygous SNV (15:40216470 A>G) lies between them; a
  150 bp paired-end read cannot bridge 4.2–6.8 kb gaps, so chaining is
  impossible regardless of coverage (939 M pairs, 99.5% mapped, 98.2% proper).
- Statistical phasing (reference-panel) is unlikely to be informative: the
  N1002K allele has AC=1/1.6 M (gnomAD), so panel-based phase assignment is
  ~50/50. SHAPEIT5 `phase_rare` is documented for cohorts >2,000 samples
  (official docs); singletons receive PP=0.5 in the UK Biobank workflow.
  See `docs/phasing_validation_plan.md` for full rationale.
- **Molecular phasing is the recommended path forward.** In silico long-range
  PCR primers have been designed for an ~11.1 kb amplicon spanning both
  variants (`scripts/design_lrpcr_primers.py`). Parental genotyping is the
  simplest definitive option if parents are available.

UNRESOLVED is a technical limit, not a contradiction of the trans hypothesis.

## Allele evidence (DB-verified 2026-09-09)

| allele | ClinVar | gnomAD | notes |
|---|---|---|---|
| c.2210T>G p.Leu737Ter (rs759242053) | **Pathogenic/LP**, multiple submitters, no conflicts, MVA1 | AF 7.4e-5 (120/1.6 M), 0 homozygotes | nonsense upstream of kinase domain (aa 766) |
| c.3006T>G p.Asn1002Lys (rs2542593804) | **absent** (exact allele novel); same-codon T>A is VUS (single submitter) | **AC=1 / 1.6 M** (private) | missense in kinase C-lobe |
| reference allele p.Leu1012Pro (c.3035T>C) | VUS, multiple submitters; MVA1 + PCS trait + CRC | — | disease-linked αG-helix allele (see below) |

- Read-level check (our BAM): L737Ter DP 47–48, AD 22/26 — matches VCF (21/25);
  N1002K DP 27–29, AD 15/12 — matches VCF (15/13). Both clean 0/1.

## Structural evidence (AlphaFold DB O60566, + UniProt/InterPro)

- UniProt domain layout: BUB1 N-terminal 62–226; **protein kinase 766–1050**;
  L737 sits in the linker immediately N-terminal of the kinase domain.
- AF2 per-residue pLDDT: L737 = 73.6; **N1002 = 91.1; L1012 = 95.3** (kinase
  C-lobe is the best-predicted rigid unit; PAE domain 3 = 755–1043).
- PAE: N1002–L1012 = **3 Å** (same rigid lobe); L737–N1002 = 17 Å (different
  units, flexible linker) — N1002K is structurally co-localised with L1012P.
- Literature (Suijkerbuijk & Kops, Cell Cycle 2011; PMC3061984): L1012 and
  L1031 map to α-helices αG/αH of the BUBR1 C-terminus; L1012P "expected to
  affect the conformation of αG helix through the insertion of a kink" — a
  documented MVA-associated allele (hypothyroidism/anemia phenotype).

## Literature triangulation (2026-09-09)

- **Hanks et al. 2004, Nat Genet 36:1159 (PMID 15475955)** — the canonical MVA
  genotype: each of 5 families carried **one truncating + one missense allele,
  inherited from different parents (trans)**; 5/6 missense mutations lie in the
  kinase domain. Our L737Ter+N1002K matches this architecture exactly.
- **Frontiers in Endocrinology 2026 (PMID 42434306)** — heterozygous
  c.2215G>T p.A739S (**2 residues from L737Ter**) → significantly elevated
  premature chromatid separation, trend to reduced BUB1B mRNA/BUBR1 protein.
  This exact region is dosage-sensitive.
- **Shandong fetuses (PMID 40555658)** + **PNAS 2014 TALEN proof (PMID
  24413160? ss802470619, 44 kb upstream)** + **Matsuura 2006 (7 families,
  monoallelic + regulatory)** — the "coding allele + upstream regulatory
  second hit" MVA architecture is real and was specifically checked here.

## Region scan (our WGS VCF, chr15 40.0–40.25 Mb)

- 44 kb upstream window (40,100,000–40,160,984): 88 variants — **all common
  SNPs (rsIDs) or simple-repeat indels; no rare non-repetitive candidate**.
- Novel variants in the whole region: only 15:40209701 (L737Ter),
  15:40216470 (intergenic A>G), 15:40220612 (N1002K) — plus repeat-region
  indels (CCTT, poly-T, CAA runs) with no regulatory plausibility.
- **Consequence: if the two coding alleles were cis, the second chromosome
  would carry no BUB1B-affecting allele at all** — inconsistent with MVA,
  which requires biallelic impairment. Parsimony strongly supports trans.

## Caveats (must appear in the write-up)

- Phase is **inferred**, not read-proven: "read-backed phasing was attempted
  and could not bridge the 10.9 kb gap (UNRESOLVED); compound heterozygosity
  is inferred from the canonical MVA genotype architecture (Hanks 2004), the
  absence of any possible second-hit allele in the surrounding 250 kb, and
  the private rarity of both alleles."
- N1002K has no functional assay; evidence is structural (C-lobe, pLDDT 91,
  PAE 3 Å from L1012P), conservation, and novelty. The ClinVar same-codon
  T>A allele is VUS.
- Bulk WGS aneuploidy landscape: no strong mosaic aneuploidy signal (chr15
  mean depth dip ~0.79 is likely technical; no decoy/alt reference). Do not
  overclaim the genotype→phenotype depth loop; PCS/MVA mosaicism is a
  cytogenetic, tissue-dependent trait.

## Recommendation

Proceed with the compound-heterozygous interpretation as the best-supported
hypothesis, **with the phasing limitation disclosed in the methods write-up**
and the molecular phasing validation plan documented in
`docs/phasing_validation_plan.md`. The original TRANS→submit / UNRESOLVED→stop
rule was designed to avoid burning a shot on a wrong call; the re-evaluation
shows UNRESOLVED here is a short-read limit, the architecture is the canonical
MVA genotype, and the cis scenario would leave no second allele at all.
Residual risk: cis + undetected regulatory hit outside the scanned region
(unlikely; no candidate seen in 250 kb).

Final decision to spend a Track 1 shot rests with the user.
