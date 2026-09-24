#!/usr/bin/env python3
"""Generate ≥50 street sequences with GT 3D distances + floor-scale cues.

LOCK (Anthony): NO fixed object heights. Scale reference = BUILDING FLOORS
(each floor ≈ 8–10 ft / 2.4–3.0 m). Lights vary ~3–5 m by intersection;
model must derive light/sign height by floor-span in frame.

Extends video_synth temporal family (street + 3 lights + depth):
  - classes: buildings (floor meta), lights, cars, pedestrians, stop signs,
    intersections
  - distance bands ~5 / 50 / 100 / 200 m
  - frame-to-frame parallax (growing→approach, shrinking→recede)

GT meters ONLY in distances_gt.json sidecars — never in meta.json / prompts.
meta.json exposes visible geometry + building n_floors / floor_height_m
(standard knowledge) + apparent_px — NOT ground-truth meters.

Usage:
  python examples/distance_est/generate.py
  python examples/distance_est/generate.py --n-seq 56 --seed 240924
"""
from __future__ import annotations

import argparse
import json
import random
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from physics import (
    DEFAULT_FOCAL_PX,
    FLOOR_HEIGHT_M_DEFAULT,
    FLOOR_HEIGHT_M_MAX,
    FLOOR_HEIGHT_M_MIN,
    band_for_distance,
    parallax_signal,
)

ROOT = Path(__file__).resolve().parents[2]
OUT_DEFAULT = ROOT / "data" / "video_synth" / "distance_est"

STREET_NAMES = [
    "Oak Ave", "Pine St", "Maple Blvd", "Cedar Rd",
    "Elm Way", "Birch Ln", "Willow Dr", "Ash Ct",
]
CAR_COLORS = ["red", "blue", "green", "yellow", "white", "black", "gray", "orange"]
COLOR_RGB = {
    "red": (200, 50, 50), "blue": (50, 90, 200), "green": (40, 160, 70),
    "yellow": (220, 200, 40), "white": (230, 230, 230), "black": (30, 30, 30),
    "gray": (120, 120, 130), "orange": (230, 130, 40),
    "asphalt": (55, 55, 60), "sky": (135, 180, 220),
    "building": (95, 90, 85), "stop_sign": (200, 30, 30),
}

BANDS_M = [5.0, 50.0, 100.0, 200.0]
CYCLE = {"G": 6, "Y": 3, "R": 7}


def _font(size: int = 11):
    try:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
    except Exception:
        return ImageFont.load_default()


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def light_state_at(frame_i: int, phase_offset: int) -> str:
    period = CYCLE["R"] + CYCLE["Y"] + CYCLE["G"]
    t = (frame_i + phase_offset) % period
    if t < CYCLE["G"]:
        return "G"
    if t < CYCLE["G"] + CYCLE["Y"]:
        return "Y"
    return "R"


def project(d_m: float, lateral_m: float, *, focal: float, cx0: float, horizon_y: float, road_scale: float) -> tuple[float, float, float]:
    """Pinhole: closer → larger apparent + lower on screen (larger cy)."""
    d = max(1.0, d_m)
    scale = focal / d
    cx = cx0 + lateral_m * scale * road_scale
    # Ground-plane: cam_height_m≈1.6; cy rises as 1/d (nearer = lower in frame)
    cam_h = 1.6
    cy = horizon_y + (focal * cam_h / d) * 0.22
    return cx, cy, scale


@dataclass
class WorldObj:
    oid: str
    cls: str  # building|light|car|pedestrian|stop_sign|intersection
    color: str
    d0_m: float
    v_depth: float
    lateral0_m: float
    v_lat: float
    # True 3D extent used ONLY for rendering + GT sidecar (estimator must NOT
    # assume fixed catalog heights — lights vary 3–5 m; cars/peds vary too).
    true_height_m: float
    true_width_m: float = 1.0
    phase_offset: int = 0
    name: str = ""
    n_floors: int = 0
    floor_height_m: float = FLOOR_HEIGHT_M_DEFAULT


@dataclass
class DistSequence:
    seq_id: str
    street_name: str
    n_frames: int
    width: int
    height: int
    seed: int
    density: str
    focal_px: float
    objects: list[WorldObj] = field(default_factory=list)


