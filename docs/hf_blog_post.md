# One genome, two broken alleles: what it takes to diagnose a real kid

*How we went from 5 million variants to a single compound-heterozygous call in BUB1B — and why the interesting part is everything we had to rule out first.*

---

There is a child somewhere whose cells can't count chromosomes.

Every time one of their cells divides, there's a measurable chance a daughter cell gets the wrong number of chromosomes — too many, too few, scrambled. Over a childhood, that accumulated chaos produces a distinctive, brutal signature: a head that stopped growing on schedule, a brain development gone subtly wrong, and — the detail that gives the disease its menace — childhood cancers, fed by the same genomic instability that made them possible.

The condition has a name: **mosaic variegated aneuploidy**, MVA. It's vanishingly rare. And for the SageBio *Rare Disease, Real Kid* hackathon, this child's whole-genome sequence — 5 million variants, all of them potential suspects or alibis — was the entire puzzle.

This is the story of how we narrowed 5 million suspects to two, and why we almost didn't trust our own answer.

## The needle: BUB1B, twice

BUB1B encodes **BUBR1**, a 1050-amino-acid protein that sits at the heart of the spindle assembly checkpoint — the cell's last sanity check before it divides. When BUBR1 works, no chromosome gets left behind. When it doesn't, you get MVA.

Our pipeline was deliberately boring: annotate everything with Ensembl VEP, keep only rare variants (gnomAD AF ≤ 0.001) in functionally relevant consequence classes, intersect with a panel of genes known to cause MVA and its mimics, and ask one question: **does any gene carry two rare functional alleles?**

One gene did. Only one.

- **`chr15:40,209,701 T>G` → p.Leu737Ter.** A single letter turns a leucine codon into a stop sign. ClinVar already lists it: Pathogenic/Likely pathogenic for MVA1, multiple independent submitters. In gnomAD it exists at ~8 alleles per hundred thousand — rare enough, present enough, never homozygous. It's the kind of variant that waits silently in carriers until it meets a partner.

- **`chr15:40,220,612 T>G` → p.Asn1002Lys.** The second allele is subtler — a missense change in the C-terminal lobe of BUBR1's pseudokinase domain. It's essentially unique: a single allele in all of gnomAD v4. Every computational lens we put on it agrees it's trouble — SIFT deleterious, PolyPhen probably-damaging, AlphaMissense 0.92, and the site itself is one of the most constrained positions in the vertebrate genome (phyloP 4.8 — evolution has been saying "don't touch this" for 400 million years).

The clincher is architectural. In MVA, you essentially never see two truncating alleles — biallelic loss of BUBR1 is embryonic lethal in mice. The viable pattern is exactly what this child carries: **one allele that makes a broken protein, plus one that makes a weakened one.** Textbook.

## Why we didn't just submit and walk away

Here's the uncomfortable part: the two variants are 10.9 kilobases apart, and short-read sequencing cannot prove they're on opposite chromosomes. The average library fragment is ~1.3 kb. No read pair spans the gap. *In trans* is an inference — a very well-supported one, but an inference.

So before spending one of the competition's six submission shots, we ran an audit designed to *kill* our own call:

**Could it be a different variant in BUB1B?** We checked every ClinVar pathogenic allele at the locus — absent. The famous upstream regulatory variant from Ochiai 2014 (which causes MVA when homozygous by lowering BUB1B expression) — homozygous reference at 46× coverage. Any second P/LP allele — none.

**Could it be a different gene?** This is where the audit earned its keep. Our 15-gene panel, it turned out, was **missing two genes**: SLF2 and SMC5, the cause of MVA5/MVA6 (Atelis syndrome) — a sibling disorder described only in 2022. We found the omission ourselves, post-hoc checked the VCF, and found only common polymorphisms in both genes. The panel is now 17 genes, and the report says the exclusion was post-hoc, not from the ranked pipeline. Honesty costs a sentence; dishonesty costs the paper.

**Could it be something the assay can't see?** Partially unanswerable — and we say so. A small intronic Alu insertion, a deep-intronic pseudoexon, a cryptic structural variant: all invisible to SNV callers. The falsifier audit ends with the sentence it deserves: definitive exclusion requires long reads or RNA-seq, which is why the call remains "**presumed** compound heterozygous."

There was even a red herring handled correctly: a rare SNV sitting between the two variants — deep in intron 20, absent from every database, exactly the kind of variant that *could* have been a causal second allele or a phasing bridge. SpliceAI says it does nothing to splicing (max Δ 0.00), conservation says the position doesn't matter (phyloP −0.41). It remains what it is: a rare passenger, disclosed rather than hidden.

## What a stop sign does to a machine

Look at the structure and the two alleles tell one coherent story.

BUBR1's business end is modular: degron motifs (KEN boxes, D-box, ABBA motifs) that grab CDC20, a TPR domain for kinetochore docking, a GLEBS domain that binds BUB3, a KARD region for PP2A recruitment — and then, at the C-terminus, a pseudokinase domain that acts as a structural scaffold.

**p.Leu737Ter** cuts the protein at residue 737 — keeping every one of those interaction modules but amputating the entire pseudokinase domain and the C-terminal CDC20 contact surface. It's not a missing page; it's the last third of the book gone.

