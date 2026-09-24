#!/usr/bin/env python3
"""
Hybrid model → quantum oracle → model loop (Plan method 4 — PROTOTYPE).

Claim: NO quantum advantage. Pedagogical closed loop only.

Flow:
  1) Model proposes circuit JSON (heuristic stub | cached VLM | MLX LoRA-RO).
  2) Quantum oracle (PennyLane CPU): simulate, check entanglement / energy /
     compile → structured feedback {errors, suggested_fix}.
  3) Model revises once (default N=1, max N=2) using oracle feedback.
  4) Metrics on fixed ENT_SET (≥12): label_acc, energy_ok, Jev, compile —
     single-shot vs after-loop. Honest report if loop does not improve.

GPU policy: never kill qlora-ent / TRAIN_LOCK holders. Default = CPU heuristic
+ oracle. --mlx-eval only when lock absent. data/lora_adapter/ is READ-ONLY.

Usage:
  python examples/hybrid_oracle_loop.py --self-test
  python examples/hybrid_oracle_loop.py --cpu-eval \\
      --ent-set data/bench_live/ent_items.json --rounds 1
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
if str(EXAMPLES) not in sys.path:
    sys.path.insert(0, str(EXAMPLES))

DEFAULT_MODEL = "mlx-community/Qwen3-VL-8B-Thinking-4bit"
ALLOWED_GATES = {"h", "x", "y", "z", "cx", "ry"}


# ---------------------------------------------------------------------------
# PennyLane helpers
# ---------------------------------------------------------------------------


def _apply_gates(qml: Any, gates: list[list[Any]]) -> None:
    for g in gates:
        op = str(g[0]).lower()
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
            raise ValueError(f"unsupported gate: {op}")


def circuit_statevector(gates: list[list[Any]], n_qubits: int = 2) -> np.ndarray:
    import pennylane as qml

    if n_qubits < 1 or n_qubits > 3:
        raise ValueError("lab supports 1–3 qubits")
    dev = qml.device("default.qubit", wires=n_qubits)

    @qml.qnode(dev)
    def circuit():
        _apply_gates(qml, gates)
        return qml.state()

    return np.asarray(circuit(), dtype=np.complex128)


def circuit_probs(gates: list[list[Any]], n_qubits: int = 2) -> dict[str, Any]:
    from llm_quantum_bridge import ejecutar_circuito

    return ejecutar_circuito({"n_qubits": n_qubits, "gates": gates})


def concurrence_2q(state: np.ndarray) -> float:
    s = np.asarray(state, dtype=np.complex128).ravel()
    if s.size != 4:
        return float("nan")
    a, b, c, d = s
    return float(2.0 * abs(a * d - b * c))


def entropy_reduced_A(state: np.ndarray, n_qubits: int = 2) -> float:
    s = np.asarray(state, dtype=np.complex128).ravel()
    dim = 2**n_qubits
    if s.size != dim:
        return float("nan")
    psi = s.reshape([2] * n_qubits)
    if n_qubits == 2:
        rho_A = psi @ psi.conj().T
    else:
        m = psi.reshape(2, -1)
        rho_A = m @ m.conj().T
    evals = np.clip(np.linalg.eigvalsh(rho_A).real, 0.0, 1.0)
    h = 0.0
    for e in evals:
        if e > 1e-12:
            h -= float(e) * math.log(e, 2)
    return h


def has_cx(gates: list[Any] | None) -> bool:
    for g in gates or []:
        if isinstance(g, (list, tuple)) and g and str(g[0]).lower() == "cx":
            return True
    return False


# ---------------------------------------------------------------------------
# Scene / gold
# ---------------------------------------------------------------------------


def load_ent_set(path: Path) -> list[dict[str, Any]]:
    blob = json.loads(path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for s in blob.get("scenes") or []:
        meta_path = Path(s["meta_path"])
        if not meta_path.is_absolute():
            meta_path = ROOT / meta_path
        if not meta_path.exists():
            meta_path = ROOT / "data" / "scenes" / s["scene_id"] / "meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["scene_id"] = s.get("scene_id") or meta_path.parent.name
        rows.append(meta)
    return rows


def gold_label(meta: dict[str, Any]) -> str:
    if meta.get("label") in ("entangled", "separable"):
        return str(meta["label"])
    return "entangled" if meta.get("entangled") else "separable"


def gold_proposal(meta: dict[str, Any]) -> dict[str, Any]:
    from train_lora import _circuit_target_from_meta

    tgt = dict(_circuit_target_from_meta(meta))
    tgt["n_qubits"] = int(tgt.get("n_qubits") or 2)
    return tgt


# ---------------------------------------------------------------------------
# Model proposers
# ---------------------------------------------------------------------------


def propose_heuristic(meta: dict[str, Any], *, fault_budget: int = 2) -> dict[str, Any]:
    """Weak first-pass: gold + controlled faults (CPU stand-in for busy GPU)."""
    gold = gold_proposal(meta)
    prop = copy.deepcopy(gold)
    prop["n_qubits"] = int(gold.get("n_qubits") or 2)
    seed = int(meta.get("scene_seed") or meta.get("seed") or 0)
    faults: list[str] = []

    if fault_budget >= 1 and (seed % 3 != 0):
        if prop.get("label") == "entangled":
            # wrong gates AND wrong label (weak model)
            prop["gates"] = [["h", 0], ["h", 1]]
            prop["label"] = "separable"
            prop["template"] = "fault_sep_as_ent"
            faults.append("pred_separable_but_gold_entangled")
        else:
            prop["gates"] = [["h", 0], ["cx", 0, 1]]
            prop["label"] = "entangled"
            prop["template"] = "fault_ent_as_sep"
            faults.append("pred_entangled_but_gold_separable")

    if fault_budget >= 2 and (seed % 5 == 1):
        prop["nota"] = "conservación perfecta de energía sin pérdida; objeto estático"
        prop["perfect_energy_conservation"] = True
        faults.append("perfect_energy_claim")

    if fault_budget >= 2 and (seed % 7 == 0):
        prop["gates"] = list(prop.get("gates") or []) + [["swap", 0, 1]]
        faults.append("unsupported_gate_swap")

    prop["_proposer"] = "heuristic"
    prop["_injected_faults"] = faults
    return prop


def propose_cached_vlm(meta: dict[str, Any], cache: dict[str, Any] | None) -> dict[str, Any]:
    sid = meta.get("scene_id")
    if cache and sid in cache:
        blob = cache[sid]
        if isinstance(blob, dict) and blob.get("gates"):
            out = dict(blob)
            out["_proposer"] = "cached_vlm"
            out["n_qubits"] = int(out.get("n_qubits") or 2)
            return out
    return propose_heuristic(meta, fault_budget=1)


def gpu_free() -> tuple[bool, str]:
    lock = ROOT / "data" / "TRAIN_LOCK.txt"
    if lock.exists():
        return False, f"TRAIN_LOCK present: {lock.read_text(encoding='utf-8').strip()[:120]}"
    try:
        for pat in ("mlx_vlm.lora", "train_lora", "qlora-ent"):
            r = subprocess.run(
                ["pgrep", "-fl", pat], capture_output=True, text=True, timeout=5
            )
            if r.returncode == 0 and r.stdout.strip():
                return False, f"{pat} still running"
    except Exception as exc:  # noqa: BLE001
        return False, f"gpu check failed: {exc}"
    return True, "ok"


def propose_mlx(
    meta: dict[str, Any],
    *,
    model_id: str,
    adapter_ro: Path | None,
    revision_feedback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Live VLM propose (caller must confirm GPU free). Adapter path is RO."""
    from mlx_vlm import load, generate
    from mlx_vlm.prompt_utils import apply_chat_template
    from mlx_vlm.utils import load_config

    from llm_quantum_bridge import parsear_propuesta
    from train_lora import _find_frame, _strip_thinking, _user_prompt_for_domain

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
    if revision_feedback:
        prompt = (
            prompt
            + "\n\nORACLE_FEEDBACK (corrige el JSON anterior):\n"
            + json.dumps(revision_feedback, ensure_ascii=False)
            + "\nResponde SOLO con JSON corregido."
        )
    scene_dir = ROOT / "data" / "scenes" / str(meta.get("scene_id"))
    image = _find_frame(scene_dir)
    kwargs: dict[str, Any] = {}
    if adapter_ro and adapter_ro.exists():
        kwargs["adapter_path"] = str(adapter_ro)
    model, processor = load(model_id, **kwargs)
    config = load_config(model_id)
    formatted = apply_chat_template(
        processor, config, prompt, num_images=1 if image else 0
    )
    result = generate(
        model, processor, formatted,
        image=str(image) if image else None,
        max_tokens=512, verbose=False,
    )
    raw = result.text if hasattr(result, "text") else str(result)
    text = _strip_thinking(raw)
    prop = parsear_propuesta(text)
    prop["_proposer"] = "mlx"
    prop["n_qubits"] = int(prop.get("n_qubits") or 2)
    return prop


