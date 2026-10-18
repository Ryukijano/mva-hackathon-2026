# Figures — MVA Hackathon 2026

Rendered with PyMOL (OSMesa headless, white studio background) + matplotlib + PIL. `.pse` files reopen in desktop PyMOL.

| File | Source | Shows |
|---|---|---|
| `out/bubr1_alphafold_structural_proof.png` (`.pdf`) | AlphaFold DB API v6 (`O60566` + 6 interactors) + AlphaMissense + ESM-1v | **4-panel structural synthesis `(a)-(d)`**: `(a)` domain map, per-residue pLDDT & rolling AlphaMissense; `(b)` `1,050 × 1,050` PAE matrix (3 rigid domains `47–211`, `406–463`, `755–1043`; cross-domain PAE `28–29 Å`; `PDB 6TLJ` resolved `19–345`); `(c)` saturation mutagenesis across all 19 substitutions at `L737` (UGA readthrough `L737W/R/C` all `Likely Benign`), `A739`, `N1004` (`0/19 LPath`), `R814`, `K668`, `L1012`, and `N1002` (`18/19 LPath`, `N1002K = 0.9229`); `(d)` Track 1/2 pathway interactome confidence (`O60566`, `O43684`, `Q12834`, `Q13257`, `Q8IXJ6`, `Q92900`, `P62942`) + ESM-1v window concordance |
| `out/bubr1_plddt_overview.png` | AlphaFold AF-O60566-F1 v6 | Full-length BUBR1 coloured by per-residue pLDDT (`1–736` mean `55.74` vs `737–1050` mean `82.05`), with `K668`, `p.Leu737Ter`, `R814H`, `p.Asn1002Lys`, and `p.Leu1012Pro` marked |
| `out/bubr1_L737Ter_truncation.png` | AF-O60566-F1 v6 | Residues `1–736` retained (teal/navy TPR `62–226`, gold KARD `665–682` with `K668`) vs `737–1050` lost to the stop-gain (salmon pseudokinase domain) |
| `out/bubr1_clobe_N1002_L1012.png` | AF-O60566-F1 v6 | Pseudokinase C-lobe atomic environment: `p.Asn1002Lys` (red; C-cap of α-helix `990–1001` forming 3 H-bonds to `Trp978:N 2.83 Å`, `Val998:O 2.83 Å`, `Asn1004:O 3.14 Å`) vs `p.Leu1012Pro` (orange; core of α-helix `1008–1020`, `12.32 Å` Cα–Cα separation) |
| `out/apcc_mcc_highlight.png` | RCSB `6TLJ` (3.8 Å cryo-EM) | APC/C (grey) inhibited by the MCC — BUBR1 chain S (`19–345`, red), two CDC20 propellers chains Q/R (orange), closed MAD2L1 chain Z (gold) |
| `out/apcc_mcc_complex.png` | RCSB `6TLJ` | Full 18-subunit APC/C–MCC holoenzyme (72,305 atoms), chain-coloured with BUBR1 highlighted in red |
| `out/pp2a_b56_bubr1.png` | RCSB `5JJA` (2.5 Å crystal) | PP2A-B56γ (teal) bound by the BUBR1 KARD LxxIxE peptide (`668–675`, red) with the `Lys668` SIRT2 deacetylation switch highlighted in gold |
| `out/bubr1_kinetochore_complex.png` | RCSB `3SI5` (2.2 Å crystal) | BUBR1 N-terminal TPR domain (`64–215`, blue/salmon) docking to the KNL1/Blinkin peptide (`234–252`, gold) |
| `out/mechanism_schematic.png` | matplotlib (`mechanism_schematic.py`) | Track 1/2 mechanism & therapeutic gating: BUBR1 domains & exon 17/23 NMD gate (`747 nt` spliced / `~10.9 kb` genomic) → amlexanox dual NMD-inhibition + UGA readthrough (`L737W/R/C` Likely Benign) → pathology cascade → 5-tier intervention stack + anti-targets + LINCS firewall (`0 ACCEPT / 2 WEAK / 674 REJECT`) |

Scripts: `make_structural_proof_figure.py`, `render_bubr1.py`, `render_highlight.py`, `render_complexes.py`, `render_gif_frames.py`, `mechanism_schematic.py`.
Structures: `structures/AF-O60566-F1-model_v6.cif`, `AF-O60566-F1-predicted_aligned_error_v6.json`, `6TLJ.cif`, `5JJA.cif`, `3SI5.cif`.

Annotated rotating GIFs (36 frames each, `render_gif_frames.py`):
- `out/bubr1_trunc_rotate.gif` (truncation map)
- `out/clobe_rotate.gif` & `readme/clobe_rotate_readme.gif` (C-lobe `N1002K` H-bond staple vs `L1012P`)
- `out/apcc_mcc_rotate.gif` & `readme/apcc_mcc_rotate_readme.gif` (`PDB 6TLJ` APC/C + MCC)
