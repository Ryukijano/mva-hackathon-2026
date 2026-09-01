"""ESM-1v ensemble masked LLR for UniProt missense substitutions."""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence

import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer

from mva_hackathon.drug.targets import AA20

ESM1V_REPOS = tuple(
    f"facebook/esm1v_t33_650M_UR90S_{i}" for i in range(1, 6)
)

# Meier et al. 2021 ESM-1v: 1022 amino acids + CLS/EOS. HF config is 1026 positions.
ESM1V_MAX_AA = 1022


def load_sequence(fasta_path: str) -> str:
    lines = []
    with open(fasta_path) as fh:
        for line in fh:
            if line.startswith(">"):
                continue
            lines.append(line.strip())
    return "".join(lines)


def _aa_id(tokenizer, aa: str) -> int:
    tid = tokenizer.convert_tokens_to_ids(aa)
    if tid is None or tid == tokenizer.unk_token_id:
        raise KeyError(f"Amino acid {aa!r} missing from tokenizer vocab")
    return int(tid)


def residue_window(pos: int, length: int, max_aa: int = ESM1V_MAX_AA) -> tuple[int, int]:
    """1-based inclusive (start, end) window of at most max_aa residues containing pos."""
    if length <= max_aa:
        return 1, length
    start = max(1, min(pos - max_aa // 2, length - max_aa + 1))
    return start, start + max_aa - 1


def _load_mlm(repo: str, device: torch.device):
    kwargs: dict = {
        "attn_implementation": "eager",
    }
    if device.type == "cuda":
        kwargs["dtype"] = torch.bfloat16
    try:
        model = AutoModelForMaskedLM.from_pretrained(repo, **kwargs)
    except TypeError:
        kwargs.pop("attn_implementation", None)
        kwargs.pop("dtype", None)
        if device.type == "cuda":
            kwargs["torch_dtype"] = torch.bfloat16
        model = AutoModelForMaskedLM.from_pretrained(repo, **kwargs)
    if hasattr(model.config, "_attn_implementation"):
        model.config._attn_implementation = "eager"
    model.to(device)
    model.eval()
    return model


def _score_window(
    model,
    tokenizer,
    window_seq: str,
    local_positions: Sequence[int],
    device: torch.device,
    batch_size: int,
    max_positions: int,
) -> dict[int, dict[str, float]]:
    """Mask 1-based positions inside window_seq; return LLR vs WT for all 20 AA."""
    wt_ids = {_aa_id(tokenizer, aa): aa for aa in AA20}
    encoded = tokenizer(window_seq, return_tensors="pt", add_special_tokens=True)
    input_ids = encoded["input_ids"]
    n_tokens = int(input_ids.size(1))
    if n_tokens > max_positions:
        raise ValueError(
            f"Token length {n_tokens} exceeds max_position_embeddings={max_positions} "
            f"(window_aa={len(window_seq)})"
        )
    results: dict[int, dict[str, float]] = {}
    for start in range(0, len(local_positions), batch_size):
        chunk = list(local_positions[start : start + batch_size])
        batch_ids = input_ids.repeat(len(chunk), 1)
        for row, pos in enumerate(chunk):
            if pos < 1 or pos > len(window_seq):
                raise IndexError(f"local position {pos} outside window of {len(window_seq)}")
            batch_ids[row, pos] = tokenizer.mask_token_id
        out = model(input_ids=batch_ids.to(device))
        logits = out.logits.float()
        for row, pos in enumerate(chunk):
            logp = torch.log_softmax(logits[row, pos], dim=-1)
            wt = window_seq[pos - 1]
            wt_tid = _aa_id(tokenizer, wt)
            scores = {}
            for tid, aa in wt_ids.items():
                scores[aa] = float(logp[tid] - logp[wt_tid])
            results[pos] = scores
    return results


@torch.inference_mode()
def position_llr_batch(
    model,
    tokenizer,
    seq: str,
    positions: Sequence[int],
    device: torch.device,
    batch_size: int = 16,
) -> dict[int, dict[str, float]]:
    """Mask each 1-indexed UniProt position; return LLR(mut) − LLR(WT) for all 20 AA.

    Proteins longer than ESM-1v's 1022-aa limit are scored in a centered window.
    Token layout is [CLS] + residues, so residue i (1-based in the window) is at index i.
    """
    max_positions = int(getattr(model.config, "max_position_embeddings", 1026))
    max_aa = min(ESM1V_MAX_AA, max_positions - 2)
    groups: dict[tuple[int, int], list[int]] = defaultdict(list)
    for pos in positions:
        start, end = residue_window(pos, len(seq), max_aa=max_aa)
        groups[(start, end)].append(pos)

    results: dict[int, dict[str, float]] = {}
    for (start, end), group_pos in groups.items():
        window_seq = seq[start - 1 : end]
        local = [p - start + 1 for p in group_pos]
        print(
            f"  window {start}-{end} aa={len(window_seq)} n_pos={len(group_pos)} "
            f"max_aa={max_aa}",
            flush=True,
        )
        local_scores = _score_window(
            model,
            tokenizer,
            window_seq,
            local,
            device,
            batch_size,
            max_positions,
        )
        for loc, scores in local_scores.items():
            results[loc + start - 1] = scores
    return results


def ensemble_llr(
    seq: str,
    positions: Iterable[int],
    device: torch.device | None = None,
    batch_size: int = 16,
    repos: Sequence[str] = ESM1V_REPOS,
) -> dict[int, dict[str, float]]:
    """Mean LLR across ESM-1v ensemble members."""
    device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
    pos_list = sorted(set(int(p) for p in positions))
    acc: dict[int, dict[str, list[float]]] = {p: {aa: [] for aa in AA20} for p in pos_list}

    tokenizer = None
    for repo in repos:
        print(f"loading {repo}", flush=True)
        tokenizer = tokenizer or AutoTokenizer.from_pretrained(repo)
        model = _load_mlm(repo, device)
        one = position_llr_batch(model, tokenizer, seq, pos_list, device, batch_size)
        for pos, scores in one.items():
            for aa, val in scores.items():
                acc[pos][aa].append(val)
        del model
        if device.type == "cuda":
            torch.cuda.empty_cache()

    mean: dict[int, dict[str, float]] = {}
    for pos, by_aa in acc.items():
        mean[pos] = {aa: sum(vals) / len(vals) for aa, vals in by_aa.items()}
    return mean
