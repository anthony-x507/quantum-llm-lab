#!/usr/bin/env python3
"""Generate ≥80 DANGER ZONE sequences (critical object in 30–70 m).

Focus: mid-band reinforce where baseline ~50 m was 48.69%.
Every sequence has ≥1 priority object with exact GT distance in [30, 70]
AND approach/recede label (v_depth → motion).

Reuses FLOOR-SCALE lock: building floors 2.4–3.0 m; lights vary 3–5 m
(no fixed light height). Soft car/ped size priors used at *eval* only.

Output: data/video_synth/distance_est/danger50/
GT only in distances_gt.json — never in meta/prompts.

Usage:
  python examples/distance_est/generate_danger50.py
  python examples/distance_est/generate_danger50.py --n-seq 88 --seed 24092450
"""
from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from physics import (
    DEFAULT_FOCAL_PX,
    FLOOR_HEIGHT_M_DEFAULT,
    FLOOR_HEIGHT_M_MAX,
    FLOOR_HEIGHT_M_MIN,
    DANGER_ZONE_M_HI,
    DANGER_ZONE_M_LO,
    band_for_distance,
    in_danger_zone,
    parallax_signal,
)
# Reuse render helpers from generate.py
from generate import (
    STREET_NAMES,
    CAR_COLORS,
    COLOR_RGB,
    CYCLE,
    WorldObj,
    DistSequence,
    _font,
    _clamp,
    light_state_at,
    project,
    render_frame,
)

ROOT = Path(__file__).resolve().parents[2]
OUT_DEFAULT = ROOT / "data" / "video_synth" / "distance_est" / "danger50"


