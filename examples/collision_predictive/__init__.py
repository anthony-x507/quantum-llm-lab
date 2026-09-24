"""Predictive collision layer — hypo actions → physical consequences (CPU).

Separate domain from street-lights video F1 and inverse corridor balls.
Integrates notes with WorkingMemory / floor-scale distance / inverse F1.

Emit: chosen_action + predicted_consequence + is_safe
Distance: consume via distance_consumer stubs (no unmerged-branch import).
"""
from .physics import ACTIONS, predict_emit, predict_cv_no_collision, rollout
from .memory_bridge import (
    emit_to_tool_out,
    update_memory_from_collision,
    distance_note,
    attach_distance_stub,
)
from .distance_consumer import (
    DistanceEstimate,
    proxy_estimates_from_agents,
    enrich_emit_with_distance,
    band_for_est_m,
    urgency_score,
)

__all__ = [
    "ACTIONS",
    "predict_emit",
    "predict_cv_no_collision",
    "rollout",
    "emit_to_tool_out",
    "update_memory_from_collision",
    "distance_note",
    "attach_distance_stub",
    "DistanceEstimate",
    "proxy_estimates_from_agents",
    "enrich_emit_with_distance",
    "band_for_est_m",
    "urgency_score",
]
