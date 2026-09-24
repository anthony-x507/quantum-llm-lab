#!/usr/bin/env python3
"""First Jev experiment cycle: 5 synthetic scenes → 8B proposes → sim → arbitrate → JSONL."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
EXAMPLES = Path(__file__).resolve().parent
if str(EXAMPLES) not in sys.path:
    sys.path.insert(0, str(EXAMPLES))

MODEL_ID = "mlx-community/Qwen3-VL-8B-Thinking-4bit"
FALLBACK_PROPOSAL = {
    "n_qubits": 2,
    "gates": [["h", 0], ["cx", 0, 1], ["ry", 1, 0.4]],
    "nota": "Demo fallback: Bell-like + RY atenuación (parse falló).",
    "proposal_source": "fallback",
}


def _load_bridge():
    import importlib.util

    bridge_path = EXAMPLES / "llm_quantum_bridge.py"
    spec = importlib.util.spec_from_file_location("llm_quantum_bridge", bridge_path)
    bridge = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(bridge)
    return bridge


def _load_jev():
    import importlib.util

    path = EXAMPLES / "jev_arbiter.py"
    spec = importlib.util.spec_from_file_location("jev_arbiter", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def make_scenes(n: int = 5, out_dir: Path | None = None, seed: int = 42) -> list[dict[str, Any]]:
    """Generate n scenes via synthetic_physics_dataset (preferred) or synthetic_fall."""
    out = out_dir or (ROOT / "data" / "experiment_scenes")
    out.mkdir(parents=True, exist_ok=True)
    scenes: list[dict[str, Any]] = []

    try:
        from synthetic_physics_dataset import generate_dataset

        generate_dataset(n_scenes=n, out_dir=out, seed=seed, frames_per_scene=20)
        for i in range(n):
            meta_path = out / f"scene_{i:04d}" / "meta.json"
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            summary = (
                f"{meta.get('color')} {meta.get('shape')} {meta.get('size')} "
                f"material={meta.get('material')} surface={meta.get('surface')} "
                f"g={meta.get('gravity_condition')} restitution={meta.get('restitution')} "
                f"multi={meta.get('multi_object')}"
            )
            # Ensure energy-loss signal for Jev rule 2
            scene = dict(meta)
            scene["scene_id"] = f"scene_{i:04d}"
            scene["scene_summary"] = summary
            scene["trayectoria"] = "caída con rebotes (dataset sintético)"
            scene["objeto"] = f"{meta.get('shape')} {meta.get('color')}"
            if meta.get("restitution") is not None:
                loss = max(0.0, 1.0 - float(meta["restitution"]))
                scene["perdida_energia_por_rebote"] = round(loss, 4)
            frame0 = out / f"scene_{i:04d}" / "frame_0000.png"
            scene["frame_path"] = str(frame0) if frame0.exists() else None
            scenes.append(scene)
        return scenes
    except Exception as exc:
        print(f"[warn] synthetic_physics_dataset falló ({exc}); usando synthetic_fall", file=sys.stderr)

    from vision.synthetic_fall import generate_falling_ball_frames

    for i in range(n):
        sdir = out / f"fall_{i:04d}"
        restitution = 0.55 + 0.08 * i
        paths, trace = generate_falling_ball_frames(
            sdir, n_frames=24, restitution=restitution
        )
        structured = trace.to_structured()
        structured["scene_id"] = f"fall_{i:04d}"
        structured["scene_summary"] = (
            f"pelota caída restitution={restitution:.2f} "
            f"loss={structured.get('perdida_energia_por_rebote')}"
        )
        structured["frame_path"] = str(paths[0]) if paths else None
        structured["restitution"] = restitution
        scenes.append(structured)
    return scenes


_VLM_CACHE: dict[str, Any] = {}


def _get_vlm(model_id: str):
    if model_id in _VLM_CACHE:
        return _VLM_CACHE[model_id]
    from mlx_vlm import load
    from mlx_vlm.utils import load_config

    print(f"Cargando VLM {model_id} …", flush=True)
    model, processor = load(model_id)
    config = load_config(model_id)
    _VLM_CACHE[model_id] = (model, processor, config)
    return _VLM_CACHE[model_id]


def _strip_think_and_extract(text_out: str) -> str:
    """Remove <think> blocks; if unclosed, take after last </think>; else keep JSON span."""
    if not text_out:
        return ""
    # Closed think tags
    cleaned = re.sub(r"<think>[\s\S]*?</think>", "", text_out, flags=re.I)
    # If a closing tag remains / was present: take text after last </think>
    lower_orig = text_out.lower()
    if "</think>" in lower_orig:
        idx = lower_orig.rfind("</think>")
        cleaned = text_out[idx + len("</think>"):]
    elif "<think>" in lower_orig and "{" in text_out:
        # Unclosed think: keep from first '{' onward
        cleaned = text_out[text_out.find("{"):]
    cleaned = cleaned.strip()
    # If still no clear JSON start, try from first '{'
    if "{" in cleaned:
        start = cleaned.find("{")
        # Brace-balanced extract for preview / parse helper
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


def _fallback_for_scene(scene: dict[str, Any]) -> dict[str, Any]:
    """Slightly vary fallback gates by scene hash so logs aren't identical."""
    fb = dict(FALLBACK_PROPOSAL)
    sid = str(scene.get("scene_id") or scene.get("scene_summary") or "x")
    h = int(hashlib.md5(sid.encode("utf-8")).hexdigest()[:8], 16)
    theta = round(0.30 + (h % 50) / 100.0, 3)  # 0.30 .. 0.79
    # keep structure; vary RY angle and optional extra Z on q0
    gates = [["h", 0], ["cx", 0, 1], ["ry", 1, theta]]
    if h % 2 == 1:
        gates.append(["z", 0])
    fb["gates"] = gates
    fb["nota"] = f"Demo fallback scene-hash (theta={theta}; parse falló)."
    fb["proposal_source"] = "fallback"
    return fb


