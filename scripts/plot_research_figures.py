#!/usr/bin/env python3
"""Publication figures for ESM-1v missense LLR and PrimeKG drug ranks."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OKABE = {
    "blue": "#0072B2",
    "orange": "#E69F00",
    "green": "#009E73",
    "red": "#D55E00",
    "purple": "#CC79A7",
    "grey": "#999999",
}

plt.rcParams.update(
    {
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "font.family": "sans-serif",
        "font.size": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "legend.fontsize": 9,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)


def _bold_legend(ax) -> None:
    leg = ax.get_legend()
    if leg is None:
        return
    for text in leg.get_texts():
        text.set_fontweight("bold")


def plot_named_llr(named_json: Path, out: Path) -> None:
    rows = json.loads(named_json.read_text())
    labels = [r["label"] for r in rows]
    vals = [r["llr"] for r in rows]
    colors = []
    for lab in labels:
        if lab == "N1002K":
            colors.append(OKABE["red"])
        elif lab in {"L1012P", "R814H"}:
            colors.append(OKABE["blue"])
        else:
            colors.append(OKABE["grey"])
    fig, ax = plt.subplots(figsize=(3.4, 3.2))
    ax.bar(labels, vals, color=colors, width=0.7, edgecolor="black", linewidth=0.4)
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_ylabel("ESM-1v ensemble LLR (nats)")
    ax.set_title("BUBR1 missense effect (O60566)")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(out.with_suffix(".pdf"))
    fig.savefig(out.with_suffix(".png"))
    plt.close(fig)


def plot_clobe_trace(llr_csv: Path, out: Path) -> None:
    df = pd.read_csv(llr_csv)
    window = df[(df["pos"] >= 990) & (df["pos"] <= 1030)]
    worst = window.loc[~window["is_wt"]].groupby("pos")["llr_ensemble_mean"].min()
    fig, ax = plt.subplots(figsize=(4.8, 2.9))
    ax.plot(
        worst.index,
        worst.values,
        color=OKABE["blue"],
        linewidth=1.8,
        label="Min LLR (any AA)",
    )
    alleles = [
        (1002, "K", "N1002K", OKABE["red"]),
        (1012, "P", "L1012P", OKABE["orange"]),
    ]
    for pos, mut, lab, color in alleles:
        row = window[(window["pos"] == pos) & (window["mut"] == mut)]
        if row.empty:
            continue
        val = float(row["llr_ensemble_mean"].iloc[0])
        ax.scatter([pos], [val], color=color, s=36, zorder=5, edgecolor="black", linewidth=0.4)
        ax.axvline(pos, color=color, linestyle="--", linewidth=1.2, alpha=0.85)
        ax.annotate(
            f"{lab}\n{val:.2f}",
            xy=(pos, val),
            xytext=(6, 8),
            textcoords="offset points",
            fontsize=8,
            fontweight="bold",
            color=color,
        )
    ax.set_xlabel("UniProt O60566 position")
    ax.set_ylabel("ESM-1v LLR (nats)")
    ax.legend(loc="lower left", prop={"weight": "bold"})
    _bold_legend(ax)
    fig.tight_layout()
    fig.savefig(out.with_suffix(".pdf"))
    fig.savefig(out.with_suffix(".png"))
    plt.close(fig)


WATCH = [
    "fedratinib",
    "baricitinib",
    "ruxolitinib",
    "tofacitinib",
    "sirolimus",
    "everolimus",
    "temsirolimus",
    "ridaforolimus",
    "tocilizumab",
    "bos172722",
    "cambinol",
    "omaveloxolone",
]


def _drug_color(name: str) -> str:
    n = name.lower()
    if "bos172722" in n or "barasertib" in n:
        return OKABE["red"]
    if any(k in n for k in ("sirolimus", "everolimus", "temsirolimus", "ridaforolimus")):
        return OKABE["orange"]
    if any(
        k in n
        for k in ("fedratinib", "baricitinib", "ruxolitinib", "tofacitinib", "upadacitinib", "filgotinib")
    ):
        return OKABE["blue"]
    return OKABE["grey"]


def plot_drug_ranks(mean_csv: Path, out: Path, title: str) -> None:
    df = pd.read_csv(mean_csv)
    df["name_l"] = df["name"].str.lower()
    n_drugs = len(df)
    hits = []
    seen = set()
    for needle in WATCH:
        sub = df[df["name_l"] == needle]
        if sub.empty:
            continue
        row = sub.iloc[0]
        if row["name"] in seen:
            continue
        seen.add(row["name"])
        hits.append(row)
    if not hits:
        return
    plot_df = pd.DataFrame(hits).sort_values("mean_rank")
    fig, ax = plt.subplots(figsize=(4.8, 3.8))
    y = range(len(plot_df))
    colors = [_drug_color(n) for n in plot_df["name_l"]]
    ax.barh(list(y), plot_df["mean_rank"], color=colors, edgecolor="black", linewidth=0.4)
    ax.set_yticks(list(y), plot_df["name"])
    ax.invert_yaxis()
    ax.set_xlabel(f"Mean rank among {n_drugs} drugs (1 = closest; 3 seeds)")
    ax.set_title(title)
    ax.axvline(0.1 * n_drugs, color=OKABE["grey"], linestyle=":", linewidth=1.0, label="Top 10%")
    ax.legend(loc="lower right", prop={"weight": "bold"})
    _bold_legend(ax)
    fig.tight_layout()
    fig.savefig(out.with_suffix(".pdf"))
    fig.savefig(out.with_suffix(".png"))
    plt.close(fig)


def plot_clinvar_blb(scores_csv: Path, named_json: Path, out: Path) -> None:
    df = pd.read_csv(scores_csv)
    blb = df[df["bucket"] == "B/LB"].drop_duplicates("label")
    if blb.empty:
        return
    named = {r["label"]: r["llr"] for r in json.loads(named_json.read_text())} if named_json.exists() else {}
    fig, ax = plt.subplots(figsize=(3.6, 3.4))
    rng = np.random.default_rng(0)
    x = rng.uniform(-0.12, 0.12, size=len(blb))
    ax.scatter(
        x,
        blb["llr"],
        color=OKABE["grey"],
        s=22,
        alpha=0.85,
        edgecolor="black",
        linewidth=0.3,
        label="ClinVar B/LB",
        zorder=3,
    )
    median = float(blb["llr"].median())
    ax.axhline(median, color=OKABE["grey"], linestyle="--", linewidth=1.2, label=f"B/LB median ({median:.2f})")
    if "N1002K" in named:
        ax.axhline(
            named["N1002K"],
            color=OKABE["red"],
            linewidth=1.6,
            label=f"N1002K ({named['N1002K']:.2f})",
        )
    if "L1012P" in named:
        ax.axhline(
            named["L1012P"],
            color=OKABE["blue"],
            linewidth=1.4,
            label=f"L1012P ({named['L1012P']:.2f})",
        )
    ax.set_xlim(-0.6, 0.6)
    ax.set_xticks([])
    ax.set_ylabel("ESM-1v ensemble LLR (nats)")
    ax.set_title("N1002K vs ClinVar B/LB missenses")
    ax.legend(loc="best", prop={"weight": "bold"})
    _bold_legend(ax)
    fig.tight_layout()
    fig.savefig(out.with_suffix(".pdf"))
    fig.savefig(out.with_suffix(".png"))
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/2026-08-31_bub1b_computational/outputs"),
    )
    args = ap.parse_args()
    figdir = args.out_dir / "figures"
    figdir.mkdir(parents=True, exist_ok=True)

    named = args.out_dir / "esm1v_named_missenses.json"
    if named.exists():
        plot_named_llr(named, figdir / "fig1_esm1v_named_llr")
    llr = args.out_dir / "esm1v_bub1b_llr.csv"
    if llr.exists():
        plot_clobe_trace(llr, figdir / "fig2_esm1v_clobe_trace")
    ranks = args.out_dir / "primekg_drug_ranks_mean.csv"
    if ranks.exists():
        plot_drug_ranks(
            ranks,
            figdir / "fig3_primekg_watched_drugs",
            "PrimeKG E2 (axis + anti-target seeds)",
        )
    e2b = args.out_dir / "e2b_no_antitarget" / "primekg_drug_ranks_mean.csv"
    if e2b.exists():
        plot_drug_ranks(
            e2b,
            figdir / "fig4_primekg_e2b_no_antitarget",
            "PrimeKG E2b (anti-target seeds dropped)",
        )
    clinvar = args.out_dir / "e1c_clinvar" / "esm1v_clinvar_missense_scores.csv"
    if clinvar.exists():
        plot_clinvar_blb(
            clinvar,
            args.out_dir / "esm1v_named_missenses.json",
            figdir / "fig5_esm1v_clinvar_blb",
        )
    print(f"figures in {figdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
