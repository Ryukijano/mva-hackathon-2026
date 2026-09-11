# ClinVar verification — 2026-09-10

## Method

Both ClinVar variation IDs cited in the Track 1 report were verified directly
against the NCBI ClinVar E-utilities API (`esummary.fcgi`).

## VCV000533901 — p.Leu737Ter (allele 1)

- **Accession:** VCV000533901.9
- **Title:** NM_001211.6(BUB1B):c.2210T>G (p.Leu737Ter)
- **GRCh38:** chr15:40209701 T>G
- **Classification:** Pathogenic/Likely pathogenic
- **Last evaluated:** 2024/10/09
- **Review status:** criteria provided, multiple submitters, no conflicts
- **Submitters:** SCV000762865, SCV004031025
- **RCVs:** RCV000641226, RCV003324778
- **Trait:** Mosaic variegated aneuploidy syndrome 1 (MedGen C3661900; OMIM 257300)
- **Molecular consequence:** nonsense
- **Protein change:** L737*
- **dbSNP:** rs759242053
- **ClinGen:** CA7475986

**Status:** Confirmed. The Track 1 report's citation of VCV000533901 is accurate.

## VCV004600147 — p.Asn1002Lys (allele 2, protein change)

- **Accession:** VCV004600147.1
- **Title:** NM_001211.6(BUB1B):c.3006T>A (p.Asn1002Lys)
- **GRCh38:** chr15:40220612 T>A
- **Classification:** Uncertain significance
- **Last evaluated:** 2025/09/19
- **Review status:** criteria provided, single submitter
- **Submitter:** SCV007198955
- **RCV:** RCV006331804
- **Trait:** Inborn genetic diseases (MedGen C0950123; MeSH D030342) — generic, NOT MVA1-specific
- **Molecular consequence:** missense variant, intron variant
- **Protein change:** N1002K

**Corrections applied:**
1. The accession was previously written as "VCV4600147" (missing leading zeros).
   Corrected to "VCV004600147.1" throughout the repository.
2. The last-evaluated date was previously written as "Jan 2026" or "11 Jan 2026".
   The API returns "2025/09/19" (19 September 2025). Corrected throughout.
3. The trait was not previously specified. It is "Inborn genetic diseases"
   (a generic trait), not MVA1-specific. This is now stated explicitly.
4. The submitter SCV ID was not previously cited. Added: SCV007198955.

**Our exact allele (c.3006T>G) is absent from ClinVar.** The ClinVar record
is for the alternative nucleotide change c.3006T>A, which produces the same
protein change (N1002K) at the same genomic coordinate (chr15:40220612).
A search of the ClinVar database for BUB1B c.3006T>G or for variants at
chr15:40220612 with the T>G allele returned no records.

## Files updated

- `submissions/Ryukijano_track1_report.md` — 4 references corrected
- `README.md` — 1 reference corrected
- `WHAT_WE_DID.md` — 1 reference corrected
- `docs/track1_first_principles.md` — 4 references corrected
- `docs/next_plan.md` — 1 reference corrected
- `experiments/2026-08-31_bub1b_computational/SUMMARY.md` — 1 reference corrected
- `experiments/2026-08-31_bub1b_computational/outputs/RESULTS.md` — 1 reference corrected

The raw ClinVar export at
`experiments/2026-08-31_bub1b_computational/outputs/e1c_clinvar/clinvar_bub1b_canonical_missense.csv`
uses the numeric ID "4600147" (without the VCV prefix) and is left unchanged
as it is a raw data export.
