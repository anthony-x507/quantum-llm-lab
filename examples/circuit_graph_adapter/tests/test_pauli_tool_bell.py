"""PennyLane tool on Bell state."""

import numpy as np

from examples.circuit_graph_adapter.pauli_tool import bell_proposal, run_pauli_tool


def test_bell_unitary_and_energy():
    r = run_pauli_tool(bell_proposal())
    assert r.unitary_ok is True
    assert r.error is None
    assert r.backend.startswith("pennylane")
    # Φ+: P(00)=P(11)=0.5, ⟨ZZ⟩ = +1 for Φ+ ... wait:
    # |Φ+> = (|00>+|11>)/√2 → ZZ|00>=+|00>, ZZ|11>=+|11> → ⟨ZZ⟩=+1
    # Actually Bell Φ+ has ⟨ZZ⟩ = +1. (Ψ- has -1.)
    assert abs(r.energy - 1.0) < 1e-5
    assert abs(r.probabilities.get("00", 0) - 0.5) < 1e-5
    assert abs(r.probabilities.get("11", 0) - 0.5) < 1e-5
    assert abs(r.probabilities.get("01", 0)) < 1e-5
    assert isinstance(r.fingerprint, str) and len(r.fingerprint) == 12


def test_invalid_gate_not_ok():
    r = run_pauli_tool({"n_qubits": 2, "gates": [["not_a_gate", 0]]})
    assert r.unitary_ok is False
    assert r.error
