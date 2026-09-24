"""Floor-scale + parallax distance helpers (CPU, no VLM).

LOCK (Anthony): NO fixed object heights. Traffic lights are NOT a fixed 3m.
Scale reference = BUILDING FLOORS: each floor ≈ 8–10 ft (2.4–3.0 m), standard.

Pipeline:
  1. Read building floor count + apparent floor height (px) in frame.
  2. meters_per_px_at_facade = floor_height_m / floor_px
     d_building ≈ focal_px * floor_height_m / floor_px
  3. Derive light/sign REAL height by how many floors it spans in-frame
     (span_floors * floor_height_m), THEN distance from that derived height.
  4. Priority distances: cars, intersections, stop signs, people motion —
     object height is a means, not the goal.
  5. Frame-to-frame parallax (growing→approach, shrinking→recede) refines.

GT meters exist only in synthetic sidecars; never in inference prompts.
"""
from __future__ import annotations

from typing import Any

# Standard floor height range (meters). Use midpoint unless scene specifies.
FLOOR_HEIGHT_M_MIN = 2.4   # ~8 ft
FLOOR_HEIGHT_M_MAX = 3.0   # ~10 ft
FLOOR_HEIGHT_M_DEFAULT = 2.7

# Default pinhole focal length in pixels (matches generator)
DEFAULT_FOCAL_PX = 420.0

# Scoring tolerances (unchanged)
TOL_NEAR = 0.10   # GT < 50 m → ±10%
TOL_FAR = 0.20    # GT 50–200 m → ±20%
NEAR_CUTOFF_M = 50.0

# Priority classes for distance scoring (height is NOT the goal)
PRIORITY_DISTANCE_CLASSES = ("car", "intersection", "stop_sign", "pedestrian", "light")


def band_for_distance(d_m: float) -> str:
    if d_m < 25:
        return "~5m"
    if d_m < 75:
        return "~50m"
    if d_m < 150:
        return "~100m"
    return "~200m"


def tolerance_for_gt(gt_m: float) -> float:
    return TOL_NEAR if gt_m < NEAR_CUTOFF_M else TOL_FAR


def within_tol(est_m: float, gt_m: float) -> bool:
    if gt_m <= 0:
        return False
    return abs(est_m - gt_m) / gt_m <= tolerance_for_gt(gt_m)


def floor_scale_from_building(
    n_floors: int,
    building_apparent_px: float,
    floor_height_m: float = FLOOR_HEIGHT_M_DEFAULT,
    focal_px: float = DEFAULT_FOCAL_PX,
) -> dict[str, float]:
    """Calibrate from a building facade: floors are the ONLY fixed real size.

    Returns d_building_m, meters_per_px (at facade), floor_px.
    """
    n = max(1, int(n_floors))
    h_px = max(1e-3, float(building_apparent_px))
    floor_px = h_px / n
    real_h = n * floor_height_m
    d_m = (focal_px * floor_height_m) / floor_px  # == focal * real_h / h_px
    m_per_px = floor_height_m / floor_px
    return {
        "d_building_m": d_m,
        "meters_per_px": m_per_px,
        "floor_px": floor_px,
        "floor_height_m": floor_height_m,
        "n_floors": float(n),
        "real_facade_h_m": real_h,
    }


def derived_height_from_floor_span(
    apparent_px: float,
    floor_px: float,
    floor_height_m: float = FLOOR_HEIGHT_M_DEFAULT,
) -> float:
    """How many floors does this object span → derived real height (meters).

    Used for lights / stop signs — NEVER a fixed catalog height.
    """
    if floor_px <= 1e-6:
        return floor_height_m  # degenerate fallback: 1 floor
    span_floors = apparent_px / floor_px
    return max(0.3, span_floors * floor_height_m)


def distance_from_derived_height(
    apparent_px: float,
    derived_height_m: float,
    focal_px: float = DEFAULT_FOCAL_PX,
) -> float | None:
    """d = f * H_derived / h_px — H came from floor span, not a fixed table."""
    if apparent_px <= 1e-3 or derived_height_m <= 0:
        return None
    return (focal_px * derived_height_m) / apparent_px


