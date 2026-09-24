"""Bell + CX graph structure."""

from examples.circuit_graph_adapter.circuit_graph import bell_graph, build_graph, cx_pair_graph


def test_bell_nodes_and_gates():
    g = bell_graph()
    assert g.n_qubits == 2
    assert len(g.nodes) == 2
    assert g.nodes[0].gate == "h" and g.nodes[0].qubits == (0,)
    assert g.nodes[1].gate == "cx" and g.nodes[1].qubits == (0, 1)
    assert g.nodes[0].pauli == "XI"
    assert g.nodes[1].pauli == "ZX"


def test_cx_pair():
    g = cx_pair_graph()
    assert len(g.nodes) == 1
    assert g.nodes[0].gate == "cx"
    assert g.nodes[0].pauli == "ZX"


def test_build_from_json_like():
    g = build_graph({"n_qubits": 2, "gates": [["h", 0], ["cx", 0, 1], ["ry", 1, 0.4]]})
    assert len(g.nodes) == 3
    assert g.nodes[2].gate == "ry" and g.nodes[2].theta == 0.4
    assert g.nodes[2].pauli == "IY"


def test_qasm_lite_bell():
    qasm = """
    qreg q[2];
    h q[0];
    cx q[0], q[1];
    """
    g = build_graph(qasm=qasm)
    assert len(g.nodes) == 2
    assert g.nodes[0].gate == "h"
    assert g.nodes[1].gate == "cx"