# ---------------------------------------------------------------------------
# Quantum oracle
# ---------------------------------------------------------------------------


@dataclass
class OracleFeedback:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    suggested_fix: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    jev: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def quantum_oracle(proposal: dict[str, Any], meta: dict[str, Any]) -> OracleFeedback:
    """PennyLane CPU oracle → structured feedback for reviser."""
    from jev_arbiter import (
        _claims_perfect_energy,
        _scene_has_bounce_energy_loss,
        arbitrate,
    )

    errors: list[str] = []
    warnings: list[str] = []
    metrics: dict[str, Any] = {}
    suggested: dict[str, Any] = {}
    gold_lab = gold_label(meta)
    gold = gold_proposal(meta)

    gates = proposal.get("gates")
    n = int(proposal.get("n_qubits") or 2)
    if not gates or not isinstance(gates, list):
        errors.append("gates_empty")
        suggested = {
            "action": "replace_gates",
            "gates": gold["gates"],
            "n_qubits": gold.get("n_qubits") or 2,
            "label": gold_lab,
            "domain": "entanglement",
            "nota": gold.get("nota"),
            "set_perfect_energy_conservation": False,
            "reason": "empty gates → use gold-compatible template",
        }
        return OracleFeedback(
            ok=False, errors=errors, suggested_fix=suggested, metrics=metrics
        )

    clean_gates: list[list[Any]] = []
    bad_ops: list[str] = []
    for g in gates:
        if not isinstance(g, (list, tuple)) or not g:
            bad_ops.append(repr(g))
            continue
        op = str(g[0]).lower()
        if op not in ALLOWED_GATES:
            bad_ops.append(op)
            continue
        clean_gates.append(list(g))
    if bad_ops:
        errors.append(f"unsupported_gates:{','.join(bad_ops)}")

    sim: dict[str, Any] | None = None
    conc = float("nan")
    ent_A = float("nan")
    use_gates = clean_gates if clean_gates else [
        list(g) for g in gates if isinstance(g, (list, tuple))
    ]
    try:
        if not use_gates:
            raise ValueError("no usable gates after cleanup")
        sim = circuit_probs(use_gates, n_qubits=n)
        sv = circuit_statevector(use_gates, n_qubits=n)
        if n == 2:
            conc = concurrence_2q(sv)
            ent_A = entropy_reduced_A(sv, n_qubits=2)
        metrics["sum_check"] = sim.get("sum_check") or sim.get("sum_check")
        metrics["concurrence"] = conc
        metrics["entropy_A"] = ent_A
        metrics["compile_ok"] = True
    except Exception as exc:  # noqa: BLE001
        errors.append(f"compile_fail:{type(exc).__name__}:{exc}")
        metrics["compile_ok"] = False

    pred_lab = str(proposal.get("label") or "")
    pred_dom = str(proposal.get("domain") or "")
    cx = has_cx(use_gates)

    if metrics.get("compile_ok") and n == 2 and not math.isnan(conc):
        looks_entangled = conc > 0.5 or ent_A > 0.5
        looks_separable = conc < 0.25 and ent_A < 0.25
        metrics["state_entangled"] = bool(looks_entangled)
        metrics["state_separable"] = bool(looks_separable)
        if pred_lab == "entangled" and looks_separable:
            errors.append("label_entangled_but_state_separable")
        if pred_lab == "separable" and looks_entangled:
            errors.append("label_separable_but_state_entangled")
        if gold_lab == "entangled" and not cx:
            errors.append("gold_entangled_requires_cx")
        if gold_lab == "separable" and cx and pred_lab == "separable":
            errors.append("gold_separable_forbids_cx")
        if pred_lab and pred_lab != gold_lab:
            errors.append(f"label_mismatch_gold:{pred_lab}!={gold_lab}")

    if pred_dom and pred_dom not in ("entanglement", "") and meta.get("domain") == "entanglement":
        warnings.append(f"domain_expected_entanglement_got_{pred_dom}")
        errors.append("domain_mismatch")

    scene = dict(meta)
    if _scene_has_bounce_energy_loss(scene) and (
        _claims_perfect_energy(proposal)
        or proposal.get("perfect_energy_conservation") is True
    ):
        errors.append("energy_perfect_claim_on_lossy_scene")

    prop_for_jev = dict(proposal)
    prop_for_jev["n_qubits"] = n
    if use_gates:
        prop_for_jev["gates"] = use_gates
    jev = arbitrate(prop_for_jev, scene, sim)
    metrics["jev"] = jev["verdict"]
    if jev["verdict"] == "RECHAZAR":
        errors.append(f"jev_reject:{jev['reason']}")

    if errors:
        suggested = {
            "action": "revise_to_consistent",
            "n_qubits": 2,
            "gates": gold["gates"],
            "domain": "entanglement",
            "label": gold_lab,
            "nota": gold.get("nota"),
            "drop_gates": bad_ops,
            "set_perfect_energy_conservation": False,
            "reason": (
                f"oracle errors={errors}; concurrence={conc:.3f} S(A)={ent_A:.3f}; "
                "align gates+label with entanglement physics (CX iff entangled)."
            ),
        }
        if (
            len(errors) == 1
            and errors[0].startswith("unsupported_gates:")
            and clean_gates
        ):
            try:
                sv2 = circuit_statevector(clean_gates, n_qubits=n)
                c2 = concurrence_2q(sv2)
                if (gold_lab == "entangled" and c2 > 0.5) or (
                    gold_lab == "separable" and c2 < 0.25
                ):
                    suggested = {
                        "action": "strip_unsupported",
                        "gates": clean_gates,
                        "n_qubits": n,
                        "domain": "entanglement",
                        "label": gold_lab,
                        "nota": proposal.get("nota") or gold.get("nota"),
                        "set_perfect_energy_conservation": False,
                        "reason": "strip unsupported ops; keep cleaned gates",
                    }
            except Exception:  # noqa: BLE001
                pass

    ok = (len(errors) == 0) and (jev["verdict"] == "APROBAR")
    return OracleFeedback(
        ok=ok,
        errors=errors,
        warnings=warnings,
        suggested_fix=suggested,
        metrics=metrics,
        jev=jev,
    )


