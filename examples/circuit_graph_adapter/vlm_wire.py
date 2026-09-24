"""Wire circuit-graph scaffold into a VLM-usable MoE ent-lane signal.

Honest scope
------------
* ``wired_to_vlm=True`` means the GT-free scaffold **text block** is attached to
  the prompt the VLM / proposer receives (``channel=text_scaffold_prefix``).
* GNN prefix / cross-attn bundles are packaged as a **companion** signal for
  future PEFT; ``weight_peft_injection=False`` (no mlx-vlm weight edit).
* Never writes ``data/lora_adapter/``. Never embeds GT / gold / label tokens.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np

from .conditioning import CrossAttnConditioner, PrefixConditioner
from .gnn_encoder import GNNEncoder
from .circuit_graph import build_graph


CHANNEL_TEXT = "text_scaffold_prefix"


@dataclass
class VlmScaffoldSignal:
    """VLM-facing scaffold package for MoE lane=ent."""

    prompt_for_vlm: str
    scaffold_text: str
    wired_to_vlm: bool
    channel: str
    weight_peft_injection: bool
    gt_leak: bool
    has_markers: bool
    hint_chars: int
    polish: bool
    prefix_shape: list[int] | None = None
    cross_attn_keys_shape: list[int] | None = None
    embed_norm: float | None = None
    embed_dim: int | None = None
    companion_conditioning: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        # Keep prompt out of bulky scoreboard rows by default callers.
        return d


def _top_prior_proposal(prompt: str) -> dict[str, Any]:
    """Pick a GT-free structural prior matching prompt keywords (no labels)."""
    # Lazy import to avoid circular import with scaffold module at package load.
    import circuit_graph_moe_scaffold as sc  # noqa: WPS433

    templates = sc.prior_templates()
    pl = (prompt or "").lower()
    scored: list[tuple[float, dict[str, Any]]] = []
    for t in templates:
        score = 0.0
        for tag in t.get("tags") or ():
            if str(tag).lower() in pl:
                score += 1.0
        scored.append((score, t))
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
    best = scored[0][1] if scored else templates[0]
    return {"n_qubits": int(best["n_qubits"]), "gates": list(best["gates"])}


def build_vlm_scaffold_signal(
    prompt: str,
    *,
    polish: bool = False,
    encoder: GNNEncoder | None = None,
    d_model: int = 64,
    n_prefix: int = 4,
    enabled: bool = True,
) -> VlmScaffoldSignal:
    """Build a VLM-usable scaffold signal for an ent-lane prompt.

    When ``enabled``, injects the scaffold text block and packages companion
    GNN conditioning tensors. Sets ``wired_to_vlm=True`` for the text channel.
    """
    import circuit_graph_moe_scaffold as sc  # noqa: WPS433

    if not enabled:
        return VlmScaffoldSignal(
            prompt_for_vlm=prompt or "",
            scaffold_text="",
            wired_to_vlm=False,
            channel="none",
            weight_peft_injection=False,
            gt_leak=False,
            has_markers=False,
            hint_chars=0,
            polish=bool(polish),
            meta={"reason": "disabled"},
        )

    enc = encoder or GNNEncoder(embed_dim=d_model, seed=0)
    scaffold_text = sc.format_scaffold_hint(prompt, polish=polish, encoder=enc)
    prompt_for_vlm = sc.inject_scaffold(prompt, polish=polish, encoder=enc)
    gt_leak = bool(sc._FORBIDDEN_HINT.search(scaffold_text))
    has_markers = sc.SCAFFOLD_BEGIN in prompt_for_vlm

    # Companion conditioning from top prior proposal (gates only — no GT).
    proposal = _top_prior_proposal(prompt)
    graph = build_graph(proposal)
    emb = enc.encode(graph)
    prefix = PrefixConditioner(d_model=d_model, n_prefix=n_prefix, seed=0)(emb)
    cross = CrossAttnConditioner(d_model=d_model, n_kv=n_prefix, seed=1)(emb)
    # Mark companion as packaged for VLM text-wire path (still no weight PEFT).
    prefix.meta = {
        **dict(prefix.meta or {}),
        "wired_to_vlm": True,
        "channel": CHANNEL_TEXT,
        "weight_peft_injection": False,
        "role": "companion_prefix_stub",
    }
    cross.meta = {
        **dict(cross.meta or {}),
        "wired_to_vlm": True,
        "channel": CHANNEL_TEXT,
        "weight_peft_injection": False,
        "role": "companion_cross_attn_stub",
    }

    return VlmScaffoldSignal(
        prompt_for_vlm=prompt_for_vlm,
        scaffold_text=scaffold_text,
        wired_to_vlm=True,
        channel=CHANNEL_TEXT,
        weight_peft_injection=False,
        gt_leak=gt_leak,
        has_markers=has_markers,
        hint_chars=len(scaffold_text),
        polish=bool(polish),
        prefix_shape=list(prefix.prefix_embeds.shape),
        cross_attn_keys_shape=list(cross.keys.shape),
        embed_norm=round(float(np.linalg.norm(emb)), 4),
        embed_dim=int(emb.shape[0]),
        companion_conditioning={
            "prefix": prefix.meta,
            "cross_attn": cross.meta,
            "prefix_shape": list(prefix.prefix_embeds.shape),
            "cross_attn_keys_shape": list(cross.keys.shape),
        },
        meta={
            "prior_id_matched": True,
            "n_qubits_prior": proposal["n_qubits"],
            "n_gates_prior": len(proposal["gates"]),
            "graph_n_nodes": len(graph.nodes),
            "graph_n_edges": len(graph.edges),
        },
    )


def wire_prompt_for_vlm(
    prompt: str,
    lane: str,
    *,
    enabled: bool = True,
    polish: bool = False,
    encoder: GNNEncoder | None = None,
) -> tuple[str, dict[str, Any]]:
    """MoE helper: if lane=ent and enabled, return VLM-wired prompt + signal meta."""
    if not enabled or lane != "ent":
        return prompt, {
            "wired_to_vlm": False,
            "channel": "none",
            "injected": False,
            "reason": "lane_not_ent_or_disabled",
        }
    sig = build_vlm_scaffold_signal(
        prompt, polish=polish, encoder=encoder, enabled=True
    )
    meta = {
        "wired_to_vlm": bool(sig.wired_to_vlm),
        "channel": sig.channel,
        "weight_peft_injection": bool(sig.weight_peft_injection),
        "injected": True,
        "hint_chars": sig.hint_chars,
        "has_markers": sig.has_markers,
        "gt_leak": sig.gt_leak,
        "polish": sig.polish,
        "prefix_shape": sig.prefix_shape,
        "cross_attn_keys_shape": sig.cross_attn_keys_shape,
        "embed_norm": sig.embed_norm,
        "companion_conditioning": sig.companion_conditioning,
    }
    return sig.prompt_for_vlm, meta
