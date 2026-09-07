# LINCS L2S2 + L1000CDS2 — short result

Full campaign context: [`../../WHAT_WE_DID.md`](../../WHAT_WE_DID.md). Method: [`README.md`](README.md).

Nine GEO contrast/gene-list definitions (GSE22206 human MVA; GSE134781 / GSE134780 mouse *BubR1* hypomorphs) were queried at 100/150/250 genes through **L2S2** (primary) and **L1000CDS2** (secondary). GSE247267 produced no DEGs and was not queried. The false-rescue firewall gates on L2S2 **directional reverse FDR** (`adj_pvalue_down < 0.05`), penalizes **MIXED** directionality (both reverse and mimic FDR signatures → WEAK, not ACCEPT), thresholds L1000CDS2 on positive scores, and keeps only currently approved medications that are not anti-target, not cytotoxic / broad cancer-kinase, and not a conditional/adjunct biological tier.

| Status | n unique drugs |
|---|
| ACCEPT | 0 |
| WEAK | 2 |
| REJECT | 674 |

**WEAK:** sirolimus (mTORC1/FKBP rapalog; 2 engines, 4 total signatures, **1** FDR-significant L2S2 reverse signature in GSE22206 case vs control 100-gene `adj_pvalue_down = 9.14e-05`; **4** FDR-significant mimic signatures; 3 L1000CDS2 signatures, mean score 0.045). **MIXED direction** — downgraded from ACCEPT because the drug mimics the disease signature in more contexts than it reverses it. The reverse signal is not robust to gene-list size: at 150/250 genes in the same contrast, sirolimus is a strong mimic (`adj_pvalue_up ≈ 1e-13`). The 100-gene down-list contains 14 nominal genes (86 FDR + 14 nominal).
**WEAK:** dasatinib (multi-kinase/senolytic; 2 engines, 2 total signatures, **1** FDR-significant L2S2 reverse signature in GSE22206 case vs control 100-gene `adj_pvalue_down = 1.51e-05`; **2** mimic signatures; 1 L1000CDS2 signature). **MIXED direction** — also downgraded by the MIXED penalty, not solely by the tier-string filter.

**REJECTED:** everolimus (mTORC1/FKBP rapalog; general FDR enrichment `adj_p = 7.46e-04` and mimic signatures, but **no FDR-significant reverse** and no L1000CDS2 support); perhexiline (L1000CDS2-only, no reverse signal, rejected by pediatric safety due to hepatotoxicity and lack of pediatric indication).

**Known retrieval limitation:** The current L2S2 data was retrieved with the server's default sort (mimic ascending), which may miss strong rescue candidates. The query script has been corrected to use `sortby=adj_pvalue_down` for future re-queries, but the server was unavailable (504) during this analysis.

Absence of a hit is not evidence against Ataluren, Ravicti, arimoclomol, NMN, or JAK/IL-6 drugs. No LINCS result establishes BUBR1 rescue, SAC correction, or patient benefit.
