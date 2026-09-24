#!/usr/bin/env python3
"""Generate 200+ varied visual physics scenes (PNG frames + meta.json).

Self-contained: Pillow + numpy only. No display, no paid APIs.
Deterministic with --seed.

Usage:
  python examples/synthetic_physics_dataset.py
  python examples/synthetic_physics_dataset.py --n-scenes 220 --out data/scenes --seed 42
  python examples/synthetic_physics_dataset.py --n-scenes 3 --frames-per-scene 24  # smoke
"""

from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw

# ---------------------------------------------------------------------------
# Variation axes (combinatorial / sampled)
# ---------------------------------------------------------------------------

SHAPES = ("square", "circle", "triangle", "rectangle", "irregular_polygon")
COLORS = ("red", "blue", "green", "yellow")
SIZES = ("small", "medium", "large")
MATERIALS = ("dense", "light", "hollow")
SURFACES = ("hard_elastic_floor", "soft_lossy_floor", "ramp", "curve")
CONDITIONS = ("vacuum_freefall", "air_drag", "lateral_wind", "mars_g", "moon_g")

COLOR_RGB = {
    "red": (220, 60, 60),
    "blue": (50, 100, 220),
    "green": (50, 180, 80),
    "yellow": (230, 200, 40),
}

SIZE_RADIUS = {"small": 8, "medium": 14, "large": 22}

# mass scale and bounce restitution by material
MATERIAL_MASS = {"dense": 2.5, "light": 0.6, "hollow": 0.35}
MATERIAL_REST_MULT = {"dense": 0.85, "light": 1.0, "hollow": 1.15}

# base gravity (px/s^2) and mods by condition
G_EARTH = 480.0
CONDITION_G = {
    "vacuum_freefall": 1.0,
    "air_drag": 1.0,
    "lateral_wind": 1.0,
    "mars_g": 0.38,
    "moon_g": 0.165,
}
CONDITION_DRAG = {
    "vacuum_freefall": 0.0,
    "air_drag": 0.018,
    "lateral_wind": 0.008,
    "mars_g": 0.004,
    "moon_g": 0.0,
}
CONDITION_WIND_X = {
    "vacuum_freefall": 0.0,
    "air_drag": 0.0,
    "lateral_wind": 90.0,  # px/s^2 lateral accel
    "mars_g": 0.0,
    "moon_g": 0.0,
}

SURFACE_REST = {
    "hard_elastic_floor": 0.88,
    "soft_lossy_floor": 0.42,
    "ramp": 0.75,
    "curve": 0.70,
}

WIDTH, HEIGHT = 160, 120
DT = 1.0 / 30.0


@dataclass
class Body:
    shape: str
    color: str
    size: str
    material: str
    x: float
    y: float
    vx: float
    vy: float
    radius: float
    mass: float
    polygon: list[tuple[float, float]] = field(default_factory=list)

    def as_meta(self) -> dict[str, Any]:
        return {
            "shape": self.shape,
            "color": self.color,
            "size": self.size,
            "material": self.material,
            "radius_px": self.radius,
            "mass": round(self.mass, 4),
        }


def _irregular_verts(rng: random.Random, r: float, n: int = 6) -> list[tuple[float, float]]:
    verts: list[tuple[float, float]] = []
    for i in range(n):
        ang = 2 * math.pi * i / n + rng.uniform(-0.2, 0.2)
        rr = r * rng.uniform(0.55, 1.15)
        verts.append((rr * math.cos(ang), rr * math.sin(ang)))
    return verts


def _make_body(
    rng: random.Random,
    *,
    shape: str,
    color: str,
    size: str,
    material: str,
    x: float,
    y: float,
    vx: float = 0.0,
    vy: float = 0.0,
) -> Body:
    r = float(SIZE_RADIUS[size])
    if shape == "rectangle":
        r = r * 1.15
    mass = MATERIAL_MASS[material] * (r / 14.0) ** 2
    poly: list[tuple[float, float]] = []
    if shape == "irregular_polygon":
        poly = _irregular_verts(rng, r)
    return Body(
        shape=shape,
        color=color,
        size=size,
        material=material,
        x=x,
        y=y,
        vx=vx,
        vy=vy,
        radius=r,
        mass=mass,
        polygon=poly,
    )


