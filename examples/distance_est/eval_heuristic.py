#!/usr/bin/env python3
"""CPU floor-scale distance eval + tracking/prediction ablation.

Scale lock: FLOOR-SCALE (building floors 2.4–3.0 m). NO fixed object heights.
GT meters loaded ONLY post-hoc from distances_gt.json.
Anti-contam audit every eval; dirty → INVALID.

Metrics:
  - % correct distance by range band (tol 10% if GT<50m, 20% if 50–200m)
  - Ablation: tracking±distance vs tracking-only
  - Ablation: next-frame distance prediction ±floor-calibrated signal
    (proxy for whether distance helps inverse-planning-style future pred)

Usage:
  python examples/distance_est/eval_heuristic.py
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
    PRIORITY_DISTANCE_CLASSES,
    band_for_distance,
    estimate_via_floor_scale,
    parallax_signal,
    pick_building_scale,
    predict_next_distance,
    refine_with_parallax,
    track_associate_greedy,
    within_tol,
)

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "video_synth" / "distance_est"
AUDIT_DIR = ROOT / "data" / "eval_audit"


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " ET"


def build_prompt(meta: dict[str, Any], t: int, *, inject_gt: dict | None = None) -> str:
    """Visible history only. Floor meta OK (scale ref). GT meters NEVER unless inject test."""
    fr = meta["frames"][t]
    lines = [
        "DOMAIN=distance_est STYLE=street_floor_scale",
        "SCALE_LOCK=FLOOR-SCALE building floors 2.4–3.0m — NO fixed object heights",
        f"Task: estimate meters to priority objects (cars, intersections, stop signs, pedestrians, lights) at t={t}.",
        "Signal: building-floor scale + frame-to-frame parallax.",
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
    """Leak check: explicit GT keys / injection only (not numeric cx coincidence)."""
    if "WARNING_INJECTED_GT" in prompt:
        return True
    if "gt_m" in prompt or "_gt_m" in prompt or "distances_gt" in prompt:
        return True
    # explicit JSON-ish gt dump
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
            })
        return out

    buildings = [o for o in objects if o.get("class") == "building"]
    bcy = float(buildings[0]["cy"]) if buildings else None
    for o in objects:
        est, conf, method = estimate_via_floor_scale(o, scale, focal_px, building_cy=bcy)
        para = "unknown"
        if prev_by_id and o["id"] in prev_by_id and est is not None:
            prev = prev_by_id[o["id"]]
            para = parallax_signal(float(prev.get("apparent_px") or 1), float(o["apparent_px"]))
            if prev.get("est_m"):
                est, conf = refine_with_parallax(est, para, float(prev["apparent_px"]), float(o["apparent_px"]))
                method = method + "+parallax"
        out.append({
            "id": o["id"], "class": o["class"],
            "est_m": None if est is None else round(float(est), 3),
            "confidence": round(conf, 3),
            "method": method,
            "parallax": para,
            "cx": o["cx"], "cy": o["cy"],
            "apparent_px": o["apparent_px"],
        })
    return out


def score_distances(
    preds: list[dict[str, Any]],
    gt_objs: list[dict[str, Any]],
    *,
    priority_only: bool = True,
) -> dict[str, Any]:
    gt_map = {o["id"]: o for o in gt_objs}
    bands: dict[str, dict[str, int]] = {}
    rows = []
    for p in preds:
        g = gt_map.get(p["id"])
        if g is None:
            continue
        if priority_only and g["class"] not in PRIORITY_DISTANCE_CLASSES:
            continue
        if p.get("est_m") is None:
            continue
        band = g["gt_band"]
        bands.setdefault(band, {"n": 0, "correct": 0})
        ok = within_tol(float(p["est_m"]), float(g["gt_m"]))
        bands[band]["n"] += 1
        if ok:
            bands[band]["correct"] += 1
        rows.append({
            "id": p["id"], "class": g["class"], "gt_m": g["gt_m"], "est_m": p["est_m"],
            "band": band, "correct": ok, "confidence": p.get("confidence"),
            "method": p.get("method"), "parallax": p.get("parallax"),
        })
    by_band = {}
    for b, st in bands.items():
        by_band[b] = {
            "n": st["n"],
            "correct": st["correct"],
            "pct": round(100.0 * st["correct"] / st["n"], 2) if st["n"] else None,
        }
    n = sum(st["n"] for st in bands.values())
    c = sum(st["correct"] for st in bands.values())
    return {
        "n": n,
        "correct": c,
        "pct": round(100.0 * c / n, 2) if n else None,
        "by_band": by_band,
        "rows_sample": rows[:12],
    }


def eval_tracking(seq_meta: dict, seq_gt: dict, *, use_distance: bool) -> dict[str, Any]:
    """ID association accuracy vs GT id continuity (same id across frames)."""
    focal = float(seq_meta.get("focal_px") or DEFAULT_FOCAL_PX)
    frames = seq_meta["frames"]
    gt_frames = {fr["t"]: fr for fr in seq_gt["frames"]}
    prev_est = None
    prev_meta_objs = None
    # Build predicted tracks by greedy assoc; score: matched pair shares GT id
    # (we know true ids in meta for synth — association uses only cx/cy/class/+est)
    # For fair ID-free assoc test: hide ids at associate time.
    correct = 0
    total = 0
    prev_by_anon: list[dict[str, Any]] = []
    anon_to_real: dict[str, str] = {}

    for fr in frames:
        t = fr["t"]
        ests = estimate_frame(fr["objects"], prev_est, focal)
        est_map = {e["id"]: e for e in ests}

        # anonymize current
        curr_anon = []
        curr_map = {}
        for i, o in enumerate(fr["objects"]):
            aid = f"c{i}"
            e = est_map[o["id"]]
            row = {
                "id": aid, "class": o["class"], "cx": o["cx"], "cy": o["cy"],
                "est_m": e.get("est_m"), "apparent_px": o["apparent_px"],
            }
            curr_anon.append(row)
            curr_map[aid] = o["id"]

        if prev_by_anon:
            matches = track_associate_greedy(prev_by_anon, curr_anon, use_distance=use_distance)
            for pid, cid, _ in matches:
                total += 1
                if anon_to_real.get(pid) == curr_map[cid]:
                    correct += 1

        # roll
        prev_by_anon = []
        anon_to_real = {}
        for i, o in enumerate(fr["objects"]):
            aid = f"p{i}"
            e = est_map[o["id"]]
            prev_by_anon.append({
                "id": aid, "class": o["class"], "cx": o["cx"], "cy": o["cy"],
                "est_m": e.get("est_m"), "apparent_px": o["apparent_px"],
            })
            anon_to_real[aid] = o["id"]

        prev_est = {o["id"]: {**o, **est_map[o["id"]]} for o in fr["objects"]}
        _ = gt_frames.get(t)  # loaded post-hoc only for scoring elsewhere

    return {
        "mode": "tracking+distance" if use_distance else "tracking-only",
        "n": total,
        "correct": correct,
        "pct": round(100.0 * correct / total, 2) if total else None,
    }


def eval_future_pred(seq_meta: dict, seq_gt: dict, *, use_distance: bool) -> dict[str, Any]:
    """Next-frame distance prediction vs GT (inverse-planning-style along depth).

    tracking-only: predict next apparent size rate without meters, convert via
    floor scale at next frame only after the fact for scoring... Actually:
      - without distance: predict next cx,cy by constant image velocity; score
        position hit (loose) — weak depth signal
      - with distance: predict next gt_m via constant depth-rate; score with tol
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

        for o in fr["objects"]:
            if o["class"] not in PRIORITY_DISTANCE_CLASSES:
                continue
            e = est_map[o["id"]]
            if o["id"] not in next_gt:
                continue
            # position extrapolation (always)
            if prev_est and o["id"] in prev_est:
                dx = o["cx"] - prev_est[o["id"]]["cx"]
                dy = o["cy"] - prev_est[o["id"]]["cy"]
            else:
                dx = dy = 0.0
            pred_cx = o["cx"] + dx
            pred_cy = o["cy"] + dy
            np_ = next_pos.get(o["id"])
            if np_:
                n_pos += 1
                if (pred_cx - np_["cx"]) ** 2 + (pred_cy - np_["cy"]) ** 2 <= 20 ** 2:
                    c_pos += 1

            if use_distance and e.get("est_m") is not None:
                d_prev = prev_est[o["id"]].get("est_m") if prev_est and o["id"] in prev_est else None
                d_vel = predict_next_distance(float(e["est_m"]), float(d_prev) if d_prev else None)
                # Blend hold-last (stable) with parallax/depth-rate (motion) —
                # pure velocity overshoots when floor-scale est is noisy frame-to-frame.
                para = e.get("parallax") or "unknown"
                w_vel = 0.55 if para in ("approach", "recede") else 0.20
                d_hat = (1 - w_vel) * float(e["est_m"]) + w_vel * d_vel
                n += 1
                if within_tol(d_hat, float(next_gt[o["id"]]["gt_m"])):
                    c += 1
            elif not use_distance:
                # image-size rate → crude next distance via floor scale at *current*
                # (no explicit meters memory): use apparent growth only as motion,
                # score as incorrect depth unless stable — honest weak baseline
                n += 1
                # hold last apparent→ if we don't have meters, use building scale
                # at next frame on predicted size
                scale = pick_building_scale(fr["objects"], focal)
                if scale and prev_est and o["id"] in prev_est:
                    from physics import estimate_via_floor_scale as _est
                    fake = dict(o)
                    # predict next size
                    sp = float(prev_est[o["id"]]["apparent_px"])
                    sc = float(o["apparent_px"])
                    fake["apparent_px"] = sc * (sc / sp if sp > 1 else 1.0)
                    d_hat, _, _ = _est(fake, scale, focal)
                    if d_hat is not None and within_tol(d_hat, float(next_gt[o["id"]]["gt_m"])):
                        c += 1
                # else miss

        prev_est = {o["id"]: {**o, **est_map[o["id"]]} for o in fr["objects"]}

    return {
        "mode": "pred+distance" if use_distance else "pred-tracking-only",
        "distance_pred_n": n,
        "distance_pred_correct": c,
        "distance_pred_pct": round(100.0 * c / n, 2) if n else None,
        "position_pred_n": n_pos,
        "position_pred_correct": c_pos,
        "position_pred_pct": round(100.0 * c_pos / n_pos, 2) if n_pos else None,
    }


