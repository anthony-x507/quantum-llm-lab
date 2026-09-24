"""Bridge: predictive-collision emit → WorkingMemory (video temporal prototype).

ANTI-CONTAM: only model/tool emits enter memory — never gt_* / consequences_gt.
Distance cues: perception estimates only via distance_consumer (stub-safe).
"""
from __future__ import annotations

from typing import Any, Protocol

from distance_consumer import (
    DistanceEstimate,
    enrich_emit_with_distance,
    distance_note as _distance_note_from_est,
    proxy_estimates_from_agents,
)


class MemoryLike(Protocol):
    tool_notes: list[str]
    preds: list[dict]
    history: list[dict]

    def update_from_tool(self, tool_out: dict) -> None: ...


def emit_to_tool_out(emit: dict[str, Any]) -> dict[str, Any]:
    """Map collision emit schema into TrafficPhysicsTool-compatible tool_out."""
    # Refuse BEFORE filtering — accidental gt_* must never enter memory path
    for k in emit.keys():
        if str(k).startswith("gt_") or k in ("gt", "futures", "consequences_gt", "distances_gt"):
            raise RuntimeError(f"CONTAMINATION: refusing to put {k} into WorkingMemory")
    safe_keys = (
        "chosen_action", "predicted_consequence", "is_safe",
        "partner_of_ego", "any_collision", "note", "source", "predicted_agents",
        "distance_note", "distance_notes", "distance_urgency_max",
        "distance_partner_band",
    )
    out = {k: emit[k] for k in safe_keys if k in emit and k != "predicted_agents"}
    out.setdefault("source", "CollisionPhysicsTool/numpy")
    note = (
        f"collision layer: action={emit.get('chosen_action')} "
        f"consequence={emit.get('predicted_consequence')} "
        f"is_safe={emit.get('is_safe')}"
    )
    if emit.get("distance_note"):
        note += f" | {emit['distance_note']}"
    out["note"] = note
    # predicted positions (perceptions) — OK in memory; not GT
    if emit.get("predicted_agents"):
        out["predicted_positions"] = [
            {"id": a["oid"], "x": a["x"], "y": a["y"],
             "vx": a.get("vx"), "vy": a.get("vy")}
            for a in emit["predicted_agents"]
        ]
    # HARD: strip any accidental gt_ keys
    for k in list(out.keys()):
        if k.startswith("gt_") or k in ("gt", "futures", "consequences_gt", "distances_gt"):
            raise RuntimeError(f"CONTAMINATION: refusing to put {k} into WorkingMemory")
    return out


def update_memory_from_collision(mem: MemoryLike, emit: dict[str, Any]) -> dict[str, Any]:
    tool_out = emit_to_tool_out(emit)
    mem.update_from_tool(tool_out)
    return tool_out


def distance_note(est_m: float | None, cls: str) -> str:
    """Back-compat wrapper — prefer DistanceEstimate via distance_consumer."""
    if est_m is None:
        return "distance_est: unavailable"
    est: DistanceEstimate = {
        "oid": "?",
        "cls": cls,
        "est_m": float(est_m),
        "confidence": 0.5,
        "band": "",
        "source": "legacy_distance_note",
    }
    from distance_consumer import band_for_est_m
    est["band"] = band_for_est_m(float(est_m))
    return _distance_note_from_est(est)


def attach_distance_stub(
    emit: dict[str, Any],
    agents: list[dict[str, Any]],
    *,
    estimates: list[DistanceEstimate] | None = None,
) -> dict[str, Any]:
    """Enrich emit with distance urgency (proxy stub if estimates not provided)."""
    ests = estimates if estimates is not None else proxy_estimates_from_agents(agents)
    return enrich_emit_with_distance(emit, ests)
