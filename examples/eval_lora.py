#!/usr/bin/env python3
"""
Compara modelo base vs LoRA en N escenas de prueba.

Métricas: JSON parseable, compila PennyLane, Jev APROBAR.
Reporta mejora absoluta en tasa Jev.

  python examples/eval_lora.py --adapter data/lora_adapter --n-test 10
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "examples"))

from train_lora import evaluate_subset, load_scenes  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Eval base vs LoRA adapter")
    p.add_argument("--model", default="mlx-community/Qwen3-VL-8B-Thinking-4bit")
    p.add_argument("--adapter", type=Path, default=ROOT / "data" / "lora_adapter")
    p.add_argument("--scenes", type=Path, default=ROOT / "data" / "scenes")
    p.add_argument("--n-test", type=int, default=10)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=Path, default=None, help="JSON report path")
    args = p.parse_args()

    rows = load_scenes(args.scenes)
    if not rows:
        print(f"Sin escenas en {args.scenes}. Genera el dataset primero.", file=sys.stderr)
        return 1

    print("=== BASE ===", flush=True)
    base = evaluate_subset(
        rows, model_id=args.model, adapter=None, n_test=args.n_test, seed=args.seed
    )
    print(
        json.dumps(
            {k: base[k] for k in ("n", "parse_rate", "compile_rate", "jev_approve_rate", "domain_acc", "label_acc", "energy_ok_rate", "unique_gate_combos", "used_vlm")},
            indent=2,
        )
    )

    adapter_path = str(args.adapter) if args.adapter.exists() else None
    if not adapter_path:
        print(f"[warn] Adapter no encontrado en {args.adapter}; solo reporto BASE.", file=sys.stderr)
        ft = None
    else:
        print("=== FINE-TUNE (adapter) ===", flush=True)
        ft = evaluate_subset(
            rows,
            model_id=args.model,
            adapter=adapter_path,
            n_test=args.n_test,
            seed=args.seed,
        )
        print(
            json.dumps(
                {k: ft[k] for k in ("n", "parse_rate", "compile_rate", "jev_approve_rate", "domain_acc", "label_acc", "energy_ok_rate", "unique_gate_combos", "used_vlm")},
                indent=2,
            )
        )

    report = {"base": base, "finetuned": ft}
    if ft:
        report["delta"] = {
            "parse_rate": ft["parse_rate"] - base["parse_rate"],
            "compile_rate": ft["compile_rate"] - base["compile_rate"],
            "jev_approve_rate": ft["jev_approve_rate"] - base["jev_approve_rate"],
            "domain_acc": ft.get("domain_acc", 0) - base.get("domain_acc", 0),
            "label_acc": ft.get("label_acc", 0) - base.get("label_acc", 0),
        }
        d = report["delta"]["jev_approve_rate"]
        print(f"\nMejora Jev APROBAR: {d:+.0%} (meta: +20 puntos)")
        print(
            f"FT domain_acc={ft.get('domain_acc', 0):.2f} "
            f"label_acc={ft.get('label_acc', 0):.2f} "
            f"energy_ok={ft.get('energy_ok_rate', 0):.2f} "
            f"gate_combos={ft.get('unique_gate_combos', 0)} "
            f"(meta label≥0.7)"
        )
        ok = d >= 0.20
        print("Criterio de éxito:", "PASS" if ok else "NO PASS aún")

    out = args.out or (args.adapter / "eval_compare.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Reporte: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
