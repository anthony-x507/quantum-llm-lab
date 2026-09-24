"""Capa de visión local: frames sintéticos + grounding (demo o MLX VLM)."""

from .synthetic_fall import generate_falling_ball_frames, synthesize_physics_trace
from .grounding import (
    ground_frames,
    GroundingResult,
    augment_vision_circuit_prompt,
    circuit_vision_prompt_suffix,
    circuit_vision_json_only_retry_prompt,
)

__all__ = [
    "generate_falling_ball_frames",
    "synthesize_physics_trace",
    "ground_frames",
    "GroundingResult",
    "augment_vision_circuit_prompt",
    "circuit_vision_prompt_suffix",
    "circuit_vision_json_only_retry_prompt",
]