def _surface_y(surface: str, x: float, floor_base: float) -> float:
    """Floor height (y, origin top) at horizontal position x."""
    if surface == "ramp":
        # left high, right low
        t = max(0.0, min(1.0, x / max(1.0, WIDTH - 1)))
        return floor_base - 28.0 * (1.0 - t)
    if surface == "curve":
        # concave bowl
        mid = WIDTH / 2.0
        dx = (x - mid) / mid
        return floor_base - 22.0 * (dx * dx)
    return floor_base


def _draw_surface(draw: ImageDraw.ImageDraw, surface: str, floor_base: int) -> None:
    pts: list[tuple[int, int]] = []
    for x in range(WIDTH):
        y = int(round(_surface_y(surface, float(x), float(floor_base))))
        pts.append((x, y))
    # fill below surface
    poly = [(0, HEIGHT - 1), *pts, (WIDTH - 1, HEIGHT - 1)]
    if surface == "soft_lossy_floor":
        fill = (70, 90, 70)
    elif surface == "hard_elastic_floor":
        fill = (90, 90, 100)
    elif surface == "ramp":
        fill = (100, 85, 70)
    else:
        fill = (80, 80, 110)
    draw.polygon(poly, fill=fill)
    # surface edge
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=(180, 180, 190), width=2)


def _draw_body(draw: ImageDraw.ImageDraw, body: Body) -> None:
    rgb = COLOR_RGB[body.color]
    cx, cy = body.x, body.y
    r = body.radius
    if body.shape == "circle":
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgb)
    elif body.shape == "square":
        draw.rectangle([cx - r, cy - r, cx + r, cy + r], fill=rgb)
    elif body.shape == "rectangle":
        draw.rectangle([cx - r * 1.3, cy - r * 0.7, cx + r * 1.3, cy + r * 0.7], fill=rgb)
    elif body.shape == "triangle":
        pts = [
            (cx, cy - r),
            (cx - r, cy + r),
            (cx + r, cy + r),
        ]
        draw.polygon(pts, fill=rgb)
    else:  # irregular_polygon
        verts = body.polygon or _irregular_verts(random.Random(0), r)
        pts = [(cx + vx, cy + vy) for vx, vy in verts]
        draw.polygon(pts, fill=rgb)


def _resolve_collision(a: Body, b: Body) -> None:
    """Simple elastic-ish 2-body collision (equal treatment by mass)."""
    dx = b.x - a.x
    dy = b.y - a.y
    dist = math.hypot(dx, dy) or 1e-6
    min_d = a.radius + b.radius
    if dist >= min_d:
        return
    nx, ny = dx / dist, dy / dist
    # separate
    overlap = min_d - dist
    inv_m = 1.0 / a.mass + 1.0 / b.mass
    a.x -= nx * overlap * (1.0 / a.mass) / inv_m
    a.y -= ny * overlap * (1.0 / a.mass) / inv_m
    b.x += nx * overlap * (1.0 / b.mass) / inv_m
    b.y += ny * overlap * (1.0 / b.mass) / inv_m
    # relative velocity along normal
    rvx = a.vx - b.vx
    rvy = a.vy - b.vy
    vn = rvx * nx + rvy * ny
    if vn > 0:
        return
    e = 0.75
    j = -(1 + e) * vn / inv_m
    a.vx += (j / a.mass) * nx
    a.vy += (j / a.mass) * ny
    b.vx -= (j / b.mass) * nx
    b.vy -= (j / b.mass) * ny


