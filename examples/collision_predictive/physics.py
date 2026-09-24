"""Elastic 2D disk collision physics for predictive collision layer (CPU).

Laws (real kinematics, not vision-only):
  - Constant velocity between events
  - Elastic pairwise disk collisions (momentum + kinetic energy conserved
    for frictionless equal-elasticity contacts; masses matter)
  - Soft wall bounce on arena inset
  - Hypo actions mutate ego velocity then rollout

ANTI-CONTAM: this module never reads GT sidecars; only state vectors.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np

ARENA_W = 320
ARENA_H = 200
MARGIN = 10
ACTIONS = ("coast", "brake", "accelerate", "turn_left", "turn_right")

# Action kinematics (ego only)
BRAKE_FACTOR = 0.35          # multiply speed
ACCEL_DELTA = 3.5            # add along heading
TURN_RAD = math.radians(35)  # yaw delta per action apply


def apply_action(ego: dict[str, Any], action: str) -> dict[str, Any]:
    """Return a copy of ego with velocity mutated by discrete action."""
    out = dict(ego)
    vx, vy = float(out["vx"]), float(out["vy"])
    speed = math.hypot(vx, vy)
    action = str(action)
    if action == "coast":
        pass
    elif action == "brake":
        vx *= BRAKE_FACTOR
        vy *= BRAKE_FACTOR
    elif action == "accelerate":
        if speed < 1e-6:
            # default heading +x if stationary
            vx, vy = ACCEL_DELTA, 0.0
        else:
            ux, uy = vx / speed, vy / speed
            vx += ux * ACCEL_DELTA
            vy += uy * ACCEL_DELTA
    elif action == "turn_left":
        c, s = math.cos(TURN_RAD), math.sin(TURN_RAD)
        vx, vy = c * vx - s * vy, s * vx + c * vy
    elif action == "turn_right":
        c, s = math.cos(-TURN_RAD), math.sin(-TURN_RAD)
        vx, vy = c * vx - s * vy, s * vx + c * vy
    else:
        raise ValueError(f"unknown action {action}")
    out["vx"], out["vy"] = float(vx), float(vy)
    return out


def _wall_bounce(o: dict[str, Any]) -> None:
    r = float(o.get("r", 8))
    lo_x, hi_x = MARGIN + r, ARENA_W - MARGIN - r
    lo_y, hi_y = MARGIN + r, ARENA_H - MARGIN - r
    x, y, vx, vy = float(o["x"]), float(o["y"]), float(o["vx"]), float(o["vy"])
    if x < lo_x:
        x = lo_x + (lo_x - x)
        vx = -vx
    elif x > hi_x:
        x = hi_x - (x - hi_x)
        vx = -vx
    if y < lo_y:
        y = lo_y + (lo_y - y)
        vy = -vy
    elif y > hi_y:
        y = hi_y - (y - hi_y)
        vy = -vy
    o["x"], o["y"], o["vx"], o["vy"] = x, y, vx, vy


def _resolve_elastic(a: dict[str, Any], b: dict[str, Any]) -> bool:
    """If overlapping disks, resolve elastic collision in-place. Return True if collided."""
    dx = float(b["x"]) - float(a["x"])
    dy = float(b["y"]) - float(a["y"])
    dist = math.hypot(dx, dy)
    ra, rb = float(a.get("r", 8)), float(b.get("r", 8))
    min_dist = ra + rb
    if dist >= min_dist or dist < 1e-9:
        return False
    # normal
    nx, ny = dx / dist, dy / dist
    # relative velocity along normal
    dvx = float(a["vx"]) - float(b["vx"])
    dvy = float(a["vy"]) - float(b["vy"])
    vn = dvx * nx + dvy * ny
    if vn <= 0:
        # already separating — still push apart to clear overlap
        overlap = min_dist - dist
        ma, mb = float(a.get("mass", 1.0)), float(b.get("mass", 1.0))
        inv = 1.0 / (ma + mb)
        a["x"] = float(a["x"]) - nx * overlap * (mb * inv)
        a["y"] = float(a["y"]) - ny * overlap * (mb * inv)
        b["x"] = float(b["x"]) + nx * overlap * (ma * inv)
        b["y"] = float(b["y"]) + ny * overlap * (ma * inv)
        return True
    ma, mb = float(a.get("mass", 1.0)), float(b.get("mass", 1.0))
    # 1D elastic along normal
    impulse = (2.0 * vn) / (ma + mb)
    a["vx"] = float(a["vx"]) - impulse * mb * nx
    a["vy"] = float(a["vy"]) - impulse * mb * ny
    b["vx"] = float(b["vx"]) + impulse * ma * nx
    b["vy"] = float(b["vy"]) + impulse * ma * ny
    # separate centers
    overlap = min_dist - dist
    inv = 1.0 / (ma + mb)
    a["x"] = float(a["x"]) - nx * overlap * (mb * inv)
    a["y"] = float(a["y"]) - ny * overlap * (mb * inv)
    b["x"] = float(b["x"]) + nx * overlap * (ma * inv)
    b["y"] = float(b["y"]) + ny * overlap * (ma * inv)
    return True


def step_world(agents: list[dict[str, Any]], *, substeps: int = 4) -> tuple[list[dict[str, Any]], list[tuple[str, str]]]:
    """Advance one frame with substeps; return new agents + collision pairs this frame."""
    state = [dict(o) for o in agents]
    pairs: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    dt = 1.0 / float(substeps)
    for _ in range(substeps):
        for o in state:
            o["x"] = float(o["x"]) + float(o["vx"]) * dt
            o["y"] = float(o["y"]) + float(o["vy"]) * dt
            _wall_bounce(o)
        n = len(state)
        for i in range(n):
            for j in range(i + 1, n):
                if _resolve_elastic(state[i], state[j]):
                    key = tuple(sorted((state[i]["oid"], state[j]["oid"])))
                    if key not in seen:
                        seen.add(key)
                        pairs.append(key)  # type: ignore[arg-type]
    return state, pairs


def rollout(
    agents: list[dict[str, Any]],
    k: int,
    *,
    ego_id: str = "ego",
    action: str | None = None,
) -> dict[str, Any]:
    """Roll forward k frames. Optionally apply `action` to ego once at t0.

    Returns final agents, collision_events (list of {t, pair}), any_collision,
    partner_of_ego (first collider with ego or None).
    """
    state = [dict(o) for o in agents]
    if action is not None:
        for i, o in enumerate(state):
            if o["oid"] == ego_id:
                state[i] = apply_action(o, action)
                break
    events: list[dict[str, Any]] = []
    partner = None
    for t in range(1, int(k) + 1):
        state, pairs = step_world(state)
        for a, b in pairs:
            events.append({"t": t, "pair": [a, b]})
            if partner is None and ego_id in (a, b):
                partner = b if a == ego_id else a
    return {
        "agents": state,
        "collision_events": events,
        "any_collision": len(events) > 0,
        "ego_collision": partner is not None,
        "partner_of_ego": partner,
        "action": action,
        "k": int(k),
    }


def consequence_label(roll: dict[str, Any], agents0: list[dict[str, Any]]) -> str:
    """Human/machine consequence tag from rollout (no GT)."""
    if not roll["ego_collision"]:
        if roll["any_collision"]:
            return "third_party_collision_only"
        return "clear"
    pid = roll["partner_of_ego"]
    by = {o["oid"]: o for o in agents0}
    p = by.get(pid or "", {})
    cls = str(p.get("class", "agent"))
    # classify rear-end vs cross using relative positions at t0
    ego = by.get("ego")
    if ego and p:
        dx = float(p["x"]) - float(ego["x"])
        dy = float(p["y"]) - float(ego["y"])
        evx, evy = float(ego["vx"]), float(ego["vy"])
        speed = math.hypot(evx, evy) + 1e-9
        # along-track component
        along = (dx * evx + dy * evy) / speed
        cross = abs((-evy * dx + evx * dy) / speed)
        if cls == "pedestrian":
            return f"cross_pedestrian_{pid}"
        if along > 0 and cross < float(ego.get("r", 8)) * 2.5:
            return f"rear_end_{pid}"
        return f"side_swipe_{pid}"
    return f"collide_{pid}"


def predict_emit(
    agents: list[dict[str, Any]],
    k: int,
    *,
    action: str | None = None,
    choose_safest: bool = False,
) -> dict[str, Any]:
    """Emit schema: chosen_action + predicted_consequence + is_safe.

    If choose_safest, evaluate all ACTIONS and pick first safe (prefer coast),
    else use given action (default coast).
    """
    if choose_safest:
        # Prefer safe actions; among safe prefer larger min-clearance, then
        # coast→brake→turn_*→accelerate (inverse-r2 polish; holds 100%).
        order = ("coast", "brake", "turn_left", "turn_right", "accelerate")
        safe: list[tuple[float, int, dict[str, Any], dict[str, Any]]] = []
        first_unsafe: dict[str, Any] | None = None
        first_unsafe_roll: dict[str, Any] | None = None
        for idx, a in enumerate(order):
            roll = rollout(agents, k, action=a)
            emit = {
                "chosen_action": a,
                "predicted_consequence": consequence_label(roll, agents),
                "is_safe": not roll["ego_collision"],
            }
            if emit["is_safe"]:
                ego = next(o for o in roll["agents"] if o["oid"] == "ego")
                gaps = []
                for o in roll["agents"]:
                    if o["oid"] == "ego":
                        continue
                    rsum = float(o.get("r", 8)) + float(ego.get("r", 8))
                    gaps.append(math.hypot(float(o["x"]) - float(ego["x"]), float(o["y"]) - float(ego["y"])) - rsum)
                clearance = min(gaps) if gaps else 1e9
                safe.append((clearance, idx, emit, roll))
            elif first_unsafe is None:
                first_unsafe, first_unsafe_roll = emit, roll
        if safe:
            safe.sort(key=lambda t: (-t[0], t[1]))
            _, _, best, roll = safe[0]
        else:
            assert first_unsafe is not None and first_unsafe_roll is not None
            best, roll = first_unsafe, first_unsafe_roll
        best["partner_of_ego"] = roll["partner_of_ego"]
        best["any_collision"] = roll["any_collision"]
        best["predicted_agents"] = [
            {"oid": o["oid"], "x": o["x"], "y": o["y"], "vx": o["vx"], "vy": o["vy"]}
            for o in roll["agents"]
        ]
        return best

    a = action if action is not None else "coast"
    roll = rollout(agents, k, action=a)
    return {
        "chosen_action": a,
        "predicted_consequence": consequence_label(roll, agents),
        "is_safe": not roll["ego_collision"],
        "partner_of_ego": roll["partner_of_ego"],
        "any_collision": roll["any_collision"],
        "predicted_agents": [
            {"oid": o["oid"], "x": o["x"], "y": o["y"], "vx": o["vx"], "vy": o["vy"]}
            for o in roll["agents"]
        ],
    }


def _cv_wall_step(o: dict[str, Any]) -> None:
    """One Euler frame of CV with elastic wall bounce (no agent-agent resolve)."""
    r = float(o.get("r", 8))
    lo_x, hi_x = MARGIN + r, ARENA_W - MARGIN - r
    lo_y, hi_y = MARGIN + r, ARENA_H - MARGIN - r
    x = float(o["x"]) + float(o["vx"])
    y = float(o["y"]) + float(o["vy"])
    vx, vy = float(o["vx"]), float(o["vy"])
    if x < lo_x:
        x = lo_x + (lo_x - x)
        vx = -vx
    elif x > hi_x:
        x = hi_x - (x - hi_x)
        vx = -vx
    if y < lo_y:
        y = lo_y + (lo_y - y)
        vy = -vy
    elif y > hi_y:
        y = hi_y - (y - hi_y)
        vy = -vy
    o["x"], o["y"], o["vx"], o["vy"] = x, y, vx, vy


def _cv_pair_overlaps(state: list[dict[str, Any]]) -> tuple[str | None, bool]:
    """Return (ego_partner_or_None, any_pairwise_overlap). No mass/elastic resolve."""
    partner: str | None = None
    any_c = False
    n = len(state)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = state[i], state[j]
            if math.hypot(float(a["x"]) - float(b["x"]), float(a["y"]) - float(b["y"])) < (
                float(a.get("r", 8)) + float(b.get("r", 8))
            ):
                any_c = True
                if a["oid"] == "ego" or b["oid"] == "ego":
                    if partner is None:
                        partner = b["oid"] if a["oid"] == "ego" else a["oid"]
    return partner, any_c


def _cv_step_with_tp_mass(
    state: list[dict[str, Any]],
) -> tuple[str | None, bool]:
    """One CV frame: wall Euler, then mass-aware third-party bounce only.

    Ego overlaps are flagged geometrically and NOT elastically resolved
    (keeps inverse_cv distinct from collision_physics oracle, which uses
    4 substeps + ego resolve). Third-party pairs use observable ``mass``
    from perception state (meta frames — never GT futures).
    """
    for o in state:
        _cv_wall_step(o)
    partner: str | None = None
    any_c = False
    n = len(state)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = state[i], state[j]
            dx = float(b["x"]) - float(a["x"])
            dy = float(b["y"]) - float(a["y"])
            dist = math.hypot(dx, dy)
            min_d = float(a.get("r", 8)) + float(b.get("r", 8))
            if dist >= min_d or dist < 1e-9:
                continue
            ego_pair = a["oid"] == "ego" or b["oid"] == "ego"
            if ego_pair:
                any_c = True
                if partner is None:
                    partner = b["oid"] if a["oid"] == "ego" else a["oid"]
                # geometric flag only — no ego elastic resolve (ablation vs physics)
            else:
                any_c = True
                _resolve_elastic(a, b)
    return partner, any_c


def predict_cv_no_collision(
    agents: list[dict[str, Any]],
    k: int,
    *,
    action: str | None = None,
) -> dict[str, Any]:
    """Inverse-style CV baseline (inverse-r3): action-aware + TP mass bounce.

    Applies hypo action to ego once, steps k frames with wall bounce.
    **Third-party** overlaps resolve with observable masses (perception
    state in meta — not GT futures) so redirected agents can enter/leave
    ego's path. **Ego** overlaps stay geometric flags only (no elastic
    ego resolve, no substeps) — still an ablation floor vs
    ``collision_physics`` (4-substep mass-aware ego+TP oracle).

    inverse-r2 was pure geometric pairwise (no TP bounce) → 99.82%;
    residual misses were TP-redirect cases (e.g. cp_198).
    """
    state = [dict(o) for o in agents]
    if action is not None:
        for i, o in enumerate(state):
            if o["oid"] == "ego":
                state[i] = apply_action(o, action)
                break
    partner: str | None = None
    any_c = False
    for _ in range(int(k)):
        p, ac = _cv_step_with_tp_mass(state)
        any_c = any_c or ac
        if p is not None and partner is None:
            partner = p
    fake_roll = {
        "ego_collision": partner is not None,
        "any_collision": any_c or partner is not None,
        "partner_of_ego": partner,
    }
    return {
        "chosen_action": action if action is not None else "coast",
        "predicted_consequence": consequence_label(fake_roll, agents),
        "is_safe": partner is None,
        "partner_of_ego": partner,
        "any_collision": fake_roll["any_collision"],
        "predicted_agents": [
            {"oid": o["oid"], "x": o["x"], "y": o["y"], "vx": o["vx"], "vy": o["vy"]}
            for o in state
        ],
        "predictor": "inverse_cv_tp_mass",
    }


def check_physics_gate(
    agents0: list[dict[str, Any]],
    predicted_agents: list[dict[str, Any]],
    k: int,
) -> dict[str, Any]:
    """Flag teleport / flying — same spirit as inverse physics gate."""
    by0 = {o["oid"]: o for o in agents0}
    fails = []
    for p in predicted_agents:
        o0 = by0.get(p["oid"])
        if not o0:
            fails.append({"oid": p["oid"], "reason": "unknown_oid"})
            continue
        jump = math.hypot(float(p["x"]) - float(o0["x"]), float(p["y"]) - float(o0["y"]))
        speed = math.hypot(float(o0["vx"]), float(o0["vy"]))
        max_j = max(speed, 0.5) * float(k) * 3.5 + 40.0  # allow collision kicks
        r = float(o0.get("r", 8))
        if (
            float(p["x"]) < MARGIN - 2
            or float(p["x"]) > ARENA_W - MARGIN + 2
            or float(p["y"]) < MARGIN - 2
            or float(p["y"]) > ARENA_H - MARGIN + 2
        ):
            fails.append({"oid": p["oid"], "reason": "wall_phase_or_flying"})
        elif jump > max_j:
            fails.append({"oid": p["oid"], "reason": "teleport", "jump": jump, "max_j": max_j})
    return {"physics_fail": len(fails) > 0, "n_fail": len(fails), "details": fails}
