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

# Danger zone (reinforce mid-band) — FROZEN at 100% (tip-distance-danger)
DANGER_ZONE_M_LO = 30.0
DANGER_ZONE_M_HI = 70.0

# Side polish outside DZ: near mid + outer mid (tip-distance-mid) — FROZEN floors
MID_NEAR_M_LO = 5.0
MID_NEAR_M_HI = 30.0
MID_OUTER_M_LO = 70.0
MID_OUTER_M_HI = 100.0

# Side polish FAR band ~100–200 m (tip-distance-far)
FAR_M_LO = 100.0
FAR_M_HI = 200.0
FAR_NEAR_M_LO = 100.0
FAR_NEAR_M_HI = 150.0
FAR_OUTER_M_LO = 150.0
FAR_OUTER_M_HI = 200.0

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


def in_mid_near(d_m: float) -> bool:
    """5–30 m near/mid band (outside frozen DZ) — hold floor."""
    return MID_NEAR_M_LO <= d_m <= MID_NEAR_M_HI


def in_mid_outer(d_m: float) -> bool:
    """70–100 m outer/mid band (outside frozen DZ) — hold floor."""
    return MID_OUTER_M_LO <= d_m <= MID_OUTER_M_HI


def in_far(d_m: float) -> bool:
    """100–200 m far band (tip-distance-far target)."""
    return FAR_M_LO <= d_m <= FAR_M_HI


def in_far_near(d_m: float) -> bool:
    """100–150 m far-near slice."""
    return FAR_NEAR_M_LO <= d_m <= FAR_NEAR_M_HI


def in_far_outer(d_m: float) -> bool:
    """150–200 m far-outer slice."""
    return FAR_OUTER_M_LO <= d_m <= FAR_OUTER_M_HI


