"""Skip-gram embeddings on a PrimeKG neighbourhood of BUB1B / MVA1."""
from __future__ import annotations

import csv
import random
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

try:
    from tqdm import tqdm
except ImportError:

    def tqdm(iterable, **kwargs):
        return iterable

from mva_hackathon.drug.targets import ANTI_TARGET_GENES, AXIS_TARGETS

SEED_DISEASE_SUBSTR = "mosaic variegated aneuploidy"
DRUG_TYPES = frozenset({"drug", "drug/drug", "compound"})


def _is_drug(node_type: str) -> bool:
    t = node_type.lower()
    return "drug" in t or t in DRUG_TYPES


def _is_seed_name(name: str, node_type: str, *, exclude_anti_targets: bool = False) -> bool:
    n = name.strip()
    t = node_type.lower()
    key = n.upper()
    if key in AXIS_TARGETS or key in ANTI_TARGET_GENES:
        if exclude_anti_targets and key in ANTI_TARGET_GENES:
            return False
        return True
    if SEED_DISEASE_SUBSTR in n.lower() and "disease" in t:
        return True
    return False


def extract_axis_subgraph(
    kg_csv: Path,
    *,
    exclude_anti_targets: bool = False,
) -> tuple[dict[int, tuple[str, str]], list[tuple[int, int]]]:
    """Return node_id -> (name, type) and undirected unique edges in the 1-hop axis graph."""
    seed_ids: set[int] = set()
    with kg_csv.open(newline="") as fh:
        reader = csv.DictReader(fh)
        for row in tqdm(reader, desc="PrimeKG pass 1 (seeds)"):
            if _is_seed_name(row["x_name"], row["x_type"], exclude_anti_targets=exclude_anti_targets):
                seed_ids.add(int(row["x_index"]))
            if _is_seed_name(row["y_name"], row["y_type"], exclude_anti_targets=exclude_anti_targets):
                seed_ids.add(int(row["y_index"]))

    nodes: dict[int, tuple[str, str]] = {}
    edges: set[tuple[int, int]] = set()
    with kg_csv.open(newline="") as fh:
        reader = csv.DictReader(fh)
        for row in tqdm(reader, desc="PrimeKG pass 2 (1-hop)"):
            xi, yi = int(row["x_index"]), int(row["y_index"])
            if xi in seed_ids or yi in seed_ids:
                nodes[xi] = (row["x_name"], row["x_type"])
                nodes[yi] = (row["y_name"], row["y_type"])
                a, b = (xi, yi) if xi < yi else (yi, xi)
                if a != b:
                    edges.add((a, b))
    return nodes, sorted(edges)


class EdgeDataset(Dataset):
    def __init__(self, mapped_edges: list[tuple[int, int]]):
        self.edges = mapped_edges

    def __len__(self) -> int:
        return len(self.edges)

    def __getitem__(self, idx: int) -> tuple[int, int]:
        return self.edges[idx]


class SkipGram(nn.Module):
    def __init__(self, n_nodes: int, dim: int = 64):
        super().__init__()
        self.emb = nn.Embedding(n_nodes, dim)
        nn.init.uniform_(self.emb.weight, -0.1, 0.1)

    def forward(self, src: torch.Tensor, dst: torch.Tensor, neg: torch.Tensor) -> torch.Tensor:
        s = self.emb(src)
        d = self.emb(dst)
        n = self.emb(neg)
        pos = torch.sigmoid((s * d).sum(dim=-1)).clamp(1e-6, 1 - 1e-6)
        neg_score = torch.sigmoid((s.unsqueeze(1) * n).sum(dim=-1)).clamp(1e-6, 1 - 1e-6)
        loss = -torch.log(pos).mean() - torch.log(1 - neg_score).mean()
        return loss


def train_embeddings(
    n_nodes: int,
    mapped_edges: list[tuple[int, int]],
    seed: int,
    device: torch.device,
    dim: int = 64,
    epochs: int = 50,
    batch_size: int = 2048,
    lr: float = 1e-2,
    n_neg: int = 5,
) -> torch.Tensor:
    random.seed(seed)
    torch.manual_seed(seed)
    loader = DataLoader(
        EdgeDataset(mapped_edges),
        batch_size=batch_size,
        shuffle=True,
        drop_last=False,
        num_workers=0,
    )
    model = SkipGram(n_nodes, dim).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    for _ in tqdm(range(epochs), desc=f"skip-gram seed={seed}"):
        for src, dst in loader:
            src = src.to(device)
            dst = dst.to(device)
            neg = torch.randint(0, n_nodes, (src.size(0), n_neg), device=device)
            loss = model(src, dst, neg)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
    return model.emb.weight.detach()


def cosine_to_query(emb: torch.Tensor, query_idx: int) -> torch.Tensor:
    q = emb[query_idx]
    q = q / (q.norm() + 1e-8)
    e = emb / (emb.norm(dim=1, keepdim=True) + 1e-8)
    return e @ q


def rank_drugs(
    nodes: dict[int, tuple[str, str]],
    id_to_local: dict[int, int],
    emb: torch.Tensor,
    query_global: int,
) -> list[dict[str, object]]:
    local_q = id_to_local[query_global]
    sim = cosine_to_query(emb, local_q)
    rows = []
    for gid, (name, ntype) in nodes.items():
        if not _is_drug(ntype):
            continue
        loc = id_to_local[gid]
        rows.append(
            {
                "node_id": gid,
                "name": name,
                "type": ntype,
                "cosine": float(sim[loc]),
            }
        )
    rows.sort(key=lambda r: r["cosine"], reverse=True)
    for i, row in enumerate(rows, start=1):
        row["rank"] = i
        row["pct"] = 100.0 * i / max(len(rows), 1)
    return rows
