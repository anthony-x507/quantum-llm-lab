"""Grounding: frames → texto estructurado (demo físico o VLM MLX)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .synthetic_fall import PhysicsTrace, generate_falling_ball_frames


@dataclass
class GroundingResult:
    structured: dict[str, Any]
    narrative: str
    source: str  # "demo-physics" | "mlx-vlm"
    frame_dir: str

    def as_llm_context(self) -> str:
        return (
            "Observación visual grounded (visión local):\n"
            + json.dumps(self.structured, ensure_ascii=False, indent=2)
            + "\n\nNarrativa:\n"
            + self.narrative
        )


def ground_frames(
    *,
    frame_dir: str | Path | None = None,
    mode: str = "demo",
    model_id: str | None = None,
    n_frames: int = 48,
    regenerate: bool = True,
) -> GroundingResult:
    """
    mode=demo: usa la traza física sintética (sin VLM).
    mode=mlx: intenta mlx-vlm (Qwen2-VL u otro) sobre unos frames clave.
    """
    out = Path(frame_dir or "examples/out_frames")
    if regenerate or not (out / "physics_trace.json").exists():
        paths, trace = generate_falling_ball_frames(out, n_frames=n_frames)
    else:
        import json as _json

        data = _json.loads((out / "physics_trace.json").read_text(encoding="utf-8"))
        # Reconstruir mínima para narrativa demo
        from .synthetic_fall import PhysicsTrace as PT

        raw = data["raw"]
        trace = PT(**raw)
        paths = sorted(out.glob("frame_*.png"))

    if mode == "demo":
        structured = trace.to_structured()
        narrative = _narrative_from_structured(structured)
        return GroundingResult(
            structured=structured,
            narrative=narrative,
            source="demo-physics",
            frame_dir=str(out),
        )

    if mode == "mlx":
        mid = model_id or "mlx-community/Qwen2-VL-7B-Instruct-4bit"
        structured, narrative = _ground_with_mlx_vlm(paths, mid, fallback=trace)
        return GroundingResult(
            structured=structured,
            narrative=narrative,
            source="mlx-vlm",
            frame_dir=str(out),
        )

    raise ValueError(f"mode desconocido: {mode} (usa demo|mlx)")


def _narrative_from_structured(s: dict[str, Any]) -> str:
    n_b = len(s.get("rebotes") or [])
    return (
        f"Se observa un(a) {s.get('objeto', 'objeto')} en {s.get('trayectoria')}. "
        f"Aceleración aproximada {s.get('aceleracion_aprox_px_s2')} px/s² "
        f"(g simulado {s.get('gravedad_simulada_px_s2')}). "
        f"Hay {n_b} rebote(s); en cada uno se pierde fracción "
        f"{s.get('perdida_energia_por_rebote')} de energía cinética. "
        f"Frames: {s.get('n_frames')}."
    )



def _strip_think_and_extract(text_out: str) -> str:
    """Remove <think> blocks; prefer text after last </think>; else keep JSON span."""
    import re

    if not text_out:
        return ""
    cleaned = re.sub(r"<think>[\s\S]*?</think>", "", text_out, flags=re.I)
    lower_orig = text_out.lower()
    if "</think>" in lower_orig:
        idx = lower_orig.rfind("</think>")
        cleaned = text_out[idx + len("</think>") :]
    elif "<think>" in lower_orig and "{" in text_out:
        cleaned = text_out[text_out.find("{") :]
    cleaned = cleaned.strip()
    if "{" in cleaned:
        start = cleaned.find("{")
        depth = 0
        in_str = False
        escape = False
        end = None
        for i in range(start, len(cleaned)):
            ch = cleaned[i]
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
                    end = i
                    break
        if end is not None:
            return cleaned[start : end + 1]
        return cleaned[start:]
    return cleaned


def _ground_with_mlx_vlm(
    paths: list[Path],
    model_id: str,
    fallback: PhysicsTrace,
) -> tuple[dict[str, Any], str]:
    """
    Intenta mlx_vlm. Si no hay Mac/MLX, falla con mensaje claro.
    Pide JSON estructurado; si el parse falla, mezcla con fallback físico.
    """
    try:
        from mlx_vlm import load, generate
        from mlx_vlm.prompt_utils import apply_chat_template
        from mlx_vlm.utils import load_config
    except ImportError as exc:
        raise SystemExit(
            "mlx-vlm no disponible. En Mac Apple Silicon:\n"
            "  pip install mlx-vlm\n"
            "O usa --demo para grounding desde la física sintética.\n"
            f"Detalle: {exc}"
        ) from exc

    # Pocos frames clave: inicio, mid, cerca de 1er rebote, final
    idxs = sorted({0, len(paths) // 3, len(paths) // 2, max(0, len(paths) - 1)})
    sample = [str(paths[i]) for i in idxs if i < len(paths)]

    prompt = (
        "Describe en español lo que ves en estos frames de un objeto en movimiento. "
        "Si tienes modo think/reasoning, limita el thinking a máximo 2 oraciones y luego "
        "emite el JSON. Responde ÚNICAMENTE con UN objeto JSON (sin markdown) con claves: "
        "objeto, trayectoria, aceleracion_aprox_px_s2, rebotes (lista de enteros frame), "
        "perdida_energia_por_rebote (0-1), nota."
    )

    model, processor = load(model_id)
    config = load_config(model_id)
    formatted = apply_chat_template(processor, config, prompt, num_images=len(sample))
    # mlx-vlm>=0.7: generate(model, processor, prompt, image=..., max_tokens=...)
    # Do NOT pass image paths as positional prompt (breaks as "prompt mistaken for image").
    result = generate(
        model,
        processor,
        formatted,
        image=sample,
        max_tokens=768,
        verbose=False,
    )
    text = result.text if hasattr(result, "text") else (
        result if isinstance(result, str) else str(result)
    )

    try:
        import re

        cleaned = _strip_think_and_extract(text)
        m = re.search(r"\{[\s\S]*\}", cleaned)
        structured = json.loads(m.group(0) if m else cleaned)
        structured["_vlm_parse"] = "ok"
        structured["_vlm_raw_preview"] = text[:240]
    except Exception:
        structured = fallback.to_structured()
        structured["nota_vlm"] = f"Parse falló; se usó traza física. Raw: {text[:400]}"
        structured["_vlm_parse"] = "fallback_physics"

    narrative = _narrative_from_structured(structured)
    narrative += f"\n(Fuente VLM: {model_id})"
    return structured, narrative