def build_danger_sequence(idx: int, n_frames: int, seed: int, width: int = 384, height: int = 192) -> DistSequence:
    """Critical object(s) forced into 30–70 m with approach/recede label."""
    rng = random.Random(seed + idx * 1009)
    street = STREET_NAMES[idx % len(STREET_NAMES)]
    density = ["low", "med", "high"][idx % 3]
    focal = DEFAULT_FOCAL_PX
    objs: list[WorldObj] = []

    # Buildings mid/far (floor-scale ref) — keep outside exclusive danger focus
    for b in range(2):
        d = rng.uniform(90.0, 200.0)
        n_floors = rng.randint(3, 8)
        fh = rng.uniform(FLOOR_HEIGHT_M_MIN, FLOOR_HEIGHT_M_MAX)
        true_h = n_floors * fh
        lat = (-28 if b == 0 else 28) + rng.uniform(-3, 3)
        objs.append(WorldObj(
            oid=f"bld_{b}", cls="building", color="building",
            d0_m=d, v_depth=rng.choice([0.0, 0.05, -0.05]),
            lateral0_m=lat, v_lat=0.0,
            true_height_m=true_h, true_width_m=true_h * rng.uniform(0.45, 0.75),
            n_floors=n_floors, floor_height_m=round(fh, 3),
        ))

    # --- CRITICAL danger-zone objects (30–70 m) with approach/recede ---
    n_crit = {"low": 3, "med": 4, "high": 5}[density]
    crit_classes = ["car", "pedestrian", "light", "stop_sign", "car", "pedestrian", "intersection"]
    for c in range(n_crit):
        cls = crit_classes[c % len(crit_classes)]
        d = rng.uniform(DANGER_ZONE_M_LO, DANGER_ZONE_M_HI)
        # Force clear approach or recede (not stable) for label
        approach = (idx + c) % 2 == 0
        if cls == "car":
            speed = rng.uniform(0.6, 2.4)
            car_h = rng.uniform(1.4, 1.9)
            car_w = rng.uniform(4.0, 5.2)
            objs.append(WorldObj(
                oid=f"car_{CAR_COLORS[c % len(CAR_COLORS)][:3]}{c}",
                cls="car", color=CAR_COLORS[c % len(CAR_COLORS)],
                d0_m=d, v_depth=(-speed if approach else speed),
                lateral0_m=rng.uniform(-18, 18),
                v_lat=rng.uniform(-0.12, 0.12),
                true_height_m=car_h, true_width_m=car_w,
            ))
        elif cls == "pedestrian":
            speed = rng.uniform(0.25, 1.0)
            ped_h = rng.uniform(1.5, 1.9)
            objs.append(WorldObj(
                oid=f"ped_{c}", cls="pedestrian",
                color=rng.choice(["black", "red", "blue", "gray"]),
                d0_m=d, v_depth=(-speed if approach else speed),
                lateral0_m=rng.choice([-1, 1]) * rng.uniform(8, 18),
                v_lat=rng.uniform(-0.04, 0.04),
                true_height_m=ped_h, true_width_m=ped_h * 0.28,
            ))
        elif cls == "light":
            speed = rng.uniform(0.3, 1.2)
            h = rng.uniform(3.0, 5.0)  # LOCK: varied
            lat = rng.uniform(-16, 16)
            objs.append(WorldObj(
                oid=f"L{c+1}", cls="light", color="pole",
                d0_m=d, v_depth=(-speed if approach else speed),
                lateral0_m=lat, v_lat=0.0,
                true_height_m=h, true_width_m=h * 0.35,
                phase_offset=rng.randint(0, 19),
                name=f"{street} & danger",
            ))
            objs.append(WorldObj(
                oid=f"ix_{c+1}", cls="intersection", color="crosswalk",
                d0_m=d, v_depth=(-speed if approach else speed),
                lateral0_m=lat * 0.15, v_lat=0.0,
                true_height_m=0.6, true_width_m=4.0,
                name=f"intersection_danger_{c+1}",
            ))
        elif cls == "stop_sign":
            speed = rng.uniform(0.2, 0.8)
            sh = rng.uniform(2.0, 2.8)
            objs.append(WorldObj(
                oid=f"stop_{c}", cls="stop_sign", color="stop_sign",
                d0_m=d, v_depth=(-speed if approach else speed),
                lateral0_m=rng.choice([-1, 1]) * rng.uniform(10, 20),
                v_lat=0.0, true_height_m=sh, true_width_m=sh * 0.55,
            ))
        else:  # intersection alone
            speed = rng.uniform(0.3, 1.0)
            objs.append(WorldObj(
                oid=f"ix_solo_{c}", cls="intersection", color="crosswalk",
                d0_m=d, v_depth=(-speed if approach else speed),
                lateral0_m=rng.uniform(-6, 6), v_lat=0.0,
                true_height_m=0.6, true_width_m=4.0,
                name=f"intersection_solo_{c}",
            ))

    # Distractors outside danger band (near / far) so scale cues still present
    for i in range(2):
        d_far = rng.uniform(120.0, 210.0)
        car_h = rng.uniform(1.4, 1.9)
        objs.append(WorldObj(
            oid=f"car_far{i}", cls="car", color=CAR_COLORS[(i + 3) % len(CAR_COLORS)],
            d0_m=d_far, v_depth=rng.choice([-0.5, 0.0, 0.5]),
            lateral0_m=rng.uniform(-22, 22), v_lat=0.0,
            true_height_m=car_h, true_width_m=rng.uniform(4.0, 5.0),
        ))
    d_near = rng.uniform(4.0, 12.0)
    objs.append(WorldObj(
        oid="ped_near0", cls="pedestrian", color="black",
        d0_m=d_near, v_depth=rng.choice([-0.3, 0.3]),
        lateral0_m=rng.choice([-1, 1]) * rng.uniform(6, 14),
        v_lat=0.0, true_height_m=rng.uniform(1.5, 1.85), true_width_m=0.45,
    ))
    # One far light for floor-span variety
    objs.append(WorldObj(
        oid="L_far", cls="light", color="pole",
        d0_m=rng.uniform(100.0, 180.0), v_depth=0.0,
        lateral0_m=rng.uniform(-20, 20), v_lat=0.0,
        true_height_m=rng.uniform(3.0, 5.0), true_width_m=1.4,
        phase_offset=rng.randint(0, 19), name=f"{street} far",
    ))

    return DistSequence(
        seq_id=f"dz_{idx:03d}_{street.lower().replace(' ', '_')}",
        street_name=street, n_frames=n_frames, width=width, height=height,
        seed=seed + idx, density=density, focal_px=focal, objects=objs,
    )


