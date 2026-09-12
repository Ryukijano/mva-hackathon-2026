# BUB1B locus falsifier audit — could the true second allele have been missed?

**Date:** Sept 2026. **Question:** does the proband carry any *other* candidate allele
(coding, splice, regulatory, structural, or homozygous) that could be the true second
hit, making `p.Asn1002Lys` a passenger? All checks were run directly on the gated
proband WGS VCF/BAM (not committed).

## Method

Every check below was executed against the proband's realigned BAM
(`data/bam/WGS_EX2312012_HGWCNDSX7.bam`) and the raw VCF
(`data/WGS_EX2312012_HGWCNDSX7.vcf.gz`) on GRCh38.

## 1. Complete BUB1B heterozygous inventory (chr15:40,161,000–40,221,140)

Only **8 heterozygous variants** exist in the entire BUB1B gene span:

| GRCh38 pos | change | consequence | gnomAD v4 | interpretation |
|---|---|---|---|---|
| 40,168,264 | G>A | intron 2/22 | genome AF 1.6% (rs28570325) | common, benign |
| 40,180,642 | CT>C | intron 5/22 | genome AF 22% (rs71132149) | common indel |
| 40,181,093 | AT>A | intron 5/22 | genome AF 65% (rs372589327) | common indel |
| 40,182,809 | A>C | intron 5/22 | genome AF 1.9% (rs28620590) | common |
| 40,192,892 | C>T | intron 8/22 | genome AF 0.21% (rs185599777) | uncommon |
| 40,209,701 | T>G | **p.Leu737Ter** | ~7.9e-5 | **target allele 1** |
| 40,216,470 | A>G | intron 20/22 | **absent from gnomAD v4** | rare deep-intronic, see §4 |
| 40,220,612 | T>G | **p.Asn1002Lys** | 1 exome allele | **target allele 2** |

## 2. Known pathogenic BUB1B alleles — none present

All ~100 ClinVar Pathogenic/Likely-pathogenic BUB1B variants were mapped to GRCh38
and cross-checked against the proband's calls. The proband carries **none** of the
established MVA1 alleles other than the submitted pair — including every known
deep-intronic splice allele:

- c.36-1G>A, c.239+2T>C, c.581+1G>T, c.751+1G>T, c.967-2A>T, c.2009+1G>A,
  c.2285-2A>G, c.2386-2A>G, c.2535+195C>A, c.2851-1G>C — **all absent**.
- The Rio Frio 2010 deep-intronic region (c.2386-11 / c.2386-16) — **absent**.
- All truncating alleles (c.2210del, c.2363_2364del, c.2436_2439dup, etc.) — **absent**.

## 3. Known upstream regulatory variant — absent

The ~44 kb upstream intergenic G>A regulatory variant shown by Ochiai et al. 2014
(PMID 24344301) to cause MVA when homozygous (ss802470619 / rs576524605;
c.-44133G>A; **GRCh38 chr15:40,117,088 G>A**): the proband VCF has **no call** at
that position and direct `samtools depth` at chr15:40,117,080–095 shows uniform
**~45–46x coverage** — i.e., the position is homozygous-reference, not a coverage
gap. The variant is definitively absent.

## 4. The intervening SNV 15:40,216,470 A>G — reclassified

- VEP (live re-query): **BUB1B intron_variant (MODIFIER)** on every protein-coding
  transcript — it is *intronic*, not "intergenic" as an earlier memo draft stated.
- **Absent from gnomAD v4 (exomes and genomes), dbSNP (no rsID exists for
  15-40216470-A-G), and ClinVar** — a private/ultra-rare variant, not a common SNP.
- SpliceAI max delta score 0.00; nearest splice junctions ≥884 bp away; phyloP100way
  **−0.41** (unconserved, slightly accelerated) — no functional signal.
- It is a legitimate candidate only as a **phasing bridge** (its two sub-gaps are
  6.77 kb and 4.14 kb, both exceeding the ~1.3 kb max insert size). As a *causal*
  second allele it is not supported by any functional evidence — but it is disclosed
  here as the one rare non-coding variant in the locus.

## 5. Structural / copy-number / UPD checks — all clean

- **Depth:** uniform ~46× across BUB1B (chr15:40,160,000–40,222,000); no 500-bp
  window deviates below 23× or above 69× → no exon-scale or larger CNV.
- **SVs:** zero symbolic alleles (SVTYPE/<DEL>/<DUP>/<INS>/<INV>/BND) in the VCF
  over the locus.