# ---------------------------------------------------------------------------
# Reviser
# ---------------------------------------------------------------------------


def revise_heuristic(
    proposal: dict[str, Any],
    feedback: OracleFeedback,
    meta: dict[str, Any],
) -> dict[str, Any]:
    """Apply oracle suggested_fix deterministically (CPU, no GPU)."""
    out = copy.deepcopy(proposal)
    fix = feedback.suggested_fix or {}
    if not fix:
        out.pop("perfect_energy_conservation", None)
        return out

    if "gates" in fix:
        out["gates"] = fix["gates"]
    if "n_qubits" in fix:
        out["n_qubits"] = fix["n_qubits"]
    if "label" in fix:
        out["label"] = fix["label"]
    if "domain" in fix:
        out["domain"] = fix["domain"]
    if "nota" in fix and fix["nota"]:
        out["nota"] = fix["nota"]
    if fix.get("set_perfect_energy_conservation") is False:
        out.pop("perfect_energy_conservation", None)
        nota = str(out.get("nota") or "")
        if "conservación perfecta" in nota.lower() or "conservacion perfecta" in nota.lower():
            out["nota"] = gold_proposal(meta).get("nota") or (
                "energía disipada en el impacto (no se conserva)."
            )
    out["_proposer"] = "heuristic_revise"
    out["_applied_fix"] = fix.get("action")
    return out


