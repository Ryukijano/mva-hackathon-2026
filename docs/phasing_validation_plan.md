# BUB1B phasing validation plan — molecular confirmation strategy

Date: 2026-09-10. Companion to `results/wgs_phasing/phasing_report.md` and
`results/wgs_phasing/decision_memo.md`.

## 1. Problem statement

The two candidate causal *BUB1B* variants are 10,911 bp apart on chr15:

| Variant | GRCh38 | HGVS | Status |
|---|---|---|---|
| p.Leu737Ter | `15:40209701 T>G` | `c.2210T>G` | ClinVar Pathogenic/LP (VCV000533901) |
| p.Asn1002Lys | `15:40220612 T>G` | `c.3006T>G` | Novel; ClinVar VUS for same protein via c.3006T>A |

WhatsHap read-backed phasing returned **UNRESOLVED** because:

- Maximum observed fragment length (TLEN) ≈ 1,348 bp.
- No read pair spans >9 kb on chr15.
- Only one intervening heterozygous SNV (15:40216470 A>G) exists between the
  targets, but both gaps (6.77 kb and 4.14 kb) exceed the fragment length.
- The original WhatsHap input excluded non-SNV variants (TYPE="snp" filter),
  omitting a heterozygous STR/indel near 15:40216547; however, even with that
  variant included, both remaining gaps still exceed the insert size.

