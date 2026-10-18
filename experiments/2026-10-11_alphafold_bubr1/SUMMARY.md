# AlphaFold DB v6 & Structural Interactome Analysis of BUBR1 (UniProt O60566) and Pathway Partners

**Scope.** Protein-level structural, Predicted Aligned Error (PAE), saturation AlphaMissense, and experimental PDB complex analysis for Track 1 (`p.Leu737Ter`, `p.Asn1002Lys`) and Track 2 (amlexanox/UPF1 NMD gate, UGA readthrough tolerance at codon 737, SIRT2/K668/PP2A-B56γ stabilisation, and FKBP1A rapalog binding). No patient genome, VCF, or FASTQ content was read or sent to any external API.

## 1. Source Models & AlphaFold EBI API Metadata (v6, 2025-08-01)

Public AlphaFold Protein Structure Database v6 models and PAE matrices were retrieved via `alphafold.ebi.ac.uk/api/prediction/<UNIPROT>` (`experiments/2026-10-11_alphafold_bubr1/pathway_partners_af_v6.csv`):

| UniProt | Protein | Role in MVA1 / Track 1–2 Axis | AF Model ID | Length (aa) | Global Mean pLDDT | Frac pLDDT > 90 | Mean PAE (Å) | PAE Rigid Domains (Residues) |
|---|---|---|---|---|---|---|---|---|
| **O60566** | **BUB1B (BUBR1)** | MCC effector core; Track 1 causal locus | `AF-O60566-F1` v6 | 1,050 | **63.59** | 14.7% | 24.78 | **3 rigid domains:** `47–211` (TPR), `406–463` (GLEBS), `755–1043` (pseudokinase) |
| **O43684** | **BUB3** | Obligate GLEBS partner of BUBR1 | `AF-O43684-F1` v6 | 328 | **95.94** | 92.7% | 3.75 | `8–301` (1 rigid WD40 β-propeller) |
| **Q12834** | **CDC20** | APC/C co-activator locked by BUBR1 KEN/ABBA/D-box | `AF-Q12834-F1` v6 | 499 | **84.12** | 61.5% | 15.39 | `164–477` (1 rigid WD40 propeller; disordered N-term `1–163`) |
| **Q13257** | **MAD2L1** | MCC closed C-Mad2 checkpoint partner | `AF-Q13257-F1` v6 | 205 | **93.81** | 90.2% | 4.62 | `8–202` (1 rigid HORMA domain) |
| **Q8IXJ6** | **SIRT2** | Track 2 Prong 1b deacetylase targeting BUBR1 K668 | `AF-Q8IXJ6-F1` v6 | 389 | **81.69** | 60.4% | 13.39 | `57–356` (1 rigid catalytic deacetylase core) |
| **Q92900** | **UPF1 (RENT1)** | Track 2 Prong 1a NMD RNA helicase inhibited by amlexanox | `AF-Q92900-F1` v6 | 1,129 | **72.75** | 41.4% | 20.10 | **2 rigid domains:** `117–282` (CH domain), `290–927` (helicase core) |
| **P62942** | **FKBP1A (FKBP12)** | Track 2 ChEMBL rapalog receptor (`FKBP12–rapamycin–mTOR`) | `AF-P62942-F1` v6 | 108 | **96.25** | 98.1% | 3.42 | `1–108` (1 compact rigid PPIase fold) |

> **Disorder & Multi-Domain Warning (`AF-O60566-F1`):** Full-length BUBR1 has a global mean pLDDT of **63.59** (`37.3%` Very Low `<50`, `13.9%` Low `50–70`, `34.1%` Confident `70–90`, `14.7%` Very High `>90`) and a global mean PAE of **24.78 Å** because its three well-folded domains (`47–211`, `406–463`, `755–1043`) are connected by long, intrinsically disordered linkers collecting linear degron/docking motifs (KEN1, KEN2, D-box, ABBA, KARD). Per-residue pLDDT is stored in the B-factor column of `AF-O60566-F1-model_v6.cif`. Downstream 3D structural comparisons must be restricted to individual ordered domains rather than global whole-protein superposition.

## 2. BUBR1 Region pLDDT & PAE Domain Architecture (`AF-O60566-F1` v6)

