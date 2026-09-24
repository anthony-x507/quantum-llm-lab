"""JSON/QASM-lite gates → typed Clifford–Pauli circuit graph.

Nodes = gates with an associated Pauli string. Edges = Pauli anti-commutation
on overlapping support ([Pi, Pj] != 0). Built ONLY from proposed gates — never
from GT labels / gold / eval fields (see build_graph signature + tests).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

ALLOWED_GATES = frozenset({"h", "x", "y", "z", "cx", "ry"})

# Forbidden kwargs that would indicate GT leakage into the graph builder.
_FORBIDDEN_BUILD_KEYS = frozenset(
    {
        "label",
        "gold",
        "gt",
        "ground_truth",
        "collapsed_to",
        "gold_gates",
        "gt_gates",
        "target_label",
        "y_true",
    }
)

# Pauli multiplication table for single-qubit {I,X,Y,Z} (phase ignored for
# commutation checks; we only care about anti-commute vs commute).
_PAULI = ("I", "X", "Y", "Z")


def _pauli_commute(a: str, b: str) -> bool:
    """True if single-qubit Paulis a,b commute (phase-free)."""
    a, b = a.upper(), b.upper()
    if a == "I" or b == "I" or a == b:
        return True
    # Distinct non-I Paulis anti-commute.
    return False


def _tensor_commute(p: str, q: str) -> bool:
    """Commute check for equal-length Pauli strings (tensor product)."""
    if len(p) != len(q):
        raise ValueError(f"Pauli length mismatch: {p!r} vs {q!r}")
    # [P,Q]=0 iff number of anti-commuting positions is even.
    anticomm_positions = 0
    for a, b in zip(p, q):
        if not _pauli_commute(a, b):
            anticomm_positions += 1
    return (anticomm_positions % 2) == 0


def _pad_pauli(local: dict[int, str], n_qubits: int) -> str:
    chars = ["I"] * n_qubits
    for q, p in local.items():
        if q < 0 or q >= n_qubits:
            raise ValueError(f"qubit {q} out of range for n_qubits={n_qubits}")
        chars[q] = p.upper()
    return "".join(chars)


def gate_to_pauli(gate: str, qubits: Sequence[int], n_qubits: int) -> str:
    """Map lab gate → full-width Pauli string (proxy typing for graph edges)."""
    g = gate.lower()
    if g == "h":
        # H conjugates Z↔X; proxy as X on the wire for anti-comm structure.
        return _pad_pauli({int(qubits[0]): "X"}, n_qubits)
    if g == "x":
        return _pad_pauli({int(qubits[0]): "X"}, n_qubits)
    if g == "y":
        return _pad_pauli({int(qubits[0]): "Y"}, n_qubits)
    if g == "z":
        return _pad_pauli({int(qubits[0]): "Z"}, n_qubits)
    if g == "ry":
        return _pad_pauli({int(qubits[0]): "Y"}, n_qubits)
    if g == "cx":
        c, t = int(qubits[0]), int(qubits[1])
        return _pad_pauli({c: "Z", t: "X"}, n_qubits)
    raise ValueError(f"unsupported gate: {gate}")


@dataclass(frozen=True)
class GateNode:
    index: int
    gate: str
    qubits: tuple[int, ...]
    theta: float | None
    pauli: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "gate": self.gate,
            "qubits": list(self.qubits),
            "theta": self.theta,
            "pauli": self.pauli,
        }


@dataclass
class CircuitGraph:
    n_qubits: int
    nodes: list[GateNode] = field(default_factory=list)
    edges: list[tuple[int, int]] = field(default_factory=list)  # undirected pairs (i<j)

    def to_dict(self) -> dict[str, Any]:
        return {
            "n_qubits": self.n_qubits,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [list(e) for e in self.edges],
            "n_nodes": len(self.nodes),
            "n_edges": len(self.edges),
        }


def _parse_gate_list(gates: Iterable[Any], n_qubits: int) -> list[GateNode]:
    nodes: list[GateNode] = []
    for i, raw in enumerate(gates):
        if not isinstance(raw, (list, tuple)) or len(raw) < 2:
            raise ValueError(f"gate entry must be list-like [op, ...], got {raw!r}")
        op = str(raw[0]).lower()
        if op not in ALLOWED_GATES:
            raise ValueError(f"gate not in lab alphabet: {op}")
        theta: float | None = None
        if op == "cx":
            if len(raw) < 3:
                raise ValueError(f"cx needs control,target: {raw}")
            qubits = (int(raw[1]), int(raw[2]))
        elif op == "ry":
            if len(raw) < 3:
                raise ValueError(f"ry needs qubit,theta: {raw}")
            qubits = (int(raw[1]),)
            theta = float(raw[2])
        else:
            qubits = (int(raw[1]),)
        for q in qubits:
            if q < 0 or q >= n_qubits:
                raise ValueError(f"qubit {q} out of range n_qubits={n_qubits}")
        pauli = gate_to_pauli(op, qubits, n_qubits)
        nodes.append(GateNode(index=i, gate=op, qubits=qubits, theta=theta, pauli=pauli))
    return nodes


def _anticomm_edges(nodes: Sequence[GateNode]) -> list[tuple[int, int]]:
    edges: list[tuple[int, int]] = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if not _tensor_commute(nodes[i].pauli, nodes[j].pauli):
                edges.append((i, j))
    return edges


_QASM_GATE_RE = re.compile(
    r"^\s*(h|x|y|z|cx|cnot|ry)\s*"
    r"(?:\(([^)]*)\))?\s*"
    r"q\[(\d+)\](?:\s*,\s*q\[(\d+)\])?\s*;?\s*$",
    re.IGNORECASE,
)


def parse_qasm_lite(qasm: str) -> dict[str, Any]:
    """Minimal OpenQASM-ish subset → proposal dict {n_qubits, gates}."""
    lines = [ln.strip() for ln in qasm.splitlines() if ln.strip() and not ln.strip().startswith("//")]
    n_qubits = 2
    gates: list[list[Any]] = []
    for ln in lines:
        m = re.match(r"qreg\s+\w+\[(\d+)\]", ln, re.I)
        if m:
            n_qubits = int(m.group(1))
            continue
        m = _QASM_GATE_RE.match(ln)
        if not m:
            continue
        op = m.group(1).lower()
        if op == "cnot":
            op = "cx"
        params = m.group(2)
        q0 = int(m.group(3))
        q1 = m.group(4)
        if op == "cx":
            if q1 is None:
                raise ValueError(f"cx needs two qubits: {ln}")
            gates.append(["cx", q0, int(q1)])
        elif op == "ry":
            if params is None:
                raise ValueError(f"ry needs theta: {ln}")
            gates.append(["ry", q0, float(params)])
        else:
            gates.append([op, q0])
    return {"n_qubits": n_qubits, "gates": gates}


def build_graph(
    proposal: dict[str, Any] | None = None,
    *,
    gates: Sequence[Any] | None = None,
    n_qubits: int | None = None,
    qasm: str | None = None,
    **kwargs: Any,
) -> CircuitGraph:
    """Build CircuitGraph from proposed gates / QASM-lite.

    Rejects GT/label kwargs to prevent data leakage into the graph.
    """
    bad = _FORBIDDEN_BUILD_KEYS.intersection(kwargs)
    if bad:
        raise TypeError(
            f"build_graph does not accept ground-truth fields {sorted(bad)}; "
            "graph must be built from proposed gates only"
        )
    if kwargs:
        raise TypeError(f"unexpected kwargs: {sorted(kwargs)}")

    if qasm is not None:
        proposal = parse_qasm_lite(qasm)
    if proposal is None:
        if gates is None or n_qubits is None:
            raise ValueError("provide proposal dict, or gates+n_qubits, or qasm")
        proposal = {"n_qubits": int(n_qubits), "gates": list(gates)}

    if not isinstance(proposal, dict):
        raise TypeError("proposal must be a dict")
    # Ignore non-circuit metadata if present, but never *use* labels as structure.
    n = int(proposal.get("n_qubits", n_qubits or 2))
    g_list = proposal.get("gates") if gates is None else gates
    if g_list is None:
        raise ValueError("proposal missing 'gates'")
    nodes = _parse_gate_list(g_list, n)
    edges = _anticomm_edges(nodes)
    return CircuitGraph(n_qubits=n, nodes=nodes, edges=edges)


def bell_graph() -> CircuitGraph:
    """Canonical Bell: H(0) + CX(0,1)."""
    return build_graph({"n_qubits": 2, "gates": [["h", 0], ["cx", 0, 1]]})


def cx_pair_graph(control: int = 0, target: int = 1, n_qubits: int = 2) -> CircuitGraph:
    return build_graph({"n_qubits": n_qubits, "gates": [["cx", control, target]]})
