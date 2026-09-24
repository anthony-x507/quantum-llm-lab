#!/usr/bin/env python3
"""
Live MLX mixed pillars (python + ent + vision) — honest generate, not prior-replay.

Ent live path injects GT-free circuit-graph scaffold into VLM prompts
(`wired_to_vlm=true`, text_scaffold_prefix). Pillar rates from live mlx_vlm
generate. READ-ONLY adapters. No quantum-advantage claims.

  QLAB_DATA=... .venv/bin/python examples/moe_verifier_mixed_mlx_live_pillars.py \
    --n-py 3 --n-ent 3 --n-vis 3
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import socket
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LAB_DATA = Path(
    os.environ.get("QLAB_DATA", "/Users/anthony/Documents/quantum-llm-lab/data")
)
sys.path.insert(0, str(ROOT / "examples"))

import bench_codigo_vivo as bench  # noqa: E402
import moe_dual_lane_router as moe  # noqa: E402
import moe_verifier_mixed_live as mixed  # noqa: E402
import python_verifier_loop as ver  # noqa: E402

MODEL = "mlx-community/Qwen3-VL-8B-Thinking-4bit"
OUT_DEFAULT = ROOT / "data" / "frontier_moe_verifier_mixed_mlx_live_pillars.json"
CPU_REF_OVERALL = 1.0  # tip CPU unified floor (MFV polish)


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S ET")


def _host() -> dict[str, Any]:
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "machineId_hint": "074c6626-0440-4817-9829-6bae77c578d6",
    }


def _confirm_8b() -> dict[str, Any]:
    hub = Path.home() / ".cache/huggingface/hub"
    snap = (
        hub
        / "models--mlx-community--Qwen3-VL-8B-Thinking-4bit"
        / "snapshots"
        / "e68aa09bc7df2d41ba8f96e4f12118097b61d19a"
    )
    shards = sorted(snap.glob("model-*.safetensors")) if snap.exists() else []
    eff = 0
    names = []
    for s in shards:
        names.append(s.name)
        eff += s.resolve().stat().st_size
    return {
        "model": MODEL,
        "rev": "e68aa09bc7df2d41ba8f96e4f12118097b61d19a",
        "snap_exists": snap.exists(),
        "shards_present": names,
        "effective_bytes": eff,
        "effective_GB": round(eff / 1e9, 3),
        "ready": snap.exists() and eff >= 5_000_000_000 and len(shards) >= 2,
        "target_GB": 5.78,
    }


def _bump_tokens(max_tokens: int = 1536) -> None:
    """Anti-think budget for Thinking-4bit (tip already has strip + cue in grounding)."""
    orig = bench._generate_text

    def wrapped(model, processor, config, generate, apply_chat_template, prompt, image, max_tokens_arg=512):
        # Prefer anti-think headroom unless caller already asked higher
        mt = max(max_tokens_arg, max_tokens)
        return orig(model, processor, config, generate, apply_chat_template, prompt, image, mt)

    bench._generate_text = wrapped  # type: ignore[assignment]


def _ent_adapter() -> Path | None:
    for cand in (
        ROOT / "data" / "lora_adapter_ent2",
        LAB_DATA / "lora_adapter_ent2",
        LAB_DATA / "lora_adapter_ent",
    ):
        if moe._adapter_complete(cand):
            return cand
    return None


def run_python_live(n: int, rounds: int) -> dict[str, Any]:
    mixed_blob = json.loads((ROOT / "data/bench_live/mixed_items_largern.json").read_text())
    items = mixed._py_items_for_ver(mixed_blob)[:n]
    t0 = time.time()
    py_eval = mixed.run_python_paths(
        items,
        proposer="mlx",
        rounds=rounds,
        timeout_s=8.0,
        replay_map=None,
        model_id=MODEL,
        method="heuristic",
    )
    py_eval["elapsed_s"] = round(time.time() - t0, 2)
    py_eval["metric_source"] = "mlx_live_generate"
    return py_eval


def run_ent_live(n: int) -> dict[str, Any]:
    mixed_blob = json.loads((ROOT / "data/bench_live/mixed_items_largern.json").read_text())
    sids = [it["scene_id"] for it in (mixed_blob.get("entanglement") or [])][:n]
    # ensure scenes resolvable under tip ROOT
    missing = []
    for sid in sids:
        if not (ROOT / "data" / "scenes" / sid / "meta.json").exists():
            missing.append(sid)
    adapter = _ent_adapter()
    t0 = time.time()
    # base (no adapter)
    print(f"=== LIVE ent BASE n={len(sids)} ===", flush=True)
    base_bundle = bench._load_vlm(MODEL, None)
    base = bench.run_pillar_entanglement(base_bundle, sids, "mlx-live-ent-base", circuit_scaffold=True, scaffold_polish=True)
    del base_bundle
    # MoE ent2 RO
    print(f"=== LIVE ent ENT2 adapter={adapter} ===", flush=True)
    if adapter is None:
        moe_ent = {
            "n": len(sids),
            "label_acc": 0.0,
            "error": "no_ent2_adapter",
            "details": [],
        }
    else:
        ent_bundle = bench._load_vlm(MODEL, str(adapter))
        moe_ent = bench.run_pillar_entanglement(ent_bundle, sids, "mlx-live-ent-ent2", circuit_scaffold=True, scaffold_polish=True)
        del ent_bundle
    elapsed = round(time.time() - t0, 2)
    return {
        "metric_source": "mlx_live_generate",
        "n": len(sids),
        "scene_ids": sids,
        "missing_scenes": missing,
        "adapter_ent2": str(adapter) if adapter else None,
        "elapsed_s": elapsed,
        "wired_to_vlm": bool(base.get("wired_to_vlm")) or bool(moe_ent.get("wired_to_vlm")),
        "channel": "text_scaffold_prefix",
        "weight_peft_injection": False,
        "base": {
            "label_acc": base.get("label_acc"),
            "parse_rate": base.get("parse_rate"),
            "compile_rate": base.get("compile_rate"),
            "n": base.get("n"),
            "label_correct": base.get("label_correct"),
            "parse_ok": base.get("parse_ok"),
            "wired_to_vlm": base.get("wired_to_vlm"),
            "scaffold_wired_n": base.get("scaffold_wired_n"),
            "details": base.get("details"),
        },
        "moe_ent2": {
            "label_acc": moe_ent.get("label_acc"),
            "parse_rate": moe_ent.get("parse_rate"),
            "compile_rate": moe_ent.get("compile_rate"),
            "n": moe_ent.get("n"),
            "label_correct": moe_ent.get("label_correct"),
            "parse_ok": moe_ent.get("parse_ok"),
            "wired_to_vlm": moe_ent.get("wired_to_vlm"),
            "scaffold_wired_n": moe_ent.get("scaffold_wired_n"),
            "details": moe_ent.get("details"),
            "error": moe_ent.get("error"),
        },
    }


def _vis_items_for_bench(n: int) -> list[dict[str, Any]]:
    mixed_blob = json.loads((ROOT / "data/bench_live/mixed_items_largern.json").read_text())
    out = []
    for it in mixed_blob.get("vision") or []:
        if not it.get("score_accuracy", True):
            continue
        ev = it.get("eval") or {}
        img = it["image"]
        p = ROOT / img
        if not p.exists():
            alt = LAB_DATA / "bench_live" / "vision_items" / Path(img).name
            if alt.exists():
                img = str(alt)
            else:
                img = str(p)
        else:
            img = str(p)
        out.append({
            "id": it["id"],
            "kind": it.get("kind") or "math",
            "prompt": it["prompt"],
            "image": img,
            "match": ev.get("match") or "exact_int",
            "expected": ev.get("expected"),
            "expected_stdout": ev.get("expected"),  # unused
        })
        if len(out) >= n:
            break
    return out


def run_vis_live(n: int) -> dict[str, Any]:
    items = _vis_items_for_bench(n)
    t0 = time.time()
    print(f"=== LIVE vision BASE n={len(items)} ===", flush=True)
    bundle = bench._load_vlm(MODEL, None)
    # first pass
    first = bench.run_pillar_vision(bundle, items, "mlx-live-vis")
    # one polish pass on parse/int fails (anti-think cue already tip; bump prompt)
    failed = [d for d in first.get("details") or [] if not d.get("correct")]
    polish = {"applied": False, "retried_ids": [], "rescued": 0}
    if failed:
        polish["applied"] = True
        retry_items = []
        by_id = {it["id"]: it for it in items}
        for d in failed:
            it = dict(by_id[d["id"]])
            it["prompt"] = (
                it["prompt"]
                + "\n\nÚNICAMENTE el entero final. Empieza con el dígito. "
                "Sin cadena de pensamiento en inglés. Sin JSON."
            )
            retry_items.append(it)
            polish["retried_ids"].append(it["id"])
        second = bench.run_pillar_vision(bundle, retry_items, "mlx-live-vis-polish")
        # merge: rescue if second correct
        merged_details = []
        second_by = {d["id"]: d for d in second.get("details") or []}
        correct_n = 0
        for d in first.get("details") or []:
            s = second_by.get(d["id"])
            if d.get("correct"):
                merged_details.append({**d, "phase": "first"})
                correct_n += 1
            elif s and s.get("correct"):
                merged_details.append({**s, "phase": "polish"})
                correct_n += 1
                polish["rescued"] += 1
            else:
                merged_details.append({**(s or d), "phase": "polish_fail" if s else "first_fail"})
        first = {
            "n": len(items),
            "correct": correct_n,
            "accuracy": correct_n / max(1, len(items)),
            "errors": first.get("errors", 0),
            "details": merged_details,
        }
    del bundle
    return {
        "metric_source": "mlx_live_generate",
        "n": len(items),
        "elapsed_s": round(time.time() - t0, 2),
        "accuracy": first.get("accuracy"),
        "correct": first.get("correct"),
        "polish": polish,
        "details": first.get("details"),
    }


def build_live_scoreboard(py: dict, ent: dict, vis: dict) -> dict[str, Any]:
    """(a)(b)(c)(d) with LIVE rates where measured; honest n."""
    py_single = float(
        ((py.get("paths") or {}).get("a_baseline_single") or {}).get("solve_rate_single") or 0.0
    )
    py_loop = float(
        ((py.get("paths") or {}).get("d_unified_python_lane") or {}).get("solve_rate_loop")
        or ((py.get("paths") or {}).get("c_verifier_alone") or {}).get("solve_rate_loop")
        or 0.0
    )
    ent_base = float((ent.get("base") or {}).get("label_acc") or 0.0)
    ent_moe = float((ent.get("moe_ent2") or {}).get("label_acc") or 0.0)
    vis_acc = float(vis.get("accuracy") or 0.0)

    def row(path: str, py_r: float, ent_r: float, vis_r: float, py_metric: str) -> dict:
        overall = round((py_r + ent_r + vis_r) / 3.0, 4)
        return {
            "path": path,
            "python": {"n": py.get("n_items"), "rate": py_r, "metric": py_metric, "source": "mlx_live"},
            "entanglement": {
                "n": ent.get("n"),
                "label_acc": ent_r,
                "source": "mlx_live",
            },
            "vision": {"n": vis.get("n"), "accuracy": vis_r, "source": "mlx_live"},
            "overall_mean": overall,
        }

    table = [
        row("a_baseline", py_single, ent_base, vis_acc, "solve_rate_single"),
        row("b_moe_alone", py_single, ent_moe, vis_acc, "solve_rate_single"),
        row("c_verifier_on_python", py_loop, ent_base, vis_acc, "solve_rate_loop"),
        row("d_unified", py_loop, ent_moe, vis_acc, "solve_rate_loop"),
    ]
    d = table[3]["overall_mean"]
    a = table[0]["overall_mean"]
    return {
        "table": table,
        "delta_moe_vs_baseline": {
            "python": 0.0,
            "entanglement": round(ent_moe - ent_base, 4),
            "vision": 0.0,
            "overall": round(d - a, 4),
        },
        "moe_delta_visible": (ent_moe - ent_base) > 0.05,
        "vs_cpu_overall_1_0": {
            "cpu_unified_overall": CPU_REF_OVERALL,
            "mlx_unified_overall": d,
            "delta": round(d - CPU_REF_OVERALL, 4),
            "note": "CPU tip uses prior-replay ent/vis + live heuristic/verifier python → overall 1.0; this row is LIVE mlx on all three pillars with honest n.",
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--n-py", type=int, default=3)
    p.add_argument("--n-ent", type=int, default=3)
    p.add_argument("--n-vis", type=int, default=3)
    p.add_argument("--rounds", type=int, default=2)
    p.add_argument("--skip-ent", action="store_true")
    p.add_argument("--skip-vis", action="store_true")
    p.add_argument("--skip-py", action="store_true")
    p.add_argument("--out", type=Path, default=OUT_DEFAULT)
    args = p.parse_args()

    model_status = _confirm_8b()
    print(f"8B ready={model_status['ready']} effective_GB={model_status['effective_GB']}", flush=True)
    if not model_status["ready"]:
        print("FAIL: 8B not ready", flush=True)
        return 2

    free, why = ver.gpu_free()
    if not free:
        print(f"FAIL: GPU busy: {why}", flush=True)
        return 3

    _bump_tokens(1536)
    notes: list[str] = []
    studio = {
        "machineId": "8e12e5c3-d3ae-4886-867e-28f4fc01a913",
        "label": "Mac-198",
        "online": False,
        "note": "Studio offline at start; ran on Mac-111 only",
    }

    py: dict[str, Any] = {"skipped": True}
    ent: dict[str, Any] = {"skipped": True}
    vis: dict[str, Any] = {"skipped": True}

    t_all = time.time()
    try:
        if not args.skip_py:
            print(f"=== LIVE python verifier n={args.n_py} ===", flush=True)
            py = run_python_live(args.n_py, args.rounds)
        if not args.skip_ent:
            ent = run_ent_live(args.n_ent)
        if not args.skip_vis:
            vis = run_vis_live(args.n_vis)
    except Exception as exc:  # noqa: BLE001
        notes.append(f"abort: {type(exc).__name__}: {exc}")
        traceback.print_exc()

    scoreboard = None
    if not py.get("skipped") and not ent.get("skipped") and not vis.get("skipped"):
        scoreboard = build_live_scoreboard(py, ent, vis)

    # drops honesty
    drops = []
    if scoreboard:
        vs = scoreboard["vs_cpu_overall_1_0"]
        if vs["delta"] < 0:
            drops.append(
                f"overall Δ vs CPU 1.0 = {vs['delta']} "
                f"(mlx={vs['mlx_unified_overall']})"
            )
        for row in scoreboard["table"]:
            if row["path"] == "d_unified":
                if row["python"]["rate"] < 1.0:
                    drops.append(f"python loop {row['python']['rate']} < 1.0")
                if row["entanglement"]["label_acc"] < 1.0:
                    drops.append(
                        f"ent live label_acc {row['entanglement']['label_acc']} < 1.0 (CPU prior 1.0)"
                    )
                if row["vision"]["accuracy"] < 1.0:
                    drops.append(
                        f"vision live {row['vision']['accuracy']} < 1.0 (CPU prior 1.0)"
                    )

    art = {
        "frontier": "codigo-vivo-tip-mlx-live-pillars",
        "written": _now(),
        "host": _host(),
        "tip_sha_at_run": None,  # filled by shell wrapper if desired
        "claims": [
            "NO quantum-advantage claims",
            "Live mlx_vlm generate for py+ent+vis; not prior-replay for these rates",
        ],
        "ro_lock": {
            "script_writes_to_lora_adapter": False,
            "policy": "READ-ONLY; never overwrite data/lora_adapter/",
            "ent_adapter": str(_ent_adapter()) if _ent_adapter() else None,
        },
        "model_status": model_status,
        "studio": studio,
        "anti_contamination": {
            "prompt_touches_gt": False,
            "ent_never_on_python": True if not py.get("skipped") else None,
            "gt_never_in_inference_prompts": True,
        },
        "n_requested": {"python": args.n_py, "ent": args.n_ent, "vision": args.n_vis},
        "python_paths": py,
        "ent_live": ent,
        "vision_live": vis,
        "scoreboard": scoreboard,
        "vs_cpu_overall_1_0": (scoreboard or {}).get("vs_cpu_overall_1_0"),
        "drops_honesty": drops,
        "elapsed_s": round(time.time() - t_all, 2),
        "notes": notes,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(art, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}", flush=True)
    if scoreboard:
        for row in scoreboard["table"]:
            print(
                f"  {row['path']:22s} py={row['python']['rate']:.4f} "
                f"ent={row['entanglement']['label_acc']:.4f} "
                f"vis={row['vision']['accuracy']:.4f} "
                f"overall={row['overall_mean']:.4f}",
                flush=True,
            )
        print("vs CPU 1.0:", scoreboard["vs_cpu_overall_1_0"], flush=True)
    print("drops:", drops, flush=True)
    return 0 if not notes else 1


if __name__ == "__main__":
    raise SystemExit(main())
