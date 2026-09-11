# LINCS L2S2 + L1000CDS2 — short result

Full campaign context: [`../../WHAT_WE_DID.md`](../../WHAT_WE_DID.md). Method: [`README.md`](README.md).

Nine GEO contrast/gene-list definitions (GSE22206 human MVA; GSE134781 / GSE134780 mouse *BubR1* hypomorphs) were queried at 100/150/250 genes through **L2S2** (primary) and **L1000CDS2** (secondary). GSE247267 produced no DEGs and was not queried. The false-rescue firewall gates on L2S2 **directional reverse FDR** (`adj_pvalue_down < 0.05`), penalizes **MIXED** directionality (both reverse and mimic FDR signatures → WEAK, not ACCEPT), thresholds L1000CDS2 on positive scores, and keeps only currently approved medications that are not anti-target, not cytotoxic / broad cancer-kinase, and not a conditional/adjunct biological tier.

| Status | n unique drugs |
|---|
| ACCEPT | 0 |
| WEAK | 2 |
| REJECT | 674 |

**Denominator note:** 676 is the union of unique drugs retrieved across both engines (L2S2 + L1000CDS2). The rescue-sorted re-query (L2S2 only, `sortby=adj_pvalue_down`) considered 474 drugs and produced the same `ACCEPT=0 / WEAK=2 / REJECT=472` conclusion, validating that the zero-ACCEPT result is not an artifact of mimic-sorted retrieval. See `results/rescue_firewall/comparison_summary.md`.

**WEAK:** sirolimus (mTORC1/FKBP rapalog; 2 engines, 4 total signatures, **1** FDR-significant L2S2 reverse signature in GSE22206 case vs control 100-gene `adj_pvalue_down = 9.14e-05`; **4** FDR-significant mimic signatures; 3 L1000CDS2 signatures, mean score 0.045). **MIXED direction** — downgraded from ACCEPT because the drug mimics the disease signature in more contexts than it reverses it. The reverse signal is not robust to gene-list size: at 150/250 genes in the same contrast, sirolimus is a strong mimic (`adj_pvalue_up ≈ 1e-13`). The 100-gene down-list contains 14 nominal genes (86 FDR + 14 nominal).
**WEAK:** dasatinib (multi-kinase/senolytic; 2 engines, 2 total signatures, **1** FDR-significant L2S2 reverse signature in GSE22206 case vs control 100-gene `adj_pvalue_down = 1.51e-05`; **2** mimic signatures; 1 L1000CDS2 signature). **MIXED direction** — also downgraded by the MIXED penalty, not solely by the tier-string filter.

**REJECTED:** everolimus (mTORC1/FKBP rapalog; general FDR enrichment `adj_p = 7.46e-04` and mimic signatures, but **no FDR-significant reverse** and no L1000CDS2 support); perhexiline (L1000CDS2-only, no reverse signal, rejected by pediatric safety due to hepatotoxicity and lack of pediatric indication).

**Post-hoc mechanism check (sirolimus):** independent of the transcriptomic signal, rapamycin is itself aneugenic — it induces chromosome malsegregation and CREST-positive micronuclei in human lymphocytes/lymphoblasts and rodent cells via the p70S6K pathway (Bonatti et al. 1998, *Chromosoma* 107:498–506, doi:10.1007/s004120050335), and an unpublished rapamycin-diet note in *BubR1^H/H* mice was not positive (Baker 2013, *Cell Rep*). The WEAK/MIXED sirolimus signal should therefore be read as a context-specific observation with a mechanism-based anti-target concern in MVA1, not a rescue lead; any further consideration requires micronucleus/missegregation assays in patient cells.

**Retrieval-sort sensitivity check:** The original L2S2 data was retrieved with the server's default sort (mimic ascending). The queries were re-run with `sortby=adj_pvalue_down` (rescue-first) and the firewall was re-executed on the rescue-sorted consensus files. The conclusion is unchanged: `ACCEPT=0 / WEAK=2 / REJECT=rest` in both runs. The rescue-sorted re-query retrieved *more* mimic signatures for both weak hits, strengthening the MIXED penalty.

Absence of a hit is not evidence against Ataluren, Ravicti, arimoclomol, NMN, or JAK/IL-6 drugs. No LINCS result establishes BUBR1 rescue, SAC correction, or patient benefit.