def run_eval(data_dir: Path) -> dict[str, Any]:
    split = json.loads((data_dir / "SPLIT.json").read_text())
    eval_ids = split["eval_ids"]
    audit_path = AUDIT_DIR / f"distance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    all_dist_rows = []
    band_acc: dict[str, dict[str, int]] = {}
    dirty = 0
    track_only = {"n": 0, "correct": 0}
    track_dist = {"n": 0, "correct": 0}
    pred_only = {"n": 0, "correct": 0, "pos_n": 0, "pos_c": 0}
    pred_dist = {"n": 0, "correct": 0, "pos_n": 0, "pos_c": 0}

    for sid in eval_ids:
        seq_dir = data_dir / sid
        meta = json.loads((seq_dir / "meta.json").read_text())
        gt = json.loads((seq_dir / "distances_gt.json").read_text())
        # assert anti-contam structure
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
            # score post-hoc
            for p in preds:
                g = next((x for x in gt_fr["objects"] if x["id"] == p["id"]), None)
                if g is None or g["class"] not in PRIORITY_DISTANCE_CLASSES:
                    continue
                if p.get("est_m") is None:
                    continue
                band = g["gt_band"]
                band_acc.setdefault(band, {"n": 0, "correct": 0})
                band_acc[band]["n"] += 1
                ok = within_tol(float(p["est_m"]), float(g["gt_m"]))
                if ok:
                    band_acc[band]["correct"] += 1
                all_dist_rows.append({
                    "seq_id": sid, "t": t, "id": p["id"], "class": g["class"],
                    "gt_m": g["gt_m"], "est_m": p["est_m"], "band": band,
                    "correct": ok, "method": p.get("method"), "parallax": p.get("parallax"),
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
                    "retrieval": None,
                    "tool": "floor_scale+parallax",
                }) + "\n")
            if touches:
                dirty += 1
            prev = {o["id"]: {**o, **next(p for p in preds if p["id"] == o["id"])} for o in fr["objects"]}

        tr0 = eval_tracking(meta, gt, use_distance=False)
        tr1 = eval_tracking(meta, gt, use_distance=True)
        track_only["n"] += tr0["n"]; track_only["correct"] += tr0["correct"]
        track_dist["n"] += tr1["n"]; track_dist["correct"] += tr1["correct"]

        pr0 = eval_future_pred(meta, gt, use_distance=False)
        pr1 = eval_future_pred(meta, gt, use_distance=True)
        pred_only["n"] += pr0["distance_pred_n"]; pred_only["correct"] += pr0["distance_pred_correct"]
        pred_only["pos_n"] += pr0["position_pred_n"]; pred_only["pos_c"] += pr0["position_pred_correct"]
        pred_dist["n"] += pr1["distance_pred_n"]; pred_dist["correct"] += pr1["distance_pred_correct"]
        pred_dist["pos_n"] += pr1["position_pred_n"]; pred_dist["pos_c"] += pr1["position_pred_correct"]

    def pct(n, c):
        return round(100.0 * c / n, 2) if n else None

    by_band = {
        b: {"n": st["n"], "correct": st["correct"], "pct": pct(st["n"], st["correct"])}
        for b, st in sorted(band_acc.items())
    }
    n = sum(st["n"] for st in band_acc.values())
    c = sum(st["correct"] for st in band_acc.values())

    result = {
        "ts": _now(),
        "domain": "distance_est",
        "scale_lock": "FLOOR-SCALE",
        "no_fixed_object_heights": True,
        "predictor": "floor_scale_parallax_heuristic",
        "n_eval_seq": len(eval_ids),
        "distance": {
            "n": n, "correct": c, "pct": pct(n, c),
            "by_band": by_band,
            "tol": {"lt_50m": "10%", "50_to_200m": "20%"},
            "priority_classes": list(PRIORITY_DISTANCE_CLASSES),
        },
        "ablation_tracking": {
            "tracking_only": {"n": track_only["n"], "correct": track_only["correct"], "pct": pct(track_only["n"], track_only["correct"])},
            "tracking_plus_distance": {"n": track_dist["n"], "correct": track_dist["correct"], "pct": pct(track_dist["n"], track_dist["correct"])},
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
            "note": "Future depth prediction proxy (inverse-planning-style along camera axis); separate domain from corridor inverse_planning.",
        },
        "anti_contam": {
            "audit_path": str(audit_path.relative_to(ROOT)),
            "dirty_count": dirty,
            "status": "INVALID" if dirty else "CLEAN",
        },
        "gpu": "deferred — heuristic CPU only; LoRA queued behind existing waiters",
        "sample_rows": all_dist_rows[:15],
    }
    out_json = data_dir / "EVAL_FLOOR_SCALE_CPU.json"
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
    # meta must not contain gt_m
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
    ap.add_argument("--contam-self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.contam_self_test:
        r = contam_self_test(args.data)
        print(json.dumps(r, indent=2))
        sys.exit(0 if r["passed"] else 1)
    r = run_eval(args.data)
    print(json.dumps({
        "distance_pct": r["distance"]["pct"],
        "by_band": r["distance"]["by_band"],
        "ablation_tracking": r["ablation_tracking"],
        "ablation_future_pred": {
            "tracking_only": r["ablation_future_pred"]["tracking_only"]["distance_pred_pct"],
            "plus_distance": r["ablation_future_pred"]["plus_distance"]["distance_pred_pct"],
        },
        "anti_contam": r["anti_contam"],
        "scale_lock": r["scale_lock"],
    }, indent=2))


if __name__ == "__main__":
    main()
