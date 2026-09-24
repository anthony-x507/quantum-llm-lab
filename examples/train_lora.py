#!/usr/bin/env python3
"""
Fine-tune LoRA / QLoRA del Qwen3-VL (mlx-vlm) sobre caídas + entrelazamiento + superposición.

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
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "examples") not in sys.path:
    sys.path.insert(0, str(ROOT / "examples"))



def _strip_thinking(text: str) -> str:
    """Remove Qwen3 Thinking blocks before JSON parse (PASO 4)."""
    import re

    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"<thinking>.*?</thinking>", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    return cleaned.strip()


def _circuit_target_from_meta(meta: dict[str, Any]) -> dict[str, Any]:
    """Target toy por dominio: fall | entanglement | superposition."""
    domain = meta.get("domain") or meta.get("train_target_kind") or "fall"
    if isinstance(domain, str) and domain.endswith("_circuit"):
        domain = domain.replace("_circuit", "")
    label = meta.get("label")

    if domain == "entanglement" or meta.get("train_target_kind") in (
        "bell_circuit",
        "product_circuit",
    ):
        entangled = bool(meta.get("entangled", meta.get("train_target_kind") == "bell_circuit"))
        bell = meta.get("bell_state") or "Phi+"
        shape = str(meta.get("shape") or "?")
        seed = int(meta.get("scene_seed") or meta.get("seed") or 0)
        corr = str(meta.get("correlation") or "")
        # Optional scene-gen hint; else deterministic pick from cues.
        tpl = meta.get("ent_template")
        # === ENTANGLED: diversify Bell / CX patterns (distinct gate fingerprints) ===
        # Allowed gates: h,x,y,z,cx,ry. CX required for entangled; forbidden for separable.
        if entangled:
            bell_map = {
                "Phi+": "bell_hcx",
                "Phi-": "bell_xhcx",
                "Psi+": "bell_hxcx",
                "Psi-": "bell_xxhcx",
            }
            pool = [
                "bell_hcx",      # H + CX
                "bell_xhcx",     # X + H + CX
                "bell_hxcx",     # H + X(q1) + CX
                "bell_xxhcx",    # X + H + X(q1) + CX
                "bell_hcxz",     # H + CX + Z
                "bell_yhcx",     # Y + H + CX
                "bell_hcxry",    # H + CX + RY (soft)
            ]
            if not tpl:
                tpl = bell_map.get(str(bell)) or pool[seed % len(pool)]
                # shape cue diversifies further when bell already mapped
                if shape in ("star", "ring") and tpl == "bell_hcx":
                    tpl = "bell_hcxry"
                elif shape in ("triangle",) and tpl == "bell_hcx":
                    tpl = "bell_yhcx"
                elif corr.endswith("_phase") or "phase" in corr:
                    tpl = "bell_hcxz"
            gates_by_tpl = {
                "bell_hcx": [["h", 0], ["cx", 0, 1]],
                "bell_xhcx": [["x", 0], ["h", 0], ["cx", 0, 1]],
                "bell_hxcx": [["h", 0], ["x", 1], ["cx", 0, 1]],
                "bell_xxhcx": [["x", 0], ["h", 0], ["x", 1], ["cx", 0, 1]],
                "bell_hcxz": [["h", 0], ["cx", 0, 1], ["z", 1]],
                "bell_yhcx": [["y", 0], ["h", 0], ["cx", 0, 1]],
                "bell_hcxry": [["h", 0], ["cx", 0, 1], ["ry", 1, 0.4]],
            }
            if tpl not in gates_by_tpl:
                tpl = "bell_hcx"
            return {
                "n_qubits": 2,
                "gates": gates_by_tpl[tpl],
                "domain": "entanglement",
                "label": "entangled",
                "bell_state": bell,
                "template": tpl,
                "nota": (
                    f"Circuito Bell ({bell}/{tpl}): produce entrelazamiento (CX presente); "
                    "la escena visual muestra correlación no-local (no producto separable)."
                ),
            }
        # === SEPARABLE / product: NO CX — diversify product fingerprints ===
        sep_pool = [
            "sep_hh",    # H H
            "sep_xx",    # X X
            "sep_hy",    # H Y
            "sep_ryry",  # RY RY
            "sep_hx",    # H X
            "sep_zz",    # Z Z
            "sep_yh",    # Y H
        ]
        if not tpl:
            tpl = sep_pool[seed % len(sep_pool)]
            if shape in ("ring", "circle") and tpl == "sep_hh":
                tpl = "sep_ryry"
            elif shape in ("star",) and tpl == "sep_hh":
                tpl = "sep_zz"
        gates_by_tpl = {
            "sep_hh": [["h", 0], ["h", 1]],
            "sep_xx": [["x", 0], ["x", 1]],
            "sep_hy": [["h", 0], ["y", 1]],
            "sep_ryry": [["ry", 0, 0.5], ["ry", 1, 0.5]],
            "sep_hx": [["h", 0], ["x", 1]],
            "sep_zz": [["z", 0], ["z", 1]],
            "sep_yh": [["y", 0], ["h", 1]],
        }
        if tpl not in gates_by_tpl:
            tpl = "sep_hh"
        return {
            "n_qubits": 2,
            "gates": gates_by_tpl[tpl],
            "domain": "entanglement",
            "label": "separable",
            "template": tpl,
            "nota": (
                f"Estado producto (separable/{tpl}): sin CX — no hay entrelazamiento; "
                "trayectorias independientes."
            ),
        }

    if domain == "superposition" or meta.get("train_target_kind") in (
        "superposition_circuit",
        "collapse_circuit",
    ):
        collapsed = bool(meta.get("collapsed", meta.get("train_target_kind") == "collapse_circuit"))
        if not collapsed:
            return {
                "n_qubits": 2,
                "gates": [["h", 0]],
                "domain": "superposition",
                "label": "superposed",
                "hypotheses": ["A", "B"],
                "nota": (
                    "Superposición: H en q0 mantiene hipótesis A|B; "
                    "NO medir ni colapsar prematuramente."
                ),
            }
        # collapsed: H then explicit Z-basis "measure" metaphor via X/id choice
        chosen = meta.get("collapsed_to") or "A"
        gates: list[list[Any]] = [["h", 0]]
        if chosen == "B":
            gates.append(["x", 0])  # flip to other hypothesis after "measure"
        return {
            "n_qubits": 2,
            "gates": gates,
            "domain": "superposition",
            "label": "collapsed",
            "collapsed_to": chosen,
            "nota": (
                f"Colapso ya ocurrió → hipótesis {chosen}; "
                "no fingir superposición abierta."
            ),
        }

    # fall / figuras (default) — ≥6 plantillas distintas (PASO 5+ diversity)
    rest = meta.get("restitution")
    if meta.get("energy_loss_per_bounce") is not None:
        loss = float(meta["energy_loss_per_bounce"])
    elif meta.get("perdida_energia_por_rebote") is not None:
        loss = float(meta["perdida_energia_por_rebote"])
    elif rest is not None:
        loss = float(max(0.0, min(1.0, 1.0 - float(rest))))
    else:
        loss = 0.3
    theta = round(0.2 + min(1.0, max(0.0, loss)) * 1.0, 3)
    n_bounce = len(meta.get("bounce_frames") or meta.get("rebotes") or [])
    shape = str(meta.get("shape", "?"))
    surface = str(meta.get("surface") or "")
    cond = str(meta.get("gravity_condition") or meta.get("condition") or "vacuum_freefall")
    multi = bool(meta.get("multi_object"))

    # Deterministic template pick from physics cues (not gold labels).
    # Templates stay inside Jev-allowed gates: h,x,y,z,cx,ry.
    # Each branch must produce a DISTINCT gate-name fingerprint.
    # Order: rare cues first so soft_ry/ramp do not starve drag/irregular/classic.
    if shape in ("star", "irregular_polygon", "ring"):
        # formas irregulares: X+RY (sin CX) — firma distinta
        gates = [["x", 0], ["ry", 0, theta], ["h", 1]]
        tpl = "irregular_xry"
    elif cond == "air_drag" or (n_bounce >= 2 and not multi and surface == "hard_elastic_floor"):
        # drag / rebotes: dissipative chain (no CX) — distinct from wind
        gates = [["h", 0], ["ry", 0, theta], ["x", 1], ["ry", 1, round(theta * 0.6, 3)]]
        tpl = "drag_bounce"
    elif surface in ("ramp",) or (shape == "triangle" and surface not in ("soft_lossy_floor", "hard_elastic_floor")):
        # ramp / wedge: Y then RY (tilt signature)
        gates = [["y", 0], ["ry", 0, theta], ["h", 1]]
        tpl = "ramp_yry"
    elif surface in ("soft_lossy_floor",) or (loss >= 0.55 and n_bounce >= 1):
        # soft floor / high loss: Z phase then dissipative RY
        gates = [["h", 0], ["z", 0], ["ry", 0, theta]]
        tpl = "soft_zry"
    elif cond == "lateral_wind" or multi:
        # wind / multi-object: CX then dual RY
        gates = [["h", 0], ["cx", 0, 1], ["ry", 1, theta], ["ry", 0, round(theta * 0.5, 3)]]
        tpl = "wind_dual_ry"
    elif cond in ("moon_g", "mars_g") or loss < 0.25:
        # low-g / low-loss: soft RY only (energy almost conserved)
        gates = [["h", 0], ["ry", 0, round(theta * 0.4, 3)]]
        tpl = "soft_ry"
    elif shape == "triangle":
        # remaining triangles on flat floors still get ramp tilt signature
        gates = [["y", 0], ["ry", 0, theta], ["h", 1]]
        tpl = "ramp_yry"
    else:
        # vacuum / default: H+CX+RY
        gates = [["h", 0], ["cx", 0, 1], ["ry", 1, theta]]
        tpl = "classic_hcxry"

    return {
        "n_qubits": 2,
        "gates": gates,
        "domain": "fall",
        "label": label or ("fall_multi" if multi else "fall"),
        "shape": shape,
        "template": tpl,
        "nota": (
            f"Firma toy de caída ({shape}/{cond}/{tpl}) con pérdida por rebote (~{loss:.2f}); "
            "energía disipada en el impacto (no se conserva)."
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


def _user_prompt_for_domain(meta: dict[str, Any], summary: dict[str, Any]) -> str:
    """Neutral task instruction + non-gold visual/physics signals only (no scene gold labels)."""
    _ = meta  # domain must be inferred by the model; do not inject gold domain/label
    return (
        "Eres un asistente de circuitos cuánticos. Mira la imagen. Responde SOLO JSON válido "
        "con claves n_qubits, gates, domain, label, nota. "
        "gates ∈ h,x,y,z,cx,ry. "
        "Si hay pérdida por rebote, di que la energía se disipa en el impacto; "
        "no digas que la energía se conserva. "
        f"Escena: {json.dumps(summary, ensure_ascii=False)}"
    )


def build_chat_dataset(rows: list[dict[str, Any]], out_jsonl: Path) -> int:
    """Formato compatible con pipelines VLM: messages + images. Mezcla TODOS los dominios."""
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out_jsonl.open("w", encoding="utf-8") as fh:
        for row in rows:
            meta = row["meta"]
            # PASO 1: user-visible summary keeps visual/physics signals only.
            # Gold keys (domain/label/entangled/...) stay in assistant completion, not user turn.
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
                    "multi_object",
                    "objects",
                )
                if meta.get(k) is not None
            }
            user = _user_prompt_for_domain(meta, summary)
            assistant = json.dumps(row["target"], ensure_ascii=False)
            rec: dict[str, Any] = {
                "messages": [
                    {"role": "user", "content": user},
                    {"role": "assistant", "content": assistant},
                ],
                "scene_id": row["scene_id"],
                "domain": meta.get("domain", "fall"),
                "label": meta.get("label") or row["target"].get("label"),
            }
            if row.get("frame_path"):
                rec["images"] = [row["frame_path"]]
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1
    return n


def _stage_hf_dataset_dir(dataset_path: Path) -> Path:
    """mlx_vlm.lora uses datasets.load_dataset(path); a bare .jsonl fails.
    A directory containing train.jsonl loads correctly.
    """
    dataset_path = Path(dataset_path)
    if dataset_path.is_dir() and (dataset_path / "train.jsonl").exists():
        return dataset_path
    if dataset_path.is_file() and dataset_path.suffix == ".jsonl":
        staged = dataset_path.parent / "lora_dataset_hf"
        staged.mkdir(parents=True, exist_ok=True)
        dest = staged / "train.jsonl"
        if dest.exists() or dest.is_symlink():
            dest.unlink()
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
    out_dir.mkdir(parents=True, exist_ok=True)
    # mlx_vlm.lora → datasets.load_dataset(path); stage HF-friendly train.jsonl dir.
    dataset_for_mlx = _stage_hf_dataset_dir(Path(dataset_path))
    cmd = [
        sys.executable,
        "-m",
        "mlx_vlm.lora",
        "--model-path",
        model,
        "--dataset",
        str(dataset_for_mlx),
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
        "--train-on-completions",
        "--grad-checkpoint",
        "--gradient-accumulation-steps",
        "4",
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
    # Stratify so entanglement is not under-sampled vs fall (ent eval signal).
    if len(rows) <= n_test:
        sample = rows[:]
    else:
        by_dom: dict[str, list] = {"fall": [], "entanglement": [], "superposition": [], "other": []}
        for r in rows:
            d = str((r.get("meta") or {}).get("domain") or "other")
            by_dom.setdefault(d if d in by_dom else "other", []).append(r)
        for v in by_dom.values():
            rng.shuffle(v)
        n_ent = max(2, int(round(n_test * 0.40)))
        n_fall = max(2, int(round(n_test * 0.30)))
        n_sup = max(1, n_test - n_ent - n_fall)
        sample = []
        sample.extend(by_dom["entanglement"][:n_ent])
        sample.extend(by_dom["fall"][:n_fall])
        sample.extend(by_dom["superposition"][:n_sup])
        leftover = (
            by_dom["entanglement"][n_ent:]
            + by_dom["fall"][n_fall:]
            + by_dom["superposition"][n_sup:]
            + by_dom["other"]
        )
        rng.shuffle(leftover)
        while len(sample) < n_test and leftover:
            sample.append(leftover.pop())
        rng.shuffle(sample)
        sample = sample[:n_test]

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
    domain_hits = label_hits = energy_ok_n = energy_loss_n = 0
    gate_combos: set[tuple[str, ...]] = set()
    details: list[dict[str, Any]] = []
    for row in sample:
        proposal: dict[str, Any]
        source = "gold"
        if use_vlm and model is not None:
            # Align with train prompt (PASO1 anti-leak + PASO4 eval parity)
            prompt = _user_prompt_for_domain(row["meta"], {
                k: row["meta"].get(k)
                for k in (
                    "shape", "color", "surface", "gravity_condition",
                    "energy_loss_per_bounce", "perdida_energia_por_rebote",
                    "restitution", "trayectoria", "objeto", "multi_object", "objects",
                )
                if row["meta"].get(k) is not None
            })
            image = row.get("frame_path")
            formatted = apply_chat_template(
                processor, config, prompt, num_images=1 if image else 0
            )
            try:
                result = generate(
                    model, processor, formatted, image=image, max_tokens=512, verbose=False
                )
                raw = result.text if hasattr(result, "text") else str(result)
                text = _strip_thinking(raw)
                if parsear_propuesta is None:
                    raise RuntimeError("parsear_propuesta unavailable")
                proposal = parsear_propuesta(text)
                source = "vlm"
            except Exception as exc:  # noqa: BLE001
                # Do NOT inflate metrics with gold fallback (PASO 4)
                proposal = {"n_qubits": 2, "gates": []}
                source = f"fail:{type(exc).__name__}"
                details.append({
                    "scene_id": row.get("scene_id"),
                    "source": source,
                    "error": str(exc)[:240],
                    "ok_parse": False,
                    "ok_compile": False,
                    "jev": None,
                })
                continue
        else:
            proposal = row["target"]
            source = "gold_dry"

        ok_parse = "gates" in proposal and "n_qubits" in proposal and bool(proposal.get("gates"))
        # gold_dry is only for --dry-metrics style; live VLM path never counts gold as win
        if ok_parse and source != "gold_dry":
            parsed += 1
        elif ok_parse and source == "gold_dry":
            parsed += 1  # explicit dry path only
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

        gold_dom = str((row.get("target") or {}).get("domain") or row["meta"].get("domain") or "")
        gold_lab = str((row.get("target") or {}).get("label") or row["meta"].get("label") or "")
        pred_dom = str(proposal.get("domain") or "")
        pred_lab = str(proposal.get("label") or "")
        ok_domain = bool(pred_dom) and pred_dom == gold_dom
        ok_label = bool(pred_lab) and pred_lab == gold_lab
        if ok_domain:
            domain_hits += 1
        if ok_label:
            label_hits += 1
        # energy consistency: when scene has bounce loss, proposal must not claim perfect conservation
        from jev_arbiter import _scene_has_bounce_energy_loss, _claims_perfect_energy
        has_loss = _scene_has_bounce_energy_loss(scene)
        energy_ok = (not has_loss) or (not _claims_perfect_energy(proposal))
        if energy_ok:
            energy_ok_n += 1
        if has_loss:
            energy_loss_n += 1
        gnames = []
        for g in (proposal.get("gates") or []):
            if isinstance(g, (list, tuple)) and g:
                gnames.append(str(g[0]).lower())
            elif isinstance(g, str):
                gnames.append(g.lower())
        if gnames:
            gate_combos.add(tuple(gnames))

        details.append(
            {
                "scene_id": row["scene_id"],
                "source": source,
                "parse": ok_parse,
                "compile": ok_compile,
                "jev": verdict["verdict"],
                "reason": verdict["reason"],
                "gold_domain": gold_dom,
                "pred_domain": pred_dom,
                "ok_domain": ok_domain,
                "gold_label": gold_lab,
                "pred_label": pred_lab,
                "ok_label": ok_label,
                "energy_ok": energy_ok,
                "gate_names": gnames,
            }
        )

    n = max(1, len(sample))
    # Entanglement-specific accuracy (among gold_domain==entanglement details)
    ent_details = [d for d in details if d.get("gold_domain") == "entanglement"]
    ent_n = len(ent_details)
    ent_domain_acc = (
        sum(1 for d in ent_details if d.get("ok_domain")) / ent_n if ent_n else None
    )
    ent_label_acc = (
        sum(1 for d in ent_details if d.get("ok_label")) / ent_n if ent_n else None
    )
    ent_gate_combos = {
        tuple(d.get("gate_names") or [])
        for d in ent_details
        if d.get("gate_names")
    }
    return {
        "n": len(sample),
        "parse_rate": parsed / n,
        "compile_rate": compiled / n,
        "jev_approve_rate": approved / n,
        "domain_acc": domain_hits / n,
        "label_acc": label_hits / n,
        "energy_ok_rate": energy_ok_n / n,
        "energy_loss_scenes": energy_loss_n,
        "unique_gate_combos": len(gate_combos),
        "ent_n": ent_n,
        "ent_domain_acc": ent_domain_acc,
        "ent_label_acc": ent_label_acc,
        "ent_unique_gate_combos": len(ent_gate_combos),
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
    from collections import Counter
    dom = Counter((r["meta"].get("domain") or "fall") for r in rows)
    print(f"Dataset JSONL: {args.dataset_jsonl} ({n} filas) dominios={dict(dom)}")
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
