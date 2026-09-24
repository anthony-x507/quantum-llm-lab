"""PennyLane CPU tool: unitary_ok, energy (⟨Z⊗Z⟩ / ⟨Z⟩), fingerprint."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np


@dataclass
class PauliToolResult:
    unitary_ok: bool
    energy: float
    fingerprint: str
    probabilities: dict[str, float]
    n_qubits: int
    backend: str
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _apply_gates(qml, gates: list[Any]) -> None:
    for g in gates:
        op = str(g[0]).lower()
        if op == "h":
            qml.Hadamard(wires=int(g[1]))
        elif op == "x":
            qml.PauliX(wires=int(g[1]))
        elif op == "y":
            qml.PauliY(wires=int(g[1]))
        elif op == "z":
            qml.PauliZ(wires=int(g[1]))
        elif op == "cx":
            qml.CNOT(wires=[int(g[1]), int(g[2])])
        elif op == "ry":
            qml.RY(float(g[2]), wires=int(g[1]))
        else:
            raise ValueError(f"unsupported gate: {op}")


def _fingerprint(probs: np.ndarray, n: int) -> str:
    # Round for stability, hash bitstring probs + argmax.
    rounded = np.round(probs, 6)
    dominant = format(int(np.argmax(probs)), f"0{n}b")
    blob = ",".join(f"{p:.6f}" for p in rounded) + f"|{dominant}"
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()[:12]


def run_pauli_tool(proposal: dict[str, Any]) -> PauliToolResult:
    """Execute proposed circuit on PennyLane default.qubit (CPU).

    energy:
      - 1 qubit: ⟨Z⟩
      - ≥2 qubits: ⟨Z⊗Z⊗I...⟩ on wires (0,1)  (documented lab observable)
    """
    backend = "pennylane.default.qubit"
    try:
        import pennylane as qml
    except ImportError as exc:
        return PauliToolResult(
            unitary_ok=False,
            energy=float("nan"),
            fingerprint="error",
            probabilities={},
            n_qubits=int(proposal.get("n_qubits", 0)),
            backend=backend,
            error=f"pennylane missing: {exc}",
        )

    n = int(proposal.get("n_qubits", 2))
    gates = list(proposal.get("gates") or [])
    if n < 1 or n > 8:
        return PauliToolResult(
            unitary_ok=False,
            energy=float("nan"),
            fingerprint="error",
            probabilities={},
            n_qubits=n,
            backend=backend,
            error=f"n_qubits out of range: {n}",
        )

    try:
        dev = qml.device("default.qubit", wires=n)

        @qml.qnode(dev)
        def probs_circuit():
            _apply_gates(qml, gates)
            return qml.probs(wires=range(n))

        @qml.qnode(dev)
        def energy_circuit():
            _apply_gates(qml, gates)
            if n == 1:
                return qml.expval(qml.PauliZ(0))
            obs = qml.PauliZ(0) @ qml.PauliZ(1)
            return qml.expval(obs)

        probs = np.asarray(probs_circuit(), dtype=float)
        energy = float(np.asarray(energy_circuit()))
        sum_ok = abs(float(probs.sum()) - 1.0) < 1e-5
        unitary_ok = bool(sum_ok and np.all(probs >= -1e-9))
        estados = [format(i, f"0{n}b") for i in range(len(probs))]
        prob_map = {s: float(p) for s, p in zip(estados, probs)}
        fp = _fingerprint(probs, n)
        return PauliToolResult(
            unitary_ok=unitary_ok,
            energy=energy,
            fingerprint=fp,
            probabilities=prob_map,
            n_qubits=n,
            backend=backend,
            error=None,
        )
    except Exception as exc:  # noqa: BLE001 — tool must not crash smoke
        return PauliToolResult(
            unitary_ok=False,
            energy=float("nan"),
            fingerprint="error",
            probabilities={},
            n_qubits=n,
            backend=backend,
            error=str(exc),
        )


def bell_proposal() -> dict[str, Any]:
    return {"n_qubits": 2, "gates": [["h", 0], ["cx", 0, 1]]}
