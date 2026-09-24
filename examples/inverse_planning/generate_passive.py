#!/usr/bin/env python3
"""Fase 1 passive inverse-planning scene generator (CPU).

Domain choice (LOCKED, visually distinct from street-lights F1):
  TOP-DOWN CORRIDOR ARENA — colored balls + boxes slide on a flat 2D plane
  with elastic wall bounces; ONE discrete corridor SIGNAL (red/amber/green)
  that toggles on a fixed schedule. No cars, no street intersection, no
  multi-light traffic scene. Keeps this domain separable from video_f1.

For each sequence:
  frames/frame_XX.png     — rendered top-down view
  meta.json               — visible history (objects + signal per frame);
                            NO future GT
  futures_gt.json         — SIDECAR only: for each query frame N and k in
                            {1,3,5}, the true state at N+k (post-hoc eval)

Train/eval split strict (default 32/8). Retrieval index (if built) = train only.

Usage:
  python examples/inverse_planning/generate_passive.py
  python examples/inverse_planning/generate_passive.py --n-seq 40 --seed 240924
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

from physics import ARENA_H, ARENA_W, MARGIN, _reflect_step

# ---------------------------------------------------------------------------
# Visual palette — deliberately NOT street-F1 (no asphalt lanes / car sprites)
# ---------------------------------------------------------------------------
BG = (32, 36, 48)          # dark slate floor
GRID = (48, 54, 70)
WALL = (90, 96, 112)
SIGNAL_COLORS = {
    "red": (220, 64, 64),
    "amber": (230, 170, 50),
    "green": (60, 190, 100),
}
BALL_PALETTE = [
    (70, 160, 240),   # blue
    (240, 120, 70),   # orange
    (180, 90, 220),   # purple
    (90, 210, 180),   # teal
]
BOX_PALETTE = [
    (200, 180, 90),
    (160, 110, 80),
    (120, 160, 200),
]

HORIZONS = (1, 3, 5)
DEFAULT_N_SEQ = 40
DEFAULT_TRAIN = 32
DEFAULT_EVAL = 8


def _font(size: int = 12):
    try:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
    except Exception:
        return ImageFont.load_default()


def _sample_object(rng: random.Random, oid: int) -> dict[str, Any]:
    shape = rng.choice(["ball", "box"])
    color = rng.choice(BALL_PALETTE if shape == "ball" else BOX_PALETTE)
    x = rng.uniform(MARGIN + 10, ARENA_W - MARGIN - 10)
    y = rng.uniform(MARGIN + 10, ARENA_H - MARGIN - 10)
    # speed 2..12 px/frame; angle any
    speed = rng.uniform(2.0, 12.0)
    ang = rng.uniform(0, 2 * math.pi)
    vx, vy = speed * math.cos(ang), speed * math.sin(ang)
    return {
        "oid": f"o{oid}",
        "shape": shape,
        "color": list(color),
        "x": float(x),
        "y": float(y),
        "vx": float(vx),
        "vy": float(vy),
        "r": 7 if shape == "ball" else 8,
    }


def _signal_schedule(n_frames: int, period: int, phase: int) -> list[str]:
    cycle = ["green", "green", "amber", "red", "red", "red"]
    out = []
    for t in range(n_frames):
        out.append(cycle[(t + phase) % len(cycle)])
    return out


def _step_objects(objs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    nxt = []
    for o in objs:
        x, y, vx, vy = _reflect_step(o["x"], o["y"], o["vx"], o["vy"], dt=1.0)
        d = dict(o)
        d.update({"x": x, "y": y, "vx": vx, "vy": vy})
        nxt.append(d)
    return nxt


def _render(objs: list[dict[str, Any]], signal: str, frame_idx: int, seq_id: str) -> Image.Image:
    img = Image.new("RGB", (ARENA_W, ARENA_H), BG)
    dr = ImageDraw.Draw(img)
    # grid (top-down feel)
    for gx in range(0, ARENA_W, 20):
        dr.line([(gx, 0), (gx, ARENA_H)], fill=GRID, width=1)
    for gy in range(0, ARENA_H, 20):
        dr.line([(0, gy), (ARENA_W, gy)], fill=GRID, width=1)
    # wall border
    dr.rectangle([2, 2, ARENA_W - 3, ARENA_H - 3], outline=WALL, width=3)
    # corridor signal panel (top-center) — NOT a street light pole
    sx0, sy0, sx1, sy1 = ARENA_W // 2 - 18, 4, ARENA_W // 2 + 18, 22
    dr.rectangle([sx0, sy0, sx1, sy1], fill=(20, 20, 28), outline=(180, 180, 190), width=1)
    sc = SIGNAL_COLORS[signal]
    dr.ellipse([sx0 + 10, sy0 + 3, sx1 - 10, sy1 - 3], fill=sc)
    # objects
    for o in objs:
        cx, cy, r = o["x"], o["y"], o["r"]
        col = tuple(int(c) for c in o["color"])
        if o["shape"] == "ball":
            dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col, outline=(255, 255, 255))
        else:
            dr.rectangle([cx - r, cy - r, cx + r, cy + r], fill=col, outline=(255, 255, 255))
        # oid tag
        dr.text((cx - 4, cy - 4), o["oid"][-1], fill=(0, 0, 0), font=_font(10))
    # footer label
    dr.text((6, ARENA_H - 14), f"{seq_id} t={frame_idx:02d} sig={signal}", fill=(160, 165, 180), font=_font(10))
    return img


def _public_frame_state(objs: list[dict[str, Any]], signal: str, t: int) -> dict[str, Any]:
    """State visible to the model (no futures)."""
    return {
        "t": t,
        "signal": signal,
        "objects": [
            {
                "oid": o["oid"],
                "shape": o["shape"],
                "color": o["color"],
                "x": round(o["x"], 3),
                "y": round(o["y"], 3),
                "vx": round(o["vx"], 3),
                "vy": round(o["vy"], 3),
            }
            for o in objs
        ],
    }


def generate_sequence(seq_idx: int, rng: random.Random, n_frames: int) -> dict[str, Any]:
    n_obj = rng.randint(2, 4)
    objs = [_sample_object(rng, i) for i in range(n_obj)]
    period = rng.choice([4, 5, 6])
    phase = rng.randint(0, 5)
    signals = _signal_schedule(n_frames, period, phase)
    frames_states: list[dict[str, Any]] = []
    renders: list[Image.Image] = []
    for t in range(n_frames):
        st = _public_frame_state(objs, signals[t], t)
        frames_states.append(st)
        renders.append(_render(objs, signals[t], t, f"seq_{seq_idx:03d}"))
        objs = _step_objects(objs)

    # Build GT futures sidecar: for each N where N+k < n_frames
    futures: list[dict[str, Any]] = []
    for n in range(n_frames):
        for k in HORIZONS:
            tgt = n + k
            if tgt >= n_frames:
                continue
            futures.append({
                "query_t": n,
                "k": k,
                "gt_t": tgt,
                "gt_signal": frames_states[tgt]["signal"],
                "gt_objects": frames_states[tgt]["objects"],
            })

    return {
        "n_frames": n_frames,
        "n_objects": n_obj,
        "signal_period": period,
        "signal_phase": phase,
        "frames": frames_states,
        "futures_gt": futures,
        "renders": renders,
    }


def write_sequence(out_dir: Path, seq_idx: int, split: str, data: dict[str, Any], seed: int) -> dict[str, Any]:
    seq_id = f"seq_{seq_idx:03d}"
    root = out_dir / split / seq_id
    frames_dir = root / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    for t, img in enumerate(data["renders"]):
        img.save(frames_dir / f"frame_{t:02d}.png")

    meta = {
        "domain": "inverse_planning_passive",
        "scene_style": "topdown_corridor_balls_boxes_one_signal",
        "scene_style_note": (
            "Top-down 2D corridor arena with sliding balls/boxes + one discrete "
            "corridor signal. Visually distinct from street-lights video F1 "
            "(no cars, no multi-light intersection)."
        ),
        "seq_id": seq_id,
        "split": split,
        "seed": seed,
        "n_frames": data["n_frames"],
        "n_objects": data["n_objects"],
        "signal_period": data["signal_period"],
        "signal_phase": data["signal_phase"],
        "horizons_supported": list(HORIZONS),
        "frames": data["frames"],  # visible history only — no futures
        "anti_contamination": {
            "futures_in_meta": False,
            "gt_sidecar": "futures_gt.json",
            "rule": "GT futures NEVER passed to model; eval loads sidecar post-hoc only",
        },
    }
    (root / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")

    gt = {
        "seq_id": seq_id,
        "split": split,
        "sidecar": True,
        "usage": "POST_HOC_EVAL_ONLY",
        "futures": data["futures_gt"],
    }
    (root / "futures_gt.json").write_text(json.dumps(gt, indent=2) + "\n")

    return {
        "seq_id": seq_id,
        "split": split,
        "n_frames": data["n_frames"],
        "n_objects": data["n_objects"],
        "n_futures": len(data["futures_gt"]),
        "path": str(root),
    }


def build_retrieval_index(out_dir: Path, train_entries: list[dict[str, Any]]) -> Path:
    """Train-only retrieval index: store last-frame object centroids + signal.

    Eval must NEVER be indexed (anti-contam lock).
    """
    index = []
    for e in train_entries:
        meta = json.loads((Path(e["path"]) / "meta.json").read_text())
        last = meta["frames"][-1]
        index.append({
            "seq_id": e["seq_id"],
            "split": "train",
            "t": last["t"],
            "signal": last["signal"],
            "objects": [
                {"oid": o["oid"], "shape": o["shape"], "x": o["x"], "y": o["y"]}
                for o in last["objects"]
            ],
        })
    idx_path = out_dir / "retrieval_index_train.json"
    idx_path.write_text(json.dumps({
        "domain": "inverse_planning_passive",
        "source_split": "train_only",
        "n_entries": len(index),
        "anti_contamination": "eval sequences MUST NOT appear here",
        "entries": index,
    }, indent=2) + "\n")
    return idx_path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n-seq", type=int, default=DEFAULT_N_SEQ)
    ap.add_argument("--n-train", type=int, default=DEFAULT_TRAIN)
    ap.add_argument("--n-eval", type=int, default=DEFAULT_EVAL)
    ap.add_argument("--seed", type=int, default=240924)
    ap.add_argument("--out", type=Path, default=Path("data/inverse_planning"))
    ap.add_argument("--min-frames", type=int, default=10)
    ap.add_argument("--max-frames", type=int, default=20)
    args = ap.parse_args()

    assert args.n_train + args.n_eval == args.n_seq, "n_train + n_eval must equal n_seq"
    assert args.n_seq >= 40, "need ≥40 sequences for Fase 1"
    assert 10 <= args.min_frames <= args.max_frames <= 20

    rng = random.Random(args.seed)
    np.random.seed(args.seed)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "train").mkdir(exist_ok=True)
    (args.out / "eval").mkdir(exist_ok=True)

    entries: list[dict[str, Any]] = []
    for i in range(args.n_seq):
        split = "train" if i < args.n_train else "eval"
        n_frames = rng.randint(args.min_frames, args.max_frames)
        # per-seq rng derived for reproducibility
        seq_rng = random.Random(args.seed * 1009 + i * 17)
        data = generate_sequence(i, seq_rng, n_frames)
        e = write_sequence(args.out, i, split, data, seed=args.seed)
        entries.append(e)
        print(f"  [{split}] {e['seq_id']} frames={e['n_frames']} objs={e['n_objects']} futures={e['n_futures']}")

    train_e = [e for e in entries if e["split"] == "train"]
    eval_e = [e for e in entries if e["split"] == "eval"]
    idx_path = build_retrieval_index(args.out, train_e)

    # contamination self-check: eval ids must not be in retrieval index
    idx = json.loads(idx_path.read_text())
    idx_ids = {e["seq_id"] for e in idx["entries"]}
    eval_ids = {e["seq_id"] for e in eval_e}
    leak = idx_ids & eval_ids
    assert not leak, f"RETRIEVAL LEAK: {leak}"

    summary = {
        "domain": "inverse_planning_passive",
        "fase": 1,
        "scene_style": "topdown_corridor_balls_boxes_one_signal",
        "seed": args.seed,
        "n_seq": args.n_seq,
        "n_train": len(train_e),
        "n_eval": len(eval_e),
        "horizons": list(HORIZONS),
        "retrieval_index": str(idx_path),
        "retrieval_leak": list(leak),
        "adapter_target_later": "data/lora_adapter_inverse/",
        "quantum_adapter": "data/lora_adapter/ READ-ONLY — do not use for this domain numbers",
        "street_f1": "data/video_synth/fase1/ — SEPARATE domain, do not mix",
        "entries": entries,
    }
    (args.out / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    (args.out / "INDEX.json").write_text(json.dumps({"entries": entries}, indent=2) + "\n")

    md = f"""# Inverse planning — Fase 1 passive dataset

