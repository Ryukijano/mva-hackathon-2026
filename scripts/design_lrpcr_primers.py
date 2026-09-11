#!/usr/bin/env python3
"""Design long-range PCR primers flanking both BUB1B candidate variants.

Produces an ~11.1 kb amplicon spanning:
  - p.Leu737Ter  (chr15:40209701 T>G)
  - p.Asn1002Lys (chr15:40220612 T>G)
  - intervening het SNV (chr15:40216470 A>G)

Requires: primer3-py, samtools (for faidx), and the GRCh38 reference genome.
"""
import subprocess
import sys
import os
import primer3

REF = os.environ.get(
    "MVA_REF",
    "refs/Homo_sapiens.GRCh38.dna.primary_assembly.fa",
)
SAMTOOLS = os.environ.get("SAMTOOLS", "samtools")

def faidx(region: str) -> str:
    """Extract a region from the reference genome using samtools faidx."""
    out = subprocess.check_output(
        [SAMTOOLS, "faidx", REF, region], text=True
    )
    lines = out.strip().split("\n")
    return "".join(lines[1:])

def design_primers(template: str, side: str, genomic_offset: int) -> list:
    """Design left or right primers from a template sequence."""
    pick_left = side == "left"
    res = primer3.bindings.design_primers(
        {
            "SEQUENCE_ID": side,
            "SEQUENCE_TEMPLATE": template,
            "SEQUENCE_INCLUDED_REGION": [0, len(template)],
        },
        {
            "PRIMER_TASK": "pick_primer_list",
            "PRIMER_PICK_LEFT_PRIMER": 1 if pick_left else 0,
            "PRIMER_PICK_RIGHT_PRIMER": 0 if pick_left else 1,
            "PRIMER_PICK_INTERNAL_OLIGO": 0,
            "PRIMER_OPT_SIZE": 25,
            "PRIMER_MIN_SIZE": 22,
            "PRIMER_MAX_SIZE": 30,
            "PRIMER_OPT_TM": 63.0,
            "PRIMER_MIN_TM": 58.0,
            "PRIMER_MAX_TM": 68.0,
            "PRIMER_MIN_GC": 35.0,
            "PRIMER_MAX_GC": 65.0,
            "PRIMER_NUM_RETURN": 5,
            "PRIMER_MAX_POLY_X": 4,
            "PRIMER_SALT_MONOVALENT": 50.0,
            "PRIMER_DNA_CONC": 50.0,
        },
    )
    key = "LEFT" if pick_left else "RIGHT"
    n = res.get(f"PRIMER_{key}_NUM_RETURNED", 0)
    primers = []
    for i in range(min(5, n)):
        seq = res[f"PRIMER_{key}_{i}_SEQUENCE"]
        tm = res[f"PRIMER_{key}_{i}_TM"]
        gc = res[f"PRIMER_{key}_{i}_GC_PERCENT"]
        pos, length = res[f"PRIMER_{key}_{i}"]
        primers.append({
            "seq": seq, "tm": tm, "gc": gc, "length": length,
            "pos": pos, "genomic_offset": genomic_offset,
        })
    return primers

def main():
    upstream = faidx("15:40209001-40209700")
    downstream = faidx("15:40220613-40221200")

    fwd_primers = design_primers(upstream[-200:], "left", 40209501)
    rev_primers = design_primers(downstream[:200], "right", 40220613)

    print("=== FORWARD PRIMERS (upstream of L737Ter) ===")
    for i, p in enumerate(fwd_primers):
        gs = p["genomic_offset"] + p["pos"]
        print(f"  F{i+1}: 5'-{p['seq']}-3' | Tm={p['tm']:.1f}°C | "
              f"GC={p['gc']:.0f}% | len={p['length']} | "
              f"chr15:{gs}-{gs+p['length']-1}")

    print("\n=== REVERSE PRIMERS (downstream of N1002K) ===")
    for i, p in enumerate(rev_primers):
        g3 = p["genomic_offset"] + p["pos"]
        print(f"  R{i+1}: 5'-{p['seq']}-3' | Tm={p['tm']:.1f}°C | "
              f"GC={p['gc']:.0f}% | len={p['length']} | "
              f"3'-end at chr15:{g3}")

    if fwd_primers and rev_primers:
        f0 = fwd_primers[0]
        r0 = rev_primers[0]
        fwd_start = f0["genomic_offset"] + f0["pos"]
        rev_end = r0["genomic_offset"] + r0["pos"]
        amplicon = rev_end - fwd_start + 1
        print(f"\n=== BEST PAIR AMPLICON (F1 + R1) ===")
        print(f"  Amplicon size: ~{amplicon} bp")
        print(f"  Spans L737Ter (40209701): "
              f"{'YES' if fwd_start < 40209701 < rev_end else 'NO'}")
        print(f"  Spans N1002K (40220612): "
              f"{'YES' if fwd_start < 40220612 < rev_end else 'NO'}")
        print(f"  Spans het SNV (40216470): "
              f"{'YES' if fwd_start < 40216470 < rev_end else 'NO'}")

if __name__ == "__main__":
    main()
