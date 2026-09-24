"""Conditioning stubs: graph embedding → prefix tokens / cross-attn keys.

These do NOT wire into a real VLM (Qwen 8B). They expose a clear interface for
future PEFT / prefix-tuning / cross-attention injection.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class PrefixBundle:
    """Fake prefix token embeddings ready for concat on the LLM prompt side."""

    prefix_embeds: np.ndarray  # [n_prefix, d_model]
    n_prefix: int
    d_model: int
    meta: dict[str, Any]


@dataclass
class CrossAttnBundle:
    """Projected keys/values for a cross-attention conditioner block."""

    keys: np.ndarray    # [n_kv, d_model]
    values: np.ndarray  # [n_kv, d_model]
    n_kv: int
    d_model: int
    meta: dict[str, Any]


class PrefixConditioner:
    """Project graph embedding → n_prefix pseudo-token vectors of size d_model."""

    def __init__(self, d_model: int = 128, n_prefix: int = 4, seed: int = 0) -> None:
        self.d_model = d_model
        self.n_prefix = n_prefix
        rng = np.random.default_rng(seed)
        # Lazy proj sized on first call.
        self._proj: np.ndarray | None = None
        self._rng = rng

    def _ensure_proj(self, in_dim: int) -> np.ndarray:
        if self._proj is None or self._proj.shape[0] != in_dim:
            # [in_dim, n_prefix * d_model]
            self._proj = self._rng.normal(
                0.0, 1.0 / max(in_dim, 1) ** 0.5, size=(in_dim, self.n_prefix * self.d_model)
            ).astype(np.float32)
        return self._proj

    def __call__(self, embedding: np.ndarray) -> PrefixBundle:
        emb = np.asarray(embedding, dtype=np.float32).reshape(-1)
        W = self._ensure_proj(emb.shape[0])
        flat = emb @ W
        prefix = flat.reshape(self.n_prefix, self.d_model)
        return PrefixBundle(
            prefix_embeds=prefix,
            n_prefix=self.n_prefix,
            d_model=self.d_model,
            meta={"kind": "prefix", "wired_to_vlm": False},
        )


class CrossAttnConditioner:
    """Project graph embedding → a small set of K/V vectors (stub)."""

    def __init__(self, d_model: int = 128, n_kv: int = 4, seed: int = 1) -> None:
        self.d_model = d_model
        self.n_kv = n_kv
        self._rng = np.random.default_rng(seed)
        self._Wk: np.ndarray | None = None
        self._Wv: np.ndarray | None = None

    def _ensure(self, in_dim: int) -> tuple[np.ndarray, np.ndarray]:
        out = self.n_kv * self.d_model
        if self._Wk is None or self._Wk.shape[0] != in_dim:
            scale = 1.0 / max(in_dim, 1) ** 0.5
            self._Wk = self._rng.normal(0.0, scale, size=(in_dim, out)).astype(np.float32)
            self._Wv = self._rng.normal(0.0, scale, size=(in_dim, out)).astype(np.float32)
        assert self._Wv is not None
        return self._Wk, self._Wv

    def __call__(self, embedding: np.ndarray) -> CrossAttnBundle:
        emb = np.asarray(embedding, dtype=np.float32).reshape(-1)
        Wk, Wv = self._ensure(emb.shape[0])
        keys = (emb @ Wk).reshape(self.n_kv, self.d_model)
        values = (emb @ Wv).reshape(self.n_kv, self.d_model)
        return CrossAttnBundle(
            keys=keys,
            values=values,
            n_kv=self.n_kv,
            d_model=self.d_model,
            meta={"kind": "cross_attn", "wired_to_vlm": False},
        )
