"""Unit tests for ESM-1v residue windows and ensemble size guard.

Model loading is mocked: no ESM weights are downloaded or loaded.
"""
from __future__ import annotations

import pytest
import torch

from mva_hackathon.drug.targets import AA20
from mva_hackathon.research import esm1v

BUB1B_LEN = 1050  # O60566 length
MAX_AA = esm1v.ESM1V_MAX_AA  # 1022


@pytest.mark.parametrize("pos", [1, 1022, 1023, 1050])
def test_window_contains_position_and_is_full_length(pos):
    start, end = esm1v.residue_window(pos, BUB1B_LEN)
    assert start <= pos <= end
    assert end - start + 1 == MAX_AA


def test_window_rule_boundaries():
    assert esm1v.residue_window(1, BUB1B_LEN) == (1, 1022)
    assert esm1v.residue_window(1022, BUB1B_LEN) == (1, 1022)
    assert esm1v.residue_window(1023, BUB1B_LEN) == (29, 1050)
    assert esm1v.residue_window(1050, BUB1B_LEN) == (29, 1050)


def test_short_protein_uses_whole_sequence():
    assert esm1v.residue_window(5, 100) == (1, 100)


class _FakeTokenizer:
    def from_pretrained(self, repo):  # pragma: no cover - trivial
        return object()


def _fake_scores(model, tokenizer, seq, positions, device, batch_size):
    return {p: {aa: 0.0 for aa in AA20} for p in positions}


@pytest.fixture
def mocked_esm(monkeypatch):
    monkeypatch.setattr(esm1v.AutoTokenizer, "from_pretrained", lambda repo: object())
    monkeypatch.setattr(esm1v, "_load_mlm", lambda repo, device: object())
    monkeypatch.setattr(esm1v, "position_llr_batch", _fake_scores)
    return monkeypatch


def _seq(n=20):
    return "A" * n


def test_ensemble_raises_with_fewer_than_five_models(mocked_esm):
    with pytest.raises(RuntimeError, match="3 models loaded, expected 5"):
        esm1v.ensemble_llr(
            _seq(), [1, 2], device=torch.device("cpu"), repos=esm1v.ESM1V_REPOS[:3]
        )


def test_ensemble_allow_partial_works(mocked_esm):
    out = esm1v.ensemble_llr(
        _seq(),
        [1, 2],
        device=torch.device("cpu"),
        repos=esm1v.ESM1V_REPOS[:3],
        allow_partial=True,
    )
    assert set(out) == {1, 2}
    assert set(out[1]) == set(AA20)


def test_ensemble_full_five_models_passes(mocked_esm):
    out = esm1v.ensemble_llr(_seq(), [1], device=torch.device("cpu"))
    assert set(out) == {1}
    assert len(esm1v.ESM1V_REPOS) == 5
