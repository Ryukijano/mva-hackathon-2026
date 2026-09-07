#!/usr/bin/env python3
"""WGS follow-up report: mosaic-aneuploidy landscape + BUB1B read-backed phasing.

Inputs are produced by scripts/slurm/wgs/03_phase_depth.sh:
  * mosdepth 100 kb regional depth (MAPQ>=20)
  * mosdepth genome summary
  * whatshap-phased chr15 VCF
  * whatshap stats text

Outputs (small, committable) in results/wgs_phasing/:
  * aneuploidy_landscape.csv  - per-chromosome normalized depth + deviant bins
  * aneuploidy_bins.csv       - all 100 kb bins with normalized depth / z-score
  * aneuploidy_landscape.png  - genome-wide depth figure (if matplotlib exists)
  * phasing_report.md         - trans/cis verdict for the two BUB1B alleles
"""
from __future__ import annotations

import argparse
import csv
import gzip
import statistics
from pathlib import Path

TARGETS = {40209701: "p.Leu737Ter", 40220612: "p.Asn1002Lys"}
AUTOSOMES = {str(i) for i in range(1, 23)}


def load_regions(path: Path) -> list[tuple[str, int, int, float]]:
    rows = []
    with gzip.open(path, "rt") as fh:
        for line in fh:
            chrom, start, end, depth = line.rstrip("\n").split("\t")[:4]
            rows.append((chrom, int(start), int(end), float(depth)))
    return rows


def robust_z(values: list[float]) -> tuple[float, float]:
    med = statistics.median(values)
    mad = statistics.median(abs(v - med) for v in values) or 1e-9
    return med, 1.4826 * mad