def _governing_law(
    surface: str,
    condition: str,
    multi: bool,
    materials: list[str],
) -> str:
    parts = [
        f"Newtonian 2D kinematics under g_eff={CONDITION_G[condition]:.3f}*g_earth",
    ]
    if CONDITION_DRAG[condition] > 0:
        parts.append(f"linear air drag coeff={CONDITION_DRAG[condition]}")
    if abs(CONDITION_WIND_X[condition]) > 0:
        parts.append(f"lateral wind accel={CONDITION_WIND_X[condition]} px/s^2")
    parts.append(f"surface={surface} restitution_base={SURFACE_REST[surface]}")
    parts.append(f"materials={','.join(materials)} (mass/restitution scale)")
    if surface == "ramp":
        parts.append("inclined floor (ramp): normal bounce + along-slope slide")
    if surface == "curve":
        parts.append("concave curve floor (bowl)")
    if multi:
        parts.append("multi-body elastic collisions (impulse along contact normal)")
    return "; ".join(parts)


def simulate_scene(
    rng: random.Random,
    *,
    shape: str,
    color: str,
    size: str,
    material: str,
    surface: str,
    condition: str,
    n_frames: int,
    multi: bool,
    scene_seed: int,
) -> tuple[list[Image.Image], dict[str, Any]]:
    floor_base = HEIGHT - 6
    g = G_EARTH * CONDITION_G[condition]
    drag = CONDITION_DRAG[condition]
    wind = CONDITION_WIND_X[condition]
    rest_base = SURFACE_REST[surface] * MATERIAL_REST_MULT[material]
    rest_base = max(0.15, min(0.98, rest_base))

    bodies: list[Body] = []
    # primary object drops from upper region
    x0 = rng.uniform(WIDTH * 0.25, WIDTH * 0.75)
    y0 = rng.uniform(12, 36)
    vx0 = rng.uniform(-40, 40) if condition == "lateral_wind" else rng.uniform(-15, 15)
    bodies.append(
        _make_body(
            rng,
            shape=shape,
            color=color,
            size=size,
            material=material,
            x=x0,
            y=y0,
            vx=vx0,
            vy=rng.uniform(-10, 10),
        )
    )

    if multi:
        # second object: different shape/color/material sample
        s2 = rng.choice(SHAPES)
        c2 = rng.choice([c for c in COLORS if c != color] or list(COLORS))
        z2 = rng.choice(SIZES)
        m2 = rng.choice(MATERIALS)
        bodies.append(
            _make_body(
                rng,
                shape=s2,
                color=c2,
                size=z2,
                material=m2,
                x=rng.uniform(WIDTH * 0.2, WIDTH * 0.8),
                y=rng.uniform(20, 50),
                vx=rng.uniform(-50, 50),
                vy=rng.uniform(-20, 20),
            )
        )

    trajectory: list[dict[str, Any]] = []
    frames: list[Image.Image] = []

    for fi in range(n_frames):
        frame_snap: list[dict[str, Any]] = []
        for bi, body in enumerate(bodies):
            # forces
            ax = wind / max(body.mass, 0.1) * 0.4 + wind * 0.6  # wind mostly independent of mass
            ay = g
            # drag ~ -k * v / mass (heavier resists drag more)
            if drag > 0:
                ax -= drag * body.vx / body.mass
                ay -= drag * body.vy / body.mass
            body.vx += ax * DT
            body.vy += ay * DT
            body.x += body.vx * DT
            body.y += body.vy * DT

            # walls
            if body.x < body.radius:
                body.x = body.radius
                body.vx = abs(body.vx) * 0.8
            if body.x > WIDTH - body.radius:
                body.x = WIDTH - body.radius
                body.vx = -abs(body.vx) * 0.8

            # floor / surface
            sy = _surface_y(surface, body.x, float(floor_base)) - body.radius
            if body.y >= sy:
                body.y = sy
                if abs(body.vy) > 2.0:
                    body.vy = -body.vy * rest_base
                    # ramp: add slope-parallel push
                    if surface == "ramp":
                        body.vx += 25.0 * DT
                    if surface == "curve":
                        mid = WIDTH / 2.0
                        body.vx += -0.15 * (body.x - mid)
                else:
                    body.vy = 0.0
                    body.vx *= 0.96  # friction

            frame_snap.append(
                {
                    "id": bi,
                    "x": round(body.x, 3),
                    "y": round(body.y, 3),
                    "vx": round(body.vx, 3),
                    "vy": round(body.vy, 3),
                }
            )

        if multi and len(bodies) >= 2:
            _resolve_collision(bodies[0], bodies[1])

        trajectory.append({"frame": fi, "objects": frame_snap})

        # render
        img = Image.new("RGB", (WIDTH, HEIGHT), (28, 28, 36))
        draw = ImageDraw.Draw(img)
        _draw_surface(draw, surface, floor_base)
        for body in bodies:
            _draw_body(draw, body)
        frames.append(img)

    primary = bodies[0]
    meta: dict[str, Any] = {
        "scene_seed": scene_seed,
        "shape": primary.shape,
        "color": primary.color,
        "size": primary.size,
        "material": primary.material,
        "surface": surface,
        "gravity_condition": condition,
        "g_px_s2": round(g, 3),
        "restitution": round(rest_base, 4),
        "n_frames": n_frames,
        "dt": DT,
        "width": WIDTH,
        "height": HEIGHT,
        "multi_object": multi,
        "objects": [b.as_meta() for b in bodies],
        "trajectory": trajectory,
        "governing_law": _governing_law(
            surface, condition, multi, [b.material for b in bodies]
        ),
        "seed": scene_seed,
    }
    return frames, meta


