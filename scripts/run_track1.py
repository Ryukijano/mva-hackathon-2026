#!/usr/bin/env python3
"""Track 1 pipeline: VCF -> panel -> score -> pair -> CSV."""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import yaml

from mva_hackathon.data.pheno import parse_docx
from mva_hackathon.panel import all_panel_genes, load_panel
from mva_hackathon.utils.paths import load_paths
from mva_hackathon.variants.filter import keep_candidate
from mva_hackathon.variants.pair import group_variants_by_gene
from mva_hackathon.variants.parse import parse_vep_vcf
from mva_hackathon.variants.score import epcr_from_pair, pair_score, variant_pathogenicity
from mva_hackathon.variants.spliceai import parse_spliceai_vcf, run_spliceai
from mva_hackathon.variants.vep import build_vep_command, run_vep
from mva_hackathon.variants.writer import write_submission


def load_config(path: Path) -> dict:
    with open(path) as fh:
        return yaml.safe_load(fh)


def score_variant(record: dict, config: dict) -> float:
    """Compute a single pathogenicity score from VEP + SpliceAI fields."""
    consequence = record.get("Consequence", "")
    popeve = record.get("popEVE")
    am = record.get("am_pathogenicity")
    splice_delta = record.get("spliceai_delta")
    cadd = record.get("CADD_PHRED")

    return variant_pathogenicity(
        consequence,
        popeve,
        am,
        splice_delta,
        cadd,
        ptv_score=config["scoring"]["ptv_score"],
        missense_pop_weight=config["scoring"]["missense_pop_weight"],
        missense_am_weight=config["scoring"]["missense_am_weight"],
        popeve_severe=config["filter"].get("popeve_severe", -5.056),
    )


def build_rows(
    variants: list[dict],
    pheno: dict,
    panel: dict,
    config: dict,
) -> list[dict]:
    """Generate ranked CSV rows from scored, filtered variants.

    Evaluates all combinations within each gene so a strong compound-het pair
    is never missed by a heuristic window.
    """
    import itertools

    by_gene = group_variants_by_gene(variants)
    rows = []
    for gene, gene_vars in by_gene.items():
        if len(gene_vars) < 2:
            continue
        # Evaluate every pair; product scoring naturally favours a strong
        # truncating allele plus a strong missense/PTV.
        for a, b in itertools.combinations(gene_vars, 2):
            ps = pair_score(a["pathogenicity"], b["pathogenicity"])
            rows.append(
                {
                    "chrom_1": a["CHROM"],
                    "pos_1": a["POS"],
                    "ref_1": a["REF"],
                    "alt_1": a["ALT"],
                    "chrom_2": b["CHROM"],
                    "pos_2": b["POS"],
                    "ref_2": b["REF"],
                    "alt_2": b["ALT"],
                    "pathogenicity": ps,
                    "gene": gene,
                }
            )

    rows.sort(key=lambda r: r["pathogenicity"], reverse=True)
    writer_cfg = config.get("writer", {})
    primary_floor = writer_cfg.get("primary_epcr", 0.5)
    secondary_max = writer_cfg.get("secondary_epcr_max", 0.15)
    out = []
    for rank, row in enumerate(rows[: config.get("max_submission_rows", 10)], start=1):
        primary = rank <= 3
        out.append(
            {
                "chrom_1": row["chrom_1"],
                "pos_1": row["pos_1"],
                "ref_1": row["ref_1"],
                "alt_1": row["alt_1"],
                "chrom_2": row["chrom_2"],
                "pos_2": row["pos_2"],
                "ref_2": row["ref_2"],
                "alt_2": row["alt_2"],
                "epcr": f"{epcr_from_pair(row['pathogenicity'], primary, primary_floor, secondary_max):.6f}",
                "finding_type": "primary" if primary else "secondary",
                "notes": f"{row['gene']} | pair score {row['pathogenicity']:.3f}",
            }
        )
    return out


