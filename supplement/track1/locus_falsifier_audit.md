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
(PMID 24344301) to cause MVA when homozygous (and linked to the Matsuura 2006 "6G3"
haplotype): **no rare heterozygous or homozygous call exists in the proband** in the
corresponding window. All calls in the upstream region are common rsID SNPs
(e.g. rs1471584, rs12909145, rs11630670) or reference-bias homozygotes.

## 4. The intervening SNV 15:40,216,470 A>G — reclassified

- VEP: **BUB1B intron 20/22 intron_variant (MODIFIER)** — it is *intronic*, not
  "intergenic" as an earlier draft of the phasing memo stated.
- Absent from gnomAD v4 (exomes and genomes), dbSNP, and ClinVar — a **rare**
  variant, not a common SNP.
- SpliceAI max delta score 0.00; nearest splice junctions ≥884 bp away — no
  predicted splice effect.
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

## Conclusion

`p.Leu737Ter` + `p.Asn1002Lys` is the **unique best-supported compound-heterozygous
pair among all variants detectable by this short-read SNV/indel pipeline** — there
is no third coding, splice, or known-regulatory candidate, and no CNV, SV, UPD, or
homozygous alternative. The residual, explicitly disclosed, limitation is a **truly
novel cryptic mechanism invisible to SNV callers and ≤200-bp CNV resolution**
(e.g. a small intronic Alu/SVA insertion that produces no heterozygous SNP, or a
deep-intronic pseudoexon). Definitive exclusion of that class requires long-read
sequencing and/or RNA-seq, which is why the submission retains the "presumed
compound heterozygous" qualifier and the phasing-validation plan.
