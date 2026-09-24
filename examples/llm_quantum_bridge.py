#!/usr/bin/env python3
"""
Puente mínimo LLM → circuito cuántico → simulador.

- Modo --demo: el "LLM" es un stub que propone un circuito fijo (sin descargar modelos).
- Modo --mlx: usa mlx-lm en Apple Silicon para que un modelo pequeño proponga el circuito.

El simulador (PennyLane, CPU) siempre verifica y ejecuta el circuito de 2–3 qubits.
Comentarios en español. Punto de partida, no producto terminado.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

import numpy as np

# ---------------------------------------------------------------------------
# 1) Propuesta del "LLM": texto → lista de puertas
# ---------------------------------------------------------------------------

# Formato esperado (JSON en una sola línea o bloque):
# {"n_qubits": 2, "gates": [["h", 0], ["cx", 0, 1], ["ry", 1, 0.5]]}
# Puertas: h, x, y, z, cx (control, target), ry (qubit, theta)

DEMO_PROPOSAL = {
    "n_qubits": 2,
    "gates": [
        ["h", 0],
        ["cx", 0, 1],
        ["ry", 1, 0.4],
    ],
    "nota": "Circuito Bell-like + rotación suave en q1 (stub demo).",
}


def proponer_circuito_demo(_prompt: str) -> dict[str, Any]:
    """Stub: simula lo que diría un LLM pequeño sin bajar pesos."""
    return dict(DEMO_PROPOSAL)


def proponer_circuito_mlx(prompt: str, model_id: str) -> dict[str, Any]:
    """
    Pide a un modelo MLX un JSON de circuito.
    Requiere: pip install 'quantum-llm-lab[mlx]' en macOS Apple Silicon.
    """
    try:
        from mlx_lm import load, generate
    except ImportError as exc:
        raise SystemExit(
            "mlx-lm no está instalado o no estás en macOS Apple Silicon.\n"
            "Instala con: pip install 'mlx-lm'  (solo Darwin)\n"
            "O corre con --demo para probar el simulador sin LLM.\n"
            f"Detalle: {exc}"
        ) from exc

    system = (
        "Eres un asistente de circuitos cuánticos. Responde SOLO con un JSON "
        'válido de la forma {"n_qubits":2|3,"gates":[["h",0],["cx",0,1],["ry",1,0.3]]}. '
        "Puertas permitidas: h, x, y, z, cx, ry. Sin markdown ni texto extra."
    )
    full = f"{system}\n\nUsuario: {prompt}\n\nJSON:"
    model, tokenizer = load(model_id)
    raw = generate(model, tokenizer, prompt=full, max_tokens=200, verbose=False)
    return parsear_propuesta(raw)


def _extract_balanced_json(texto: str) -> str | None:
    """Find first '{' ... matching '}' with brace balance (not greedy regex)."""
    start = texto.find("{")
    while start != -1:
        depth = 0
        in_str = False
        escape = False
        for i in range(start, len(texto)):
            ch = texto[i]
            if in_str:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return texto[start : i + 1]
        start = texto.find("{", start + 1)
    return None


def parsear_propuesta(texto: str) -> dict[str, Any]:
    """Extrae el primer objeto JSON del texto del modelo (brace-balanced)."""
    texto = texto.strip()
    try:
        data = json.loads(texto)
        if isinstance(data, dict) and "gates" in data:
            return data
    except json.JSONDecodeError:
        pass

    blob = _extract_balanced_json(texto)
    if not blob:
        raise ValueError(f"No encontré JSON en la respuesta del modelo:\n{texto[:500]}")
    data = json.loads(blob)
    if "gates" not in data:
        raise ValueError(f"JSON sin 'gates': {data}")
    data.setdefault("n_qubits", 2)
    return data


# ---------------------------------------------------------------------------
# 2) Simulador PennyLane (CPU)
# ---------------------------------------------------------------------------

def ejecutar_circuito(propuesta: dict[str, Any]) -> dict[str, Any]:
    """Construye y mide el circuito en el dispositivo default.qubit."""
    import pennylane as qml

    n = int(propuesta.get("n_qubits", 2))
    if n < 1 or n > 3:
        raise ValueError("Este lab solo acepta 1–3 qubits (punto de partida).")

    gates = propuesta["gates"]
    dev = qml.device("default.qubit", wires=n)

    @qml.qnode(dev)
    def circuito():
        for g in gates:
            op = g[0].lower()
            if op == "h":
                qml.Hadamard(wires=int(g[1]))
            elif op == "x":
                qml.PauliX(wires=int(g[1]))
            elif op == "y":
                qml.PauliY(wires=int(g[1]))
            elif op == "z":
                qml.PauliZ(wires=int(g[1]))
            elif op == "cx":
                qml.CNOT(wires=[int(g[1]), int(g[2])])
            elif op == "ry":
                qml.RY(float(g[2]), wires=int(g[1]))
            else:
                raise ValueError(f"Puerta no soportada en el lab: {op}")
        return qml.probs(wires=range(n))

    probs = np.asarray(circuito(), dtype=float)
    estados = [format(i, f"0{n}b") for i in range(len(probs))]
    return {
        "n_qubits": n,
        "gates": gates,
        "probabilities": {s: float(p) for s, p in zip(estados, probs)},
        "sum_check": float(probs.sum()),
    }


# ---------------------------------------------------------------------------
# 3) CLI
# ---------------------------------------------------------------------------

DEFAULT_PROMPT = (
    "Propón un circuito de 2 qubits que prepare un estado tipo Bell "
    "y luego rote un poco el segundo qubit."
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="LLM (demo o MLX) propone un circuito; PennyLane lo ejecuta en CPU."
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Usa stub en lugar de MLX (recomendado para la primera prueba).",
    )
    parser.add_argument(
        "--mlx",
        action="store_true",
        help="Usa mlx-lm en Apple Silicon (descarga un modelo pequeño la primera vez).",
    )
    parser.add_argument(
        "--model",
        default="mlx-community/Llama-3.2-3B-Instruct-4bit",
        help="ID Hugging Face / MLX Community (solo con --mlx).",
    )
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help="Instrucción en lenguaje natural para el LLM.",
    )
    parser.add_argument(
        "--context-file",
        default=None,
        help="JSON de visión (grounding.json): antepone llm_context al prompt.",
    )
    args = parser.parse_args(argv)

    if args.context_file:
        from pathlib import Path
        import json as _json
        blob = _json.loads(Path(args.context_file).read_text(encoding="utf-8"))
        ctx = blob.get("llm_context") or _json.dumps(blob.get("structured", blob), ensure_ascii=False)
        args.prompt = (
            "Contexto visual grounded:\n"
            + ctx
            + "\n\nTarea: "
            + args.prompt
        )

    if args.mlx and args.demo:
        print("Elige solo uno: --demo o --mlx", file=sys.stderr)
        return 2
    if not args.mlx and not args.demo:
        # Por defecto demo: cero fricción la primera vez
        args.demo = True

    print("=== quantum-llm-lab ===")
    print(f"Modo: {'MLX ' + args.model if args.mlx else 'demo (stub)'}")
    print(f"Prompt: {args.prompt}\n")

    if args.mlx:
        propuesta = proponer_circuito_mlx(args.prompt, args.model)
    else:
        propuesta = proponer_circuito_demo(args.prompt)

    print("Propuesta del LLM:")
    print(json.dumps(propuesta, ensure_ascii=False, indent=2))
    print()

    resultado = ejecutar_circuito(propuesta)
    print("Resultado del simulador (probabilidades):")
    for estado, p in resultado["probabilities"].items():
        barra = "#" * int(round(p * 40))
        print(f"  |{estado}>  {p:.4f}  {barra}")
    print(f"\nSuma de probs (debe ~1.0): {resultado['sum_check']:.6f}")
    print("Listo. Itera el prompt o cambia a --mlx en tu Mac M4.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