- **Scene style:** top-down corridor arena, balls/boxes + one discrete signal
  (NOT street-lights F1; NOT classical sport/projectile stills; NOT quantum).
- **Seed:** {args.seed}
- **Sequences:** {args.n_seq} (train={len(train_e)}, eval={len(eval_e)})
- **Frames/seq:** {args.min_frames}–{args.max_frames}
- **Horizons k:** {list(HORIZONS)}
- **GT futures:** `futures_gt.json` sidecars only — never in `meta.json` / prompts
- **Retrieval index:** train-only → `{idx_path.name}` (leak={list(leak) or '∅'})
- **Adapter (later, GPU free):** `data/lora_adapter_inverse/` only
"""
    (args.out / "SUMMARY.md").write_text(md)
    (args.out / "SCENE_CHOICE.md").write_text(
        "# Scene choice (Fase 1)\n\n"
        "Top-down 2D **corridor arena** with sliding colored **balls and boxes** "
        "and **one** discrete corridor signal (red/amber/green panel).\n\n"
        "Chosen to stay visually and semantically separate from:\n"
        "- street-lights video F1 (cars + multi-light intersection)\n"
        "- classical sport/projectile stills\n"
        "- quantum circuit scenes\n"
    )
    print(f"\nDONE n={args.n_seq} train={len(train_e)} eval={len(eval_e)} leak={leak or '∅'}")
    print(f"Wrote {args.out / 'SUMMARY.json'}")


if __name__ == "__main__":
    main()