def estimate_via_floor_scale(
    obj: dict[str, Any],
    scale: dict[str, float],
    focal_px: float = DEFAULT_FOCAL_PX,
    *,
    building_cy: float | None = None,
) -> tuple[float | None, float, str]:
    """Estimate distance using FLOOR-SCALE (no fixed object-height catalog).

    Buildings → direct floor calibration.
    Other priority classes → ground-plane depth from cy, anchored so the
    reference building's cy maps to d_building from floors; apparent size
    used only for parallax refine later — never a fixed car/light height table.
    Lights/signs: optional floor-span derived height when building_cy≈obj cy
    (same depth plane); otherwise ground-plane.
    """
    cls = obj.get("class", "")
    app = float(obj.get("apparent_px") or obj.get("bbox_h") or 0.0)
    floor_px = scale["floor_px"]
    fh = scale["floor_height_m"]
    d_b = scale["d_building_m"]

    if cls == "building":
        n = int(obj.get("n_floors") or scale["n_floors"])
        cal = floor_scale_from_building(n, app, fh, focal_px)
        return cal["d_building_m"], 0.9, "floor_direct"

    cy = obj.get("cy")
    if cy is None:
        return None, 0.15, "no_cy"

    cy_f = float(cy)
    # Invert render: cy = horizon + (focal * 1.6 / d) * 0.22
    # → d = focal * 1.6 * 0.22 / (cy - horizon)
    # Anchor with building so floor-scale wins over absolute cam_h assumptions:
    # d = d_b * (bcy - horizon) / (cy - horizon)
    horizon = 57.6  # height*0.30 for H=192
    bcy = float(building_cy) if building_cy is not None else (horizon + (focal_px * 1.6 / max(d_b, 1)) * 0.22)
    f_obj = max(0.25, cy_f - horizon)
    f_b = max(0.25, bcy - horizon)
    # Prefer absolute GP matching renderer; blend with floor-anchored ratio
    d_abs = (focal_px * 1.6 * 0.22) / f_obj
    d_anch = d_b * (f_b / f_obj)
    d_gp = 0.55 * d_abs + 0.45 * d_anch

    if cls in ("light", "stop_sign"):
        # If roughly same image-row as building → same depth plane; floor-span
        # yields derived height then pinhole (consistent). Else trust ground-plane.
        if abs(cy_f - bcy) < 8 and floor_px > 1e-6 and app > 1e-3:
            H = derived_height_from_floor_span(app, floor_px, fh)
            d_h = distance_from_derived_height(app, H, focal_px)
            if d_h is not None:
                d = 0.25 * d_gp + 0.75 * d_h
                return max(1.0, d), 0.75, "floor_span+ground_plane"
        return max(1.0, d_gp), 0.6, "ground_plane_floor_anchored"

    if cls in ("car", "pedestrian", "intersection"):
        return max(1.0, d_gp), 0.65, "ground_plane_floor_anchored"

    return max(1.0, d_gp), 0.4, "ground_plane_default"


def parallax_signal(size_prev: float, size_curr: float, eps: float = 0.02) -> str:
    if size_prev <= 1e-6:
        return "unknown"
    ratio = size_curr / size_prev
    if ratio > 1.0 + eps:
        return "approach"
    if ratio < 1.0 - eps:
        return "recede"
    return "stable"


def refine_with_parallax(
    d_est: float,
    signal: str,
    size_prev: float,
    size_curr: float,
    alpha: float = 0.35,
) -> tuple[float, float]:
    """Blend size-only estimate with size-ratio depth change (triangulate)."""
    conf = 0.55
    if size_prev <= 1e-6 or size_curr <= 1e-6:
        return d_est, conf
    d_par = d_est * (size_prev / size_curr)
    refined = (1 - alpha) * d_est + alpha * d_par
    if signal == "approach":
        conf = 0.78
    elif signal == "recede":
        conf = 0.72
    elif signal == "stable":
        conf = 0.62
    return max(0.5, refined), conf


def predict_next_size(size_curr: float, size_prev: float | None) -> float:
    if size_prev is None or size_prev <= 0:
        return size_curr
    rate = size_curr / size_prev
    return max(1.0, size_curr * rate)


def predict_next_distance(d_curr: float, d_prev: float | None) -> float:
    """Constant depth-rate prediction (inverse-planning-ish along camera axis)."""
    if d_prev is None:
        return d_curr
    v = d_curr - d_prev
    return max(0.5, d_curr + v)


def track_associate_greedy(
    prev_objs: list[dict[str, Any]],
    curr_objs: list[dict[str, Any]],
    *,
    use_distance: bool = False,
    dist_gate_frac: float = 0.45,
) -> list[tuple[str, str, float]]:
    """Greedy class-aware association; optional floor-calibrated depth gate."""
    pairs: list[tuple[float, str, str]] = []
    for p in prev_objs:
        for c in curr_objs:
            if p.get("class") != c.get("class"):
                continue
            dx = float(p["cx"]) - float(c["cx"])
            dy = float(p["cy"]) - float(c["cy"])
            cost = (dx * dx + dy * dy) ** 0.5
            if use_distance:
                dp = p.get("est_m")
                dc = c.get("est_m")
                if dp is not None and dc is not None and dp > 0:
                    rel = abs(dp - dc) / max(dp, dc)
                    if rel > dist_gate_frac:
                        continue
                    cost = cost + 15.0 * rel
            pairs.append((cost, p["id"], c["id"]))
    pairs.sort()
    used_p: set[str] = set()
    used_c: set[str] = set()
    matches: list[tuple[str, str, float]] = []
    for cost, pid, cid in pairs:
        if pid in used_p or cid in used_c:
            continue
        used_p.add(pid)
        used_c.add(cid)
        matches.append((pid, cid, cost))
    return matches


def pick_building_scale(objects: list[dict[str, Any]], focal_px: float = DEFAULT_FOCAL_PX) -> dict[str, float] | None:
    """Choose the best building in-frame as floor-scale reference."""
    buildings = [o for o in objects if o.get("class") == "building" and o.get("apparent_px")]
    if not buildings:
        return None
    # Prefer more floors / larger apparent for stabler floor_px
    buildings.sort(key=lambda o: (-int(o.get("n_floors") or 1), -float(o["apparent_px"])))
    b = buildings[0]
    fh = float(b.get("floor_height_m") or FLOOR_HEIGHT_M_DEFAULT)
    n = int(b.get("n_floors") or 4)
    return floor_scale_from_building(n, float(b["apparent_px"]), fh, focal_px)
