#!/usr/bin/env python3
"""Generate ≥200 classical visual physics scenes (NOT quantum).

Image → executable Python that simulates classical motion and returns
verifiable numeric predictions (range, max_height, impact_speed).

Domains (balanced):
  1) Sport balls + collisions/impulse: baseball, soccer, golf
  2) Rockets / projectiles: ballistic, angled, drag, elastic/inelastic
  3) Vary mass, restitution, angle, spin, surface

Self-contained: Pillow + numpy only (no display). Deterministic with --seed.

Usage:
  python examples/synthetic_classical_physics.py
  python examples/synthetic_classical_physics.py --n-scenes 220 --out data/classical_scenes --seed 42
  python examples/synthetic_classical_physics.py --n-scenes 4  # smoke
"""

from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 240, 180
G_EARTH = 9.81  # m/s^2 (SI for GT; pixels are visual only)

# Subdomains for balanced sampling
SPORT_SUBS = ("baseball", "soccer", "golf")
PROJECTILE_SUBS = (
    "ballistic",
    "angled_projectile",
    "drag_projectile",
    "elastic_collision",
    "inelastic_collision",
)
ALL_SUBS = SPORT_SUBS + PROJECTILE_SUBS

SURFACES = ("hard_ground", "grass", "dirt", "green_fairway", "ramp", "concrete")
BALL_COLORS = {
    "baseball": (240, 240, 235),
    "soccer": (40, 40, 40),
    "golf": (245, 245, 250),
    "projectile": (220, 80, 60),
    "rocket": (90, 140, 220),
}


@dataclass
class PhysicsParams:
    """Equation parameters (ground truth)."""

    subdomain: str
    mass_kg: float
    v0_m_s: float
    angle_deg: float
    spin_rpm: float
    restitution: float
    drag_coeff: float
    g_m_s2: float
    surface: str
    # collision partner (optional)
    mass2_kg: float = 0.0
    v2_m_s: float = 0.0
    # Magnus / lift scale (dimensionless toy)
    magnus_k: float = 0.0
    # launch height above ground (m)
    y0_m: float = 0.0


@dataclass
class Metrics:
    range_m: float
    max_height_m: float
    impact_speed_m_s: float
    # optional extras
    hang_time_s: float = 0.0
    bounce_height_m: float = 0.0
    post_collision_v1_m_s: float = 0.0
    post_collision_v2_m_s: float = 0.0


def _tol(metrics: Metrics) -> dict[str, float]:
    """Relative/absolute tolerances for eval."""
    return {
        "range_m": max(0.05, 0.03 * abs(metrics.range_m) + 0.02),
        "max_height_m": max(0.03, 0.03 * abs(metrics.max_height_m) + 0.01),
        "impact_speed_m_s": max(0.08, 0.03 * abs(metrics.impact_speed_m_s) + 0.05),
    }


# ---------------------------------------------------------------------------
# Analytic / numerical classical solvers (GT)
# ---------------------------------------------------------------------------

def _projectile_vacuum(v0: float, angle_deg: float, g: float, y0: float = 0.0) -> Metrics:
    th = math.radians(angle_deg)
    vx = v0 * math.cos(th)
    vy = v0 * math.sin(th)
    # time of flight for landing at y=0 from y0
    # 0 = y0 + vy t - 0.5 g t^2
    disc = vy * vy + 2.0 * g * y0
    t_flight = (vy + math.sqrt(max(0.0, disc))) / g if g > 0 else 0.0
    range_m = vx * t_flight
    # max height relative to ground
    t_apex = vy / g if g > 0 else 0.0
    max_h = y0 + vy * t_apex - 0.5 * g * t_apex * t_apex
    if max_h < y0:
        max_h = y0
    # impact speed
    vy_imp = vy - g * t_flight
    impact = math.hypot(vx, vy_imp)
    return Metrics(
        range_m=round(range_m, 6),
        max_height_m=round(max_h, 6),
        impact_speed_m_s=round(impact, 6),
        hang_time_s=round(t_flight, 6),
    )