def propose_circuit_vlm(
    scene: dict[str, Any],
    model_id: str,
    *,
    max_tokens: int = 1024,
) -> dict[str, Any]:
    """Ask Qwen3-VL for a circuit JSON; fallback once on parse failure."""
    from mlx_vlm import generate
    from mlx_vlm.prompt_utils import apply_chat_template

    model, processor, config = _get_vlm(model_id)
    summary = scene.get("scene_summary") or json.dumps(
        {k: scene.get(k) for k in (
            "objeto", "trayectoria", "perdida_energia_por_rebote",
            "shape", "color", "surface", "restitution", "gravity_condition",
        ) if scene.get(k) is not None},
        ensure_ascii=False,
    )
    prompt = (
        "DEBES responder ÚNICAMENTE con UN objeto JSON que empiece inmediatamente con `{`. "
        "Sin cadena de pensamiento en inglés. Sin markdown. Sin texto antes ni después del JSON. "
        "Si tienes modo think/reasoning, limita el thinking a máximo 2 oraciones y luego emite el JSON. "
        "Eres un asistente de circuitos cuánticos. Dada esta escena de física visual, "
        "propón un circuito de 2 qubits cuya estructura toy firme (1) caída/aceleración y "
        "(2) pérdida de energía en rebotes (usa RY para atenuación; NO afirmes conservación "
        "perfecta). Responde SOLO JSON válido: "
        '{"n_qubits":2,"gates":[["h",0],["cx",0,1],["ry",1,0.4]],"nota":"..."}. '
        "Puertas: h,x,y,z,cx,ry.\n\n"
        f"Escena: {summary}"
    )
    image = None
    fp = scene.get("frame_path")
    if fp and Path(fp).exists():
        image = fp

    num_images = 1 if image else 0
    formatted = apply_chat_template(processor, config, prompt, num_images=num_images)
    # mlx-vlm>=0.7: generate(model, processor, prompt, image=..., max_tokens=...)
    result = generate(
        model,
        processor,
        formatted,
        image=image,
        max_tokens=max_tokens,
        verbose=False,
    )
    text_out = result.text if hasattr(result, "text") else (result if isinstance(result, str) else str(result))
    raw_full = text_out
    text_out = _strip_think_and_extract(text_out)
    try:
        from llm_quantum_bridge import parsear_propuesta

        data = parsear_propuesta(text_out)
        data["proposal_source"] = "mlx_vlm"
        data["raw_preview"] = (raw_full or "")[:400]
        return data
    except Exception as exc:
        print(f"[warn] JSON parse falló ({exc}); usando fallback", file=sys.stderr)
        fb = _fallback_for_scene(scene)
        fb["raw_preview"] = (raw_full or "")[:400]
        fb["parse_error"] = str(exc)[:200]
        return fb



