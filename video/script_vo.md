# Track 2 pitch — voice-over script (v3, 2026-10-09)

Status: **v3 — revised after the 2026-10-09 review.** Changes from v2: S4 is back to six spoken lines so each on-screen element fires on its line (v2 had five, which shifted the animations); amlexanox and sirolimus wording now matches the sources (in vitro ranges, a single-donor caveat); arimoclomol is a negative EMA opinion, not a refusal; L1012P is labelled a comparator with no literature claim; the repository link is removed from the closing card. Budget: total runtime ≤180 s, checked by measured WAV duration (`video/timing.json`), not word count.

Each scene has a `Display:` note (the canonical on-screen wording; `video/render/scenes.py` implements it) and a fenced `spoken` block (fed verbatim to Kokoro TTS — respellings are deliberate). `video/tts.py` parses the fenced `spoken` blocks; edit those to change the VO. `video/qa.py` scans on-screen text, spoken text and `timing.json`.

Must-keep claims: two-variant call (protein level only) · NMD-first reasoning (readthrough needs a transcript) · amlexanox as the mechanistically matched approved option, reported in vitro only · proteostasis tier order with caveats · transcriptomic firewall reported as a negative result · sirolimus as a potential anti-target · disclaimer.

## S0 — Title (no VO)

```spoken
```

## S1 — The case

Display: embryonal rhabdomyosarcoma · growth restriction · microcephaly; *BUB1B* p.Leu737Ter (ClinVar P/LP, MVA1) + p.Asn1002Lys (ultra-rare C-lobe missense; AlphaMissense 0.9229; ESM-1v LLR −0.110, in-house); presumed compound heterozygous (phase unresolved); Track 1 full match.

```spoken
A child with embryonal rhabdomyosarcoma, growth restriction, and microcephaly.
Genome sequencing points to two ultra-rare variants in bub-one-B, encoding the checkpoint protein bub-R-one.
One is a stop-gain, leucine seven-thirty-seven stop, ClinVar P-L-P for mosaic variegated aneuploidy.
The other is a C-lobe missense, asparagine ten-oh-two lysine.
One truncating allele plus one missense: the published MVA pattern, presumed compound heterozygous. Our Track One submission scored a full match.
```

## S2 — Mechanism

Display: kinetochore → MCC holds APC/C → weak BUBR1 → premature anaphase → mosaic aneuploidy → proteotoxic/lysosomal stress, micronuclei → cGAS–STING → IFN / IL-6 (can support aneuploid-cell survival).

```spoken
Bub-R-one holds the mitotic checkpoint together, keeping the anaphase trigger, A-P-C-C, silent until every chromosome is attached.
With one allele truncated and one weakened, anaphase starts early; chromosomes mis-segregate into a mosaic of aneuploid cells.
Aneuploid cells carry protein-folding and lysosomal stress, and micronuclei that can activate see-gas sting.
Interferon and I-L-six signalling can then help those cells survive.
Our strategy: restore functional bub-R-one first, then buffer the damage.
```

## S3 — The stack

Display: (1) UGA rescue — **amlexanox** (FDA: 5% topical paste only; NMD inhibition + readthrough, in vitro, patient cells, 0.2–100 µM; systemic dosing not established); ataluren (US NDA resubmission withdrawn 12 Feb 2026). (2) SIRT2 / NAD⁺ — NMN, NR = supplement comparators (NMN lawful as a supplement, FDA, 29 Sep 2025). (3) Approved proteostasis — Ravicti (FDA/EMA, urea-cycle; 4-PBA prodrug, extrapolated) → arimoclomol (FDA with miglustat, NPC; EMA negative opinion Jul 2026, re-examination requested) → metformin / rilmenidine (approved; autophagy rationale, no MVA data). (4) Potential anti-target — sirolimus (in vitro chromosome mis-segregation; anti-target status unproven).

```spoken
Our stack is upstream-first.
Prong one, the stop allele: its transcript is predicted to be degraded by nonsense-mediated decay, so readthrough has nothing to read.
So we lead with am-lexanox: reported to block decay and promote readthrough in patient cells, in vitro only.
It's approved only as a topical paste.
Ataluren can't rescue a transcript that's gone; its U-S resubmission was withdrawn in February.
Prong two: stabilise bub-R-one through sirtuin two; N-M-N and N-R are supplements, comparators only.
Downstream: Ravicti, arimoclomol (EMA recommended refusal, July), then metformin or rilmenidine, which lack MVA data. Sirolimus is a potential anti-target: rapamycin causes mis-segregation in cell studies.
```

## S4 — Evidence

Display: `track2/drug_screen.py --approved-only` → ChEMBL 92 → 32 approved rows (eligible matches, not leads) · reverse-signature firewall (L2S2 + L1000CDS2; reverse FDR < 0.05) over 676 drugs; single-donor reference (GSE22206) + BubR1-mouse signatures: ACCEPT 0 / WEAK 2 (sirolimus, dasatinib) / REJECT 674 · amlexanox: no significant reverse signal (readthrough and NMD cannot be tested) · sirolimus: 1 reverse vs 4 mimic signatures, 3 from one donor · ESM-1v LLR N1002K −0.110 vs L1012P −1.801 (in-house, unverified) · no registered MVA/BUB1B trials (ClinicalTrials.gov).

```spoken
Our transcriptomic firewall rejected nearly everything.
A target-first chembl screen found ninety-two rows, thirty-two approved: eligible matches, not leads.
The reverse-signature screen covered six hundred seventy-six drugs and tests only transcriptomic reversal, so it cannot detect readthrough or NMD, amlexanox's mechanism.
Zero accepted, two weak, six hundred seventy-four rejected.
Sirolimus reversed one signature and mimicked four, three from one donor's dataset. We treat it as a potential anti-target.
A protein language model scores our missense far milder than the L ten-twelve P comparator: no assumed equivalence.
```

## S5 — Close

Display: assay-gated flowchart · disclaimer · CC BY 4.0 · drug-status facts checked 9 Oct 2026 · narration: synthetic voice (Kokoro-82M, local). No repository link is shown.

```spoken
Next steps, assay-gated: restore full-length bub-R-one, stabilise what remains, measure aggregate load, with oncology surveillance throughout.
This is a preclinical N-of-one research proposal, not clinical advice or a treatment recommendation.
```
