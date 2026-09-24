"""Clifford–Pauli circuit graph adapter (frontier).

Build graphs from proposed gates only (no GT labels), encode with a small
torch-CPU GNN, package a VLM-usable scaffold signal for MoE ent lane, and
score with PennyLane tools.
"""

from .circuit_graph import CircuitGraph, GateNode, build_graph, bell_graph
from .gnn_encoder import GNNEncoder, encode
from .conditioning import PrefixConditioner, CrossAttnConditioner
from .pauli_tool import PauliToolResult, run_pauli_tool
from .vlm_wire import (
    VlmScaffoldSignal,
    build_vlm_scaffold_signal,
    wire_prompt_for_vlm,
    CHANNEL_TEXT,
)

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
    "VlmScaffoldSignal",
    "build_vlm_scaffold_signal",
    "wire_prompt_for_vlm",
    "CHANNEL_TEXT",
]

__version__ = "0.1.1"
