"""GNN embedding shape / dtype."""

import numpy as np

from examples.circuit_graph_adapter.circuit_graph import bell_graph, build_graph
from examples.circuit_graph_adapter.gnn_encoder import GNNEncoder, encode


def test_encode_shape_default():
    emb = encode(bell_graph(), embed_dim=64, seed=0)
    assert isinstance(emb, np.ndarray)
    assert emb.shape == (64,)
    assert emb.dtype == np.float32
    assert np.isfinite(emb).all()


def test_encode_shape_custom():
    enc = GNNEncoder(embed_dim=128, n_layers=2, seed=1)
    g = build_graph({"n_qubits": 2, "gates": [["h", 0], ["cx", 0, 1], ["ry", 1, 0.4]]})
    emb = enc.encode(g)
    assert emb.shape == (128,)
    assert float(np.linalg.norm(emb)) > 0.0


def test_empty_graph_zeros():
    enc = GNNEncoder(embed_dim=64, seed=0)
    from examples.circuit_graph_adapter.circuit_graph import CircuitGraph

    emb = enc.encode(CircuitGraph(n_qubits=2, nodes=[], edges=[]))
    assert emb.shape == (64,)
    assert np.allclose(emb, 0.0)