def build_sequence(idx: int, n_frames: int, seed: int, width: int = 384, height: int = 192) -> DistSequence:
    rng = random.Random(seed + idx * 997)
    street = STREET_NAMES[idx % len(STREET_NAMES)]
    density = ["low", "med", "high"][idx % 3]
    focal = DEFAULT_FOCAL_PX
    objs: list[WorldObj] = []

    # --- Buildings FIRST (floor-scale reference) — mid/far bands ---
    for b in range(2):
        band = BANDS_M[2 + (b % 2)]  # 100 or 200
        d = _clamp(band * rng.uniform(0.9, 1.1), 40.0, 220.0)
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

    # --- Lights: TRUE height varies 3–5 m (NOT fixed 3 m) ---
    light_bands = [BANDS_M[i % len(BANDS_M)] for i in range(3)]
    rot = idx % 4
    light_bands = light_bands[rot:] + light_bands[:rot]
    for i in range(3):
        d = _clamp(light_bands[i] * rng.uniform(0.85, 1.15), 4.0, 220.0)
        v_d = rng.choice([-0.4, -0.15, 0.0, 0.15, 0.35]) if d < 80 else rng.choice([-0.8, -0.3, 0.0, 0.3])
        lat = (-18.0 + i * 18.0) + rng.uniform(-2, 2)
        h = rng.uniform(3.0, 5.0)  # LOCK: varied by intersection
        objs.append(WorldObj(
            oid=f"L{i+1}", cls="light", color="pole",
            d0_m=d, v_depth=v_d, lateral0_m=lat, v_lat=0.0,
            true_height_m=h, true_width_m=h * 0.35,
            phase_offset=rng.randint(0, 19),
            name=f"{street} & {['1st','2nd','3rd'][i]}",
        ))
        # Intersection marker at same depth as light (priority distance target)
        objs.append(WorldObj(
            oid=f"ix_{i+1}", cls="intersection", color="crosswalk",
            d0_m=d, v_depth=v_d, lateral0_m=lat * 0.15,
            v_lat=0.0, true_height_m=0.6, true_width_m=4.0,
            name=f"intersection_{i+1}",
        ))

    n_cars = {"low": 3, "med": 4, "high": 5}[density]
    n_peds = {"low": 2, "med": 3, "high": 3}[density]
    n_stops = {"low": 1, "med": 2, "high": 2}[density]

    band_cycle = list(BANDS_M)
    rng.shuffle(band_cycle)

    for c in range(n_cars):
        band = band_cycle[c % len(band_cycle)]
        d = _clamp(band * rng.uniform(0.8, 1.2), 4.0, 220.0)
        approach = rng.random() < 0.55
        speed = rng.uniform(0.3, 2.2) if d < 60 else rng.uniform(0.8, 4.0)
        v_d = -speed if approach else speed * rng.uniform(0.3, 1.0)
        # Varied true car height/length for render only (not an estimator catalog)
        car_h = rng.uniform(1.4, 1.9)
        car_w = rng.uniform(4.0, 5.2)
        objs.append(WorldObj(
            oid=f"car_{CAR_COLORS[c % len(CAR_COLORS)][:3]}{c}",
            cls="car", color=CAR_COLORS[c % len(CAR_COLORS)],
            d0_m=d, v_depth=v_d, lateral0_m=rng.uniform(-22, 22),
            v_lat=rng.uniform(-0.15, 0.15),
            true_height_m=car_h, true_width_m=car_w,
        ))

    for p in range(n_peds):
        band = band_cycle[(p + 2) % len(band_cycle)]
        d = _clamp(band * rng.uniform(0.75, 1.15), 4.0, 180.0)
        approach = rng.random() < 0.5
        speed = rng.uniform(0.15, 0.9)
        ped_h = rng.uniform(1.5, 1.9)  # varied; estimator uses floor-relative
        objs.append(WorldObj(
            oid=f"ped_{p}", cls="pedestrian",
            color=rng.choice(["black", "red", "blue", "gray"]),
            d0_m=d, v_depth=(-speed if approach else speed),
            lateral0_m=rng.choice([-1, 1]) * rng.uniform(8, 20),
            v_lat=rng.uniform(-0.05, 0.05),
            true_height_m=ped_h, true_width_m=ped_h * 0.28,
        ))

    for s in range(n_stops):
        band = band_cycle[(s + 1) % len(band_cycle)]
        d = _clamp(band * rng.uniform(0.85, 1.15), 5.0, 160.0)
        # Stop-sign true height varies — derive via floor span at inference
        sh = rng.uniform(2.0, 2.8)
        objs.append(WorldObj(
            oid=f"stop_{s}", cls="stop_sign", color="stop_sign",
            d0_m=d, v_depth=rng.choice([-0.2, 0.0, 0.2]),
            lateral0_m=rng.choice([-1, 1]) * rng.uniform(10, 24),
            v_lat=0.0, true_height_m=sh, true_width_m=sh * 0.55,
        ))

    return DistSequence(
        seq_id=f"de_{idx:03d}_{street.lower().replace(' ', '_')}",
        street_name=street, n_frames=n_frames, width=width, height=height,
        seed=seed + idx, density=density, focal_px=focal, objects=objs,
    )


