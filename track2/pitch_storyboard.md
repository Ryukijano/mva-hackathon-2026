# Track 2 — 3-Minute Pitch Video Storyboard (revised)

**Format:** screen recording + voiceover, 180 s total. No raw genome sequence or coordinates visible.

## 0:00–0:40 — The Case & Molecular Cause
- **Visual:** proband phenotype card (HPO terms: rhabdomyosarcoma, IUGR, short stature, microcephaly, recurrent miscarriage) → simplified schematic of BUBR1 domains. A star marks the C-terminal stop-gain p.Leu737Ter and a second star marks the C-lobe missense p.Asn1002Lys.
- **VO:** "A child with embryonal rhabdomyosarcoma, growth restriction and microcephaly. Whole-genome sequencing found the cause: two ultra-rare BUB1B variants — a truncating p.Leu737Ter, ClinVar pathogenic for MVA1, and a novel C-lobe missense p.Asn1002Lys. That is the classic viable MVA1 architecture: one severe null and one hypomorphic missense."
- **On-screen:** EPCR 0.950 compound-het call; only BUB1B in the MVA panel carries two rare functional alleles; N1002K AlphaMissense 0.9229, but ESM-1v says mild.

## 0:40–1:35 — Two Upstream Leads + a Proteostasis-First Stack
- **Visual:** four-tier diagram: (1) Direct readthrough of the UGA stop, (2) BUBR1 protein stabilisation via SIRT2/NAD+, (3) proteostasis/autophagy, (4) biomarker-gated inflammation. Show the cascade: weak SAC → mosaic aneuploidy → proteotoxic + lysosomal stress → ROS → micronuclei → cGAS-STING → IFN/IL-6.
- **VO:** "We take a two-pronged upstream approach. First, Ataluren and ELX-02 are translational readthrough drugs that can let ribosomes read past the UGA stop codon in p.Leu737Ter and restore full-length BUBR1. Even a few percent full-length protein can rescue checkpoint function. Second, NMN raises the residual BUBR1 pool through SIRT2 deacetylation of K668 — but that 58% lifespan gain was SIRT2 transgenic, not NMN. For organellar damage we now lead with Ravicti, a sodium-free 4-PBA prodrug that rescues aneuploidy-associated aggregates in human iPSC neurons, and trehalose, which drives mTORC1-independent autophagy through TFEB. Rapamycin only rescued fly neuroblast counts, not brain size. Antioxidants and Nrf2 activators are flagged because they can promote cancer progression in an MVA1 child."
- **On-screen:** North 2014 (SIRT2–K668); Keeling 2016 / Peltz 2008 (ataluren UGA readthrough); ELX-02 CF organoid data; Fisher 2020 (4-PBA iPSC neurons); Santaguida & Amon 2015 (TFEB in aneuploidy); Piskounova 2015 (NAC metastasis).

## 1:35–2:25 — Computational Target-First Screen
- **Visual:** ChEMBL screen output (92 drug-target rows) → `--approved-only` filter (32 rows) → ranked candidate table → anti-target list. Emphasise the FKBP1A vs MTOR distinction for rapalogs.
- **VO:** "We ran a target-first ChEMBL screen across the axis. Adding FKBP1A fixed the rapalog retrieval: sirolimus and everolimus bind FKBP12, not the MTOR kinase domain. The approved-only filter gives 32 candidates. We then manually added Ataluren, ELX-02, Ravicti, trehalose, and spermidine from the literature, because their targets are the ribosome or general proteostasis, not single genes."
- **On-screen:** `track2/drug_screen.py --approved-only`; `chembl_axis_drugs_approved.csv` excerpt; manual-candidate table.

## 2:25–3:00 — Validation Plan & Closing
- **Visual:** validation flowchart: (1) Western blot for full-length BUBR1 after readthrough drugs, (2) BUBR1 protein after NMN, (3) aggregate/apoptosis after Ravicti/arimoclomol, (4) TFEB/autophagy after trehalose, (5) ISG/IL-6 biomarker before JAK/IL-6 blockade, (6) oncology surveillance throughout.
- **VO:** "Next steps are all assay-gated: can we restore full-length BUBR1, can we stabilise the residual protein, can we clear aggregates, and can we justify Tier 3 only with a real interferon signature? Genotype, mechanism, mutation-specific rescue, target screen, anti-target filter, and oncology-aware safety — reusable for the next N-of-1."
- **On-screen:** GitHub repo URL; three-tier summary; safety table; CC BY 4.0.

## Shot list
1. Title card + team name.
2. Phenotype card (no genome sequence).
3. BUBR1-domain schematic with two variant marks.
4. Four-tier mechanism diagram.
5. Terminal window running `drug_screen.py --approved-only`.
6. CSV table zoom (manual leads + approved ChEMBL hits + anti-targets).
7. Validation flowchart.
8. Closing slide with repository URL and CC BY 4.0.

## Recording checklist
- [ ] Record at 1080p, trim to exactly 180 s with `ffmpeg`.
- [ ] Upload unlisted to YouTube/Vimeo and insert the URL in the submission form.
- [ ] No raw genomic coordinates or FASTA/sequence visible in any frame.
