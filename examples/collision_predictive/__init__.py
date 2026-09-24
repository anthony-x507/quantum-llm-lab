"""Predictive collision layer — hypo actions + elastic physics (CPU).

Separate domain from street-lights video F1 and inverse corridor balls.
Integrates notes with WorkingMemory / floor-scale distance / inverse F1.
"""
__all__ = ["ACTIONS", "EMIT_SCHEMA_KEYS"]

ACTIONS = ("coast", "brake", "accelerate", "turn_left", "turn_right")
EMIT_SCHEMA_KEYS = ("chosen_action", "predicted_consequence", "is_safe")