def sample_configs(n_scenes: int, rng: random.Random) -> list[dict[str, Any]]:
    """Sample varied configs; guarantee axis coverage then fill randomly."""
    configs: list[dict[str, Any]] = []
    # systematic coverage pass
    axes = [
        ("shape", SHAPES),
        ("color", COLORS),
        ("size", SIZES),
        ("material", MATERIALS),
        ("surface", SURFACES),
        ("condition", CONDITIONS),
    ]
    for axis_name, values in axes:
        for v in values:
            cfg = {
                "shape": rng.choice(SHAPES),
                "color": rng.choice(COLORS),
                "size": rng.choice(SIZES),
                "material": rng.choice(MATERIALS),
                "surface": rng.choice(SURFACES),
                "condition": rng.choice(CONDITIONS),
                "multi": rng.random() < 0.28,
            }
            cfg[axis_name if axis_name != "condition" else "condition"] = v
            configs.append(cfg)

    # multi-object guaranteed batch
    for _ in range(min(20, n_scenes)):
        configs.append(
            {
                "shape": rng.choice(SHAPES),
                "color": rng.choice(COLORS),
                "size": rng.choice(SIZES),
                "material": rng.choice(MATERIALS),
                "surface": rng.choice(SURFACES),
                "condition": rng.choice(CONDITIONS),
                "multi": True,
            }
        )

    while len(configs) < n_scenes:
        configs.append(
            {
                "shape": rng.choice(SHAPES),
                "color": rng.choice(COLORS),
                "size": rng.choice(SIZES),
                "material": rng.choice(MATERIALS),
                "surface": rng.choice(SURFACES),
                "condition": rng.choice(CONDITIONS),
                "multi": rng.random() < 0.30,
            }
        )

    rng.shuffle(configs)
    return configs[:n_scenes]


