"""Small synthetic CircuitGraph generator for future GNN pretrain."""

from __future__ import annotations

import itertools
from typing import Iterator

import numpy as np

from .circuit_graph import CircuitGraph, build_graph

_SINGLE = ("h", "x", "y", "z")


def make_bell() -> CircuitGraph:
    return build_graph({"n_qubits": 2, "gates": [["h", 0], ["cx", 0, 1]]})


def make_random(
    n_qubits: int = 2,
    n_gates: int = 4,
    seed: int = 0,
    p_cx: float = 0.3,
    p_ry: float = 0.2,
) -> CircuitGraph:
    rng = np.random.default_rng(seed)
    gates: list[list[object]] = []
    for _ in range(n_gates):
        r = float(rng.random())
        if n_qubits >= 2 and r < p_cx:
            c, t = rng.choice(n_qubits, size=2, replace=False)
            gates.append(["cx", int(c), int(t)])
        elif r < p_cx + p_ry:
            q = int(rng.integers(0, n_qubits))
            theta = float(rng.uniform(-np.pi, np.pi))
            gates.append(["ry", q, theta])
        else:
            op = str(rng.choice(_SINGLE))
            q = int(rng.integers(0, n_qubits))
            gates.append([op, q])
    return build_graph({"n_qubits": n_qubits, "gates": gates})


def iter_synthetic(
    n: int = 32,
    seed: int = 0,
    include_bell: bool = True,
) -> Iterator[CircuitGraph]:
    if include_bell:
        yield make_bell()
        n -= 1
    for i in range(max(n, 0)):
        nq = 2 if i % 3 else 3
        yield make_random(n_qubits=nq, n_gates=3 + (i % 4), seed=seed + i)


def bell_variants() -> list[CircuitGraph]:
    """A few Bell-like / CX patterns."""
    specs = [
        {"n_qubits": 2, "gates": [["h", 0], ["cx", 0, 1]]},
        {"n_qubits": 2, "gates": [["h", 1], ["cx", 1, 0]]},
        {"n_qubits": 2, "gates": [["x", 0], ["h", 0], ["cx", 0, 1]]},
        {"n_qubits": 3, "gates": [["h", 0], ["cx", 0, 1], ["cx", 1, 2]]},
    ]
    return [build_graph(s) for s in specs]


def enumerate_depth2(n_qubits: int = 2) -> list[CircuitGraph]:
    """Tiny exhaustive set for smoke pretrain toys (depth ≤2 singles + optional cx)."""
    out: list[CircuitGraph] = []
    for g0, g1 in itertools.product(_SINGLE, repeat=2):
        for q0 in range(n_qubits):
            for q1 in range(n_qubits):
                out.append(
                    build_graph(
                        {
                            "n_qubits": n_qubits,
                            "gates": [[g0, q0], [g1, q1]],
                        }
                    )
                )
    return out