def _obj_state(o: WorldObj, t: int, focal: float, W: int, H: int) -> dict[str, Any]:
    d = max(1.5, o.d0_m + o.v_depth * t)
    lat = o.lateral0_m + o.v_lat * t
    horizon_y = H * 0.30
    cx, cy, scale = project(d, lat, focal=focal, cx0=W / 2, horizon_y=horizon_y, road_scale=1.0)
    apparent = o.true_height_m * scale
    w_px = max(2.0, o.true_width_m * scale * (0.5 if o.cls == "car" else 1.0))
    h_px = max(2.0, apparent)

    if o.v_depth < -0.05:
        motion = "approach"
    elif o.v_depth > 0.05:
        motion = "recede"
    else:
        motion = "stable"

    out = {
        "id": o.oid, "class": o.cls, "color": o.color, "t": t,
        "cx": round(_clamp(cx, 4, W - 4), 2),
        "cy": round(_clamp(cy, 4, H - 4), 2),
        "apparent_px": round(float(apparent), 3),
        "bbox_w": round(float(w_px), 2),
        "bbox_h": round(float(h_px), 2),
        "motion_hint": motion,
        "_gt_m": round(d, 3),
        "_gt_band": band_for_distance(d),
        "_in_danger_zone": in_danger_zone(d),
        "_v_depth": o.v_depth,
        "_approach_recede": motion,
        "_true_height_m": o.true_height_m,
        "name": o.name,
        "phase_offset": o.phase_offset,
    }
    if o.cls == "building":
        out["n_floors"] = o.n_floors
        out["floor_height_m"] = o.floor_height_m
        out["floor_px"] = round(apparent / max(1, o.n_floors), 3)
    return out