**Trans configuration is strongly favored** by the autosomal-recessive MVA1
phenotype, the canonical nonsense + hypomorphic missense architecture (Hanks
et al. 2004), the absence of a third *BUB1B* coding/splice candidate in the
scanned region, and the exclusion of obvious *CEP57*/*TRIP13* candidates.
However, **phase has not been molecularly confirmed**.

## 2. Why statistical phasing is not definitive here

SHAPEIT5 `phase_rare` (Hofmeister et al. 2023, *Nat Genet*) is a powerful
tool for phasing rare variants in **large cohorts** (>2,000 samples
recommended per official documentation). It is not a gold-standard
solution for a single proband for the following reasons:

1. **Cohort design:** `phase_rare` phases rare alleles by finding
   conditioning haplotypes from other carriers in the target dataset. In a
   one-sample input, there are no other carriers.
2. **Singleton behaviour:** p.Asn1002Lys has AC=1 in gnomAD v4 exomes
   (AF ≈ 6.8e-07) and is absent from gnomAD genomes. In the documented UK
   Biobank workflow, singletons receive PP=0.5 (uninformative).
3. **No `--reference` in `phase_rare`:** The external panel feeds
   `phase_common` (which supports `--reference`), not `phase_rare`. The
   panel improves the common-variant scaffold but does not provide rare-
   allele carriers for the HMM conditioning step.
4. **PP is per-site, not pairwise P(trans):** Combining two per-site
   confidence scores into a pairwise phase probability requires accounting
   for scaffold switch errors, ancestry match, and dependence between
   assignments — this is not a validated output of the tool.
5. **Ancestry mismatch risk:** If the proband's ancestry is not well
   represented in 1000G/HGDP, the common-scaffold haplotype estimates may
   be less accurate, compounding rare-variant uncertainty.

Statistical phasing may be attempted as an **exploratory sensitivity
analysis** but must not be described as definitive confirmation.

## 3. Molecular phasing options (in priority order)

### 3.1 Parental genotyping (strongest, simplest)

If both parents are available and consent:

1. Genotype `15:40209701 T>G` and `15:40220612 T>G` in both parents
   (Sanger or targeted NGS).
2. If one variant is inherited from each parent → **trans confirmed**.
3. If both variants are inherited from the same parent → **cis confirmed**
   (would require searching for a second hit elsewhere).

**Advantages:** Gold standard; unambiguous; low cost.
**Limitations:** Requires parental availability and consent.

### 3.2 Targeted long-range PCR + Sanger/NGS sequencing

Amplify a single ~11.1 kb fragment containing both variant sites, then
determine phase by sequencing the amplicon.

#### Primer design (in silico, primer3-py v2.3.1)

| Primer | Sequence (5'→3') | Tm | GC% | Len | Position (GRCh38) |
|---|---|---|---|---|---|
| **BUB1B-LR-F** | `CCTACTCAGTCACCATGGTGTTCAC` | 63.0°C | 52% | 25 | chr15:40209640–40209664 |
| **BUB1B-LR-R** | `GCAAAGCCCCAGGACTAGTTAACTT` | 63.0°C | 48% | 25 | 3'-end at chr15:40220748 |

**Amplicon:** ~11,109 bp (chr15:40209640–40220748)
- Spans p.Leu737Ter (chr15:40209701): **YES**
- Spans p.Asn1002Lys (chr15:40220612): **YES**
- Spans intervening het SNV (chr15:40216470): **YES** (additional phasing marker)

#### Protocol outline

1. **Long-range PCR** using a high-processivity polymerase:
   - TaKaRa LA Taq (up to 30 kb), Q5 High-Fidelity (NEB), or KAPA HiFi.
   - Extension time: ~6–7 min at 68°C (1 kb/min for LA Taq).
   - Annealing: ~60°C (Tm-matched primers).
2. **Amplicon verification:** Run on a pulse-field gel or Agilent TapeStation
   to confirm a single ~11.1 kb band.
3. **Phase determination options:**
   - **Sanger sequencing** of the amplicon with internal primers targeting
     each variant site. If both variants appear in a single sequencing read
     (or in overlapping reads from the same amplicon molecule), phase is
     resolved. However, Sanger reads are typically <1 kb, so this requires
     allele-specific strategy (see below).
   - **Oxford Nanopore amplicon sequencing:** Sequence the full 11.1 kb
     amplicon on a MinION. Each read is a single molecule spanning both
     variants → direct haplotype assignment. This is the preferred approach.
   - **PacBio HiFi amplicon sequencing:** Similar to ONT but with higher
     per-read accuracy. Also suitable.
   - **Allele-specific PCR:** Design a forward primer with the 3'-end
     matching one allele at site 1, paired with a reverse primer at site 2.
     A product only forms if both alleles are in cis. This is a simpler but
     less information-rich approach.

#### Expected outcomes

| Result | Interpretation |
|---|---|
| Both variants on the same amplicon molecule (same read) | **Cis** — would require searching for a trans second hit |
| Variants on different amplicon molecules (different reads) | **Trans** — compound heterozygosity confirmed |
| Only one allele amplifies | Allele dropout; repeat with adjusted conditions |

**Advantages:** Does not require parental samples; direct molecular proof;
amplicon can also capture the intervening het SNV for triple-marker phasing.
**Limitations:** Requires wet-lab access; 11 kb amplicon may be difficult in
GC-rich or repetitive regions; allele dropout possible.

### 3.3 Targeted long-read WGS (Cas9 enrichment / adaptive sampling)

If whole-genome long-read sequencing is not available, targeted enrichment
of the BUB1B locus via:

- **Cas9-mediated enrichment** (e.g., ONT Cas9 Sequencing Kit):
  Design guide RNAs flanking the 10.9 kb region; enrich and sequence on
  MinION/PromethION.
- **ONT adaptive sampling:** Software-based targeting on a MinION flow
  cell; no wet-lab enrichment needed.

**Advantages:** Native DNA (no PCR bias); can capture structural variants;
long reads easily span 10.9 kb.
**Limitations:** Higher cost than amplicon; requires ONT platform access.

### 3.4 Linked-read or Hi-C phasing (if existing data available)

If linked-read (10x Genomics) or Hi-C data exist for the proband, these
can phase variants over much longer distances than standard paired-end
reads. Not available in the current dataset.

## 4. What the report should say now

Until molecular or parental phasing is performed:

> The two *BUB1B* variants are **presumed compound heterozygous** based on
> the autosomal-recessive MVA1 phenotype, the canonical
> truncating + hypomorphic missense architecture (Hanks et al. 2004), the
> absence of a third *BUB1B* coding/splice candidate in the scanned region,
> and the exclusion of obvious *CEP57*/*TRIP13* alternatives. Direct
> short-read phasing is unresolved because the 10,911 bp interval exceeds
> the library's maximum observed fragment length (~1,348 bp), and no chain
> of read-connected heterozygous sites bridges the gap. Population-based
> statistical phasing (SHAPEIT5) is unlikely to be informative for the
> effectively singleton p.Asn1002Lys allele and would not constitute
> definitive confirmation. **Parental genotyping or targeted long-range
> PCR followed by long-read sequencing is recommended for definitive phase
> confirmation.**

## 5. Reproducibility

Primer design script: `scripts/design_lrpcr_primers.py` (uses primer3-py).
Reference genome: `refs/Homo_sapiens.GRCh38.dna.primary_assembly.fa`.
Primer design inputs: 700 bp upstream and 588 bp downstream flanking sequences
extracted via `samtools faidx`.

## 6. References

1. Hofmeister RJ, et al. Accurate rare variant phasing of whole-genome and
   whole-exome sequencing data in the UK Biobank. *Nat Genet* 55:1243–1249
   (2023). doi:10.1038/s41588-023-01415-w.
2. Hanks S, et al. Constitutional mosaic aneuploidy syndrome. *Nat Genet*
   36:1159–1161 (2004). PMID 15475955.
3. SHAPEIT5 official documentation: https://odelaneau.github.io/shapeit/
4. Guo MH, et al. Inferring compound heterozygosity from large-scale exome
   sequencing data. *Nat Genet* 56:152–161 (2024). doi:10.1038/s41588-023-01608-3.
