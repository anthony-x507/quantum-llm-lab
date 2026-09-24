#!/usr/bin/env python3
"""Generate predictive-collision synthetic sequences (CPU).

Domain (LOCKED — distinct from street F1 and inverse corridor balls):
  TOP-DOWN MERGE LANE — ego disk + other vehicles/pedestrians with MASS.
  Hypo actions on ego: coast / brake / accelerate / turn_left / turn_right.
  World steps with elastic disk collisions (masses + radii matter).

Per sequence:
  frames/frame_XX.png   — rendered top-down
  meta.json             — visible history ONLY (no futures / no consequences GT)
  consequences_gt.json  — SIDECAR: for each (query_t, k, action) the real
                          future under that action (is_safe, consequence, partners)
                          loaded POST-HOC by eval only

Split default 320 train / 80 eval (choose_safest-n expand beyond tip n=40).
Hard-negative mix: unsafe-looking-but-safe / safe-looking-but-unsafe / near-miss choice.
Retrieval index = train only (ids list).

Usage:
  .venv/bin/python examples/collision_predictive/generate.py
  .venv/bin/python examples/collision_predictive/generate.py --n-seq 400 --n-train 320 --n-eval 80 --seed 24092447
"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from physics import (
    ACTIONS,
    ARENA_H,
    ARENA_W,
    MARGIN,
    apply_action,
    consequence_label,
    rollout,
    step_world,
)

HORIZONS = (1, 3, 5)
DEFAULT_N = 400
DEFAULT_TRAIN = 320
DEFAULT_EVAL = 80
# Hardneg mix fractions (choose_safest pressure; physics GT still elastic oracle)
HARDNEG_UNSAFE_LOOK_SAFE = 0.22
HARDNEG_SAFE_LOOK_UNSAFE = 0.22
HARDNEG_NEAR_MISS = 0.16
# remainder = baseline random merge-lane

BG = (28, 32, 40)
LANE = (50, 56, 68)
EGO_COLOR = (80, 200, 255)
VEH_COLORS = [(240, 140, 70), (200, 90, 90), (160, 160, 80)]
PED_COLOR = (220, 220, 100)


def _font(size: int = 11):
    try:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
    except Exception:
        return ImageFont.load_default()


def _pick_hardneg_kind(rng: random.Random) -> str:
    """Scene style for choose_safest pressure (not GT; meta tag only)."""
    u = rng.random()
    if u < HARDNEG_UNSAFE_LOOK_SAFE:
        return "unsafe_look_safe"
    u -= HARDNEG_UNSAFE_LOOK_SAFE
    if u < HARDNEG_SAFE_LOOK_UNSAFE:
        return "safe_look_unsafe"
    u -= HARDNEG_SAFE_LOOK_UNSAFE
    if u < HARDNEG_NEAR_MISS:
        return "near_miss_choice"
    return "baseline"


def _sample_agents(
    rng: random.Random,
    *,
    hardneg_kind: str = "baseline",
) -> list[dict[str, Any]]:
    """Ego on left lane heading +x; others ahead / crossing with masses.

    Hardneg kinds (visual/distance cues vs elastic truth):
      unsafe_look_safe — close ahead but co-moving / pulling away → coast often safe
      safe_look_unsafe — far/slow look but strong closing → coast rear-ends
      near_miss_choice — coast/accel unsafe; brake or turn clears (planner pressure)
      baseline — prior random merge-lane mix
    """
    agents: list[dict[str, Any]] = []
    ego_y = float(rng.uniform(70, 130))
    if hardneg_kind == "unsafe_look_safe":
        ego_vx = float(rng.uniform(5.0, 8.0))
        agents.append({
            "oid": "ego",
            "class": "vehicle",
            "mass": 1.0,
            "r": 10.0,
            "x": float(rng.uniform(40, 65)),
            "y": ego_y,
            "vx": ego_vx,
            "vy": float(rng.uniform(-0.4, 0.4)),
            "color": list(EGO_COLOR),
        })
        # Close ahead but matching/faster vx → looks urgent, physics often clear
        agents.append({
            "oid": "v0",
            "class": "vehicle",
            "mass": float(rng.uniform(0.9, 1.4)),
            "r": float(rng.uniform(9.0, 11.0)),
            "x": float(agents[0]["x"] + rng.uniform(28, 48)),  # near / DZ-looking
            "y": float(ego_y + rng.uniform(-8, 8)),
            "vx": float(ego_vx + rng.uniform(0.5, 2.5)),  # pulling away
            "vy": float(rng.uniform(-0.5, 0.5)),
            "color": list(rng.choice(VEH_COLORS)),
        })
        # distractor pedestrian lateral, not on collision course
        agents.append({
            "oid": "p1",
            "class": "pedestrian",
            "mass": 0.25,
            "r": 5.0,
            "x": float(rng.uniform(160, ARENA_W - 40)),
            "y": float(rng.uniform(MARGIN + 15, ARENA_H - MARGIN - 15)),
            "vx": float(rng.uniform(-1.0, 1.0)),
            "vy": float(rng.uniform(-2.5, 2.5)),
            "color": list(PED_COLOR),
        })
    elif hardneg_kind == "safe_look_unsafe":
        ego_vx = float(rng.uniform(7.0, 10.0))
        agents.append({
            "oid": "ego",
            "class": "vehicle",
            "mass": 1.0,
            "r": 10.0,
            "x": float(rng.uniform(35, 55)),
            "y": ego_y,
            "vx": ego_vx,
            "vy": float(rng.uniform(-0.3, 0.3)),
            "color": list(EGO_COLOR),
        })
        # Far ahead / slow — looks mid/far safe but strong closing → rear-end under coast
        agents.append({
            "oid": "v0",
            "class": "vehicle",
            "mass": float(rng.uniform(1.0, 1.8)),
            "r": float(rng.uniform(9.0, 12.0)),
            "x": float(rng.uniform(180, min(260, ARENA_W - 40))),
            "y": float(ego_y + rng.uniform(-6, 6)),
            "vx": float(rng.uniform(0.2, 1.8)),  # much slower
            "vy": float(rng.uniform(-0.4, 0.4)),
            "color": list(rng.choice(VEH_COLORS)),
        })
        agents.append({
            "oid": "v1",
            "class": "vehicle",
            "mass": float(rng.uniform(0.8, 1.3)),
            "r": float(rng.uniform(8.0, 11.0)),
            "x": float(rng.uniform(120, 170)),
            "y": float(ego_y + rng.uniform(35, 55) * rng.choice([-1, 1])),
            "vx": float(rng.uniform(2.0, 5.0)),
            "vy": float(rng.uniform(-0.8, 0.8)),
            "color": list(rng.choice(VEH_COLORS)),
        })
    elif hardneg_kind == "near_miss_choice":
        ego_vx = float(rng.uniform(6.0, 9.0))
        agents.append({
            "oid": "ego",
            "class": "vehicle",
            "mass": 1.0,
            "r": 10.0,
            "x": float(rng.uniform(40, 60)),
            "y": ego_y,
            "vx": ego_vx,
            "vy": 0.0,
            "color": list(EGO_COLOR),
        })
        # Slow vehicle dead ahead — coast/accel hits; brake/turn often clears
        agents.append({
            "oid": "v0",
            "class": "vehicle",
            "mass": float(rng.uniform(1.0, 1.6)),
            "r": float(rng.uniform(9.0, 12.0)),
            "x": float(agents[0]["x"] + rng.uniform(55, 85)),
            "y": float(ego_y + rng.uniform(-4, 4)),
            "vx": float(rng.uniform(0.5, 2.0)),
            "vy": float(rng.uniform(-0.3, 0.3)),
            "color": list(rng.choice(VEH_COLORS)),
        })
        # Crossing ped offset — adds choose_safest ambiguity
        agents.append({
            "oid": "p1",
            "class": "pedestrian",
            "mass": 0.25,
            "r": 5.0,
            "x": float(agents[0]["x"] + rng.uniform(70, 110)),
            "y": float(ego_y + rng.choice([-1, 1]) * rng.uniform(40, 70)),
            "vx": float(rng.uniform(-0.5, 0.5)),
            "vy": float(-rng.choice([-1, 1]) * rng.uniform(2.0, 4.0)),  # toward lane
            "color": list(PED_COLOR),
        })
    else:
        # baseline — prior random merge-lane mix
        agents.append({
            "oid": "ego",
            "class": "vehicle",
            "mass": 1.0,
            "r": 10.0,
            "x": float(rng.uniform(40, 70)),
            "y": ego_y,
            "vx": float(rng.uniform(4.0, 9.0)),
            "vy": float(rng.uniform(-0.6, 0.6)),
            "color": list(EGO_COLOR),
        })
        n_other = rng.randint(2, 4)
        for i in range(n_other):
            is_ped = rng.random() < 0.35
            if is_ped:
                agents.append({
                    "oid": f"p{i}",
                    "class": "pedestrian",
                    "mass": 0.25,
                    "r": 5.0,
                    "x": float(rng.uniform(120, ARENA_W - 40)),
                    "y": float(rng.uniform(MARGIN + 20, ARENA_H - MARGIN - 20)),
                    "vx": float(rng.uniform(-1.5, 1.5)),
                    "vy": float(rng.uniform(-3.5, 3.5)),
                    "color": list(PED_COLOR),
                })
            else:
                agents.append({
                    "oid": f"v{i}",
                    "class": "vehicle",
                    "mass": float(rng.uniform(0.8, 1.6)),
                    "r": float(rng.uniform(8.0, 12.0)),
                    "x": float(rng.uniform(110, ARENA_W - 50)),
                    "y": float(agents[0]["y"] + rng.uniform(-25, 25)),
                    "vx": float(rng.uniform(1.0, 5.5)),
                    "vy": float(rng.uniform(-1.2, 1.2)),
                    "color": list(rng.choice(VEH_COLORS)),
                })
    # de-overlap initial
    for _ in range(8):
        agents, _ = step_world(agents, substeps=1)
    return agents


def _render(agents: list[dict[str, Any]], t: int, seq_id: str) -> Image.Image:
    img = Image.new("RGB", (ARENA_W, ARENA_H), BG)
    dr = ImageDraw.Draw(img)
    # lane stripes
    for y in (60, 100, 140):
        for x in range(0, ARENA_W, 24):
            dr.line([(x, y), (x + 12, y)], fill=LANE, width=2)
    dr.rectangle([0, 0, ARENA_W - 1, ARENA_H - 1], outline=(90, 96, 110), width=2)
    font = _font(10)
    for o in agents:
        x, y, r = float(o["x"]), float(o["y"]), float(o["r"])
        col = tuple(int(c) for c in o["color"])
        bbox = [x - r, y - r, x + r, y + r]
        if o["class"] == "pedestrian":
            dr.ellipse(bbox, fill=col, outline=(20, 20, 20))
        else:
            dr.ellipse(bbox, fill=col, outline=(255, 255, 255) if o["oid"] == "ego" else (20, 20, 20), width=2)
        # velocity tick
        dr.line([(x, y), (x + o["vx"] * 2, y + o["vy"] * 2)], fill=(255, 255, 255), width=1)
        dr.text((x - r, y - r - 10), o["oid"], fill=(200, 200, 200), font=font)
    dr.text((4, 4), f"{seq_id} t={t}", fill=(180, 180, 190), font=font)
    return img


def _public_agents(agents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Visible state for meta — includes mass/radius (physics observables), no futures."""
    out = []
    for o in agents:
        out.append({
            "oid": o["oid"],
            "class": o["class"],
            "mass": float(o["mass"]),
            "r": float(o["r"]),
            "x": float(o["x"]),
            "y": float(o["y"]),
            "vx": float(o["vx"]),
            "vy": float(o["vy"]),
        })
    return out


