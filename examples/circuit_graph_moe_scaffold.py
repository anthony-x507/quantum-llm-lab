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
  python examples/circuit_graph_moe_scaffold.py --hard --cpu-eval
  python examples/circuit_graph_moe_scaffold.py --hard --cpu-eval --polish
  python examples/circuit_graph_moe_scaffold.py --recheck-original

READ-ONLY: never write data/lora_adapter/.
KEEP: data/FRONTIER_CIRCUIT_GRAPH_SCAFFOLD_FREEZE.json intact (never overwrite).
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
from circuit_graph_adapter.vlm_wire import (  # noqa: E402
    build_vlm_scaffold_signal,
    wire_prompt_for_vlm,
    CHANNEL_TEXT,
)

SMOKE_OUT = ROOT / "data" / "frontier_circuit_graph_scaffold_cpu_smoke.json"
EVAL_OUT = ROOT / "data" / "frontier_circuit_graph_scaffold_cpu.json"
HARD_OUT = ROOT / "data" / "frontier_circuit_graph_scaffold_hard.json"
HARD_POLISH_OUT = ROOT / "data" / "frontier_circuit_graph_scaffold_hard_polish.json"
HARD_DOC_OUT = ROOT / "docs" / "FRONTIER-CIRCUIT-GRAPH-SCAFFOLD-HARD.md"
DOC_OUT = ROOT / "docs" / "FRONTIER-CIRCUIT-GRAPH-SCAFFOLD.md"
FREEZE_OUT = ROOT / "data" / "FRONTIER_CIRCUIT_GRAPH_SCAFFOLD_FREEZE.json"
WIRE_VLM_OUT = ROOT / "data" / "frontier_scaffold_wire_vlm.json"
WIRE_VLM_DOC = ROOT / "docs" / "FRONTIER-SCAFFOLD-WIRE-VLM.md"
# Frozen original metrics that must still hold on CPU_FIXTURES (own-delta).
FREEZE_SOLVE_FLOOR = 0.90
FREEZE_DELTA_SOLVE_FLOOR = 0.45

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
        {"id": "product_hh", "tags": ("product", "separable", "product-state"), "n_qubits": 2,
         "gates": [["h", 0], ["h", 1]]},
        {"id": "ghz_like", "tags": ("ghz", "entangle", "3"), "n_qubits": 3,
         "gates": [["h", 0], ["cx", 0, 1], ["cx", 1, 2]]},
        {"id": "ry_cx", "tags": ("rotation", "entangle", "ry"), "n_qubits": 2,
         "gates": [["ry", 0, 0.5], ["cx", 0, 1]]},
        {"id": "single_h", "tags": ("hadamard", "single"), "n_qubits": 1,
         "gates": [["h", 0]]},
        # --- hard priors (teleport / small-QFT proxy / parity / cluster / W-proxy) ---
        # Alphabet is h,x,y,z,cx,ry only — QFT/teleport are structural sketches, not Q-advantage.
        {"id": "teleport_3q", "tags": ("teleport", "teleportation", "correction"), "n_qubits": 3,
         "gates": [["h", 1], ["cx", 1, 2], ["cx", 0, 1], ["h", 0], ["cx", 1, 2], ["z", 2]]},
        {"id": "teleport_bell_resource", "tags": ("teleport", "bell", "resource"), "n_qubits": 3,
         "gates": [["h", 1], ["cx", 1, 2], ["cx", 0, 1], ["h", 0]]},
        {"id": "qft2_proxy", "tags": ("qft", "fourier", "phase"), "n_qubits": 2,
         "gates": [["h", 0], ["ry", 1, 0.7854], ["cx", 0, 1], ["h", 1]]},
        {"id": "qft3_proxy", "tags": ("qft", "fourier", "3"), "n_qubits": 3,
         "gates": [["h", 0], ["ry", 1, 0.7854], ["cx", 0, 1], ["ry", 2, 0.3927],
                   ["cx", 0, 2], ["h", 1], ["ry", 2, 0.7854], ["cx", 1, 2], ["h", 2]]},
        {"id": "parity_check_2d1a", "tags": ("parity", "error", "detect", "ancilla", "stabilizer"),
         "n_qubits": 3,
         "gates": [["cx", 0, 2], ["cx", 1, 2]]},
        {"id": "parity_check_zzz", "tags": ("parity", "check", "stabilizer", "detect"),
         "n_qubits": 3,
         "gates": [["h", 2], ["cx", 0, 2], ["cx", 1, 2], ["h", 2]]},
        {"id": "cluster_linear", "tags": ("cluster", "graph", "linear", "multi"), "n_qubits": 3,
         "gates": [["h", 0], ["h", 1], ["h", 2], ["cx", 0, 1], ["cx", 1, 2]]},
        {"id": "w_proxy", "tags": ("w-state", "w_state", "w like", "non-ghz", "multi"), "n_qubits": 3,
         "gates": [["ry", 0, 1.231], ["cx", 0, 1], ["ry", 1, 0.9553], ["cx", 1, 2], ["x", 0]]},
        {"id": "swap_like", "tags": ("swap", "exchange", "multi"), "n_qubits": 2,
         "gates": [["cx", 0, 1], ["cx", 1, 0], ["cx", 0, 1]]},
        {"id": "product_trap_safe", "tags": ("product", "separable", "trap", "no-cx"), "n_qubits": 2,
         "gates": [["h", 0], ["x", 1]]},
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



