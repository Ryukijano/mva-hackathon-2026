"""Load and resolve AIRE path configs."""
from __future__ import annotations

from pathlib import Path

from omegaconf import OmegaConf


def load_paths(path: str | Path | None = None) -> dict:
    """Load configs/paths/aire.yaml and resolve ${project} etc."""
    if path is None:
        path = Path(__file__).parents[2] / "configs" / "paths" / "aire.yaml"
    cfg = OmegaConf.load(path)
    return OmegaConf.to_container(cfg, resolve=True)
