# Figures — MVA Hackathon 2026

Rendered with PyMOL (OSMesa headless) + matplotlib. `.pse` files reopen in desktop PyMOL.

| File | Source | Shows |
|---|---|---|
| `out/bubr1_plddt_overview.png` | AlphaFold AF-O60566 | Full-length BUBR1, pLDDT colouring, L737/N1002/L1012 marked |
| `out/bubr1_L737Ter_truncation.png` | AF-O60566 | Residues 1–736 retained (cyan) vs 737–1050 lost to the stop-gain (salmon) |
| `out/bubr1_clobe_N1002_L1012.png` | AF-O60566 | Pseudokinase C-lobe zoom: N1002K (our variant) vs L1012P (known MVA1), 10 residues apart |
| `out/apcc_mcc_highlight.png` | RCSB 6TLJ | APC/C (grey) inhibited by the MCC — BUBR1 chain S (red), CDC20 chains Q/R (orange), MAD2A chain Z (yellow) |
| `out/apcc_mcc_complex.png` | RCSB 6TLJ | Same complex, chain-coloured |
| `out/pp2a_b56_bubr1.png` | RCSB 5JJA | PP2A-B56γ (cyan) bound by the BUBR1 KARD segment (red, res ~665–682, retained after L737Ter) |
| `out/bubr1_kinetochore_complex.png` | RCSB 3SI5 | BUBR1 TPR domain docking to the kinetochore |
| `out/mechanism_schematic.png` | matplotlib | Track 2 mechanism: NMD gate → amlexanox → rescue; pathology cascade → tiers + anti-targets + safety gates |

Scripts: `render_bubr1.py`, `render_complexes.py`, `render_highlight.py`, `mechanism_schematic.py`.
Structures: `structures/AF-O60566-F1-model_v6.cif`, `6TLJ.cif`, `5JJA.cif`, `3SI5.cif` + PAE JSON.
