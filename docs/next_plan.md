# Next plan — post-audit, pre-submission (11 Sep 2026)

**Deadline:** 24 Oct 2026, 23:59 UTC (~6 weeks). Judging ~2–3 months after close.
**Scope:** synthesises the 10–11 Sep 2026 parallel audit (Track 1, Track 2, literature/challenge,
BUB1B deep validation), fresh ClinVar/gnomAD v4/dbSNP checks, a live pull of the challenge
Space source (`evaluation.py`, `config.py`, `submit_track1.py`, `submit_track2.py`, `faq.py`,
`rules.py`, `leaderboard.py`), and the current community discussions (#1–#22).

---

## What the live Space pull confirmed (11 Sep 2026)

- **`evaluation.py` matches our local clone** (`src/mva_hackathon/eval/scorer.py`) — rank tiers
  100/50/25/10, compound-het partial credit at half points, F-max at the individual-variant
  level, ties broken by original CSV order.
- **Upload contract (Track 1):** `display_name` + `github_url` (must start `https://github.com/`)
  + report file (`.pdf` or `.md`) + predictions CSV. The methods XLSX is an optional organiser —
  the report itself is the methods description. `finding_type` is informational only.
- **Upload contract (Track 2):** `display_name` + `github_url` + **`video_url` (required)** +
  report file (`.pdf`/`.md`) + optional `notes` box. Up to 3 submissions; panel reviews the latest.
- **`config.py`:** `MAX_TRACK1_SUBMISSIONS = 6`, `MAX_TRACK2_SUBMISSIONS = 3`,
  leaderboard dataset `SageBio/mva-hackathon-2026-leaderboard` (private), ground truth
  `SageBio/mva-hackathon-2026-gt/gold_standard_track1.json` (private — not touched).
- **FAQ:** perfect scores already exist on the Track 1 leaderboard; the methods write-up is
  the judged differentiator ("Two perfect scores can look very different once we read how
  each team got there" — discussion #18). Track 2 judged on rigor/impact/innovation/scalability.
- **Discussion #19 (closed):** resubmitting to attach methods creates a second leaderboard
  entry; organisers can retract the first and refund the quota — but best practice remains
  **attach the report on the first upload**.
- **Discussion #10:** methods template updated 28 Aug 2026 with a required LLM-usage line;
  already-submitted teams only need to update the report in the linked GitHub repo.
- **Discussion #22 (open):** another team has "hit the wall" on the cis/trans issue and is
  weighing UK Biobank access cost — phasing is a shared, unsolved limitation, not a
  Ryukijano-specific failure.
- **Discussion #17 (open):** reference FASTA confirmed as
  `GCA_000001405.15_GRCh38_no_alt_analysis_set_plus_hs38d1_maskedGRC_exclusions_v2_no_chr.fasta`
  (bare contigs, Sentieon 202308.02 + GATK VariantFiltration). `PGT`/`PID` are declared but
  only populated at homozygous indels — absent at both target alleles, consistent with our
  WhatsHap UNRESOLVED verdict.
- **Discussion #5 (open):** drug combinations of market-approved medications are acceptable;
  investigational-only compounds do not fit Track 2's scope → ELX-02 correctly stays in the
  future-research tier.
- **Discussion #2 (open):** third-party LLMs allowed when the service is a "processor, not
  recipient" (commercial terms, no training, limited retention). Our disclosures already
  match this framing.
- **Discussion #20 (open):** a competitor flagged incidental ClinVar P/LP findings in the
  submission notes — secondary findings are judged qualitatively; we currently submit one
  primary row and no secondary rows (defensible, but a reviewer may ask).

---

## Track 1 status — verified today

| Check | Result |
|---|---|
| Official CSV template headers | `proband_id,chrom_1,pos_1,ref_1,alt_1,chrom_2,pos_2,ref_2,alt_2,epcr,finding_type,notes` — **our CSV matches exactly** |
| `proband_id` value | Template uses `PROBAND01`; ours matches |
| EPCR | `0.950000` in (0,1]; single `primary` row — optimal under the scorer |
| ClinVar VCV000533901 | P/LP, multiple submitters, last eval 2024/10/09; dbSNP rs759242053 |
| ClinVar VCV004600147.1 | VUS via `c.3006T>A`, single submitter SCV007198955, 19 Sep 2025, generic trait; our `c.3006T>G` is ClinVar-absent; dbSNP rs2542593804 |
| gnomAD v4 | L737Ter exome AC=115 (AF 7.87e-05), genome AC=5 (AF 3.29e-05); N1002K exome AC=1 (AF 6.84e-07), genomes absent |
| SpliceAI `-D 4999` sweep | Done — max DS 0.03/0.02, no splice mechanism |
| AlphaGenome AVI | Done — 33.76 / 25.61 Phred |
| WhatsHap phasing | UNRESOLVED — structural short-read limit, disclosed |
| VCF `PGT`/`PID` at target sites | Absent (header-declared, populated only at hom indels) |
| `pytest tests/` | 39/39 pass |

## Track 2 status — verified today

| Check | Result |
|---|---|
| LINCS firewall | `ACCEPT=0 / WEAK=2 (sirolimus, dasatinib, both MIXED) / REJECT=674` (orig), `0/2/472` (rescue-sorted) |
| Rescue-sort metadata bug | **Fixed** — `04_firewall.py` now derives `l2s2_retrieval_sort` from `--results-dir` or `--retrieval-sort` |
| `03b_run_l2s2_queries.py` path | **Fixed** — now repo-relative (`Path(__file__).parents[2]`) |
| Regulatory | Ataluren: UK/MHRA conditional only (PLGB 44221/0003, renewed 24/02/2026; FDA NDA withdrawn 12 Feb 2026; EMA non-renewal 28 Mar 2025). Arimoclomol: FDA Miplyffa 20 Sep 2024; EMA Meplyffa refused 23 Jul 2026, re-exam requested 5 Aug 2026. Others verified. |
| Report/submissions sync | **Done** — `submissions/Ryukijano_track2_report.md` and `_candidates.csv` copied from canonical |
| Pitch video | **Not recorded** — the single true blocker |

---

## What is still missing that could stop us winning

### P0 — True blockers

| # | Blocker | Consequence | Owner | Due |
|---|---|---|---|---|
| 1 | **Track 2 pitch video (3 min, YouTube/Vimeo)** | Track 2 cannot be submitted — `video_url` is a required field in `submit_track2.py`. | User | ASAP |
| 2 | ~~**Track 1 shot decision**~~ | **DONE 12 Sep 2026 — submitted CSV + report + GitHub URL in one shot; scorer returned full match at rank 1 (100.0 rank pts, F-max 1.000).** Both alleles confirmed; p.Asn1002Lys c.3006T>G is now a confirmed MVA1 allele. | — | — |
| 3 | ~~**GitHub repo must be public after close**~~ | **DONE 12 Sep 2026** — repo flipped to public early (user decision; nothing gated tracked). | — | — |

### P1 — High-value polish for the judged write-up

| # | Item | Status |
|---|---|---|
| 1 | Track 1 report now says "presumed/best-supported", includes A739S functional context, cryptic-second-hit caveat, re-verified ClinVar/gnomAD/dbSNP lines | **Done** |
| 2 | Methods answers exist in the `.md` report; the XLSX template is optional but filled copies can be committed for completeness | Optional |
| 3 | Residual-BUBR1 wording normalised to 11% ± 3% (Baker 2004) across README/WHAT_WE_DID/SUMMARY/report | **Done** |
| 4 | Track 2 dossier refreshed: ataluren FDA-withdrawal date, Meplyffa naming, arimoclomol re-exam, FDA label URL | **Done** |
| 5 | Commit force-added small artifacts (`results/alphagenome/`, `results/spliceai/`, `supplement/track1/clinvar_verification.md`) or move to `supplement/` | **Pending decision** — either works; supplement is cleaner |
| 6 | Re-check ataluren UK/MHRA + arimoclomol EU re-exam outcome within ~1 week of submission | 17–21 Oct |

### P2 — Nice-to-have

- Optional secondary/incidental-finding row in the CSV (a competitor did a full ClinVar P/LP scan — discussion #20). Not required; only do it if a quick whole-VCF ClinVar P/LP scan can be run reproducibly.
- PDF render of both reports for upload (`pandoc` or similar).
- Filled `methods_description_form.xlsx` copies committed under `submissions/` for judges who prefer the structured form.

### P3 — Not worth doing

- Re-running the 84 GB WGS pipeline (UNRESOLVED is structural, not a data problem).
- Statistical phasing on a singleton AC=1 allele (uninformative).
- UK Biobank / external phasing panels — discussion #22 shows another team is weighing the cost; we already know it cannot resolve this pair (the intervening het SNV density is the bottleneck, not population LD).
- AlphaFold-from-scratch, PrimeKG/TxGNN retraining, more LINCS re-queries.
- Claiming the noisy chr15 depth dip as mosaic aneuploidy.

---

## Recommended sequence

1. **Now:** commit the audit-driven edits + regenerated firewall CSVs; update GitHub issues + Notion.
2. **User this week:** record the Track 2 pitch (storyboard ready), submit Track 1 (CSV + `.md` report + GitHub URL in one shot).
3. **17–21 Oct:** final regulatory re-check; submit Track 2 (report + GitHub + video URL + notes).
4. **24–25 Oct:** make repo public; begin 30-day deletion window for gated data.
