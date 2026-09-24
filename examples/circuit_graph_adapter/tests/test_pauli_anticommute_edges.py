"""Anti-commutation edges between Pauli-typed nodes."""

from examples.circuit_graph_adapter.circuit_graph import build_graph


def test_x_z_anticommute_edge():
    # X on q0 and Z on q0 anti-commute → one edge.
    g = build_graph({"n_qubits": 1, "gates": [["x", 0], ["z", 0]]})
    assert g.nodes[0].pauli == "X"
    assert g.nodes[1].pauli == "Z"
    assert g.edges == [(0, 1)]


def test_x_x_commute_no_edge():
    g = build_graph({"n_qubits": 1, "gates": [["x", 0], ["x", 0]]})
    assert g.edges == []


def test_disjoint_support_commute():
    # X on q0 and Z on q1 → tensor commute (one anti-comm position? wait: XI vs IZ
    # positions: (X,I) commute, (I,Z) commute → 0 anticomm → edge absent.
    g = build_graph({"n_qubits": 2, "gates": [["x", 0], ["z", 1]]})
    assert g.nodes[0].pauli == "XI"
    assert g.nodes[1].pauli == "IZ"
    assert g.edges == []


def test_bell_h_cx_edge():
    # H→XI, CX→ZX: position0 (X,Z) anticomm, position1 (I,X) commute → odd → edge.
    g = build_graph({"n_qubits": 2, "gates": [["h", 0], ["cx", 0, 1]]})
    assert (0, 1) in g.edges