And here's the detail that shapes the whole therapeutic strategy: the stop codon lands 742 nucleotides upstream of the last exon junction — safely inside the zone where **nonsense-mediated decay** destroys the transcript before it can even make the broken protein. Loftee calls it a high-confidence LoF. The literature agrees — every characterized BUBR1 PTC allele loses its transcript to NMD.

**p.Asn1002Lys**, meanwhile, sits inside the ordered C-lobe of that same pseudokinase — 10 residues from L1012P, a known MVA1 allele that destabilizes the protein. It doesn't touch the catalytic site (pseudokinases barely have one), but it swaps a neutral asparagine for a charged lysine on a conserved, folded surface. The likely story: a hypomorph — a full-length protein that folds slightly wrong, holds slightly less well, does the checkpoint slightly worse.

One allele makes nothing. The other makes something unreliable. Together: a checkpoint that works at ~11% capacity — matching the residual BUBR1 level in the classic *BubR1* hypomorphic mouse, which develops the same mosaic aneuploidy and the same cancer predisposition.

## The therapeutic logic — and its hard gate

Because the PTC transcript is NMD-degraded, the most direct intervention isn't a readthrough drug alone — it's **rescue the transcript first, then read through the stop.** That reframes the whole Track 2 dossier:

- **Amlexanox** becomes the mechanistically-matched lead: it does *both* — NMD inhibition and PTC readthrough — and is FDA-approved (as a topical paste for aphthous ulcers; systemic use is investigational and we say so).
- **Ataluren** drops to comparator status: UGA readthrough only, no NMD activity, conditionally authorized in the UK only — for an NMD-degraded transcript, readthrough alone may have nothing to work on.
- Behind them, the hypothesis tier: proteostasis chaperones (Ravicti, arimoclomol), approved autophagy inducers (metformin, rilmenidine), and — only if a patient's cells show the signature — biomarker-gated JAK/IL-6 modulation under oncology surveillance.
- And an explicit anti-target list: anything that weakens the checkpoint further or feeds cGAS–STING. Sirolimus — the tempting mTOR hit — gets gated because rapamycin *itself* induces chromosome missegregation. For a child whose cells already missegregate, that's not a rescue; it's an accelerant.

The transcriptomic screen (LINCS L2S2) found **zero** clean rescue signatures — and we reported that as a negative result rather than a failed analysis. In a field where hype is cheap, a clean negative is worth more than a weak positive.

## What we claim, precisely

1. The proband's phenotype is consistent with biallelic BUB1B loss-of-function (MVA1).
2. Two rare functional BUB1B alleles are present: one ClinVar-pathogenic stop-gain, one ultra-rare constrained-site missense.
3. The pair is the *unique best-supported* compound-het among all variants this assay can see — after falsifying every alternative we could test.
4. Phase is unresolved. N1002K is a VUS. Cryptic non-coding mechanisms cannot be excluded by short reads alone.

## What is actually new here

We checked the literature before claiming anything:

- **No published drug-repurposing dossier for MVA exists.** MVA management in the literature is supportive — growth hormone, cancer surveillance, a single HSCT case report — plus one standing warning (avoid antimitotic chemo; Sakamoto 2017). A mechanism-gated candidate list with explicit safety triage is, as far as we can find, the first.
- **Amlexanox for a BUB1B premature stop is a novel application.** Its dual NMD-inhibition + readthrough mechanism is established in other diseases (Gonzalez-Hilarion 2012) — never proposed for MVA.
- **Flagging sirolimus as an anti-target in MVA is novel** — and it matters, because autophagy-first repurposing logic keeps surfacing rapalogs. Rapamycin itself induces chromosome missegregation (Bonatti 1998). One honest caveat: a 2025/26 *Drosophila* MVA-model paper (González-Blanco et al.) found *genetic* TOR depletion protective — which is why our dossier treats mTOR as a context-dependent open question, not a settled danger, and why any mTOR modulation is gated behind a patient-cell micronucleus assay.
- **N1002K is an unpublished MVA1 allele** — absent from every case report and review; ClinVar knows it only as a generic VUS. If this diagnosis is confirmed, it's a new entry in the MVA1 allelic series, sitting 10 residues from L1012P in the same pseudokinase C-lobe.
- **Not novel, deliberately:** the proteostasis/autophagy-rescue *concept* in MVA (González-Blanco et al. — our specific drug list is new, the idea isn't), the NMD-dependency of BUBR1 PTCs (Suijkerbuijk 2010 — we leaned on it), and the PTC + pseudokinase-missense genotype architecture (the classic MVA1 pattern since Hanks 2004 — our case fits it).

And the deliverables that make it checkable: a reproducible pipeline (VEP 116 offline → 17-gene panel → AF filter → SpliceAI → score → pair), a scorer clone that passes 39 tests, a locus falsifier audit, structural figures from AlphaFold and the APC/C–MCC cryo-EM structure, and a Track 2 dossier that leads with mechanism instead of hope.

---

*Rare disease genomics is mostly the discipline of not fooling yourself. The variants that matter are the ones that survive you trying to kill them.*

**Repo:** [github.com/Ryukijano/mva-hackathon-2026](https://github.com/Ryukijano/mva-hackathon-2026) (public after the hackathon) · **Figures + code:** this HF repo · **Challenge:** [SageBio Space](https://huggingface.co/spaces/SageBio/rare-disease-real-kid-mva-hackathon-2026)

*Not medical advice; a computational hypothesis for a hackathon, awaiting the experiments it prescribes.*
