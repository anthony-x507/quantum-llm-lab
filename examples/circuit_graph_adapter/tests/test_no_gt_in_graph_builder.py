"""Graph builder must reject GT/label kwargs (no leakage)."""

import inspect

import pytest

from examples.circuit_graph_adapter import circuit_graph
from examples.circuit_graph_adapter.circuit_graph import build_graph


@pytest.mark.parametrize(
    "kw",
    ["label", "gold", "gt", "ground_truth", "collapsed_to", "gold_gates", "gt_gates"],
)
def test_rejects_gt_kwargs(kw):
    with pytest.raises(TypeError, match="ground-truth|does not accept"):
        build_graph({"n_qubits": 2, "gates": [["h", 0]]}, **{kw: "collapsed"})


def test_signature_has_no_label_param():
    sig = inspect.signature(build_graph)
    forbidden = {"label", "gold", "gt", "ground_truth", "collapsed_to"}
    assert forbidden.isdisjoint(sig.parameters.keys())


def test_proposal_may_contain_label_but_unused():
    # Labels inside the proposal dict are ignored for structure; must not crash
    # and must not change the graph vs a clean proposal.
    dirty = {
        "n_qubits": 2,
        "gates": [["h", 0], ["cx", 0, 1]],
        "label": "collapsed",
        "collapsed_to": "A",
        "gold": "SHOULD_NOT_MATTER",
    }
    clean = {"n_qubits": 2, "gates": [["h", 0], ["cx", 0, 1]]}
    g1 = build_graph(dirty)
    g2 = build_graph(clean)
    assert g1.to_dict() == g2.to_dict()


def test_forbidden_set_documented():
    assert "label" in circuit_graph._FORBIDDEN_BUILD_KEYS
    assert "gold" in circuit_graph._FORBIDDEN_BUILD_KEYS