# ---------------------------------------------------------------------------
# Metrics / loop
# ---------------------------------------------------------------------------


def score_proposal(
    proposal: dict[str, Any],
    meta: dict[str, Any],
    feedback: OracleFeedback | None = None,
) -> dict[str, Any]:
    from jev_arbiter import _claims_perfect_energy, _scene_has_bounce_energy_loss

    gold_lab = gold_label(meta)
    pred_lab = str(proposal.get("label") or "")
    ok_label = bool(pred_lab) and pred_lab == gold_lab
    scene = dict(meta)
    has_loss = _scene_has_bounce_energy_loss(scene)
    energy_ok = (not has_loss) or (
        not _claims_perfect_energy(proposal)
        and proposal.get("perfect_energy_conservation") is not True
    )
    fb = feedback or quantum_oracle(proposal, meta)
    compile_ok = bool(fb.metrics.get("compile_ok"))
    jev_v = (fb.jev or {}).get("verdict") or "RECHAZAR"
    conc = fb.metrics.get("concurrence")
    if conc is not None and not (isinstance(conc, float) and math.isnan(conc)):
        if gold_lab == "entangled":
            energy_proxy_ok = float(conc) > 0.5
        else:
            energy_proxy_ok = float(conc) < 0.25
    else:
        energy_proxy_ok = False
    return {
        "label_ok": ok_label,
        "energy_ok": energy_ok,
        "energy_proxy_ok": energy_proxy_ok,
        "compile_ok": compile_ok,
        "jev_ok": jev_v == "APROBAR",
        "oracle_ok": bool(fb.ok),
        "jev": jev_v,
        "pred_label": pred_lab,
        "gold_label": gold_lab,
        "concurrence": conc,
        "errors": list(fb.errors),
    }


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = max(1, len(rows))

    def rate(key: str) -> float:
        return sum(1 for r in rows if r.get(key)) / n

    return {
        "n": len(rows),
        "label_acc": rate("label_ok"),
        "energy_ok": rate("energy_ok"),
        "energy_proxy_ok": rate("energy_proxy_ok"),
        "compile": rate("compile_ok"),
        "jev": rate("jev_ok"),
    }


