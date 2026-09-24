"""Physics-law gate for inverse-planning predictions (Fase 1).

Predicted futures must obey simple 2D kinematics (constant velocity with
optional elastic wall bounce). Teleports / wall-phasing / unbound jumps
→ physics_fail even if Euclidean position is within tolerance of GT.
"""
from __future__ import annotations

from typing import Any

import numpy as np

# Arena matches generate_passive.py (pixels)
ARENA_W = 240
ARENA_H = 180
MARGIN = 8  # object radius / wall inset used by generator
MAX_SPEED_PX = 18.0  # hard cap used in generator sampling
TELEPORT_MULT = 2.5  # jump > TELEPORT_MULT * max_expected → teleport fail


def _reflect_step(x: float, y: float, vx: float, vy: float, dt: float = 1.0) -> tuple[float, float, float, float]:
    """One Euler step with elastic bounce on arena walls (inset MARGIN)."""
    nx = x + vx * dt
    ny = y + vy * dt
    lo_x, hi_x = float(MARGIN), float(ARENA_W - MARGIN)
    lo_y, hi_y = float(MARGIN), float(ARENA_H - MARGIN)
    if nx < lo_x:
        nx = lo_x + (lo_x - nx)
        vx = -vx
    elif nx > hi_x:
        nx = hi_x - (nx - hi_x)
        vx = -vx
    if ny < lo_y:
        ny = lo_y + (lo_y - ny)
        vy = -vy
    elif ny > hi_y:
        ny = hi_y - (ny - hi_y)
        vy = -vy
    # clamp residual
    nx = float(np.clip(nx, lo_x, hi_x))
    ny = float(np.clip(ny, lo_y, hi_y))
    return nx, ny, vx, vy


def extrapolate_cv(
    history: list[dict[str, Any]],
    k: int,
) -> dict[str, Any]:
    """Constant-velocity (+ wall bounce) foresight from last two frames.

    history: list of object state dicts with keys x,y,vx,vy,shape,color,oid
             ordered oldest→newest; last entry is frame N.
    Returns predicted state at N+k (same schema, no GT).
    """
    if not history:
        raise ValueError("empty history")
    cur = dict(history[-1])
    if len(history) >= 2:
        prev = history[-2]
        vx = float(cur.get("vx", cur["x"] - prev["x"]))
        vy = float(cur.get("vy", cur["y"] - prev["y"]))
    else:
        vx = float(cur.get("vx", 0.0))
        vy = float(cur.get("vy", 0.0))
    x, y = float(cur["x"]), float(cur["y"])
    for _ in range(int(k)):
        x, y, vx, vy = _reflect_step(x, y, vx, vy, dt=1.0)
    out = dict(cur)
    out.update({"x": x, "y": y, "vx": vx, "vy": vy})
    return out


def check_physics(
    history: list[dict[str, Any]],
    predicted: dict[str, Any],
    k: int,
    *,
    pos_tol: float = 6.0,
) -> dict[str, Any]:
    """Return physics verdict for one object prediction.

    Fail modes:
      - teleport: |pred - last| >> k * |v| * TELEPORT_MULT (or >> k*MAX_SPEED)
      - wall_phase: pred outside arena inset (object left the plane / flew out)
      - inconsistent_kinematics: pred far from any CV+bounce rollout AND
        displacement not explainable by speed bound (caught as teleport mostly)
      - flying: reserved (top-down 2D; used if z!=0 or y inverted absurdly)

    Note: being close to GT is IRRELEVANT here — we only check kinematics.
    """
    if not history:
        return {"physics_ok": False, "fail_reason": "no_history", "physics_fail": True}

    last = history[-1]
    px, py = float(predicted["x"]), float(predicted["y"])
    lx, ly = float(last["x"]), float(last["y"])

    # wall / flying out of arena
    lo_x, hi_x = MARGIN - 1.0, ARENA_W - MARGIN + 1.0
    lo_y, hi_y = MARGIN - 1.0, ARENA_H - MARGIN + 1.0
    if px < lo_x or px > hi_x or py < lo_y or py > hi_y:
        return {
            "physics_ok": False,
            "fail_reason": "wall_phase_or_flying",
            "physics_fail": True,
            "pred": [px, py],
        }

    # expected max travel
    if len(history) >= 2:
        prev = history[-2]
        speed = float(np.hypot(last["x"] - prev["x"], last["y"] - prev["y"]))
    else:
        speed = float(np.hypot(last.get("vx", 0.0), last.get("vy", 0.0)))
    speed = max(speed, float(np.hypot(last.get("vx", 0.0), last.get("vy", 0.0))))
    max_expected = max(speed, 0.5) * float(k) * TELEPORT_MULT
    max_hard = MAX_SPEED_PX * float(k) * TELEPORT_MULT
    jump = float(np.hypot(px - lx, py - ly))
    if jump > max(max_expected, max_hard):
        return {
            "physics_ok": False,
            "fail_reason": "teleport",
            "physics_fail": True,
            "jump": jump,
            "max_expected": max_expected,
        }

    # consistency vs CV+bounce rollout (soft: large miss ≠ auto-fail if speed-ok;
    # only flag if pred is nowhere near rollout AND jump is suspicious — already
    # covered. Extra: if k>=1 and jump≈0 while speed high and no bounce expected
    # we still allow (could be oscillating). Keep gate strict on teleport/phase.
    cv = extrapolate_cv(history, k)
    dist_cv = float(np.hypot(px - cv["x"], py - cv["y"]))
    # If prediction claims a path far from CV but still within speed bound,
    # mark kinematics_warn but NOT physics_fail (model may use different law).
    # Strict fail only for teleport / flying / wall_phase.
    return {
        "physics_ok": True,
        "fail_reason": None,
        "physics_fail": False,
        "dist_to_cv_rollout": dist_cv,
        "cv_near": dist_cv <= pos_tol * 2,
    }


def check_scene_physics(
    history_objects: list[list[dict[str, Any]]],
    predicted_objects: list[dict[str, Any]],
    k: int,
) -> dict[str, Any]:
    """history_objects[i] = history for object i; predicted_objects aligned by oid."""
    by_oid_hist = {}
    for hist in history_objects:
        if hist:
            by_oid_hist[hist[-1]["oid"]] = hist
    fails = []
    details = []
    for pred in predicted_objects:
        oid = pred["oid"]
        hist = by_oid_hist.get(oid, [])
        d = check_physics(hist, pred, k)
        d["oid"] = oid
        details.append(d)
        if d.get("physics_fail"):
            fails.append(d)
    return {
        "physics_fail": len(fails) > 0,
        "n_fail": len(fails),
        "n_obj": len(predicted_objects),
        "details": details,
    }
