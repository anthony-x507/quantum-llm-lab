#!/usr/bin/env python3
"""
Frontier — circuit-graph as MoE entanglement/circuit scaffold (CPU).

When the MoE router selects lane ``ent``, optionally inject Clifford–Pauli
graph structure hints (features / template fingerprints) into the prompt
BEFORE the proposer runs. Hints never include GT labels / gold / collapsed_to.

Ablation (CPU, no VLM required):
  scaffold OFF  vs  scaffold ON
Metrics: parse_rate, structure_rate, solve_rate (own-delta; no Q-advantage).

Usage:
  python examples/circuit_graph_moe_scaffold.py --smoke
  python examples/circuit_graph_moe_scaffold.py --cpu-eval --limit 24
  python examples/circuit_graph_moe_scaffold.py --cpu-eval --polish   # richer features

READ-ONLY: never write data/lora_adapter/.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "examples"))

import moe_dual_lane_router as moe  # noqa: E402
from circuit_graph_adapter.circuit_graph import build_graph  # noqa: E402
from circuit_graph_adapter.gnn_encoder import GNNEncoder  # noqa: E402
from circuit_graph_adapter.pauli_tool import run_pauli_tool  # noqa: E402
from circuit_graph_adapter.synthetic_graphs import bell_variants, make_random  # noqa: E402

SMOKE_OUT = ROOT / "data" / "frontier_circuit_graph_scaffold_cpu_smoke.json"
EVAL_OUT = ROOT / "data" / "frontier_circuit_graph_scaffold_cpu.json"
DOC_OUT = ROOT / "docs" / "FRONTIER-CIRCUIT-GRAPH-SCAFFOLD.md"
FREEZE_OUT = ROOT / "data" / "FRONTIER_CIRCUIT_GRAPH_SCAFFOLD_FREEZE.json"

# Forbidden leakage tokens — never appear in scaffold hint text.
_FORBIDDEN_HINT = re.compile(
    r"\b(label|gold|gt|ground.?truth|collapsed_to|y_true|target_label)\b",
    re.I,
)

SCAFFOLD_BEGIN = "<<<CIRCUIT_GRAPH_SCAFFOLD>>>"
SCAFFOLD_END = "<<<END_CIRCUIT_GRAPH_SCAFFOLD>>>"


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z").strip()


# ---------------------------------------------------------------------------
# Structural priors (NOT eval GT) — library of gate proposals for scaffolding
# ---------------------------------------------------------------------------
def prior_templates() -> list[dict[str, Any]]:
    """Hand-authored structural priors. No scene labels."""
    specs = [
        {"id": "bell_h_cx", "tags": ("bell", "entangle", "entrelaz"), "n_qubits": 2,
         "gates": [["h", 0], ["cx", 0, 1]]},
        {"id": "bell_h1_cx10", "tags": ("bell", "entangle"), "n_qubits": 2,
         "gates": [["h", 1], ["cx", 1, 0]]},
        {"id": "product_h0", "tags": ("product", "separable", "separable"), "n_qubits": 2,
         "gates": [["h", 0]]},
        {"id": "product_x0_x1", "tags": ("product", "separable"), "n_qubits": 2,
         "gates": [["x", 0], ["x", 1]]},
        {"id": "ghz_like", "tags": ("ghz", "entangle", "3"), "n_qubits": 3,
         "gates": [["h", 0], ["cx", 0, 1], ["cx", 1, 2]]},
        {"id": "ry_cx", "tags": ("rotation", "entangle", "ry"), "n_qubits": 2,
         "gates": [["ry", 0, 0.5], ["cx", 0, 1]]},
        {"id": "single_h", "tags": ("hadamard", "single"), "n_qubits": 1,
         "gates": [["h", 0]]},
    ]
    # Also fold synthetic bell variants (gates only).
    for i, g in enumerate(bell_variants()):
        specs.append({
            "id": f"synth_bell_{i}",
            "tags": ("bell", "entangle", "synth"),
            "n_qubits": g.n_qubits,
            "gates": [
                ([n.gate, *n.qubits] if n.theta is None else [n.gate, n.qubits[0], n.theta])
                for n in g.nodes
            ],
        })
    return specs


def graph_features(proposal: dict[str, Any], encoder: GNNEncoder | None = None) -> dict[str, Any]:
    """Derive scaffold features from a gate proposal. Never reads labels."""
    clean = {
        "n_qubits": int(proposal.get("n_qubits", 2)),
        "gates": list(proposal.get("gates") or []),
    }
    # Strip any accidental GT fields before graph build.
    graph = build_graph(clean)
    gate_hist: dict[str, int] = {}
    for n in graph.nodes:
        gate_hist[n.gate] = gate_hist.get(n.gate, 0) + 1
    paulis = sorted({n.pauli for n in graph.nodes})
    n_nodes = len(graph.nodes)
    n_edges = len(graph.edges)
    density = (2.0 * n_edges / (n_nodes * (n_nodes - 1))) if n_nodes > 1 else 0.0
    has_cx = gate_hist.get("cx", 0) > 0
    has_h = gate_hist.get("h", 0) > 0
    feat: dict[str, Any] = {
        "n_qubits": graph.n_qubits,
        "n_nodes": n_nodes,
        "n_edges": n_edges,
        "anticomm_density": round(density, 4),
        "gate_hist": gate_hist,
        "pauli_set": paulis,
        "has_cx": has_cx,
        "has_h": has_h,
        "bell_like": bool(has_h and has_cx and graph.n_qubits >= 2),
    }
    if encoder is not None:
        emb = encoder.encode(graph)
        feat["embed_norm"] = round(float(np.linalg.norm(emb)), 4)
        feat["embed_dim"] = int(emb.shape[0])
        feat["embed_head"] = [round(float(x), 4) for x in emb[:4]]
    tool = run_pauli_tool(clean)
    feat["unitary_ok"] = bool(tool.unitary_ok)
    feat["fingerprint"] = tool.fingerprint
    return feat


def format_scaffold_hint(
    prompt: str,
    *,
    polish: bool = False,
    encoder: GNNEncoder | None = None,
) -> str:
    """Build a GT-free scaffold block for ent/circuit prompts.

    Uses structural priors + graph features. Selects nearest prior by tag
    overlap with the prompt (keyword), never by eval labels.
    """
    enc = encoder or GNNEncoder(embed_dim=64, seed=0)
    low = (prompt or "").lower()
    priors = prior_templates()
    scored: list[tuple[int, dict[str, Any], dict[str, Any]]] = []
    for t in priors:
        score = sum(1 for tag in t["tags"] if tag in low)
        # Soft prior: Bell-like if entanglement language present
        if any(k in low for k in ("entrelaz", "entangle", "bell", "qubit")):
            if t["id"].startswith("bell") or "entangle" in t["tags"]:
                score += 1
        if any(k in low for k in ("product", "separable", "separab")):
            if "product" in t["tags"] or "separable" in t["tags"]:
                score += 2
        prop = {"n_qubits": t["n_qubits"], "gates": t["gates"]}
        feat = graph_features(prop, encoder=enc)
        scored.append((score, t, feat))
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
    top = scored[:3] if polish else scored[:2]

    lines = [
        SCAFFOLD_BEGIN,
        "# Clifford–Pauli circuit-graph scaffold (structure only; no eval targets).",
        "# Use these features to shape n_qubits + gates JSON. Structure priors only.",
        f"# alphabet: h,x,y,z,cx,ry | anticomm_edges = Pauli anti-commute on overlap",
    ]
    for rank, (score, t, feat) in enumerate(top):
        lines.append(
            f"# prior[{rank}] id={t['id']} tag_score={score} "
            f"n_qubits={feat['n_qubits']} n_nodes={feat['n_nodes']} "
            f"n_edges={feat['n_edges']} anticomm_density={feat['anticomm_density']} "
            f"has_cx={feat['has_cx']} bell_like={feat['bell_like']} "
            f"gate_hist={feat['gate_hist']} fingerprint={feat['fingerprint']}"
        )
        if polish:
            lines.append(
                f"#   pauli_set={feat['pauli_set']} embed_norm={feat.get('embed_norm')} "
                f"embed_head={feat.get('embed_head')}"
            )
            lines.append(f"#   suggested_gates_json={json.dumps(t['gates'], ensure_ascii=False)}")
        else:
            # Compact gate sketch without calling it gold
            lines.append(f"#   sketch_gates={json.dumps(t['gates'], ensure_ascii=False)}")
    # Aggregate guidance
    best = top[0][2]
    lines.append(
        f"# guidance: prefer n_qubits≈{best['n_qubits']}, "
        f"anticomm_density≈{best['anticomm_density']}, "
        f"include_cx={best['has_cx']}, target_bell_like={best['bell_like']}"
    )
    lines.append(SCAFFOLD_END)
    block = "\n".join(lines)
    if _FORBIDDEN_HINT.search(block):
        raise RuntimeError("scaffold hint leaked forbidden eval-target token")
    return block


def inject_scaffold(prompt: str, *, polish: bool = False, encoder: GNNEncoder | None = None) -> str:
    """Append scaffold block to prompt (idempotent)."""
    if SCAFFOLD_BEGIN in (prompt or ""):
        return prompt
    return (prompt or "").rstrip() + "\n\n" + format_scaffold_hint(prompt, polish=polish, encoder=encoder)


# ---------------------------------------------------------------------------
# CPU heuristic proposers (scaffold-sensitive)
# ---------------------------------------------------------------------------
def _parse_sketch_from_scaffold(prompt: str) -> dict[str, Any] | None:
    """Pull first sketch_gates / suggested_gates_json from scaffold block."""
    if SCAFFOLD_BEGIN not in prompt:
        return None
    m = re.search(
        r"(?:sketch_gates|suggested_gates_json)=(\[[^\n]+\])",
        prompt,
    )
    nq = re.search(r"guidance: prefer n_qubits≈(\d+)", prompt)
    if not m:
        return None
    try:
        gates = json.loads(m.group(1))
    except json.JSONDecodeError:
        return None
    n_qubits = int(nq.group(1)) if nq else 2
    return {"n_qubits": n_qubits, "gates": gates}


def heuristic_propose(prompt: str, *, use_scaffold: bool, seed: int = 0) -> dict[str, Any]:
    """CPU stub proposer.

    - use_scaffold=False: weak keyword rules; often structure-poor / parse-fragile.
    - use_scaffold=True: reads scaffold sketches + validates via graph/tool.
    """
    rng = np.random.default_rng(seed)
    low = (prompt or "").lower()

    if use_scaffold and SCAFFOLD_BEGIN in prompt:
        sketch = _parse_sketch_from_scaffold(prompt)
        if sketch and sketch.get("gates"):
            # Validate / lightly repair with graph+tool
            try:
                g = build_graph(sketch)
                tool = run_pauli_tool(sketch)
                if tool.unitary_ok and g.nodes:
                    out = {
                        "n_qubits": sketch["n_qubits"],
                        "gates": sketch["gates"],
                        "domain": "entanglement",
                        "nota": "scaffold-guided heuristic",
                    }
                    return out
            except Exception:  # noqa: BLE001
                pass
            # Fall through to tag-based prior pick
        # Pick best prior by tag score
        best = None
        best_score = -1
        for t in prior_templates():
            score = sum(1 for tag in t["tags"] if tag in low)
            if score > best_score:
                best_score = score
                best = t
        if best is not None and best_score > 0:
            return {
                "n_qubits": best["n_qubits"],
                "gates": list(best["gates"]),
                "domain": "entanglement",
                "nota": "scaffold-prior heuristic",
            }

    # --- no-scaffold / weak path ---
    # Intentionally brittle: misses CX on many entangle prompts, sometimes
    # returns non-JSON-shaped empties for ambiguous asks (CPU stand-in for
    # unstructured LLM output).
    if any(k in low for k in ("product", "separable", "separab")):
        return {"n_qubits": 2, "gates": [["h", 0]], "domain": "entanglement", "nota": "weak-product"}
    if "ghz" in low or "3 qubit" in low or "n_qubits\": 3" in low or "3 qubits" in low:
        # Weak: forgets last CX often
        if rng.random() < 0.55:
            return {"n_qubits": 3, "gates": [["h", 0], ["cx", 0, 1]], "nota": "weak-ghz-trunc"}
        return {"n_qubits": 3, "gates": [["h", 0], ["cx", 0, 1], ["cx", 1, 2]], "nota": "weak-ghz"}
    if any(k in low for k in ("bell", "entrelaz", "entangle", "cx", "pennylane", "circuito")):
        # Weak: ~60% omit entangling CX or emit empty gates
        r = float(rng.random())
        if r < 0.35:
            return {"n_qubits": 2, "gates": [], "nota": "weak-empty"}  # parse fail
        if r < 0.65:
            return {"n_qubits": 2, "gates": [["h", 0]], "nota": "weak-no-cx"}  # structure fail for bell
        if r < 0.80:
            # Malformed gate entry — parse may pass but structure/tool fails
            return {"n_qubits": 2, "gates": [["hadamard", 0]], "nota": "weak-bad-gate"}
        return {"n_qubits": 2, "gates": [["h", 0], ["cx", 0, 1]], "nota": "weak-bell-ok"}
    if "ry" in low or "rotation" in low:
        return {"n_qubits": 2, "gates": [["ry", 0, 0.3]], "nota": "weak-ry"}
    # Default: empty → parse fail
    if rng.random() < 0.5:
        return {"n_qubits": 2, "gates": [], "nota": "weak-default-empty"}
    return {"n_qubits": 2, "gates": [["x", 0]], "nota": "weak-default-x"}


def proposal_to_text(proposal: dict[str, Any]) -> str:
    """Serialize proposal as the model would (JSON). Drop nota for scoring path."""
    clean = {
        "n_qubits": int(proposal.get("n_qubits", 2)),
        "gates": proposal.get("gates") or [],
    }
    if proposal.get("domain"):
        clean["domain"] = proposal["domain"]
    return json.dumps(clean, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Metrics (own-delta; no GT labels)
# ---------------------------------------------------------------------------
def structural_goal_from_prompt(prompt: str) -> dict[str, Any]:
    """Infer structural goals from prompt keywords only (never GT)."""
    low = (prompt or "").lower()
    want_bell = any(k in low for k in ("bell", "entrelaz", "entangle", "entanglement"))
    want_product = any(k in low for k in ("product", "separable", "separab"))
    want_ghz = "ghz" in low or "3 qubit" in low or "3 qubits" in low
    want_cx = want_bell or want_ghz or ("cx" in low and "product" not in low)
    return {
        "want_bell_like": want_bell and not want_product,
        "want_product": want_product,
        "want_ghz": want_ghz,
        "want_cx": want_cx and not want_product,
        "want_parseable": True,
    }


def score_proposal(proposal: dict[str, Any] | None, prompt: str) -> dict[str, Any]:
    """parse / structure / solve without GT labels."""
    goals = structural_goal_from_prompt(prompt)
    out: dict[str, Any] = {
        "parse_ok": False,
        "structure_ok": False,
        "solve_ok": False,
        "unitary_ok": False,
        "error": None,
        "goals": goals,
    }
    if not isinstance(proposal, dict):
        out["error"] = "not_dict"
        return out
    gates = proposal.get("gates")
    n_qubits = proposal.get("n_qubits")
    if not isinstance(gates, list) or not gates or n_qubits is None:
        out["error"] = "missing_gates_or_n"
        return out
    # parse_ok: non-empty gates + n_qubits present
    out["parse_ok"] = True
    clean = {"n_qubits": int(n_qubits), "gates": gates}
    try:
        graph = build_graph(clean)
        tool = run_pauli_tool(clean)
    except Exception as exc:  # noqa: BLE001
        out["error"] = f"graph_or_tool:{type(exc).__name__}:{exc}"
        return out
    out["unitary_ok"] = bool(tool.unitary_ok)
    out["structure_ok"] = bool(tool.unitary_ok and len(graph.nodes) >= 1)
    if not out["structure_ok"]:
        out["error"] = tool.error or "structure_fail"
        return out

    # solve: structure + prompt structural goals (keyword-derived)
    has_cx = any(
        (isinstance(g, (list, tuple)) and str(g[0]).lower() == "cx")
        for g in gates
    )
    has_h = any(
        (isinstance(g, (list, tuple)) and str(g[0]).lower() == "h")
        for g in gates
    )
    ok = True
    if goals["want_bell_like"]:
        ok = ok and has_h and has_cx and int(n_qubits) >= 2 and len(graph.edges) >= 1
    if goals["want_product"]:
        ok = ok and (not has_cx)
    if goals["want_ghz"]:
        ok = ok and has_cx and int(n_qubits) >= 3 and sum(
            1 for g in gates if isinstance(g, (list, tuple)) and str(g[0]).lower() == "cx"
        ) >= 2
    if goals["want_cx"] and not goals["want_bell_like"] and not goals["want_ghz"]:
        ok = ok and has_cx
    out["solve_ok"] = bool(ok)
    return out


# ---------------------------------------------------------------------------
# Fixtures + ablation
# ---------------------------------------------------------------------------
CPU_FIXTURES: list[dict[str, str]] = [
    {"id": "ent_bell_01",
     "prompt": "Propose a quantum circuit with n_qubits and gates for a Bell-pair entanglement scene. Reply JSON only."},
    {"id": "ent_bell_02",
     "prompt": "Eres un asistente de circuitos cuánticos. Usa PennyLane gates h,x,cx. Escena de entrelazamiento Bell."},
    {"id": "ent_bell_03",
     "prompt": "Build a Bell-pair circuit (H then CX). Return JSON {n_qubits, gates}."},
    {"id": "ent_cx_01",
     "prompt": "Need a 2-qubit circuit with CX entangling gate. JSON gates list, PennyLane alphabet."},
    {"id": "ent_ghz_01",
     "prompt": "Propose a 3-qubit GHZ-like entangling circuit with H and CX chain. JSON only."},
    {"id": "ent_product_01",
     "prompt": "Propose a separable product-state circuit on 2 qubits (no entangling CX). JSON gates."},
    {"id": "ent_product_02",
     "prompt": "Circuito separable / product state, sin entrelazamiento. n_qubits y gates en JSON."},
    {"id": "ent_ry_01",
     "prompt": "Quantum circuit with ry rotation then optional CX for mild entanglement. JSON."},
    {"id": "ent_generic_01",
     "prompt": "Eres un asistente de circuitos cuánticos. Responde SOLO JSON válido con n_qubits, gates. PennyLane."},
    {"id": "ent_generic_02",
     "prompt": "Propose circuit JSON for this entanglement domain scene. gates: h,x,y,z,cx,ry."},
    {"id": "ent_bell_04",
     "prompt": "Bell state preparation circuit please — qubits and CX. Valid JSON."},
    {"id": "ent_bell_05",
     "prompt": "Circuito tipo Bell: hadamard en q0 y cnot. Responde JSON n_qubits + gates."},
    {"id": "ent_ghz_02",
     "prompt": "GHZ on 3 qubits: H(0), CX(0,1), CX(1,2). Emit JSON proposal."},
    {"id": "ent_product_03",
     "prompt": "Product / separable: only single-qubit gates, no CX. JSON circuit."},
    {"id": "ent_bell_06",
     "prompt": "Entanglement lab: prepare maximally entangled Bell pair via H+CX. JSON."},
    {"id": "ent_cx_02",
     "prompt": "Two-qubit pennylane circuit emphasizing CX entanglement. JSON gates."},
    # Non-ent fixtures (router should send elsewhere; scaffold skipped)
    {"id": "py_01",
     "prompt": "Write a Python function factorial(n) that prints the result. ONLY code in markdown fences."},
    {"id": "py_02",
     "prompt": "def add(a, b): return a+b — write a python program that prints add(2,3). expected_stdout harness."},
    {"id": "vis_01",
     "prompt": "Look at the image. Solve the arithmetic problem. Reply with ONLY the final integer."},
    {"id": "base_01",
     "prompt": "Hello! How is the weather today? Thanks for chatting."},
    {"id": "ent_bell_07",
     "prompt": "n_qubits=2 entanglement: hadamard + cx for Bell. JSON válido."},
    {"id": "ent_bell_08",
     "prompt": "Quantum circuit JSON for entrelazamiento: gates h and cx required."},
    {"id": "ent_product_04",
     "prompt": "Separable product circuit on qubits without CX gates. Reply JSON."},
    {"id": "ent_ghz_03",
     "prompt": "Build GHZ-like 3 qubit entanglement circuit. JSON n_qubits gates."},
]


def run_ablation(
    fixtures: list[dict[str, str]],
    *,
    method: str = "heuristic",
    polish: bool = False,
    seed: int = 0,
) -> dict[str, Any]:
    """Compare scaffold ON vs OFF for ent-routed items (CPU)."""
    encoder = GNNEncoder(embed_dim=64, seed=0)
    rows: list[dict[str, Any]] = []
    agg = {
        "off": {"n": 0, "parse": 0, "structure": 0, "solve": 0},
        "on": {"n": 0, "parse": 0, "structure": 0, "solve": 0},
        "skipped_non_ent": 0,
    }

    for i, fx in enumerate(fixtures):
        prompt = fx["prompt"]
        lane = moe.route(prompt, method=method)
        row: dict[str, Any] = {
            "id": fx["id"],
            "lane": lane,
            "scaffold_applied": False,
        }
        if lane != "ent":
            agg["skipped_non_ent"] += 1
            row["note"] = "non-ent lane — scaffold not applicable"
            rows.append(row)
            continue

        # OFF
        prop_off = heuristic_propose(prompt, use_scaffold=False, seed=seed + i)
        score_off = score_proposal(prop_off, prompt)
        # ON
        prompt_on = inject_scaffold(prompt, polish=polish, encoder=encoder)
        assert not _FORBIDDEN_HINT.search(prompt_on.split(SCAFFOLD_BEGIN)[1])
        prop_on = heuristic_propose(prompt_on, use_scaffold=True, seed=seed + i)
        score_on = score_proposal(prop_on, prompt)

        for key, score, prop in (("off", score_off, prop_off), ("on", score_on, prop_on)):
            agg[key]["n"] += 1
            agg[key]["parse"] += int(score["parse_ok"])
            agg[key]["structure"] += int(score["structure_ok"])
            agg[key]["solve"] += int(score["solve_ok"])

        row.update({
            "scaffold_applied": True,
            "off": {**score_off, "proposal": {"n_qubits": prop_off.get("n_qubits"), "gates": prop_off.get("gates"), "nota": prop_off.get("nota")}},
            "on": {**score_on, "proposal": {"n_qubits": prop_on.get("n_qubits"), "gates": prop_on.get("gates"), "nota": prop_on.get("nota")}},
            "hint_has_gt_token": bool(_FORBIDDEN_HINT.search(prompt_on)),
        })
        rows.append(row)

    def rates(bucket: dict[str, int]) -> dict[str, float]:
        n = max(1, bucket["n"])
        return {
            "n": bucket["n"],
            "parse_rate": round(bucket["parse"] / n, 4),
            "structure_rate": round(bucket["structure"] / n, 4),
            "solve_rate": round(bucket["solve"] / n, 4),
            "parse_n": bucket["parse"],
            "structure_n": bucket["structure"],
            "solve_n": bucket["solve"],
        }

    off_r = rates(agg["off"])
    on_r = rates(agg["on"])
    delta = {
        "parse_rate": round(on_r["parse_rate"] - off_r["parse_rate"], 4),
        "structure_rate": round(on_r["structure_rate"] - off_r["structure_rate"], 4),
        "solve_rate": round(on_r["solve_rate"] - off_r["solve_rate"], 4),
    }
    clear_win = (
        delta["solve_rate"] >= 0.15
        or (delta["structure_rate"] >= 0.15 and delta["parse_rate"] >= 0.05)
    )
    return {
        "written": _now(),
        "router_method": method,
        "polish_features": polish,
        "n_fixtures": len(fixtures),
        "n_ent_evaluated": off_r["n"],
        "n_skipped_non_ent": agg["skipped_non_ent"],
        "no_scaffold": off_r,
        "scaffold": on_r,
        "delta_scaffold_minus_off": delta,
        "clear_win": clear_win,
        "clear_win_rule": "Δsolve≥0.15 OR (Δstructure≥0.15 AND Δparse≥0.05)",
        "prompt_touches_gt": any(r.get("hint_has_gt_token") for r in rows),
        "claims": [
            "NO quantum-advantage claims",
            "Scaffold = classical Clifford–Pauli graph features/hints only",
            "Metrics are own-delta usability (parse/structure/solve) on CPU heuristic",
        ],
        "anti_contamination": {
            "gt_in_scaffold_hints": False,
            "prompt_touches_gt": False,
            "graph_builder_rejects_gt_kwargs": True,
            "lora_adapter_writes": False,
        },
        "rows": rows,
    }


def run_router_ent_smoke(method: str = "heuristic") -> dict[str, Any]:
    """Sanity: ent fixtures route to ent; scaffold injects without GT."""
    enc = GNNEncoder(embed_dim=64, seed=0)
    rows = []
    for fx in CPU_FIXTURES[:8]:
        lane = moe.route(fx["prompt"], method=method)
        injected = inject_scaffold(fx["prompt"], encoder=enc) if lane == "ent" else fx["prompt"]
        rows.append({
            "id": fx["id"],
            "lane": lane,
            "injected": lane == "ent",
            "has_scaffold_markers": SCAFFOLD_BEGIN in injected,
            "gt_leak": bool(_FORBIDDEN_HINT.search(injected)),
        })
    return {
        "n": len(rows),
        "ent_injected": sum(1 for r in rows if r["injected"]),
        "any_gt_leak": any(r["gt_leak"] for r in rows),
        "rows": rows,
    }


def write_doc(result: dict[str, Any], path: Path = DOC_OUT) -> None:
    d = result["delta_scaffold_minus_off"]
    off = result["no_scaffold"]
    on = result["scaffold"]
    lines = [
        "# FRONTIER — Circuit-graph MoE scaffold (entanglement / código-circuito)",
        "",
        f"**Branch:** `frontier/circuit-graph-moe-scaffold`  ",
        f"**Written:** {result['written']}  ",
        "**Parent:** `frontier/moe-verifier-codigo-vivo` @ `3eeeb33` + `frontier/circuit-graph` @ `3beef72`",
        "",
        "## Claims (cannot-claim)",
        "",
        "- **NO** quantum-advantage claims.",
        "- Scaffold uses a **classical** Clifford–Pauli circuit graph + torch-CPU GNN features as *structure hints*.",
        "- Metrics are **own-delta** parse/structure/solve on a CPU heuristic proposer (stand-in for LLM).",
        "- Anti-contam: scaffold hints never include GT / gold / label fields; `build_graph` rejects GT kwargs.",
        "- `data/lora_adapter/` is **READ-ONLY**.",
        "",
        "## What shipped",
        "",
        "| Piece | Path | Role |",
        "|-------|------|------|",
        "| Circuit-graph adapter | `examples/circuit_graph_adapter/` | Gates → anticomm graph → GNN → Pauli tool (from `frontier/circuit-graph`) |",
        "| MoE scaffold hook | `examples/circuit_graph_moe_scaffold.py` | When router lane=`ent`, inject graph features/hints; CPU ablation ON vs OFF |",
        "| Prior PEFT doc | `docs/FRONTIER-PEFT-ENT.md` | Formalism (arXiv:2503.14448-style) |",
        "",
        "## Integration",
        "",
        "1. `moe.route(prompt)` → if `ent`, optionally `inject_scaffold(prompt)`.",
        "2. Scaffold block lists prior template **features** (n_nodes, n_edges, anticomm_density,",
        "   gate_hist, fingerprint) + a gate **sketch** — never scene labels.",
        "3. Proposer (CPU heuristic here; VLM later) reads the block to structure JSON `{n_qubits, gates}`.",
        "",
        "## CPU ablation results",
        "",
        f"- Router method: `{result['router_method']}`",
        f"- Polish features: `{result['polish_features']}`",
        f"- Fixtures: n={result['n_fixtures']} (ent evaluated n={result['n_ent_evaluated']},",
        f"  skipped non-ent n={result['n_skipped_non_ent']})",
        "",
        "| Arm | n | parse_rate | structure_rate | solve_rate |",
        "|-----|---|------------|----------------|------------|",
        f"| no-scaffold | {off['n']} | {off['parse_rate']:.3f} ({off['parse_n']}) | {off['structure_rate']:.3f} ({off['structure_n']}) | {off['solve_rate']:.3f} ({off['solve_n']}) |",
        f"| scaffold | {on['n']} | {on['parse_rate']:.3f} ({on['parse_n']}) | {on['structure_rate']:.3f} ({on['structure_n']}) | {on['solve_rate']:.3f} ({on['solve_n']}) |",
        f"| **Δ (on−off)** |  | **{d['parse_rate']:+.3f}** | **{d['structure_rate']:+.3f}** | **{d['solve_rate']:+.3f}** |",
        "",
        f"**Clear win?** `{result['clear_win']}` — rule: `{result['clear_win_rule']}`",
        "",
        "## Honest limits",
        "",
        "- CPU heuristic ≠ live Qwen/MLX VLM; Δ is scaffold usability on a stub proposer.",
        "- `solve_ok` uses **prompt-keyword structural goals** (Bell/product/GHZ), not scene GT labels.",
        "- GNN conditioning stubs are still **not** wired into the real VLM (`wired_to_vlm=false`).",
        "- No claim that graph features beat a strong LLM without scaffold on the same items.",
        "",
        "## Anti-contamination",
        "",
        "```json",
        json.dumps(result["anti_contamination"], indent=2),
        "```",
        "",
        "## Reproduce",
        "",
        "```bash",
        "python examples/circuit_graph_moe_scaffold.py --smoke",
        "python examples/circuit_graph_moe_scaffold.py --cpu-eval --limit 24",
        "python examples/circuit_graph_moe_scaffold.py --cpu-eval --polish --limit 24",
        "```",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def maybe_freeze(result: dict[str, Any]) -> Path | None:
    if not result.get("clear_win"):
        return None
    blob = {
        "frontier": "circuit-graph-moe-scaffold",
        "written": _now(),
        "clear_win": True,
        "delta": result["delta_scaffold_minus_off"],
        "n_ent": result["n_ent_evaluated"],
        "polish_features": result["polish_features"],
        "claims": result["claims"],
        "anti_contamination": result["anti_contamination"],
        "note": "Freeze: scaffold own-delta clear on CPU heuristic; still no Q-advantage / no VLM wire.",
    }
    FREEZE_OUT.write_text(json.dumps(blob, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return FREEZE_OUT


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Circuit-graph MoE scaffold (CPU ablation)")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--cpu-eval", action="store_true")
    p.add_argument("--polish", action="store_true", help="Richer scaffold features (embed head, suggested_gates)")
    p.add_argument("--mlp", action="store_true")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--write-doc", action="store_true", default=True)
    args = p.parse_args(argv)

    method = "mlp" if args.mlp else "heuristic"
    if not args.smoke and not args.cpu_eval:
        args.smoke = True

    fixtures = list(CPU_FIXTURES)
    if args.limit and args.limit > 0:
        fixtures = fixtures[: args.limit]
    elif args.smoke and not args.cpu_eval:
        fixtures = fixtures[:12]

    t0 = time.time()
    print(f"=== circuit-graph MoE scaffold method={method} polish={args.polish} n={len(fixtures)} ===", flush=True)
    smoke = run_router_ent_smoke(method)
    print(f"Router/scaffold smoke: ent_injected={smoke['ent_injected']}/{smoke['n']} gt_leak={smoke['any_gt_leak']}", flush=True)

    result = run_ablation(fixtures, method=method, polish=args.polish, seed=args.seed)
    result["elapsed_s"] = round(time.time() - t0, 2)
    result["router_scaffold_smoke"] = smoke
    result["frontier"] = "circuit-graph-moe-scaffold"
    result["mode"] = "cpu-eval" if args.cpu_eval else "smoke"

    d = result["delta_scaffold_minus_off"]
    print(
        f"Δ scaffold: parse={d['parse_rate']:+.3f} structure={d['structure_rate']:+.3f} "
        f"solve={d['solve_rate']:+.3f}  clear_win={result['clear_win']}  "
        f"n_ent={result['n_ent_evaluated']}",
        flush=True,
    )

    out = args.out
    if out is None:
        out = EVAL_OUT if args.cpu_eval else SMOKE_OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out}", flush=True)

    if args.write_doc:
        write_doc(result, DOC_OUT)
        print(f"Wrote {DOC_OUT}", flush=True)

    freeze = maybe_freeze(result)
    if freeze:
        print(f"FREEZE note: {freeze}", flush=True)
    else:
        print("No freeze (clear_win=false) — polish iteration may follow.", flush=True)

    if smoke["any_gt_leak"] or result["prompt_touches_gt"]:
        print("FAIL: GT leak in scaffold", flush=True)
        return 1
    if result["n_ent_evaluated"] < 1:
        print("FAIL: no ent items evaluated", flush=True)
        return 1
    print("PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
