# Next plan — post-synthesis, pre-submission (7 Sep 2026)

**Deadline:** 24 Oct 2026, 23:59 UTC (~7 weeks). Judging through 24 Nov.
**Guiding fact (from the Space's own announcements):** many teams already have perfect Track 1 scores; "two perfect scores can look very different once we read how each team got there." The **methods write-up is the differentiator**. Everything below is ranked by write-up value per unit of compute, and by risk-retirement before we spend a submission shot.

---

## P0 — Submission mechanics (learned from the organizers' discussions)

1. **The submission form takes a methods description together with the CSV.** Discussion #19 shows a participant burning a second shot just to attach methods. → Prepare **both** the CSV and the methods description *before* the first upload; one shot should suffice.
2. **The methods template now has a required LLM-usage question** (discussion #10, updated template). Our README already discloses AI assistance (Anthropic API / Cursor, commercial terms, no training on inputs) — port that wording into the template answer.
3. Reference genome confirmed in discussion #17: GRCh38 no-alt analysis set + hs38d1 decoy (matches our VCF header); Sentieon 202308.02 + GATK VariantFiltration. Cite this in the methods write-up.
4. Re-verify ClinVar VCV000533901 / VCV4600147 and the gnomAD v4 counts **on submission day** (live databases).

## P1 — The one experiment that can still change the call: FASTQ read-backed phasing (+ mosaic landscape)

**Why it is first:** our only unproven assumption is that the two *BUB1B* alleles are **in trans** (parental phasing impossible — no parents' data). The gated dataset contains **8 FASTQ files (~84 GB, 4 lanes × R1/R2)** — no BAM. Aligning them ourselves gives:

1. **Read-backed phasing (WhatsHap)** across the ~11 kb between `15:40209701` and `15:40220612` plus intervening het SNPs → *demonstrate* (or refute!) in-trans. Either outcome is publishable in the write-up: proof upgrades our weakest claim; refutation saves us from spending a shot on a wrong call.
2. **Depth-based mosaic aneuploidy landscape** (per-chromosome read-depth Z-scores, ~5 Mb bins) → computationally reproduce the "mosaic variegated" cytogenetic finding from WGS alone. This is a signature figure for the write-up and validates the phenotype→genotype link end-to-end.
3. **High-confidence VAFs** for both alleles (current VCF: 54% / 46% at 46×/28× — already germline-like; FASTQ re-derivation makes it bulletproof).

**Cost:** 1 AIRE CPU job (no GPU): BWA-MEM2 align (~24–36 h at 16–32 cores), sort/index (~120 GB BAM on `$SCRATCH`), WhatsHap phase on BUB1B, mosdepth bin-depth. Data stays on `$SCRATCH`; delete with the rest of the gated data within 30 days of close. Needs `bwa-mem2` + `samtools` + `whathap` + `mosdepth` added to an env (conda, not login-node runs).

**Decision rule:** phasing proves trans → submit with "read-backed phasing confirms compound heterozygosity" (strongest possible write-up). Phasing proves cis or is unresolvable → stop, re-evaluate the call before spending any shot.

## P2 — Cheap in-silico strengtheners (each ≤ half a day)

| Item | Tool | Write-up value |
|---|---|---|
| **BUB1B constraint metrics** | ✅ done 7 Sep: pLI ≈ 5.5e-17 (not haploinsufficient — recessive-compatible), LoF z 3.74, mis z 1.30, OE LoF upper 0.75 (gnomAD API) | Explains why a PTV at AF ~7.9e-05 is carrier-compatible |
| **AlphaGenome variant effects** (splicing Δ, expression tracks for both alleles) | `science_skills/alphagenome_single_variant_analysis/` — needs an AlphaGenome API key (not found in env; request or skip) | Modern in-silico layer; tests splice impact near both alleles |
| **Deep-intronic SpliceAI sweep on BUB1B** (`-D 4999`, whole-gene VCF slice) | existing AIRE refs + env; small Slurm job | Closes the "third variant / cryptic splice" gap in the falsifiers list |
| **ClinVar benign-only control** (exclude single-submitter LB) | recompute from cached `variant_summary.txt.gz` | Robustness check on the ESM-1v B/LB median (−0.161) |

## P3 — Track 2 (parallel, mostly non-compute)

1. **L2S2 re-query** with `sortby=adj_pvalue_down` (issue #3; server was 504 — retry weekly).
2. **Regulatory re-verification** of ataluren/arimoclomol/omaveloxolone claims against FDA/EMA/MHRA primary pages (issue #5).
3. **3-minute pitch video** — the only Track 2 blocker; storyboard is ready (`track2/pitch_storyboard.md`). User records; we can draft the VO timing sheet per scene.
4. Keep sirolimus framed as WEAK/MIXED + aneugenicity caveat (done in `2e7d7a0`).

## P4 — Submission sequence

1. Track 1: upload CSV + methods (template incl. LLM statement) + GitHub URL — **one shot**, only after P1 resolves phasing.
2. Track 2: dossier + pitch URL — panel reviews the **latest** of 3 shots, so submit once, complete.
3. Post-close: delete gated genome/FASTQ within 30 days; keep ranked findings + code (CC BY 4.0).

---

## Sequenced this week

| Day | Action |
|---|---|
| 1 | Submit AIRE CPU job: download FASTQs → BWA-MEM2 align → sort/index (P1) |
| 1–2 | While aligning: deep-intronic SpliceAI sweep + ClinVar benign-only control (P2) |
| 2 | WhatsHap phasing + mosdepth landscape; make the figure |
| 3 | Update `track1_report.md` + `docs/track1_first_principles.md` with phasing result; decision gate |
| 3–4 | AlphaGenome runs if API key available; L2S2 retry |
| 4–5 | Finalize methods write-up against the latest template; submit Track 1 (1 shot) |

**Explicitly not doing:** reading the ground truth (`groundtruth.py` / private GT dataset); training TxGNN-style models (no time, no gain); adding hedge rows to the CSV (cannot improve the automated score); re-running LINCS unless the L2S2 server recovers.