- **Clipped-read breakpoints:** soft-clip clusters are few, shallow (≤15 reads at
  46×), and **sequence-heterogeneous** (no concordant clipped stack) → no
  Alu/SVA-type insertion breakpoint.
- **UPD/isodisomy:** chr15 carries 85,227 het calls; het density is normal in every
  1-Mb bin around BUB1B (511 hets in the 40-Mb bin) → no segmental isodisomy.
- **Homozygous cause:** only 6 hom calls inside BUB1B, all common (genome AF
  0.32–0.999) reference-bias homozygotes → no hidden homozygous allele.

## 5b. Panel-completeness check — SLF2 and SMC5 (added post-audit)

A literature audit found the original 15-gene panel **missed two established
MVA-like disease genes**: SLF2 (MVA5 / Atelis-1, OMIM #620184) and SMC5 (MVA6 /
Atelis-2, OMIM #620185; Grange et al. 2022). Post-hoc check on the proband VCF:

- SLF2 (chr10:100,912,963–100,965,134): 65 variants — the only missense call is
  the common polymorphism 10:100,924,623 C>A (gnomAD AF 0.48). **No rare
  coding/splice variant.**
- SMC5 (chr9:70,258,270–70,354,874): 88 variants — the only missense call is
  9:70,282,518 G>A (gnomAD AF 0.88, i.e. homozygous for the common allele).
  **No rare coding/splice variant.**

Panel extended to 17 genes (`configs/panel.yaml`, `atelis` group) for future runs.
The exclusion is post-hoc, not from the ranked pipeline — disclosed honestly.

## 6. External database verification of the submitted pair (live re-query)

- **L737Ter** (chr15:40,209,701 T>G): ClinVar VCV000533901 = NM_001211.6:c.2210T>G,
  Pathogenic/Likely pathogenic, multiple submitters no conflicts, last eval
  2024-10-09. gnomAD v4: AC=115 exomes (AF 7.87e-5), 0 homozygotes, rs759242053.
  VEP/Loftee: `stop_gained`, **high-confidence LoF, 50_BP_RULE:PASS,
  DIST_FROM_LAST_EXON:742** → canonical NMD substrate. phyloP100way 2.91.
- **N1002K** (chr15:40,220,612 T>G): ClinVar has the same *protein* change via
  c.3006T>A (VCV004600147, VUS single submitter, 2025-09-19); our c.3006T>G
  allele is ClinVar-absent. gnomAD v4: AC=1 exome (AF 6.8e-7), rs2542593804.
  VEP: missense N/K, SIFT deleterious (0.01), PolyPhen probably_damaging (0.997),
  AlphaMissense likely_pathogenic 0.9229. phyloP100way **4.80** — a strongly
  constrained site. Structural: ordered C-lobe of the pseudokinase domain
  (945–1040), 10 residues N-terminal of the known MVA1 allele L1012P; not in the
  catalytic site but plausibly destabilizing to the C-lobe surface.
  *Checked-and-noted:* the neighboring p.Asn1004Ser (rs34998711, 2 residues away)
  carries a legacy ClinVar MVA1 association but is now classified
  **Benign/Likely benign** (multi-submitter, Mar 2026; 3 gnomAD homozygotes) —
  so the "disease neighbourhood" argument rests on L1012P, not N1004S.
- **NMD evidence for BUB1B PTCs (literature):** patient BUB1B nonsense alleles
  386X, 731X, 1833delT and the deep-intronic c.2386-11A>G all show absent/reduced
  transcript by NMD (Suijkerbuijk 2010; Matsuura 2006; Rio Frio 2010) — supports
  the NMD-gated readthrough strategy in Track 2.

## Conclusion

`p.Leu737Ter` + `p.Asn1002Lys` is the **unique best-supported compound-heterozygous
pair among all variants detectable by this short-read SNV/indel pipeline** — there
is no third coding, splice, or known-regulatory candidate, no CNV, SV, UPD, or
homozygous alternative, and no causal allele in the post-hoc-checked SLF2/SMC5
Atelis genes. The residual, explicitly disclosed, limitation is a **truly novel
cryptic mechanism invisible to SNV callers and ≤200-bp CNV resolution** (e.g. a
small intronic Alu/SVA insertion that produces no heterozygous SNP, or a
deep-intronic pseudoexon). Definitive exclusion of that class requires long-read
sequencing and/or RNA-seq, which is why the submission retains the "presumed
compound heterozygous" qualifier and the phasing-validation plan.
