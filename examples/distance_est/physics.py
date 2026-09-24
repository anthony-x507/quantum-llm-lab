"""Floor-scale + parallax distance helpers (CPU, no VLM).

LOCK (Anthony): NO fixed traffic-light heights. Traffic lights are NOT a fixed 3m.
Scale reference = BUILDING FLOORS: each floor ≈ 8–10 ft (2.4–3.0 m), standard.

Pipeline:
  1. Read building floor count + apparent floor height (px) in frame.
  2. meters_per_px_at_facade = floor_height_m / floor_px
     d_building ≈ focal_px * floor_height_m / floor_px
  3. Derive light/sign REAL height by how many floors it spans in-frame
     (span_floors * floor_height_m), THEN distance from that derived height.
  4. Soft apparent-size priors for cars (~4.5 m length) and pedestrians (~1.7 m
     height) — NOT for lights (still floor-span / 3–5 m vary).
  5. Fine frame-to-frame parallax triangulates mid-band (30–70 m DANGER ZONE).
  6. Closing-speed + time-to-impact from apparent growth rate.

GT meters exist only in synthetic sidecars; never in inference prompts.
"""
from __future__ import annotations

from typing import Any

# Standard floor height range (meters). Use midpoint unless scene specifies.
FLOOR_HEIGHT_M_MIN = 2.4   # ~8 ft
FLOOR_HEIGHT_M_MAX = 3.0   # ~10 ft
FLOOR_HEIGHT_M_DEFAULT = 2.7

# Soft size priors (cars / peds only — NEVER lights)
CAR_LENGTH_M_PRIOR = 4.5
CAR_HEIGHT_M_PRIOR = 1.55
PED_HEIGHT_M_PRIOR = 1.7

# Default pinhole focal length in pixels (matches generator)
DEFAULT_FOCAL_PX = 420.0

# Scoring tolerances (unchanged)
TOL_NEAR = 0.10   # GT < 50 m → ±10%
TOL_FAR = 0.20    # GT 50–200 m → ±20%
NEAR_CUTOFF_M = 50.0

# Danger zone (reinforce mid-band)
DANGER_ZONE_M_LO = 30.0
DANGER_ZONE_M_HI = 70.0

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


def in_danger_zone(d_m: float) -> bool:
    return DANGER_ZONE_M_LO <= d_m <= DANGER_ZONE_M_HI


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


def distance_from_size_prior(
    apparent_px: float,
    prior_m: float,
    focal_px: float = DEFAULT_FOCAL_PX,
) -> float | None:
    """Soft prior: d = f * H_prior / h_px (cars ~4.5 m length / peds ~1.7 m)."""
    if apparent_px <= 1e-3 or prior_m <= 0:
        return None
    return (focal_px * prior_m) / apparent_px


