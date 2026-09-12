# X / Twitter drafts — MVA Hackathon 2026

## Option A: single post (~280 chars)

> A child's cells can't count chromosomes. 5M variants in one genome → 2 broken BUB1B alleles. Then we spent the real effort trying to prove ourselves wrong — and caught a gap in our own gene panel instead. Falsification-first rare-disease genomics. #RareDisease #Genomics

*(attach: apcc_mcc_rotate.gif)*

## Option B: thread (6 posts)

**1/**
A child whose cells can't count chromosomes.

5 million variants in their genome. Somewhere in there: two broken letters explaining a rare disease — mosaic variegated aneuploidy — and the childhood cancers that come with it.

Here's how we found them, and how we tried to prove ourselves wrong. 🧵

**2/**
Of 5M variants, exactly one gene carried two rare functional hits: BUB1B.

Allele 1 → a stop codon at residue 737. Already ClinVar-pathogenic.
Allele 2 → a missense at 1002. Essentially unique (1 allele in gnomAD), at one of the most constrained sites in the vertebrate genome (phyloP 4.8).

**3/**
The structure tells the story. The stop-gain deletes BUBR1's entire pseudokinase domain — the scaffold the spindle checkpoint hangs on. The missense sits 10 residues from a proven disease allele in the same folded lobe.

*(attach: bubr1_trunc_rotate.gif or apcc_mcc_highlight.png)*

**4/**
Then we tried to kill our own answer:

• every other ClinVar-pathogenic BUB1B allele — absent
• the known upstream regulatory variant — homozygous-ref at 46× depth
• CNVs / SVs / UPD — none
• our own gene panel — missing SLF2 + SMC5 (Atelis genes). We caught it, checked the VCF, both clean

The call survived because it was the only thing left standing.

**5/**
Therapy has a hard gate: the stop codon sits in the NMD zone — the transcript is degraded before it can even make broken protein.

So readthrough alone may have nothing to work on. The mechanistically-matched lead is amlexanox (NMD inhibition + readthrough in one drug) — a novel application for MVA.

*(attach: mechanism_schematic.png)*

**6/**
Honest limits: phasing is inferred, not proven. N1002K is a VUS. Short reads can't exclude cryptic structural variants. Repo documents all of it — falsifier audit, a clean LINCS negative (0 rescues / 674 rejections), 39 tests.

To our knowledge: the first mechanism-gated repurposing dossier for MVA.

*(attach: link to repo/blog)*

## Novelty claims — verified safe to make

| Claim | Status |
|---|---|
| First drug-repurposing dossier for MVA | Verified — no prior paper; literature is supportive care only |
| Amlexanox for BUB1B PTC | Novel application (mechanism known in other diseases — Gonzalez-Hilarion 2012) |
| Sirolimus as anti-target warning | Novel warning (mechanism known — Bonatti 1998); caveat: González-Blanco 2025 fly model found *genetic* TOR depletion protective |
| N1002K as MVA1 allele | Novel variant — unpublished, ClinVar VUS only for generic "inborn genetic diseases" |
| Proteostasis/autophagy rescue concept | NOT novel — cite González-Blanco 2025/26 (Drosophila MVA model); our drug list is novel |

## Don't claim

- Phasing proven (it's inferred)
- N1002K pathogenic (VUS)
- "AI discovered the therapy" (mechanism-first reasoning + ChEMBL screen)
- Any patient data / identifying details
