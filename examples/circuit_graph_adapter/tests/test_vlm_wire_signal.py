"""VLM wire: scaffold text channel usable by VLM (wired_to_vlm=true)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "examples"))

from circuit_graph_adapter.vlm_wire import (  # noqa: E402
    build_vlm_scaffold_signal,
    wire_prompt_for_vlm,
    CHANNEL_TEXT,
)
import circuit_graph_moe_scaffold as sc  # noqa: E402


def test_build_signal_wired_true_no_gt():
    prompt = "Construye un circuito Bell de 2 qubits con H y CX."
    sig = build_vlm_scaffold_signal(prompt, polish=True)
    assert sig.wired_to_vlm is True
    assert sig.channel == CHANNEL_TEXT
    assert sig.weight_peft_injection is False
    assert sig.has_markers is True
    assert sc.SCAFFOLD_BEGIN in sig.prompt_for_vlm
    assert sig.gt_leak is False
    assert sig.prefix_shape == [4, 64]
    assert sig.companion_conditioning["prefix"]["wired_to_vlm"] is True


def test_wire_prompt_only_on_ent():
    prompt = "GHZ de 3 qubits"
    p_ent, m_ent = wire_prompt_for_vlm(prompt, "ent", enabled=True)
    assert m_ent["wired_to_vlm"] is True
    assert sc.SCAFFOLD_BEGIN in p_ent
    p_py, m_py = wire_prompt_for_vlm(prompt, "python", enabled=True)
    assert m_py["wired_to_vlm"] is False
    assert p_py == prompt


def test_disabled_not_wired():
    sig = build_vlm_scaffold_signal("bell", enabled=False)
    assert sig.wired_to_vlm is False
    assert sig.channel == "none"
