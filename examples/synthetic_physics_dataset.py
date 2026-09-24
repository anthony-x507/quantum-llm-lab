#!/usr/bin/env python3
"""Generate 200+ varied scenes: falls/figures + entanglement + superposition.

Self-contained: Pillow + numpy only. No display, no paid APIs.
Deterministic with --seed.
Domains mix in one tree under data/scenes/ for joint LoRA training.

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

SHAPES = ("square", "circle", "triangle", "rectangle", "irregular_polygon", "pentagon", "hexagon", "star", "ring")
DOMAINS = ("fall", "entanglement", "superposition")
# mix: ~55% fall / ~22% entanglement / ~23% superposition (see sample_configs)
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


def _regular_polygon_pts(cx: float, cy: float, r: float, n: int, rot: float = -math.pi / 2) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    for i in range(n):
        ang = rot + 2 * math.pi * i / n
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


def _star_pts(cx: float, cy: float, r: float, n: int = 5) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    for i in range(n * 2):
        ang = -math.pi / 2 + math.pi * i / n
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    return pts


def _draw_body(draw: ImageDraw.ImageDraw, body: Body, *, alpha_hint: int | None = None) -> None:
    rgb = COLOR_RGB[body.color]
    if alpha_hint is not None:
        # Pillow RGB ImageDraw has no alpha; fade by blending toward bg
        bg = (28, 28, 36)
        t = max(0.0, min(1.0, alpha_hint / 255.0))
        rgb = tuple(int(bg[i] * (1 - t) + rgb[i] * t) for i in range(3))
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
    elif body.shape == "pentagon":
        draw.polygon(_regular_polygon_pts(cx, cy, r, 5), fill=rgb)
    elif body.shape == "hexagon":
        draw.polygon(_regular_polygon_pts(cx, cy, r, 6, rot=0.0), fill=rgb)
    elif body.shape == "star":
        draw.polygon(_star_pts(cx, cy, r, 5), fill=rgb)
    elif body.shape == "ring":
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=rgb, width=max(2, int(r * 0.35)))
        inner = r * 0.45
        draw.ellipse([cx - inner, cy - inner, cx + inner, cy + inner], fill=(28, 28, 36))
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



def simulate_entanglement_scene(
    rng: random.Random,
    *,
    n_frames: int,
    scene_seed: int,
    entangled: bool,
    ent_template: str | None = None,
    bell_state: str | None = None,
    pattern: str | None = None,
) -> tuple[list[Image.Image], dict[str, Any]]:
    """Visual metaphor: two particles; entrelazado = correlación espejo + enlace; separable = independientes.
    pattern ∈ mirror|phase_link|shared_orbit|anti_xy diversifies motion/link cues for gate templates.
    """
    shapes = [rng.choice(SHAPES), rng.choice(SHAPES)]
    colors = [rng.choice(COLORS), rng.choice([c for c in COLORS if c != shapes[0]] or list(COLORS))]
    # ensure distinct colors
    c2 = rng.choice([c for c in COLORS if c != colors[0]] or list(COLORS))
    colors[1] = c2
    sizes = [rng.choice(SIZES), rng.choice(SIZES)]
    materials = [rng.choice(MATERIALS), rng.choice(MATERIALS)]

    a = _make_body(
        rng, shape=shapes[0], color=colors[0], size=sizes[0], material=materials[0],
        x=WIDTH * 0.28, y=HEIGHT * 0.35, vx=0, vy=0,
    )
    b = _make_body(
        rng, shape=shapes[1], color=colors[1], size=sizes[1], material=materials[1],
        x=WIDTH * 0.72, y=HEIGHT * 0.35, vx=0, vy=0,
    )
    phase0 = rng.uniform(0, 2 * math.pi)
    pattern = pattern or rng.choice(["mirror", "phase_link", "shared_orbit", "anti_xy"])
    frames: list[Image.Image] = []
    trajectory: list[dict[str, Any]] = []
    for fi in range(n_frames):
        t = fi / max(1, n_frames - 1)
        ang = phase0 + t * 2 * math.pi
        # shared oscillation if entangled; independent if separable — pattern diversifies cues
        if entangled:
            if pattern == "phase_link":
                a.x = WIDTH * 0.30 + 8 * math.sin(ang)
                a.y = HEIGHT * 0.40 + 12 * math.cos(ang)
                b.x = WIDTH * 0.70 + 8 * math.sin(ang + math.pi / 2)
                b.y = HEIGHT * 0.40 + 12 * math.cos(ang + math.pi / 2)
            elif pattern == "shared_orbit":
                r = 28
                a.x = WIDTH * 0.5 + r * math.cos(ang)
                a.y = HEIGHT * 0.42 + r * math.sin(ang)
                b.x = WIDTH * 0.5 + r * math.cos(ang + math.pi)
                b.y = HEIGHT * 0.42 + r * math.sin(ang + math.pi)
            else:  # mirror / anti_xy
                a.x = WIDTH * 0.28 + 10 * math.sin(ang)
                a.y = HEIGHT * 0.35 + 8 * math.cos(ang)
                b.x = WIDTH * 0.72 - 10 * math.sin(ang)
                b.y = HEIGHT * 0.35 - 8 * math.cos(ang)
            link = True
        else:
            a.x = WIDTH * 0.28 + 12 * math.sin(ang)
            a.y = HEIGHT * 0.35 + 10 * math.cos(ang * 1.3)
            b.x = WIDTH * 0.72 + 14 * math.sin(ang * 0.7 + 1.1)
            b.y = HEIGHT * 0.55 + 9 * math.cos(ang * 0.9)
            link = False

        img = Image.new("RGB", (WIDTH, HEIGHT), (18, 22, 40))
        draw = ImageDraw.Draw(img)
        # faint axes
        draw.line([(8, HEIGHT // 2), (WIDTH - 8, HEIGHT // 2)], fill=(40, 45, 70), width=1)
        if link:
            link_col = {
                "phase_link": (160, 220, 255),
                "shared_orbit": (255, 180, 220),
                "anti_xy": (180, 160, 255),
                "mirror": (200, 170, 255),
            }.get(pattern, (180, 160, 255))
            draw.line([(a.x, a.y), (b.x, b.y)], fill=link_col, width=2)
            # Bell-ish glyph in center
            mx, my = (a.x + b.x) / 2, (a.y + b.y) / 2
            draw.ellipse([mx - 4, my - 4, mx + 4, my + 4], fill=(200, 180, 255))
            if pattern == "phase_link":
                draw.arc([mx - 12, my - 12, mx + 12, my + 12], 0, 270, fill=link_col, width=2)
        _draw_body(draw, a)
        _draw_body(draw, b)
        # label strip (visual cue, not text-heavy)
        tag = (200, 120, 255) if entangled else (120, 140, 120)
        draw.rectangle([4, 4, 20, 14], fill=tag)
        frames.append(img)
        trajectory.append({
            "frame": fi,
            "objects": [
                {"id": 0, "x": round(a.x, 3), "y": round(a.y, 3)},
                {"id": 1, "x": round(b.x, 3), "y": round(b.y, 3)},
            ],
            "linked": link,
        })

    if entangled:
        bell_state = bell_state or rng.choice(["Phi+", "Phi-", "Psi+", "Psi-"])
    else:
        bell_state = None
    # Default template if caller did not pin one
    if not ent_template:
        if entangled:
            bell_map = {"Phi+": "bell_hcx", "Phi-": "bell_xhcx", "Psi+": "bell_hxcx", "Psi-": "bell_xxhcx"}
            ent_template = bell_map.get(str(bell_state), "bell_hcx")
        else:
            ent_template = ["sep_hh", "sep_xx", "sep_hy", "sep_ryry", "sep_hx", "sep_zz", "sep_yh"][
                scene_seed % 7
            ]
    corr = {
        "mirror": "anti_correlated_xy",
        "anti_xy": "anti_correlated_xy",
        "phase_link": "phase_correlated",
        "shared_orbit": "orbit_anticorrelated",
    }.get(pattern, "anti_correlated_xy") if entangled else "independent"
    meta: dict[str, Any] = {
        "domain": "entanglement",
        "scene_seed": scene_seed,
        "seed": scene_seed,
        "entangled": entangled,
        "separable": not entangled,
        "bell_state": bell_state,
        "ent_template": ent_template,
        "pattern": pattern,
        "correlation": corr,
        "shape": a.shape,
        "color": a.color,
        "objects": [a.as_meta(), b.as_meta()],
        "n_frames": n_frames,
        "width": WIDTH,
        "height": HEIGHT,
        "trajectory": trajectory,
        "multi_object": True,
        "surface": "quantum_canvas",
        "gravity_condition": "n/a_entanglement",
        "governing_law": (
            f"Toy Bell pair visual ({bell_state}/{pattern}/{ent_template}); non-local correlation metaphor"
            if entangled
            else f"Two separable particles ({ent_template}); independent trajectories (product state)"
        ),
        "label": "entangled" if entangled else "separable",
        "train_target_kind": "bell_circuit" if entangled else "product_circuit",
    }
    return frames, meta


def simulate_superposition_scene(
    rng: random.Random,
    *,
    n_frames: int,
    scene_seed: int,
    collapsed: bool,
) -> tuple[list[Image.Image], dict[str, Any]]:
    """Visual metaphor: ghost dual hypotheses until measurement collapses to one."""
    shape_a = rng.choice(SHAPES)
    shape_b = rng.choice([s for s in SHAPES if s != shape_a] or list(SHAPES))
    color_a = rng.choice(COLORS)
    color_b = rng.choice([c for c in COLORS if c != color_a] or list(COLORS))
    size = rng.choice(SIZES)
    mat = rng.choice(MATERIALS)
    hyp_a = _make_body(rng, shape=shape_a, color=color_a, size=size, material=mat, x=WIDTH * 0.35, y=HEIGHT * 0.4)
    hyp_b = _make_body(rng, shape=shape_b, color=color_b, size=size, material=mat, x=WIDTH * 0.65, y=HEIGHT * 0.4)
    measure_frame = int(n_frames * rng.uniform(0.55, 0.85)) if collapsed else None
    chosen = rng.choice(["A", "B"]) if collapsed else None

    frames: list[Image.Image] = []
    trajectory: list[dict[str, Any]] = []
    for fi in range(n_frames):
        t = fi / max(1, n_frames - 1)
        wobble = 6 * math.sin(t * 4 * math.pi + scene_seed)
        hyp_a.x = WIDTH * 0.35 + wobble
        hyp_b.x = WIDTH * 0.65 - wobble
        hyp_a.y = HEIGHT * 0.4 + 4 * math.cos(t * 3 * math.pi)
        hyp_b.y = HEIGHT * 0.4 - 4 * math.cos(t * 3 * math.pi)

        img = Image.new("RGB", (WIDTH, HEIGHT), (22, 20, 32))
        draw = ImageDraw.Draw(img)
        draw.rectangle([WIDTH // 2 - 1, 10, WIDTH // 2 + 1, HEIGHT - 10], fill=(50, 50, 70))

        show_both = (not collapsed) or (measure_frame is not None and fi < measure_frame)
        if show_both:
            _draw_body(draw, hyp_a, alpha_hint=140)
            _draw_body(draw, hyp_b, alpha_hint=140)
            # superposition brace
            draw.arc([20, 20, WIDTH - 20, 50], 200, 340, fill=(160, 200, 255), width=2)
            tag = (100, 180, 255)
        else:
            body = hyp_a if chosen == "A" else hyp_b
            body.x = WIDTH * 0.5
            body.y = HEIGHT * 0.45
            _draw_body(draw, body, alpha_hint=255)
            # collapse flash
            draw.ellipse([WIDTH // 2 - 18, 16, WIDTH // 2 + 18, 40], outline=(255, 220, 120), width=2)
            tag = (255, 200, 80)
        draw.rectangle([4, 4, 20, 14], fill=tag)
        frames.append(img)
        trajectory.append({
            "frame": fi,
            "superposed": show_both,
            "collapsed_to": None if show_both else chosen,
        })

    meta: dict[str, Any] = {
        "domain": "superposition",
        "scene_seed": scene_seed,
        "seed": scene_seed,
        "superposed": not collapsed,
        "collapsed": collapsed,
        "hypotheses": [
            {"id": "A", **hyp_a.as_meta()},
            {"id": "B", **hyp_b.as_meta()},
        ],
        "measure_frame": measure_frame,
        "collapsed_to": chosen if collapsed else None,
        "shape": shape_a,
        "color": color_a,
        "objects": [hyp_a.as_meta(), hyp_b.as_meta()],
        "n_frames": n_frames,
        "width": WIDTH,
        "height": HEIGHT,
        "trajectory": trajectory,
        "multi_object": True,
        "surface": "quantum_canvas",
        "gravity_condition": "n/a_superposition",
        "governing_law": (
            "Premature collapse: measurement already chose one hypothesis"
            if collapsed
            else "Hold dual hypotheses A|B until measurement; do not collapse early"
        ),
        "label": "collapsed" if collapsed else "superposed",
        "train_target_kind": "collapse_circuit" if collapsed else "superposition_circuit",
    }
    return frames, meta


def sample_configs(n_scenes: int, rng: random.Random) -> list[dict[str, Any]]:
    """Sample varied configs across fall / entanglement / superposition domains."""
    configs: list[dict[str, Any]] = []

    # --- Fall / classical visual physics (expanded shapes) ---
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
                "domain": "fall",
                "shape": rng.choice(SHAPES),
                "color": rng.choice(COLORS),
                "size": rng.choice(SIZES),
                "material": rng.choice(MATERIALS),
                "surface": rng.choice(SURFACES),
                "condition": rng.choice(CONDITIONS),
                "multi": rng.random() < 0.32,
            }
            key = "condition" if axis_name == "condition" else axis_name
            cfg[key] = v
            configs.append(cfg)

    # Guaranteed multi + wind combos (e.g. red square + blue circle with wind)
    for _ in range(min(24, n_scenes)):
        configs.append(
            {
                "domain": "fall",
                "shape": rng.choice(SHAPES),
                "color": rng.choice(COLORS),
                "size": rng.choice(SIZES),
                "material": rng.choice(MATERIALS),
                "surface": rng.choice(SURFACES),
                "condition": "lateral_wind",
                "multi": True,
            }
        )

    # --- Entanglement subset (~38% target; was under-represented vs fall) ---
    ENT_TEMPLATES_BELL = [
        "bell_hcx", "bell_xhcx", "bell_hxcx", "bell_xxhcx",
        "bell_hcxz", "bell_yhcx", "bell_hcxry",
        "bell_zhcx", "bell_hycx", "bell_ryhcx", "bell_hcx_x",
    ]
    ENT_TEMPLATES_SEP = [
        "sep_hh", "sep_xx", "sep_hy", "sep_ryry", "sep_hx", "sep_zz", "sep_yh",
        "sep_xy", "sep_hz", "sep_yz", "sep_ryx",
    ]
    n_ent = max(12, int(n_scenes * 0.38))
    for i in range(n_ent):
        entangled = i % 3 != 0  # ~2/3 entangled, 1/3 separable contrast
        tpl = (
            ENT_TEMPLATES_BELL[i % len(ENT_TEMPLATES_BELL)]
            if entangled
            else ENT_TEMPLATES_SEP[i % len(ENT_TEMPLATES_SEP)]
        )
        configs.append(
            {
                "domain": "entanglement",
                "entangled": entangled,
                "ent_template": tpl,
                "bell_state": ["Phi+", "Phi-", "Psi+", "Psi-"][i % 4] if entangled else None,
                "pattern": ["mirror", "phase_link", "shared_orbit", "anti_xy"][i % 4],
            }
        )

    # --- Superposition subset (~27%) ---
    n_sup = max(8, int(n_scenes * 0.27))
    for i in range(n_sup):
        configs.append(
            {
                "domain": "superposition",
                "collapsed": i % 4 == 0,  # mostly hold superposition; some collapse demos
            }
        )

    while len(configs) < n_scenes:
        roll = rng.random()
        if roll < 0.35:
            configs.append(
                {
                    "domain": "fall",
                    "shape": rng.choice(SHAPES),
                    "color": rng.choice(COLORS),
                    "size": rng.choice(SIZES),
                    "material": rng.choice(MATERIALS),
                    "surface": rng.choice(SURFACES),
                    "condition": rng.choice(CONDITIONS),
                    "multi": rng.random() < 0.35,
                }
            )
        elif roll < 0.73:
            entangled = rng.random() < 0.7
            tpl = rng.choice(ENT_TEMPLATES_BELL if entangled else ENT_TEMPLATES_SEP)
            configs.append({
                "domain": "entanglement",
                "entangled": entangled,
                "ent_template": tpl,
                "bell_state": rng.choice(["Phi+", "Phi-", "Psi+", "Psi-"]) if entangled else None,
                "pattern": rng.choice(["mirror", "phase_link", "shared_orbit", "anti_xy"]),
            })
        else:
            configs.append({"domain": "superposition", "collapsed": rng.random() < 0.25})

    # Stratified trim: keep domain mix when n_scenes is small
    by_dom: dict[str, list] = {"fall": [], "entanglement": [], "superposition": []}
    for c in configs:
        by_dom.setdefault(c.get("domain", "fall"), []).append(c)
    for v in by_dom.values():
        rng.shuffle(v)
    # target mix ~35 fall / 38 ent / 27 super (ent no longer under vs fall)
    n_fall = max(1, int(round(n_scenes * 0.35)))
    n_ent = max(1, int(round(n_scenes * 0.38)))
    n_sup = max(1, n_scenes - n_fall - n_ent)
    # adjust if pool short
    picked: list = []
    picked.extend(by_dom["fall"][:n_fall])
    picked.extend(by_dom["entanglement"][:n_ent])
    picked.extend(by_dom["superposition"][:n_sup])
    # fill remainder from leftovers
    leftover = (
        by_dom["fall"][n_fall:]
        + by_dom["entanglement"][n_ent:]
        + by_dom["superposition"][n_sup:]
    )
    rng.shuffle(leftover)
    while len(picked) < n_scenes and leftover:
        picked.append(leftover.pop())
    rng.shuffle(picked)
    return picked[:n_scenes]



def write_summary(out: Path, metas: list[dict[str, Any]], seed: int) -> None:
    counts = {
        "shape": Counter(m.get("shape") for m in metas if m.get("shape") is not None),
        "color": Counter(m.get("color") for m in metas if m.get("color") is not None),
        "size": Counter(m.get("size") for m in metas if m.get("size") is not None),
        "material": Counter(m.get("material") for m in metas if m.get("material") is not None),
        "surface": Counter(m.get("surface") for m in metas if m.get("surface") is not None),
        "gravity_condition": Counter(
            m.get("gravity_condition") for m in metas if m.get("gravity_condition") is not None
        ),
        "multi_object": Counter(bool(m.get("multi_object")) for m in metas),
        "domain": Counter(m.get("domain", "fall") for m in metas),
        "label": Counter(str(m.get("label", "fall")) for m in metas),
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
                "shape": m.get("shape"),
                "color": m.get("color"),
                "size": m.get("size"),
                "material": m.get("material"),
                "surface": m.get("surface"),
                "gravity_condition": m.get("gravity_condition"),
                "multi_object": m.get("multi_object"),
                "domain": m.get("domain", "fall"),
                "label": m.get("label"),
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
    start_index: int = 0,
    domain_only: str | None = None,
) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    configs = sample_configs(n_scenes, rng)
    if domain_only:
        # Force all configs to requested domain (enrichment appends).
        forced: list[dict[str, Any]] = []
        for i in range(n_scenes):
            if domain_only == "entanglement":
                entangled = i % 3 != 0
                ENT_B = [
                    "bell_hcx", "bell_xhcx", "bell_hxcx", "bell_xxhcx",
                    "bell_hcxz", "bell_yhcx", "bell_hcxry",
                    "bell_zhcx", "bell_hycx", "bell_ryhcx", "bell_hcx_x",
                ]
                ENT_S = [
                    "sep_hh", "sep_xx", "sep_hy", "sep_ryry", "sep_hx", "sep_zz", "sep_yh",
                    "sep_xy", "sep_hz", "sep_yz", "sep_ryx",
                ]
                forced.append({
                    "domain": "entanglement",
                    "entangled": entangled,
                    "ent_template": (ENT_B if entangled else ENT_S)[i % (len(ENT_B) if entangled else len(ENT_S))],
                    "bell_state": ["Phi+", "Phi-", "Psi+", "Psi-"][i % 4] if entangled else None,
                    "pattern": ["mirror", "phase_link", "shared_orbit", "anti_xy"][i % 4],
                })
            elif domain_only == "superposition":
                forced.append({"domain": "superposition", "collapsed": i % 4 == 0})
            else:
                forced.append({
                    "domain": "fall",
                    "shape": rng.choice(SHAPES),
                    "color": rng.choice(COLORS),
                    "size": rng.choice(SIZES),
                    "material": rng.choice(MATERIALS),
                    "surface": rng.choice(SURFACES),
                    "condition": rng.choice(CONDITIONS),
                    "multi": rng.random() < 0.35,
                })
        configs = forced
    metas: list[dict[str, Any]] = []

    for i, cfg in enumerate(configs):
        idx = start_index + i
        scene_seed = seed * 100000 + idx
        scene_rng = random.Random(scene_seed)
        # slight per-scene frame jitter around default
        n_fr = frames_per_scene
        if frames_per_scene >= 24:
            n_fr = int(scene_rng.randint(max(16, frames_per_scene - 6), frames_per_scene + 6))

        domain = cfg.get("domain", "fall")
        if domain == "entanglement":
            frames, meta = simulate_entanglement_scene(
                scene_rng,
                n_frames=n_fr,
                scene_seed=scene_seed,
                entangled=bool(cfg.get("entangled", True)),
                ent_template=cfg.get("ent_template"),
                bell_state=cfg.get("bell_state"),
                pattern=cfg.get("pattern"),
            )
        elif domain == "superposition":
            frames, meta = simulate_superposition_scene(
                scene_rng,
                n_frames=n_fr,
                scene_seed=scene_seed,
                collapsed=bool(cfg.get("collapsed", False)),
            )
        else:
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
            meta["domain"] = "fall"
            meta["label"] = "fall_multi" if meta.get("multi_object") else "fall"
            meta["train_target_kind"] = "fall_circuit"
        scene_dir = out / f"scene_{idx:04d}"
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
    print(f"Done: {n_scenes} scenes under {out.resolve()} (start_index={start_index})")
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
    p.add_argument(
        "--start-index",
        type=int,
        default=0,
        help="Scene id offset (append enrichment without overwriting scene_0000+)",
    )
    p.add_argument(
        "--domain-only",
        type=str,
        default=None,
        choices=["fall", "entanglement", "superposition"],
        help="Force all generated scenes to one domain (enrichment)",
    )
    args = p.parse_args()
    generate_dataset(
        n_scenes=args.n_scenes,
        out_dir=args.out,
        seed=args.seed,
        frames_per_scene=args.frames_per_scene,
        start_index=args.start_index,
        domain_only=args.domain_only,
    )


if __name__ == "__main__":
    main()
