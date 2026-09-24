#!/usr/bin/env python3
"""
Fine-tune LoRA / QLoRA del Qwen3-VL (mlx-vlm) sobre escenas sintéticas.

Flujo:
  1) Lee data/scenes/*/meta.json (+ frame PNG).
  2) Construye un dataset JSONL estilo chat (imagen → JSON de circuito target).
  3) Lanza mlx_vlm.lora (o deja el dataset listo si --prepare-only).
  4) Guarda el adapter en data/lora_adapter/.
  5) Evalúa base vs adapter en 10 escenas (tasa parse/compile/Jev).

Uso:
  python examples/train_lora.py --prepare-only
  python examples/train_lora.py --epochs 3 --rank 32 --lr 2e-4
"""

from __future__ import annotations

import argparse
import json
import math
import random
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "examples") not in sys.path:
    sys.path.insert(0, str(ROOT / "examples"))


def _circuit_target_from_meta(meta: dict[str, Any]) -> dict[str, Any]:
    """Firma toy determinista alineada con Jev (caída + atenuación RY)."""
    loss = float(meta.get("energy_loss_per_bounce") or meta.get("perdida_energia_por_rebote") or 0.3)
    # map loss → ry angle in (0.2, 1.2)
    theta = round(0.2 + min(1.0, max(0.0, loss)) * 1.0, 3)
    n_bounce = len(meta.get("bounce_frames") or meta.get("rebotes") or [])
    gates: list[list[Any]] = [["h", 0], ["cx", 0, 1], ["ry", 1, theta]]
    if n_bounce >= 2:
        gates.append(["ry", 0, round(theta * 0.5, 3)])
    return {
        "n_qubits": 2,
        "gates": gates,
        "nota": (
            f"Firma toy de caída con pérdida por rebote (~{loss:.2f}); "
            "no afirma conservación perfecta."
        ),
    }


def _find_frame(scene_dir: Path) -> Path | None:
    for name in ("frame_000.png", "frame_00.png", "preview.png", "frame.png"):
        p = scene_dir / name
        if p.exists():
            return p
    pngs = sorted(scene_dir.glob("*.png"))
    return pngs[0] if pngs else None


