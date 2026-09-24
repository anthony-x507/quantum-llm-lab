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
    """Remove think/thinking blocks; prefer text after last close tag; else JSON span.

    Reuses lab anti-think pattern from examples/run_jev_experiment.py +
    examples/train_lora._strip_thinking (also strips <thinking>).
    """
    import re

    if not text_out:
        return ""
    # Closed think / thinking tags (Qwen3 Thinking + variants)
    cleaned = re.sub(r"<think>[\s\S]*?</think>", "", text_out, flags=re.I)
    cleaned = re.sub(r"<thinking>[\s\S]*?</thinking>", "", cleaned, flags=re.I)
    lower_orig = text_out.lower()
    # Prefer content after last closing tag (even if open tag missing)
    for closer in ("</think>", "</thinking>"):
        if closer in lower_orig:
            idx = lower_orig.rfind(closer)
            cleaned = text_out[idx + len(closer) :]
            break
    else:
        # Unclosed think: keep from first '{' if present
        if ("<think>" in lower_orig or "<thinking>" in lower_orig) and "{" in text_out:
            cleaned = text_out[text_out.find("{") :]
    cleaned = cleaned.strip()
    # Drop common markdown fences around JSON
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s*```\s*$", "", cleaned)
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


_JSON_SCHEMA_KEYS = (
    "objeto, trayectoria, aceleracion_aprox_px_s2, rebotes (lista de enteros frame), "
    "perdida_energia_por_rebote (0-1), nota"
)


def _vlm_prompt_think_then_json() -> str:
    """Phase-1: allow short think, then force JSON (jev-style anti-think cue)."""
    return (
        "Describe en español lo que ves en estos frames de un objeto en movimiento. "
        "Si tienes modo think/reasoning, cierra el thinking YA (máximo 2 oraciones) y "
        "después emite SOLO el JSON. "
        "DEBES responder ÚNICAMENTE con UN objeto JSON que empiece inmediatamente con `{`. "
        "Sin cadena de pensamiento en inglés. Sin markdown. Sin texto antes ni después del JSON. "
        f"Claves requeridas: {_JSON_SCHEMA_KEYS}."
    )


def _vlm_prompt_json_only() -> str:
    """Phase-2: no think; JSON-only recovery when phase-1 burned tokens on prose."""
    return (
        "NO pienses en voz alta. NO uses <think>. NO escribas inglés narrativo. "
        "Answer ONLY JSON. Empieza tu respuesta con el carácter `{` y termina con `}`. "
        "Un único objeto JSON (sin markdown) con claves: "
        f"{_JSON_SCHEMA_KEYS}."
    )


def _mlx_generate_text(model, processor, formatted, sample, max_tokens: int) -> str:
    """Keep generate(model, processor, prompt, image=sample) call shape (mlx-vlm>=0.7)."""
    from mlx_vlm import generate

    result = generate(
        model,
        processor,
        formatted,
        image=sample,
        max_tokens=max_tokens,
        verbose=False,
    )
    return result.text if hasattr(result, "text") else (
        result if isinstance(result, str) else str(result)
    )


def _try_parse_vlm_json(text: str) -> dict | None:
    import re

    cleaned = _strip_think_and_extract(text)
    m = re.search(r"\{[\s\S]*\}", cleaned)
    blob = m.group(0) if m else cleaned
    try:
        data = json.loads(blob)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _ground_with_mlx_vlm(
    paths: list[Path],
    model_id: str,
    fallback: PhysicsTrace,
    *,
    max_tokens: int = 1536,
    json_only_max_tokens: int = 512,
) -> tuple[dict[str, Any], str]:
    """
    Intenta mlx_vlm. Si no hay Mac/MLX, falla con mensaje claro.
    Anti-think (Thinking-4bit): max_tokens≥1536 + strip think + force JSON cue;
    two-phase JSON-only retry if phase-1 burns budget on prose.
    Si el parse falla, mezcla con fallback físico.
    """
    try:
        from mlx_vlm import load
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

    model, processor = load(model_id)
    config = load_config(model_id)

    # Phase 1: short-think + JSON (headroom for Thinking-4bit)
    prompt1 = _vlm_prompt_think_then_json()
    formatted1 = apply_chat_template(
        processor, config, prompt1, num_images=len(sample)
    )
    # mlx-vlm>=0.7: generate(model, processor, prompt, image=..., max_tokens=...)
    # Do NOT pass image paths as positional prompt (breaks as "prompt mistaken for image").
    text = _mlx_generate_text(model, processor, formatted1, sample, max_tokens)
    parsed = _try_parse_vlm_json(text)
    phase = "think_then_json"
    tokens_budget = max_tokens

    # Phase 2: JSON-only recovery (no think allowed)
    if parsed is None:
        prompt2 = _vlm_prompt_json_only()
        formatted2 = apply_chat_template(
            processor, config, prompt2, num_images=len(sample)
        )
        text2 = _mlx_generate_text(
            model, processor, formatted2, sample, json_only_max_tokens
        )
        parsed2 = _try_parse_vlm_json(text2)
        if parsed2 is not None:
            parsed = parsed2
            text = text2
            phase = "json_only_retry"
            tokens_budget = json_only_max_tokens
        else:
            # Keep longer raw for diagnostics; note both attempts
            text = (
                f"[phase1 max_tokens={max_tokens}] {text}\n"
                f"[phase2 max_tokens={json_only_max_tokens}] {text2}"
            )
            phase = "both_failed"
            tokens_budget = max_tokens + json_only_max_tokens

    if parsed is not None:
        structured = parsed
        structured["_vlm_parse"] = "ok"
        structured["_vlm_phase"] = phase
        structured["_vlm_max_tokens"] = tokens_budget
        structured["_vlm_raw_preview"] = text[:240]
    else:
        structured = fallback.to_structured()
        structured["nota_vlm"] = f"Parse falló; se usó traza física. Raw: {text[:400]}"
        structured["_vlm_parse"] = "fallback_physics"
        structured["_vlm_phase"] = phase
        structured["_vlm_max_tokens"] = tokens_budget

    narrative = _narrative_from_structured(structured)
    narrative += f"\n(Fuente VLM: {model_id})"
    return structured, narrative