def _projectile_drag(
    v0: float,
    angle_deg: float,
    g: float,
    drag_c: float,
    mass: float,
    y0: float = 0.0,
    dt: float = 0.001,
) -> Metrics:
    """Linear drag: a = - (c/m) v  (toy). Numerical RK-ish Euler."""
    th = math.radians(angle_deg)
    x, y = 0.0, y0
    vx, vy = v0 * math.cos(th), v0 * math.sin(th)
    max_h = y
    t = 0.0
    k = drag_c / max(mass, 1e-6)
    while y >= 0.0 or t < 1e-9:
        speed = math.hypot(vx, vy)
        ax = -k * vx
        ay = -g - k * vy
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
        t += dt
        if y > max_h:
            max_h = y
        if t > 60.0:
            break
        if y < 0.0 and t > 0.05:
            break
    impact = math.hypot(vx, vy)
    return Metrics(
        range_m=round(max(0.0, x), 6),
        max_height_m=round(max_h, 6),
        impact_speed_m_s=round(impact, 6),
        hang_time_s=round(t, 6),
    )


def _projectile_magnus(
    v0: float,
    angle_deg: float,
    g: float,
    spin_rpm: float,
    magnus_k: float,
    mass: float,
    y0: float = 0.0,
    dt: float = 0.001,
) -> Metrics:
    """Toy Magnus: lateral lift ~ k * ω × v (2D: vertical lift from backspin)."""
    th = math.radians(angle_deg)
    x, y = 0.0, y0
    vx, vy = v0 * math.cos(th), v0 * math.sin(th)
    omega = spin_rpm * 2.0 * math.pi / 60.0  # rad/s
    max_h = y
    t = 0.0
    while True:
        # lift force direction perpendicular to velocity (backspin → upward for +vx)
        speed = math.hypot(vx, vy) + 1e-9
        # F_L / m ≈ magnus_k * omega * speed / mass  in +y for backspin
        a_lift = (magnus_k * omega * speed) / max(mass, 1e-6)
        ax = 0.0
        ay = -g + a_lift
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
        t += dt
        if y > max_h:
            max_h = y
        if t > 60.0:
            break
        if y < 0.0 and t > 0.05:
            break
    impact = math.hypot(vx, vy)
    return Metrics(
        range_m=round(max(0.0, x), 6),
        max_height_m=round(max_h, 6),
        impact_speed_m_s=round(impact, 6),
        hang_time_s=round(t, 6),
    )


def _bounce_after_fall(h: float, e: float, g: float = G_EARTH) -> Metrics:
    """Drop from height h, bounce restitution e → bounce height e^2 h."""
    impact = math.sqrt(2.0 * g * h)
    bounce_h = (e * e) * h
    # treat "range" as 0 for vertical drop; max_height = drop height
    return Metrics(
        range_m=0.0,
        max_height_m=round(h, 6),
        impact_speed_m_s=round(impact, 6),
        bounce_height_m=round(bounce_h, 6),
        hang_time_s=round(math.sqrt(2.0 * h / g), 6),
    )


def _elastic_1d(m1: float, v1: float, m2: float, v2: float) -> Metrics:
    """1D elastic collision velocities."""
    u1 = ((m1 - m2) / (m1 + m2)) * v1 + (2 * m2 / (m1 + m2)) * v2
    u2 = (2 * m1 / (m1 + m2)) * v1 + ((m2 - m1) / (m1 + m2)) * v2
    # map to reportable metrics: "range" unused → use |u1|; impact = relative approach
    approach = abs(v1 - v2)
    return Metrics(
        range_m=round(abs(u1), 6),  # post-v1 magnitude as stand-in range metric
        max_height_m=0.0,
        impact_speed_m_s=round(approach, 6),
        post_collision_v1_m_s=round(u1, 6),
        post_collision_v2_m_s=round(u2, 6),
    )


def _inelastic_1d(m1: float, v1: float, m2: float, v2: float) -> Metrics:
    """Perfectly inelastic: stick together."""
    v = (m1 * v1 + m2 * v2) / (m1 + m2)
    approach = abs(v1 - v2)
    return Metrics(
        range_m=round(abs(v), 6),
        max_height_m=0.0,
        impact_speed_m_s=round(approach, 6),
        post_collision_v1_m_s=round(v, 6),
        post_collision_v2_m_s=round(v, 6),
    )


