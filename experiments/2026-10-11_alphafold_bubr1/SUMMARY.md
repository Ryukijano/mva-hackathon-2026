# AlphaFold DB model of BUBR1 (UniProt O60566): pLDDT and structural context for p.Leu737Ter and p.Asn1002Lys

**Scope.** This is a protein-level structural check only. No genome, VCF or FASTQ content was read or sent to any API.

## Source and model
- Model: AF-O60566-F1, AlphaFold Monomer v2.0 pipeline, **model_v6** (latest; created 2025-08-01; AF API `latestVersion` 6).
- Downloads (public AlphaFold DB, fetched with a browser-style User-Agent because the default curl UA returned HTTP 403):
  - `https://alphafold.ebi.ac.uk/files/AF-O60566-F1-model_v6.pdb` → `AF-O60566-F1-model_v6.pdb`
  - `https://alphafold.ebi.ac.uk/files/AF-O60566-F1-model_v6.cif` → `AF-O60566-F1-model_v6.cif`
  - API metadata: `https://alphafold.ebi.ac.uk/api/prediction/O60566` → `api.json`
- Global mean pLDDT (API): 63.59. Sequence length 1050, identical to the API sequence.
- The model is a **monomer**. AlphaFold predicts a single chain and cannot evaluate phasing, splicing, NMD, or pathogenicity.

## Mean pLDDT by region
| Region | Mean pLDDT | n |
|---|---|---|
| 1–736 (retained by L737Ter) | 55.74 | 736 |
| 737–1050 (lost by L737Ter) | 82.05 | 314 |
| D-box 224–232 | 54.63 | 9 |
| KNL1-binding 152–185 | 94.10 | 34 |
| Disordered 368–393 | 40.65 | 26 |
| Disordered 456–480 | 46.51 | 25 |
| ±10 around 737 (727–747) | 80.00 | 21 |
| ±10 around 1002 (992–1012) | 91.45 | 21 |
| ±10 around 1012 (1002–1022) | 90.83 | 21 |

Region boundaries were checked against live UniProt annotations: BUB1 N-terminal domain 62–226; KNL1 interaction region 152–185; disordered 368–393 and 456–480; D-box motif 224–232; protein kinase domain 766–1050.

## Residues 1002 and 1012
- Residue 737 is Leu (pLDDT 73.56).
- Residue 1002 is Asn, pLDDT 91.06, which is above 70 and in a confident region.
- Residue 1012 is Leu, pLDDT 95.31.
- CA neighbours within 10 Å (self excluded): 1002 = 20, 1012 = 25. The mean across all residues is 11.6. This is a neighbour count, not computed SASA.
- The CA–CA distance between 1002 and 1012 is **12.32 Å**, so they are **not** within 10 Å of each other in the model.

## Interpretation (monomer model only)
- The truncation at 737 removes the C-terminal kinase domain (766–1050). That region is predicted with high confidence (mean 82.05), so the loss is structured, not disorder.
- The N1002K position sits in a confident, fairly buried part of the lost kinase domain.
- AlphaFold does not model the BUBR1–BUB3, KNL1, or CDC20 complexes or any phasing or splicing effect. Nothing here tests pathogenicity or NMD.

## Files (under `experiments/2026-10-11_alphafold_bubr1/`)
- `AF-O60566-F1-model_v6.pdb`, `AF-O60566-F1-model_v6.cif`, `api.json`
- `plddt_per_residue.csv`: residue, aa, pLDDT, CA neighbours within 10 Å, confident (>70) flag
- `region_summary.txt`: full numeric output
- `analyze_bubr1_af.py`: reproducible analysis script
- `SUMMARY.md`: this file

Nothing was written to `submissions/`, `results/` or `supplement/track1/`. No commit or push was made.
