# Track 2 — 3-Minute Pitch Video Storyboard

**Format:** screen recording + voiceover, 180 s total.

## 0:00–0:45 — The Case & Molecular Cause
- **Visual:** proband phenotype card (HPO terms: rhabdomyosarcoma, IUGR, short stature, microcephaly, recurrent miscarriage) → genome browser at chr15:40209701 and chr15:40220612.
- **VO:** "A child with embryonal rhabdomyosarcoma, growth restriction and microcephaly. Whole-genome sequencing revealed the cause: two ultra-rare BUB1B variants — a truncating p.Leu737Ter, pathogenic in ClinVar for MVA1, and a novel kinase-like-domain missense p.Asn1002Lys, AlphaMissense likely-pathogenic. That is the classic viable MVA1 architecture. Residual protein in this child has not been measured; the mouse hypomorph class is about 10%."
- **On-screen:** EPCR 0.950 compound-het call; only BUB1B in the 15-gene MVA panel carried 2 rare functional alleles.

## 0:45–1:45 — Multi-Tiered Repurposing Logic
- **Visual:** three-tier diagram (Upstream / Organelle / Systemic) with the cascade: weak SAC → aneuploidy → proteotoxic stress + ROS → micronuclei → cGAS-STING → IFN.
- **VO:** "Because the disease is hypomorphic, we can't silence the gene — we must stabilize remaining protein and blunt downstream damage. Tier 1: NMN raises BUBR1 protein via SIRT2–K668. The 58% lifespan gain is SIRT2 overexpression, not NMN. Tier 2: rapamycin rescued fly neuroblast counts, not brain size; the fly brain-size rescue was Sod2 and GTPx-1 overexpression — NAC and MitoQ are the drug analogues we propose. Tier 3: baricitinib, biomarker-gated, for the micronuclei-driven interferon storm."
- **On-screen:** North 2014 (NMN = protein; SIRT2-Tg = lifespan); González-Blanco 2026 (Sod2/GTPx-1 vs rapamycin NB counts); NEJM 2020 (baricitinib, 35 children).

## 1:45–2:30 — Computational & In Vivo Evidence
- **Visual:** ChEMBL screen output (85 drug-target rows) → ranked candidate table → anti-target list.
- **VO:** "We ran a target-first drug screen across the whole axis — SAC, SIRT2, mTOR, Nrf2, JAK, IL-6 — and graded every hit by evidence in BUBR1-hypomorphic models and pediatric approval. The screen also told us what NOT to do: MPS1 and Aurora B inhibitors would weaken the checkpoint further — they're cancer drugs, and would make this child worse. Our top candidates: NMN, rapamycin, NAC, MitoQ, omaveloxolone, with baricitinib and tocilizumab as biomarker-gated adjuncts."
- **On-screen:** `track2/drug_screen.py` running; candidates CSV; excluded anti-targets.

## 2:30–3:00 — Clinical Translation & Summary
- **Visual:** proposed trial path: patient-derived cells → fly model → BubR1^H/L1002P mouse (nearest published class, not N1002K) → N-of-1 protocol with monitoring.
- **VO:** "Next: confirm BUBR1 protein in patient cells, test NMN on that protein, and gate Tier 3 on an IFN signature. Genotype, mechanism, axis screen, anti-target filter, paediatric safety — reusable for the next N-of-1."
- **On-screen:** https://github.com/Ryukijano/mva-hackathon-2026 ; three-tier summary.