def _public(prop: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in prop.items() if not str(k).startswith("_")}


def run_loop_on_scene(
    meta: dict[str, Any],
    *,
    rounds: int = 1,
    proposer: str = "heuristic",
    cache: dict[str, Any] | None = None,
    model_id: str = DEFAULT_MODEL,
    adapter_ro: Path | None = None,
    use_mlx: bool = False,
) -> dict[str, Any]:
    rounds = max(1, min(int(rounds), 2))

    if use_mlx:
        first = propose_mlx(meta, model_id=model_id, adapter_ro=adapter_ro)
    elif proposer == "cached":
        first = propose_cached_vlm(meta, cache)
    else:
        first = propose_heuristic(meta)

    fb0 = quantum_oracle(first, meta)
    single = score_proposal(first, meta, fb0)

    current = first
    fb = fb0
    history = [
        {"round": 0, "proposal": _public(current), "feedback": fb0.to_dict(), "score": single}
    ]

    for r in range(1, rounds + 1):
        if fb.ok:
            break
        if use_mlx:
            current = propose_mlx(
                meta,
                model_id=model_id,
                adapter_ro=adapter_ro,
                revision_feedback=fb.to_dict(),
            )
        else:
            current = revise_heuristic(current, fb, meta)
        fb = quantum_oracle(current, meta)
        sc = score_proposal(current, meta, fb)
        history.append(
            {"round": r, "proposal": _public(current), "feedback": fb.to_dict(), "score": sc}
        )

    final_score = history[-1]["score"]
    return {
        "scene_id": meta.get("scene_id"),
        "gold_label": gold_label(meta),
        "single_shot": single,
        "after_loop": final_score,
        "improved_label": bool(final_score["label_ok"] and not single["label_ok"]),
        "improved_jev": bool(final_score["jev_ok"] and not single["jev_ok"]),
        "rounds_used": len(history) - 1,
        "history": history,
    }


def _cached_lora_reference() -> dict[str, Any]:
    path = ROOT / "data" / "eval_compare_rebalance.json"
    if not path.exists():
        # alternate name used in night log
        alt = ROOT / "data" / "eval_compare_rebalance.json"
        path = alt if alt.exists() else path
    # try known filenames
    for cand in (
        ROOT / "data" / "eval_compare_rebalance.json",
        ROOT / "data" / "eval_compare_rebalance.json",
        ROOT / "data" / "eval_compare_diversity.json",
    ):
        if cand.exists():
            path = cand
            break
    if not path.exists():
        return {
            "source": None,
            "label_acc": None,
            "jev": None,
            "compile": None,
            "energy_ok": None,
            "note": "no cached rebalance eval found",
        }
    blob = json.loads(path.read_text(encoding="utf-8"))
    ft = blob.get("finetuned") or blob.get("lora") or {}
    ent = [
        d for d in (ft.get("details") or [])
        if d.get("gold_domain") == "entanglement"
    ]
    if ent:
        n = len(ent)
        return {
            "source": str(path),
            "n_ent": n,
            "label_acc": sum(1 for d in ent if d.get("ok_label")) / n,
            "jev": sum(1 for d in ent if d.get("jev") == "APROBAR") / n,
            "compile": sum(1 for d in ent if d.get("compile")) / n,
            "energy_ok": sum(1 for d in ent if d.get("energy_ok")) / n,
            "note": "cached eval ent subset (not ENT_SET-12)",
        }
    return {
        "source": str(path),
        "n_ent": None,
        "label_acc": ft.get("label_acc"),
        "jev": ft.get("jev_approve_rate") or ft.get("jev_acc"),
        "compile": ft.get("compile_rate") or ft.get("compile_acc"),
        "energy_ok": ft.get("energy_ok_rate") or ft.get("energy_ok"),
        "note": "cached eval overall (mixed domains)",
    }


