# Addendum (11 Oct 2026, updated 17 Oct 2026): Structural, PAE, AlphaMissense & Protein-LM Context for BUBR1 (`p.Leu737Ter`, `p.Asn1002Lys`, `p.Leu1012Pro`)

**Scope.** Protein-level structural and sequence-model analysis supporting the Track 1 and Track 2 reports (`figures/out/bubr1_alphafold_structural_proof.png`). It does not change any submitted CSV or clinical classification. All coordinates use UniProt `O60566` (`1,050 aa`) and `NM_001211.6` (`23 exons`). No patient genome, VCF, or FASTQ data was sent to external APIs.

---

## 1. AlphaFold DB v6 Monomer (`AF-O60566-F1`), PAE Matrix & Pathway Interactome

Source: `experiments/2026-10-11_alphafold_bubr1/` (`SUMMARY.md`, `region_summary.txt`, `plddt_per_residue.csv`, `alphamissense_key_residues.csv`, `n1002_l1012_atomic_contacts.csv`, `pathway_partners_af_v6.csv`).

| Region / Site | Mean pLDDT | Intra-Region Mean PAE (Å) | Mean AlphaMissense | Structural Summary |
|---|---|---|---|---|
| `1–736` (retained by `p.Leu737Ter`) | **55.74** | — | 0.3989 (29.1% LPath) | Structured TPR (`62–226`, pLDDT `86.3`, PAE `7.20 Å`) + disordered linkers hosting KEN/D-box/ABBA/KARD motifs |
| `737–1050` (lost by `p.Leu737Ter`) | **82.05** | **8.04** | 0.4341 (32.0% LPath) | `85.7%` of residues have `pLDDT > 70`; truncation amputates a cohesively folded domain (`766–1050` mean pLDDT `83.62`, PAE `7.69 Å`), not disorder |
| `Lys668` (SIRT2 deacetylation site) | **30.17** | — | **0.6648** (13/19 LPath) | Disordered in monomer; folds upon binding `PP2A-B56γ` as the N-terminal anchor of KARD `668–675` (`PDB 5JJA`) |
| `Leu737` (`p.Leu737Ter` UGA stop) | **73.56** | — | **0.1865** (**0/19 LPath**) | Pre-pseudokinase 3₁₀-helix linker; **all three near-cognate UGA readthrough insertions are Likely Benign (`L737W = 0.1503`, `L737R = 0.1888`, `L737C = 0.3217`)** |
| `Asn1002` (`p.Asn1002Lys`, proband) | **91.06** | — | **0.8195** (**18/19 LPath**) | Buried C-cap of α-helix `990–1001` (20 Cα neighbours ≤ 10 Å vs protein mean 11.6); `N1002K = 0.9229 (LPath)` |
| `Asn1004` (`p.Asn1004Ser` Benign ref) | **89.62** | — | **0.1587** (**0/19 LPath**) | Solvent-exposed residue 2 aa from `Asn1002`; ClinVar Benign `N1004S = 0.0477 (LBen)` |
| `Leu1012` (`p.Leu1012Pro` MVA1 ref) | **95.31** | — | **0.7915** (**16/19 LPath**) | Deep hydrophobic core of α-helix `1008–1020` (25 Cα neighbours ≤ 10 Å); `L1012P = 0.8720 (LPath)` |

### Key Structural Proofs
1. **PAE (`2–3 Å`) vs Physical Euclidean Distance (`12.32 Å`):** In the `1,050 × 1,050` AlphaFold v6 PAE matrix, `PAE(1002, 1012) = 2–3 Å` (indicating high confidence in their relative positioning within rigid domain 3, `755–1043`), whereas their physical **`Cα–Cα` distance is `12.32 Å`**. Earlier notes in `PROJECT_RECORD.md` that quoted "PAE distance = 3 Å" conflated positional error with physical distance; `Asn1002` and `Leu1012` sit in the same C-lobe subdomain but are **not** in direct atomic contact.
2. **Atomic Mechanism of `p.Asn1002Lys` vs `p.Asn1004Ser`:** In `AF-O60566-F1-model_v6.pdb`, `Asn1002` caps the C-terminus of α-helix `990–1001` through **three intramolecular sidechain–backbone hydrogen bonds** (`Asn1002:OD1`–`Trp978:N` at **2.83 Å**, `Asn1002:ND2`–`Val998:O` at **2.83 Å**, and `Asn1002:ND2`–`Asn1004:O` at **3.14 Å**) and packs against `Phe977` (**3.46 Å**). Replacing `Asn1002` with `Lys` removes the `OD1` H-bond acceptor stapling β-strand `978–980` and places a bulky `+1` sidechain **3.62 Å** from `Arg999`. By contrast, `Asn1004` two residues away projects into solvent (`0/19 LPath`).
3. **Why `PDB 6TLJ` Lacks the Pseudokinase Domain:** Cross-domain PAE between residues `1–736` and `737–1050` is **27.7–29.1 Å**, confirming that the C-terminal pseudokinase is tethered by a flexible linker. Consequently, in the 3.8 Å cryo-EM structure of `APC/C–MCC` (`PDB 6TLJ`), only BUBR1 residues **`19–345`** (KEN1, TPR, D-box `224–232`, ABBA, KEN2 gripping `CDC20-Q`, `CDC20-R`, and `MAD2L1`) are resolved, whereas residues `346–1050` are unmodelled.
4. **Spliced cDNA vs Genomic NMD Distance for `c.2210T>G` (`p.Leu737Ter`):** On `NM_001211.6` (23 exons), `c.2210T>G` lies in **exon 17 of 23**, **747 nt** (`LOFTEE DIST_FROM_LAST_EXON:742`) upstream of the terminal exon 22/23 junction in spliced mRNA coordinates (74 nt upstream of the exon 17/18 junction) and **~10.9 kb (`10,946 bp`)** upstream of exon 23 in GRCh38 genomic coordinates. Both figures describe the same canonical NMD geometry (`>50–55 nt` rule).

