"""Capa de visión local: frames sintéticos + grounding (demo o MLX VLM)."""

from .synthetic_fall import generate_falling_ball_frames, synthesize_physics_trace
from .grounding import ground_frames, GroundingResult

__all__ = [
    "generate_falling_ball_frames",
    "synthesize_physics_trace",
    "ground_frames",
    "GroundingResult",
]