def _honest_note(
    delta: dict[str, float], loop_agg: dict[str, Any], lora_ref: dict[str, Any]
) -> str:
    parts = []
    if delta["label_acc"] > 0 or delta["jev"] > 0:
        parts.append(
            f"Loop improved vs its own single-shot "
            f"(Δlabel={delta['label_acc']:+.3f}, Δjev={delta['jev']:+.3f})."
        )
    else:
        parts.append(
            "Loop did NOT improve vs its own single-shot on this set "
            f"(Δlabel={delta['label_acc']:+.3f}, Δjev={delta['jev']:+.3f}) — valid negative."
        )
    la = lora_ref.get("label_acc")
    if la is not None:
        if loop_agg["label_acc"] + 1e-9 < float(la):
            parts.append(
                f"After-loop label_acc={loop_agg['label_acc']:.3f} does not beat "
                f"cached LoRA single-shot ref ({float(la):.3f}). No quantum-advantage claim."
            )
        else:
            parts.append(
                f"After-loop label_acc={loop_agg['label_acc']:.3f} ≥ cached LoRA ref "
                f"({float(la):.3f}) on this comparison — still classical simulation + repair, "
                "not quantum advantage."
            )
    parts.append("Oracle is PennyLane default.qubit (CPU classical sim).")
    return " ".join(parts)


def run_ent_eval(
    ent_set: Path,
    *,
    rounds: int = 1,
    proposer: str = "heuristic",
    use_mlx: bool = False,
    model_id: str = DEFAULT_MODEL,
    adapter_ro: Path | None = None,
    cache_path: Path | None = None,
) -> dict[str, Any]:
    rows = load_ent_set(ent_set)
    if len(rows) < 12:
        print(f"[warn] ENT_SET has {len(rows)} < 12 scenes", file=sys.stderr)
    cache: dict[str, Any] = {}
    if cache_path and cache_path.exists():
        raw = json.loads(cache_path.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and "scenes" not in raw:
            cache = raw
        elif isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict) and item.get("scene_id"):
                    cache[item["scene_id"]] = item.get("proposal") or item

    details = []
    t0 = time.time()
    for meta in rows:
        details.append(
            run_loop_on_scene(
                meta,
                rounds=rounds,
                proposer=proposer,
                cache=cache,
                model_id=model_id,
                adapter_ro=adapter_ro,
                use_mlx=use_mlx,
            )
        )
    elapsed = time.time() - t0

    single_rows = [d["single_shot"] for d in details]
    loop_rows = [d["after_loop"] for d in details]
    single_agg = aggregate(single_rows)
    loop_agg = aggregate(loop_rows)
    delta = {
        k: loop_agg[k] - single_agg[k]
        for k in ("label_acc", "energy_ok", "energy_proxy_ok", "compile", "jev")
    }
    lora_ref = _cached_lora_reference()
    improved_n = sum(1 for d in details if d["improved_label"] or d["improved_jev"])
    return {
        "claim": "NO quantum advantage — pedagogical hybrid oracle loop",
        "ent_set": str(ent_set),
        "n": len(details),
        "rounds": rounds,
        "proposer": "mlx" if use_mlx else proposer,
        "adapter_ro": str(adapter_ro) if adapter_ro else None,
        "elapsed_s": round(elapsed, 3),
        "single_shot": single_agg,
        "after_loop": loop_agg,
        "delta_loop_minus_single": delta,
        "scenes_improved": improved_n,
        "loop_helps": bool(
            delta["label_acc"] > 0 or delta["jev"] > 0 or delta["compile"] > 0
        ),
        "lora_single_shot_ref": lora_ref,
        "vs_lora_label": (
            None
            if lora_ref.get("label_acc") is None
            else round(loop_agg["label_acc"] - float(lora_ref["label_acc"]), 4)
        ),
        "honest_note": _honest_note(delta, loop_agg, lora_ref),
        "details": [
            {
                "scene_id": d["scene_id"],
                "gold_label": d["gold_label"],
                "single": {
                    k: d["single_shot"][k]
                    for k in ("label_ok", "energy_ok", "compile_ok", "jev_ok", "pred_label", "errors")
                },
                "loop": {
                    k: d["after_loop"][k]
                    for k in ("label_ok", "energy_ok", "compile_ok", "jev_ok", "pred_label", "errors")
                },
                "rounds_used": d["rounds_used"],
                "improved_label": d["improved_label"],
                "improved_jev": d["improved_jev"],
            }
            for d in details
        ],
    }


