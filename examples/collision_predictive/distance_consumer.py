"""Consume floor-scale distance estimates as collision-layer inputs (stub-safe).

Integration rule (Anthony LOCK tip-collision-pred 2026-09-24):
  - Prefer estimates from distance_est / tip-distance-danger when available.
  - Do NOT import unmerged distance-branch modules — callers pass estimates in.
  - GT meters from distances_gt.json / consequences_gt.json NEVER accepted.
  - Perception `est_m` (+ optional confidence) only; used as urgency cue, not oracle.

Bands align with distance-danger DANGER ZONE (30–70 m) for tip temporal vision.
"""
from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Protocol, TypedDict


class DistanceEstimate(TypedDict, total=False):
    oid: str
    cls: str
    est_m: float
    confidence: float
    band: str
    source: str  # e.g. "floor_scale_stub" | "distance_est_v2" | "unavailable"


class DistanceProvider(Protocol):
    """Optional provider — tip-distance-danger can satisfy this later without merge."""

    def estimate_for_frame(self, agents: list[dict[str, Any]]) -> list[DistanceEstimate]:
        ...


# Band thresholds (meters). mid splits into danger_zone for 30–70 reinforce.
NEAR_M = 15.0
DANGER_LO_M = 30.0
DANGER_HI_M = 70.0
FAR_M = 100.0


def band_for_est_m(est_m: float | None) -> str:
    if est_m is None:
        return "unknown"
    if est_m < NEAR_M:
        return "near"
    if DANGER_LO_M <= est_m <= DANGER_HI_M:
        return "danger_zone"
    if est_m < DANGER_LO_M:
        return "mid_approach"  # 15–30
    if est_m < FAR_M:
        return "far"
    return "very_far"


def urgency_score(est_m: float | None, *, confidence: float = 1.0) -> float:
    """Higher = more urgent collision attention. Confidence gates weak estimates."""
    if est_m is None or confidence < 0.35:
        return 0.0
    band = band_for_est_m(est_m)
    base = {
        "near": 1.0,
        "mid_approach": 0.75,
        "danger_zone": 0.85,  # LOCK: reinforce 30–70 m attention
        "far": 0.35,
        "very_far": 0.15,
        "unknown": 0.0,
    }.get(band, 0.0)
    return round(base * float(confidence), 4)


def distance_note(est: DistanceEstimate | Mapping[str, Any] | None) -> str:
    """Human/machine cue — perception only; never GT meters."""
    if not est or est.get("est_m") is None:
        return "distance_est: unavailable"
    est_m = float(est["est_m"])
    cls = str(est.get("cls") or "agent")
    band = str(est.get("band") or band_for_est_m(est_m))
    src = str(est.get("source") or "stub")
    conf = est.get("confidence")
    conf_s = f" conf={float(conf):.2f}" if conf is not None else ""
    return (
        f"distance_est_heuristic: class={cls} band={band} "
        f"est_m≈{est_m:.1f}{conf_s} source={src} (perception; not GT)"
    )


def refuse_gt_meters(payload: Mapping[str, Any]) -> None:
    """Hard refuse GT distance / consequence keys on the consumer path."""
    banned = (
        "gt_m", "gt_distance", "distances_gt", "consequences_gt",
        "gt_is_safe", "gt_consequence", "gt_partner", "futures",
    )
    for k in payload.keys():
        ks = str(k)
        if ks.startswith("gt_") or ks in banned:
            raise RuntimeError(
                f"CONTAMINATION: distance_consumer refusing GT key {k}"
            )


def proxy_estimates_from_agents(
    agents: list[dict[str, Any]],
    *,
    px_per_m: float = 2.0,
    ego_id: str = "ego",
) -> list[DistanceEstimate]:
    """CPU synth stand-in when distance_est branch is unavailable.

    Maps arena pixel range from ego → rough meters. This is a *perception proxy*
    for integration tests — NOT GT (GT lives only in sidecars, post-hoc).
    """
    ego = next((o for o in agents if o.get("oid") == ego_id), None)
    if ego is None:
        return []
    ex, ey = float(ego["x"]), float(ego["y"])
    out: list[DistanceEstimate] = []
    for o in agents:
        if o.get("oid") == ego_id:
            continue
        dx = float(o["x"]) - ex
        dy = float(o["y"]) - ey
        dist_px = (dx * dx + dy * dy) ** 0.5
        est_m = dist_px / float(px_per_m)
        band = band_for_est_m(est_m)
        out.append({
            "oid": str(o["oid"]),
            "cls": str(o.get("class", "agent")),
            "est_m": round(est_m, 3),
            "confidence": 0.55,  # honest: proxy, not floor-scale VLM
            "band": band,
            "source": "arena_px_proxy_stub",
        })
    return out


def enrich_emit_with_distance(
    emit: MutableMapping[str, Any],
    estimates: list[DistanceEstimate] | None,
) -> dict[str, Any]:
    """Attach distance urgency cues to emit. Never mutates physics verdict from GT.

    Adds:
      distance_notes: list[str]
      distance_urgency_max: float
      distance_partner_band: optional band of predicted partner
    """
    refuse_gt_meters(emit)
    estimates = estimates or []
    for e in estimates:
        refuse_gt_meters(e)

    notes = [distance_note(e) for e in estimates]
    urgencies = [
        urgency_score(e.get("est_m"), confidence=float(e.get("confidence") or 1.0))
        for e in estimates
    ]
    emit["distance_notes"] = notes
    emit["distance_urgency_max"] = max(urgencies) if urgencies else 0.0

    partner = emit.get("partner_of_ego")
    partner_band = None
    if partner:
        for e in estimates:
            if e.get("oid") == partner:
                partner_band = e.get("band") or band_for_est_m(e.get("est_m"))
                break
    if partner_band is not None:
        emit["distance_partner_band"] = partner_band

    # Composite note for WorkingMemory
    if notes:
        top = max(
            estimates,
            key=lambda e: urgency_score(
                e.get("est_m"), confidence=float(e.get("confidence") or 1.0)
            ),
            default=None,
        )
        emit["distance_note"] = distance_note(top) if top else "distance_est: unavailable"
    else:
        emit["distance_note"] = "distance_est: unavailable"
    return dict(emit)


def integrate_distance_into_prompt_lines(
    estimates: list[DistanceEstimate] | None,
) -> list[str]:
    """Optional prompt appendix — perception bands only; never GT meters/labels."""
    if not estimates:
        return ["Distance cues: unavailable (stub)"]
    lines = ["Distance cues (perception estimates; NOT GT):"]
    for e in estimates:
        refuse_gt_meters(e)
        lines.append("  " + distance_note(e))
    return lines