---

## 2. ESM-1v 5-Model Ensemble — Window Verification (`29–1050` vs `1–1022`)

Sources: `experiments/2026-08-31_bub1b_computational/outputs/RESULTS.md` (`29–1050` C-terminal-anchored window) and `experiments/2026-10-11_esm1v_fixed/` (`1–1022` N-terminal-anchored window via `residue_window()`). Five `facebook/esm1v_t33_650M_UR90S_{1–5}` models, UniProt `O60566`. More negative LLR indicates stronger evolutionary constraint.

| Substitution / Control | Window `29–1050` (GPU bf16) | Window `29–1050` (CPU fp32) | Window `1–1022` (`2026-10-11_esm1v_fixed`, GPU) | Conclusion |
|---|---|---|---|---|
| **p.Asn1002Lys (`N1002K`)** | **−0.110** | −0.105 | **−0.0625** | Mild in 1D sequence (3rd-mildest in `29–1050`, 2nd-mildest in `1–1022` of 19 AAs at pos 1002) |
| **p.Leu1012Pro (`L1012P`)** | **−1.801** | −1.802 | **−2.1582** | Severely damaging in both windows (`|ΔLLR|` to `N1002K` = **1.69 nats** in `29–1050`, **2.10 nats** in `1–1022`) |
| **p.Arg814His (`R814H`)** | **−1.444** | −1.468 | **−1.4387** | Damaging MVA1 comparator in both windows |
| **p.Lys668Gln (`K668Q`)** | **−0.309** | −0.311 | **−0.3234** | Acetylation-mimic control; mild in both windows |
| **ClinVar B/LB control (n=34 unique)** | Median **−0.161** (mean −0.033) | — | Median **−0.1769** (mean −0.0170) | `N1002K` sits above (milder than) the benign median in both windows (rank 18/34 and 19/34); `L1012P` sits below all 34 B/LB variants |

- **Verification status:** The `2026-10-11_esm1v_fixed` rerun is **complete** and confirms that switching from the `29–1050` window to the `1–1022` window moves `N1002K` by only `+0.048 nats` (`−0.110 → −0.0625`) and widens the gap to `L1012P` from `1.69 nats` to `2.10 nats`. Both pre-registered H1 falsifiers hold under both windowing rules. Across the repository we cite the canonical pre-registered `−0.110` / `−1.801` numbers alongside the `1–1022` verification (`−0.0625` / `−2.1582`).

---

## 3. Literature & Experimental Boundaries

- **Suijkerbuijk et al., *Cancer Res* 2010;70:4891–4900 & *PLoS One* 2012;7:e40632:** Biallelic MVA patient cell lines exhibit low BUBR1 abundance: nonsense alleles undergo NMD transcript loss, while C-terminal pseudokinase missense alleles (`p.Arg814His`, `p.Leu1012Pro`) increase protein turnover (`2–6-fold` reduction in patient cells; rescued by MG132/geldanamycin chase) rather than abolishing catalytic activity (the human pseudokinase is catalytically dispensable).
- **Experimental structures:** `PDB 6TLJ` (APC/C–MCC, 3.8 Å, resolves BUBR1 `19–345`), `PDB 5JJA` (PP2A-B56γ–BUBR1 KARD `668–675`, 2.5 Å), `PDB 3SI5` (BUBR1 TPR `64–215`–KNL1 `234–252`, 2.2 Å), `PDB 2WVI` (human BUBR1 TPR, 1.8 Å), `PDB 6JKK` (*Drosophila* BubR1 kinase domain, 1.85 Å homology proxy; human pseudokinase `766–1050` remains uncrystallised).
- **What these analyses do NOT show:** Monomer structure and *in silico* scores do not prove phasing, splicing, NMD efficiency, or clinical pathogenicity on their own, nor do they substitute for patient-cell Western blot (`BUBR1` steady-state + cycloheximide/MG132 chase), RT-qPCR NMD-rescue assays, or CREST+ micronucleus assays.