def in_gp_heavy_band(d_m: float) -> bool:
    """GP-heavy: frozen DZ + outer mid + far (weak size priors at range)."""
    return in_danger_zone(d_m) or in_mid_outer(d_m) or in_far(d_m)


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
        # NEVER fixed light/sign catalog height (real lights ~3–5 m vary).
        # Floor-span is ONLY valid when object is coplanar with facade
        # (d_gp ≈ d_building). Near lights share cy with far buildings but are
        # NOT coplanar — floor-span then invents huge "span floors" and
        # overshoots the 30–70 m DANGER ZONE. Prefer GP; honesty when unsure.
        # FAR 100–200 m: size/span priors weak → GP-heavy like DZ/outer mid.
        dz = in_danger_zone(d_gp)
        outer = in_mid_outer(d_gp)
        near = in_mid_near(d_gp)
        far = in_far(d_gp)
        gp_heavy = dz or outer or far
        coplanar = abs(d_gp - d_b) / max(d_b, 1.0) < 0.28 and abs(cy_f - bcy) < 6
        if coplanar and floor_px > 1e-6 and app > 1e-3:
            H = derived_height_from_floor_span(app, floor_px, fh)
            d_h = distance_from_derived_height(app, H, focal_px)
            if d_h is not None:
                # Facade-coplanar: soft span in DZ/outer/far; near trusts GP more
                if far:
                    w_h = 0.22
                elif gp_heavy:
                    w_h = 0.25
                elif near:
                    w_h = 0.15
                else:
                    w_h = 0.55
                d = (1.0 - w_h) * d_gp + w_h * d_h
                return max(1.0, d), 0.72, "floor_span+ground_plane"
        if floor_px > 1e-6 and app > 1e-3:
            H = derived_height_from_floor_span(app, floor_px, fh)
            d_h = distance_from_derived_height(app, H, focal_px)
            if d_h is not None:
                rel = abs(d_h - d_gp) / max(d_gp, 1.0)
                if rel > 0.45:
                    # Strong disagreement → honesty: GP only, low conf
                    return max(1.0, d_gp), 0.42, "gp_honesty_span_disagree"
                # Mild disagree: tiny span vote outside danger/outer/far; none inside
                if far:
                    w_h = 0.04
                    conf = 0.56
                elif gp_heavy:
                    w_h = 0.05
                    conf = 0.58
                elif near:
                    w_h = 0.08
                    conf = 0.64
                else:
                    w_h = 0.18
                    conf = 0.62
                d = (1.0 - w_h) * d_gp + w_h * d_h
                return max(1.0, d), conf, "ground_plane_floor_anchored"
        return max(1.0, d_gp), 0.60, "ground_plane_floor_anchored"

    if cls == "car":
        # Triangulate GP + length prior (bbox_w ≈ length * scale * 0.5 in render)
        # and soft height prior on apparent_px.
        # DZ + outer mid + FAR: heavier GP (size prior noisy at range). Near: trust size more.
        d_len = distance_from_size_prior(max(bbox_w, 1e-3) / 0.5, CAR_LENGTH_M_PRIOR, focal_px)
        d_h = distance_from_size_prior(app, CAR_HEIGHT_M_PRIOR, focal_px)
        dz = in_danger_zone(d_gp)
        outer = in_mid_outer(d_gp)
        near = in_mid_near(d_gp)
        far = in_far(d_gp)
        gp_heavy = dz or outer
        parts = [d_gp]
        if far:
            # Far: GP dominates; tiny prior votes only
            weights = [0.72]
            w_len, w_h = 0.16, 0.12
            conf = 0.76
            thr = 0.50  # honesty earlier — priors less trustworthy far
        elif gp_heavy:
            weights = [0.62]
            w_len, w_h = 0.23, 0.15
            conf = 0.80
            thr = 0.55
        elif near:
            weights = [0.40]
            w_len, w_h = 0.35, 0.25
            conf = 0.82
            thr = 0.70
        else:
            weights = [0.50]
            w_len, w_h = 0.30, 0.20
            conf = 0.78
            thr = 0.55
        if d_len is not None:
            parts.append(d_len)
            weights.append(w_len)
        if d_h is not None:
            parts.append(d_h)
            weights.append(w_h)
        wsum = sum(weights)
        d = sum(p * w for p, w in zip(parts, weights)) / wsum
        # Honesty: if size priors violently disagree with GP, trust GP
        priors = [x for x in (d_len, d_h) if x is not None]
        if priors:
            d_prior = sum(priors) / len(priors)
            if abs(d_prior - d_gp) / max(d_gp, 1.0) > thr:
                return max(1.0, d_gp), 0.48, "gp_honesty_car_prior_disagree"
        return max(1.0, d), conf, "gp+car_size_prior"

    if cls == "pedestrian":
        d_h = distance_from_size_prior(app, PED_HEIGHT_M_PRIOR, focal_px)
        if d_h is not None:
            dz = in_danger_zone(d_gp)
            outer = in_mid_outer(d_gp)
            near = in_mid_near(d_gp)
            far = in_far(d_gp)
            # DZ/outer/far: softer height prior; near: trust height prior more
            if far:
                w_h, conf, thr = 0.18, 0.74, 0.50
            elif dz or outer:
                w_h, conf, thr = 0.28, 0.78, 0.55
            elif near:
                w_h, conf, thr = 0.42, 0.82, 0.70
            else:
                w_h, conf, thr = 0.30, 0.76, 0.55
            if abs(d_h - d_gp) / max(d_gp, 1.0) > thr:
                return max(1.0, d_gp), 0.48, "gp_honesty_ped_prior_disagree"
            d = (1.0 - w_h) * d_gp + w_h * d_h
            return max(1.0, d), conf, "gp+ped_height_prior"
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
    # Finer parallax in DZ + outer mid + FAR; near also leans on motion
    if alpha is None:
        dz = in_danger_zone(d_est)
        outer = in_mid_outer(d_est)
        near = in_mid_near(d_est)
        far = in_far(d_est)
        if signal in ("approach", "recede"):
            if far:
                alpha = 0.68  # lean harder on parallax at range
            elif dz or outer:
                alpha = 0.62
            elif near:
                alpha = 0.55
            else:
                alpha = 0.42
        else:
            if far:
                alpha = 0.14  # stable far: trust GP more (noise)
            elif dz or outer:
                alpha = 0.18  # stable: trust GP/size more
            elif near:
                alpha = 0.22
            else:
                alpha = 0.20
    refined = (1 - alpha) * d_est + alpha * d_par
    if signal == "approach":
        conf = 0.82
    elif signal == "recede":
        conf = 0.78
    elif signal == "stable":
        conf = 0.65
    return max(0.5, refined), conf