def generate(out_dir: Path, n_seq: int = 88, n_frames: int = 12, seed: int = 24092450, train_frac: float = 0.8) -> dict[str, Any]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for p in out_dir.glob("dz_*"):
        if p.is_dir():
            shutil.rmtree(p)

    index = []
    band_counts: dict[str, int] = {"~5m": 0, "~50m": 0, "~100m": 0, "~200m": 0}
    danger_obs = 0
    approach_n = recede_n = stable_n = 0
    class_counts: dict[str, int] = {}
    PRIORITY = {"car", "intersection", "stop_sign", "pedestrian", "light"}
    priority_danger = 0

    for i in range(n_seq):
        seq = build_danger_sequence(i, n_frames, seed)
        seq_dir = out_dir / seq.seq_id
        frames_dir = seq_dir / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)

        meta_frames: list[dict[str, Any]] = []
        gt_frames: list[dict[str, Any]] = []
        prev_size: dict[str, float] = {}
        crit_t0 = []

        for t in range(seq.n_frames):
            states = [_obj_state(o, t, seq.focal_px, seq.width, seq.height) for o in seq.objects]
            img = render_frame(seq, t, states)
            img.save(frames_dir / f"frame_{t:03d}.png", format="PNG", optimize=True)

            visible = []
            gt_objs = []
            for s in states:
                sig = parallax_signal(prev_size.get(s["id"], s["apparent_px"]), s["apparent_px"])
                prev_size[s["id"]] = s["apparent_px"]
                vis: dict[str, Any] = {
                    "id": s["id"], "class": s["class"], "color": s["color"],
                    "cx": s["cx"], "cy": s["cy"],
                    "apparent_px": s["apparent_px"],
                    "bbox_w": s["bbox_w"], "bbox_h": s["bbox_h"],
                    "motion_hint": s["motion_hint"],
                }
                if s["class"] == "building":
                    vis["n_floors"] = s["n_floors"]
                    vis["floor_height_m"] = s["floor_height_m"]
                    vis["floor_px"] = s["floor_px"]
                if s["class"] == "light":
                    vis["state"] = s.get("state", light_state_at(t, s["phase_offset"]))
                visible.append(vis)
                gt_objs.append({
                    "id": s["id"], "class": s["class"],
                    "gt_m": s["_gt_m"], "gt_band": s["_gt_band"],
                    "in_danger_zone": s["_in_danger_zone"],
                    "approach_recede": s["_approach_recede"],
                    "v_depth": s["_v_depth"],
                    "true_height_m": s["_true_height_m"],
                    "parallax_signal": sig,
                    "apparent_px": s["apparent_px"],
                    **({"n_floors": s["n_floors"], "floor_height_m": s["floor_height_m"]} if s["class"] == "building" else {}),
                })
                band_counts[s["_gt_band"]] = band_counts.get(s["_gt_band"], 0) + 1
                class_counts[s["class"]] = class_counts.get(s["class"], 0) + 1
                if s["_in_danger_zone"]:
                    danger_obs += 1
                    if s["class"] in PRIORITY:
                        priority_danger += 1
                ar = s["_approach_recede"]
                if ar == "approach":
                    approach_n += 1
                elif ar == "recede":
                    recede_n += 1
                else:
                    stable_n += 1
                if t == 0 and s["_in_danger_zone"] and s["class"] in PRIORITY:
                    crit_t0.append({
                        "id": s["id"], "class": s["class"],
                        "gt_m": s["_gt_m"], "approach_recede": ar,
                    })

            meta_frames.append({"t": t, "objects": visible})
            gt_frames.append({"t": t, "objects": gt_objs})

        meta = {
            "domain": "distance_est",
            "family": "video_synth_temporal_danger50",
            "danger_zone_m": [DANGER_ZONE_M_LO, DANGER_ZONE_M_HI],
            "scale_lock": "FLOOR-SCALE (building floors 2.4–3.0 m) — NO fixed object heights; soft car~4.5m / ped~1.7m priors at eval",
            "seq_id": seq.seq_id,
            "street_name": seq.street_name,
            "n_frames": seq.n_frames,
            "width": seq.width,
            "height": seq.height,
            "density": seq.density,
            "focal_px": seq.focal_px,
            "seed": seq.seed,
            "frames": meta_frames,
            "note": "NO ground-truth meters here. GT in distances_gt.json sidecar only. "
                    "Critical objects targeted to 30–70 m DANGER ZONE with approach/recede.",
        }
        (seq_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

        gt = {
            "seq_id": seq.seq_id,
            "focal_px": seq.focal_px,
            "scale_lock": "FLOOR-SCALE",
            "danger_zone_m": [DANGER_ZONE_M_LO, DANGER_ZONE_M_HI],
            "floor_height_range_m": [FLOOR_HEIGHT_M_MIN, FLOOR_HEIGHT_M_MAX],
            "critical_t0": crit_t0,
            "frames": gt_frames,
            "objects_t0": [
                {
                    "id": o.oid, "class": o.cls, "d0_m": round(o.d0_m, 3),
                    "v_depth": o.v_depth,
                    "approach_recede": ("approach" if o.v_depth < -0.05 else "recede" if o.v_depth > 0.05 else "stable"),
                    "band": band_for_distance(o.d0_m),
                    "in_danger_zone": in_danger_zone(o.d0_m),
                    "true_height_m": round(o.true_height_m, 3),
                    **({"n_floors": o.n_floors, "floor_height_m": o.floor_height_m} if o.cls == "building" else {}),
                }
                for o in seq.objects
            ],
        }
        (seq_dir / "distances_gt.json").write_text(json.dumps(gt, indent=2) + "\n", encoding="utf-8")

        index.append({
            "seq_id": seq.seq_id, "street_name": seq.street_name,
            "n_frames": seq.n_frames, "density": seq.density,
            "n_objects": len(seq.objects),
            "n_critical_danger_t0": len(crit_t0),
            "critical_t0": crit_t0,
            "classes": sorted({o.cls for o in seq.objects}),
            "bands_t0": sorted({band_for_distance(o.d0_m) for o in seq.objects}),
            "buildings": [
                {"id": o.oid, "n_floors": o.n_floors, "floor_height_m": o.floor_height_m}
                for o in seq.objects if o.cls == "building"
            ],
            "dir": seq.seq_id,
        })
        if (i + 1) % 10 == 0 or i == 0:
            print(f"  [{i+1}/{n_seq}] {seq.seq_id} crit_dz={len(crit_t0)}", flush=True)

    ids = [r["seq_id"] for r in index]
    rng = random.Random(seed)
    shuffled = ids[:]
    rng.shuffle(shuffled)
    n_train = max(1, int(round(len(shuffled) * train_frac)))
    train_ids = sorted(shuffled[:n_train])
    eval_ids = sorted(shuffled[n_train:])
    split = {
        "seed": seed,
        "train_ids": train_ids,
        "eval_ids": eval_ids,
        "n_train": len(train_ids),
        "n_eval": len(eval_ids),
        "danger_zone_m": [DANGER_ZONE_M_LO, DANGER_ZONE_M_HI],
        "rule": "GT meters NEVER in prompt/memory/retrieval; distances_gt.json post-hoc only; "
                "scale=FLOOR-SCALE; soft car/ped priors at eval only",
    }
    (out_dir / "SPLIT.json").write_text(json.dumps(split, indent=2) + "\n", encoding="utf-8")

    n_with_crit = sum(1 for r in index if r["n_critical_danger_t0"] >= 1)
    summary = {
        "domain": "distance_est",
        "family": "video_synth_temporal_danger50",
        "danger_zone_m": [DANGER_ZONE_M_LO, DANGER_ZONE_M_HI],
        "scale_lock": "FLOOR-SCALE",
        "floor_height_m": {"min": FLOOR_HEIGHT_M_MIN, "max": FLOOR_HEIGHT_M_MAX, "default": FLOOR_HEIGHT_M_DEFAULT},
        "no_fixed_object_heights": True,
        "soft_size_priors_eval_only": {"car_length_m": 4.5, "ped_height_m": 1.7},
        "light_true_height_range_m": [3.0, 5.0],
        "priority_distance_classes": sorted(PRIORITY),
        "n_sequences": len(index),
        "n_sequences_with_critical_danger_t0": n_with_crit,
        "n_frames_each": n_frames,
        "seed": seed,
        "split": {"n_train": len(train_ids), "n_eval": len(eval_ids)},
        "band_observation_counts": band_counts,
        "danger_zone_observations": danger_obs,
        "priority_danger_zone_observations": priority_danger,
        "approach_recede_counts": {"approach": approach_n, "recede": recede_n, "stable": stable_n},
        "class_observation_counts": class_counts,
        "focal_px": DEFAULT_FOCAL_PX,
        "baseline_50m_pct": 48.69,
        "baseline_commit": "bcbcdc8",
        "adapter_target": "data/lora_adapter_distance/",
        "quantum_adapter_ro": "data/lora_adapter/",
        "anti_contam": "meta.json has no gt_m; distances_gt.json sidecar only",
        "sequences": index,
    }
    (out_dir / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (out_dir / "INDEX.json").write_text(json.dumps({"sequences": index, "split": split}, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# DANGER ZONE (~50 m) focused set SUMMARY",
        "",
        f"- **Danger zone:** {DANGER_ZONE_M_LO}–{DANGER_ZONE_M_HI} m",
        f"- sequences: **{len(index)}** × {n_frames} frames (≥1 critical in zone @ t0: **{n_with_crit}**)",
        f"- priority danger-zone observations: **{priority_danger}**",
        f"- approach/recede/stable: {approach_n}/{recede_n}/{stable_n}",
        f"- Baseline ~50 m band: **48.69%** (bcbcdc8)",
        f"- Soft priors (eval): car ~4.5 m length, ped ~1.7 m height — lights still floor-span",
        "",
    ]
    (out_dir / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    ap.add_argument("--n-seq", type=int, default=88)
    ap.add_argument("--n-frames", type=int, default=12)
    ap.add_argument("--seed", type=int, default=24092450)
    ap.add_argument("--train-frac", type=float, default=0.8)
    args = ap.parse_args(argv)
    print(f"Generating danger50 → {args.out}", flush=True)
    summary = generate(args.out, n_seq=args.n_seq, n_frames=args.n_frames, seed=args.seed, train_frac=args.train_frac)
    print(json.dumps({
        "n_sequences": summary["n_sequences"],
        "n_with_critical_danger_t0": summary["n_sequences_with_critical_danger_t0"],
        "split": summary["split"],
        "priority_danger_zone_observations": summary["priority_danger_zone_observations"],
        "approach_recede_counts": summary["approach_recede_counts"],
        "band_observation_counts": summary["band_observation_counts"],
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