def generate_sequence(
    seq_id: str,
    rng: random.Random,
    n_frames: int,
    *,
    hardneg_kind: str | None = None,
) -> dict[str, Any]:
    kind = hardneg_kind if hardneg_kind is not None else _pick_hardneg_kind(rng)
    agents = _sample_agents(rng, hardneg_kind=kind)
    frames_meta = []
    frames_img = []
    full_states = []  # internal for GT rollout from each t
    for t in range(n_frames):
        frames_meta.append({"t": t, "agents": _public_agents(agents)})
        frames_img.append(_render(agents, t, seq_id))
        full_states.append([dict(o) for o in agents])
        agents, _ = step_world(agents)

    # Build GT sidecars: for query frames and each action × k, true consequence
    # under applying action at query_t then rolling k steps with elastic physics.
    futures = []
    # query every other frame leaving room for k=5
    for query_t in range(0, n_frames - max(HORIZONS) - 1, 2):
        state0 = full_states[query_t]
        for k in HORIZONS:
            if query_t + k >= n_frames:
                continue
            # Natural future (coast world without re-applying — for reference)
            # Action-conditional GT: apply action then k elastic steps
            for action in ACTIONS:
                roll = rollout(state0, k, action=action)
                futures.append({
                    "query_t": query_t,
                    "k": k,
                    "action": action,
                    "gt_is_safe": not roll["ego_collision"],
                    "gt_consequence": consequence_label(roll, state0),
                    "gt_partner": roll["partner_of_ego"],
                    "gt_any_collision": roll["any_collision"],
                    "gt_agents": [
                        {"oid": o["oid"], "x": o["x"], "y": o["y"], "vx": o["vx"], "vy": o["vy"]}
                        for o in roll["agents"]
                    ],
                })
            # Also record "natural" passive future at query_t+k from recorded tape
            # (world already stepped without hypo action) — for inverse-style compare
            natural = full_states[query_t + k]
            # Detect ego overlap in natural tape
            ego = next(o for o in natural if o["oid"] == "ego")
            partner = None
            for o in natural:
                if o["oid"] == "ego":
                    continue
                if math.hypot(o["x"] - ego["x"], o["y"] - ego["y"]) < float(o["r"]) + float(ego["r"]) - 0.5:
                    partner = o["oid"]
                    break
            # collisions that occurred along the natural path
            # approximate by checking each intermediate
            nat_partner = partner
            for tt in range(query_t + 1, query_t + k + 1):
                st = full_states[tt]
                eg = next(o for o in st if o["oid"] == "ego")
                for o in st:
                    if o["oid"] == "ego":
                        continue
                    if math.hypot(o["x"] - eg["x"], o["y"] - eg["y"]) < float(o["r"]) + float(eg["r"]) - 0.5:
                        nat_partner = o["oid"]
                        break
                if nat_partner:
                    break
            fake = {
                "ego_collision": nat_partner is not None,
                "any_collision": nat_partner is not None,
                "partner_of_ego": nat_partner,
            }
            futures.append({
                "query_t": query_t,
                "k": k,
                "action": "natural_passive",
                "gt_is_safe": nat_partner is None,
                "gt_consequence": consequence_label(fake, state0) if nat_partner else "clear",
                "gt_partner": nat_partner,
                "gt_any_collision": nat_partner is not None,
                "gt_agents": [
                    {"oid": o["oid"], "x": o["x"], "y": o["y"], "vx": o["vx"], "vy": o["vy"]}
                    for o in natural
                ],
            })

    meta = {
        "seq_id": seq_id,
        "domain": "collision_predictive",
        "style": "topdown_merge_lane",
        "hardneg_kind": kind,
        "n_frames": n_frames,
        "arena": {"w": ARENA_W, "h": ARENA_H, "margin": MARGIN},
        "actions": list(ACTIONS),
        "horizons": list(HORIZONS),
        "frames": frames_meta,
        "emit_schema": ["chosen_action", "predicted_consequence", "is_safe"],
        "anti_contamination": {
            "futures_in_meta": False,
            "consequences_gt_sidecar_only": True,
            "rule": "GT consequences / future agents NEVER in prompt/memory/retrieval at inference",
        },
        "integrates_with": [
            "examples/video_temporal_prototype.py::WorkingMemory",
            "examples/inverse_planning/ (Fase2 action-conditional)",
            "examples/distance_est/ (floor-scale note; depth→mass deferred)",
        ],
    }
    gt_doc = {
        "seq_id": seq_id,
        "note": "POST-HOC ONLY — never load into prompts/memory/retrieval at inference",
        "futures": futures,
    }
    return {"meta": meta, "gt": gt_doc, "images": frames_img}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("data/collision_predictive"))
    ap.add_argument("--n-seq", type=int, default=DEFAULT_N)
    ap.add_argument("--n-train", type=int, default=DEFAULT_TRAIN)
    ap.add_argument("--n-eval", type=int, default=DEFAULT_EVAL)
    ap.add_argument("--seed", type=int, default=24092447)
    ap.add_argument("--frames-min", type=int, default=12)
    ap.add_argument("--frames-max", type=int, default=18)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    np.random.seed(args.seed)
    out: Path = args.out
    train_dir = out / "train"
    eval_dir = out / "eval"
    train_dir.mkdir(parents=True, exist_ok=True)
    eval_dir.mkdir(parents=True, exist_ok=True)

    index = []
    n_train = args.n_train
    assert args.n_train + args.n_eval == args.n_seq

    hardneg_counts: dict[str, int] = {}
    for i in range(args.n_seq):
        seq_id = f"cp_{i:03d}"
        split = "train" if i < n_train else "eval"
        n_frames = rng.randint(args.frames_min, args.frames_max)
        kind = _pick_hardneg_kind(rng)
        hardneg_counts[kind] = hardneg_counts.get(kind, 0) + 1
        bundle = generate_sequence(seq_id, rng, n_frames, hardneg_kind=kind)
        dest = (train_dir if split == "train" else eval_dir) / seq_id
        dest.mkdir(parents=True, exist_ok=True)
        frames_dir = dest / "frames"
        frames_dir.mkdir(exist_ok=True)
        for t, im in enumerate(bundle["images"]):
            im.save(frames_dir / f"frame_{t:02d}.png")
        (dest / "meta.json").write_text(json.dumps(bundle["meta"], indent=2) + "\n")
        (dest / "consequences_gt.json").write_text(json.dumps(bundle["gt"], indent=2) + "\n")
        index.append({
            "seq_id": seq_id,
            "split": split,
            "n_frames": n_frames,
            "hardneg_kind": kind,
            "n_gt_futures": len(bundle["gt"]["futures"]),
            "path": str(dest.relative_to(out)),
        })
        print(
            f"[gen] {seq_id} split={split} frames={n_frames} "
            f"hardneg={kind} gt={len(bundle['gt']['futures'])}",
            flush=True,
        )

    train_ids = [e["seq_id"] for e in index if e["split"] == "train"]
    eval_ids = [e["seq_id"] for e in index if e["split"] == "eval"]
    assert not (set(train_ids) & set(eval_ids))

    retrieval = {
        "rule": "train only — eval ids rejected",
        "train_ids": train_ids,
        "eval_ids_NOT_INDEXED": eval_ids,
        "leak": [],
    }
    (out / "retrieval_index_train.json").write_text(json.dumps(retrieval, indent=2) + "\n")
    (out / "INDEX.json").write_text(json.dumps({"seed": args.seed, "sequences": index}, indent=2) + "\n")
    summary = {
        "domain": "collision_predictive",
        "seed": args.seed,
        "n_seq": args.n_seq,
        "n_train": len(train_ids),
        "n_eval": len(eval_ids),
        "horizons": list(HORIZONS),
        "actions": list(ACTIONS),
        "emit_schema": ["chosen_action", "predicted_consequence", "is_safe"],
        "physics": "elastic_disk_2d_masses",
        "hardneg_mix": {
            "unsafe_look_safe": HARDNEG_UNSAFE_LOOK_SAFE,
            "safe_look_unsafe": HARDNEG_SAFE_LOOK_UNSAFE,
            "near_miss_choice": HARDNEG_NEAR_MISS,
            "baseline_remainder": round(
                1.0 - HARDNEG_UNSAFE_LOOK_SAFE - HARDNEG_SAFE_LOOK_UNSAFE - HARDNEG_NEAR_MISS, 4
            ),
            "realized_counts": hardneg_counts,
        },
        "anti_contamination": "consequences_gt.json sidecar only; meta has no futures",
        "adapter_future": "data/lora_adapter_collision/ (empty; VLM deferred)",
        "quantum_adapter": "data/lora_adapter/ READ-ONLY — never touch",
        "branch_tag": "tip-choose-safest-n",
    }
    (out / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    (out / "SUMMARY.md").write_text(
        f"# Collision predictive dataset\n\n"
        f"seed={args.seed} n={args.n_seq} train={len(train_ids)} eval={len(eval_ids)}\n"
        f"actions={list(ACTIONS)} horizons={list(HORIZONS)}\n"
        f"hardneg_counts={hardneg_counts}\n"
        f"GT = consequences_gt.json sidecars only.\n"
        f"branch=tip-choose-safest-n\n"
    )
    (out / "SCENE_CHOICE.md").write_text(
        "# Scene choice (collision predictive)\n\n"
        "Top-down **merge lane** with ego + vehicles/pedestrians (masses + radii).\n"
        "Elastic disk collisions. Discrete hypo actions on ego.\n\n"
        "Hardneg mix (choose_safest-n): unsafe-looking-but-safe, safe-looking-but-unsafe,\n"
        "near-miss choice pressure — meta.hardneg_kind only; GT still post-hoc sidecar.\n\n"
        "Deliberately **not** street-F1 (no multi-light intersection render),\n"
        "**not** inverse corridor balls/boxes/signal, **not** quantum.\n"
    )
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