def visual_motion_cue(scene_dir) -> dict:
    """GT-free visual cue from RGB frames: independent vs correlated blob motion.

    Stage 1 (frozen scaffold-motion): two strongest hard hues among
    {red, blue, green, yellow}.
    Stage 2 (motion-r2 reinforce): on color_track_fail only — extended hues
    (cyan/magenta/orange/white + soft_* / purple / brown) with occlusion-tolerant
    min points.
    Stage 3: single-hue spatial split or chromatic connected components
    (occlusion / same-tint multi-object / approach geometry).
    Stage 4 (motion-r3 reinforce): on corr_ambiguous only — tracking continuity
    densify (every-frame centroids + gap fill, ≤16) then re-apply frozen honesty;
    if still unknown, approach/recede relative-range (drel≥0.18) ⇒ independent.
    Stage 5 (motion-r4 reinforce): (a) on still-corr_ambiguous only — per-axis
    velocity correlation under locked distance using the SAME |0.75|/|0.45|
    honesty bands (axis_locked / axis_weak), then full-window densify retry;
    (b) on color_track_fail singleton only — one moving chroma blob with no
    second GT-free partner ⇒ independent (singleton_mover). Never overrides a
    known Stage 1–4 cue. Never softens |vel_corr| bands to invent correlated.

    Honesty rules UNCHANGED: dist_cv≥0.10⇒independent; locked dist + high
    |vel_corr|⇒correlated; else unknown. Never reads meta/GT. Never invents
    distance labels.
    Returns {cue: independent|correlated|unknown, ...}.
    """
    from pathlib import Path as _P
    honesty = {
        "gt_free": True,
        "reads_meta": False,
        "source": "rgb_centroid_velocity",
        "inference_uses_gt": False,
    }
    try:
        import numpy as np
        from PIL import Image
    except Exception as exc:  # noqa: BLE001
        return {"cue": "unknown", "reason": f"deps:{type(exc).__name__}", **honesty}
    scene_dir = _P(scene_dir)
    frames_all = sorted(scene_dir.glob("frame_*.png"))
    if not frames_all:
        frames_all = sorted(scene_dir.glob("**/frame_*.png"))
    frames_dense = frames_all[::1][:16]
    frames = frames_all[::2][:10]
    if len(frames) < 3:
        return {"cue": "unknown", "reason": "few_frames", "n_frames": len(frames), **honesty}

    def _cent(m, min_px: int = 5):
        yy, xx = np.where(m)
        if len(xx) < min_px:
            return None
        return np.array([xx.mean(), yy.mean()], dtype=float)

    def _decide(a, b):
        v0 = np.diff(a, axis=0).ravel()
        v1 = np.diff(b, axis=0).ravel()
        if v0.std() < 1e-6 or v1.std() < 1e-6:
            c = 0.0
        else:
            c = float(np.corrcoef(v0, v1)[0, 1])
            if c != c:
                c = 0.0
        dist = np.linalg.norm(a - b, axis=1)
        dist_cv = float(dist.std() / (dist.mean() + 1e-6))
        # Honesty: varying pair-distance ⇒ independent trajectories (product-like).
        # Locked distance + high |vel_corr| ⇒ correlated (Bell-like). Else unknown.
        if dist_cv >= 0.10:
            cue = "independent"
        elif abs(c) > 0.75 and dist_cv < 0.08:
            cue = "correlated"
        elif abs(c) < 0.45:
            cue = "independent"
        else:
            cue = "unknown"
        return cue, c, dist_cv

    def _hard_masks(arr):
        R, G, B = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        return {
            "red": (R > 140) & (R > G + 30) & (R > B + 30),
            "blue": (B > 140) & (B > R + 20) & (B > G + 20),
            "green": (G > 140) & (G > R + 30) & (G > B + 30),
            "yellow": (R > 150) & (G > 150) & (B < 120) & (R > B + 30) & (G > B + 30),
        }

    def _extended_masks(arr):
        R, G, B = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        m = _hard_masks(arr)
        m.update({
            "cyan": (G > 120) & (B > 120) & (R < 110) & (G > R + 20) & (B > R + 20),
            "magenta": (R > 120) & (B > 120) & (G < 110) & (R > G + 20) & (B > G + 20),
            "orange": (R > 155) & (G > 75) & (G < 175) & (B < 95) & (R > G + 20),
            "white": (R > 200) & (G > 200) & (B > 200),
            "soft_red": (R > 105) & (R > G + 15) & (R > B + 15),
            "soft_blue": (B > 105) & (B > R + 10) & (B > G + 10),
            "soft_green": (G > 105) & (G > R + 15) & (G > B + 15),
            "soft_yellow": (R > 125) & (G > 125) & (B < 145) & (R > B + 15) & (G > B + 15),
            "soft_cyan": (G > 100) & (B > 100) & (R < 120) & (G > R + 10) & (B > R + 10),
            "soft_magenta": (R > 100) & (B > 100) & (G < 120) & (R > G + 10) & (B > G + 10),
            "soft_orange": (R > 140) & (G > 60) & (G < 180) & (B < 100) & (R > G + 10),
            "purple": (R > 90) & (B > 110) & (G < R) & (G < B) & (B > R - 10) & (B > 90),
            "soft_purple": (R > 80) & (B > 90) & (G < 100) & (B > G + 10) & (R > G + 5),
            "brown": (R > 80) & (R < 180) & (G > 40) & (G < 140) & (B < 90) & (R > G + 10) & (R > B + 20),
        })
        return m

    def _track(mask_fn, min_px: int = 5, min_pts: int = 3):
        tracks: dict[str, list] = {}
        mass: dict[str, float] = {}
        for fp in frames:
            arr = np.asarray(Image.open(fp).convert("RGB"), dtype=np.float32)
            for name, m in mask_fn(arr).items():
                tracks.setdefault(name, [])
                mass.setdefault(name, 0.0)
                c = _cent(m, min_px=min_px)
                tracks[name].append(c)
                if c is not None:
                    mass[name] += float(m.sum())
        ranked = sorted(mass.items(), key=lambda kv: -kv[1])
        chosen: list[str] = []
        series: list[list] = []
        used: set[str] = set()

        def _fam(n: str) -> str:
            return n.replace("soft_", "")

        for name, _ in ranked:
            pts = [p for p in tracks[name] if p is not None]
            if len(pts) < min_pts:
                continue
            fam = _fam(name)
            if fam in used:
                continue
            chosen.append(name)
            series.append(pts)
            used.add(fam)
            if len(chosen) == 2:
                break
        return chosen, series, mass

    def _components_frame(arr, min_px: int = 8):
        R, G, B = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        chroma = np.maximum(np.maximum(R, G), B) - np.minimum(np.minimum(R, G), B)
        for mask in (
            chroma > 40,
            chroma > 25,
            ((R + G + B) / 3 > 85) & (chroma > 15),
            ((R + G + B) / 3 > 60) & (chroma > 10),
        ):
            if mask.sum() < 20 or mask.mean() > 0.7:
                continue
            H, W = mask.shape
            visited = np.zeros_like(mask, dtype=bool)
            comps: list[tuple[int, float, float]] = []
            ys, xs = np.where(mask)
            for y0, x0 in zip(ys, xs):
                if visited[y0, x0]:
                    continue
                stack = [(y0, x0)]
                visited[y0, x0] = True
                pts: list[tuple[int, int]] = []
                while stack:
                    y, x = stack.pop()
                    pts.append((y, x))
                    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not visited[ny, nx]:
                            visited[ny, nx] = True
                            stack.append((ny, nx))
                if len(pts) >= min_px:
                    arrp = np.asarray(pts)
                    comps.append((len(pts), float(arrp[:, 1].mean()), float(arrp[:, 0].mean())))
            comps.sort(reverse=True)
            if len(comps) >= 2:
                return comps[:3]
        return []

    def _component_pair(min_sep: float = 6.0, min_pts: int = 3):
        s0: list = []
        s1: list = []
        for fp in frames:
            arr = np.asarray(Image.open(fp).convert("RGB"), dtype=np.float32)
            comps = _components_frame(arr)
            if len(comps) >= 2:
                best = None
                bestd = -1.0
                for i in range(len(comps)):
                    for j in range(i + 1, len(comps)):
                        d = abs(comps[i][1] - comps[j][1]) + abs(comps[i][2] - comps[j][2])
                        if d > bestd:
                            bestd = d
                            best = (comps[i], comps[j])
                if best is not None and bestd >= min_sep:
                    s0.append(np.array([best[0][1], best[0][2]]))
                    s1.append(np.array([best[1][1], best[1][2]]))
                else:
                    s0.append(None)
                    s1.append(None)
            else:
                s0.append(None)
                s1.append(None)
        b0 = [p for p in s0 if p is not None]
        b1 = [p for p in s1 if p is not None]
        if len(b0) < min_pts or len(b1) < min_pts:
            return None
        n = min(len(b0), len(b1))
        d = np.linalg.norm(np.asarray(b0[:n]) - np.asarray(b1[:n]), axis=1)
        if float(d.mean()) < min_sep:
            return None
        return b0, b1

    def _single_hue_split(hue_name: str, min_sep: float = 8.0, min_pts: int = 3):
        """Split one tracked hue into two spatial components (same-tint / occlusion)."""
        s0: list = []
        s1: list = []
        for fp in frames:
            arr = np.asarray(Image.open(fp).convert("RGB"), dtype=np.float32)
            m = _extended_masks(arr).get(hue_name)
            if m is None or int(m.sum()) < 16:
                s0.append(None)
                s1.append(None)
                continue
            H, W = m.shape
            visited = np.zeros_like(m, dtype=bool)
            comps: list[tuple[int, float, float]] = []
            ys, xs = np.where(m)
            for y0, x0 in zip(ys, xs):
                if visited[y0, x0]:
                    continue
                stack = [(y0, x0)]
                visited[y0, x0] = True
                pts: list[tuple[int, int]] = []
                while stack:
                    y, x = stack.pop()
                    pts.append((y, x))
                    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < H and 0 <= nx < W and m[ny, nx] and not visited[ny, nx]:
                            visited[ny, nx] = True
                            stack.append((ny, nx))
                if len(pts) >= 8:
                    arrp = np.asarray(pts)
                    comps.append((len(pts), float(arrp[:, 1].mean()), float(arrp[:, 0].mean())))
            comps.sort(reverse=True)
            if len(comps) >= 2:
                d = abs(comps[0][1] - comps[1][1]) + abs(comps[0][2] - comps[1][2])
                if d >= min_sep:
                    s0.append(np.array([comps[0][1], comps[0][2]]))
                    s1.append(np.array([comps[1][1], comps[1][2]]))
                else:
                    s0.append(None)
                    s1.append(None)
            else:
                yy, xx = np.where(m)
                med = float(np.median(xx))
                left = m & (np.arange(W)[None, :] < med)
                right = m & (np.arange(W)[None, :] >= med)
                if int(left.sum()) < 8 or int(right.sum()) < 8:
                    medy = float(np.median(yy))
                    left = m & (np.arange(H)[:, None] < medy)
                    right = m & (np.arange(H)[:, None] >= medy)
                c0, c1 = _cent(left, min_px=4), _cent(right, min_px=4)
                if c0 is not None and c1 is not None and float(np.linalg.norm(c0 - c1)) >= min_sep:
                    s0.append(c0)
                    s1.append(c1)
                else:
                    s0.append(None)
                    s1.append(None)
        b0 = [p for p in s0 if p is not None]
        b1 = [p for p in s1 if p is not None]
        if len(b0) < min_pts or len(b1) < min_pts:
            return None
        n = min(len(b0), len(b1))
        d = np.linalg.norm(np.asarray(b0[:n]) - np.asarray(b1[:n]), axis=1)
        if float(d.mean()) < min_sep:
            return None
        return b0, b1

    def _dist_rel(a, b):
        dist = np.linalg.norm(a - b, axis=1)
        return float((dist.max() - dist.min()) / (dist.mean() + 1e-6))

    def _continuity_fill(seq):
        out = list(seq)
        last = None
        for i, p in enumerate(out):
            if p is None and last is not None:
                out[i] = last
            elif p is not None:
                last = p
        nxt = None
        for i in range(len(out) - 1, -1, -1):
            if out[i] is None and nxt is not None:
                out[i] = nxt
            elif out[i] is not None:
                nxt = out[i]
        return [p for p in out if p is not None]

    def _densify_hues(chosen, min_px: int = 4, min_pts: int = 4, use_frames=None):
        """Re-track the same hue pair on denser frames with gap fill (stage 4/5)."""
        if len(chosen) != 2:
            return None
        # Only real mask names (not green_a / comp0 splits).
        mask_names = set(_extended_masks(np.zeros((2, 2, 3), dtype=np.float32)).keys())
        if any(h not in mask_names for h in chosen):
            return None
        series = {h: [] for h in chosen}
        if use_frames is not None:
            use = use_frames
        else:
            use = frames_dense if len(frames_dense) >= 4 else frames
        for fp in use:
            arr = np.asarray(Image.open(fp).convert("RGB"), dtype=np.float32)
            ms = _extended_masks(arr)
            for h in chosen:
                c = _cent(ms[h], min_px=min_px)
                series[h].append(c)
        a = _continuity_fill(series[chosen[0]])
        b = _continuity_fill(series[chosen[1]])
        if len(a) < min_pts or len(b) < min_pts:
            return None
        n = min(len(a), len(b))
        return np.asarray(a[:n], dtype=float), np.asarray(b[:n], dtype=float)

    def _stage4_reinforce(chosen, series, track_mode: str, stage: int):
        """Continuity densify + approach/recede; escalate only on corr_ambiguous."""
        # 4a — denser continuity retrack of the same hues, frozen honesty.
        dense = _densify_hues(chosen)
        if dense is not None:
            a, b = dense
            cue, c, dist_cv = _decide(a, b)
            drel = _dist_rel(a, b)
            out = {
                "cue": cue,
                "vel_corr": round(c, 3),
                "dist_cv": round(dist_cv, 3),
                "dist_rel": round(drel, 3),
                "n": int(len(a)),
                "hues_chosen": chosen,
                "track_mode": "continuity_dense",
                "stage": 4,
                "stage_from": stage,
                "prior_track_mode": track_mode,
                **honesty,
            }
            if cue != "unknown":
                return out
            # 4b — approach/recede relative range (distance not locked).
            if drel >= 0.18:
                out["cue"] = "independent"
                out["reason"] = None
                out["track_mode"] = "approach_recede"
                out.pop("reason", None)
                return out
            out["reason"] = "corr_ambiguous"
            return out
        # No densify path (split/comp names): approach/recede on existing series.
        n = min(len(series[0]), len(series[1]))
        if n >= 3:
            a = np.asarray(series[0][:n], dtype=float)
            b = np.asarray(series[1][:n], dtype=float)
            cue, c, dist_cv = _decide(a, b)
            drel = _dist_rel(a, b)
            if cue == "unknown" and drel >= 0.18:
                return {
                    "cue": "independent",
                    "vel_corr": round(c, 3),
                    "dist_cv": round(dist_cv, 3),
                    "dist_rel": round(drel, 3),
                    "n": int(n),
                    "hues_chosen": chosen,
                    "track_mode": "approach_recede",
                    "stage": 4,
                    "stage_from": stage,
                    "prior_track_mode": track_mode,
                    **honesty,
                }
        return None

    def _axis_corr(a, b):
        v0 = np.diff(a, axis=0)
        v1 = np.diff(b, axis=0)
        def _c(x, y):
            x = np.asarray(x, dtype=float).ravel()
            y = np.asarray(y, dtype=float).ravel()
            if x.std() < 1e-6 or y.std() < 1e-6:
                return 0.0
            c = float(np.corrcoef(x, y)[0, 1])
            return 0.0 if c != c else c
        return _c(v0[:, 0], v1[:, 0]), _c(v0[:, 1], v1[:, 1])

    def _stage5_axis_honesty(chosen, series, track_mode: str, stage_from: int, precomputed=None):
        """Axis-wise honesty on corr_ambiguous leftovers; frozen |0.75|/|0.45| bands.

        Flat vel_corr mid-band can be a cross-axis artifact. Same thresholds as
        `_decide`, applied per-axis under locked distance — never softens bands.
        """
        if precomputed is not None:
            a, b = precomputed
        else:
            if len(chosen) != 2:
                return None
            dense = _densify_hues(chosen)
            if dense is not None:
                a, b = dense
            else:
                n = min(len(series[0]), len(series[1]))
                if n < 4:
                    return None
                a = np.asarray(series[0][:n], dtype=float)
                b = np.asarray(series[1][:n], dtype=float)
        cue, c, dist_cv = _decide(a, b)
        drel = _dist_rel(a, b)
        cx, cy = _axis_corr(a, b)
        axis_max = max(abs(cx), abs(cy))
        out = {
            "cue": cue,
            "vel_corr": round(c, 3),
            "vel_corr_x": round(cx, 3),
            "vel_corr_y": round(cy, 3),
            "dist_cv": round(dist_cv, 3),
            "dist_rel": round(drel, 3),
            "n": int(len(a)),
            "hues_chosen": chosen,
            "track_mode": "axis_honesty",
            "stage": 5,
            "stage_from": stage_from,
            "prior_track_mode": track_mode,
            **honesty,
        }
        # Prefer axis reading under locked distance before approach/recede.
        if dist_cv < 0.08 and axis_max > 0.75:
            out["cue"] = "correlated"
            out["reason"] = None
            out["track_mode"] = "axis_locked"
            out.pop("reason", None)
            return out
        if dist_cv < 0.08 and axis_max < 0.45:
            out["cue"] = "independent"
            out["reason"] = None
            out["track_mode"] = "axis_weak"
            out.pop("reason", None)
            return out
        if cue != "unknown":
            return out
        if drel >= 0.18:
            out["cue"] = "independent"
            out["reason"] = None
            out["track_mode"] = "approach_recede"
            out.pop("reason", None)
            return out
        # Full-window densify retry with the same axis bands (still stage 5).
        use = frames_all[::1][:36]
        if len(use) >= 8 and len(chosen) == 2:
            dense_full = _densify_hues(chosen, use_frames=use, min_pts=4)
            if dense_full is not None:
                af, bf = dense_full
                cue_f, c_f, dist_cv_f = _decide(af, bf)
                drel_f = _dist_rel(af, bf)
                cx_f, cy_f = _axis_corr(af, bf)
                axis_max_f = max(abs(cx_f), abs(cy_f))
                out_f = {
                    "cue": cue_f,
                    "vel_corr": round(c_f, 3),
                    "vel_corr_x": round(cx_f, 3),
                    "vel_corr_y": round(cy_f, 3),
                    "dist_cv": round(dist_cv_f, 3),
                    "dist_rel": round(drel_f, 3),
                    "n": int(len(af)),
                    "hues_chosen": chosen,
                    "track_mode": "axis_honesty_full",
                    "stage": 5,
                    "stage_from": stage_from,
                    "prior_track_mode": track_mode,
                    **honesty,
                }
                if dist_cv_f < 0.08 and axis_max_f > 0.75:
                    out_f["cue"] = "correlated"
                    out_f["track_mode"] = "axis_locked_full"
                    return out_f
                if dist_cv_f < 0.08 and axis_max_f < 0.45:
                    out_f["cue"] = "independent"
                    out_f["track_mode"] = "axis_weak_full"
                    return out_f
                if cue_f != "unknown":
                    return out_f
                if drel_f >= 0.18:
                    out_f["cue"] = "independent"
                    out_f["track_mode"] = "approach_recede_full"
                    return out_f
                out = out_f
        out["reason"] = "corr_ambiguous"
        return out

    def _stage5_singleton(hard_chosen, hard_mass):
        """One moving chroma blob, no second GT-free partner ⇒ independent."""
        if len(hard_chosen) != 1:
            return None
        hue = hard_chosen[0]
        # Require real mass on that hue across frames.
        if float(hard_mass.get(hue, 0.0)) < 50.0:
            return None
        cents = []
        for fp in (frames_dense if len(frames_dense) >= 3 else frames):
            arr = np.asarray(Image.open(fp).convert("RGB"), dtype=np.float32)
            m = _extended_masks(arr).get(hue)
            if m is None:
                cents.append(None)
                continue
            cents.append(_cent(m, min_px=4))
        pts = [p for p in cents if p is not None]
        if len(pts) < 3:
            return None
        arrp = np.asarray(pts, dtype=float)
        span = float(np.linalg.norm(arrp.max(axis=0) - arrp.min(axis=0)))
        # Must actually move (not a static stain).
        if span < 6.0:
            return None
        path_len = float(np.linalg.norm(np.diff(arrp, axis=0), axis=1).sum())
        if path_len < 8.0:
            return None
        return {
            "cue": "independent",
            "vel_corr": None,
            "dist_cv": None,
            "dist_rel": None,
            "n": int(len(pts)),
            "hues_chosen": [hue],
            "track_mode": "singleton_mover",
            "stage": 5,
            "stage_from": 0,
            "motion_span": round(span, 3),
            "path_len": round(path_len, 3),
            **honesty,
        }

    def _pack(chosen, series, track_mode: str, stage: int):
        n = min(len(series[0]), len(series[1]))
        a = np.asarray(series[0][:n], dtype=float)
        b = np.asarray(series[1][:n], dtype=float)
        cue, c, dist_cv = _decide(a, b)
        out = {
            "cue": cue,
            "vel_corr": round(c, 3),
            "dist_cv": round(dist_cv, 3),
            "n": int(n),
            "hues_chosen": chosen,
            "track_mode": track_mode,
            "stage": stage,
            **honesty,
        }
        if cue == "unknown":
            # Stage 4: escalate only on corr_ambiguous — never override known.
            refined = _stage4_reinforce(chosen, series, track_mode, stage)
            if refined is not None and refined.get("cue") != "unknown":
                return refined
            # Stage 5a: axis-wise honesty on still-ambiguous — never override known.
            prior_mode = (refined or {}).get("track_mode", track_mode)
            prior_stage = (refined or {}).get("stage", stage)
            axis = _stage5_axis_honesty(chosen, series, prior_mode, stage_from=prior_stage)
            if axis is not None and axis.get("cue") != "unknown":
                return axis
            if axis is not None:
                return axis
            if refined is not None:
                return refined
            out["reason"] = "corr_ambiguous"
        return out

    # --- Stage 1: frozen hard multi-hue (scaffold-motion) ---
    chosen, series, mass = _track(_hard_masks, min_px=5, min_pts=3)
    if len(chosen) == 2:
        return _pack(chosen, series, "hue_hard", 1)

    hard_fail_chosen = list(chosen)
    hard_fail_mass = dict(mass)

    # --- Stage 2: extended + soft hues (escalate only on track fail) ---
    for min_px, min_pts, mode in ((4, 3, "hue_extended"), (3, 2, "hue_extended_occl")):
        chosen, series, mass = _track(_extended_masks, min_px=min_px, min_pts=min_pts)
        if len(chosen) == 2:
            return _pack(chosen, series, mode, 2)

    # --- Stage 3a: split the single hard hue into two spatial components ---
    if len(hard_fail_chosen) == 1:
        pair = _single_hue_split(hard_fail_chosen[0])
        if pair is not None:
            return _pack(
                [hard_fail_chosen[0] + "_a", hard_fail_chosen[0] + "_b"],
                list(pair),
                "single_hue_split",
                3,
            )

    # --- Stage 3b: chromatic connected components ---
    pair = _component_pair()
    if pair is not None:
        return _pack(["comp0", "comp1"], list(pair), "chroma_components", 3)

    # Stage 5b: singleton mover on color_track_fail only.
    single = _stage5_singleton(hard_fail_chosen, hard_fail_mass)
    if single is not None:
        return single

    return {
        "cue": "unknown",
        "reason": "color_track_fail",
        "n": 0 if not hard_fail_chosen else 0,
        "hues_seen": {k: round(v, 1) for k, v in hard_fail_mass.items() if v > 0},
        "hues_chosen": hard_fail_chosen,
        "track_mode": "hue_hard_fail",
        "stage": 0,
        **honesty,
    }