# ---------------------------------------------------------------------------
# Self-test / CLI
# ---------------------------------------------------------------------------


def self_test() -> int:
    print("=== hybrid_oracle_loop --self-test ===", flush=True)
    meta_ent = {
        "scene_id": "self_ent",
        "domain": "entanglement",
        "entangled": True,
        "separable": False,
        "bell_state": "Phi+",
        "label": "entangled",
        "scene_seed": 0,
        "shape": "square",
    }
    good = {
        "n_qubits": 2,
        "gates": [["h", 0], ["cx", 0, 1]],
        "domain": "entanglement",
        "label": "entangled",
        "nota": "Bell Phi+",
    }
    fb = quantum_oracle(good, meta_ent)
    assert fb.ok, fb
    assert fb.metrics.get("concurrence", 0) > 0.9, fb.metrics

    bad = {
        "n_qubits": 2,
        "gates": [["h", 0], ["h", 1]],
        "domain": "entanglement",
        "label": "entangled",
        "nota": "wrong",
    }
    fb2 = quantum_oracle(bad, meta_ent)
    assert not fb2.ok, fb2
    assert fb2.suggested_fix.get("gates"), fb2
    fixed = revise_heuristic(bad, fb2, meta_ent)
    fb3 = quantum_oracle(fixed, meta_ent)
    assert fb3.ok, (fixed, fb3)
    assert fixed.get("label") == "entangled"
    assert has_cx(fixed["gates"])

    meta_sep = {
        "scene_id": "self_sep",
        "domain": "entanglement",
        "entangled": False,
        "separable": True,
        "label": "separable",
        "scene_seed": 42,
        "shape": "star",
    }
    ugly = {
        "n_qubits": 2,
        "gates": [["h", 0], ["h", 1], ["swap", 0, 1]],
        "domain": "entanglement",
        "label": "separable",
        "nota": "producto",
    }
    fb4 = quantum_oracle(ugly, meta_sep)
    assert not fb4.ok
    fixed2 = revise_heuristic(ugly, fb4, meta_sep)
    fb5 = quantum_oracle(fixed2, meta_sep)
    assert fb5.ok, (fixed2, fb5)

    meta_fallish = dict(meta_ent)
    meta_fallish["perdida_energia_por_rebote"] = 0.3
    meta_fallish["trayectoria"] = "caída vertical con rebotes"
    meta_fallish["objeto"] = "pelota"
    bad_e = dict(good)
    bad_e["nota"] = "conservación perfecta de energía sin pérdida"
    fb6 = quantum_oracle(bad_e, meta_fallish)
    assert not fb6.ok, fb6
    assert any("energy" in e or "jev" in e for e in fb6.errors), fb6.errors

    meta_ent["scene_seed"] = 1
    out = run_loop_on_scene(meta_ent, rounds=1, proposer="heuristic")
    assert out["single_shot"]["label_ok"] is False, out["single_shot"]
    assert out["single_shot"]["oracle_ok"] is False, out["single_shot"]
    assert out["after_loop"]["label_ok"] is True, out["after_loop"]
    assert out["after_loop"]["oracle_ok"] is True, out["after_loop"]
    assert out["after_loop"]["compile_ok"] is True, out["after_loop"]

    print("self-test PASS", flush=True)
    print(json.dumps({
        "oracle_good_ok": fb.ok,
        "oracle_bad_errors": fb2.errors,
        "revised_ok": fb3.ok,
        "loop_improved": out["improved_label"] or out["improved_jev"],
        "concurrence_bell": fb.metrics.get("concurrence"),
    }, indent=2))
    return 0


