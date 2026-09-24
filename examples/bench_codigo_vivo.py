#!/usr/bin/env python3
"""
Three-pillar "código vivo" benchmark: Python executable | Entanglement | Vision.
Base (adapter=null) vs LoRA READ-ONLY. No quantum-advantage claims.

  python examples/bench_codigo_vivo.py \
    --adapter data/lora_adapter \
    --out data/BENCHMARK_CODIGO_VIVO.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "examples"))

from train_lora import (  # noqa: E402
    _circuit_target_from_meta,
    _find_frame,
    _strip_thinking,
    _user_prompt_for_domain,
)

MODEL_DEFAULT = "mlx-community/Qwen3-VL-8B-Thinking-4bit"


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")


def _extract_python(text: str) -> str:
    t = _strip_thinking(text)
    m = re.search(r"```(?:python)?\s*([\s\S]*?)```", t, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # drop leading prose lines until a python-looking line
    lines = t.splitlines()
    start = 0
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith(("import ", "from ", "print(", "def ", "x=", "s=", "n=", "#")) or s == "print(sum(range(1,11)))":
            start = i
            break
    return "\n".join(lines[start:]).strip()


def _run_python_sandbox(code: str, timeout_s: float = 5.0) -> dict[str, Any]:
    """Isolated-ish subprocess: -I, temp cwd, capture stdout/stderr."""
    if not code.strip():
        return {"ok": False, "stdout": "", "stderr": "empty_code", "exit_code": -1, "error": "empty_code"}
    # block obvious network imports by rewriting is too brittle; rely on -I + no env + timeout
    with tempfile.TemporaryDirectory(prefix="qlab_py_") as td:
        script = Path(td) / "main.py"
        script.write_text(code, encoding="utf-8")
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": td, "PYTHONDONTWRITEBYTECODE": "1"}
        try:
            proc = subprocess.run(
                [sys.executable, "-I", str(script)],
                cwd=td,
                capture_output=True,
                text=True,
                timeout=timeout_s,
                env=env,
            )
            return {
                "ok": proc.returncode == 0,
                "stdout": proc.stdout,
                "stderr": (proc.stderr or "")[:500],
                "exit_code": proc.returncode,
                "error": None if proc.returncode == 0 else f"exit_{proc.returncode}",
            }
        except subprocess.TimeoutExpired:
            return {"ok": False, "stdout": "", "stderr": "timeout", "exit_code": -9, "error": "timeout"}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "stdout": "", "stderr": str(exc)[:500], "exit_code": -1, "error": type(exc).__name__}


def _norm_stdout(s: str) -> str:
    return (s or "").replace("\r\n", "\n").strip() + "\n"


def _extract_int_answer(text: str) -> str | None:
    t = _strip_thinking(text)
    # last standalone integer
    nums = re.findall(r"(?m)(?<![\w.])(-?\d+)(?![\w.])", t)
    if not nums:
        return None
    return nums[-1]


def _load_vlm(model_id: str, adapter: str | None):
    from mlx_vlm import load, generate
    from mlx_vlm.prompt_utils import apply_chat_template
    from mlx_vlm.utils import load_config

    kwargs = {"adapter_path": adapter} if adapter else {}
    print(f"[{_now()}] Loading VLM {model_id} adapter={adapter!r}", flush=True)
    model, processor = load(model_id, **kwargs)
    config = load_config(model_id)
    return model, processor, config, generate, apply_chat_template


def _generate_text(model, processor, config, generate, apply_chat_template, prompt: str, image: str | None, max_tokens: int = 512) -> str:
    formatted = apply_chat_template(
        processor, config, prompt, num_images=1 if image else 0
    )
    result = generate(
        model, processor, formatted, image=image, max_tokens=max_tokens, verbose=False
    )
    raw = result.text if hasattr(result, "text") else str(result)
    return raw


def run_pillar_python(model_bundle, items: list[dict], tag: str) -> dict[str, Any]:
    model, processor, config, generate, apply_chat_template = model_bundle
    details = []
    solved = 0
    errors = 0
    for it in items:
        prompt = (
            it["prompt"]
            + "\n\nRules: emit ONLY valid Python 3 source. No markdown fences. No explanation."
        )
        err = None
        raw = code = ""
        run = {"ok": False, "stdout": "", "stderr": "", "exit_code": -1, "error": "not_run"}
        correct = False
        try:
            raw = _generate_text(model, processor, config, generate, apply_chat_template, prompt, None, 512)
            code = _extract_python(raw)
            run = _run_python_sandbox(code, float(it.get("timeout_s", 5)))
            if run.get("error"):
                errors += 1
            correct = _norm_stdout(run.get("stdout", "")) == _norm_stdout(it["expected_stdout"])
            if correct:
                solved += 1
        except Exception as exc:  # noqa: BLE001
            err = f"{type(exc).__name__}: {exc}"
            errors += 1
            traceback.print_exc()
        details.append({
            "id": it["id"],
            "kind": it["kind"],
            "correct": correct,
            "expected": it["expected_stdout"],
            "stdout": (run.get("stdout") or "")[:200],
            "stderr": (run.get("stderr") or "")[:200],
            "exit_code": run.get("exit_code"),
            "exec_error": run.get("error"),
            "gen_error": err,
            "code_preview": (code or "")[:240],
            "raw_preview": _strip_thinking(raw)[:240] if raw else "",
        })
        print(f"  [{tag} python] {it['id']} correct={correct} err={run.get('error') or err}", flush=True)
    n = max(1, len(items))
    return {
        "n": len(items),
        "solved": solved,
        "solve_rate": solved / n,
        "exec_errors": errors,
        "details": details,
    }


def run_pillar_entanglement(
    model_bundle,
    scene_ids: list[str],
    tag: str,
    *,
    circuit_scaffold: bool = True,
    scaffold_polish: bool = False,
) -> dict[str, Any]:
    from jev_arbiter import arbitrate, _scene_has_bounce_energy_loss, _claims_perfect_energy
    from llm_quantum_bridge import ejecutar_circuito, parsear_propuesta

    model, processor, config, generate, apply_chat_template = model_bundle
    details = []
    parse_ok = compile_ok = label_ok = domain_ok = energy_ok_n = circuit_ran = 0
    gate_combos: set[tuple[str, ...]] = set()
    scaffold_wired_n = 0
    scaffold_gt_leaks = 0
    for sid in scene_ids:
        scene_dir = ROOT / "data" / "scenes" / sid
        meta_path = scene_dir / "meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        target = _circuit_target_from_meta(meta)
        frame = _find_frame(scene_dir)
        summary = {
            k: meta.get(k)
            for k in (
                "shape", "color", "surface", "gravity_condition",
                "energy_loss_per_bounce", "perdida_energia_por_rebote",
                "restitution", "trayectoria", "objeto", "multi_object", "objects",
            )
            if meta.get(k) is not None
        }
        prompt = _user_prompt_for_domain(meta, summary)
        # GT-free visual motion cue -> scaffold keywords (never reads meta labels)
        try:
            from circuit_graph_moe_scaffold import visual_motion_cue, motion_cue_prompt_suffix
            _mc = visual_motion_cue(scene_dir)
            _suf = motion_cue_prompt_suffix(str(_mc.get('cue') or 'unknown'))
            if _suf:
                prompt = prompt.rstrip() + '\n' + _suf
        except Exception:
            _mc = {'cue': 'unknown'}
        scaffold_meta: dict[str, Any] | None = None
        if circuit_scaffold:
            try:
                from circuit_graph_adapter.vlm_wire import wire_prompt_for_vlm

                prompt, scaffold_meta = wire_prompt_for_vlm(
                    prompt, "ent", enabled=True, polish=scaffold_polish
                )
                if scaffold_meta.get("wired_to_vlm"):
                    scaffold_wired_n += 1
                if scaffold_meta.get("gt_leak"):
                    scaffold_gt_leaks += 1
            except Exception as _sc_exc:  # noqa: BLE001
                scaffold_meta = {
                    "wired_to_vlm": False,
                    "error": f"{type(_sc_exc).__name__}: {_sc_exc}",
                }
        source = "vlm"
        proposal: dict[str, Any] = {"n_qubits": 2, "gates": []}
        raw = ""
        ok_parse = ok_compile = ok_label = ok_domain = energy_ok = False
        sim = None
        verdict = {"verdict": "RECHAZAR", "reason": "no_run"}
        gnames: list[str] = []
        try:
            raw = _generate_text(
                model, processor, config, generate, apply_chat_template,
                prompt, str(frame) if frame else None, 512,
            )
            text = _strip_thinking(raw)
            proposal = parsear_propuesta(text)
            ok_parse = "gates" in proposal and "n_qubits" in proposal and bool(proposal.get("gates"))
            if ok_parse:
                parse_ok += 1
                try:
                    sim = ejecutar_circuito(proposal)
                    ok_compile = True
                    compile_ok += 1
                    circuit_ran += 1
                except Exception as exc:  # noqa: BLE001
                    ok_compile = False
                    source = f"compile_fail:{type(exc).__name__}"
            scene = dict(meta)
            if "perdida_energia_por_rebote" not in scene and "energy_loss_per_bounce" in scene:
                scene["perdida_energia_por_rebote"] = scene["energy_loss_per_bounce"]
            if "trayectoria" not in scene:
                scene["trayectoria"] = "caída vertical con rebotes"
            verdict = arbitrate(proposal, scene, sim)
            gold_dom = str(target.get("domain") or meta.get("domain") or "")
            gold_lab = str(target.get("label") or meta.get("label") or "")
            pred_dom = str(proposal.get("domain") or "")
            pred_lab = str(proposal.get("label") or "")
            ok_domain = bool(pred_dom) and pred_dom == gold_dom
            ok_label = bool(pred_lab) and pred_lab == gold_lab
            if ok_domain:
                domain_ok += 1
            if ok_label:
                label_ok += 1
            has_loss = _scene_has_bounce_energy_loss(scene)
            energy_ok = (not has_loss) or (not _claims_perfect_energy(proposal))
            if energy_ok:
                energy_ok_n += 1
            for g in (proposal.get("gates") or []):
                if isinstance(g, (list, tuple)) and g:
                    gnames.append(str(g[0]).lower())
                elif isinstance(g, dict) and g.get("name"):
                    gnames.append(str(g["name"]).lower())
                elif isinstance(g, str):
                    gnames.append(g.lower())
            if gnames:
                gate_combos.add(tuple(gnames))
        except Exception as exc:  # noqa: BLE001
            source = f"fail:{type(exc).__name__}"
            verdict = {"verdict": "RECHAZAR", "reason": str(exc)[:200]}
        details.append({
            "scene_id": sid,
            "source": source,
            "parse": ok_parse,
            "compile": ok_compile,
            "circuit_ran": ok_compile,
            "jev": verdict.get("verdict"),
            "reason": verdict.get("reason"),
            "ok_domain": ok_domain,
            "ok_label": ok_label,
            "energy_ok": energy_ok,
            "gate_names": gnames,
            "raw_preview": _strip_thinking(raw)[:200] if raw else "",
            "circuit_graph_scaffold": scaffold_meta,
        })
        print(f"  [{tag} ent] {sid} parse={ok_parse} compile={ok_compile} label={ok_label} energy={energy_ok}", flush=True)
    n = max(1, len(scene_ids))
    return {
        "n": len(scene_ids),
        "parse_ok": parse_ok,
        "compile_ok": compile_ok,
        "circuit_ran": circuit_ran,
        "label_correct": label_ok,
        "domain_correct": domain_ok,
        "energy_ok": energy_ok_n,
        "parse_rate": parse_ok / n,
        "compile_rate": compile_ok / n,
        "label_acc": label_ok / n,
        "domain_acc": domain_ok / n,
        "energy_ok_rate": energy_ok_n / n,
        "unique_gate_combos": len(gate_combos),
        "wired_to_vlm": bool(circuit_scaffold) and scaffold_wired_n == len(scene_ids) and len(scene_ids) > 0,
        "scaffold_wired_n": scaffold_wired_n,
        "scaffold_gt_leaks": scaffold_gt_leaks,
        "channel": "text_scaffold_prefix" if circuit_scaffold else "none",
        "weight_peft_injection": False,
        "details": details,
    }


def run_pillar_vision(model_bundle, items: list[dict], tag: str) -> dict[str, Any]:
    from llm_quantum_bridge import parsear_propuesta

    model, processor, config, generate, apply_chat_template = model_bundle
    details = []
    correct_n = 0
    errors = 0
    for it in items:
        img = str(ROOT / it["image"]) if not Path(it["image"]).is_absolute() else it["image"]
        # paths in json may be relative like data/bench_live/...
        if not Path(img).exists():
            img2 = ROOT / it["image"]
            img = str(img2)
        raw = ""
        pred = None
        correct = False
        err = None
        try:
            raw = _generate_text(
                model, processor, config, generate, apply_chat_template,
                it["prompt"], img, 512,
            )
            text = _strip_thinking(raw)
            if it["match"] == "exact_int":
                pred = _extract_int_answer(text)
                correct = pred is not None and pred == str(it["expected"])
            elif it["match"] == "json_gates_contain":
                try:
                    proposal = parsear_propuesta(text)
                    gnames = []
                    for g in (proposal.get("gates") or []):
                        if isinstance(g, (list, tuple)) and g:
                            gnames.append(str(g[0]).upper())
                        elif isinstance(g, dict) and g.get("name"):
                            gnames.append(str(g["name"]).upper())
                        elif isinstance(g, str):
                            gnames.append(g.upper())
                    need = [g.upper() for g in it.get("expected_gates") or []]
                    nq_ok = int(proposal.get("n_qubits") or 0) == int(it.get("n_qubits") or 0)
                    correct = nq_ok and all(any(n in g for g in gnames) or n in gnames for n in need)
                    # simpler: each expected name appears as substring of some gate name
                    correct = nq_ok and all(
                        any(n.upper() == g.upper() or g.upper().startswith(n.upper()) for g in gnames)
                        for n in need
                    )
                    pred = {"n_qubits": proposal.get("n_qubits"), "gates": gnames}
                except Exception as exc:  # noqa: BLE001
                    err = f"parse:{type(exc).__name__}"
                    errors += 1
            if correct:
                correct_n += 1
        except Exception as exc:  # noqa: BLE001
            err = f"{type(exc).__name__}: {exc}"
            errors += 1
        details.append({
            "id": it["id"],
            "kind": it["kind"],
            "correct": correct,
            "expected": it.get("expected") or it.get("expected_gates"),
            "pred": pred,
            "error": err,
            "raw_preview": _strip_thinking(raw)[:240] if raw else "",
        })
        print(f"  [{tag} vision] {it['id']} correct={correct} pred={pred} err={err}", flush=True)
    n = max(1, len(items))
    return {
        "n": len(items),
        "correct": correct_n,
        "accuracy": correct_n / n,
        "errors": errors,
        "details": details,
    }


def _delta(a: float | int | None, b: float | int | None):
    if a is None or b is None:
        return None
    return b - a


def summarize(base: dict, ft: dict) -> dict:
    return {
        "python": {
            "base_solve_rate": base["python"]["solve_rate"],
            "adapter_solve_rate": ft["python"]["solve_rate"],
            "delta": _delta(base["python"]["solve_rate"], ft["python"]["solve_rate"]),
            "base_solved": f"{base['python']['solved']}/{base['python']['n']}",
            "adapter_solved": f"{ft['python']['solved']}/{ft['python']['n']}",
        },
        "entanglement": {
            "base_label_acc": base["entanglement"]["label_acc"],
            "adapter_label_acc": ft["entanglement"]["label_acc"],
            "delta_label": _delta(base["entanglement"]["label_acc"], ft["entanglement"]["label_acc"]),
            "base_energy_ok_rate": base["entanglement"]["energy_ok_rate"],
            "adapter_energy_ok_rate": ft["entanglement"]["energy_ok_rate"],
            "delta_energy": _delta(base["entanglement"]["energy_ok_rate"], ft["entanglement"]["energy_ok_rate"]),
            "base_compile_rate": base["entanglement"]["compile_rate"],
            "adapter_compile_rate": ft["entanglement"]["compile_rate"],
            "delta_compile": _delta(base["entanglement"]["compile_rate"], ft["entanglement"]["compile_rate"]),
            "base_counts": {
                "label": f"{base['entanglement']['label_correct']}/{base['entanglement']['n']}",
                "energy": f"{base['entanglement']['energy_ok']}/{base['entanglement']['n']}",
                "compile": f"{base['entanglement']['compile_ok']}/{base['entanglement']['n']}",
            },
            "adapter_counts": {
                "label": f"{ft['entanglement']['label_correct']}/{ft['entanglement']['n']}",
                "energy": f"{ft['entanglement']['energy_ok']}/{ft['entanglement']['n']}",
                "compile": f"{ft['entanglement']['compile_ok']}/{ft['entanglement']['n']}",
            },
        },
        "vision": {
            "base_accuracy": base["vision"]["accuracy"],
            "adapter_accuracy": ft["vision"]["accuracy"],
            "delta": _delta(base["vision"]["accuracy"], ft["vision"]["accuracy"]),
            "base_correct": f"{base['vision']['correct']}/{base['vision']['n']}",
            "adapter_correct": f"{ft['vision']['correct']}/{ft['vision']['n']}",
        },
    }


def write_md(report: dict, path: Path) -> None:
    s = report["summary"]
    lines = [
        "# BENCHMARK_CODIGO_VIVO — three pillars",
        "",
        f"**Written:** {report.get('written')}",
        f"**Model:** `{report.get('model')}`",
        f"**Adapter (READ-ONLY):** `{report.get('adapter')}`",
        f"**Base:** adapter=null",
        "",
        "> No quantum-advantage claims. Execution errors reported honestly.",
        "",
        "## Per-pillar table",
        "",
        "| pillar | metric | base | adapter | Δ |",
        "|--------|--------|------|---------|---|",
        f"| 1 Python | solve_rate | {s['python']['base_solve_rate']:.3f} ({s['python']['base_solved']}) | {s['python']['adapter_solve_rate']:.3f} ({s['python']['adapter_solved']}) | {s['python']['delta']:+.3f} |",
        f"| 2 Entanglement | label_acc | {s['entanglement']['base_label_acc']:.3f} ({s['entanglement']['base_counts']['label']}) | {s['entanglement']['adapter_label_acc']:.3f} ({s['entanglement']['adapter_counts']['label']}) | {s['entanglement']['delta_label']:+.3f} |",
        f"| 2 Entanglement | energy_ok_rate | {s['entanglement']['base_energy_ok_rate']:.3f} ({s['entanglement']['base_counts']['energy']}) | {s['entanglement']['adapter_energy_ok_rate']:.3f} ({s['entanglement']['adapter_counts']['energy']}) | {s['entanglement']['delta_energy']:+.3f} |",
        f"| 2 Entanglement | compile_rate (PennyLane ran) | {s['entanglement']['base_compile_rate']:.3f} ({s['entanglement']['base_counts']['compile']}) | {s['entanglement']['adapter_compile_rate']:.3f} ({s['entanglement']['adapter_counts']['compile']}) | {s['entanglement']['delta_compile']:+.3f} |",
        f"| 3 Vision | accuracy | {s['vision']['base_accuracy']:.3f} ({s['vision']['base_correct']}) | {s['vision']['adapter_accuracy']:.3f} ({s['vision']['adapter_correct']}) | {s['vision']['delta']:+.3f} |",
        "",
        "## Notes",
        f"- Python set: `data/bench_live/PYTHON_SET.md` (N={report['base']['python']['n']})",
        f"- Entanglement set: `data/bench_live/ENT_SET.md` (N={report['base']['entanglement']['n']})",
        f"- Vision set: `data/bench_live/VISION_SET.md` (N={report['base']['vision']['n']})",
        "- Strip Thinking; max_tokens≥512; anti-leak prompts on ent pillar.",
        "- Vision note: image→answer often helped more than pure code emission.",
        "",
        "## Paths",
        f"- Mac: `{path}`",
        "- Box copy: `/workspace/quantum-night/BENCHMARK_CODIGO_VIVO.md`",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--model", default=MODEL_DEFAULT)
    p.add_argument("--adapter", type=Path, default=ROOT / "data" / "lora_adapter")
    p.add_argument("--out", type=Path, default=ROOT / "data" / "BENCHMARK_CODIGO_VIVO.json")
    p.add_argument("--skip-python", action="store_true")
    p.add_argument("--skip-ent", action="store_true")
    p.add_argument("--skip-vision", action="store_true")
    args = p.parse_args()

    py_items = json.loads((ROOT / "data/bench_live/python_items.json").read_text())["items"]
    ent_items = json.loads((ROOT / "data/bench_live/ent_items.json").read_text())
    vis_items = json.loads((ROOT / "data/bench_live/vision_items.json").read_text())["items"]
    # fix relative image paths
    for it in vis_items:
        ip = Path(it["image"])
        if not ip.is_absolute():
            it["image"] = str((ROOT / ip).resolve()) if not ip.exists() else str(ip.resolve())
            if not Path(it["image"]).exists():
                it["image"] = str((ROOT / "data/bench_live/vision_items" / Path(ip).name).resolve())

    adapter_path = args.adapter
    if not (adapter_path / "adapters.safetensors").exists():
        alt = ROOT / "data/lora_adapter_frozen_rebalance_20260924-041300"
        if (alt / "adapters.safetensors").exists():
            print(f"[warn] {adapter_path} missing; using frozen archive {alt}", flush=True)
            adapter_path = alt
        else:
            print(f"[error] no adapter at {adapter_path}", file=sys.stderr)
            return 1

    # Resolve vision paths relative to ROOT
    for it in vis_items:
        cand = Path(it["image"])
        if not cand.exists():
            for c in [
                ROOT / it["image"],
                ROOT / "data/bench_live/vision_items" / Path(str(it["image"])).name,
            ]:
                if c.exists():
                    it["image"] = str(c)
                    break

    def empty_py():
        return {"n": 0, "solved": 0, "solve_rate": 0.0, "exec_errors": 0, "details": []}

    def empty_ent():
        return {
            "n": 0, "parse_ok": 0, "compile_ok": 0, "circuit_ran": 0,
            "label_correct": 0, "domain_correct": 0, "energy_ok": 0,
            "parse_rate": 0.0, "compile_rate": 0.0, "label_acc": 0.0,
            "domain_acc": 0.0, "energy_ok_rate": 0.0, "unique_gate_combos": 0,
            "details": [],
        }

    def empty_vis():
        return {"n": 0, "correct": 0, "accuracy": 0.0, "errors": 0, "details": []}

    def run_all(adapter: str | None, tag: str) -> dict:
        bundle = _load_vlm(args.model, adapter)
        out = {
            "python": empty_py() if args.skip_python else run_pillar_python(bundle, py_items, tag),
            "entanglement": empty_ent() if args.skip_ent else run_pillar_entanglement(bundle, ent_items["scene_ids"], tag),
            "vision": empty_vis() if args.skip_vision else run_pillar_vision(bundle, vis_items, tag),
        }
        # free memory hint
        del bundle
        return out

    t0 = time.time()
    print("=== BASE (adapter=null) ===", flush=True)
    base = run_all(None, "base")
    print("=== ADAPTER (READ-ONLY LoRA) ===", flush=True)
    ft = run_all(str(adapter_path), "adapter")

    report = {
        "written": _now(),
        "elapsed_s": round(time.time() - t0, 1),
        "model": args.model,
        "adapter": str(adapter_path),
        "adapter_null_for_base": True,
        "claims": "No quantum-advantage claims. Usability / executable-code metrics only.",
        "sets": {
            "python": "data/bench_live/PYTHON_SET.md",
            "entanglement": "data/bench_live/ENT_SET.md",
            "vision": "data/bench_live/VISION_SET.md",
            "balanced_n30_queued": "data/balanced_eval_set_n30.json",
        },
        "base": base,
        "adapter_run": ft,
        "summary": summarize(base, ft),
    }
    # alias key finetuned for familiarity
    report["finetuned"] = ft

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path = args.out.with_suffix(".md")
    write_md(report, md_path)
    print(f"Wrote {args.out}", flush=True)
    print(f"Wrote {md_path}", flush=True)
    print(json.dumps(report["summary"], indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