def _obj_state(o: WorldObj, t: int, focal: float, W: int, H: int) -> dict[str, Any]:
    d = max(1.5, o.d0_m + o.v_depth * t)
    lat = o.lateral0_m + o.v_lat * t
    horizon_y = H * 0.30
    cx, cy, scale = project(d, lat, focal=focal, cx0=W / 2, horizon_y=horizon_y, road_scale=1.0)
    # Apparent size from TRUE 3D height (render GT) — estimator must rediscover
    # via floor span, not a fixed catalog.
    apparent = o.true_height_m * scale
    w_px = max(2.0, o.true_width_m * scale * (0.5 if o.cls == "car" else 1.0))
    h_px = max(2.0, apparent)

    motion = "stable"
    if o.v_depth < -0.05:
        motion = "approach"
    elif o.v_depth > 0.05:
        motion = "recede"

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
        "_v_depth": o.v_depth,
        "_true_height_m": o.true_height_m,  # sidecar only
        "name": o.name,
        "phase_offset": o.phase_offset,
    }
    if o.cls == "building":
        out["n_floors"] = o.n_floors
        out["floor_height_m"] = o.floor_height_m
        out["floor_px"] = round(apparent / max(1, o.n_floors), 3)
    return out


def render_frame(seq: DistSequence, t: int, states: list[dict[str, Any]]) -> Image.Image:
    W, H = seq.width, seq.height
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    font_sm = _font(9)
    draw.rectangle([0, 0, W, int(H * 0.30)], fill=COLOR_RGB["sky"])
    draw.rectangle([0, int(H * 0.30), W, H], fill=COLOR_RGB["asphalt"])
    draw.line([(W * 0.5, H * 0.30), (0, H)], fill=(80, 80, 85), width=2)
    draw.line([(W * 0.5, H * 0.30), (W, H)], fill=(80, 80, 85), width=2)
    draw.rectangle([W // 2 - 50, 4, W // 2 + 50, 18], fill=(30, 30, 40))
    draw.text((W // 2 - 36, 5), seq.street_name, fill=(255, 255, 255), font=font_sm)

    ordered = sorted(states, key=lambda s: -s["_gt_m"])
    lamp_map = {"R": "red", "Y": "yellow", "G": "green"}
    for s in ordered:
        cx, cy = s["cx"], s["cy"]
        bw, bh = max(2.0, s["bbox_w"]), max(2.0, s["bbox_h"])
        cls = s["class"]
        if cls == "building":
            x0, y0 = cx - bw / 2, cy - bh
            draw.rectangle([x0, y0, cx + bw / 2, cy], fill=COLOR_RGB["building"], outline=(40, 40, 40))
            n = int(s.get("n_floors") or 4)
            floor_h = bh / n
            for fi in range(n):
                fy = y0 + fi * floor_h
                draw.line([x0, fy, cx + bw / 2, fy], fill=(70, 68, 64), width=1)
                # windows per floor
                for wx in range(int(x0 + 3), int(cx + bw / 2 - 3), max(5, int(bw / 4))):
                    draw.rectangle([wx, fy + 2, wx + 3, fy + max(3, floor_h - 3)], fill=(180, 190, 210))
            draw.text((cx - 12, y0 - 12), f"{s['id']}|{n}fl", fill=(255, 255, 255), font=font_sm)
        elif cls == "intersection":
            # crosswalk stripes at depth
            for yy in range(int(cy - 4), int(cy + 6), 3):
                draw.rectangle([cx - bw / 2, yy, cx + bw / 2, yy + 2], fill=(200, 200, 200))
            draw.text((cx - 8, cy - 12), s["id"], fill=(255, 255, 100), font=font_sm)
        elif cls == "stop_sign":
            # octagon-ish + pole
            draw.rectangle([cx - 1, cy - bh, cx + 1, cy], fill=(60, 60, 60))
            r = max(3, bw / 2)
            draw.ellipse([cx - r, cy - bh, cx + r, cy - bh + 2 * r], fill=COLOR_RGB["stop_sign"], outline=(20, 20, 20))
            draw.text((cx - 6, cy - bh - 10), "STOP", fill=(255, 255, 255), font=font_sm)
        elif cls == "light":
            st = light_state_at(t, s["phase_offset"])
            pole_top = cy - bh
            draw.rectangle([cx - 2, pole_top, cx + 2, cy], fill=(40, 40, 45))
            draw.rectangle([cx - 6, pole_top - 4, cx + 6, pole_top + bh * 0.55], fill=(25, 25, 30), outline=(10, 10, 10))
            for i, lab in enumerate(["R", "Y", "G"]):
                ly = pole_top + i * (bh * 0.18)
                col = COLOR_RGB[lamp_map[lab]] if st == lab else (50, 50, 50)
                draw.ellipse([cx - 4, ly, cx + 4, ly + max(3, bh * 0.15)], fill=col)
            s["state"] = st
            draw.text((cx - 10, pole_top - 12), s["id"], fill=(20, 20, 20), font=font_sm)
        elif cls == "car":
            rgb = COLOR_RGB.get(s["color"], (180, 50, 50))
            draw.rounded_rectangle(
                [cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2],
                radius=max(1, int(bh / 6)), fill=rgb, outline=(20, 20, 25),
            )
            draw.rectangle([cx - bw * 0.2, cy - bh * 0.35, cx + bw * 0.2, cy - bh * 0.05], fill=(170, 200, 230))
            draw.text((cx - 10, cy - bh / 2 - 10), s["id"][:7], fill=(255, 255, 255), font=font_sm)
        else:  # pedestrian
            rgb = COLOR_RGB.get(s["color"], (30, 30, 30))
            head_r = max(2, bh * 0.12)
            draw.ellipse([cx - head_r, cy - bh, cx + head_r, cy - bh + 2 * head_r], fill=rgb)
            draw.line([cx, cy - bh + 2 * head_r, cx, cy - bh * 0.2], fill=rgb, width=max(1, int(bw / 3)))
            draw.line([cx - bw / 2, cy - bh * 0.55, cx + bw / 2, cy - bh * 0.55], fill=rgb, width=max(1, int(bw / 3)))
            draw.line([cx, cy - bh * 0.2, cx - bw / 3, cy], fill=rgb, width=max(1, int(bw / 3)))
            draw.line([cx, cy - bh * 0.2, cx + bw / 3, cy], fill=rgb, width=max(1, int(bw / 3)))
            draw.text((cx - 8, cy - bh - 10), s["id"][:6], fill=(255, 255, 255), font=font_sm)

    draw.text((4, H - 14), f"{seq.seq_id} f={t}/{seq.n_frames - 1}", fill=(255, 255, 255), font=font_sm)
    return img


def generate(out_dir: Path, n_seq: int = 56, n_frames: int = 12, seed: int = 240924, train_frac: float = 0.8) -> dict[str, Any]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for p in out_dir.glob("de_*"):
        if p.is_dir():
            shutil.rmtree(p)

    index = []
    band_counts: dict[str, int] = {"~5m": 0, "~50m": 0, "~100m": 0, "~200m": 0}
    class_counts: dict[str, int] = {}
    priority_band_counts: dict[str, int] = {"~5m": 0, "~50m": 0, "~100m": 0, "~200m": 0}
    PRIORITY = {"car", "intersection", "stop_sign", "pedestrian", "light"}

    for i in range(n_seq):
        seq = build_sequence(i, n_frames, seed)
        seq_dir = out_dir / seq.seq_id
        frames_dir = seq_dir / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)

        meta_frames: list[dict[str, Any]] = []
        gt_frames: list[dict[str, Any]] = []
        prev_size: dict[str, float] = {}

        for t in range(seq.n_frames):
            states = [_obj_state(o, t, seq.focal_px, seq.width, seq.height) for o in seq.objects]
            img = render_frame(seq, t, states)
            img.save(frames_dir / f"frame_{t:03d}.png", format="PNG", optimize=True)

            visible = []
            gt_objs = []
            for s in states:
                sig = parallax_signal(prev_size.get(s["id"], s["apparent_px"]), s["apparent_px"])
                prev_size[s["id"]] = s["apparent_px"]
                # PUBLIC meta — NO gt meters. Floor meta is standard knowledge.
                vis: dict[str, Any] = {
                    "id": s["id"], "class": s["class"], "color": s["color"],
                    "cx": s["cx"], "cy": s["cy"],
                    "apparent_px": s["apparent_px"],
                    "bbox_w": s["bbox_w"], "bbox_h": s["bbox_h"],
                    "motion_hint": s["motion_hint"],
                }
                if s["class"] == "building":
                    vis["n_floors"] = s["n_floors"]
                    vis["floor_height_m"] = s["floor_height_m"]  # standard 2.4–3.0
                    vis["floor_px"] = s["floor_px"]
                if s["class"] == "light":
                    vis["state"] = s.get("state", light_state_at(t, s["phase_offset"]))
                visible.append(vis)
                gt_objs.append({
                    "id": s["id"], "class": s["class"],
                    "gt_m": s["_gt_m"], "gt_band": s["_gt_band"],
                    "v_depth": s["_v_depth"],
                    "true_height_m": s["_true_height_m"],  # render truth; not for prompts
                    "parallax_signal": sig,
                    "apparent_px": s["apparent_px"],
                    **({"n_floors": s["n_floors"], "floor_height_m": s["floor_height_m"]} if s["class"] == "building" else {}),
                })
                band_counts[s["_gt_band"]] = band_counts.get(s["_gt_band"], 0) + 1
                class_counts[s["class"]] = class_counts.get(s["class"], 0) + 1
                if s["class"] in PRIORITY:
                    priority_band_counts[s["_gt_band"]] = priority_band_counts.get(s["_gt_band"], 0) + 1

            meta_frames.append({"t": t, "objects": visible})
            gt_frames.append({"t": t, "objects": gt_objs})

        meta = {
            "domain": "distance_est",
            "family": "video_synth_temporal",
            "scale_lock": "FLOOR-SCALE (building floors 2.4–3.0 m) — NO fixed object heights",
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
                    "Buildings expose n_floors + floor_height_m (standard) for scale.",
        }
        (seq_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

        gt = {
            "seq_id": seq.seq_id,
            "focal_px": seq.focal_px,
            "scale_lock": "FLOOR-SCALE",
            "floor_height_range_m": [FLOOR_HEIGHT_M_MIN, FLOOR_HEIGHT_M_MAX],
            "frames": gt_frames,
            "objects_t0": [
                {
                    "id": o.oid, "class": o.cls, "d0_m": round(o.d0_m, 3),
                    "v_depth": o.v_depth, "band": band_for_distance(o.d0_m),
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
            "classes": sorted({o.cls for o in seq.objects}),
            "bands_t0": sorted({band_for_distance(o.d0_m) for o in seq.objects}),
            "buildings": [
                {"id": o.oid, "n_floors": o.n_floors, "floor_height_m": o.floor_height_m}
                for o in seq.objects if o.cls == "building"
            ],
            "dir": seq.seq_id,
        })
        if (i + 1) % 10 == 0 or i == 0:
            print(f"  [{i+1}/{n_seq}] {seq.seq_id} objs={len(seq.objects)} bands={index[-1]['bands_t0']}", flush=True)

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
        "rule": "GT meters NEVER in prompt/memory/retrieval; distances_gt.json post-hoc only; "
                "scale=FLOOR-SCALE not fixed-object-height",
    }
    (out_dir / "SPLIT.json").write_text(json.dumps(split, indent=2) + "\n", encoding="utf-8")

    summary = {
        "domain": "distance_est",
        "family": "video_synth_temporal",
        "scale_lock": "FLOOR-SCALE",
        "floor_height_m": {"min": FLOOR_HEIGHT_M_MIN, "max": FLOOR_HEIGHT_M_MAX, "default": FLOOR_HEIGHT_M_DEFAULT},
        "no_fixed_object_heights": True,
        "light_true_height_range_m": [3.0, 5.0],
        "priority_distance_classes": sorted(PRIORITY),
        "n_sequences": len(index),
        "n_frames_each": n_frames,
        "seed": seed,
        "split": {"n_train": len(train_ids), "n_eval": len(eval_ids)},
        "distance_bands_m": BANDS_M,
        "band_observation_counts": band_counts,
        "priority_band_observation_counts": priority_band_counts,
        "class_observation_counts": class_counts,
        "focal_px": DEFAULT_FOCAL_PX,
        "adapter_target": "data/lora_adapter_distance/",
        "quantum_adapter_ro": "data/lora_adapter/",
        "anti_contam": "meta.json has no gt_m; distances_gt.json sidecar only; floor meta is scale ref not distance GT",
        "sequences": index,
    }
    (out_dir / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (out_dir / "INDEX.json").write_text(json.dumps({"sequences": index, "split": split}, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Distance estimation — synthetic set SUMMARY",
        "",
        "- **Scale lock:** FLOOR-SCALE (building floors 2.4–3.0 m) — **NO fixed object heights**",
        "- Lights true height varies **3–5 m** by intersection (derive via floor-span)",
        "- Priority distances: cars, intersections, stop signs, pedestrians (+ lights)",
        f"- **Family:** video_synth temporal — NOT inverse_planning corridor",
        f"- sequences: **{len(index)}** × {n_frames} frames",
        f"- split: train **{len(train_ids)}** / eval **{len(eval_ids)}**",
        f"- bands: {BANDS_M} m (jittered)",
        f"- Adapter: `data/lora_adapter_distance/` (never `data/lora_adapter/`)",
        f"- GT: `distances_gt.json` sidecar only",
        "",
        "## Priority-class band counts",
        "",
        "| band | count |",
        "|------|-------|",
    ]
    for b in ["~5m", "~50m", "~100m", "~200m"]:
        lines.append(f"| {b} | {priority_band_counts.get(b, 0)} |")
    lines += ["", "| seq | street | frames | objs | bands_t0 | buildings |",
              "|-----|--------|--------|------|----------|-----------|"]
    for r in index:
        bld = ",".join(f"{b['id']}:{b['n_floors']}fl@{b['floor_height_m']}m" for b in r["buildings"])
        lines.append(
            f"| `{r['seq_id']}` | {r['street_name']} | {r['n_frames']} | {r['n_objects']} | "
            f"{','.join(r['bands_t0'])} | {bld} |"
        )
    (out_dir / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    ap.add_argument("--n-seq", type=int, default=56)
    ap.add_argument("--n-frames", type=int, default=12)
    ap.add_argument("--seed", type=int, default=240924)
    ap.add_argument("--train-frac", type=float, default=0.8)
    args = ap.parse_args(argv)
    print(f"Generating distance_est (FLOOR-SCALE) → {args.out}", flush=True)
    summary = generate(args.out, n_seq=args.n_seq, n_frames=args.n_frames, seed=args.seed, train_frac=args.train_frac)
    print(json.dumps({
        "n_sequences": summary["n_sequences"],
        "split": summary["split"],
        "scale_lock": summary["scale_lock"],
        "priority_band_observation_counts": summary["priority_band_observation_counts"],
        "class_observation_counts": summary["class_observation_counts"],
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