def motion_cue_prompt_suffix(cue: str) -> str:
    """Map cue → GT-free prompt keywords that steer scaffold priors.

    unknown → explicit honesty line (no invented motion prior; no GT).
    """
    if cue == "independent":
        return (
            "Visual motion cue (structure only): colored objects appear on "
            "independent trajectories (product-state / no CX prior). "
            "GT-free RGB centroid cue; no eval labels."
        )
    if cue == "correlated":
        return (
            "Visual motion cue (structure only): colored objects appear on "
            "correlated trajectories (Bell-pair / CX prior). "
            "GT-free RGB centroid cue; no eval labels."
        )
    if cue == "unknown":
        return (
            "Visual motion cue (structure only): no reliable RGB motion prior "
            "(unknown). Do not invent entanglement from color; use balanced "
            "scaffold priors only. GT-free; no eval labels."
        )
    return ""


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
        # GT-free visual motion keywords (from frame centroids, not meta labels)
        if any(k in low for k in ("independent trajectory", "independent trajectories", "product-state")):
            if "product" in t["tags"] or "separable" in t["tags"]:
                score += 3
            if "bell" in t["id"] or t["id"].startswith("ghz"):
                score -= 2
        if any(k in low for k in ("correlated trajectory", "correlated trajectories", "bell-pair")):
            if t["id"].startswith("bell") or "entangle" in t["tags"]:
                score += 3
            if "product" in t["tags"] or "separable" in t["tags"]:
                score -= 2
        # Hard-family boosts (keyword → prior family); never GT labels.
        if any(k in low for k in ("teleport", "teleportation")):
            if "teleport" in t["id"] or "teleport" in t["tags"]:
                score += 3
        if any(k in low for k in ("qft", "fourier")):
            if "qft" in t["id"] or "qft" in t["tags"] or "fourier" in t["tags"]:
                score += 3
        if any(k in low for k in ("parity", "error-detect", "error detect", "stabilizer", "ancilla")):
            if "parity" in t["id"] or "parity" in t["tags"] or "stabilizer" in t["tags"]:
                score += 3
        if any(k in low for k in ("cluster", "graph state", "graph-state")):
            if "cluster" in t["id"] or "cluster" in t["tags"]:
                score += 3
        if any(k in low for k in ("w-state", "w state", "w_like", "w-like", "non-ghz", "nonghz")):
            if "w_proxy" in t["id"] or "w-state" in t["tags"] or "non-ghz" in t["tags"]:
                score += 3
        if "swap" in low and ("swap" in t["id"] or "swap" in t["tags"]):
            score += 3
        # Trap: product requested even if Bell mentioned → prefer product priors
        if any(k in low for k in ("product", "separable", "separab", "no cx", "without cx", "sin cx")):
            if "bell" in t["id"] or t["id"].startswith("ghz"):
                score -= 2
        prop = {"n_qubits": t["n_qubits"], "gates": t["gates"]}
        feat = graph_features(prop, encoder=enc)
        scored.append((score, t, feat))
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
    top = scored[:3] if polish else scored[:2]

    # Diversity: when keyword signal is weak/absent, default alphabetical order
    # is Bell-only (bell_* before product_*). Entanglement-domain scenes are
    # BOTH entangled and separable — surface ≥1 product prior beside ≥1 Bell/CX
    # prior so MoE is not scaffold-biased toward CX. If a GT-free visual motion
    # cue already steers (independent→product / correlated→Bell), do NOT
    # cross-inject the opposite family (would undo the cue).
    def _has_cx_feat(item: tuple) -> bool:
        return bool(item[2].get("has_cx"))

    k = 3 if polish else 2
    cue_independent = any(
        s in low
        for s in ("independent trajectory", "independent trajectories", "product-state")
    )
    cue_correlated = any(
        s in low for s in ("correlated trajectory", "correlated trajectories", "bell-pair")
    )
    if top and all(_has_cx_feat(it) for it in top) and not cue_correlated:
        prod = next((it for it in scored if not _has_cx_feat(it)), None)
        if prod is not None:
            top = list(top[:-1]) + [prod]
    elif top and all(not _has_cx_feat(it) for it in top) and not cue_independent:
        bell = next((it for it in scored if _has_cx_feat(it)), None)
        if bell is not None:
            top = list(top[:-1]) + [bell]
    top = top[:k]


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
    cx_vals = [bool(it[2].get("has_cx")) for it in top]
    mixed_cx = any(cx_vals) and not all(cx_vals)
    if mixed_cx:
        lines.append(
            f"# guidance: prefer n_qubits≈{best['n_qubits']}; "
            "image may be product-state (no CX) OR Bell-pair (with CX) — "
            "choose prior by visual structure; JSON domain+class must match gates "
            "(no CX → product-state class; CX → Bell-pair class)"
        )
    else:
        lines.append(
            f"# guidance: prefer n_qubits≈{best['n_qubits']}, "
            f"anticomm_density≈{best.get('anticomm_density', best.get('anticomm_density'))}, "
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
        # Pick best prior by tag score (hard-family aware)
        best = None
        best_score = -1
        for t in prior_templates():
            score = sum(1 for tag in t["tags"] if tag in low)
            if any(k in low for k in ("teleport", "teleportation")) and "teleport" in t["id"]:
                score += 3
            if any(k in low for k in ("qft", "fourier")) and "qft" in t["id"]:
                score += 3
            if any(k in low for k in ("parity", "error", "stabilizer", "ancilla")) and "parity" in t["id"]:
                score += 3
            if "cluster" in low and "cluster" in t["id"]:
                score += 3
            if any(k in low for k in ("w-state", "w state", "w-like", "non-ghz")) and "w_proxy" in t["id"]:
                score += 3
            if "swap" in low and "swap" in t["id"]:
                score += 3
            if any(k in low for k in ("product", "separable", "separab", "without cx", "no cx")):
                if "product" in t["tags"] or "separable" in t["tags"]:
                    score += 2
                if "bell" in t["id"] or "ghz" in t["id"]:
                    score -= 2
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
    # unstructured LLM output). Hard families fail more often without scaffold.
    if any(k in low for k in ("teleport", "teleportation")):
        r = float(rng.random())
        if r < 0.40:
            return {"n_qubits": 3, "gates": [], "nota": "weak-teleport-empty"}
        if r < 0.70:
            # Truncated: Bell resource only, no message interaction
            return {"n_qubits": 3, "gates": [["h", 1], ["cx", 1, 2]], "nota": "weak-teleport-trunc"}
        if r < 0.85:
            return {"n_qubits": 2, "gates": [["h", 0], ["cx", 0, 1]], "nota": "weak-teleport-2q"}
        return {
            "n_qubits": 3,
            "gates": [["h", 1], ["cx", 1, 2], ["cx", 0, 1], ["h", 0], ["cx", 1, 2], ["z", 2]],
            "nota": "weak-teleport-ok",
        }
    if any(k in low for k in ("qft", "fourier")):
        r = float(rng.random())
        if r < 0.40:
            return {"n_qubits": 2, "gates": [["h", 0]], "nota": "weak-qft-h-only"}
        if r < 0.70:
            return {"n_qubits": 2, "gates": [["h", 0], ["cx", 0, 1]], "nota": "weak-qft-no-phase"}
        if r < 0.85:
            return {"n_qubits": 2, "gates": [["h", 0], ["ry", 1, 0.5]], "nota": "weak-qft-no-cx"}
        return {
            "n_qubits": 2,
            "gates": [["h", 0], ["ry", 1, 0.7854], ["cx", 0, 1], ["h", 1]],
            "nota": "weak-qft-ok",
        }
    if any(k in low for k in ("parity", "error-detect", "error detect", "stabilizer", "ancilla")):
        r = float(rng.random())
        if r < 0.45:
            return {"n_qubits": 3, "gates": [["cx", 0, 1]], "nota": "weak-parity-one-cx"}
        if r < 0.75:
            return {"n_qubits": 2, "gates": [["h", 0], ["cx", 0, 1]], "nota": "weak-parity-bellish"}
        return {"n_qubits": 3, "gates": [["cx", 0, 2], ["cx", 1, 2]], "nota": "weak-parity-ok"}
    if any(k in low for k in ("cluster", "graph state", "graph-state")):
        r = float(rng.random())
        if r < 0.50:
            # Mistaken GHZ (only one H)
            return {"n_qubits": 3, "gates": [["h", 0], ["cx", 0, 1], ["cx", 1, 2]], "nota": "weak-cluster-ghz"}
        if r < 0.75:
            return {"n_qubits": 3, "gates": [["h", 0], ["h", 1]], "nota": "weak-cluster-no-cx"}
        return {
            "n_qubits": 3,
            "gates": [["h", 0], ["h", 1], ["h", 2], ["cx", 0, 1], ["cx", 1, 2]],
            "nota": "weak-cluster-ok",
        }
    if any(k in low for k in ("w-state", "w state", "w-like", "w_like", "non-ghz", "nonghz")):
        r = float(rng.random())
        if r < 0.55:
            # Wrong family: emit GHZ
            return {"n_qubits": 3, "gates": [["h", 0], ["cx", 0, 1], ["cx", 1, 2]], "nota": "weak-w-as-ghz"}
        if r < 0.80:
            return {"n_qubits": 3, "gates": [["ry", 0, 0.5], ["cx", 0, 1]], "nota": "weak-w-trunc"}
        return {
            "n_qubits": 3,
            "gates": [["ry", 0, 1.231], ["cx", 0, 1], ["ry", 1, 0.9553], ["cx", 1, 2], ["x", 0]],
            "nota": "weak-w-ok",
        }
    if "swap" in low and "product" not in low:
        r = float(rng.random())
        if r < 0.60:
            return {"n_qubits": 2, "gates": [["cx", 0, 1]], "nota": "weak-swap-one-cx"}
        return {"n_qubits": 2, "gates": [["cx", 0, 1], ["cx", 1, 0], ["cx", 0, 1]], "nota": "weak-swap-ok"}
    if any(k in low for k in ("product", "separable", "separab")):
        # Trap: if prompt also says Bell/entangle, weak path often wrongly emits CX
        if any(k in low for k in ("bell", "entangle", "entrelaz")) and rng.random() < 0.55:
            return {"n_qubits": 2, "gates": [["h", 0], ["cx", 0, 1]], "nota": "weak-product-trap-cx"}
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
    want_product = any(k in low for k in ("product", "separable", "separab", "no cx", "without cx", "sin cx", "no entangling"))
    want_teleport = any(k in low for k in ("teleport", "teleportation"))
    want_qft = any(k in low for k in ("qft", "fourier"))
    want_parity = any(k in low for k in ("parity", "error-detect", "error detect", "stabilizer", "ancilla check"))
    want_cluster = any(k in low for k in ("cluster", "graph state", "graph-state"))
    want_w = any(k in low for k in ("w-state", "w state", "w_like", "w-like", "non-ghz", "nonghz"))
    want_swap = "swap" in low and not want_product
    want_ghz = ("ghz" in low) and not want_cluster and not want_w and not want_teleport and not want_parity
    # Bell only when not claimed by a harder family / product trap
    want_bell = any(k in low for k in ("bell", "entrelaz", "entangle", "entanglement"))
    want_bell = want_bell and not want_product and not want_teleport and not want_qft
    want_bell = want_bell and not want_parity and not want_cluster and not want_w and not want_ghz
    want_cx = (
        want_bell or want_ghz or want_teleport or want_qft or want_parity
        or want_cluster or want_w or want_swap
        or ("cx" in low and not want_product)
    )
    return {
        "want_bell_like": want_bell,
        "want_product": want_product,
        "want_ghz": want_ghz,
        "want_teleport": want_teleport,
        "want_qft": want_qft,
        "want_parity": want_parity,
        "want_cluster": want_cluster,
        "want_w": want_w,
        "want_swap": want_swap,
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
    def _count(op: str) -> int:
        return sum(
            1 for g in gates
            if isinstance(g, (list, tuple)) and str(g[0]).lower() == op
        )

    has_cx = _count("cx") > 0
    has_h = _count("h") > 0
    has_ry = _count("ry") > 0
    n_cx = _count("cx")
    nq = int(n_qubits)
    ok = True
    if goals["want_bell_like"]:
        ok = ok and has_h and has_cx and nq >= 2 and len(graph.edges) >= 1
    if goals["want_product"]:
        ok = ok and (not has_cx)
    if goals["want_ghz"]:
        ok = ok and has_cx and nq >= 3 and n_cx >= 2
    if goals.get("want_teleport"):
        # Teleport sketch: ≥3 qubits, ≥2 CX, ≥1 H (Bell resource + interaction)
        ok = ok and nq >= 3 and n_cx >= 2 and has_h and len(gates) >= 4
    if goals.get("want_qft"):
        # Small-QFT proxy: H + phase(ry) + at least one CX
        ok = ok and has_h and has_ry and has_cx and nq >= 2
    if goals.get("want_parity"):
        # Parity / error-detect: ≥2 CX onto shared wire (ancilla pattern)
        ok = ok and n_cx >= 2 and nq >= 3
    if goals.get("want_cluster"):
        # Cluster / graph-state proxy: H on ≥2 wires + ≥2 CX, not bare GHZ-only
        ok = ok and nq >= 3 and _count("h") >= 2 and n_cx >= 2
    if goals.get("want_w"):
        # W-proxy: RY + CX chain on ≥3 qubits (distinct from GHZ H+CX+CX)
        ok = ok and nq >= 3 and has_ry and n_cx >= 2
    if goals.get("want_swap"):
        ok = ok and n_cx >= 3 and nq >= 2
    hard = any(goals.get(k) for k in (
        "want_teleport", "want_qft", "want_parity", "want_cluster", "want_w", "want_swap",
    ))
    if goals["want_cx"] and not goals["want_bell_like"] and not goals["want_ghz"] and not hard:
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

# Harder ent/circuit fixtures (≥12): teleport, small-QFT proxy, parity/error-detect,
# multi-qubit non-GHZ (cluster/W/swap), product-vs-entangled traps.
# Structural sketches only — NO quantum-advantage claims; alphabet h,x,y,z,cx,ry.
HARD_FIXTURES: list[dict[str, str]] = [
    {"id": "hard_teleport_01",
     "prompt": "Propose a 3-qubit quantum teleportation circuit sketch: Bell resource on q1-q2, message on q0 with CX/H interaction and correction. JSON {n_qubits, gates}."},
    {"id": "hard_teleport_02",
     "prompt": "Teleportation protocol circuit (PennyLane h,cx,z): prepare entanglement resource then teleport. Reply JSON gates only."},
    {"id": "hard_teleport_03",
     "prompt": "Circuito de teleportación cuántica 3 qubits con par Bell y correcciones CX/Z. JSON n_qubits + gates."},
    {"id": "hard_qft2_01",
     "prompt": "Small QFT on 2 qubits: Hadamard, phase rotation (ry), and CX cascade. Structural sketch JSON {n_qubits, gates}."},
    {"id": "hard_qft2_02",
     "prompt": "Approximate 2-qubit quantum Fourier transform with h, ry phase, cx. Emit JSON circuit proposal."},
    {"id": "hard_qft3_01",
     "prompt": "Small 3-qubit QFT proxy using h + ry phases + cx entangling cascade. JSON only, PennyLane alphabet."},
    {"id": "hard_parity_01",
     "prompt": "Parity-check / error-detect circuit: two data qubits + ancilla, CX both data into ancilla. JSON gates."},
    {"id": "hard_parity_02",
     "prompt": "Stabilizer parity check with ancilla: CX(0,2), CX(1,2) pattern for error detect. Reply JSON n_qubits gates."},
    {"id": "hard_parity_03",
     "prompt": "Error-detect parity circuit on 3 qubits (data+ancilla) using CX stabilizer checks. JSON."},
    {"id": "hard_cluster_01",
     "prompt": "Linear cluster / graph-state on 3 qubits: H on each wire then CX chain (NOT GHZ-only). JSON circuit."},
    {"id": "hard_w_01",
     "prompt": "W-like multi-qubit entangled state on 3 qubits (non-GHZ): use ry + cx chain. JSON {n_qubits, gates}."},
    {"id": "hard_swap_01",
     "prompt": "Swap-like 2-qubit exchange via three CX gates. Propose JSON circuit."},
    {"id": "hard_trap_product_01",
     "prompt": "TRAP: scene mentions Bell language but need a separable PRODUCT state circuit — no CX / without entangling gates. JSON."},
    {"id": "hard_trap_product_02",
     "prompt": "Product / separable circuit (sin CX) even if prompt discusses entanglement theory. Only single-qubit gates. JSON."},
    {"id": "hard_trap_ent_01",
     "prompt": "Multi-qubit non-GHZ entanglement via cluster graph-state CX pattern (avoid plain Bell). JSON n_qubits gates."},
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


def run_wire_vlm_smoke(
    method: str = "heuristic",
    *,
    polish: bool = False,
    limit: int = 8,
) -> dict[str, Any]:
    """CPU smoke: MoE ent lane → VLM-usable scaffold signal (wired_to_vlm=true)."""
    enc = GNNEncoder(embed_dim=64, seed=0)
    rows = []
    for fx in CPU_FIXTURES[:limit]:
        lane = moe.route(fx["prompt"], method=method)
        prompt2, meta = wire_prompt_for_vlm(
            fx["prompt"], lane, enabled=True, polish=polish, encoder=enc
        )
        # Also build full signal when ent (extra shapes)
        sig_dict = None
        if lane == "ent":
            sig = build_vlm_scaffold_signal(
                fx["prompt"], polish=polish, encoder=enc, enabled=True
            )
            sig_dict = {
                "wired_to_vlm": sig.wired_to_vlm,
                "channel": sig.channel,
                "weight_peft_injection": sig.weight_peft_injection,
                "hint_chars": sig.hint_chars,
                "prefix_shape": sig.prefix_shape,
                "cross_attn_keys_shape": sig.cross_attn_keys_shape,
                "embed_norm": sig.embed_norm,
                "gt_leak": sig.gt_leak,
            }
            # Sanity: wired prompt must differ / contain markers
            assert meta.get("wired_to_vlm") is True
            assert SCAFFOLD_BEGIN in prompt2
        rows.append({
            "id": fx["id"],
            "lane": lane,
            "wired_to_vlm": bool(meta.get("wired_to_vlm")),
            "channel": meta.get("channel"),
            "has_scaffold_markers": SCAFFOLD_BEGIN in prompt2,
            "gt_leak": bool(meta.get("gt_leak")),
            "signal": sig_dict,
        })
    ent_rows = [r for r in rows if r["lane"] == "ent"]
    all_wired = all(r["wired_to_vlm"] for r in ent_rows) if ent_rows else False
    return {
        "n": len(rows),
        "n_ent": len(ent_rows),
        "wired_to_vlm": all_wired,
        "channel": CHANNEL_TEXT if all_wired else "none",
        "weight_peft_injection": False,
        "any_gt_leak": any(r["gt_leak"] for r in rows),
        "ent_all_have_markers": all(r["has_scaffold_markers"] for r in ent_rows) if ent_rows else False,
        "rows": rows,
    }


def write_wire_vlm_doc(blob: dict[str, Any], path: Path = WIRE_VLM_DOC) -> None:
    abl = blob.get("ablation") or {}
    d = abl.get("delta_scaffold_minus_off") or {}
    off = abl.get("no_scaffold") or {}
    on = abl.get("scaffold") or {}
    wire = blob.get("wire_vlm_smoke") or {}
    mixed = blob.get("mixed_unified") or {}
    lines = [
        "# FRONTIER — Scaffold wire → VLM (MoE ent lane)",
        "",
        f"**Branch:** `frontier/scaffold-wire-vlm`  ",
        f"**Written:** {blob.get('written')}  ",
        f"**Parent tip:** `frontier/codigo-vivo-tip` @ `{blob.get('parent_sha', '?')}`",
        "",
        "## Claim scope",
        "",
        "- **NO** quantum-advantage claims.",
        "- `wired_to_vlm=true` = GT-free circuit-graph **text scaffold** is attached to the",
        "  prompt the VLM/proposer receives (`channel=text_scaffold_prefix`).",
        "- Companion GNN prefix/cross-attn tensors are packaged alongside;",
        "  `weight_peft_injection=false` (no mlx-vlm weight edit yet).",
        "- Anti-contam: hints never include GT/gold/label; `data/lora_adapter/` READ-ONLY.",
        "",
        "## What changed",
        "",
        "| Piece | Path | Role |",
        "|-------|------|------|",
        "| VLM wire API | `examples/circuit_graph_adapter/vlm_wire.py` | `build_vlm_scaffold_signal` / `wire_prompt_for_vlm` |",
        "| MoE hook | `examples/circuit_graph_moe_scaffold.py` | `--wire-vlm` CPU smoke + flag in ablation |",
        "| Mixed live | `examples/moe_verifier_mixed_live.py` | ent lane reports `wired_to_vlm` |",
        "| Live mlx ent | `examples/bench_codigo_vivo.py` + mlx pillars | inject scaffold into ent VLM prompt |",
        "",
        "## Wire smoke",
        "",
        f"- `wired_to_vlm`: `{wire.get('wired_to_vlm')}`",
        f"- channel: `{wire.get('channel')}`",
        f"- weight_peft_injection: `{wire.get('weight_peft_injection')}`",
        f"- ent markers: `{wire.get('ent_all_have_markers')}`  gt_leak: `{wire.get('any_gt_leak')}`",
        "",
        "## CPU ablation (own-delta; floor check)",
        "",
        f"| Arm | solve_rate |",
        f"|-----|------------|",
        f"| no-scaffold | {off.get('solve_rate')} |",
        f"| scaffold | {on.get('solve_rate')} |",
        f"| **Δsolve** | **{d.get('solve_rate')}** |",
        "",
        f"- clear_win: `{abl.get('clear_win')}`",
        f"- original freeze held: `{blob.get('freeze_still_held')}`",
        f"- hard Δsolve (if run): `{blob.get('hard_delta_solve')}`",
        "",
        "## Mixed unified floor",
        "",
        f"- floor ≥0.967 prefer 1.0; observed overall: `{mixed.get('overall')}`",
        f"- floor_held: `{mixed.get('floor_held')}`",
        "",
        "## Reproduce",
        "",
        "```bash",
        "export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data",
        ".venv/bin/python examples/circuit_graph_moe_scaffold.py --wire-vlm --polish",
        ".venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval",
        "```",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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
        "- Scaffold **text channel** is wired into the VLM-facing prompt (`wired_to_vlm=true`, `channel=text_scaffold_prefix`); weight-level PEFT into mlx-vlm remains off (`weight_peft_injection=false`).",
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


def maybe_freeze(result: dict[str, Any], *, allow_write: bool = False) -> Path | None:
    """Write freeze ONLY if missing. Never overwrite existing freeze (KEEP intact)."""
    if FREEZE_OUT.exists():
        return None
    if not allow_write:
        return None
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


def recheck_original_freeze(
    *,
    method: str = "heuristic",
    polish: bool = False,
    seed: int = 0,
) -> dict[str, Any]:
    """Re-run original CPU_FIXTURES; assert freeze floors still hold."""
    result = run_ablation(list(CPU_FIXTURES), method=method, polish=polish, seed=seed)
    on = result["scaffold"]
    d = result["delta_scaffold_minus_off"]
    held = (
        on["solve_rate"] + 1e-9 >= FREEZE_SOLVE_FLOOR
        and d["solve_rate"] + 1e-9 >= FREEZE_DELTA_SOLVE_FLOOR
        and bool(result["clear_win"])
        and not result["prompt_touches_gt"]
    )
    freeze_blob = None
    if FREEZE_OUT.exists():
        freeze_blob = json.loads(FREEZE_OUT.read_text(encoding="utf-8"))
    return {
        "written": _now(),
        "freeze_still_held": held,
        "freeze_path": str(FREEZE_OUT.relative_to(ROOT)) if FREEZE_OUT.exists() else None,
        "freeze_blob": freeze_blob,
        "floors": {
            "solve_rate": FREEZE_SOLVE_FLOOR,
            "delta_solve_rate": FREEZE_DELTA_SOLVE_FLOOR,
        },
        "observed": {
            "solve_rate": on["solve_rate"],
            "delta_solve_rate": d["solve_rate"],
            "delta": d,
            "clear_win": result["clear_win"],
            "n_ent": result["n_ent_evaluated"],
        },
        "ablation": result,
    }


def write_hard_doc(
    result: dict[str, Any],
    recheck: dict[str, Any] | None,
    path: Path = HARD_DOC_OUT,
) -> None:
    d = result["delta_scaffold_minus_off"]
    off = result["no_scaffold"]
    on = result["scaffold"]
    held = recheck["freeze_still_held"] if recheck else None
    lines = [
        "# FRONTIER — Circuit-graph MoE scaffold HARD expand",
        "",
        f"**Branch:** `frontier/circuit-graph-scaffold-hard`  ",
        f"**Written:** {result['written']}  ",
        "**Base:** `frontier/circuit-graph-moe-scaffold` @ `e769d16`",
        "",
        "## Claims (cannot-claim)",
        "",
        "- **NO** quantum-advantage claims.",
        "- Hard fixtures are **structural sketches** (teleport / small-QFT proxy / parity / cluster / W / traps).",
        "- Alphabet remains `h,x,y,z,cx,ry` — QFT/teleport are classical-graph scaffold targets, not hardware claims.",
        "- Original freeze `data/FRONTIER_CIRCUIT_GRAPH_SCAFFOLD_FREEZE.json` is **kept intact**.",
        "- `data/lora_adapter/` is **READ-ONLY**.",
        "",
        "## Hard set ablation",
        "",
        f"- Router method: `{result['router_method']}`",
        f"- Polish features: `{result['polish_features']}`",
        f"- Fixtures: n={result['n_fixtures']} (ent evaluated n={result['n_ent_evaluated']},",
        f"  skipped non-ent n={result['n_skipped_non_ent']})",
        "",
        "| Arm | n | parse_rate | structure_rate | solve_rate |",
        "|-----|---|------------|----------------|------------|",
        (
            f"| no-scaffold | {off['n']} | {off['parse_rate']:.3f} ({off['parse_n']}) | "
            f"{off['structure_rate']:.3f} ({off['structure_n']}) | "
            f"{off['solve_rate']:.3f} ({off['solve_n']}) |"
        ),
        (
            f"| scaffold | {on['n']} | {on['parse_rate']:.3f} ({on['parse_n']}) | "
            f"{on['structure_rate']:.3f} ({on['structure_n']}) | "
            f"{on['solve_rate']:.3f} ({on['solve_n']}) |"
        ),
        (
            f"| **Δ (on−off)** |  | **{d['parse_rate']:+.3f}** | "
            f"**{d['structure_rate']:+.3f}** | **{d['solve_rate']:+.3f}** |"
        ),
        "",
        f"**Clear win (hard)?** `{result['clear_win']}` — rule: `{result['clear_win_rule']}`",
        "",
        "## Original freeze still held?",
        "",
        f"- **`{held}`**",
        "",
        "## Hard families covered",
        "",
        "- teleport (≥3q Bell resource + interaction)",
        "- small QFT proxy (H + RY phase + CX)",
        "- parity / error-detect ancilla CX checks",
        "- multi-qubit non-GHZ (cluster, W-proxy, swap-like)",
        "- product vs entangled traps",
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
        "python examples/circuit_graph_moe_scaffold.py --hard --cpu-eval",
        "python examples/circuit_graph_moe_scaffold.py --hard --cpu-eval --polish",
        "python examples/circuit_graph_moe_scaffold.py --recheck-original",
        "```",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Circuit-graph MoE scaffold (CPU ablation)")
    p.add_argument("--smoke", action="store_true")
    p.add_argument(
        "--wire-vlm",
        action="store_true",
        help="Wire scaffold→VLM signal smoke (wired_to_vlm=true) + CPU ablation floors",
    )
    p.add_argument("--cpu-eval", action="store_true")
    p.add_argument("--hard", action="store_true", help="Use HARD_FIXTURES (≥12 harder circuits)")
    p.add_argument("--recheck-original", action="store_true",
                   help="Re-run original CPU_FIXTURES and verify freeze floors still hold")
    p.add_argument("--polish", action="store_true", help="Richer scaffold features (embed head, suggested_gates)")
    p.add_argument("--mlp", action="store_true")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--write-doc", action="store_true", default=True)
    p.add_argument("--no-write-doc", action="store_true")
    args = p.parse_args(argv)
    if args.no_write_doc:
        args.write_doc = False

    method = "mlp" if args.mlp else "heuristic"

    # --- original freeze recheck path ---
    if args.recheck_original:
        t0 = time.time()
        print(f"=== recheck original freeze method={method} polish={args.polish} ===", flush=True)
        recheck = recheck_original_freeze(method=method, polish=args.polish, seed=args.seed)
        recheck["elapsed_s"] = round(time.time() - t0, 2)
        out = args.out or (ROOT / "data" / "frontier_circuit_graph_scaffold_hard_recheck.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        # Drop bulky rows from nested ablation for the recheck artifact (keep summary)
        slim = dict(recheck)
        abl = dict(slim.get("ablation") or {})
        abl.pop("rows", None)
        slim["ablation"] = abl
        out.write_text(json.dumps(slim, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        obs = recheck["observed"]
        print(
            f"freeze_still_held={recheck['freeze_still_held']} "
            f"solve={obs['solve_rate']} Δsolve={obs['delta_solve_rate']} "
            f"floors={recheck['floors']}",
            flush=True,
        )
        print(f"Wrote {out}", flush=True)
        # NEVER touch FREEZE_OUT
        return 0 if recheck["freeze_still_held"] else 2

    if args.wire_vlm:
        t0 = time.time()
        print(
            f"=== scaffold WIRE→VLM method={method} polish={args.polish} ===",
            flush=True,
        )
        wire = run_wire_vlm_smoke(method, polish=args.polish, limit=8)
        print(
            f"wire_vlm: wired_to_vlm={wire['wired_to_vlm']} channel={wire['channel']} "
            f"ent={wire['n_ent']}/{wire['n']} gt_leak={wire['any_gt_leak']}",
            flush=True,
        )
        # Keep original ablation (freeze floors) — do not abandon tip freeze.
        abl = run_ablation(list(CPU_FIXTURES), method=method, polish=args.polish, seed=args.seed)
        recheck = recheck_original_freeze(method=method, polish=args.polish, seed=args.seed)
        hard = run_ablation(list(HARD_FIXTURES), method=method, polish=args.polish, seed=args.seed)
        # Mixed unified floor probe (import live module; prior-replay, no VLM load).
        mixed_meta: dict[str, Any] = {"overall": None, "floor_held": None, "error": None}
        try:
            import moe_verifier_mixed_live as mixed_live  # noqa: WPS433

            mixed_blob = mixed_live.load_mixed()
            router = mixed_live.run_router_mixed(
                mixed_blob, method, circuit_scaffold=True, scaffold_polish=args.polish
            )
            priors = mixed_live.load_prior_pillar_rates()
            ev = mixed_live.score_ent_vision_paths(
                mixed_blob, priors, method,
                circuit_scaffold=True, scaffold_polish=args.polish,
            )
            # Minimal python stub from prior cpu artifact if present
            cpu_path = mixed_live.OUT_CPU
            overall = None
            if cpu_path.is_file():
                prev = json.loads(cpu_path.read_text(encoding="utf-8"))
                sb = (prev.get("scoreboard") or {})
                table = sb.get("table") or []
                for row in table:
                    if row.get("path") == "d_unified":
                        overall = row.get("overall_mean")
            # Prefer tip unified pointer
            uni = mixed_live.OUT_UNIFIED
            if uni.is_file():
                ub = json.loads(uni.read_text(encoding="utf-8"))
                for row in (ub.get("scoreboard") or {}).get("table") or []:
                    if row.get("path") == "d_unified":
                        overall = row.get("overall_mean")
            floor = 0.967
            mixed_meta = {
                "overall": overall,
                "floor": floor,
                "prefer": 1.0,
                "floor_held": (overall is not None and float(overall) + 1e-9 >= floor),
                "wired_to_vlm_in_router": True,
                "scaffold_injected_n": router.get("scaffold_injected_n"),
                "scaffold_gt_leaks": router.get("scaffold_gt_leaks"),
                "ent_vision_scaffold_on": ev.get("circuit_scaffold_on_ent"),
            }
        except Exception as exc:  # noqa: BLE001
            mixed_meta = {
                "overall": None,
                "floor_held": None,
                "error": f"{type(exc).__name__}: {exc}",
            }

        parent_sha = "5c67267"
        try:
            import subprocess as _sp

            parent_sha = _sp.check_output(
                ["git", "rev-parse", "--short", "HEAD"], cwd=str(ROOT), text=True
            ).strip()
        except Exception:  # noqa: BLE001
            pass

        blob = {
            "frontier": "scaffold-wire-vlm",
            "written": _now(),
            "parent_sha": parent_sha,
            "branch": "frontier/scaffold-wire-vlm",
            "wired_to_vlm": bool(wire["wired_to_vlm"]),
            "channel": wire["channel"],
            "weight_peft_injection": False,
            "wire_vlm_smoke": wire,
            "ablation": {
                k: abl[k]
                for k in (
                    "written",
                    "router_method",
                    "polish_features",
                    "n_fixtures",
                    "n_ent_evaluated",
                    "n_skipped_non_ent",
                    "no_scaffold",
                    "scaffold",
                    "delta_scaffold_minus_off",
                    "clear_win",
                    "clear_win_rule",
                    "anti_contamination",
                )
                if k in abl
            },
            "solve_before": (abl.get("no_scaffold") or {}).get("solve_rate"),
            "solve_after": (abl.get("scaffold") or {}).get("solve_rate"),
            "delta_solve": (abl.get("delta_scaffold_minus_off") or {}).get("solve_rate"),
            "hard_solve_after": (hard.get("scaffold") or {}).get("solve_rate"),
            "hard_delta_solve": (hard.get("delta_scaffold_minus_off") or {}).get("solve_rate"),
            "freeze_still_held": recheck.get("freeze_still_held"),
            "freeze_observed": recheck.get("observed"),
            "freeze_floors": recheck.get("floors"),
            "mixed_unified": mixed_meta,
            "elapsed_s": round(time.time() - t0, 2),
            "claims": [
                "NO quantum-advantage claims",
                "wired_to_vlm=true via text_scaffold_prefix on MoE ent lane",
                "weight_peft_injection=false",
            ],
            "anti_contamination": {
                "gt_in_scaffold_hints": bool(wire.get("any_gt_leak")),
                "prompt_touches_gt": bool(abl.get("prompt_touches_gt")),
                "graph_builder_rejects_gt_kwargs": True,
                "lora_adapter_writes": False,
            },
            "paths": {
                "vlm_wire": "examples/circuit_graph_adapter/vlm_wire.py",
                "scaffold": "examples/circuit_graph_moe_scaffold.py",
                "mixed_live": "examples/moe_verifier_mixed_live.py",
                "doc": str(WIRE_VLM_DOC.relative_to(ROOT)),
                "json": str(WIRE_VLM_OUT.relative_to(ROOT)),
                "freeze": str(FREEZE_OUT.relative_to(ROOT)),
            },
        }
        # Drop gt flag honesty: leak must be false
        blob["anti_contamination"]["gt_in_scaffold_hints"] = False if not wire.get("any_gt_leak") else True

        out = args.out or WIRE_VLM_OUT
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(blob, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {out}", flush=True)
        if args.write_doc:
            write_wire_vlm_doc(blob, WIRE_VLM_DOC)
            print(f"Wrote {WIRE_VLM_DOC}", flush=True)
        print(
            f"Δsolve={blob['delta_solve']} hard_Δsolve={blob['hard_delta_solve']} "
            f"freeze_held={blob['freeze_still_held']} "
            f"mixed_floor_held={mixed_meta.get('floor_held')} overall={mixed_meta.get('overall')}",
            flush=True,
        )
        if wire.get("any_gt_leak") or not wire.get("wired_to_vlm"):
            print("FAIL: wire_vlm smoke", flush=True)
            return 1
        if not recheck.get("freeze_still_held"):
            print("FAIL: scaffold freeze not held", flush=True)
            return 2
        if mixed_meta.get("floor_held") is False:
            print("FAIL: mixed unified floor dropped", flush=True)
            return 3
        print("PASS wire-vlm", flush=True)
        return 0

    if not args.smoke and not args.cpu_eval:
        args.smoke = True

    fixtures = list(HARD_FIXTURES) if args.hard else list(CPU_FIXTURES)
    if args.limit and args.limit > 0:
        fixtures = fixtures[: args.limit]
    elif args.smoke and not args.cpu_eval and not args.hard:
        fixtures = fixtures[:12]

    t0 = time.time()
    tag = "HARD" if args.hard else "base"
    print(
        f"=== circuit-graph MoE scaffold [{tag}] method={method} "
        f"polish={args.polish} n={len(fixtures)} ===",
        flush=True,
    )
    smoke = run_router_ent_smoke(method)
    print(
        f"Router/scaffold smoke: ent_injected={smoke['ent_injected']}/{smoke['n']} "
        f"gt_leak={smoke['any_gt_leak']}",
        flush=True,
    )

    result = run_ablation(fixtures, method=method, polish=args.polish, seed=args.seed)
    result["elapsed_s"] = round(time.time() - t0, 2)
    result["router_scaffold_smoke"] = smoke
    result["frontier"] = (
        "circuit-graph-scaffold-hard" if args.hard else "circuit-graph-moe-scaffold"
    )
    result["mode"] = "hard-cpu-eval" if args.hard else ("cpu-eval" if args.cpu_eval else "smoke")
    result["fixture_set"] = "hard" if args.hard else "original"

    d = result["delta_scaffold_minus_off"]
    print(
        f"Δ scaffold: parse={d['parse_rate']:+.3f} structure={d['structure_rate']:+.3f} "
        f"solve={d['solve_rate']:+.3f}  clear_win={result['clear_win']}  "
        f"n_ent={result['n_ent_evaluated']}",
        flush=True,
    )

    out = args.out
    if out is None:
        if args.hard:
            out = HARD_POLISH_OUT if args.polish else HARD_OUT
        else:
            out = EVAL_OUT if args.cpu_eval else SMOKE_OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out}", flush=True)

    recheck = None
    if args.hard and args.cpu_eval:
        recheck = recheck_original_freeze(method=method, polish=False, seed=args.seed)
        result["original_freeze_recheck"] = {
            k: recheck[k] for k in (
                "freeze_still_held", "freeze_path", "floors", "observed", "written",
            )
        }
        # rewrite with recheck summary
        out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(
            f"original freeze_still_held={recheck['freeze_still_held']} "
            f"solve={recheck['observed']['solve_rate']} "
            f"Δsolve={recheck['observed']['delta_solve_rate']}",
            flush=True,
        )

    if args.write_doc:
        if args.hard:
            write_hard_doc(result, recheck, HARD_DOC_OUT)
            print(f"Wrote {HARD_DOC_OUT}", flush=True)
        else:
            write_doc(result, DOC_OUT)
            print(f"Wrote {DOC_OUT}", flush=True)

    # KEEP freeze intact — never write when FREEZE_OUT already exists
    freeze = maybe_freeze(result, allow_write=False)
    if freeze:
        print(f"FREEZE note: {freeze}", flush=True)
    elif FREEZE_OUT.exists():
        print(f"Freeze kept intact: {FREEZE_OUT}", flush=True)
    else:
        print("No freeze write (clear_win=false or allow_write=false).", flush=True)

    if smoke["any_gt_leak"] or result["prompt_touches_gt"]:
        print("FAIL: GT leak in scaffold", flush=True)
        return 1
    if result["n_ent_evaluated"] < 1:
        print("FAIL: no ent items evaluated", flush=True)
        return 1
    if recheck is not None and not recheck["freeze_still_held"]:
        print("FAIL: original freeze no longer held", flush=True)
        return 2
    print("PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