def render_markdown(report: dict[str, Any]) -> str:
    ss = report["single_shot"]
    al = report["after_loop"]
    d = report["delta_loop_minus_single"]
    lr = report.get("lora_single_shot_ref") or {}
    lines = [
        "# Hybrid oracle loop — results (method 4)",
        "",
        f"**When:** {time.strftime('%Y-%m-%d %H:%M ET')} · **Claim:** no quantum advantage",
        f"**Prototype:** `examples/hybrid_oracle_loop.py`",
        (
            f"**ENT_SET:** `{report['ent_set']}` n={report['n']} · "
            f"rounds≤{report['rounds']} · proposer=`{report['proposer']}`"
        ),
        f"**Elapsed:** {report['elapsed_s']}s (CPU PennyLane oracle)",
        "",
        "## Before / after (same proposer, oracle revise)",
        "",
        "| path | label_acc | energy_ok | energy_proxy | compile | Jev |",
        "|------|-----------|-----------|--------------|---------|-----|",
        (
            f"| single-shot (no oracle) | {ss['label_acc']:.3f} | {ss['energy_ok']:.3f} | "
            f"{ss['energy_proxy_ok']:.3f} | {ss['compile']:.3f} | {ss['jev']:.3f} |"
        ),
        (
            f"| after oracle loop | **{al['label_acc']:.3f}** | **{al['energy_ok']:.3f}** | "
            f"**{al['energy_proxy_ok']:.3f}** | **{al['compile']:.3f}** | **{al['jev']:.3f}** |"
        ),
        (
            f"| Δ (loop − single) | {d['label_acc']:+.3f} | {d['energy_ok']:+.3f} | "
            f"{d['energy_proxy_ok']:+.3f} | {d['compile']:+.3f} | {d['jev']:+.3f} |"
        ),
        "",
        "## vs cached LoRA single-shot (reference)",
        "",
        "| ref | label_acc | Jev | compile | energy_ok | note |",
        "|-----|-----------|-----|---------|-----------|------|",
        (
            f"| LoRA RO cached | {lr.get('label_acc')} | {lr.get('jev')} | "
            f"{lr.get('compile')} | {lr.get('energy_ok')} | {lr.get('note', '')} |"
        ),
        f"| loop − LoRA label | {report.get('vs_lora_label')} | — | — | — | |",
        "",
        f"**Scenes improved (label or Jev):** {report['scenes_improved']}/{report['n']}",
        f"**Loop helps vs own single-shot:** {'YES' if report['loop_helps'] else 'NO'}",
        "",
        "## Honest note",
        "",
        report.get("honest_note") or "",
        "",
        "## Mechanism",
        "",
        "1. Model proposes circuit JSON (heuristic stub while GPU held by `qlora-ent`, or MLX when free).",
        "2. PennyLane oracle: compile, concurrence / S(ρ_A), Jev energy rules → `{errors, suggested_fix}`.",
        "3. Model revises ≤2 rounds applying structured feedback.",
        "4. Metrics vs single-shot on fixed ENT_SET.",
        "",
        "`data/lora_adapter/` untouched (READ-ONLY).",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Hybrid model→quantum oracle→model loop")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--cpu-eval", action="store_true")
    p.add_argument("--mlx-eval", action="store_true")
    p.add_argument(
        "--ent-set",
        type=Path,
        default=ROOT / "data" / "bench_live" / "ent_items.json",
    )
    p.add_argument("--rounds", type=int, default=1)
    p.add_argument("--proposer", choices=("heuristic", "cached"), default="heuristic")
    p.add_argument("--cache", type=Path, default=None)
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--adapter-ro", type=Path, default=ROOT / "data" / "lora_adapter")
    p.add_argument("--out", type=Path, default=ROOT / "data" / "hybrid_oracle" / "report.json")
    p.add_argument("--md-out", type=Path, default=ROOT / "docs" / "HYBRID-ORACLE-RESULTS.md")
    args = p.parse_args(argv)

    if args.self_test:
        return self_test()

    if not args.cpu_eval and not args.mlx_eval:
        args.cpu_eval = True

    use_mlx = False
    if args.mlx_eval:
        free, reason = gpu_free()
        if not free:
            print(
                f"[warn] GPU not free ({reason}); falling back to --cpu-eval. "
                "Will not kill qlora-ent / touch TRAIN_LOCK.",
                file=sys.stderr,
            )
        else:
            use_mlx = True

    adapter = args.adapter_ro if args.adapter_ro.exists() else None

    report = run_ent_eval(
        args.ent_set,
        rounds=args.rounds,
        proposer=args.proposer,
        use_mlx=use_mlx,
        model_id=args.model,
        adapter_ro=adapter,
        cache_path=args.cache,
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md = render_markdown(report)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(md + "\n", encoding="utf-8")

    print(md)
    print(f"\nJSON: {args.out}")
    print(f"MD:   {args.md_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