| Region / Residue | Residue Span | Mean pLDDT | % Confident (>70) | Intra-Region Mean PAE (Å) | Mean AlphaMissense | Structural Interpretation |
|---|---|---|---|---|---|---|
| Retained by `p.Leu737Ter` | `1–736` (n=736) | **55.74** | 33.0% | — | 0.3989 (29.1% LPath) | Modular N-terminal TPR (`62–226`) + linear checkpoint motifs in flexible linkers |
| Lost by `p.Leu737Ter` | `737–1050` (n=314) | **82.05** | **85.7%** | **8.04** | 0.4341 (32.0% LPath) | Cohesively folded C-terminal region; truncation removes structured domain, not disorder |
| Pseudokinase domain (UniProt) | `766–1050` (n=285) | **83.62** | **88.4%** | **7.69** | 0.4472 (33.6% LPath) | Rigid C-terminal pseudokinase fold (PAE domain 3: `755–1043`) |
| N-terminal TPR domain | `62–226` (n=165) | **86.29** | 89.7% | **7.20** | 0.5612 | Rigid α-helical TPR module (`PDB 2WVI`, `3SI5`) |
| KNL1-binding groove | `152–185` (n=34) | **94.10** | 100.0% | 3.41 | 0.6540 | Core TPR helices docking KNL1 (`PDB 3SI5`) |
| D-box motif | `224–232` (n=9) | **54.63** | 0.0% | — | 0.4510 | Disordered in monomer; folds onto CDC20-R propeller in `PDB 6TLJ` |
| KARD / SIRT2 site (`Lys668`) | `668` | **30.17** | — | — | **0.6648** (13/19 LPath) | Disordered in monomer; folds as first residue of `668–675` LxxIxE peptide in `PDB 5JJA` |
| Stop-gain codon (`Leu737`) | `737` (±10: `727–747`) | **73.56** (80.00) | — | — | **0.1865** (**0/19 LPath**) | Pre-pseudokinase 3₁₀-helix linker; missense-tolerant (`L737W/R/C` all `Likely Benign`) |
| PCS/RPL comparator (`Ala739`) | `739` | **70.94** | — | — | **0.1618** (0/19 LPath) | 5.45 Å from `Leu737`; Frontiers Endo 2026 (`p.Ala739Ser`) shows dosage sensitivity |
| MVA1 comparator (`Arg814`) | `814` | **90.25** | — | — | **0.5622** (10/19 LPath) | α-helix `803–815`; forms 2.73 Å salt bridge with `Asp917` |
| **Proband missense (`Asn1002`)** | `1002` (±10: `992–1012`) | **91.06** (91.45) | — | — | **0.8195** (**18/19 LPath**) | Buried C-cap of α-helix `990–1001`; 20 Cα neighbours within 10 Å (protein mean 11.6) |
| Benign control (`Asn1004`) | `1004` | **89.62** | — | — | **0.1587** (**0/19 LPath**) | Solvent-exposed loop 2 residues from `Asn1002`; ClinVar Benign `p.Asn1004Ser` (`AM = 0.0477`) |
| **MVA1 comparator (`Leu1012`)** | `1012` (±10: `1002–1022`) | **95.31** (90.83) | — | — | **0.7915** (**16/19 LPath**) | Buried hydrophobic core of α-helix `1008–1020`; 25 Cα neighbours within 10 Å |

### Cross-Domain vs Intra-Domain PAE and the `PAE = 2–3 Å` vs `Cα–Cα = 12.32 Å` Distinction
- **Cross-domain PAE (`1–736` ↔ `737–1050`):** `29.05 Å` (`1–736 → 737–1050`) and `27.65 Å` (`737–1050 → 1–736`). The N-terminal scaffold and C-terminal pseudokinase have no fixed relative orientation in the monomer model.
- **Pair (`1002`, `1012`):** `PAE(1002 → 1012) = 3.0 Å` and `PAE(1012 → 1002) = 2.0 Å`, whereas the physical **Euclidean `Cα–Cα` distance is `12.32 Å`**. PAE measures positional alignment uncertainty (in Å), not physical proximity: the low `2–3 Å` PAE proves that AlphaFold places both residues within the same rigid C-lobe subdomain with high relative confidence, while the `12.32 Å` `Cα–Cα` distance establishes that `Asn1002` and `Leu1012` do **not** directly contact each other (`>10 Å`).

## 3. Atomic-Level Environment of `Asn1002` vs `Leu1012` and Why AlphaMissense (`0.9229`) vs ESM-1v (`−0.110`) Diverge

All heavy-atom contacts `<4.0 Å` were extracted from `AF-O60566-F1-model_v6.pdb` (`n1002_l1012_atomic_contacts.csv`):

1. **`Asn1002` is a buried 3-hydrogen-bond α-helix C-cap (`pLDDT = 91.06`, 20 Cα neighbours ≤ 10 Å):**
   - `Asn1002` terminates α-helix `Gly990–Leu1001` and staples it to β-strand `978–980` and the `998–1004` turn via **three intramolecular sidechain–backbone hydrogen bonds**:
     - `Asn1002:OD1` ⋯ `Trp978:N` = **2.83 Å**
     - `Asn1002:ND2` ⋯ `Val998:O` = **2.83 Å**
     - `Asn1002:ND2` ⋯ `Asn1004:O` = **3.14 Å**
   - It also packs directly against `Phe977:CB` (**3.46 Å**) and sits **3.62 Å** from positively charged `Arg999`.
   - **Effect of `p.Asn1002Lys`:** Substituting asparagine with lysine eliminates the `OD1` hydrogen-bond acceptor (severing the 2.83 Å staple to `Trp978:N`), introduces a longer, bulkier `+1` charged sidechain into a buried polar pocket adjacent to `Arg999` (electrostatic repulsion), and perturbs the C-cap of α-helix `990–1001`. It lies **25.7–34.7 Å** away from the pseudokinase triad residues (`Lys795`, `Asp886`, `Asp911`), consistent with a local C-lobe folding/stability defect rather than direct pseudo-active-site disruption.
   - **Why predictors diverge:** Sequence-only ESM-1v scores `N1002K` as mild (`−0.110` in the `29–1050` window; `−0.0625` in the `1–1022` window) because polar `N↔K` exchanges are tolerated across evolutionary alignments in general, whereas structure-aware **AlphaMissense (`0.9229`, Likely Pathogenic; 18/19 substitutions at position 1002 classified `LPath`, mean `0.8195`)** penalizes disruption of the buried 3-H-bond helix C-cap. Conversely, at solvent-exposed **`Asn1004` just two residues away**, AlphaMissense classifies **0/19 substitutions as `LPath`** (`mean = 0.1587`; ClinVar Benign `p.Asn1004Ser = 0.0477`), confirming that AlphaMissense is resolving residue-specific 3D packing rather than flagging the entire C-lobe indiscriminately.

