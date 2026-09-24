#!/usr/bin/env python3
"""Fase 1 passive eval — constant-velocity baseline + physics gate (CPU).

Metrics (own numbers, this domain only):
  - % correct position ±tol by horizon k∈{1,3,5}
  - physics_fail rate by k
  - signal accuracy (optional auxiliary)

Predictors:
  - cv_baseline (default): constant-velocity + wall bounce — deterministic,
    no GPU. Use while qlora-ent / classical / video_f1 hold GPU.
  - vlm_base / vlm_lora: stubs gated; write to data/lora_adapter_inverse/
    when GPU free later (NOT implemented here — no train while GPU busy).

Anti-contamination:
  - GT futures loaded ONLY post-hoc from futures_gt.json sidecars
  - Prompt / audit log never includes GT
  - Contam self-test: injecting future GT into prompt → INVALID

Audit: data/eval_audit/inverse_<ts>.jsonl

Usage:
  python examples/inverse_planning/eval_passive.py
  python examples/inverse_planning/eval_passive.py --predictor cv_baseline --tol 8
  python examples/inverse_planning/eval_passive.py --contam-self-test
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

# local import
sys.path.insert(0, str(Path(__file__).resolve().parent))
from physics import check_scene_physics, extrapolate_cv

HORIZONS = (1, 3, 5)
DEFAULT_TOL = 8.0  # pixels


def _now_et_label() -> str:
    # box/Mac may be ET already; stamp with local ISO + ET tag for logs
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " ET"


def load_eval_seqs(root: Path) -> list[Path]:
    eval_dir = root / "eval"
    seqs = sorted(p for p in eval_dir.iterdir() if p.is_dir() and (p / "meta.json").exists())
    return seqs


def build_prompt(meta: dict[str, Any], query_t: int, k: int, *, inject_gt: dict | None = None) -> str:
    """Prompt touches history up to query_t ONLY. Never futures unless inject_gt (contam test)."""
    frames = meta["frames"]
    hist = frames[: query_t + 1]
    lines = [
        "DOMAIN=inverse_planning_passive STYLE=topdown_corridor",
        f"Task: given frames 0..{query_t}, predict object positions and signal at t={query_t + k} (horizon k={k}).",
        "Rules: obey 2D constant-velocity / wall-bounce kinematics. No teleporting.",
        "History:",
    ]
    for fr in hist:
        objs = ", ".join(
            f"{o['oid']}({o['shape']}@{o['x']:.1f},{o['y']:.1f} v={o['vx']:.1f},{o['vy']:.1f})"
            for o in fr["objects"]
        )
        lines.append(f"  t={fr['t']} signal={fr['signal']} | {objs}")
    lines.append(f"Predict JSON for t={query_t + k}: {{signal, objects:[{{oid,x,y}}]}}")
    if inject_gt is not None:
        # INTENTIONAL CONTAMINATION — for self-test only
        lines.append(
            "WARNING_INJECTED_GT="
            + json.dumps({"gt_signal": inject_gt.get("gt_signal"), "gt_objects": inject_gt.get("gt_objects")})
        )
    return "\n".join(lines)


def predict_cv(meta: dict[str, Any], query_t: int, k: int) -> dict[str, Any]:
    frames = meta["frames"]
    # per-object history 0..query_t
    oids = [o["oid"] for o in frames[query_t]["objects"]]
    pred_objs = []
    for oid in oids:
        hist = []
        for fr in frames[: query_t + 1]:
            for o in fr["objects"]:
                if o["oid"] == oid:
                    hist.append(o)
                    break
        pred_objs.append(extrapolate_cv(hist, k))
    # signal: naive hold-last (passive; schedule unknown to baseline)
    # Better: period-agnostic — copy last signal (honest weak baseline on signal)
    pred_signal = frames[query_t]["signal"]
    return {"signal": pred_signal, "objects": pred_objs, "predictor": "cv_baseline"}


def score_prediction(
    pred: dict[str, Any],
    gt: dict[str, Any],
    meta: dict[str, Any],
    query_t: int,
    k: int,
    tol: float,
) -> dict[str, Any]:
    frames = meta["frames"]
    # build histories for physics
    histories = []
    for o in frames[query_t]["objects"]:
        hist = []
        for fr in frames[: query_t + 1]:
            for oo in fr["objects"]:
                if oo["oid"] == o["oid"]:
                    hist.append(oo)
                    break
        histories.append(hist)

    phys = check_scene_physics(histories, pred["objects"], k)

    gt_by_oid = {o["oid"]: o for o in gt["gt_objects"]}
    hits = []
    dists = []
    for po in pred["objects"]:
        go = gt_by_oid.get(po["oid"])
        if go is None:
            hits.append(False)
            continue
        d = float(np.hypot(po["x"] - go["x"], po["y"] - go["y"]))
        dists.append(d)
        hits.append(d <= tol)
    pos_correct = all(hits) and len(hits) > 0
    signal_correct = pred.get("signal") == gt.get("gt_signal")
    return {
        "pos_correct": pos_correct,
        "frac_objs_correct": float(sum(hits) / len(hits)) if hits else 0.0,
        "mean_dist": float(np.mean(dists)) if dists else None,
        "signal_correct": signal_correct,
        "physics_fail": phys["physics_fail"],
        "physics": phys,
        "tol": tol,
    }


def run_contam_selftest(seq_dir: Path) -> dict[str, Any]:
    """Injecting future GT into prompt must be flagged INVALID."""
    meta = json.loads((seq_dir / "meta.json").read_text())
    gt_doc = json.loads((seq_dir / "futures_gt.json").read_text())
    # pick first available future
    fut = gt_doc["futures"][0]
    prompt_clean = build_prompt(meta, fut["query_t"], fut["k"])
    prompt_dirty = build_prompt(meta, fut["query_t"], fut["k"], inject_gt=fut)
    dirty = "WARNING_INJECTED_GT=" in prompt_dirty or "gt_objects" in prompt_dirty
    clean_ok = "WARNING_INJECTED_GT=" not in prompt_clean and "gt_objects" not in prompt_clean
    # Also verify meta has no futures
    meta_clean = "futures" not in meta and meta.get("anti_contamination", {}).get("futures_in_meta") is False
    verdict = "INVALID" if dirty else "UNEXPECTED_CLEAN"
    # The self-test PASSES if we correctly detect contamination as INVALID
    passed = dirty and clean_ok and meta_clean and verdict == "INVALID"
    return {
        "test": "inject_future_gt_into_prompt",
        "verdict_if_dirty": verdict,
        "dirty_detected": dirty,
        "clean_prompt_ok": clean_ok,
        "meta_has_no_futures": meta_clean,
        "passed": passed,
        "rule": "injecting future GT into prompt → INVALID (discard; never report)",
    }


def evaluate(
    root: Path,
    predictor: str,
    tol: float,
    audit_path: Path,
    *,
    contam_self_test: bool = False,
) -> dict[str, Any]:
    seqs = load_eval_seqs(root)
    if not seqs:
        raise SystemExit(f"no eval sequences under {root / 'eval'}")

    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_f = audit_path.open("w")

    # per-k accumulators
    stats = {k: {"n": 0, "pos_ok": 0, "phys_fail": 0, "sig_ok": 0, "dists": []} for k in HORIZONS}
    per_seq = []

    contam_result = None
    if contam_self_test:
        contam_result = run_contam_selftest(seqs[0])
        audit_f.write(json.dumps({"type": "contam_self_test", **contam_result, "ts": _now_et_label()}) + "\n")

    for seq_dir in seqs:
        meta = json.loads((seq_dir / "meta.json").read_text())
        gt_doc = json.loads((seq_dir / "futures_gt.json").read_text())
        # index GT by (query_t, k)
        gt_index = {(f["query_t"], f["k"]): f for f in gt_doc["futures"]}

        seq_scores = []
        for (qt, k), gt in sorted(gt_index.items()):
            prompt = build_prompt(meta, qt, k)  # NEVER includes GT
            if predictor == "cv_baseline":
                pred = predict_cv(meta, qt, k)
            else:
                raise SystemExit(
                    f"predictor={predictor} not available while GPU busy; "
                    "use cv_baseline. VLM base/LoRA → data/lora_adapter_inverse/ later."
                )
            sc = score_prediction(pred, gt, meta, qt, k, tol)
            sc.update({"query_t": qt, "k": k, "seq_id": meta["seq_id"]})
            seq_scores.append(sc)

            stats[k]["n"] += 1
            stats[k]["pos_ok"] += int(sc["pos_correct"])
            stats[k]["phys_fail"] += int(sc["physics_fail"])
            stats[k]["sig_ok"] += int(sc["signal_correct"])
            if sc["mean_dist"] is not None:
                stats[k]["dists"].append(sc["mean_dist"])

            # audit: prompt touches, prediction, NO GT
            audit_f.write(json.dumps({
                "type": "eval_step",
                "ts": _now_et_label(),
                "seq_id": meta["seq_id"],
                "query_t": qt,
                "k": k,
                "predictor": predictor,
                "prompt": prompt,
                "prediction": {
                    "signal": pred["signal"],
                    "objects": [
                        {"oid": o["oid"], "x": o["x"], "y": o["y"]} for o in pred["objects"]
                    ],
                },
                "metrics_no_gt_in_prompt": {
                    "pos_correct": sc["pos_correct"],
                    "physics_fail": sc["physics_fail"],
                    "mean_dist": sc["mean_dist"],
                },
                "gt_in_prompt": False,
                "gt_in_audit_prediction_block": False,
            }) + "\n")

        per_seq.append({"seq_id": meta["seq_id"], "n_queries": len(seq_scores)})

    audit_f.close()

    by_k = {}
    for k in HORIZONS:
        s = stats[k]
        n = max(s["n"], 1)
        by_k[str(k)] = {
            "n": s["n"],
            "pos_acc": s["pos_ok"] / n,
            "pos_ok": s["pos_ok"],
            "physics_fail_rate": s["phys_fail"] / n,
            "physics_fail": s["phys_fail"],
            "signal_acc": s["sig_ok"] / n,
            "mean_dist": float(np.mean(s["dists"])) if s["dists"] else None,
            "tol_px": tol,
        }

    result = {
        "domain": "inverse_planning_passive",
        "fase": 1,
        "predictor": predictor,
        "tol_px": tol,
        "n_eval_seq": len(seqs),
        "by_horizon_k": by_k,
        "contam_self_test": contam_result,
        "audit_log": str(audit_path),
        "adapter_used": None,
        "note": (
            "CPU constant-velocity baseline. VLM base/LoRA deferred until GPU free; "
            "future adapter path data/lora_adapter_inverse/ only. "
            "Quantum data/lora_adapter/ READ-ONLY — not used."
        ),
        "ts": _now_et_label(),
    }
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=Path("data/inverse_planning"))
    ap.add_argument("--predictor", default="cv_baseline", choices=["cv_baseline", "vlm_base", "vlm_lora"])
    ap.add_argument("--tol", type=float, default=DEFAULT_TOL)
    ap.add_argument("--contam-self-test", action="store_true", default=True)
    ap.add_argument("--no-contam-self-test", action="store_false", dest="contam_self_test")
    ap.add_argument("--audit-dir", type=Path, default=Path("data/eval_audit"))
    ap.add_argument("--out-json", type=Path, default=None)
    args = ap.parse_args()

    if args.predictor in ("vlm_base", "vlm_lora"):
        raise SystemExit(
            "GPU held by qlora-ent/classical/video_f1 — refusing VLM eval. "
            "Re-run with --predictor cv_baseline. Later: data/lora_adapter_inverse/."
        )

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    audit_path = args.audit_dir / f"inverse_{ts}.jsonl"
    result = evaluate(
        args.root,
        args.predictor,
        args.tol,
        audit_path,
        contam_self_test=args.contam_self_test,
    )

    out_json = args.out_json or (args.root / "EVAL_PASSIVE_CV.json")
    out_json.write_text(json.dumps(result, indent=2) + "\n")

    print("=== Inverse planning Fase 1 — passive eval ===")
    print(f"predictor={result['predictor']}  tol={result['tol_px']}px  n_seq={result['n_eval_seq']}")
    print(f"{'k':>4}  {'pos_acc':>8}  {'phys_fail':>10}  {'sig_acc':>8}  {'mean_d':>8}  n")
    for k, row in result["by_horizon_k"].items():
        md = f"{row['mean_dist']:.2f}" if row["mean_dist"] is not None else "n/a"
        print(
            f"{k:>4}  {row['pos_acc']:>8.3f}  {row['physics_fail_rate']:>10.3f}  "
            f"{row['signal_acc']:>8.3f}  {md:>8}  {row['n']}"
        )
    if result.get("contam_self_test"):
        c = result["contam_self_test"]
        print(f"contam_self_test: passed={c['passed']} verdict={c['verdict_if_dirty']}")
    print(f"audit: {audit_path}")
    print(f"wrote: {out_json}")


if __name__ == "__main__":
    main()
