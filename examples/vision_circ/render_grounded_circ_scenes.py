#!/usr/bin/env python3
"""Render tip-circ-expand grounded circuit vision PNGs (text-card style).

Writes into data/bench_live/vision_items/ (often gitignored / shared via QLAB_DATA).
Does NOT touch data/lora_adapter/. No GT in prompts.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 512, 320

SCENES = {
    "vis_circ_03.png": [
        "Circuit (2 qubits):",
        "q0: H",
        "Then CNOT q0->q1",
        "(no other gates)",
        "Return JSON: n_qubits,gates",
    ],
    "vis_circ_04.png": [
        "Circuit (3 qubits):",
        "q0: H",
        "Then CNOT q0->q1",
        "Then CNOT q1->q2",
        "Return JSON: n_qubits,gates",
    ],
    "vis_circ_05.png": [
        "Circuit (2 qubits):",
        "q0: X",
        "q1: RY(pi/2)",
        "Then CNOT q0->q1",
        "Return JSON: n_qubits,gates",
    ],
}


def _font(size: int = 22) -> ImageFont.ImageFont:
    for p in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ):
        try:
            return ImageFont.truetype(p, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def render(path: Path, lines: list[str]) -> None:
    img = Image.new("RGB", (W, H), (255, 255, 255))
    dr = ImageDraw.Draw(img)
    f = _font(22)
    y = 36
    for line in lines:
        dr.text((36, y), line, fill=(0, 0, 0), font=f)
        y += 36
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/bench_live/vision_items"),
        help="Directory for PNGs (shared QLAB_DATA vision_items recommended)",
    )
    args = ap.parse_args()
    for name, lines in SCENES.items():
        dest = args.out_dir / name
        render(dest, lines)
        print(f"wrote {dest} ({dest.stat().st_size} B)")


if __name__ == "__main__":
    main()
