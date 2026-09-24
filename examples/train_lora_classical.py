#!/usr/bin/env python3
"""
Train LoRA for CLASSICAL visual physics (NOT quantum).

Image → executable Python that prints {range_m, max_height_m, impact_speed_m_s}.

CRITICAL:
  - Write ONLY to data/lora_adapter_classical/ (default --out).
  - NEVER write/fuse into data/lora_adapter/ (quantum, READ-ONLY).
  - Anti-leak: user prompt has NO gold numeric metrics.

Usage:
  python examples/train_lora_classical.py --prepare-only
  python examples/train_lora_classical.py --epochs 1 --prepare-only  # dataset only
  python examples/train_lora_classical.py --epochs 1 --out data/lora_adapter_classical
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QUANTUM_ADAPTER_FORBIDDEN = (ROOT / "data" / "lora_adapter").resolve()


def _assert_out_safe(out: Path) -> None:
    resolved = out.resolve()
    if resolved == QUANTUM_ADAPTER_FORBIDDEN or QUANTUM_ADAPTER_FORBIDDEN in resolved.parents:
        raise SystemExit(
            f"REFUSING to write into quantum adapter path {QUANTUM_ADAPTER_FORBIDDEN}. "
            "Use data/lora_adapter_classical/."
        )
    if "lora_adapter_classical" not in str(resolved) and "classical" not in resolved.name:
        # soft warn but allow custom classical dirs
        print(
            f"[warn] --out {out} does not look classical; "
            "quantum data/lora_adapter/ remains forbidden.",
            file=sys.stderr,
        )


def _find_frame(scene_dir: Path) -> Path | None:
    for name in ("preview.png", "frame_0000.png", "frame_000.png", "frame.png"):
        p = scene_dir / name
        if p.exists():
            return p
    pngs = sorted(scene_dir.glob("*.png"))
    return pngs[0] if pngs else None


def load_classical_scenes(scenes_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not scenes_dir.is_dir():
        return rows
    for meta_path in sorted(scenes_dir.glob("**/meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta.get("lane") not in (None, "classical_visual_physics") and meta.get("domain") != "classical":
            # skip accidental quantum metas if mixed
            if meta.get("domain") in ("fall", "entanglement", "superposition"):
                continue
        scene_dir = meta_path.parent
        frame = _find_frame(scene_dir)
        target_py = meta.get("gold_python") or ""
        rows.append(
            {
                "scene_id": scene_dir.name,
                "meta_path": str(meta_path),
                "frame_path": str(frame) if frame else None,
                "meta": meta,
                "target_python": target_py,
            }
        )
    return rows


USER_PROMPT = (
    "You are a classical physics coding assistant. Look at the image of a motion scene. "
    "Write ONLY executable Python 3 (no markdown fences) that computes and prints a dict "
    "with keys range_m, max_height_m, impact_speed_m_s (SI units). "
    "Use math; no network; no file I/O. Infer parameters from the visual scene. "
    "Do not invent quantum circuits."
)


def _user_prompt(meta: dict[str, Any]) -> str:
    """Anti-leak: qualitative cues only — never gold metrics / full params numbers."""
    cues = meta.get("visual_cues") or {}
    summary = {
        "sport_or_mode": meta.get("sport_or_mode") or meta.get("subdomain"),
        "surface": meta.get("surface") or cues.get("surface"),
        "has_spin": cues.get("has_spin"),
        "has_drag": cues.get("has_drag"),
        "is_collision": cues.get("is_collision"),
        "angle_bin": cues.get("angle_bin"),
    }
    # drop Nones
    summary = {k: v for k, v in summary.items() if v is not None}
    return USER_PROMPT + f" Scene cues: {json.dumps(summary, ensure_ascii=False)}"


def build_chat_dataset(rows: list[dict[str, Any]], out_jsonl: Path) -> int:
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    leak = 0
    with out_jsonl.open("w", encoding="utf-8") as fh:
        for row in rows:
            meta = row["meta"]
            user = _user_prompt(meta)
            # leak check: user must not contain expected metric numbers
            exp = meta.get("expected_metrics") or {}
            for key in ("range_m", "max_height_m", "impact_speed_m_s"):
                val = exp.get(key)
                if val is None:
                    continue
                # stringify with enough precision that accidental inclusion is detectable
                s = f"{float(val):.4f}"
                if s in user and s not in ("0.0000",):
                    leak += 1
            assistant = row["target_python"]
            rec: dict[str, Any] = {
                "messages": [
                    {"role": "user", "content": user},
                    {"role": "assistant", "content": assistant},
                ],
                "scene_id": row["scene_id"],
                "domain": "classical",
                "subdomain": meta.get("subdomain"),
            }
            if row.get("frame_path"):
                rec["images"] = [row["frame_path"]]
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1
    print(f"Anti-leak scan: {leak} suspicious user rows (want 0)")
    return n


def _stage_hf_dataset_dir(dataset_path: Path) -> Path:
    dataset_path = Path(dataset_path)
    if dataset_path.is_dir() and (dataset_path / "train.jsonl").exists():
        for junk in dataset_path.glob("*.jsonl"):
            if junk.name != "train.jsonl":
                junk.unlink(missing_ok=True)
        return dataset_path
    if dataset_path.is_file() and dataset_path.suffix == ".jsonl":
        staged = dataset_path.parent / "lora_dataset_classical_hf"
        staged.mkdir(parents=True, exist_ok=True)
        for junk in staged.glob("*.jsonl"):
            junk.unlink(missing_ok=True)
        dest = staged / "train.jsonl"
        try:
            dest.symlink_to(dataset_path.resolve())
        except OSError:
            shutil.copy2(dataset_path, dest)
        return staged
    return dataset_path


def run_mlx_vlm_lora(
    *,
    model: str,
    dataset_path: Path,
    out_dir: Path,
    rank: int,
    alpha: float,
    lr: float,
    epochs: int,
    batch_size: int,
) -> int:
    _assert_out_safe(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    staged = _stage_hf_dataset_dir(dataset_path)
    cmd = [
        sys.executable,
        "-m",
        "mlx_vlm.lora",
        "--model",
        model,
        "--data",
        str(staged),
        "--adapter-path",
        str(out_dir),
        "--batch-size",
        str(batch_size),
        "--lora-layers",
        "16",
        "--iters",
        str(max(50, epochs * max(1, _count_rows(dataset_path)))),
        # Prefer completions-only training when flag exists (anti-leak PASO1)
    ]
    # Estimate iters like quantum path: epochs * n_rows
    n = _count_rows(dataset_path)
    iters = max(50, epochs * n)
    # rebuild with correct iters
    cmd = [
        sys.executable,
        "-m",
        "mlx_vlm.lora",
        "--model",
        model,
        "--data",
        str(staged),
        "--adapter-path",
        str(out_dir),
        "--train",
        "--batch-size",
        str(batch_size),
        "--num-layers",
        "16",
        "--iters",
        str(iters),
        "--learning-rate",
        str(lr),
        "--save-every",
        "100",
        "--adapter-path",
        str(out_dir),
    ]
    # Try with rank/fine-tune-type if supported — match quantum train_lora flags
    # Inspect quantum runner for exact flags:
    extra = _quantum_lora_flag_template(rank=rank, alpha=alpha, lr=lr, epochs=epochs, iters=iters)
    if extra:
        cmd = extra(model=model, staged=staged, out_dir=out_dir, batch_size=batch_size)

    print("Ejecutando:", " ".join(cmd), flush=True)
    try:
        return subprocess.call(cmd)
    except FileNotFoundError:
        print("No se pudo invocar mlx_vlm.lora. pip install -U mlx-vlm", file=sys.stderr)
        return 2


def _count_rows(dataset_path: Path) -> int:
    p = Path(dataset_path)
    if p.is_file():
        return sum(1 for _ in p.open())
    train = p / "train.jsonl"
    if train.exists():
        return sum(1 for _ in train.open())
    return 0


def _quantum_lora_flag_template(**_kw):
    """Reuse flags from examples/train_lora.run_mlx_vlm_lora if importable."""
    try:
        sys.path.insert(0, str(ROOT / "examples"))
        import train_lora as tl  # noqa: WPS433

        def runner(*, model, staged, out_dir, batch_size):
            return [
                # call the shared helper directly
            ]

        # Prefer calling the shared function
        def call(*, model, staged, out_dir, batch_size):
            return None  # signal to use tl.run_mlx_vlm_lora below

        return None
    except Exception:
        return None


def main() -> int:
    p = argparse.ArgumentParser(description="Classical LoRA train (separate from quantum)")
    p.add_argument("--model", default="mlx-community/Qwen3-VL-8B-Thinking-4bit")
    p.add_argument("--scenes", type=Path, default=ROOT / "data" / "classical_scenes")
    p.add_argument("--out", type=Path, default=ROOT / "data" / "lora_adapter_classical")
    p.add_argument(
        "--dataset-jsonl",
        type=Path,
        default=ROOT / "data" / "lora_dataset_classical.jsonl",
    )
    p.add_argument("--rank", type=int, default=16)
    p.add_argument("--alpha", type=float, default=16.0)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--epochs", type=int, default=1)
    p.add_argument("--batch-size", type=int, default=1)
    p.add_argument("--prepare-only", action="store_true")
    p.add_argument("--skip-train", action="store_true")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    _assert_out_safe(args.out)

    rows = load_classical_scenes(args.scenes)
    if len(rows) < 5:
        print(
            f"[warn] Solo {len(rows)} escenas en {args.scenes}. "
            "Genera: python examples/synthetic_classical_physics.py --n-scenes 220",
            file=sys.stderr,
        )

    n = build_chat_dataset(rows, args.dataset_jsonl)
    dom = Counter((r["meta"].get("subdomain") or "?") for r in rows)
    print(f"Dataset JSONL: {args.dataset_jsonl} ({n} filas) subdomains={dict(dom)}")
    if args.prepare_only:
        return 0 if n else 1

    if args.skip_train:
        return 0

    # Stage into classical-only HF dir so shared lora_dataset_hf (quantum/ent)
    # cannot contaminate schema (CastError on subdomain vs label).
    staged = _stage_hf_dataset_dir(args.dataset_jsonl)
    # Prefer shared mlx runner from train_lora (same flags as quantum lane)
    sys.path.insert(0, str(ROOT / "examples"))
    from train_lora import run_mlx_vlm_lora as shared_lora  # noqa: WPS433

    rc = shared_lora(
        model=args.model,
        dataset_path=staged,
        out_dir=args.out,
        rank=args.rank,
        alpha=args.alpha,
        lr=args.lr,
        epochs=args.epochs,
        batch_size=args.batch_size,
    )
    meta = {
        "lane": "classical_visual_physics",
        "model": args.model,
        "rank": args.rank,
        "alpha": args.alpha,
        "lr": args.lr,
        "epochs": args.epochs,
        "n_train_rows": n,
        "dataset": str(args.dataset_jsonl),
        "scenes": str(args.scenes),
        "note": "Separate from quantum data/lora_adapter/ (READ-ONLY).",
    }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "train_meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
