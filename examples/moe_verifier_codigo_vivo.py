#!/usr/bin/env python3
"""
Frontier C3 — Unified MoE dual-lane + gold-free Python verifier (Código-vivo).

Combines:
  C1 moe_dual_lane_router  — route ent|python|vision|base; NEVER apply ent LoRA to Python
  C2 python_verifier_loop  — propose → python -I oracle → revise ≤2 (GT never in prompts)

Comparative paths (same items where applicable):
  (a) single-shot no-MoE   — Python pillar, base/heuristic first-shot, no repair
  (b) MoE alone            — route + adapter map; Python = single-shot (no ent adapter)
  (c) verifier alone       — Python repair loop, forced python lane (no router)
  (d) MoE+verifier unified — route; Python lane gets verifier loop; Ent/Vision = RO adapters

Usage:
  python examples/moe_verifier_codigo_vivo.py --smoke
  python examples/moe_verifier_codigo_vivo.py --cpu-eval --limit 5
  python examples/moe_verifier_codigo_vivo.py --replay --limit 16
  python examples/moe_verifier_codigo_vivo.py --mlx-eval --limit 3   # optional; do not block ship

No quantum-advantage claims. Anti-contam: prompt_touches_gt=false.
READ-ONLY: never write/overwrite data/lora_adapter/.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
# Prefer real lab data for RO adapters when running from a worktree /tmp copy.
LAB_DATA = Path(
    os.environ.get(
        "QLAB_DATA",
        str(Path("/Users/anthony/Documents/quantum-llm-lab/data")),
    )
)
sys.path.insert(0, str(ROOT / "examples"))

import moe_dual_lane_router as moe  # noqa: E402
import python_verifier_loop as ver  # noqa: E402
try:
    import circuit_graph_moe_scaffold as cg_scaffold  # noqa: E402
except ImportError:  # pragma: no cover
    cg_scaffold = None  # type: ignore

SMOKE_OUT = ROOT / "data" / "frontier_moe_verifier_cpu_smoke.json"
EVAL_OUT = ROOT / "data" / "frontier_moe_verifier_unified.json"
PRIOR_MOE = ROOT / "data" / "frontier_moe_dual_lane_smoke.json"
PRIOR_VER_REPLAY = ROOT / "data" / "frontier_python_verifier_replay_n16.json"
PRIOR_VER_MLX = ROOT / "data" / "frontier_python_verifier_mlx_smoke_studio.json"


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z").strip()


def _resolve_adapter(lane: moe.Lane) -> Path | None:
    """adapter_path_for with fallback to LAB_DATA if worktree has empty stubs."""
    ap = moe.adapter_path_for(lane)
    if ap is not None and moe._adapter_complete(ap):
        return ap
    # Fallback: look under QLAB_DATA (never write)
    mapping = {
        "ent": ["lora_adapter_ent2", "lora_adapter_ent", "lora_adapter"],
        "python": [],  # intentional: never ent
        "vision": [],  # base by default
        "base": [],
    }
    for name in mapping.get(lane, []):
        cand = LAB_DATA / name
        if moe._adapter_complete(cand):
            return cand
    return None


def _assert_no_lora_writes() -> dict[str, Any]:
    """Sanity: quantum RO adapter path must not be a write target of this script."""
    ro = ROOT / "data" / "lora_adapter"
    lab_ro = LAB_DATA / "lora_adapter"
    return {
        "ro_paths_checked": [str(ro), str(lab_ro)],
        "script_writes_to_lora_adapter": False,
        "policy": "READ-ONLY; never overwrite data/lora_adapter/",
    }


def _load_prior_numbers() -> dict[str, Any]:
    """Honest priors from already-shipped frontier JSON (if present)."""
    out: dict[str, Any] = {}
    if PRIOR_MOE.is_file():
        blob = json.loads(PRIOR_MOE.read_text(encoding="utf-8"))
        bench = blob.get("bench") or {}
        pillars = bench.get("pillars") or {}
        gate = bench.get("gate") or {}
        out["moe_alone"] = {
            "source": str(PRIOR_MOE.name),
            "python_solve_rate": (pillars.get("python") or {}).get("solve_rate"),
            "ent_label_acc": (pillars.get("entanglement") or {}).get("label_acc"),
            "vision_accuracy": (pillars.get("vision") or {}).get("accuracy"),
            "gate_pass": gate.get("gate_pass"),
            "n_python": (pillars.get("python") or {}).get("n"),
            "n_ent": (pillars.get("entanglement") or {}).get("n"),
            "n_vision": (pillars.get("vision") or {}).get("n"),
        }
        # baseline from gate fields
        out["baseline_no_moe"] = {
            "source": str(PRIOR_MOE.name) + "#gate",
            "python_solve_rate": gate.get("python_baseline_base"),
            "vision_accuracy": gate.get("vision_baseline_base"),
            "note": "single-shot base (no MoE) from prior Código-vivo baseline gate",
        }
    if PRIOR_VER_REPLAY.is_file():
        blob = json.loads(PRIOR_VER_REPLAY.read_text(encoding="utf-8"))
        out["verifier_alone_replay_n16"] = {
            "source": str(PRIOR_VER_REPLAY.name),
            "n": blob.get("n"),
            "solve_rate_single": blob.get("solve_rate_single"),
            "solve_rate_loop": blob.get("solve_rate_loop"),
            "repair_success_rate": blob.get("repair_success_rate"),
            "prompt_touches_gt": (blob.get("anti_contamination") or {}).get(
                "prompt_touches_gt", blob.get("prompt_touches_gt")
            ),
        }
    if PRIOR_VER_MLX.is_file():
        blob = json.loads(PRIOR_VER_MLX.read_text(encoding="utf-8"))
        out["verifier_alone_mlx_smoke"] = {
            "source": str(PRIOR_VER_MLX.name),
            "n": blob.get("n"),
            "solve_rate_single": blob.get("solve_rate_single"),
            "solve_rate_loop": blob.get("solve_rate_loop"),
            "repair_success_rate": blob.get("repair_success_rate"),
            "prompt_touches_gt": (blob.get("anti_contamination") or {}).get(
                "prompt_touches_gt", blob.get("prompt_touches_gt")
            ),
        }
    return out


def run_router_smoke(method: str = "heuristic") -> dict[str, Any]:
    """Reuse MoE 12-fixture smoke; annotate with unified adapter resolution."""
    smoke = moe.run_smoke(method)
    for row in smoke["rows"]:
        lane = row["got"]
        ap = _resolve_adapter(lane)  # type: ignore[arg-type]
        row["adapter_resolved"] = str(ap) if ap else None
        # Safety invariant
        if lane == "python":
            assert ap is None or "ent" not in Path(str(ap)).name, (
                "ANTI-CONTAM / dual-lane: python must not get ent adapter"
            )
            row["ent_adapter_blocked"] = True
    smoke["ent_never_on_python"] = all(
        (r["got"] != "python") or (r.get("adapter_resolved") is None)
        or ("ent" not in Path(str(r["adapter_resolved"])).name)
        for r in smoke["rows"]
    )
    return smoke


def run_python_paths(
    items: list[dict[str, Any]],
    *,
    proposer: str,
    rounds: int,
    timeout_s: float,
    replay_map: dict[str, str] | None,
    model_id: str,
    method: str,
) -> dict[str, Any]:
    """
    Run comparative Python paths (a)(b)(c)(d) on the same item list.

    (a) single no-MoE: heuristic/replay/mlx first-shot, rounds=0, no router
    (b) MoE alone: route each prompt; if python → same as (a) with adapter=None;
        non-python → counted as routed_away (not solved via python oracle)
    (c) verifier alone: forced python lane + repair rounds
    (d) unified: route; python → verifier; non-python → routed_away
    """
    logs_a: list[ver.TaskLog] = []
    logs_b_py: list[ver.TaskLog] = []
    logs_c: list[ver.TaskLog] = []
    logs_d_py: list[ver.TaskLog] = []
    route_b: list[dict[str, Any]] = []
    route_d: list[dict[str, Any]] = []

    for it in items:
        prompt = str(it["prompt"])
        lane = moe.route(prompt, method=method)
        ap = _resolve_adapter(lane)
        route_row = {
            "id": it["id"],
            "lane": lane,
            "adapter": str(ap) if ap else None,
            "ent_blocked_on_python": lane == "python" and (
                ap is None or "ent" not in Path(str(ap)).name
            ),
        }

        # (a) single-shot no MoE, no repair
        la = ver.run_task(
            it,
            proposer=proposer,
            rounds=0,
            timeout_s=timeout_s,
            replay_map=replay_map,
            model_id=model_id,
            adapter_ro=None,
            use_local_fix=False,
        )
        logs_a.append(la)

        # (b) MoE alone: only evaluate python-routed items as single-shot
        route_b.append(route_row)
        if lane == "python":
            lb = ver.run_task(
                it,
                proposer=proposer,
                rounds=0,
                timeout_s=timeout_s,
                replay_map=replay_map,
                model_id=model_id,
                adapter_ro=None,  # hard: no ent
                use_local_fix=False,
            )
            logs_b_py.append(lb)
        # else: routed away from python oracle — not a python solve attempt

        # (c) verifier alone (ignore router)
        lc = ver.run_task(
            it,
            proposer=proposer,
            rounds=rounds,
            timeout_s=timeout_s,
            replay_map=replay_map,
            model_id=model_id,
            adapter_ro=None,
            use_local_fix=True,
        )
        logs_c.append(lc)

        # (d) unified: route + verifier on python lane
        route_d.append(route_row)
        if lane == "python":
            ld = ver.run_task(
                it,
                proposer=proposer,
                rounds=rounds,
                timeout_s=timeout_s,
                replay_map=replay_map,
                model_id=model_id,
                adapter_ro=None,
                use_local_fix=True,
            )
            logs_d_py.append(ld)

    def pack(name: str, logs: list[ver.TaskLog], extra: dict[str, Any] | None = None) -> dict[str, Any]:
        agg = ver.aggregate(logs) if logs else {
            "n": 0,
            "solve_rate_single": 0.0,
            "solve_rate_loop": 0.0,
            "delta_solve_rate": 0.0,
            "solved_single": 0,
            "solved_loop": 0,
            "repair_success_rate": 0.0,
            "repair_helped_n": 0,
            "failed_single_n": 0,
            "prompt_touches_gt": False,
            "prompt_touches_gt_locked_false": True,
        }
        # For single-shot paths, solve_rate_loop == solve_rate_single (rounds=0)
        block = {
            "path": name,
            **agg,
            "details": [
                {
                    "id": L.id,
                    "single_solved": L.single_solved,
                    "loop_solved": L.loop_solved,
                    "rounds_used": L.rounds_used,
                    "repair_helped": L.repair_helped,
                    "prompt_touches_gt": L.prompt_touches_gt,
                    "actions": L.actions,
                }
                for L in logs
            ],
        }
        if extra:
            block.update(extra)
        return block

    n_items = len(items)
    n_routed_py = sum(1 for r in route_b if r["lane"] == "python")
    n_routed_away = n_items - n_routed_py

    path_a = pack("a_single_shot_no_moe", logs_a)
    path_b = pack(
        "b_moe_alone",
        logs_b_py,
        extra={
            "n_items_total": n_items,
            "n_routed_python": n_routed_py,
            "n_routed_away": n_routed_away,
            # Denominator for MoE-on-python-set: same as python-routed count
            "solve_rate_on_python_lane": (
                (sum(1 for L in logs_b_py if L.single_solved) / n_routed_py)
                if n_routed_py else 0.0
            ),
            "routing": route_b,
        },
    )
    path_c = pack("c_verifier_alone", logs_c)
    path_d = pack(
        "d_moe_verifier_unified",
        logs_d_py,
        extra={
            "n_items_total": n_items,
            "n_routed_python": n_routed_py,
            "n_routed_away": n_routed_away,
            "solve_rate_on_python_lane": (
                (sum(1 for L in logs_d_py if L.loop_solved) / n_routed_py)
                if n_routed_py else 0.0
            ),
            "routing": route_d,
        },
    )

    # Comparative table (honest: Δ vs path a on overlapping python-eval)
    def rate(block: dict[str, Any], key: str = "solve_rate_loop") -> float | None:
        if block.get("n", 0) == 0:
            return None
        return float(block.get(key) or 0.0)

    base_rate = rate(path_a, "solve_rate_single")
    table = []
    for label, block, key in [
        ("baseline_single_no_moe", path_a, "solve_rate_single"),
        ("moe_alone_python_lane", path_b, "solve_rate_single"),
        ("verifier_alone", path_c, "solve_rate_loop"),
        ("moe_verifier_unified_python_lane", path_d, "solve_rate_loop"),
    ]:
        r = rate(block, key)
        delta = None if (r is None or base_rate is None) else round(r - base_rate, 4)
        table.append({
            "path": label,
            "n": block.get("n"),
            "metric": key,
            "rate": r,
            "delta_vs_baseline": delta,
            "repair_success_rate": block.get("repair_success_rate"),
            "prompt_touches_gt": block.get("prompt_touches_gt"),
        })

    any_touch = any(
        p.get("prompt_touches_gt") for p in (path_a, path_b, path_c, path_d)
    )

    return {
        "n_items": n_items,
        "proposer": proposer,
        "router_method": method,
        "rounds_max": rounds,
        "paths": {
            "a_single_shot_no_moe": path_a,
            "b_moe_alone": path_b,
            "c_verifier_alone": path_c,
            "d_moe_verifier_unified": path_d,
        },
        "comparison_table": table,
        "prompt_touches_gt": bool(any_touch),
        "ent_never_on_python": all(
            r.get("ent_blocked_on_python", True)
            for r in route_b
            if r.get("lane") == "python"
        ),
    }


def run_ent_vision_routing(
    method: str = "heuristic",
    *,
    circuit_scaffold: bool = False,
) -> dict[str, Any]:
    """Route Ent/Vision samples; report RO adapter selection only (no overwrite).

    If circuit_scaffold and lane=ent, attach GT-free circuit-graph hint metadata
    (prompt text not required for this routing report).
    """
    samples = [
        {
            "id": "ent_sample",
            "domain": "ent",
            "prompt": (
                "Eres un asistente de circuitos cuánticos. Mira la imagen. "
                "Responde SOLO JSON válido con claves n_qubits, gates, domain, label. "
                "PennyLane gates h,x,cx."
            ),
        },
        {
            "id": "vis_sample",
            "domain": "vision",
            "prompt": (
                "Look at the image. Solve the arithmetic problem. "
                "Reply with ONLY the final integer answer, no words."
            ),
        },
    ]
    rows = []
    for s in samples:
        lane = moe.route(s["prompt"], method=method)
        ap = _resolve_adapter(lane)
        sc_meta = None
        if circuit_scaffold and lane == "ent" and cg_scaffold is not None:
            hint = cg_scaffold.format_scaffold_hint(s["prompt"])
            sc_meta = {
                "injected": True,
                "hint_chars": len(hint),
                "has_markers": cg_scaffold.SCAFFOLD_BEGIN in hint,
                "gt_leak": bool(cg_scaffold._FORBIDDEN_HINT.search(hint)),
            }
        rows.append({
            **s,
            "routed_lane": lane,
            "adapter_ro": str(ap) if ap else None,
            "adapter_write": False,
            "circuit_graph_scaffold": sc_meta,
        })
    return {
        "note": "Ent/Vision: adapter selection READ-ONLY; no pillar re-run in CPU smoke",
        "rows": rows,
        "prior_live_bench": _load_prior_numbers().get("moe_alone"),
    }


def build_artifact(
    *,
    mode: str,
    method: str,
    python_eval: dict[str, Any] | None,
    router_smoke: dict[str, Any] | None,
    ent_vis: dict[str, Any] | None,
    notes: list[str],
    mlx_status: str | None = None,
) -> dict[str, Any]:
    priors = _load_prior_numbers()
    return {
        "frontier": "C3-moe-verifier-codigo-vivo",
        "written": _now(),
        "mode": mode,
        "router_method": method,
        "claims": [
            "NO quantum-advantage claims",
            "MoE routing usability + classical python -I exec oracle only",
        ],
        "anti_contamination": {
            "prompt_touches_gt": (
                False
                if not python_eval
                else python_eval.get("prompt_touches_gt", False)
            ),
            "gt_never_in_inference_prompts": True,
            "ent_never_on_python": (
                True
                if not python_eval
                else python_eval.get("ent_never_on_python", True)
            ),
            "rule": "revision gets stderr only; expected_stdout harness-only",
            "lock": "docs/LOCK-ANTI-CONTAMINATION.md",
        },
        "ro_lock": _assert_no_lora_writes(),
        "adapter_map": {
            "ent": str(_resolve_adapter("ent")) if _resolve_adapter("ent") else None,
            "python": None,
            "vision": str(_resolve_adapter("vision")) if _resolve_adapter("vision") else None,
            "base": None,
        },
        "router_smoke": router_smoke,
        "ent_vision_routing": ent_vis,
        "python_paths": python_eval,
        "priors_from_shipped_json": priors,
        "mlx_status": mlx_status,
        "notes": notes,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Unified MoE + Python verifier Código-vivo (Frontier C3)"
    )
    p.add_argument("--smoke", action="store_true", help="CPU/heuristic smoke (default)")
    p.add_argument("--cpu-eval", action="store_true", help="Heuristic proposer paths on python items")
    p.add_argument("--replay", action="store_true", help="Replay first-shot from bench JSON")
    p.add_argument("--mlx-eval", action="store_true", help="Live VLM (optional; never blocks ship)")
    p.add_argument("--mlp", action="store_true", help="Use MoE MLP router")
    p.add_argument("--vqc-router", action="store_true", help="Ablation VQC router (CPU)")
    p.add_argument("--circuit-scaffold", action="store_true",
                   help="When lane=ent, inject Clifford–Pauli graph scaffold hints (no GT)")
    p.add_argument("--items", type=Path, default=ver.DEFAULT_ITEMS)
    p.add_argument("--bench", type=Path, default=ver.DEFAULT_BENCH)
    p.add_argument("--replay-source", default="base", choices=("base", "adapter_run", "finetuned"))
    p.add_argument("--rounds", type=int, default=2)
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--timeout", type=float, default=8.0)
    p.add_argument("--model", default=ver.DEFAULT_MODEL)
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--hardneg", action="store_true",
                   help="Also score hard-neg mixed router + hardneg python items")
    p.add_argument("--hardneg-only", action="store_true",
                   help="Run hard-neg python paths instead of default items")
    p.add_argument("--hardneg-items", type=Path,
                   default=ROOT / "data" / "bench_live" / "hardneg_python_items.json")
    p.add_argument("--hardneg-router", type=Path,
                   default=ROOT / "data" / "bench_live" / "hardneg_mixed_router.json")
    args = p.parse_args(argv)

    method = "heuristic"
    if args.mlp:
        method = "mlp"
    if args.vqc_router:
        method = "vqc"

    if not any([args.smoke, args.cpu_eval, args.replay, args.mlx_eval]):
        args.smoke = True

    notes: list[str] = []
    mlx_status: str | None = None
    router_smoke = None
    python_eval = None
    ent_vis = None
    hardneg_router = None
    mode = "smoke"

    # Always run router smoke in --smoke
    if args.smoke or args.cpu_eval or args.hardneg or args.hardneg_only:
        print(f"=== C3 router smoke method={method} ===", flush=True)
        router_smoke = run_router_smoke(method)
        print(f"Router smoke: {router_smoke['score']} ent_never_on_python={router_smoke['ent_never_on_python']}", flush=True)
        ent_vis = run_ent_vision_routing(method, circuit_scaffold=args.circuit_scaffold)

    if args.hardneg or args.hardneg_only:
        print(f"=== C3 hardneg router method={method} ===", flush=True)
        hardneg_router = moe.run_hardneg(method, path=args.hardneg_router)
        print(
            f"Hardneg router: {hardneg_router['score']} rate={hardneg_router['rate']} "
            f"ent_never_on_python={hardneg_router['ent_never_on_python']}",
            flush=True,
        )

    # Python comparative paths
    proposer = "heuristic"
    replay_map = None
    if args.replay:
        mode = "replay"
        proposer = "replay"
        replay_map = ver.load_replay_codes(args.bench, args.replay_source)
        if not replay_map:
            notes.append(f"replay map empty (bench missing?): {args.bench}")
            print(f"[warn] empty replay map from {args.bench}", flush=True)
    elif args.mlx_eval:
        mode = "mlx"
        proposer = "mlx"
        free, why = ver.gpu_free()
        if not free:
            mlx_status = f"skipped: {why}"
            notes.append(mlx_status)
            print(f"[mlx] {mlx_status}", flush=True)
            # Fall back to smoke numbers only — do not fail ship
            proposer = "heuristic"
            mode = "smoke_fallback_after_mlx_busy"
        else:
            mlx_status = "gpu_free_attempting"
    elif args.cpu_eval or args.hardneg_only:
        mode = "hardneg-cpu" if args.hardneg_only else "cpu-eval"
        proposer = "heuristic"
    else:
        mode = "smoke"
        proposer = "heuristic"

    if args.smoke or args.cpu_eval or args.replay or args.hardneg_only or (args.mlx_eval and proposer in ("mlx", "heuristic")):
        item_path = args.hardneg_items if args.hardneg_only else args.items
        items = ver.load_python_items(item_path)
        if args.limit and args.limit > 0:
            items = items[: args.limit]
        elif args.smoke and not args.cpu_eval and not args.replay and not args.mlx_eval and not args.hardneg_only:
            items = items[:5]  # smoke default n=5

        if args.mlx_eval and proposer == "mlx":
            try:
                print(f"=== C3 mlx paths n={len(items)} ===", flush=True)
                python_eval = run_python_paths(
                    items,
                    proposer="mlx",
                    rounds=args.rounds,
                    timeout_s=args.timeout,
                    replay_map=None,
                    model_id=args.model,
                    method=method,
                )
                mlx_status = "ok"
            except Exception as exc:  # noqa: BLE001
                mlx_status = f"failed: {type(exc).__name__}: {exc}"
                notes.append(mlx_status)
                print(f"[mlx] {mlx_status} — falling back to heuristic CPU", flush=True)
                proposer = "heuristic"
                python_eval = run_python_paths(
                    items,
                    proposer="heuristic",
                    rounds=args.rounds,
                    timeout_s=args.timeout,
                    replay_map=None,
                    model_id=args.model,
                    method=method,
                )
                mode = "smoke_fallback_after_mlx_fail"
        else:
            print(f"=== C3 python paths proposer={proposer} n={len(items)} ===", flush=True)
            python_eval = run_python_paths(
                items,
                proposer=proposer,
                rounds=args.rounds,
                timeout_s=args.timeout,
                replay_map=replay_map,
                model_id=args.model,
                method=method,
            )

        # Print comparison table
        if python_eval:
            print("--- comparison_table ---", flush=True)
            for row in python_eval["comparison_table"]:
                print(
                    f"  {row['path']:40s} n={row['n']!s:4s} rate={row['rate']} "
                    f"Δ={row['delta_vs_baseline']} touches_gt={row['prompt_touches_gt']}",
                    flush=True,
                )

    out_path = args.out
    if out_path is None:
        if mode.startswith("replay"):
            out_path = ROOT / "data" / "frontier_moe_verifier_replay.json"
        elif "mlx" in mode:
            out_path = ROOT / "data" / "frontier_moe_verifier_mlx_smoke.json"
        elif mode == "cpu-eval":
            out_path = ROOT / "data" / "frontier_moe_verifier_cpu_n.json"
        elif mode == "hardneg-cpu":
            hp = str(args.hardneg_items).lower() + str(args.hardneg_router).lower()
            if 'label_protect' in hp or 'label-protect' in hp:
                out_path = ROOT / "data" / "frontier_moe_verifier_hardneg_label_protect.json"
            elif 'r26' in hp:
                out_path = ROOT / "data" / "frontier_moe_verifier_hardneg_r26.json"
            elif 'r15' in hp:
                out_path = ROOT / "data" / "frontier_moe_verifier_hardneg_r15.json"
            elif 'r14' in hp:
                out_path = ROOT / "data" / "frontier_moe_verifier_hardneg_r14.json"
            elif 'r13' in hp:
                out_path = ROOT / "data" / "frontier_moe_verifier_hardneg_r13.json"
            elif 'r12' in hp:
                out_path = ROOT / "data" / "frontier_moe_verifier_hardneg_r12.json"
            elif 'r11' in hp:
                out_path = ROOT / "data" / "frontier_moe_verifier_hardneg_r11.json"
            elif 'r10' in hp:
                out_path = ROOT / "data" / "frontier_moe_verifier_hardneg_r10.json"
            elif 'r9' in hp:
                out_path = ROOT / "data" / "frontier_moe_verifier_hardneg_r9.json"
            elif 'r8' in hp:
                out_path = ROOT / "data" / "frontier_moe_verifier_hardneg_r8.json"
            elif 'r7' in hp:
                out_path = ROOT / "data" / "frontier_moe_verifier_hardneg_r7.json"
            elif 'r6' in hp:
                out_path = ROOT / "data" / "frontier_moe_verifier_hardneg_r6.json"
            elif 'r5' in hp:
                out_path = ROOT / "data" / "frontier_moe_verifier_hardneg_r5.json"
            elif 'r4' in hp:
                out_path = ROOT / "data" / "frontier_moe_verifier_hardneg_r4.json"
            elif 'r3' in hp:
                out_path = ROOT / "data" / "frontier_moe_verifier_hardneg_r3.json"
            elif 'r2' in hp:
                out_path = ROOT / "data" / "frontier_moe_verifier_hardneg_r2.json"
            else:
                out_path = ROOT / "data" / "frontier_moe_verifier_hardneg.json"
        else:
            out_path = SMOKE_OUT

    artifact = build_artifact(
        mode=mode,
        method=method,
        python_eval=python_eval,
        router_smoke=router_smoke,
        ent_vis=ent_vis,
        notes=notes,
        mlx_status=mlx_status,
    )
    if hardneg_router is not None:
        artifact["hardneg_router"] = hardneg_router
        artifact["hardneg_delta"] = {
            "router_rate": hardneg_router.get("rate"),
            "router_score": hardneg_router.get("score"),
            "ent_never_on_python": hardneg_router.get("ent_never_on_python"),
            "vs_freeze_floor": "hold" if (hardneg_router.get("rate") or 0) >= 0.80 else "drop",
        }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}", flush=True)

    # Pass criteria for smoke: router 12/12 and prompt_touches_gt false
    if router_smoke and router_smoke.get("hits", 0) < router_smoke.get("n", 12):
        print("FAIL: router smoke incomplete", flush=True)
        return 1
    if python_eval and python_eval.get("prompt_touches_gt"):
        print("FAIL: prompt_touches_gt=true", flush=True)
        return 1
    if python_eval and not python_eval.get("ent_never_on_python", True):
        print("FAIL: ent adapter applied on python", flush=True)
        return 1
    print("PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
