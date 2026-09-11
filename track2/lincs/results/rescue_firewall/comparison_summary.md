# Firewall comparison: mimic-sorted vs rescue-sorted L2S2

Date: 2026-09-10

## Background

The original firewall run consumed L2S2 consensus files retrieved with the
L2S2 server's default sort (`pvalue_up` ascending, i.e. mimic-first). The
directional rescue hypothesis requires `adj_pvalue_down < 0.05` (reverse
enrichment), so the L2S2 queries were re-run with `sortby=adj_pvalue_down`
and the firewall was re-executed on the rescue-sorted consensus files.

## Inputs

| Firewall run | L2S2 source dir | L1000CDS2 included | Retrieval sort |
|---|---|---|---|
| Original | `track2/lincs/results/l2s2` | yes | `pvalue_up` (mimic-first, default) |
| Rescue-sorted | `track2/lincs/results/l2s2_rescue` | no (dir has no L1000CDS2 files) | `adj_pvalue_down` (rescue-first) |

The rescue-sorted directory contains 1,407 L2S2 consensus rows across 21
signatures and 474 unique drugs. The original directory additionally
contained L1000CDS2 rows, which is why the original firewall considered 676
drugs versus 474 here.

## Result

| Firewall run | ACCEPT | WEAK | REJECT | Total |
|---|---|---|---|---|
| Original (mimic-sorted + L1000CDS2) | 0 | 2 | 674 | 676 |
| Rescue-sorted (L2S2 only) | 0 | 2 | 472 | 474 |

### Weak hits

| Drug | Run | Engines | Total sig | Reverse (FDR) | Mimic (FDR) | General (FDR) | min p_down | min adj_p_down | Direction |
|---|---|---|---|---|---|---|---|---|---|
| sirolimus | Original | 2 | 4 | 1 | 4 | — | 6.69e-07 | 9.10e-05 | MIXED |
| sirolimus | Rescue | 1 | 1 | 1 | 9 | 2 | 1.70e-06 | 1.97e-04 | MIXED |
| dasatinib | Original | 2 | 2 | 1 | 2 | — | 9.69e-08 | 1.50e-05 | MIXED |
| dasatinib | Rescue | 1 | 1 | 1 | 5 | 0 | 7.12e-07 | 8.90e-05 | MIXED |

## Interpretation

1. **The firewall conclusion is unchanged.** Both runs produce
   `ACCEPT=0 / WEAK=2 / REJECT=rest`. No drug passes the firewall as a
   primary rescue lead.
2. **Both weak hits remain MIXED.** Sirolimus and dasatinib each have at
   least one FDR-significant reverse (`adj_pvalue_down < 0.05`) signature
   but also multiple FDR-significant mimic (`adj_pvalue_up < 0.05`)
   signatures. The MIXED-directionality penalty therefore still applies
   and downgrades them to WEAK.
3. **Rescue-sorted retrieval retrieved more mimic signatures, not fewer.**
   This is expected: sorting by `adj_pvalue_down` surfaces drugs with the
   strongest reverse signal, but those same drugs often also have strong
   mimic signals in other signatures. The rescue sort does not eliminate
   mimic evidence; it only reorders retrieval.
4. **The reverse signal is real but not specific.** Sirolimus's single
   FDR-significant reverse signature (human MVA GSE22206) is reproduced
   under rescue sorting (`adj_pvalue_down = 1.97e-04`), confirming the
   original observation. However, the nine FDR-significant mimic
   signatures indicate that sirolimus is a transcriptomic mimic in most
   contexts, not a consistent reverser.
5. **L1000CDS2 was not re-queried.** The rescue-sorted directory contains
   only L2S2 files, so the rescue firewall run has no L1000CDS2 engine.
   This is why engine counts drop from 2 to 1 for both weak hits. The
   L1000CDS2 scores from the original run remain valid (they are
   direction-thresholded at `score > 0` for reversal).

## Conclusion

The rescue-sorted re-query validates the original firewall: the zero-ACCEPT
result is not an artifact of mimic-sorted retrieval. The two weak hits
(sirolimus, dasatinib) are MIXED-direction drugs with one reverse signature
each, and they remain exploratory hypothesis-supporting signals rather
than independent or cross-species validation. No change to the Track 2
ranking is warranted.

## Files

- Original firewall: `track2/lincs/results/lincs_firewall_decisions.csv`
- Rescue firewall: `track2/lincs/results/rescue_firewall/lincs_firewall_decisions.csv`
- Rescue ranking: `track2/lincs/results/rescue_firewall/lincs_candidate_ranking.csv`
- This summary: `track2/lincs/results/rescue_firewall/comparison_summary.md`
