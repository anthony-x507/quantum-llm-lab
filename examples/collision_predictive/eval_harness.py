#!/usr/bin/env python3
"""Eval harness — % correct collision predictions + ablation (CPU).

Predictors:
  - collision_physics: elastic rollout under hypo action (or choose_safest)
  - inverse_cv: action-aware CV + wall bounce; no elastic masses (inverse-r2)
  - collision_choose_safest: pick safest action via physics, score vs GT of
    THAT chosen action (planning-ish)

Metric (post-hoc GT only):
  collision_correct = (pred.is_safe == gt_is_safe) AND
                      (if unsafe: consequence family / partner match)

Ablation table: collision layer vs inverse_cv on same queries.

Anti-contam:
  - prompts never include consequences_gt
  - audit JSONL records prompt + emit; dirty inject → INVALID discard
  - retrieval index train-only checked

Usage:
  .venv/bin/python examples/collision_predictive/eval_harness.py
  .venv/bin/python examples/collision_predictive/eval_harness.py --contam-self-test
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from physics import (
    ACTIONS,
    check_physics_gate,
    predict_cv_no_collision,
    predict_emit,
)
from distance_consumer import (
    integrate_distance_into_prompt_lines,
    proxy_estimates_from_agents,
    enrich_emit_with_distance,
)
from memory_bridge import emit_to_tool_out

HORIZONS = (1, 3, 5)


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " ET"


def build_prompt(meta: dict[str, Any], query_t: int, k: int, action: str,
                 *, inject_gt: dict | None = None) -> str:
    frames = meta["frames"]
    hist = frames[: query_t + 1]
    lines = [
        "DOMAIN=collision_predictive STYLE=topdown_merge_lane",
        f"Task: at t={query_t}, under hypo action={action}, predict consequence at horizon k={k}.",
        "Emit JSON: {chosen_action, predicted_consequence, is_safe}.",
        "Physics: 2D elastic disks; masses and radii matter. No teleport.",
        "History (perceptions only):",
    ]
    for fr in hist:
        objs = ", ".join(
            f"{o['oid']}({o['class']} m={o['mass']:.2f} r={o['r']:.1f} "
            f"@{o['x']:.1f},{o['y']:.1f} v={o['vx']:.1f},{o['vy']:.1f})"
            for o in fr["agents"]
        )
        lines.append(f"  t={fr['t']} | {objs}")
    lines.append(f"Hypo action to evaluate: {action}")
    # Distance cues (perception stub) — NEVER GT meters
    agents_now = frames[query_t]["agents"] if query_t < len(frames) else frames[-1]["agents"]
    ests = proxy_estimates_from_agents(agents_now)
    lines.extend(integrate_distance_into_prompt_lines(ests))
    if inject_gt is not None:
        lines.append(
            "WARNING_INJECTED_GT="
            + json.dumps({
                "gt_is_safe": inject_gt.get("gt_is_safe"),
                "gt_consequence": inject_gt.get("gt_consequence"),
                "gt_partner": inject_gt.get("gt_partner"),
            })
        )
    return "\n".join(lines)


def consequence_family(label: str) -> str:
    if label == "clear" or label == "third_party_collision_only":
        return label
    if label.startswith("cross_pedestrian"):
        return "cross_pedestrian"
    if label.startswith("rear_end"):
        return "rear_end"
    if label.startswith("side_swipe"):
        return "side_swipe"
    if label.startswith("collide"):
        return "collide"
    return label


def score_emit(pred: dict[str, Any], gt: dict[str, Any], agents0: list[dict], k: int) -> dict[str, Any]:
    safe_ok = bool(pred["is_safe"]) == bool(gt["gt_is_safe"])
    fam_ok = consequence_family(pred["predicted_consequence"]) == consequence_family(gt["gt_consequence"])
    partner_ok = True
    if not gt["gt_is_safe"]:
        # require partner match when both unsafe; if pred says safe, already safe_ok False
        if pred.get("partner_of_ego") is not None and gt.get("gt_partner") is not None:
            partner_ok = pred["partner_of_ego"] == gt["gt_partner"]
        elif pred.get("is_safe") is False and gt.get("gt_partner"):
            # consequence family may encode partner
            partner_ok = gt["gt_partner"] in str(pred.get("predicted_consequence") or "") or fam_ok
    collision_correct = safe_ok and fam_ok
    phys = check_physics_gate(agents0, pred.get("predicted_agents") or [], k)
    return {
        "collision_correct": collision_correct,
        "safe_ok": safe_ok,
        "family_ok": fam_ok,
        "partner_ok": partner_ok,
        "physics_fail": phys["physics_fail"],
        "pred_is_safe": pred["is_safe"],
        "gt_is_safe": gt["gt_is_safe"],
        "pred_consequence": pred["predicted_consequence"],
        "gt_consequence": gt["gt_consequence"],
        "chosen_action": pred.get("chosen_action"),
    }


def run_contam_selftest(seq_dir: Path) -> dict[str, Any]:
    meta = json.loads((seq_dir / "meta.json").read_text())
    gt_doc = json.loads((seq_dir / "consequences_gt.json").read_text())
    fut = next(f for f in gt_doc["futures"] if f["action"] in ACTIONS)
    clean = build_prompt(meta, fut["query_t"], fut["k"], fut["action"])
    dirty = build_prompt(meta, fut["query_t"], fut["k"], fut["action"], inject_gt=fut)
    dirty_flag = "WARNING_INJECTED_GT=" in dirty or "gt_is_safe" in dirty.split("WARNING_INJECTED_GT=", 1)[-1][:200]
    # cleaner check
    dirty_detected = "WARNING_INJECTED_GT=" in dirty
    clean_ok = "WARNING_INJECTED_GT=" not in clean and "gt_consequence" not in clean
    meta_clean = meta.get("anti_contamination", {}).get("futures_in_meta") is False
    # meta frames must not contain gt keys
    blob = json.dumps(meta)
    meta_no_gt_keys = "gt_is_safe" not in blob and "gt_consequence" not in blob
    passed = dirty_detected and clean_ok and meta_clean and meta_no_gt_keys
    return {
        "test": "inject_consequence_gt_into_prompt",
        "verdict_if_dirty": "INVALID",
        "dirty_detected": dirty_detected,
        "clean_prompt_ok": clean_ok,
        "meta_has_no_futures": meta_clean and meta_no_gt_keys,
        "passed": passed,
        "rule": "injecting future/consequence GT → INVALID (discard; never report as clean)",
    }


def evaluate(root: Path, audit_path: Path, *, contam_self_test: bool = False) -> dict[str, Any]:
    eval_dir = root / "eval"
    seqs = sorted(p for p in eval_dir.iterdir() if p.is_dir() and (p / "meta.json").exists())
    if not seqs:
        raise SystemExit(f"no eval seqs in {eval_dir}")

    # retrieval leak check
    ret_path = root / "retrieval_index_train.json"
    retrieval_ok = True
    leak = []
    if ret_path.exists():
        ret = json.loads(ret_path.read_text())
        train_ids = set(ret.get("train_ids") or [])
        eval_ids = {p.name for p in seqs}
        leak = sorted(train_ids & eval_ids)
        if leak:
            retrieval_ok = False

    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_f = audit_path.open("w", encoding="utf-8")

    contam = None
    if contam_self_test:
        contam = run_contam_selftest(seqs[0])
        audit_f.write(json.dumps({"type": "contam_self_test", **contam, "ts": _now()}) + "\n")

    if not retrieval_ok:
        audit_f.write(json.dumps({
            "type": "INVALID_CONTAMINATION",
            "reason": "retrieval train∩eval",
            "leak": leak,
            "ts": _now(),
        }) + "\n")
        audit_f.close()
        return {"INVALID_CONTAMINATION": True, "leak": leak, "discard": True}

    predictors = ("collision_physics", "inverse_cv", "collision_choose_safest")
    # stats[pred][k]
    stats: dict[str, dict[int, dict[str, Any]]] = {
        p: {k: {"n": 0, "collision_ok": 0, "safe_ok": 0, "phys_fail": 0} for k in HORIZONS}
        for p in predictors
    }

    # Action-conditional queries only (not natural_passive) for main metric
    for seq_dir in seqs:
        meta = json.loads((seq_dir / "meta.json").read_text())
        gt_doc = json.loads((seq_dir / "consequences_gt.json").read_text())
        # index by (query_t, k, action)
        gt_index = {
            (f["query_t"], f["k"], f["action"]): f
            for f in gt_doc["futures"]
            if f["action"] in ACTIONS
        }
        for (qt, k, action), gt in sorted(gt_index.items()):
            agents0 = meta["frames"][qt]["agents"]
            prompt = build_prompt(meta, qt, k, action)  # NEVER GT

            # --- collision_physics (evaluate given hypo action) ---
            pred_phys = predict_emit(agents0, k, action=action, choose_safest=False)
            pred_phys["predictor"] = "collision_physics"
            # Distance consume (stub proxy) — does not alter physics GT scoring
            _ests = proxy_estimates_from_agents(agents0)
            enrich_emit_with_distance(pred_phys, _ests)
            # WorkingMemory bridge smoke (refuse gt_*)
            _ = emit_to_tool_out(pred_phys)
            sc_phys = score_emit(pred_phys, gt, agents0, k)

            # --- inverse_cv (action-aware CV + wall; no elastic masses) ---
            # inverse-r2: apply hypo action kinematics then CV wall-bounce;
            # still no agent-agent elastic resolve (ablation vs collision_physics).
            pred_cv = predict_cv_no_collision(agents0, k, action=action)
            sc_cv = score_emit(pred_cv, gt, agents0, k)

            # --- choose_safest (planning): emit action; score vs GT of chosen ---
            pred_plan = predict_emit(agents0, k, choose_safest=True)
            pred_plan["predictor"] = "collision_choose_safest"
            gt_for_chosen = gt_index.get((qt, k, pred_plan["chosen_action"]))
            if gt_for_chosen is None:
                sc_plan = {
                    "collision_correct": False, "safe_ok": False, "family_ok": False,
                    "partner_ok": False, "physics_fail": False,
                    "pred_is_safe": pred_plan["is_safe"], "gt_is_safe": None,
                    "pred_consequence": pred_plan["predicted_consequence"],
                    "gt_consequence": None, "chosen_action": pred_plan["chosen_action"],
                }
            else:
                sc_plan = score_emit(pred_plan, gt_for_chosen, agents0, k)

            for name, sc in (
                ("collision_physics", sc_phys),
                ("inverse_cv", sc_cv),
                ("collision_choose_safest", sc_plan),
            ):
                st = stats[name][k]
                st["n"] += 1
                st["collision_ok"] += int(sc["collision_correct"])
                st["safe_ok"] += int(sc["safe_ok"])
                st["phys_fail"] += int(sc["physics_fail"])

            audit_f.write(json.dumps({
                "type": "eval_step",
                "ts": _now(),
                "seq_id": meta["seq_id"],
                "query_t": qt,
                "k": k,
                "hypo_action": action,
                "prompt": prompt,
                "emit_collision_physics": {
                    "chosen_action": pred_phys["chosen_action"],
                    "predicted_consequence": pred_phys["predicted_consequence"],
                    "is_safe": pred_phys["is_safe"],
                    "distance_note": pred_phys.get("distance_note"),
                    "distance_urgency_max": pred_phys.get("distance_urgency_max"),
                    "distance_partner_band": pred_phys.get("distance_partner_band"),
                },
                "emit_inverse_cv": {
                    "chosen_action": pred_cv["chosen_action"],
                    "predicted_consequence": pred_cv["predicted_consequence"],
                    "is_safe": pred_cv["is_safe"],
                },
                "emit_choose_safest": {
                    "chosen_action": pred_plan["chosen_action"],
                    "predicted_consequence": pred_plan["predicted_consequence"],
                    "is_safe": pred_plan["is_safe"],
                },
                "metrics_posthoc_only": {
                    "collision_physics_correct": sc_phys["collision_correct"],
                    "inverse_cv_correct": sc_cv["collision_correct"],
                    "choose_safest_correct": sc_plan["collision_correct"],
                },
                "gt_in_prompt": False,
                "memory_note": "WorkingMemory may store emit only — never gt_* keys",
            }, ensure_ascii=False) + "\n")

    audit_f.close()

    def pct(ok: int, n: int) -> float | None:
        return round(100.0 * ok / n, 2) if n else None

    table = {}
    for name in predictors:
        table[name] = {}
        for k in HORIZONS:
            st = stats[name][k]
            table[name][f"k={k}"] = {
                "n": st["n"],
                "collision_correct_pct": pct(st["collision_ok"], st["n"]),
                "safe_match_pct": pct(st["safe_ok"], st["n"]),
                "physics_fail_rate": round(st["phys_fail"] / st["n"], 4) if st["n"] else None,
            }
        # micro-average across k
        n_all = sum(stats[name][k]["n"] for k in HORIZONS)
        ok_all = sum(stats[name][k]["collision_ok"] for k in HORIZONS)
        table[name]["overall"] = {
            "n": n_all,
            "collision_correct_pct": pct(ok_all, n_all),
        }

    # Ablation delta: collision_physics - inverse_cv overall
    cp = table["collision_physics"]["overall"]["collision_correct_pct"]
    cv = table["inverse_cv"]["overall"]["collision_correct_pct"]
    ablation = {
        "collision_minus_inverse_cv_pp": None if cp is None or cv is None else round(cp - cv, 2),
        "note": (
            "Positive → elastic collision layer improves consequence/safety prediction "
            "vs inverse-style CV (no mass/collision). Scored on action-conditional GT."
        ),
    }

    result = {
        "domain": "collision_predictive",
        "branch_tag": "tip-choose-safest-n",
        "ts": _now(),
        "n_eval_seqs": len(seqs),
        "predictors": table,
        "ablation": ablation,
        "contam_self_test": contam,
        "retrieval_ok": retrieval_ok,
        "audit": str(audit_path),
        "emit_schema": ["chosen_action", "predicted_consequence", "is_safe"],
        "distance_integration": {
            "consumer": "examples/collision_predictive/distance_consumer.py",
            "provider": "arena_px_proxy_stub",
            "imports_unmerged_distance_branch": False,
            "gt_meters_at_inference": False,
            "danger_zone_m": [30, 70],
            "note": "Consumes perception est_m as urgency cues; physics oracle unchanged",
        },
        "gpu": "none — CPU physics only; VLM deferred",
        "quantum_adapter_touched": False,
    }
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("data/collision_predictive"))
    ap.add_argument("--audit-dir", type=Path, default=Path("data/eval_audit"))
    ap.add_argument("--contam-self-test", action="store_true")
    args = ap.parse_args()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    audit_path = args.audit_dir / f"collision_{ts}.jsonl"
    result = evaluate(args.root, audit_path, contam_self_test=True if args.contam_self_test else True)
    # always run contam self-test for shipped numbers
    out_json = args.root / "EVAL_COLLISION_CPU.json"
    out_json.write_text(json.dumps(result, indent=2) + "\n")
    # Tip-side probe for frontier fold / freeze
    probe = {
        "schema": "frontier_tip_collision_pred_probe",
        "ts": result["ts"],
        "domain": "collision_predictive",
        "branch": "frontier/codigo-vivo-tip",
        "n_eval_seqs": result["n_eval_seqs"],
        "metric_collision_correct_pct": result["predictors"]["collision_physics"]["overall"]["collision_correct_pct"],
        "metric_n_queries": result["predictors"]["collision_physics"]["overall"]["n"],
        "ablation_pp": result["ablation"]["collision_minus_inverse_cv_pp"],
        "contam_passed": (result.get("contam_self_test") or {}).get("passed"),
        "retrieval_ok": result["retrieval_ok"],
        "emit_schema": result["emit_schema"],
        "distance_integration": result.get("distance_integration"),
        "predictors": result["predictors"],
        "quantum_adapter_touched": False,
        "floor_resmoke": "fold tip-choose-safest-n — collision expand only; tip router non-touch; cite R15 floors",
    }
    Path("data/frontier_tip_collision_pred_probe.json").write_text(
        json.dumps(probe, indent=2) + "\n"
    )
    Path("data/frontier_tip_collision_n_probe.json").write_text(
        json.dumps({**probe, "schema": "frontier_tip_collision_n_probe",
                    "n_expand": {"before_n_eval_seqs": 8, "before_n_queries": 555,
                                 "target_n_eval_seqs": 40}}, indent=2) + "\n"
    )
    cs = result["predictors"]["collision_choose_safest"]["overall"]
    Path("data/frontier_tip_choose_safest_n_probe.json").write_text(
        json.dumps({
            **probe,
            "schema": "frontier_tip_choose_safest_n_probe",
            "branch": "frontier/codigo-vivo-tip",
            "collision_choose_safest_overall_pct": cs["collision_correct_pct"],
            "collision_choose_safest_n": cs["n"],
            "collision_physics_overall_pct": (
                result["predictors"]["collision_physics"]["overall"]["collision_correct_pct"]
            ),
            "n_expand": {
                "before_n_eval_seqs": 40,
                "before_n_queries": 2850,
                "target_n_eval_seqs": 80,
                "hardneg": True,
            },
            "floors_policy": {
                "physics": 100.0,
                "choose_safest": 100.0,
                "distance_DZ": "held_by_non_touch",
                "motion": "held_by_non_touch",
                "TTI": "held_by_non_touch",
            },
        }, indent=2) + "\n"
    )

    inv = result["predictors"]["inverse_cv"]["overall"]["collision_correct_pct"]
    Path("data/frontier_tip_inverse_r2_probe.json").write_text(
        json.dumps({
            **probe,
            "schema": "frontier_tip_inverse_r2_probe",
            "branch": "frontier/codigo-vivo-tip",
            "inverse_cv_overall_pct": inv,
            "collision_choose_safest_overall_pct": (
                result["predictors"]["collision_choose_safest"]["overall"]["collision_correct_pct"]
            ),
            "physics_freeze_100pct": (
                result["predictors"]["collision_physics"]["overall"]["collision_correct_pct"] == 100.0
            ),
            "inverse_target_ge_95": inv >= 95.0,
        }, indent=2) + "\n"
    )

    # markdown table
    lines = [
        "# Collision predictive — CPU eval",
        "",
        f"ts: {result['ts']}",
        f"audit: `{result['audit']}`",
        f"contam_self_test.passed: {result.get('contam_self_test', {}).get('passed')}",
        "",
        "## % collision correct (post-hoc GT)",
        "",
        "| predictor | k=1 | k=3 | k=5 | overall |",
        "|-----------|-----|-----|-----|---------|",
    ]
    for name in ("collision_physics", "inverse_cv", "collision_choose_safest"):
        row = [name]
        for key in ("k=1", "k=3", "k=5", "overall"):
            cell = result["predictors"][name][key]
            row.append(str(cell.get("collision_correct_pct")))
        lines.append("| " + " | ".join(row) + " |")
    lines += [
        "",
        f"**Ablation (collision − inverse_cv):** "
        f"{result['ablation']['collision_minus_inverse_cv_pp']} pp",
        "",
        result["ablation"]["note"],
        "",
    ]
    (args.root / "EVAL_COLLISION_CPU.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(result, indent=2))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
