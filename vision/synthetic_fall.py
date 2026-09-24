"""Genera frames de una pelota que cae con gravedad y rebotes (sin video real)."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class PhysicsTrace:
    """Traza conocida del simulador clásico (para --demo y para validar al VLM)."""

    object: str
    g: float
    dt: float
    n_frames: int
    positions_y: list[float]  # píxeles, origen arriba
    velocities_y: list[float]
    bounce_frames: list[int]
    energy_loss_per_bounce: float
    note: str

    def to_structured(self) -> dict[str, Any]:
        ys = np.asarray(self.positions_y, dtype=float)
        vs = np.asarray(self.velocities_y, dtype=float)
        # Aceleración media en fase de caída libre (antes del primer rebote)
        first_bounce = self.bounce_frames[0] if self.bounce_frames else len(ys) - 1
        seg = slice(1, max(2, first_bounce))
        if first_bounce > 2:
            # y aumenta hacia abajo en pantalla → a ≈ +g en px/s^2 (escala)
            acc = float(np.mean(np.diff(vs[seg]) / self.dt))
        else:
            acc = float(self.g)

        return {
            "objeto": self.object,
            "trayectoria": "caída vertical con rebotes (parabólica por tramos)",
            "aceleracion_aprox_px_s2": round(acc, 2),
            "gravedad_simulada_px_s2": self.g,
            "rebotes": [
                {"frame": f, "perdida_energia_frac": self.energy_loss_per_bounce}
                for f in self.bounce_frames
            ],
            "perdida_energia_por_rebote": self.energy_loss_per_bounce,
            "n_frames": self.n_frames,
            "y_px_min": float(ys.min()),
            "y_px_max": float(ys.max()),
            "nota": self.note,
        }


def synthesize_physics_trace(
    *,
    n_frames: int = 48,
    width: int = 160,
    height: int = 120,
    g: float = 400.0,
    dt: float = 1 / 30,
    restitution: float = 0.72,
    radius: int = 8,
) -> PhysicsTrace:
    """Integra caida + rebote elástico parcial; y crece hacia abajo."""
    floor = height - radius - 2
    y = float(radius + 4)
    v = 0.0
    positions: list[float] = []
    velocities: list[float] = []
    bounces: list[int] = []

    for i in range(n_frames):
        v += g * dt
        y += v * dt
        if y >= floor:
            y = floor
            if abs(v) > 1.0:
                v = -v * restitution
                bounces.append(i)
            else:
                v = 0.0
        positions.append(y)
        velocities.append(v)

    return PhysicsTrace(
        object="pelota",
        g=g,
        dt=dt,
        n_frames=n_frames,
        positions_y=positions,
        velocities_y=velocities,
        bounce_frames=bounces,
        energy_loss_per_bounce=round(1.0 - restitution**2, 4),
        note="Simulación 1D sintética (gravedad + restitución); sin cámara real.",
    )


def generate_falling_ball_frames(
    out_dir: str | Path,
    *,
    n_frames: int = 48,
    width: int = 160,
    height: int = 120,
    g: float = 400.0,
    dt: float = 1 / 30,
    restitution: float = 0.72,
    radius: int = 8,
) -> tuple[list[Path], PhysicsTrace]:
    """
    Escribe PNG en escala de grises (pelota blanca sobre fondo oscuro).
    Usa solo numpy (sin Pillow) para cero fricción extra.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    trace = synthesize_physics_trace(
        n_frames=n_frames,
        width=width,
        height=height,
        g=g,
        dt=dt,
        restitution=restitution,
        radius=radius,
    )

    cx = width // 2
    paths: list[Path] = []
    yy, xx = np.ogrid[:height, :width]

    for i, y in enumerate(trace.positions_y):
        img = np.zeros((height, width), dtype=np.uint8)
        img[:] = 24
        # suelo
        img[height - 3 :, :] = 80
        cy = int(round(y))
        mask = (xx - cx) ** 2 + (yy - cy) ** 2 <= radius**2
        img[mask] = 230
        path = out / f"frame_{i:04d}.png"
        _write_png_gray(path, img)
        paths.append(path)

    meta = out / "physics_trace.json"
    import json

    meta.write_text(
        json.dumps({"structured": trace.to_structured(), "raw": asdict(trace)}, indent=2),
        encoding="utf-8",
    )
    return paths, trace


def _write_png_gray(path: Path, img: np.ndarray) -> None:
    """PNG 8-bit grayscale mínimo (sin dependencias)."""
    import struct
    import zlib

    h, w = img.shape
    raw = b"".join(b"\x00" + img[r].tobytes() for r in range(h))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(png)