def write_summary(out: Path, metas: list[dict[str, Any]], seed: int) -> None:
    counts = {
        "shape": Counter(m["shape"] for m in metas),
        "color": Counter(m["color"] for m in metas),
        "size": Counter(m["size"] for m in metas),
        "material": Counter(m["material"] for m in metas),
        "surface": Counter(m["surface"] for m in metas),
        "gravity_condition": Counter(m["gravity_condition"] for m in metas),
        "multi_object": Counter(bool(m["multi_object"]) for m in metas),
    }
    summary = {
        "n_scenes": len(metas),
        "seed": seed,
        "width": WIDTH,
        "height": HEIGHT,
        "counts": {k: dict(v) for k, v in counts.items()},
        "scenes": [
            {
                "id": f"scene_{i:04d}",
                "shape": m["shape"],
                "color": m["color"],
                "size": m["size"],
                "material": m["material"],
                "surface": m["surface"],
                "gravity_condition": m["gravity_condition"],
                "multi_object": m["multi_object"],
                "n_frames": m["n_frames"],
                "governing_law": m["governing_law"],
            }
            for i, m in enumerate(metas)
        ],
    }
    (out / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=True), encoding="utf-8"
    )

    lines = [
        "# Synthetic physics dataset SUMMARY",
        "",
        f"- n_scenes: {len(metas)}",
        f"- seed: {seed}",
        f"- frame size: {WIDTH}x{HEIGHT}",
        "",
        "## Counts by axis",
        "",
    ]
    for axis, ctr in counts.items():
        lines.append(f"### {axis}")
        for k, v in sorted(ctr.items(), key=lambda kv: str(kv[0])):
            lines.append(f"- {k}: {v}")
        lines.append("")
    (out / "SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")


def generate_dataset(
    *,
    n_scenes: int = 220,
    out_dir: str | Path = "data/scenes",
    seed: int = 42,
    frames_per_scene: int = 30,
) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    configs = sample_configs(n_scenes, rng)
    metas: list[dict[str, Any]] = []

    for i, cfg in enumerate(configs):
        scene_seed = seed * 100000 + i
        scene_rng = random.Random(scene_seed)
        # slight per-scene frame jitter around default
        n_fr = frames_per_scene
        if frames_per_scene >= 24:
            n_fr = int(scene_rng.randint(max(16, frames_per_scene - 6), frames_per_scene + 6))

        frames, meta = simulate_scene(
            scene_rng,
            shape=cfg["shape"],
            color=cfg["color"],
            size=cfg["size"],
            material=cfg["material"],
            surface=cfg["surface"],
            condition=cfg["condition"],
            n_frames=n_fr,
            multi=bool(cfg["multi"]),
            scene_seed=scene_seed,
        )
        scene_dir = out / f"scene_{i:04d}"
        scene_dir.mkdir(parents=True, exist_ok=True)
        for fi, img in enumerate(frames):
            img.save(scene_dir / f"frame_{fi:04d}.png")
        (scene_dir / "meta.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=True), encoding="utf-8"
        )
        metas.append(meta)
        if (i + 1) % 50 == 0 or i + 1 == n_scenes:
            print(f"  wrote {i + 1}/{n_scenes} scenes -> {scene_dir}")

    write_summary(out, metas, seed)
    print(f"Done: {n_scenes} scenes under {out.resolve()}")
    print(f"  SUMMARY.json + SUMMARY.md written")
    return out


def main() -> None:
    p = argparse.ArgumentParser(
        description="Generate varied synthetic visual physics scenes (PNG + meta.json)."
    )
    p.add_argument("--n-scenes", type=int, default=220, help="Number of scenes (default 220)")
    p.add_argument(
        "--out",
        type=str,
        default="data/scenes",
        help="Output directory (default data/scenes)",
    )
    p.add_argument("--seed", type=int, default=42, help="RNG seed for determinism")
    p.add_argument(
        "--frames-per-scene",
        type=int,
        default=30,
        help="Base frames per scene (~24-36; slight jitter applied)",
    )
    args = p.parse_args()
    generate_dataset(
        n_scenes=args.n_scenes,
        out_dir=args.out,
        seed=args.seed,
        frames_per_scene=args.frames_per_scene,
    )


if __name__ == "__main__":
    main()