def compute_metrics(p: PhysicsParams) -> Metrics:
    sub = p.subdomain
    if sub in ("ballistic", "angled_projectile"):
        return _projectile_vacuum(p.v0_m_s, p.angle_deg, p.g_m_s2, p.y0_m)
    if sub == "drag_projectile":
        return _projectile_drag(p.v0_m_s, p.angle_deg, p.g_m_s2, p.drag_coeff, p.mass_kg, p.y0_m)
    if sub == "baseball":
        # bat-ball: treat as projectile with Magnus (spin)
        return _projectile_magnus(
            p.v0_m_s, p.angle_deg, p.g_m_s2, p.spin_rpm, p.magnus_k, p.mass_kg, p.y0_m
        )
    if sub == "golf":
        # backspin lift
        return _projectile_magnus(
            p.v0_m_s, p.angle_deg, p.g_m_s2, abs(p.spin_rpm), p.magnus_k, p.mass_kg, p.y0_m
        )
    if sub == "soccer":
        if p.angle_deg < 5.0 and p.y0_m > 0.1:
            # bounce / drop onto surface
            m = _bounce_after_fall(p.y0_m, p.restitution, p.g_m_s2)
            # slight horizontal range if small vx
            th = math.radians(max(p.angle_deg, 1.0))
            m.range_m = round(p.v0_m_s * math.cos(th) * m.hang_time_s, 6)
            return m
        # curve kick ≈ magnus
        return _projectile_magnus(
            p.v0_m_s, p.angle_deg, p.g_m_s2, p.spin_rpm, p.magnus_k, p.mass_kg, p.y0_m
        )
    if sub == "elastic_collision":
        return _elastic_1d(p.mass_kg, p.v0_m_s, p.mass2_kg, p.v2_m_s)
    if sub == "inelastic_collision":
        return _inelastic_1d(p.mass_kg, p.v0_m_s, p.mass2_kg, p.v2_m_s)
    return _projectile_vacuum(p.v0_m_s, p.angle_deg, p.g_m_s2, p.y0_m)


# ---------------------------------------------------------------------------
# Target Python (gold assistant completion) — MUST print JSON metrics
# ---------------------------------------------------------------------------