def run_experiment(
    *,
    n: int = 5,
    model_id: str = MODEL_ID,
    log_path: Path | None = None,
    skip_vlm: bool = False,
    max_tokens: int = 1024,
) -> Path:
    bridge = _load_bridge()
    jev = _load_jev()
    log_path = log_path or (ROOT / "data" / "experiment_log.jsonl")
    log_path.parent.mkdir(parents=True, exist_ok=True)

    scenes = make_scenes(n=n)
    # truncate log for clean first cycle
    if log_path.exists():
        log_path.write_text("", encoding="utf-8")

    first_verdict = None
    for scene in scenes:
        t0 = time.perf_counter()
        scene_id = scene.get("scene_id") or "unknown"
        summary = scene.get("scene_summary") or scene_id
        print(f"\n=== {scene_id}: {summary} ===", flush=True)

        if skip_vlm:
            proposal = _fallback_for_scene(scene)
            proposal["proposal_source"] = "fallback_skip_vlm"
        else:
            try:
                proposal = propose_circuit_vlm(scene, model_id, max_tokens=max_tokens)
            except Exception as exc:
                print(f"[warn] VLM falló ({exc}); fallback", file=sys.stderr)
                proposal = _fallback_for_scene(scene)
                proposal["vlm_error"] = str(exc)[:300]

        sim_result: dict[str, Any] | None
        try:
            sim_result = bridge.ejecutar_circuito(
                {"n_qubits": proposal.get("n_qubits", 2), "gates": proposal.get("gates") or []}
            )
        except Exception as exc:
            sim_result = {"error": str(exc), "sum_check": None, "probabilities": {}}

        decision = jev.arbitrate(proposal, scene, sim_result if "error" not in (sim_result or {}) else None)
        elapsed = time.perf_counter() - t0
        ts = datetime.now().astimezone().isoformat(timespec="seconds")

        record = {
            "scene_id": scene_id,
            "scene_summary": summary,
            "proposal": proposal,
            "jev_verdict": decision["verdict"],
            "jev_reason": decision["reason"],
            "sim_result": sim_result,
            "elapsed_sec": round(elapsed, 3),
            "model_id": model_id,
            "ts": ts,
        }
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"Jev: {decision['verdict']} — {decision['reason']}", flush=True)
        if first_verdict is None:
            first_verdict = decision

    print(f"\nLog: {log_path.resolve()} ({n} líneas)")
    if first_verdict:
        print(f"Primer veredicto: {first_verdict['verdict']} — {first_verdict['reason']}")
    return log_path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Run 5-scene Jev experiment cycle")
    p.add_argument("--n", type=int, default=5)
    p.add_argument("--model", default=MODEL_ID)
    p.add_argument("--log", default=str(ROOT / "data" / "experiment_log.jsonl"))
    p.add_argument("--skip-vlm", action="store_true", help="Use fallback proposals only")
    p.add_argument("--max-tokens", type=int, default=1024, help="VLM max_tokens (Thinking needs headroom)")
    args = p.parse_args(argv)
    run_experiment(
        n=args.n,
        model_id=args.model,
        log_path=Path(args.log),
        skip_vlm=args.skip_vlm,
        max_tokens=args.max_tokens,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
