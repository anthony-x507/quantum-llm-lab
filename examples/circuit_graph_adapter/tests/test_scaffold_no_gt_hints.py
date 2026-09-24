"""Scaffold hints must never carry GT / gold / label field names."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "examples"))

import circuit_graph_moe_scaffold as sc  # noqa: E402


_FORBIDDEN = re.compile(
    r"\b(label|gold|gt|ground.?truth|collapsed_to|y_true|target_label)\b",
    re.I,
)


def test_scaffold_hint_has_no_gt_tokens():
    prompt = (
        "Propose a Bell entanglement circuit with n_qubits and gates. "
        "PennyLane JSON only."
    )
    hint = sc.format_scaffold_hint(prompt, polish=True)
    assert sc.SCAFFOLD_BEGIN in hint
    assert _FORBIDDEN.search(hint) is None


def test_inject_only_on_structure_block():
    prompt = "Build a Bell-pair circuit. JSON."
    out = sc.inject_scaffold(prompt)
    assert out.startswith(prompt)
    assert sc.SCAFFOLD_BEGIN in out
    # Idempotent
    assert sc.inject_scaffold(out) == out


def test_build_graph_still_rejects_gt_kwargs():
    from circuit_graph_adapter.circuit_graph import build_graph
    import pytest

    with pytest.raises(TypeError):
        build_graph({"n_qubits": 2, "gates": [["h", 0]]}, label="bell")
