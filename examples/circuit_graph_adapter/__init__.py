"""Clifford–Pauli circuit graph adapter (frontier).

Build graphs from proposed gates only (no GT labels), encode with a small
torch-CPU GNN, stub-condition toward a VLM, and score with PennyLane tools.
"""

from .circuit_graph import CircuitGraph, GateNode, build_graph, bell_graph
from .gnn_encoder import GNNEncoder, encode
from .conditioning import PrefixConditioner, CrossAttnConditioner
from .pauli_tool import PauliToolResult, run_pauli_tool

__all__ = [
    "CircuitGraph",
    "GateNode",
    "build_graph",
    "bell_graph",
    "GNNEncoder",
    "encode",
    "PrefixConditioner",
    "CrossAttnConditioner",
    "PauliToolResult",
    "run_pauli_tool",
]

__version__ = "0.1.0"
