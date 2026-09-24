#!/usr/bin/env python3
"""CPU floor-scale distance eval + tracking/prediction ablation.

Scale lock: FLOOR-SCALE (building floors 2.4–3.0 m). NO fixed light heights.
Soft car (~4.5 m) / ped (~1.7 m) size priors + fine parallax + closing-speed/TTI.
GT meters loaded ONLY post-hoc from distances_gt.json.
Anti-contam audit every eval; dirty → INVALID.

Metrics:
  - % correct distance by range band (tol 10% if GT<50m, 20% if 50–200m)
  - % correct in DANGER ZONE 30–70 m (+ delta vs baseline 48.69% ~50m)
  - Ablation: tracking±distance; future-pred±distance — overall AND in danger zone
  - v5 future-track: size-rate + median blend; GP low-conf fallback (DZ floors held)

Usage:
  python examples/distance_est/eval_heuristic.py
  python examples/distance_est/eval_heuristic.py --data data/video_synth/distance_est/danger50
  python examples/distance_est/eval_heuristic.py --contam-self-test
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from physics import (
    DEFAULT_FOCAL_PX,
    DANGER_ZONE_M_HI,
    DANGER_ZONE_M_LO,
    PRIORITY_DISTANCE_CLASSES,
    band_for_distance,
    closing_speed_tti,
    estimate_via_floor_scale,
    in_danger_zone,
    parallax_signal,
    pick_building_scale,
    predict_future_distance_v5,
    predict_next_distance,
    refine_with_parallax,
    size_rate_next_distance,
    temporal_ema_distance,
    track_associate_greedy,
    within_tol,
)

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "video_synth" / "distance_est"
AUDIT_DIR = ROOT / "data" / "eval_audit"
BASELINE_50M_PCT = 48.69
BASELINE_COMMIT = "bcbcdc8"


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " ET"


def build_prompt(meta: dict[str, Any], t: int, *, inject_gt: dict | None = None) -> str:
    """Visible history only. Floor meta OK (scale ref). GT meters NEVER unless inject test."""
    fr = meta["frames"][t]
    lines = [
        "DOMAIN=distance_est STYLE=street_floor_scale",
        "SCALE_LOCK=FLOOR-SCALE building floors 2.4–3.0m — NO fixed light heights; soft car~4.5m ped~1.7m priors",
        f"Task: estimate meters to priority objects (cars, intersections, stop signs, pedestrians, lights) at t={t}.",
        "Signal: building-floor scale + fine parallax + closing-speed.",
        f"Street={meta.get('street_name')} focal_px={meta.get('focal_px')}",
        "Objects:",
    ]
    for o in fr["objects"]:
        bits = [f"{o['id']}({o['class']} cx={o['cx']} cy={o['cy']} app_px={o['apparent_px']} motion={o.get('motion_hint')})"]
        if o["class"] == "building":
            bits.append(f"floors={o.get('n_floors')} floor_h_m={o.get('floor_height_m')} floor_px={o.get('floor_px')}")
        lines.append("  " + " ".join(bits))
    lines.append('Output JSON: [{id, class, est_m, confidence}, ...]')
    if inject_gt is not None:
        lines.append("WARNING_INJECTED_GT=" + json.dumps(inject_gt))
    return "\n".join(lines)


def prompt_touches_gt(prompt: str, gt: dict[str, Any]) -> bool:
    if "WARNING_INJECTED_GT" in prompt:
        return True
    if "gt_m" in prompt or "_gt_m" in prompt or "distances_gt" in prompt:
        return True
    if '"gt_m"' in prompt or "'gt_m'" in prompt:
        return True
    return False


def estimate_frame(
    objects: list[dict[str, Any]],
    prev_by_id: dict[str, dict[str, Any]] | None,
    focal_px: float,
) -> list[dict[str, Any]]:
    scale = pick_building_scale(objects, focal_px)
    out = []
    if scale is None:
        for o in objects:
            out.append({
                "id": o["id"], "class": o["class"],
                "est_m": None, "confidence": 0.0,
                "method": "no_building_scale", "parallax": "unknown",
                "closing_speed_mps": None, "tti_s": None, "growth_frac": None,
            })
        return out

    buildings = [o for o in objects if o.get("class") == "building"]
    bcy = scale.get("building_cy")
    if bcy is None and buildings:
        bcy = float(buildings[0]["cy"])
    for o in objects:
        est, conf, method = estimate_via_floor_scale(o, scale, focal_px, building_cy=bcy)
        para = "unknown"
        cs: dict[str, Any] = {"closing_speed_mps": None, "tti_s": None, "growth_frac": None, "signal": "unknown"}
        honesty_unknown = False
        if prev_by_id and o["id"] in prev_by_id and est is not None:
            prev = prev_by_id[o["id"]]
            sp = float(prev.get("apparent_px") or 1)
            sc = float(o["apparent_px"])
            para = parallax_signal(sp, sc)
            if prev.get("est_m"):
                est, conf = refine_with_parallax(est, para, sp, sc)
                method = method + "+parallax"
                # Temporal EMA + closing-speed hold (finer mid-band)
                est = temporal_ema_distance(float(est), float(prev["est_m"]), para)
                method = method + "+ema"
            cs = closing_speed_tti(sp, sc, float(est))
        # Honesty: very low confidence → unknown (excluded from distance %; counted)
        if est is not None and conf < 0.38 and "honesty" in method:
            honesty_unknown = True
            est = None
            method = method + "+unknown"
            para = "unknown"
        out.append({
            "id": o["id"], "class": o["class"],
            "est_m": None if est is None else round(float(est), 3),
            "confidence": round(conf, 3),
            "method": method,
            "parallax": para,
            "closing_speed_mps": cs.get("closing_speed_mps"),
            "tti_s": cs.get("tti_s"),
            "growth_frac": cs.get("growth_frac"),
            "honesty_unknown": honesty_unknown,
            "cx": o["cx"], "cy": o["cy"],
            "apparent_px": o["apparent_px"],
        })
    return out


def eval_tracking(seq_meta: dict, seq_gt: dict, *, use_distance: bool, danger_only: bool = False) -> dict[str, Any]:
    focal = float(seq_meta.get("focal_px") or DEFAULT_FOCAL_PX)
    frames = seq_meta["frames"]
    gt_by_t = {fr["t"]: {o["id"]: o for o in fr["objects"]} for fr in seq_gt["frames"]}
    correct = 0
    total = 0
    prev_by_anon: list[dict[str, Any]] = []
    anon_to_real: dict[str, str] = {}
    prev_est = None

    for fr in frames:
        t = fr["t"]
        ests = estimate_frame(fr["objects"], prev_est, focal)
        est_map = {e["id"]: e for e in ests}
        gt_map = gt_by_t.get(t, {})

        curr_anon = []
        curr_map = {}
        for i, o in enumerate(fr["objects"]):
            if danger_only:
                g = gt_map.get(o["id"])
                if g is None or not in_danger_zone(float(g.get("gt_m", -1))):
                    continue
                if g["class"] not in PRIORITY_DISTANCE_CLASSES:
                    continue
            aid = f"c{i}"
            e = est_map[o["id"]]
            curr_anon.append({
                "id": aid, "class": o["class"], "cx": o["cx"], "cy": o["cy"],
                "est_m": e.get("est_m"), "apparent_px": o["apparent_px"],
            })
            curr_map[aid] = o["id"]

        if prev_by_anon and curr_anon:
            matches = track_associate_greedy(prev_by_anon, curr_anon, use_distance=use_distance)
            for pid, cid, _ in matches:
                total += 1
                if anon_to_real.get(pid) == curr_map[cid]:
                    correct += 1

        prev_by_anon = []
        anon_to_real = {}
        for i, o in enumerate(fr["objects"]):
            if danger_only:
                g = gt_map.get(o["id"])
                if g is None or not in_danger_zone(float(g.get("gt_m", -1))):
                    continue
                if g["class"] not in PRIORITY_DISTANCE_CLASSES:
                    continue
            aid = f"p{i}"
            e = est_map[o["id"]]
            prev_by_anon.append({
                "id": aid, "class": o["class"], "cx": o["cx"], "cy": o["cy"],
                "est_m": e.get("est_m"), "apparent_px": o["apparent_px"],
            })
            anon_to_real[aid] = o["id"]

        prev_est = {o["id"]: {**o, **est_map[o["id"]]} for o in fr["objects"]}

    return {
        "mode": ("tracking+distance" if use_distance else "tracking-only") + ("_danger" if danger_only else ""),
        "n": total,
        "correct": correct,
        "pct": round(100.0 * correct / total, 2) if total else None,
    }


def eval_future_pred(seq_meta: dict, seq_gt: dict, *, use_distance: bool, danger_only: bool = False) -> dict[str, Any]:
    """Future depth / position pred — v5 tip-future-track polish.

    High-conf +distance: median(legacy blend, size-rate, depth-vel).
    Low-conf / tracking-only: size-rate on est_m when available else GP on
    current frame (no poisoned fake-apparent floor-scale projection).
    Distance *estimator* path unchanged — DZ floors held via estimate_frame.
    """
    focal = float(seq_meta.get("focal_px") or DEFAULT_FOCAL_PX)
    gt_by_t = {fr["t"]: {o["id"]: o for o in fr["objects"]} for fr in seq_gt["frames"]}
    frames = seq_meta["frames"]
    prev_est: dict[str, dict] | None = None
    n = c = 0
    n_pos = c_pos = 0

    for fi, fr in enumerate(frames[:-1]):
        ests = estimate_frame(fr["objects"], prev_est, focal)
        est_map = {e["id"]: e for e in ests}
        next_fr = frames[fi + 1]
        next_gt = gt_by_t[next_fr["t"]]
        next_pos = {o["id"]: o for o in next_fr["objects"]}
        curr_gt = gt_by_t[fr["t"]]
        scale = pick_building_scale(fr["objects"], focal)

        for o in fr["objects"]:
            if o["class"] not in PRIORITY_DISTANCE_CLASSES:
                continue
            g0 = curr_gt.get(o["id"])
            if danger_only:
                if g0 is None or not in_danger_zone(float(g0.get("gt_m", -1))):
                    continue
            e = est_map[o["id"]]
            if o["id"] not in next_gt:
                continue
            if prev_est and o["id"] in prev_est:
                dx = o["cx"] - prev_est[o["id"]]["cx"]
                dy = o["cy"] - prev_est[o["id"]]["cy"]
                size_prev = float(prev_est[o["id"]]["apparent_px"])
                d_prev = prev_est[o["id"]].get("est_m")
            else:
                dx = dy = 0.0
                size_prev = None
                d_prev = None
            pred_cx = o["cx"] + dx
            pred_cy = o["cy"] + dy
            np_ = next_pos.get(o["id"])
            if np_:
                n_pos += 1
                if (pred_cx - np_["cx"]) ** 2 + (pred_cy - np_["cy"]) ** 2 <= 20 ** 2:
                    c_pos += 1

            size_curr = float(o["apparent_px"])
            d_hat: float | None = None
            if use_distance:
                d_hat, _src = predict_future_distance_v5(
                    e,
                    d_prev=float(d_prev) if d_prev is not None else None,
                    size_prev=size_prev,
                    size_curr=size_curr,
                )
                if d_hat is None:
                    # Low-conf honesty: prefer current-frame GP over size-poisoned fake
                    if scale is not None:
                        d_hat, _, _ = estimate_via_floor_scale(o, scale, focal)
                    elif e.get("est_m") is not None and size_prev is not None:
                        d_hat = size_rate_next_distance(float(e["est_m"]), size_prev, size_curr)
            else:
                # tracking-only: size-rate on est when present, else GP
                if e.get("est_m") is not None:
                    d_hat = size_rate_next_distance(float(e["est_m"]), size_prev, size_curr)
                elif scale is not None:
                    d_hat, _, _ = estimate_via_floor_scale(o, scale, focal)

            n += 1
            if d_hat is not None and within_tol(d_hat, float(next_gt[o["id"]]["gt_m"])):
                c += 1

        prev_est = {o["id"]: {**o, **est_map[o["id"]]} for o in fr["objects"]}

    return {
        "mode": ("pred+distance" if use_distance else "pred-tracking-only") + ("_danger" if danger_only else ""),
        "distance_pred_n": n,
        "distance_pred_correct": c,
        "distance_pred_pct": round(100.0 * c / n, 2) if n else None,
        "position_pred_n": n_pos,
        "position_pred_correct": c_pos,
        "position_pred_pct": round(100.0 * c_pos / n_pos, 2) if n_pos else None,
    }


def run_eval(data_dir: Path, *, out_name: str = "EVAL_FLOOR_SCALE_CPU.json") -> dict[str, Any]:
    split = json.loads((data_dir / "SPLIT.json").read_text())
    eval_ids = split["eval_ids"]
    tag = "danger50" if "danger50" in str(data_dir) else "distance"
    audit_path = AUDIT_DIR / f"{tag}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    all_dist_rows = []
    band_acc: dict[str, dict[str, int]] = {}
    danger_acc = {"n": 0, "correct": 0}
    band50_acc = {"n": 0, "correct": 0}  # ~50m band for delta vs baseline
    dirty = 0
    track_only = {"n": 0, "correct": 0}
    track_dist = {"n": 0, "correct": 0}
    track_only_dz = {"n": 0, "correct": 0}
    track_dist_dz = {"n": 0, "correct": 0}
    pred_only = {"n": 0, "correct": 0, "pos_n": 0, "pos_c": 0}
    pred_dist = {"n": 0, "correct": 0, "pos_n": 0, "pos_c": 0}
    pred_only_dz = {"n": 0, "correct": 0, "pos_n": 0, "pos_c": 0}
    pred_dist_dz = {"n": 0, "correct": 0, "pos_n": 0, "pos_c": 0}
    tti_rows = 0
    honesty_unknown_n = 0

    for sid in eval_ids:
        seq_dir = data_dir / sid
        meta = json.loads((seq_dir / "meta.json").read_text())
        gt = json.loads((seq_dir / "distances_gt.json").read_text())
        meta_blob = json.dumps(meta)
        if "gt_m" in meta_blob or '"_gt_m"' in meta_blob:
            dirty += 1
            with audit_path.open("a") as af:
                af.write(json.dumps({"seq_id": sid, "invalid": True, "reason": "gt_in_meta", "ts": _now()}) + "\n")
            continue

        focal = float(meta.get("focal_px") or DEFAULT_FOCAL_PX)
        prev = None
        for fr in meta["frames"]:
            t = fr["t"]
            prompt = build_prompt(meta, t)
            gt_fr = next(x for x in gt["frames"] if x["t"] == t)
            touches = prompt_touches_gt(prompt, gt)
            preds = estimate_frame(fr["objects"], prev, focal)
            for p in preds:
                g = next((x for x in gt_fr["objects"] if x["id"] == p["id"]), None)
                if g is None or g["class"] not in PRIORITY_DISTANCE_CLASSES:
                    continue
                if p.get("est_m") is None:
                    if p.get("honesty_unknown"):
                        honesty_unknown_n += 1
                    continue
                band = g["gt_band"]
                band_acc.setdefault(band, {"n": 0, "correct": 0})
                band_acc[band]["n"] += 1
                ok = within_tol(float(p["est_m"]), float(g["gt_m"]))
                if ok:
                    band_acc[band]["correct"] += 1
                gt_m = float(g["gt_m"])
                if in_danger_zone(gt_m):
                    danger_acc["n"] += 1
                    if ok:
                        danger_acc["correct"] += 1
                if band == "~50m":
                    band50_acc["n"] += 1
                    if ok:
                        band50_acc["correct"] += 1
                if p.get("tti_s") is not None:
                    tti_rows += 1
                all_dist_rows.append({
                    "seq_id": sid, "t": t, "id": p["id"], "class": g["class"],
                    "gt_m": g["gt_m"], "est_m": p["est_m"], "band": band,
                    "in_danger_zone": in_danger_zone(gt_m),
                    "correct": ok, "method": p.get("method"), "parallax": p.get("parallax"),
                    "closing_speed_mps": p.get("closing_speed_mps"),
                    "tti_s": p.get("tti_s"),
                })

            with audit_path.open("a") as af:
                af.write(json.dumps({
                    "ts": _now(), "seq_id": sid, "t": t,
                    "prompt_preview": prompt[:400],
                    "prompt_touches_gt": touches,
                    "invalid": touches,
                    "n_preds": len(preds),
                    "memory": "heuristic_prev_est_only",
                    "scale_lock": "FLOOR-SCALE",
                    "soft_priors": "car~4.5m ped~1.7m",
                    "retrieval": None,
                    "tool": "floor_scale+parallax+closing_speed",
                }) + "\n")
            if touches:
                dirty += 1
            prev = {o["id"]: {**o, **next(p for p in preds if p["id"] == o["id"])} for o in fr["objects"]}

        for use_d, bucket, bucket_dz in [
            (False, track_only, track_only_dz),
            (True, track_dist, track_dist_dz),
        ]:
            tr = eval_tracking(meta, gt, use_distance=use_d, danger_only=False)
            bucket["n"] += tr["n"]; bucket["correct"] += tr["correct"]
            trd = eval_tracking(meta, gt, use_distance=use_d, danger_only=True)
            bucket_dz["n"] += trd["n"]; bucket_dz["correct"] += trd["correct"]

        for use_d, bucket, bucket_dz in [
            (False, pred_only, pred_only_dz),
            (True, pred_dist, pred_dist_dz),
        ]:
            pr = eval_future_pred(meta, gt, use_distance=use_d, danger_only=False)
            bucket["n"] += pr["distance_pred_n"]; bucket["correct"] += pr["distance_pred_correct"]
            bucket["pos_n"] += pr["position_pred_n"]; bucket["pos_c"] += pr["position_pred_correct"]
            prd = eval_future_pred(meta, gt, use_distance=use_d, danger_only=True)
            bucket_dz["n"] += prd["distance_pred_n"]; bucket_dz["correct"] += prd["distance_pred_correct"]
            bucket_dz["pos_n"] += prd["position_pred_n"]; bucket_dz["pos_c"] += prd["position_pred_correct"]

    def pct(n, c):
        return round(100.0 * c / n, 2) if n else None

    by_band = {
        b: {"n": st["n"], "correct": st["correct"], "pct": pct(st["n"], st["correct"])}
        for b, st in sorted(band_acc.items())
    }
    n = sum(st["n"] for st in band_acc.values())
    c = sum(st["correct"] for st in band_acc.values())
    dz_pct = pct(danger_acc["n"], danger_acc["correct"])
    b50_pct = pct(band50_acc["n"], band50_acc["correct"])
    delta_vs_baseline = None if b50_pct is None else round(b50_pct - BASELINE_50M_PCT, 2)
    delta_dz_vs_baseline = None if dz_pct is None else round(dz_pct - BASELINE_50M_PCT, 2)

    def _err_stats(rows):
        if not rows:
            return None
        abs_err = [abs(float(r["est_m"]) - float(r["gt_m"])) for r in rows]
        rel = [abs(float(r["est_m"]) - float(r["gt_m"])) / max(float(r["gt_m"]), 1e-6) for r in rows]
        rel_s = sorted(rel)
        mid = rel_s[len(rel_s) // 2]
        return {
            "mae_m": round(sum(abs_err) / len(abs_err), 3),
            "mean_rel_err": round(sum(rel) / len(rel), 4),
            "median_rel_err": round(mid, 4),
            "note": "within-tol can saturate on synth pinhole invert; MAE shows residual meters",
        }

    err_all = _err_stats(all_dist_rows)
    err_dz = _err_stats([r for r in all_dist_rows if r.get("in_danger_zone")])

    result = {
        "ts": _now(),
        "domain": "distance_est",
        "data_dir": str(data_dir.relative_to(ROOT)) if str(data_dir).startswith(str(ROOT)) else str(data_dir),
        "scale_lock": "FLOOR-SCALE",
        "no_fixed_object_heights": True,
        "soft_size_priors": {"car_length_m": 4.5, "car_height_m": 1.55, "ped_height_m": 1.7},
        "predictor": "floor_scale_parallax_size_prior_closing_speed_v5_future_track",
        "n_eval_seq": len(eval_ids),
        "distance": {
            "n": n, "correct": c, "pct": pct(n, c),
            "by_band": by_band,
            "tol": {"lt_50m": "10%", "50_to_200m": "20%"},
            "priority_classes": list(PRIORITY_DISTANCE_CLASSES),
            "error_stats": err_all,
        },
        "danger_zone_30_70m": {
            "lo_m": DANGER_ZONE_M_LO,
            "hi_m": DANGER_ZONE_M_HI,
            "n": danger_acc["n"],
            "correct": danger_acc["correct"],
            "pct": dz_pct,
            "delta_pp_vs_baseline_50m": delta_dz_vs_baseline,
            "error_stats": err_dz,
        },
        "band_50m_vs_baseline": {
            "baseline_pct": BASELINE_50M_PCT,
            "baseline_commit": BASELINE_COMMIT,
            "n": band50_acc["n"],
            "correct": band50_acc["correct"],
            "pct": b50_pct,
            "delta_pp": delta_vs_baseline,
        },
        "closing_speed": {
            "tti_estimates_emitted": tti_rows,
            "note": "growth_frac → closing_speed_mps → tti_s when approaching",
        },
        "honesty": {
            "unknown_when_unsure_n": honesty_unknown_n,
            "note": "low-conf honesty paths emit unknown (excluded from %; not forced wrong guess)",
        },
        "ablation_tracking": {
            "tracking_only": {"n": track_only["n"], "correct": track_only["correct"], "pct": pct(track_only["n"], track_only["correct"])},
            "tracking_plus_distance": {"n": track_dist["n"], "correct": track_dist["correct"], "pct": pct(track_dist["n"], track_dist["correct"])},
            "danger_zone": {
                "tracking_only": {"n": track_only_dz["n"], "correct": track_only_dz["correct"], "pct": pct(track_only_dz["n"], track_only_dz["correct"])},
                "tracking_plus_distance": {"n": track_dist_dz["n"], "correct": track_dist_dz["correct"], "pct": pct(track_dist_dz["n"], track_dist_dz["correct"])},
            },
        },
        "ablation_future_pred": {
            "tracking_only": {
                "distance_pred_pct": pct(pred_only["n"], pred_only["correct"]),
                "n": pred_only["n"], "correct": pred_only["correct"],
                "position_pred_pct": pct(pred_only["pos_n"], pred_only["pos_c"]),
            },
            "plus_distance": {
                "distance_pred_pct": pct(pred_dist["n"], pred_dist["correct"]),
                "n": pred_dist["n"], "correct": pred_dist["correct"],
                "position_pred_pct": pct(pred_dist["pos_n"], pred_dist["pos_c"]),
            },
            "danger_zone": {
                "tracking_only": {
                    "distance_pred_pct": pct(pred_only_dz["n"], pred_only_dz["correct"]),
                    "n": pred_only_dz["n"], "correct": pred_only_dz["correct"],
                    "position_pred_pct": pct(pred_only_dz["pos_n"], pred_only_dz["pos_c"]),
                },
                "plus_distance": {
                    "distance_pred_pct": pct(pred_dist_dz["n"], pred_dist_dz["correct"]),
                    "n": pred_dist_dz["n"], "correct": pred_dist_dz["correct"],
                    "position_pred_pct": pct(pred_dist_dz["pos_n"], pred_dist_dz["pos_c"]),
                },
            },
            "note": "Future depth prediction proxy (inverse-planning-style along camera axis); danger-zone slice reported separately.",
        },
        "anti_contam": {
            "audit_path": str(audit_path.relative_to(ROOT)),
            "dirty_count": dirty,
            "status": "INVALID" if dirty else "CLEAN",
        },
        "gpu": "deferred — heuristic CPU only; LoRA queued behind existing waiters",
        "caveat": "CPU heuristic inverts synth pinhole (cy↔depth); tol@10/20% can saturate. Not a VLM claim. Residual via error_stats MAE.",
        "sample_rows": all_dist_rows[:15],
    }
    out_json = data_dir / out_name
    out_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def contam_self_test(data_dir: Path) -> dict[str, Any]:
    split = json.loads((data_dir / "SPLIT.json").read_text())
    sid = split["eval_ids"][0]
    meta = json.loads((data_dir / sid / "meta.json").read_text())
    gt = json.loads((data_dir / sid / "distances_gt.json").read_text())
    clean = build_prompt(meta, 0)
    injected = build_prompt(meta, 0, inject_gt={"gt_m": gt["frames"][0]["objects"][0]["gt_m"]})
    clean_hit = prompt_touches_gt(clean, gt)
    dirty_hit = prompt_touches_gt(injected, gt)
    meta_clean = "gt_m" not in json.dumps(meta)
    passed = (not clean_hit) and dirty_hit and meta_clean
    out = {
        "passed": passed,
        "clean_prompt_touches_gt": clean_hit,
        "injected_prompt_touches_gt": dirty_hit,
        "meta_has_no_gt_m": meta_clean,
        "scale_lock": "FLOOR-SCALE",
    }
    (data_dir / "ANTI_CONTAM_SELFTEST.json").write_text(json.dumps(out, indent=2) + "\n")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=DATA)
    ap.add_argument("--out-name", type=str, default="EVAL_FLOOR_SCALE_CPU.json")
    ap.add_argument("--contam-self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.contam_self_test:
        r = contam_self_test(args.data)
        print(json.dumps(r, indent=2))
        sys.exit(0 if r["passed"] else 1)
    r = run_eval(args.data, out_name=args.out_name)
    print(json.dumps({
        "distance_pct": r["distance"]["pct"],
        "by_band": r["distance"]["by_band"],
        "danger_zone_30_70m": r["danger_zone_30_70m"],
        "band_50m_vs_baseline": r["band_50m_vs_baseline"],
        "ablation_tracking": r["ablation_tracking"],
        "ablation_future_pred": {
            "tracking_only": r["ablation_future_pred"]["tracking_only"]["distance_pred_pct"],
            "plus_distance": r["ablation_future_pred"]["plus_distance"]["distance_pred_pct"],
            "danger_zone": {
                "tracking_only": r["ablation_future_pred"]["danger_zone"]["tracking_only"]["distance_pred_pct"],
                "plus_distance": r["ablation_future_pred"]["danger_zone"]["plus_distance"]["distance_pred_pct"],
            },
        },
        "anti_contam": r["anti_contam"],
        "scale_lock": r["scale_lock"],
    }, indent=2))


if __name__ == "__main__":
    main()