def aneuploidy_landscape(regions, out_dir: Path) -> str:
    auto = [d for c, _, _, d in regions if c in AUTOSOMES]
    med, sigma = robust_z(auto)
    med = med or 1e-9

    bin_rows = []
    per_chrom: dict[str, list[float]] = {}
    for chrom, start, end, depth in regions:
        if chrom not in AUTOSOMES | {"X", "Y"}:
            continue
        norm = depth / med
        z = (depth - med) / sigma
        bin_rows.append((chrom, start, end, depth, norm, z))
        per_chrom.setdefault(chrom, []).append((norm, z))

    chrom_order = {c: i for i, c in enumerate([str(i) for i in range(1, 23)] + ["X", "Y"])}
    chrom_rows = []
    for chrom, vals in sorted(per_chrom.items(), key=lambda kv: chrom_order.get(kv[0], 99)):
        norms = [v[0] for v in vals]
        zs = [v[1] for v in vals]
        deviant = sum(1 for z in zs if abs(z) > 4)
        chrom_rows.append(
            {
                "chrom": chrom,
                "n_bins": len(vals),
                "median_norm_depth": f"{statistics.median(norms):.4f}",
                "mean_norm_depth": f"{statistics.mean(norms):.4f}",
                "frac_bins_absz_gt4": f"{deviant / len(vals):.4f}",
            }
        )

    with open(out_dir / "aneuploidy_landscape.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(chrom_rows[0]))
        w.writeheader()
        w.writerows(chrom_rows)

    with open(out_dir / "aneuploidy_bins.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["chrom", "start", "end", "depth", "norm_depth", "robust_z"])
        w.writerows(bin_rows)

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(16, 4))
        x = 0
        ticks, labels = [], []
        order = [str(i) for i in range(1, 23)] + ["X", "Y"]
        for chrom in order:
            pts = [(x + s / 1e6, z) for c, s, e, d, n, z in bin_rows if c == chrom]
            if not pts:
                continue
            xs, ys = zip(*pts)
            ax.scatter(xs, ys, s=1, c="#444")
            ticks.append(xs[len(xs) // 2])
            labels.append(chrom)
            x = xs[-1] + 20
        ax.axhline(0, color="k", lw=0.5)
        ax.axhline(4, color="r", ls="--", lw=0.7)
        ax.axhline(-4, color="r", ls="--", lw=0.7)
        ax.set_xticks(ticks)
        ax.set_xticklabels(labels, fontsize=7)
        ax.set_xlabel("chromosome (100 kb bins, MAPQ>=20)")
        ax.set_ylabel("robust depth z-score")
        ax.set_title("WGS_EX2312012 mosaic-aneuploidy depth landscape")
        fig.tight_layout()
        fig.savefig(out_dir / "aneuploidy_landscape.png", dpi=160)
    except Exception as exc:  # matplotlib optional
        print(f"figure skipped: {exc}")

    return f"{len(regions)} bins, autosomal median depth {med:.2f}, sigma {sigma:.2f}"


def phasing_report(phased_vcf: Path, stats_path: Path, out_dir: Path) -> str:
    records: dict[int, dict] = {}
    intervening = 0
    block_ps: set[str] = set()
    with open(phased_vcf) as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            f = line.rstrip("\n").split("\t")
            pos = int(f[1])
            fmt = f[8].split(":")
            sample = f[9].split(":")
            gt = sample[fmt.index("GT")] if "GT" in fmt else ""
            ps = sample[fmt.index("PS")] if "PS" in fmt else ""
            if pos in TARGETS:
                records[pos] = {"gt": gt, "ps": ps, "ref": f[3], "alt": f[4]}
            elif 40209701 < pos < 40220612 and "|" in gt:
                intervening += 1
                if ps:
                    block_ps.add(ps)

    lines = ["# BUB1B read-backed phasing report", ""]
    stats_txt = stats_path.read_text() if stats_path.exists() else "n/a"
    lines += ["## whatshap stats (head)", "", "```", stats_txt[:2000], "```", ""]
    lines.append("## Target sites")
    lines.append("")
    for pos, name in TARGETS.items():
        r = records.get(pos)
        if r:
            lines.append(
                f"- 15:{pos} {name} ({r['ref']}>{r['alt']}): GT={r['gt']} PS={r['ps']}"
            )
        else:
            lines.append(f"- 15:{pos} {name}: not phased / absent from phased VCF")
    lines += [
        "",
        f"Intervening phased het sites between the two alleles: {intervening}",
        "",
    ]

    r1, r2 = records.get(40209701), records.get(40220612)
    if r1 and r2 and r1["ps"] and r1["ps"] == r2["ps"] and "|" in r1["gt"] and "|" in r2["gt"]:
        # haplotype index carrying the alt allele at each site (0 or 1)
        alt_pos = [i for i, a in enumerate(r1["gt"].split("|")) if a not in ("0", ".")]
        alt_pos2 = [i for i, a in enumerate(r2["gt"].split("|")) if a not in ("0", ".")]
        trans = alt_pos != alt_pos2
        verdict = (
            "TRANS (alt alleles on opposite haplotypes) — compound-het confirmed by reads"
            if trans
            else "CIS (alt alleles on the same haplotype) — STOP, re-evaluate Track 1 call"
        )
        lines += [f"## Verdict: {verdict}", ""]
    else:
        lines += [
            "## Verdict: UNRESOLVED",
            "",
            "The two sites did not land in a single phased block (or were not phased).",
            "Short reads cannot directly span the ~10.9 kb between them; the call",
            "relies on chaining intervening het variants. Check `phasing_blocks.gtf`",
            "for block boundaries around 40.2 Mb and report phasing as unproven.",
            "",
        ]

    report = "\n".join(lines)
    (out_dir / "phasing_report.md").write_text(report)
    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--regions", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--phased-vcf", type=Path, required=True)
    ap.add_argument("--stats", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    regions = load_regions(args.regions)
    print(aneuploidy_landscape(regions, args.out_dir))
    print(phasing_report(args.phased_vcf, args.stats, args.out_dir))


if __name__ == "__main__":
    main()