def run_track1(
    vcf: Path,
    pheno: Path | None,
    output: Path,
    config: dict,
    paths: dict,
    panel: dict,
) -> None:
    """End-to-end Track 1 run."""
    project = Path(paths["project"])
    annotated = project / ".cache" / f"{vcf.stem}.vep.vcf.gz"
    cache_dir = paths["vep"]["dir_cache"]
    plugins_dir = paths["vep"]["dir_plugins"]
    fasta = paths["vep"]["fasta"]

    # 1. VEP annotation
    if not annotated.exists():
        for f in (paths["alpha_missense"], paths["popeve"]):
            if not Path(f).exists():
                raise FileNotFoundError(
                    f"{f} not found. Run scripts/setup_references.sh first."
                )
        if not Path(cache_dir).exists():
            raise FileNotFoundError(
                f"VEP cache not found at {cache_dir}. Run scripts/setup_references.sh first."
            )

        cmd = build_vep_command(
            vcf,
            annotated,
            cache_dir,
            fasta if Path(fasta).exists() else None,
            paths["alpha_missense"],
            paths["popeve"],
            plugins_dir,
        )
        run_vep(cmd)

    # 2. Parse and filter
    variants = list(parse_vep_vcf(annotated))
    candidates = [
        v
        for v in variants
        if keep_candidate(v, config["filter"]["gnomad_max_af"], panel)
        and v.get("SYMBOL") in all_panel_genes(panel)
    ]

    # 3. Score missense/PTV; splice will be merged in next step
    for v in candidates:
        v["pathogenicity"] = score_variant(v, config)

    # 4. SpliceAI on filtered candidate VCF (optional, if FASTA present)
    if Path(fasta).exists():
        candidate_vcf = project / ".cache" / f"{vcf.stem}.candidates.vcf"
        # Write candidates to a minimal VCF for SpliceAI
        _write_candidate_vcf(candidates, candidate_vcf)
        spliceai_out = project / ".cache" / f"{vcf.stem}.spliceai.vcf"
        run_spliceai(candidate_vcf, spliceai_out, fasta)
        splice_scores = parse_spliceai_vcf(spliceai_out)
        for v in candidates:
            key = (v["CHROM"], int(v["POS"]), v["REF"], v["ALT"])
            if key in splice_scores:
                v.update(splice_scores[key])
                v["pathogenicity"] = score_variant(v, config)

    # 5. Parse phenotype
    pheno_data = parse_docx(pheno) if pheno and pheno.exists() else {"hpo_terms": [], "cancer_mentioned": False}

    # 6. Pair and write
    rows = build_rows(candidates, pheno_data, panel, config)
    write_submission(rows, output, proband_id="PROBAND01")
    print(f"Wrote {len(rows)} rows to {output}")


def _write_candidate_vcf(candidates: list[dict], path: Path) -> None:
    """Write a minimal VCF from the candidate list for SpliceAI."""
    path.parent.mkdir(parents=True, exist_ok=True)
    contigs = sorted({str(v["CHROM"]).lstrip("chr") for v in candidates})
    with open(path, "w") as fh:
        fh.write("##fileformat=VCFv4.2\n")
        for c in contigs:
            fh.write(f"##contig=<ID={c}>\n")
        fh.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")
        for v in candidates:
            fh.write(
                f"{v['CHROM']}\t{v['POS']}\t.\t{v['REF']}\t{v['ALT']}\t30\tPASS\t.\n"
            )


def main(argv=None):
    parser = argparse.ArgumentParser(description="MVA Track 1 compound-het pipeline")
    parser.add_argument("--vcf", required=True, type=Path, help="Input proband VCF")
    parser.add_argument("--pheno", type=Path, help="Challenge_Clinical_Phenotype_1.docx")
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--paths", type=Path, default=None)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args(argv)

    project_root = Path(__file__).parents[1]
    config_path = args.config or project_root / "configs" / "config.yaml"
    paths_path = args.paths or project_root / "configs" / "paths" / "aire.yaml"

    config = load_config(config_path)
    paths = load_paths(paths_path)
    panel = load_panel(project_root / "configs" / "panel.yaml")

    run_track1(args.vcf, args.pheno, args.output, config, paths, panel)


if __name__ == "__main__":
    main()
