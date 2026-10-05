# Track 2 pitch — voice-over script (draft v1, 2026-10-05)

Status: **DRAFT — awaiting user sign-off.** Budget: total runtime ≤180 s,
checked by measured WAV duration (`video/timing.json`), not word count.

Each scene has a `spoken` block (fed verbatim to Kokoro TTS — respellings are
deliberate) and a `display` note (the canonical written form used on screen).
`video/tts.py` parses the fenced `spoken` blocks; edit those to change the VO.
The QA coordinate scan runs over both.

Must-keep claims (PLAN.md): two-variant call · NMD gate → amlexanox over
ataluren · proteostasis tier order · LINCS 0/2/674 · sirolimus anti-target ·
disclaimer.

## S0 — Title (no VO)

```spoken
```

## S1 — The case

Display: embryonal rhabdomyosarcoma · growth restriction · microcephaly;
*BUB1B* p.Leu737Ter (ClinVar P/LP, MVA1) + p.Asn1002Lys (ultra-rare C-lobe
missense; AlphaMissense 0.9229; ESM-1v LLR −0.110); Track 1 full match.

```spoken
A child with embryonal rhabdomyosarcoma, growth restriction, and microcephaly.
Genome sequencing points to two ultra-rare variants in bub-one-B, which encodes the checkpoint protein bub-R-one.
One is a stop-gain, leucine seven-thirty-seven stop, ClinVar pathogenic for mosaic variegated aneuploidy.
The other is a missense in the C-terminal lobe, asparagine ten-oh-two lysine.
One null allele plus one hypomorph: the classic viable architecture. Our Track One call on this pair scored a full match.
```

## S2 — Mechanism

Display: kinetochore → MCC holds APC/C → weak BUBR1 → premature anaphase →
mosaic aneuploidy → proteotoxic/lysosomal stress, ROS, micronuclei →
cGAS–STING → IFN / IL-6.

```spoken
Bub-R-one is the core of the mitotic checkpoint complex. It holds the anaphase trigger, A-P-C-C, until every chromosome is attached.
With one allele truncated and the other weakened, the checkpoint lets go too early.
Chromosomes mis-segregate, leaving a mosaic of aneuploid cells.
Those cells carry protein-folding and lysosomal stress, reactive oxygen, and fragile micronuclei. When micronuclei rupture, see-gas sting fires, driving interferon and I-L-six.
So we aim upstream: raise functional bub-R-one first, then buffer the damage.
```

## S3 — The stack

Display: (1) UGA rescue — **amlexanox** (FDA: topical paste only; NMD
inhibition + readthrough); ataluren (UK/MHRA conditional only · FDA NDA
withdrawn · EMA not renewed; no NMD activity); ELX-02 (investigational).
(2) SIRT2 / NAD⁺ — NMN, NR = supplement comparators. (3) Approved
proteostasis — Ravicti (FDA/EMA, urea-cycle) → arimoclomol (FDA with
miglustat, NPC; EMA refused) → metformin (FDA/EMA) / rilmenidine (UK/EU, not
FDA). (4) Anti-target — sirolimus (aneugen; Bonatti 1998).

```spoken
Our stack is upstream-first.
Prong one: the stop allele. Its transcript is almost certainly destroyed by nonsense-mediated decay, so a readthrough drug alone has nothing to read.
That is why we lead with am-lexanox, which blocks the decay and promotes readthrough. It's approved only as a topical paste, so systemic use needs reformulation and patient-cell proof.
Ataluren has no decay activity and is not F-D-A or E-M-A approved.
Prong two: stabilise bub-R-one through sirtuin two and en-ay-dee. N-M-N and N-R are supplements: comparators only.
Downstream, approved proteostasis drugs: Ravicti, then arimoclomol, then metformin or rilmenidine.
And one anti-target: sirolimus. Rapamycin itself causes chromosome mis-segregation.
```

## S4 — Evidence

Display: `track2/drug_screen.py --approved-only` → ChEMBL 92 → 32 rows
(+FKBP1A for rapalogs) · LINCS reverse-FDR firewall over human MVA + BubR1-hypomorph mouse contrasts ACCEPT 0 / WEAK 2 /
REJECT 674 · ESM-1v LLR N1002K −0.110 vs L1012P −1.801.

```spoken
Every lead went through a firewall.
A target-first chembl screen returned ninety-two drug-target rows. Keeping approved drugs leaves thirty-two: eligible matches, not leads.
A LINCS connectivity screen against human and mouse disease signatures, gated on reverse false-discovery rate:
Zero accepted. Two weak. Six hundred seventy-four rejected.
Sirolimus reversed one signature, but mimicked the disease in four others, so it stays flagged as an anti-target.
And a protein language model scores our missense far milder than the classic L ten-twelve P allele, so we don't assume they're equivalent.
```

## S5 — Close

Display: assay-gated flowchart · disclaimer · repo URL · CC BY 4.0.

```spoken
Next steps are assay-gated: restore full-length bub-R-one, stabilise what remains, clear aggregates, with oncology surveillance throughout.
This is a preclinical N-of-one research proposal, not clinical advice or a treatment recommendation.
```
