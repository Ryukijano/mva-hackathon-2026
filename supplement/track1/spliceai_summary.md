# SpliceAI deep-intronic sweep — BUB1B full gene region

Date: 2026-09-10
Tool: SpliceAI 1.3.1 (Python module), `-D 4999` (maximum distance)
Reference: GRCh38 primary assembly
Region: chr15:40,180,000–40,300,000 (120 kb, encompassing BUB1B and flanking genes)
Variants annotated: 135

## Target variant scores

| Variant | GRCh38 | SpliceAI gene | DS_AG | DS_AL | DS_DG | DS_DL | Max DS | Verdict |
|---|---|---|---|---|---|---|---|---|
| p.Leu737Ter | 15:40209701 T>G | BUB1B | 0.03 | 0.00 | 0.00 | 0.01 | **0.03** | No splice impact (< 0.2) |
| p.Asn1002Lys | 15:40220612 T>G | BUB1B | 0.02 | 0.00 | 0.00 | 0.00 | **0.02** | No splice impact (< 0.2) |

## All variants with DS > 0.01

No variant annotated as BUB1B exceeds DS = 0.03. The only variant in the
extracted region with DS > 0.2 is in PLCB2 (chr15:40291675, DS_AL = 0.41),
a neighboring gene outside BUB1B.

## Conclusion

The deep-intronic SpliceAI sweep at maximum distance (-D 4999) confirms
that neither target BUB1B variant has a predicted splice-altering effect.
No cryptic splice-site creation or disruption is predicted for any BUB1B-
annotated variant in the 120 kb region. This closes the "cryptic splice
third hit" gap in the Track 1 falsifiers list.