2. **`Leu1012` is a deep hydrophobic core residue (`pLDDT = 95.31`, 25 Cα neighbours ≤ 10 Å):**
   - `Leu1012` sits inside α-helix `Thr1008–Asn1020` (backbone H-bonds to `Thr1008:O` at **2.86 Å** and `Ala1016:N` at **2.86 Å**) and forms cross-helix hydrophobic packing against `His874` (**3.51 Å**), `Ile956` (**3.55 Å**), `Leu867` (**3.63 Å**), `Leu953` (**3.65 Å**), and `Val870` (**3.97 Å**). Introducing a helix-breaking proline (`p.Leu1012Pro`) both breaks the α-helix `1008–1020` H-bond network and evacuates the hydrophobic core, explaining why both ESM-1v (`−1.801` / `−2.158`) and AlphaMissense (`0.8720`) score `L1012P` as severely damaging.

3. **Track 2 Prong 1a Structural Proof — Near-Cognate UGA Readthrough Tolerance at `Leu737`:**
   - Translational readthrough of `p.Leu737Ter` (`UGA`) by near-cognate tRNAs inserts **Trp (`W`), Arg (`R`), or Cys (`C`)** at residue 737.
   - Across all 19 missense substitutions at `Leu737` in AlphaFold DB's AlphaMissense table (`alphamissense_key_residues.csv`), **0/19 are Likely Pathogenic** (`mean AM = 0.1865`; 18/19 `Likely Benign`, 1/19 `Ambiguous`). Specifically, all three UGA readthrough products are classified **Likely Benign**:
     - `p.Leu737Trp` (`L737W`): **0.1503 (`LBen`)**
     - `p.Leu737Arg` (`L737R`): **0.1888 (`LBen`)**
     - `p.Leu737Cys` (`L737C`): **0.3217 (`LBen`)**
   - This provides a quantitative structural rationale that if UPF1-mediated NMD is inhibited (e.g. by amlexanox) and the ribosome reads through the `c.2210T>G` `UGA` stop codon, the resulting missense-substituted full-length BUBR1 polypeptide is predicted to fold benignly at position 737.

## 4. Integration with Experimental Cryo-EM and Crystal Structures (`PDB 6TLJ`, `5JJA`, `3SI5`)

| PDB ID | Method & Resolution | Complex | Resolved BUBR1 (O60566) Residues | Key Atomic Contacts & Relevance to Proband |
|---|---|---|---|---|
| **6TLJ** | Cryo-EM, 3.8 Å | Human APC/C–MCC (`Alfieri et al., Nature 2016`) | Chain S: **`19–210`, `221–233`, `241–323`, `341–345`** (293 aa resolved; **`346–1050` unmodelled**) | Resolves KEN1/MAD2 interface (`res 19–38` to `MAD2` at `3.59 Å`), D-box (`res 224–232` to `CDC20-R` at `4.30 Å`), ABBA/KEN2 (`res 247–345` to `CDC20-Q` at `3.51 Å`), and `APC10`/`APC2` contacts. Confirms `346–1050` is flexibly tethered outside the rigid MCC core. |
| **5JJA** | X-ray, 2.5 Å | Human PP2A-B56γ + BUBR1 KARD (`Wang et al., Nat Commun 2016`) | Chains C & D: **`668–675`** (`KLDPIIED` phosphomimetic LxxIxE peptide) | **`Lys668`** (SIRT2 deacetylation switch, Track 2 Prong 1b) is the first ordered residue of the B56γ-binding peptide. Retained N-terminal to `p.Leu737Ter`. |
| **3SI5** | X-ray, 2.2 Å | Human BUBR1 TPR + KNL1/Blinkin (`Bolanos-Garcia et al., Structure 2011`) | Chains A & B: **UNP `64–215`** (bound to KNL1 peptide `234–252`) | High-confidence N-terminal kinetochore-docking module (`AF v6 pLDDT = 94.1` in `152–185`), retained prior to `p.Leu737Ter`. |