def estimate_via_floor_scale(
    obj: dict[str, Any],
    scale: dict[str, float],
    focal_px: float = DEFAULT_FOCAL_PX,
    *,
    building_cy: float | None = None,
) -> tuple[float | None, float, str]:
    """Estimate distance using FLOOR-SCALE + soft car/ped size priors.

    Buildings → direct floor calibration.
    Cars/peds → triangulate ground-plane + apparent-size prior (4.5 m / 1.7 m).
    Lights/signs → floor-span derived height when coplanar; else ground-plane.
      NEVER a fixed light catalog height.
    """
    cls = obj.get("class", "")
    app = float(obj.get("apparent_px") or obj.get("bbox_h") or 0.0)
    bbox_w = float(obj.get("bbox_w") or 0.0)
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
    # Anchor with building so floor-scale wins over absolute cam_h assumptions.
    horizon = 57.6  # height*0.30 for H=192
    bcy = float(building_cy) if building_cy is not None else (horizon + (focal_px * 1.6 / max(d_b, 1)) * 0.22)
    f_obj = max(0.25, cy_f - horizon)
    f_b = max(0.25, bcy - horizon)
    d_abs = (focal_px * 1.6 * 0.22) / f_obj
    d_anch = d_b * (f_b / f_obj)
    d_gp = 0.55 * d_abs + 0.45 * d_anch

    if cls in ("light", "stop_sign"):
        # Same image-row as building → same depth plane; floor-span derived H.
        # Else trust ground-plane. NEVER fixed light height.
        if abs(cy_f - bcy) < 8 and floor_px > 1e-6 and app > 1e-3:
            H = derived_height_from_floor_span(app, floor_px, fh)
            d_h = distance_from_derived_height(app, H, focal_px)
            if d_h is not None:
                # Mid-band: prefer GP more (floor-span alone overshoots ~50 m lights)
                mid = DANGER_ZONE_M_LO <= d_gp <= DANGER_ZONE_M_HI
                w_h = 0.35 if mid else 0.75
                d = (1.0 - w_h) * d_gp + w_h * d_h
                return max(1.0, d), 0.75, "floor_span+ground_plane"
        return max(1.0, d_gp), 0.6, "ground_plane_floor_anchored"

    if cls == "car":
        # Triangulate GP + length prior (bbox_w ≈ length * scale * 0.5 in render)
        # and soft height prior on apparent_px.
        d_len = distance_from_size_prior(max(bbox_w, 1e-3) / 0.5, CAR_LENGTH_M_PRIOR, focal_px)
        d_h = distance_from_size_prior(app, CAR_HEIGHT_M_PRIOR, focal_px)
        parts = [d_gp]
        weights = [0.50]
        if d_len is not None:
            parts.append(d_len)
            weights.append(0.30)
        if d_h is not None:
            parts.append(d_h)
            weights.append(0.20)
        wsum = sum(weights)
        d = sum(p * w for p, w in zip(parts, weights)) / wsum
        return max(1.0, d), 0.78, "gp+car_size_prior"

    if cls == "pedestrian":
        d_h = distance_from_size_prior(app, PED_HEIGHT_M_PRIOR, focal_px)
        if d_h is not None:
            mid = DANGER_ZONE_M_LO <= d_gp <= DANGER_ZONE_M_HI
            w_h = 0.45 if mid else 0.30
            d = (1.0 - w_h) * d_gp + w_h * d_h
            return max(1.0, d), 0.76, "gp+ped_height_prior"
        return max(1.0, d_gp), 0.65, "ground_plane_floor_anchored"

    if cls == "intersection":
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
    alpha: float | None = None,
) -> tuple[float, float]:
    """Fine parallax: blend size-ratio depth change (triangulate mid-band)."""
    conf = 0.55
    if size_prev <= 1e-6 or size_curr <= 1e-6:
        return d_est, conf
    d_par = d_est * (size_prev / size_curr)
    # Stronger parallax weight in danger zone (30–70 m)
    if alpha is None:
        mid = DANGER_ZONE_M_LO <= d_est <= DANGER_ZONE_M_HI
        if signal in ("approach", "recede"):
            alpha = 0.55 if mid else 0.40
        else:
            alpha = 0.25 if mid else 0.20
    refined = (1 - alpha) * d_est + alpha * d_par
    if signal == "approach":
        conf = 0.82
    elif signal == "recede":
        conf = 0.78
    elif signal == "stable":
        conf = 0.65
    return max(0.5, refined), conf


def closing_speed_tti(
    size_prev: float,
    size_curr: float,
    d_est: float,
    *,
    dt_s: float = 1.0 / 12.0,
) -> dict[str, float | str | None]:
    """If object grows X% per frame → closing speed + time-to-impact.

    d ∝ 1/s → d_curr ≈ d_est, d_prev ≈ d_est * (s_curr / s_prev)
    v_close (m/s, + toward camera) = (d_prev - d_curr) / dt
    tti = d_curr / v_close when approaching.
    """
    out: dict[str, float | str | None] = {
        "growth_frac": None,
        "closing_speed_mps": None,
        "tti_s": None,
        "signal": "unknown",
    }
    if size_prev <= 1e-6 or size_curr <= 1e-6 or d_est <= 0 or dt_s <= 0:
        return out
    growth = (size_curr - size_prev) / size_prev
    out["growth_frac"] = round(float(growth), 5)
    signal = parallax_signal(size_prev, size_curr)
    out["signal"] = signal
    # d_prev from size ratio relative to current estimate
    d_prev = d_est * (size_curr / size_prev)
    v_close = (d_prev - d_est) / dt_s
    out["closing_speed_mps"] = round(float(v_close), 4)
    if v_close > 0.05:  # approaching
        out["tti_s"] = round(float(d_est / v_close), 3)
    return out


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
