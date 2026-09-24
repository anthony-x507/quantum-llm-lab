"""Simple message-passing GNN (torch CPU) → fixed-dim embedding."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from .circuit_graph import CircuitGraph

# Gate one-hot order matches lab alphabet.
_GATE_VOCAB = ("h", "x", "y", "z", "cx", "ry")
_PAULI_CHARS = ("I", "X", "Y", "Z")


def _node_features(graph: "CircuitGraph", max_qubits: int = 3) -> np.ndarray:
    """[n_nodes, F] float32 features: gate one-hot + qubit one-hots + theta + pauli chars."""
    n = len(graph.nodes)
    g_dim = len(_GATE_VOCAB)
    q_dim = max_qubits * 2  # up to 2 qubit slots
    p_dim = max_qubits * len(_PAULI_CHARS)
    feat_dim = g_dim + q_dim + 1 + p_dim
    X = np.zeros((n, feat_dim), dtype=np.float32)
    for i, node in enumerate(graph.nodes):
        if node.gate in _GATE_VOCAB:
            X[i, _GATE_VOCAB.index(node.gate)] = 1.0
        for slot, q in enumerate(node.qubits[:2]):
            if 0 <= q < max_qubits:
                X[i, g_dim + slot * max_qubits + q] = 1.0
        X[i, g_dim + q_dim] = float(node.theta) if node.theta is not None else 0.0
        base = g_dim + q_dim + 1
        pauli = node.pauli.ljust(max_qubits, "I")[:max_qubits]
        for qi, ch in enumerate(pauli):
            if ch in _PAULI_CHARS:
                X[i, base + qi * len(_PAULI_CHARS) + _PAULI_CHARS.index(ch)] = 1.0
    return X


def _adjacency(graph: "CircuitGraph") -> np.ndarray:
    n = len(graph.nodes)
    A = np.eye(n, dtype=np.float32)
    for i, j in graph.edges:
        A[i, j] = 1.0
        A[j, i] = 1.0
    # Degree-normalized (symmetric).
    deg = A.sum(axis=1, keepdims=True).clip(min=1.0)
    return A / np.sqrt(deg @ deg.T)


class GNNEncoder:
    """2–3 layer GraphSAGE-style MP with mean readout → fixed embedding."""

    def __init__(
        self,
        embed_dim: int = 64,
        hidden_dim: int = 64,
        n_layers: int = 3,
        max_qubits: int = 3,
        seed: int = 0,
    ) -> None:
        import torch
        import torch.nn as nn

        self.embed_dim = embed_dim
        self.hidden_dim = hidden_dim
        self.n_layers = n_layers
        self.max_qubits = max_qubits
        self.device = torch.device("cpu")
        self._torch = torch

        # Infer feat dim from a dummy empty feature builder size.
        from .circuit_graph import CircuitGraph, GateNode

        dummy = CircuitGraph(
            n_qubits=2,
            nodes=[GateNode(0, "h", (0,), None, "XI")],
        )
        in_dim = _node_features(dummy, max_qubits=max_qubits).shape[1]

        layers = []
        d_in = in_dim
        for _ in range(n_layers):
            layers.append(nn.Linear(d_in, hidden_dim))
            d_in = hidden_dim
        self.layers = nn.ModuleList(layers)
        self.out = nn.Linear(hidden_dim, embed_dim)
        self.act = nn.ReLU()

        g = torch.Generator(device="cpu")
        g.manual_seed(seed)
        for p in self.parameters():
            if p.dim() >= 2:
                nn.init.xavier_uniform_(p, generator=g)
            else:
                nn.init.zeros_(p)

        self.to(self.device)
        self.eval()

    def parameters(self):
        for m in list(self.layers) + [self.out]:
            yield from m.parameters()

    def to(self, device):
        self.device = device
        self.layers.to(device)
        self.out.to(device)
        return self

    def eval(self):
        self.layers.eval()
        self.out.eval()
        return self

    def encode_torch(self, graph: "CircuitGraph"):
        torch = self._torch
        if len(graph.nodes) == 0:
            return torch.zeros(self.embed_dim, dtype=torch.float32, device=self.device)

        X = torch.from_numpy(_node_features(graph, self.max_qubits)).to(self.device)
        A = torch.from_numpy(_adjacency(graph)).to(self.device)
        H = X
        for lin in self.layers:
            # Message passing: A @ H then linear + residual-ish.
            M = A @ H
            H = self.act(lin(M))
        # Mean pool
        pooled = H.mean(dim=0)
        return self.out(pooled)

    def encode(self, graph: "CircuitGraph") -> np.ndarray:
        torch = self._torch
        with torch.no_grad():
            vec = self.encode_torch(graph)
        return vec.detach().cpu().numpy().astype(np.float32)


# Module-level default encoder (lazy).
_DEFAULT: GNNEncoder | None = None


def get_default_encoder(embed_dim: int = 64, seed: int = 0) -> GNNEncoder:
    global _DEFAULT
    if _DEFAULT is None or _DEFAULT.embed_dim != embed_dim:
        _DEFAULT = GNNEncoder(embed_dim=embed_dim, seed=seed)
    return _DEFAULT


def encode(graph: "CircuitGraph", embed_dim: int = 64, seed: int = 0) -> np.ndarray:
    """API: encode(graph) -> np.ndarray of shape (embed_dim,)."""
    return get_default_encoder(embed_dim=embed_dim, seed=seed).encode(graph)