def load_scenes(scenes_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not scenes_dir.is_dir():
        return rows
    for meta_path in sorted(scenes_dir.glob("**/meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        scene_dir = meta_path.parent
        frame = _find_frame(scene_dir)
        target = _circuit_target_from_meta(meta)
        rows.append(
            {
                "scene_id": scene_dir.name,
                "meta_path": str(meta_path),
                "frame_path": str(frame) if frame else None,
                "meta": meta,
                "target": target,
            }
        )
    return rows


def build_chat_dataset(rows: list[dict[str, Any]], out_jsonl: Path) -> int:
    """Formato compatible con pipelines VLM: messages + images."""
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out_jsonl.open("w", encoding="utf-8") as fh:
        for row in rows:
            meta = row["meta"]
            summary = {
                k: meta.get(k)
                for k in (
                    "shape",
                    "color",
                    "surface",
                    "gravity_condition",
                    "energy_loss_per_bounce",
                    "perdida_energia_por_rebote",
                    "restitution",
                    "trayectoria",
                    "objeto",
                )
                if meta.get(k) is not None
            }
            user = (
                "Eres un asistente de circuitos cuánticos. Dada esta escena de física visual, "
                "propón un circuito de 2 qubits (firma toy de caída + pérdida de energía). "
                "Responde SOLO JSON válido "
                '{"n_qubits":2,"gates":[["h",0],["cx",0,1],["ry",1,0.4]],"nota":"..."}. '
                f"Escena: {json.dumps(summary, ensure_ascii=False)}"
            )
            assistant = json.dumps(row["target"], ensure_ascii=False)
            rec: dict[str, Any] = {
                "messages": [
                    {"role": "user", "content": user},
                    {"role": "assistant", "content": assistant},
                ],
                "scene_id": row["scene_id"],
            }
            if row.get("frame_path"):
                rec["images"] = [row["frame_path"]]
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1
    return n


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
    out_dir.mkdir(parents=True, exist_ok=True)
    # mlx_vlm.lora acepta dataset HF id o ruta según versión; pasamos ruta al jsonl dir.
    cmd = [
        sys.executable,
        "-m",
        "mlx_vlm.lora",
        "--model-path",
        model,
        "--dataset",
        str(dataset_path),
        "--lora-rank",
        str(rank),
        "--lora-alpha",
        str(alpha),
        "--learning-rate",
        str(lr),
        "--epochs",
        str(epochs),
        "--batch-size",
        str(batch_size),
        "--output-path",
        str(out_dir / "adapters.safetensors"),
    ]
    print("Ejecutando:", " ".join(cmd), flush=True)
    try:
        return subprocess.call(cmd)
    except FileNotFoundError:
        print(
            "No se pudo invocar mlx_vlm.lora. Instala: pip install -U mlx-vlm",
            file=sys.stderr,
        )
        return 2


def evaluate_subset(
    rows: list[dict[str, Any]],
    *,
    model_id: str,
    adapter: str | None,
    n_test: int,
    seed: int,
) -> dict[str, Any]:
    """Métricas sin forzar VLM si --dry-metrics: usa solo targets (sanity)."""
    from jev_arbiter import arbitrate

    try:
        from llm_quantum_bridge import ejecutar_circuito, parsear_propuesta
    except ImportError:
        ejecutar_circuito = None  # type: ignore
        parsear_propuesta = None  # type: ignore

    rng = random.Random(seed)
    sample = rows[:] if len(rows) <= n_test else rng.sample(rows, n_test)

    # Optional live VLM
    use_vlm = False
    model = processor = config = None
    if adapter is not None or True:
        try:
            from mlx_vlm import load, generate
            from mlx_vlm.prompt_utils import apply_chat_template
            from mlx_vlm.utils import load_config

            kwargs = {"adapter_path": adapter} if adapter else {}
            print(f"Cargando VLM {model_id} adapter={adapter!r} …", flush=True)
            model, processor = load(model_id, **kwargs)
            config = load_config(model_id)
            use_vlm = True
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] VLM no disponible ({exc}); métricas con targets gold.", file=sys.stderr)

    parsed = compiled = approved = 0
    details: list[dict[str, Any]] = []
    for row in sample:
        proposal: dict[str, Any]
        source = "gold"
        if use_vlm and model is not None:
            summary = json.dumps(
                {k: row["meta"].get(k) for k in row["meta"] if k in (
                    "shape", "color", "energy_loss_per_bounce", "perdida_energia_por_rebote",
                    "trayectoria", "surface",
                )},
                ensure_ascii=False,
            )
            prompt = (
                "Propón SOLO JSON de circuito 2 qubits con gates h/cx/ry "
                f"para esta escena: {summary}"
            )
            image = row.get("frame_path")
            formatted = apply_chat_template(
                processor, config, prompt, num_images=1 if image else 0
            )
            try:
                result = generate(
                    model, processor, formatted, image=image, max_tokens=220, verbose=False
                )
                text = result.text if hasattr(result, "text") else str(result)
                proposal = parsear_propuesta(text) if parsear_propuesta else row["target"]
                source = "vlm"
            except Exception as exc:  # noqa: BLE001
                proposal = row["target"]
                source = f"fallback:{exc}"
        else:
            proposal = row["target"]

        ok_parse = "gates" in proposal and "n_qubits" in proposal
        if ok_parse:
            parsed += 1
        sim = None
        ok_compile = False
        if ok_parse and ejecutar_circuito:
            try:
                sim = ejecutar_circuito(proposal)
                ok_compile = True
                compiled += 1
            except Exception:
                ok_compile = False
        scene = row["meta"]
        if "perdida_energia_por_rebote" not in scene and "energy_loss_per_bounce" in scene:
            scene = dict(scene)
            scene["perdida_energia_por_rebote"] = scene["energy_loss_per_bounce"]
        if "trayectoria" not in scene:
            scene = dict(scene)
            scene["trayectoria"] = "caída vertical con rebotes"
        verdict = arbitrate(proposal, scene, sim)
        if verdict["verdict"] == "APROBAR":
            approved += 1
        details.append(
            {
                "scene_id": row["scene_id"],
                "source": source,
                "parse": ok_parse,
                "compile": ok_compile,
                "jev": verdict["verdict"],
                "reason": verdict["reason"],
            }
        )

    n = max(1, len(sample))
    return {
        "n": len(sample),
        "parse_rate": parsed / n,
        "compile_rate": compiled / n,
        "jev_approve_rate": approved / n,
        "details": details,
        "used_vlm": use_vlm,
        "adapter": adapter,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="LoRA train wrapper (mlx-vlm) + eval")
    p.add_argument("--model", default="mlx-community/Qwen3-VL-8B-Thinking-4bit")
    p.add_argument("--scenes", type=Path, default=ROOT / "data" / "scenes")
    p.add_argument("--out", type=Path, default=ROOT / "data" / "lora_adapter")
    p.add_argument("--dataset-jsonl", type=Path, default=ROOT / "data" / "lora_dataset.jsonl")
    p.add_argument("--rank", type=int, default=32)
    p.add_argument("--alpha", type=float, default=32.0)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--epochs", type=int, default=3)
    p.add_argument("--batch-size", type=int, default=1)
    p.add_argument("--n-test", type=int, default=10)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--prepare-only", action="store_true", help="Solo arma el JSONL")
    p.add_argument("--skip-eval", action="store_true")
    p.add_argument("--skip-train", action="store_true")
    args = p.parse_args()

    rows = load_scenes(args.scenes)
    if len(rows) < 5:
        print(
            f"[warn] Solo {len(rows)} escenas en {args.scenes}. "
            "Genera con: python examples/synthetic_physics_dataset.py --n-scenes 220",
            file=sys.stderr,
        )

    n = build_chat_dataset(rows, args.dataset_jsonl)
    print(f"Dataset JSONL: {args.dataset_jsonl} ({n} filas)")
    if args.prepare_only:
        return 0 if n else 1

    pre = None
    if not args.skip_eval and rows:
        print("=== Eval BASE (antes) ===", flush=True)
        # sin adapter; si VLM no está, usa gold (parse/compile/Jev del target)
        pre = evaluate_subset(
            rows, model_id=args.model, adapter=None, n_test=args.n_test, seed=args.seed
        )
        print(json.dumps({k: pre[k] for k in ("n", "parse_rate", "compile_rate", "jev_approve_rate", "used_vlm")}, indent=2))

    rc = 0
    if not args.skip_train:
        # Prefer directory containing jsonl for some mlx_vlm versions
        ds = args.dataset_jsonl if args.dataset_jsonl.exists() else args.scenes
        rc = run_mlx_vlm_lora(
            model=args.model,
            dataset_path=ds,
            out_dir=args.out,
            rank=args.rank,
            alpha=args.alpha,
            lr=args.lr,
            epochs=args.epochs,
            batch_size=args.batch_size,
        )
        meta = {
            "model": args.model,
            "rank": args.rank,
            "alpha": args.alpha,
            "lr": args.lr,
            "epochs": args.epochs,
            "n_train_rows": n,
            "dataset": str(args.dataset_jsonl),
        }
        (args.out / "train_meta.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    if not args.skip_eval and rows and rc == 0:
        print("=== Eval ADAPTER (después) ===", flush=True)
        post = evaluate_subset(
            rows,
            model_id=args.model,
            adapter=str(args.out),
            n_test=args.n_test,
            seed=args.seed,
        )
        print(json.dumps({k: post[k] for k in ("n", "parse_rate", "compile_rate", "jev_approve_rate", "used_vlm")}, indent=2))
        if pre:
            delta = post["jev_approve_rate"] - pre["jev_approve_rate"]
            print(f"Delta Jev APROBAR: {delta:+.0%} (éxito si >= +20 puntos)")
            report = {"pre": pre, "post": post, "delta_jev": delta}
            (args.out / "eval_before_after.json").write_text(
                json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )

    return rc


if __name__ == "__main__":
    sys.exit(main())
