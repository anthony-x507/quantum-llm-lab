#!/usr/bin/env python3
"""
Capa de visión → texto grounded → (opcional) puente LLM→cuántico.

Ejemplos:
  python examples/vision_grounding.py --demo
  python examples/vision_grounding.py --demo --pipeline
  python examples/vision_grounding.py --mlx --model mlx-community/Qwen2-VL-2B-Instruct-4bit
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Permitir import vision/ desde la raíz del repo
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vision.grounding import ground_frames


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Visión local (frames sintéticos) + grounding")
    p.add_argument("--demo", action="store_true", help="Grounding desde física sintética (sin VLM)")
    p.add_argument("--mlx", action="store_true", help="Qwen2-VL u otro vía mlx-vlm")
    p.add_argument(
        "--model",
        default=None,
        help="Modelo MLX VLM. M4 128GB: Qwen2-VL-7B-Instruct-4bit. Studio 36GB: 2B-4bit.",
    )
    p.add_argument("--frames", default="examples/out_frames", help="Carpeta de PNG de salida")
    p.add_argument("--n-frames", type=int, default=48)
    p.add_argument(
        "--pipeline",
        action="store_true",
        help="Pasa el texto grounded al puente llm_quantum_bridge (hipótesis→circuito).",
    )
    p.add_argument("--keep-frames", action="store_true", help="No regenerar PNG si ya existen")
    args = p.parse_args(argv)

    mode = "mlx" if args.mlx else "demo"
    if args.mlx and args.demo:
        print("Elige --demo o --mlx", file=sys.stderr)
        return 2

    # Defaults de clúster
    model = args.model
    if mode == "mlx" and not model:
        model = "mlx-community/Qwen2-VL-7B-Instruct-4bit"

    result = ground_frames(
        frame_dir=args.frames,
        mode=mode,
        model_id=model,
        n_frames=args.n_frames,
        regenerate=not args.keep_frames,
    )

    print("=== vision grounding ===")
    print(f"Fuente: {result.source}")
    print(f"Frames: {result.frame_dir}")
    print(json.dumps(result.structured, ensure_ascii=False, indent=2))
    print("\nNarrativa:")
    print(result.narrative)

    out_json = Path(args.frames) / "grounding.json"
    out_json.write_text(
        json.dumps(
            {
                "source": result.source,
                "structured": result.structured,
                "narrative": result.narrative,
                "llm_context": result.as_llm_context(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nGuardado: {out_json}")

    if args.pipeline:
        return _run_pipeline(result.as_llm_context())
    return 0


def _run_pipeline(context: str) -> int:
    """Conecta visión → LLM puente → PennyLane."""
    import importlib.util

    bridge_path = Path(__file__).resolve().parent / "llm_quantum_bridge.py"
    spec = importlib.util.spec_from_file_location("llm_quantum_bridge", bridge_path)
    bridge = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(bridge)
    ejecutar_circuito = bridge.ejecutar_circuito
    proponer_circuito_demo = bridge.proponer_circuito_demo

    prompt = (
        "A partir de esta observación visual de un objeto que cae y rebota, "
        "formula una hipótesis física breve y propón un circuito cuántico de 2 qubits "
        "cuya estructura de amplitudes sirva como 'firma' toy de (1) caída acelerada y "
        "(2) pérdida de energía en rebotes. Responde SOLO el JSON de circuito.\n\n"
        + context
    )
    print("\n=== pipeline → llm_quantum_bridge (demo stub) ===")
    # Stub siempre disponible; en Mac con --mlx del bridge se puede extender después
    propuesta = proponer_circuito_demo(prompt)
    # Anotar contexto en la propuesta para trazabilidad
    propuesta = dict(propuesta)
    propuesta["hipotesis_contexto"] = (
        "Firma toy: Bell-like = correlación; RY = atenuación tras rebote."
    )
    print(json.dumps(propuesta, ensure_ascii=False, indent=2))
    resultado = ejecutar_circuito(propuesta)
    print("Probabilidades:")
    for est, pr in resultado["probabilities"].items():
        print(f"  |{est}> {pr:.4f}")
    print(f"Suma: {resultado['sum_check']:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
