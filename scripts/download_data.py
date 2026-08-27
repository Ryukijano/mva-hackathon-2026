#!/usr/bin/env python3
"""Download the Track 1 files from the gated Hugging Face dataset."""
from __future__ import annotations

import argparse
from pathlib import Path

from mva_hackathon.data.download import download_track1_files


def main():
    parser = argparse.ArgumentParser(description="Download MVA Track 1 files")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).parents[1] / "data",
        help="Destination directory",
    )
    args = parser.parse_args()

    paths = download_track1_files(args.data_dir)
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