def gold_python(p: PhysicsParams, metrics: Metrics) -> str:
    """Executable Python that recomputes metrics from equation params.

    Anti-leak: this string is the ASSISTANT target only — never in user prompt.
    """
    sub = p.subdomain
    lines = [
        "import math",
        f"g = {p.g_m_s2}",
        f"v0 = {p.v0_m_s}",
        f"angle_deg = {p.angle_deg}",
        f"mass = {p.mass_kg}",
        f"y0 = {p.y0_m}",
        f"spin_rpm = {p.spin_rpm}",
        f"restitution = {p.restitution}",
        f"drag_c = {p.drag_coeff}",
        f"magnus_k = {p.magnus_k}",
        f"m2 = {p.mass2_kg}",
        f"v2 = {p.v2_m_s}",
        f"subdomain = {sub!r}",
        "",
    ]
    if sub in ("ballistic", "angled_projectile"):
        lines += [
            "th = math.radians(angle_deg)",
            "vx = v0 * math.cos(th)",
            "vy = v0 * math.sin(th)",
            "disc = vy*vy + 2*g*y0",
            "t = (vy + math.sqrt(max(0.0, disc))) / g",
            "range_m = vx * t",
            "t_apex = vy / g",
            "max_height_m = y0 + vy*t_apex - 0.5*g*t_apex*t_apex",
            "vy_i = vy - g*t",
            "impact_speed_m_s = math.hypot(vx, vy_i)",
        ]
    elif sub == "drag_projectile":
        lines += [
            "th = math.radians(angle_deg)",
            "x, y = 0.0, y0",
            "vx, vy = v0*math.cos(th), v0*math.sin(th)",
            "max_height_m = y",
            "dt = 0.001",
            "k = drag_c / max(mass, 1e-6)",
            "t = 0.0",
            "while True:",
            "    ax = -k * vx",
            "    ay = -g - k * vy",
            "    vx += ax*dt; vy += ay*dt",
            "    x += vx*dt; y += vy*dt",
            "    t += dt",
            "    if y > max_height_m: max_height_m = y",
            "    if t > 60 or (y < 0 and t > 0.05): break",
            "range_m = max(0.0, x)",
            "impact_speed_m_s = math.hypot(vx, vy)",
        ]
    elif sub in ("baseball", "golf") or (sub == "soccer" and not (p.angle_deg < 5.0 and p.y0_m > 0.1)):
        lines += [
            "th = math.radians(angle_deg)",
            "x, y = 0.0, y0",
            "vx, vy = v0*math.cos(th), v0*math.sin(th)",
            "omega = spin_rpm * 2*math.pi / 60.0",
            "max_height_m = y",
            "dt = 0.001",
            "t = 0.0",
            "while True:",
            "    speed = math.hypot(vx, vy) + 1e-9",
            "    a_lift = (magnus_k * omega * speed) / max(mass, 1e-6)",
            "    ax = 0.0",
            "    ay = -g + a_lift",
            "    vx += ax*dt; vy += ay*dt",
            "    x += vx*dt; y += vy*dt",
            "    t += dt",
            "    if y > max_height_m: max_height_m = y",
            "    if t > 60 or (y < 0 and t > 0.05): break",
            "range_m = max(0.0, x)",
            "impact_speed_m_s = math.hypot(vx, vy)",
        ]
    elif sub == "soccer":
        lines += [
            "impact_speed_m_s = math.sqrt(2*g*y0)",
            "bounce_h = (restitution**2) * y0",
            "hang = math.sqrt(2*y0/g)",
            "th = math.radians(max(angle_deg, 1.0))",
            "range_m = v0 * math.cos(th) * hang",
            "max_height_m = y0",
            "impact_speed_m_s = impact_speed_m_s",
        ]
    elif sub == "elastic_collision":
        lines += [
            "u1 = ((mass-m2)/(mass+m2))*v0 + (2*m2/(mass+m2))*v2",
            "u2 = (2*mass/(mass+m2))*v0 + ((m2-mass)/(mass+m2))*v2",
            "range_m = abs(u1)",
            "max_height_m = 0.0",
            "impact_speed_m_s = abs(v0 - v2)",
        ]
    elif sub == "inelastic_collision":
        lines += [
            "v = (mass*v0 + m2*v2) / (mass + m2)",
            "range_m = abs(v)",
            "max_height_m = 0.0",
            "impact_speed_m_s = abs(v0 - v2)",
        ]
    else:
        lines += [
            "th = math.radians(angle_deg)",
            "vx = v0 * math.cos(th); vy = v0 * math.sin(th)",
            "disc = vy*vy + 2*g*y0",
            "t = (vy + math.sqrt(max(0.0, disc))) / g",
            "range_m = vx * t",
            "t_apex = vy / g",
            "max_height_m = y0 + vy*t_apex - 0.5*g*t_apex*t_apex",
            "impact_speed_m_s = math.hypot(vx, vy - g*t)",
        ]
    lines += [
        "",
        "print({'range_m': round(range_m, 6), 'max_height_m': round(max_height_m, 6), "
        "'impact_speed_m_s': round(impact_speed_m_s, 6)})",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Sampling
# ---------------------------------------------------------------------------

def sample_params(rng: random.Random, subdomain: str) -> PhysicsParams:
    surface = rng.choice(SURFACES)
    g = G_EARTH
    if subdomain == "baseball":
        return PhysicsParams(
            subdomain=subdomain,
            mass_kg=round(rng.uniform(0.142, 0.149), 4),
            v0_m_s=round(rng.uniform(30.0, 45.0), 3),
            angle_deg=round(rng.uniform(20.0, 45.0), 2),
            spin_rpm=round(rng.uniform(1200, 2500), 1),
            restitution=round(rng.uniform(0.45, 0.55), 3),
            drag_coeff=0.0,
            g_m_s2=g,
            surface=surface,
            magnus_k=round(rng.uniform(1.5e-5, 4.0e-5), 8),
            y0_m=round(rng.uniform(0.5, 1.2), 3),
        )
    if subdomain == "soccer":
        bounce = rng.random() < 0.45
        if bounce:
            return PhysicsParams(
                subdomain=subdomain,
                mass_kg=round(rng.uniform(0.41, 0.45), 4),
                v0_m_s=round(rng.uniform(0.5, 4.0), 3),
                angle_deg=round(rng.uniform(0.0, 4.0), 2),
                spin_rpm=round(rng.uniform(0, 300), 1),
                restitution=round(rng.uniform(0.55, 0.85), 3),
                drag_coeff=0.0,
                g_m_s2=g,
                surface=rng.choice(("grass", "dirt", "hard_ground")),
                magnus_k=0.0,
                y0_m=round(rng.uniform(0.8, 3.5), 3),
            )
        return PhysicsParams(
            subdomain=subdomain,
            mass_kg=round(rng.uniform(0.41, 0.45), 4),
            v0_m_s=round(rng.uniform(15.0, 32.0), 3),
            angle_deg=round(rng.uniform(12.0, 40.0), 2),
            spin_rpm=round(rng.uniform(200, 800), 1),
            restitution=round(rng.uniform(0.6, 0.8), 3),
            drag_coeff=0.0,
            g_m_s2=g,
            surface="grass",
            magnus_k=round(rng.uniform(2.0e-5, 5.0e-5), 8),
            y0_m=0.11,
        )
    if subdomain == "golf":
        return PhysicsParams(
            subdomain=subdomain,
            mass_kg=0.0459,
            v0_m_s=round(rng.uniform(40.0, 75.0), 3),
            angle_deg=round(rng.uniform(8.0, 18.0), 2),
            spin_rpm=round(rng.uniform(2000, 4000), 1),  # backspin
            restitution=round(rng.uniform(0.7, 0.85), 3),
            drag_coeff=0.0,
            g_m_s2=g,
            surface="green_fairway",
            magnus_k=round(rng.uniform(2.5e-5, 6.0e-5), 8),
            y0_m=0.02,
        )
    if subdomain == "ballistic":
        return PhysicsParams(
            subdomain=subdomain,
            mass_kg=round(rng.uniform(0.5, 5.0), 3),
            v0_m_s=round(rng.uniform(20.0, 80.0), 3),
            angle_deg=45.0,  # classic max-range angle vacuum
            spin_rpm=0.0,
            restitution=0.0,
            drag_coeff=0.0,
            g_m_s2=g,
            surface=surface,
            y0_m=0.0,
        )
    if subdomain == "angled_projectile":
        return PhysicsParams(
            subdomain=subdomain,
            mass_kg=round(rng.uniform(0.2, 3.0), 3),
            v0_m_s=round(rng.uniform(10.0, 50.0), 3),
            angle_deg=round(rng.uniform(15.0, 70.0), 2),
            spin_rpm=0.0,
            restitution=0.0,
            drag_coeff=0.0,
            g_m_s2=g,
            surface=surface,
            y0_m=round(rng.uniform(0.0, 5.0), 3),
        )
    if subdomain == "drag_projectile":
        return PhysicsParams(
            subdomain=subdomain,
            mass_kg=round(rng.uniform(0.3, 2.0), 3),
            v0_m_s=round(rng.uniform(15.0, 40.0), 3),
            angle_deg=round(rng.uniform(25.0, 55.0), 2),
            spin_rpm=0.0,
            restitution=0.0,
            drag_coeff=round(rng.uniform(0.05, 0.35), 4),
            g_m_s2=g,
            surface=surface,
            y0_m=0.0,
        )
    if subdomain == "elastic_collision":
        m1 = round(rng.uniform(0.5, 3.0), 3)
        m2 = round(rng.uniform(0.5, 3.0), 3)
        return PhysicsParams(
            subdomain=subdomain,
            mass_kg=m1,
            v0_m_s=round(rng.uniform(2.0, 12.0), 3),
            angle_deg=0.0,
            spin_rpm=0.0,
            restitution=1.0,
            drag_coeff=0.0,
            g_m_s2=g,
            surface="concrete",
            mass2_kg=m2,
            v2_m_s=round(rng.uniform(-4.0, 4.0), 3),
        )
    # inelastic
    m1 = round(rng.uniform(0.5, 4.0), 3)
    m2 = round(rng.uniform(0.5, 4.0), 3)
    return PhysicsParams(
        subdomain=subdomain,
        mass_kg=m1,
        v0_m_s=round(rng.uniform(2.0, 15.0), 3),
        angle_deg=0.0,
        spin_rpm=0.0,
        restitution=0.0,
        drag_coeff=0.0,
        g_m_s2=g,
        surface="concrete",
        mass2_kg=m2,
        v2_m_s=round(rng.uniform(-3.0, 3.0), 3),
    )


def balanced_subdomains(n: int, rng: random.Random) -> list[str]:
    """Round-robin across ALL_SUBS then shuffle lightly within blocks."""
    k = len(ALL_SUBS)
    base = n // k
    rem = n % k
    out: list[str] = []
    for i, s in enumerate(ALL_SUBS):
        out.extend([s] * (base + (1 if i < rem else 0)))
    rng.shuffle(out)
    return out


# ---------------------------------------------------------------------------
# Rendering (PIL)
# ---------------------------------------------------------------------------

def _surface_color(surface: str) -> tuple[int, int, int]:
    return {
        "hard_ground": (110, 100, 90),
        "grass": (60, 130, 70),
        "dirt": (140, 110, 70),
        "green_fairway": (50, 140, 80),
        "ramp": (120, 100, 80),
        "concrete": (130, 130, 135),
    }.get(surface, (100, 100, 100))


def _traj_points_px(p: PhysicsParams, metrics: Metrics, n: int = 40) -> list[tuple[int, int]]:
    """Map analytic/numeric trajectory to image coords for drawing."""
    margin = 20
    usable_w = WIDTH - 2 * margin
    usable_h = HEIGHT - 40 - margin
    # collision scenes: draw two balls on a line
    if p.subdomain in ("elastic_collision", "inelastic_collision"):
        y = HEIGHT - 50
        return [(margin + 30, y), (WIDTH // 2, y), (WIDTH - margin - 30, y)]

    # sample vacuum-like path for viz (even if GT used magnus/drag)
    th = math.radians(max(p.angle_deg, 1.0))
    v0 = max(p.v0_m_s, 1.0)
    g = p.g_m_s2
    # use metrics.range / max_height for scale
    R = max(metrics.range_m, 0.5)
    H = max(metrics.max_height_m, 0.2)
    pts: list[tuple[int, int]] = []
    t_flight = metrics.hang_time_s if metrics.hang_time_s > 0 else (2 * v0 * math.sin(th) / g)
    for i in range(n):
        t = t_flight * i / max(n - 1, 1)
        x_m = (v0 * math.cos(th)) * t
        y_m = p.y0_m + (v0 * math.sin(th)) * t - 0.5 * g * t * t
        if y_m < 0 and i > 0:
            break
        px = margin + int(usable_w * (x_m / R))
        py = (HEIGHT - 30) - int(usable_h * (y_m / H))
        pts.append((max(0, min(WIDTH - 1, px)), max(0, min(HEIGHT - 1, py))))
    return pts or [(margin, HEIGHT - 30)]


def render_scene(p: PhysicsParams, metrics: Metrics, scene_id: str) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), (25, 30, 45))
    draw = ImageDraw.Draw(img)
    # sky gradient-ish bands
    for y in range(HEIGHT - 30):
        c = 25 + int(20 * y / max(HEIGHT, 1))
        draw.line([(0, y), (WIDTH, y)], fill=(c, c + 5, c + 20))
    # ground
    sc = _surface_color(p.surface)
    draw.rectangle([0, HEIGHT - 28, WIDTH, HEIGHT], fill=sc)
    # label strip (NO gold numbers — qualitative only)
    label = f"{p.subdomain} | {p.surface}"
    draw.text((6, 4), label, fill=(220, 220, 230))
    draw.text((6, 16), "classical motion (SI)", fill=(160, 170, 190))

    pts = _traj_points_px(p, metrics)
    if len(pts) >= 2:
        draw.line(pts, fill=(255, 200, 80), width=2)
    # ball / bodies
    if p.subdomain in ("elastic_collision", "inelastic_collision"):
        y = HEIGHT - 50
        r1 = max(6, int(8 * math.sqrt(p.mass_kg)))
        r2 = max(6, int(8 * math.sqrt(p.mass2_kg)))
        draw.ellipse([40 - r1, y - r1, 40 + r1, y + r1], fill=(220, 80, 60), outline=(255, 255, 255))
        draw.ellipse(
            [WIDTH - 40 - r2, y - r2, WIDTH - 40 + r2, y + r2],
            fill=(80, 140, 220),
            outline=(255, 255, 255),
        )
        # velocity arrows (direction only, no numbers)
        draw.line([(40, y - r1 - 8), (40 + 25, y - r1 - 8)], fill=(255, 180, 180), width=2)
        if p.v2_m_s != 0:
            dx = -20 if p.v2_m_s < 0 else 20
            draw.line(
                [(WIDTH - 40, y - r2 - 8), (WIDTH - 40 + dx, y - r2 - 8)],
                fill=(180, 200, 255),
                width=2,
            )
        kind = "elastic" if p.subdomain == "elastic_collision" else "inelastic"
        draw.text((WIDTH // 2 - 30, HEIGHT - 50), kind, fill=(200, 200, 210))
    else:
        # launch ball at first point
        cx, cy = pts[0]
        color = BALL_COLORS.get(
            p.subdomain if p.subdomain in BALL_COLORS else "projectile",
            BALL_COLORS["projectile"],
        )
        r = 7
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color, outline=(255, 255, 255))
        # spin mark
        if p.spin_rpm > 50:
            draw.arc([cx - r, cy - r, cx + r, cy + r], 0, 270, fill=(255, 100, 100))
        # angle wedge
        th = math.radians(p.angle_deg)
        ax = cx + int(28 * math.cos(th))
        ay = cy - int(28 * math.sin(th))
        draw.line([(cx, cy), (ax, ay)], fill=(100, 255, 180), width=2)
        # landing marker
        if len(pts) > 1:
            lx, ly = pts[-1]
            draw.line([(lx, HEIGHT - 28), (lx, HEIGHT - 18)], fill=(255, 255, 100), width=2)

    draw.text((6, HEIGHT - 14), scene_id, fill=(180, 180, 190))
    return img


# ---------------------------------------------------------------------------
# Scene write
# ---------------------------------------------------------------------------

def build_meta(
    scene_id: str,
    seed: int,
    p: PhysicsParams,
    metrics: Metrics,
    py_src: str,
) -> dict[str, Any]:
    tol = _tol(metrics)
    return {
        "schema": "classical_physics_v1",
        "domain": "classical",
        "subdomain": p.subdomain,
        "scene_id": scene_id,
        "scene_seed": seed,
        "lane": "classical_visual_physics",
        "width": WIDTH,
        "height": HEIGHT,
        "equations": {
            "family": p.subdomain,
            "g_m_s2": p.g_m_s2,
            "notes": (
                "Vacuum projectile / Magnus / linear-drag / 1D collision "
                "toy models; SI units."
            ),
        },
        "params": asdict(p),
        "expected_metrics": asdict(metrics),
        "tolerance": tol,
        "surface": p.surface,
        "sport_or_mode": p.subdomain,
        # qualitative cues OK for train summary (NOT gold metrics)
        "visual_cues": {
            "has_spin": p.spin_rpm > 50,
            "has_drag": p.drag_coeff > 0,
            "is_collision": p.subdomain.endswith("collision"),
            "surface": p.surface,
            "angle_bin": (
                "steep" if p.angle_deg > 50 else ("shallow" if p.angle_deg < 20 else "mid")
            ),
        },
        "gold_python": py_src,
        "train_target_kind": "executable_python_metrics",
    }


def generate_dataset(out: Path, n_scenes: int, seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    out.mkdir(parents=True, exist_ok=True)
    subs = balanced_subdomains(n_scenes, rng)
    counts: Counter[str] = Counter()
    index: list[dict[str, Any]] = []

    for i, sub in enumerate(subs):
        scene_id = f"cscene_{i:04d}"
        scene_dir = out / scene_id
        scene_dir.mkdir(parents=True, exist_ok=True)
        scene_seed = seed * 100000 + i
        local = random.Random(scene_seed)
        p = sample_params(local, sub)
        metrics = compute_metrics(p)
        py_src = gold_python(p, metrics)
        # verify gold python executes and matches
        ok_exec = _verify_python(py_src, metrics, _tol(metrics))
        meta = build_meta(scene_id, scene_seed, p, metrics, py_src)
        meta["gold_python_verified"] = ok_exec
        img = render_scene(p, metrics, scene_id)
        img.save(scene_dir / "frame_0000.png")
        # also single preview alias
        img.save(scene_dir / "preview.png")
        (scene_dir / "meta.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        counts[sub] += 1
        index.append(
            {
                "scene_id": scene_id,
                "subdomain": sub,
                "verified": ok_exec,
                "range_m": metrics.range_m,
                "max_height_m": metrics.max_height_m,
                "impact_speed_m_s": metrics.impact_speed_m_s,
            }
        )

    summary = {
        "n_scenes": n_scenes,
        "seed": seed,
        "frame_size": [WIDTH, HEIGHT],
        "lane": "classical_visual_physics",
        "counts_by_subdomain": dict(sorted(counts.items())),
        "verified_ok": sum(1 for x in index if x["verified"]),
        "domains": {
            "sport_balls": sum(counts[s] for s in SPORT_SUBS),
            "rockets_projectiles": sum(counts[s] for s in PROJECTILE_SUBS),
        },
    }
    (out / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    (out / "INDEX.json").write_text(
        json.dumps(index, indent=2) + "\n", encoding="utf-8"
    )
    _write_summary_md(out, summary)
    _write_classical_set_md(out, summary, index)
    return summary


def _verify_python(src: str, metrics: Metrics, tol: dict[str, float]) -> bool:
    ns: dict[str, Any] = {}
    try:
        # capture print
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            exec(compile(src, "<gold>", "exec"), ns, ns)
        text = buf.getvalue().strip()
        # last line should be dict repr
        pred = eval(text.splitlines()[-1], {"__builtins__": {}}, {})
        for k in ("range_m", "max_height_m", "impact_speed_m_s"):
            gold = getattr(metrics, k)
            if abs(float(pred[k]) - float(gold)) > tol[k] + 1e-4:
                return False
        return True
    except Exception:
        return False


def _write_summary_md(out: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Classical visual physics dataset SUMMARY",
        "",
        f"- n_scenes: {summary['n_scenes']}",
        f"- seed: {summary['seed']}",
        f"- frame size: {summary['frame_size'][0]}x{summary['frame_size'][1]}",
        f"- lane: {summary['lane']} (NOT quantum)",
        f"- gold_python verified: {summary['verified_ok']}/{summary['n_scenes']}",
        "",
        "## Domain totals",
        f"- sport_balls (baseball/soccer/golf): {summary['domains']['sport_balls']}",
        f"- rockets_projectiles: {summary['domains']['rockets_projectiles']}",
        "",
        "## Counts by subdomain",
    ]
    for k, v in summary["counts_by_subdomain"].items():
        lines.append(f"- {k}: {v}")
    lines += [
        "",
        "## Ground-truth metrics",
        "Each `meta.json` has `params`, `expected_metrics` "
        "(`range_m`, `max_height_m`, `impact_speed_m_s`), and `tolerance`.",
        "Assistant target = executable Python (`gold_python`) that prints those metrics.",
        "",
        "## Anti-leak",
        "User prompts must NOT include gold numeric metrics; only qualitative visual cues.",
        "",
        "## READ-ONLY note",
        "`data/lora_adapter/` (quantum) is never a write target for this lane.",
        "Classical adapters go to `data/lora_adapter_classical/`.",
        "",
    ]
    (out / "SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")


def _write_classical_set_md(
    out: Path, summary: dict[str, Any], index: list[dict[str, Any]]
) -> None:
    lines = [
        "# CLASSICAL_SET",
        "",
        "Balanced synthetic classical motion scenes for image→Python→numeric eval.",
        "",
        f"N = **{summary['n_scenes']}** (seed={summary['seed']}).",
        "",
        "## Subdomains",
    ]
    for k, v in summary["counts_by_subdomain"].items():
        lines.append(f"- `{k}`: {v}")
    lines += [
        "",
        "## Eval protocol",
        "1. Model sees PNG + anti-leak user prompt (no gold numbers).",
        "2. Model emits executable Python.",
        "3. Runner execs Python; parses printed `{range_m, max_height_m, impact_speed_m_s}`.",
        "4. Pass if all three within `meta.tolerance`.",
        "",
        "## Sample scenes (first 8)",
    ]
    for row in index[:8]:
        lines.append(
            f"- `{row['scene_id']}` ({row['subdomain']}): "
            f"R={row['range_m']:.3f} H={row['max_height_m']:.3f} "
            f"V={row['impact_speed_m_s']:.3f} verified={row['verified']}"
        )
    lines.append("")
    (out / "CLASSICAL_SET.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate classical visual physics dataset")
    ap.add_argument("--n-scenes", type=int, default=220)
    ap.add_argument("--out", type=Path, default=Path("data/classical_scenes"))
    ap.add_argument("--seed", type=int, default=240924)
    args = ap.parse_args()
    summary = generate_dataset(args.out, args.n_scenes, args.seed)
    print(json.dumps(summary, indent=2))
    print(f"Wrote {args.out}/SUMMARY.md + CLASSICAL_SET.md")
    return 0 if summary["verified_ok"] == summary["n_scenes"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