# TTI scoring tolerances (post-hoc vs GT; never at inference)
TTI_TOL_REL = 0.20          # ±20% relative
TTI_TOL_ABS_S = 0.50        # or ±0.5 s absolute
TTI_V_CLOSE_MIN_MPS = 0.05  # approaching threshold
DEFAULT_DT_S = 1.0 / 12.0


def tti_within_tol(est_s: float | None, gt_s: float | None,
                   *, rel: float = TTI_TOL_REL, abs_s: float = TTI_TOL_ABS_S) -> bool:
    """Post-hoc TTI correctness (GT compare only)."""
    if est_s is None or gt_s is None or gt_s <= 0:
        return False
    if abs(float(est_s) - float(gt_s)) <= abs_s:
        return True
    return abs(float(est_s) - float(gt_s)) / max(float(gt_s), 1e-6) <= rel


def gt_tti_from_depth(
    gt_m_curr: float,
    *,
    gt_m_prev: float | None = None,
    v_depth_m_per_frame: float | None = None,
    dt_s: float = DEFAULT_DT_S,
) -> dict[str, float | None]:
    """GT time-to-impact from depth change (sidecar / post-hoc only).

    v_depth in synth is m/frame; negative ⇒ approaching camera.
    Never call at inference — eval harness only.
    """
    out: dict[str, float | None] = {"tti_s": None, "closing_speed_mps": None}
    if gt_m_curr <= 0 or dt_s <= 0:
        return out
    if gt_m_prev is not None:
        v_close = (float(gt_m_prev) - float(gt_m_curr)) / dt_s
    elif v_depth_m_per_frame is not None:
        v_close = (-float(v_depth_m_per_frame)) / dt_s
    else:
        return out
    out["closing_speed_mps"] = round(float(v_close), 4)
    if v_close > TTI_V_CLOSE_MIN_MPS:
        out["tti_s"] = round(float(gt_m_curr) / v_close, 3)
    return out


def tti_band(tti_s: float) -> str:
    if tti_s < 2.0:
        return "<2s"
    if tti_s < 5.0:
        return "2-5s"
    if tti_s < 15.0:
        return "5-15s"
    return ">15s"


