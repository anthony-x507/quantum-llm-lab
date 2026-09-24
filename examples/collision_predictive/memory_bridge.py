"""Bridge: predictive-collision emit → WorkingMemory (video temporal prototype).

ANTI-CONTAM: only model/tool emits enter memory — never gt_* / consequences_gt.
"""
from __future__ import annotations

from typing import Any, Protocol


class MemoryLike(Protocol):
    tool_notes: list[str]
    preds: list[dict]
    history: list[dict]

    def update_from_tool(self, tool_out: dict) -> None: ...


def emit_to_tool_out(emit: dict[str, Any]) -> dict[str, Any]:
    """Map collision emit schema into TrafficPhysicsTool-compatible tool_out."""
    # Refuse BEFORE filtering — accidental gt_* must never enter memory path
    for k in emit.keys():
        if str(k).startswith("gt_") or k in ("gt", "futures", "consequences_gt"):
            raise RuntimeError(f"CONTAMINATION: refusing to put {k} into WorkingMemory")
    safe_keys = ("chosen_action", "predicted_consequence", "is_safe",
                 "partner_of_ego", "any_collision", "note", "source", "predicted_agents")
    out = {k: emit[k] for k in safe_keys if k in emit and k != "predicted_agents"}
    out.setdefault("source", "CollisionPhysicsTool/numpy")
    out["note"] = (
        f"collision layer: action={emit.get('chosen_action')} "
        f"consequence={emit.get('predicted_consequence')} "
        f"is_safe={emit.get('is_safe')}"
    )
    # predicted positions (perceptions) — OK in memory; not GT
    if emit.get("predicted_agents"):
        out["predicted_positions"] = [
            {"id": a["oid"], "x": a["x"], "y": a["y"],
             "vx": a.get("vx"), "vy": a.get("vy")}
            for a in emit["predicted_agents"]
        ]
    # HARD: strip any accidental gt_ keys
    for k in list(out.keys()):
        if k.startswith("gt_") or k in ("gt", "futures", "consequences_gt"):
            raise RuntimeError(f"CONTAMINATION: refusing to put {k} into WorkingMemory")
    return out


def update_memory_from_collision(mem: MemoryLike, emit: dict[str, Any]) -> dict[str, Any]:
    tool_out = emit_to_tool_out(emit)
    mem.update_from_tool(tool_out)
    return tool_out


def distance_note(est_m: float | None, cls: str) -> str:
    """Optional floor-scale distance cue (from distance_est) — not GT meters from sidecar.

    Depth can later scale apparent mass/risk; VLM path deferred. CPU note only.
    """
    if est_m is None:
        return "distance_est: unavailable"
    # nearer → higher collision urgency hint (not a GT label)
    if est_m < 15:
        band = "near"
    elif est_m < 50:
        band = "mid"
    else:
        band = "far"
    return f"distance_est_heuristic: class={cls} band={band} est_m≈{est_m:.1f} (perception; not GT)"
