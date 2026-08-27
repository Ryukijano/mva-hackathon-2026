"""Hugging Face dataset download helpers for the MVA hackathon."""
from __future__ import annotations

import os
from pathlib import Path

from huggingface_hub import hf_hub_download, get_token


REPO_ID = "SageBio/mva-hackathon-2026-data"

# Minimum files needed to start Track 1
TRACK1_FILES = [
    "WGS_EX2312012_HGWCNDSX7.vcf.gz",
    "WGS_EX2312012_HGWCNDSX7.vcf.gz.tbi",
    "Challenge_Clinical_Phenotype_1.docx",
]


def get_hf_token() -> str | None:
    """Return HF token from env, or fall back to the Hugging Face CLI cache."""
    token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
    if not token:
        token = get_token()
    return token


def download_track1_files(data_dir: str | Path, token: str | None = None) -> list[Path]:
    """Download the three files needed for Track 1.

    If `token` is None, the Hugging Face Hub library will look for a token
    in the `HF_TOKEN` environment variable or in `~/.cache/huggingface/token`.
    """
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    token = token or get_hf_token()
    if not token:
        raise ValueError(
            "No Hugging Face token found. Set HF_TOKEN or run `huggingface-cli login`. "
            "You must also accept the Data Transfer Agreement on the dataset page."
        )
    downloaded = []
    for fname in TRACK1_FILES:
        path = hf_hub_download(
            repo_id=REPO_ID,
            filename=fname,
            repo_type="dataset",
            local_dir=str(data_dir),
            token=token,
        )
        downloaded.append(Path(path))
    return downloaded
