#!/usr/bin/env python3
"""Jev: árbitro mínimo APROBAR/RECHAZAR para propuestas de circuito del LLM.

Tres reglas (todas deben pasar para APROBAR):
1) El circuito compila en PennyLane con puertas h,x,y,z,cx,ry.
2) Energía: si la escena tiene pérdida por rebote, rechazar propuestas que
   afirmen conservación perfecta sin pérdida; aceptar si son consistentes
   con pérdida o silenciosas sobre energía.
3) Visual vs sim: rechazar gates vacías o claims de objeto estático cuando
   la escena es pelota cayendo; exigir que el vector de probs sume ~1 si
   la sim corrió.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

ALLOWED_GATES = {"h", "x", "y", "z", "cx", "ry"}


def _compile_ok(proposal: dict[str, Any]) -> tuple[bool, str]:
    """Rule 1: circuit must compile with allowed gates."""
    gates = proposal.get("gates")
    if not gates or not isinstance(gates, list):
        return False, "gates vacías o ausentes (no compila)"
    n = int(proposal.get("n_qubits", 2))
    if n < 1 or n > 3:
        return False, f"n_qubits={n} fuera de 1–3"
    for g in gates:
        if not isinstance(g, (list, tuple)) or not g:
            return False, f"puerta mal formada: {g!r}"
        op = str(g[0]).lower()
        if op not in ALLOWED_GATES:
            return False, f"puerta no permitida: {op}"
        try:
            if op == "cx":
                if len(g) < 3:
                    return False, "cx requiere control y target"
                int(g[1]); int(g[2])
            elif op == "ry":
                if len(g) < 3:
                    return False, "ry requiere qubit y theta"
                int(g[1]); float(g[2])
            else:
                if len(g) < 2:
                    return False, f"{op} requiere qubit"
                int(g[1])
        except (TypeError, ValueError) as exc:
            return False, f"args inválidos en {g!r}: {exc}"
    # Try real PennyLane compile if available
    try:
        from llm_quantum_bridge import ejecutar_circuito  # type: ignore

        ejecutar_circuito({"n_qubits": n, "gates": gates})
    except ImportError:
        try:
            import importlib.util
            from pathlib import Path

            bridge_path = Path(__file__).resolve().parent / "llm_quantum_bridge.py"
            spec = importlib.util.spec_from_file_location("llm_quantum_bridge", bridge_path)
            bridge = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(bridge)
            bridge.ejecutar_circuito({"n_qubits": n, "gates": gates})
        except Exception as exc:
            return False, f"no compila en PennyLane: {exc}"
    except Exception as exc:
        return False, f"no compila en PennyLane: {exc}"
    return True, "compila"


def _text_blob(proposal: dict[str, Any]) -> str:
    parts = []
    for k in ("nota", "hipotesis", "hypothesis", "reason", "claim", "energy_claim", "descripcion"):
        v = proposal.get(k)
        if isinstance(v, str):
            parts.append(v)
    # also scan nested strings
    try:
        parts.append(json.dumps(proposal, ensure_ascii=False))
    except Exception:
        pass
    return " ".join(parts).lower()


def _scene_has_bounce_energy_loss(scene: dict[str, Any]) -> bool:
    if not scene:
        return False
    # synthetic_fall structured
    if scene.get("perdida_energia_por_rebote") is not None:
        try:
            return float(scene["perdida_energia_por_rebote"]) > 0
        except (TypeError, ValueError):
            pass
    if scene.get("rebotes"):
        return True
    # synthetic_physics_dataset meta
    surface = str(scene.get("surface") or "")
    rest = scene.get("restitution")
    if rest is not None:
        try:
            if float(rest) < 0.99:
                return True
        except (TypeError, ValueError):
            pass
    if "lossy" in surface or "soft" in surface:
        return True
    gov = str(scene.get("governing_law") or "").lower()
    if "restitution" in gov and "1.0" not in gov:
        return True
    # falling ball trajectory implies bounce loss in this lab
    tray = str(scene.get("trayectoria") or scene.get("scene_summary") or "").lower()
    if "rebote" in tray or "bounce" in tray or "caída" in tray or "caida" in tray:
        return True
    return False


def _claims_perfect_energy(proposal: dict[str, Any]) -> bool:
    text = _text_blob(proposal)
    patterns = [
        r"conservaci[oó]n\s+perfecta",
        r"energ[ií]a\s+perfectamente\s+conserv",
        r"sin\s+p[eé]rdida\s+de\s+energ",
        r"perfect\s+energy\s+conservation",
        r"no\s+energy\s+loss",
        r"elastico\s+perfecto",
        r"el[aá]stico\s+perfecto",
        r"restituci[oó]n\s*=?\s*1(\.0+)?\b",
        r"conserva(ción)?\s+(toda\s+)?la\s+energ",
    ]
    for pat in patterns:
        if re.search(pat, text):
            return True
    # explicit flag
    if proposal.get("perfect_energy_conservation") is True:
        return True
    if proposal.get("energy_loss") in (0, 0.0, "0", "none", "ninguna"):
        # only if scene expects loss — checked by caller
        claim = proposal.get("energy_claim") or proposal.get("nota") or ""
        if re.search(r"conserv|sin\s+p[eé]rdida|perfect", str(claim).lower()):
            return True
    return False


def _is_falling_ball_scene(scene: dict[str, Any]) -> bool:
    if not scene:
        return False
    obj = str(scene.get("objeto") or scene.get("object") or scene.get("shape") or "").lower()
    tray = str(scene.get("trayectoria") or scene.get("scene_summary") or "").lower()
    if "pelota" in obj or "ball" in obj or "circle" in obj:
        if "ca" in tray or "fall" in tray or "rebote" in tray or "bounce" in tray:
            return True
    if scene.get("gravity_condition") or scene.get("g_px_s2") or scene.get("gravedad_simulada_px_s2"):
        return True
    if "caída" in tray or "caida" in tray or "falling" in tray:
        return True
    return False


def _claims_static(proposal: dict[str, Any]) -> bool:
    text = _text_blob(proposal)
    patterns = [
        r"objeto\s+est[aá]tico",
        r"sin\s+movimiento",
        r"est[aá]tico",
        r"static\s+object",
        r"no\s+motion",
        r"en\s+reposo(\s+permanente)?",
    ]
    return any(re.search(p, text) for p in patterns)


def _probs_ok(sim_result: dict[str, Any] | None) -> tuple[bool, str]:
    if not sim_result:
        return True, "sim no corrió (omitido)"
    s = sim_result.get("sum_check")
    if s is None and "probabilities" in sim_result:
        try:
            s = sum(float(v) for v in sim_result["probabilities"].values())
        except Exception:
            return False, "probs ilegibles"
    if s is None:
        return False, "sin sum_check ni probabilities"
    if abs(float(s) - 1.0) > 1e-3:
        return False, f"probs suman {s} (≠1)"
    return True, "probs≈1"


def arbitrate(
    proposal: dict[str, Any] | None,
    scene: dict[str, Any] | None,
    sim_result: dict[str, Any] | None,
) -> dict[str, str]:
    """Return {verdict: APROBAR|RECHAZAR, reason: one Spanish line}."""
    proposal = proposal or {}
    scene = scene or {}

    ok, detail = _compile_ok(proposal)
    if not ok:
        return {"verdict": "RECHAZAR", "reason": f"Regla1: {detail}."}

    if _scene_has_bounce_energy_loss(scene) and _claims_perfect_energy(proposal):
        return {
            "verdict": "RECHAZAR",
            "reason": "Regla2: escena con pérdida por rebote pero propuesta afirma conservación perfecta.",
        }

    if not proposal.get("gates"):
        return {"verdict": "RECHAZAR", "reason": "Regla3: gates vacías."}

    if _is_falling_ball_scene(scene) and _claims_static(proposal):
        return {
            "verdict": "RECHAZAR",
            "reason": "Regla3: escena de pelota cayendo pero propuesta afirma objeto estático.",
        }

    if sim_result is not None:
        ok_p, detail_p = _probs_ok(sim_result)
        if not ok_p:
            return {"verdict": "RECHAZAR", "reason": f"Regla3: {detail_p}."}

    return {
        "verdict": "APROBAR",
        "reason": "Circuito válido, consistente con pérdida/escena y probs≈1.",
    }


def _self_test() -> int:
    # 1) good proposal + falling scene with loss
    scene_loss = {
        "objeto": "pelota",
        "trayectoria": "caída vertical con rebotes",
        "perdida_energia_por_rebote": 0.28,
        "rebotes": [12, 24],
    }
    good = {"n_qubits": 2, "gates": [["h", 0], ["cx", 0, 1], ["ry", 1, 0.4]], "nota": "firma con atenuación"}
    # compile via bridge for sim
    import importlib.util
    from pathlib import Path

    bridge_path = Path(__file__).resolve().parent / "llm_quantum_bridge.py"
    spec = importlib.util.spec_from_file_location("llm_quantum_bridge", bridge_path)
    bridge = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(bridge)
    sim = bridge.ejecutar_circuito(good)
    r1 = arbitrate(good, scene_loss, sim)
    assert r1["verdict"] == "APROBAR", r1

    # 2) empty gates
    r2 = arbitrate({"n_qubits": 2, "gates": []}, scene_loss, None)
    assert r2["verdict"] == "RECHAZAR", r2

    # 3) perfect energy claim
    bad_e = dict(good)
    bad_e["nota"] = "conservación perfecta de energía sin pérdida"
    r3 = arbitrate(bad_e, scene_loss, sim)
    assert r3["verdict"] == "RECHAZAR", r3

    # 4) static claim on falling ball
    bad_s = dict(good)
    bad_s["nota"] = "objeto estático sin movimiento"
    r4 = arbitrate(bad_s, scene_loss, sim)
    assert r4["verdict"] == "RECHAZAR", r4

    # 5) bad gate
    r5 = arbitrate({"n_qubits": 2, "gates": [["swap", 0, 1]]}, scene_loss, None)
    assert r5["verdict"] == "RECHAZAR", r5

    print("jev_arbiter --self-test OK")
    print(json.dumps({"example_approve": r1, "example_reject_energy": r3}, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Jev arbiter APROBAR/RECHAZAR")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--proposal", type=str, default=None, help="JSON proposal string")
    p.add_argument("--scene", type=str, default=None, help="JSON scene string")
    p.add_argument("--sim", type=str, default=None, help="JSON sim_result string")
    args = p.parse_args(argv)
    if args.self_test:
        return _self_test()
    proposal = json.loads(args.proposal) if args.proposal else {}
    scene = json.loads(args.scene) if args.scene else {}
    sim = json.loads(args.sim) if args.sim else None
    out = arbitrate(proposal, scene, sim)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