def closing_speed_tti(
    size_prev: float,
    size_curr: float,
    d_est: float,
    *,
    dt_s: float = DEFAULT_DT_S,
    d_est_prev: float | None = None,
    size_prev2: float | None = None,
) -> dict[str, float | str | None]:
    """% growth per frame → closing speed + time-to-impact (seconds).

    Primary (size-invariant): tti = dt / growth = dt * s_prev/(s_curr-s_prev).
    Fallback: dist-rate when growth absent/weak-positive and depths approach
    hard (never on recede). size_prev2 reserved for future multi-frame; unused
    in v3 (EMA regressed scorable on synth).
    """
    out: dict[str, float | str | None] = {
        "growth_frac": None,
        "closing_speed_mps": None,
        "tti_s": None,
        "signal": "unknown",
        "tti_source": None,
    }
    _ = size_prev2  # API compat with eval harness
    if d_est <= 0 or dt_s <= 0:
        return out

    growth = None
    signal = "unknown"
    if size_prev > 1e-6 and size_curr > 1e-6:
        growth = (size_curr - size_prev) / size_prev
        out["growth_frac"] = round(float(growth), 5)
        signal = parallax_signal(size_prev, size_curr)
        out["signal"] = signal

    if growth is not None and growth > 1e-6:
        tti = dt_s / growth
        v_close = float(d_est) / tti if tti > 1e-9 else 0.0
        if v_close > TTI_V_CLOSE_MIN_MPS:
            out["closing_speed_mps"] = round(float(v_close), 4)
            out["tti_s"] = round(float(tti), 3)
            out["tti_source"] = "growth"
            return out
        out["closing_speed_mps"] = round(float(v_close), 4)

    if signal == "recede":
        return out
    if d_est_prev is not None and d_est_prev > 0:
        v_close_d = (float(d_est_prev) - float(d_est)) / dt_s
        if v_close_d > max(TTI_V_CLOSE_MIN_MPS * 4, 0.25):
            weak = growth is None or (0 < growth < 0.002)
            if weak:
                out["closing_speed_mps"] = round(float(v_close_d), 4)
                out["tti_s"] = round(float(d_est) / v_close_d, 3)
                out["tti_source"] = "dist_rate"
                return out
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
    """Multi-building floor-scale triangulation (weighted by floors × apparent).

    Primary ref = largest/most-floors facade; if ≥2 buildings, blend d_building and
    floor_px so mid-band ground-plane anchor is stabler (danger zone 30–70 m).
    """
    buildings = [o for o in objects if o.get("class") == "building" and o.get("apparent_px")]
    if not buildings:
        return None
    cals: list[tuple[float, dict[str, float], float]] = []  # weight, cal, cy
    for b in buildings:
        fh = float(b.get("floor_height_m") or FLOOR_HEIGHT_M_DEFAULT)
        n = int(b.get("n_floors") or 4)
        app = float(b["apparent_px"])
        cal = floor_scale_from_building(n, app, fh, focal_px)
        w = max(1.0, float(n)) * max(1.0, app)
        cy = float(b["cy"]) if b.get("cy") is not None else 57.6
        cals.append((w, cal, cy))
    cals.sort(key=lambda t: -t[0])
    primary = cals[0][1]
    if len(cals) == 1:
        primary["building_cy"] = cals[0][2]
        primary["n_buildings_used"] = 1.0
        return primary
    wsum = sum(w for w, _, _ in cals)
    d_blend = sum(w * cal["d_building_m"] for w, cal, _ in cals) / wsum
    floor_px_blend = sum(w * cal["floor_px"] for w, cal, _ in cals) / wsum
    fh_blend = sum(w * cal["floor_height_m"] for w, cal, _ in cals) / wsum
    cy_blend = sum(w * cy for w, _, cy in cals) / wsum
    out = dict(primary)
    out["d_building_m"] = d_blend
    out["floor_px"] = floor_px_blend
    out["floor_height_m"] = fh_blend
    out["meters_per_px"] = fh_blend / max(floor_px_blend, 1e-6)
    out["building_cy"] = cy_blend
    out["n_buildings_used"] = float(len(cals))
    return out


def temporal_ema_distance(
    d_curr: float,
    d_prev: float | None,
    signal: str,
    *,
    beta: float | None = None,
) -> float:
    """Light EMA toward previous estimate; stronger hold when signal=stable.

    Far band (100–200 m): stronger history hold on stable (small apparent Δ is noisy);
    slightly softer follow on approach/recede so parallax can still cut MAE.
    """
    if d_prev is None or d_prev <= 0:
        return d_curr
    if beta is None:
        far = in_far(d_curr) or in_far(d_prev)
        if signal == "stable":
            beta = 0.55 if far else 0.45  # far: trust history more
        elif signal in ("approach", "recede"):
            beta = 0.18 if far else 0.22  # far: follow parallax a bit more
        else:
            beta = 0.30
    return max(0.5, (1.0 - beta) * d_curr + beta * d_prev)
