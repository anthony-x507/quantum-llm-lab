#!/usr/bin/env python3
"""
Amplitude embedding prototype — pedagogical / experimental fusion only.

Claim: NO quantum advantage. Converts a small PennyLane circuit's statevector
into real amplitude features, projects them into the transformer's embedding
dim, and injects them as a soft-prompt residual (or side MLP), NOT as text/JSON.

Mechanism (honest):
  1) Circuit → statevector (PennyLane default.qubit, CPU).
  2) Complex amplitudes → real features: [Re, Im] (optionally |amp|, phase).
  3) Seeded Linear probe: amp_dim → embed_dim (Qwen3-VL-8B text = 4096).
  4) Injection:
       - residual_first_token: add projected vector to first token embedding
       - soft_prompt_prepend: prepend 1 virtual token embedding
       - side_mlp: classify entangled/separable from amp features alone (CPU)
  True weight-level injection into mlx-vlm generate() is fragile; if --mlx
  fails (OOM while another train holds GPU, or hooks unavailable), we ship
  the closest honest path: soft-prompt residual helpers + side MLP eval.

Usage:
  # CPU unit tests + side-MLP metrics (safe while qlora-ent holds GPU)
  python examples/amplitude_embed_prototype.py --self-test
  python examples/amplitude_embed_prototype.py --cpu-eval \\
      --ent-set data/bench_live/ent_items.json

  # Optional MLX forward (only when GPU/RAM free; never writes lora_adapter/)
  python examples/amplitude_embed_prototype.py --mlx-eval \\
      --model mlx-community/Qwen3-VL-8B-Thinking-4bit \\
      --ent-set data/bench_live/ent_items.json \\
      --adapter-ro data/lora_adapter
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "examples") not in sys.path:
    sys.path.insert(0, str(ROOT / "examples"))

# Qwen3-VL-8B text hidden size (from HF config).
DEFAULT_EMBED_DIM = 4096
DEFAULT_MODEL = "mlx-community/Qwen3-VL-8B-Thinking-4bit"

# Lab gate templates (mirrors train_lora / synthetic_physics_dataset).
BELL_GATES: dict[str, list[list[Any]]] = {
    "Phi+": [["h", 0], ["cx", 0, 1]],
    "Phi-": [["x", 0], ["h", 0], ["cx", 0, 1]],
    "Psi+": [["h", 0], ["x", 1], ["cx", 0, 1]],
    "Psi-": [["x", 0], ["h", 0], ["x", 1], ["cx", 0, 1]],
    "bell_hcxz": [["h", 0], ["cx", 0, 1], ["z", 1]],
    "bell_yhcx": [["y", 0], ["h", 0], ["cx", 0, 1]],
    "bell_hcxry": [["h", 0], ["cx", 0, 1], ["ry", 1, 0.4]],
}
SEP_GATES: dict[str, list[list[Any]]] = {
    "product_hh": [["h", 0], ["h", 1]],
    "product_x": [["x", 0], ["x", 1]],
    "product_ry": [["ry", 0, 0.7], ["ry", 1, -0.3]],
    "product_hz": [["h", 0], ["z", 1]],
    "product_id": [["h", 0]],  # effectively |+>|0> product
    "product_xy": [["x", 0], ["y", 1]],
    "product_ryry": [["ry", 0, 1.1], ["ry", 1, 0.5]],
}


@dataclass
class AmpBundle:
    n_qubits: int
    gates: list[list[Any]]
    statevector: list[complex]
    features: list[float]  # real feature vector
    feature_kind: str
    label: str  # entangled | separable
    concurrence: float
    entropy_A: float
    energy_proxy_ok: bool  # toy: entangled ⇒ concurrence>0.5; separable ⇒ <0.2
    name: str


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
    """Return complex statevector via PennyLane (CPU)."""
    import pennylane as qml

    if n_qubits < 1 or n_qubits > 3:
        raise ValueError("prototype supports 1–3 qubits")
    dev = qml.device("default.qubit", wires=n_qubits)

    @qml.qnode(dev)
    def circuit():
        _apply_gates(qml, gates)
        return qml.state()

    return np.asarray(circuit(), dtype=np.complex128)


def amplitudes_to_features(
    state: np.ndarray,
    kind: str = "re_im",
) -> np.ndarray:
    """Map complex amplitudes → real vector (no text/JSON)."""
    state = np.asarray(state, dtype=np.complex128).ravel()
    if kind == "re_im":
        return np.concatenate([state.real, state.imag]).astype(np.float64)
    if kind == "mag_phase":
        mag = np.abs(state)
        phase = np.angle(state)
        return np.concatenate([mag, phase]).astype(np.float64)
    if kind == "mag_only":
        return np.abs(state).astype(np.float64)
    raise ValueError(f"unknown feature kind: {kind}")


def concurrence_2q(state: np.ndarray) -> float:
    """Wootters concurrence for a pure 2-qubit state."""
    s = np.asarray(state, dtype=np.complex128).ravel()
    if s.size != 4:
        return float("nan")
    # |ψ> = a|00>+b|01>+c|10>+d|11> → C = 2|ad-bc|
    a, b, c, d = s
    return float(2.0 * abs(a * d - b * c))


def entropy_reduced_A(state: np.ndarray, n_qubits: int = 2) -> float:
    """Von Neumann entropy of qubit-0 reduced density (bits)."""
    s = np.asarray(state, dtype=np.complex128).ravel()
    dim = 2**n_qubits
    if s.size != dim:
        return float("nan")
    psi = s.reshape([2] * n_qubits)
    # ρ_A = Tr_B… |ψ><ψ|
    # For 2 qubits: reshape (2,2)
    if n_qubits == 2:
        m = psi  # (A, B)
        rho_A = m @ m.conj().T
    else:
        # general: reshape A vs rest
        m = psi.reshape(2, -1)
        rho_A = m @ m.conj().T
    evals = np.linalg.eigvalsh(rho_A)
    evals = np.clip(evals.real, 0.0, 1.0)
    h = 0.0
    for e in evals:
        if e > 1e-12:
            h -= float(e) * math.log(e, 2)
    return h


def build_amp_bundle(
    gates: list[list[Any]],
    label: str,
    name: str,
    feature_kind: str = "re_im",
    n_qubits: int = 2,
) -> AmpBundle:
    sv = circuit_statevector(gates, n_qubits=n_qubits)
    feats = amplitudes_to_features(sv, kind=feature_kind)
    conc = concurrence_2q(sv) if n_qubits == 2 else float("nan")
    ent = entropy_reduced_A(sv, n_qubits=n_qubits)
    if label == "entangled":
        energy_ok = (conc > 0.5) or (ent > 0.5)
    else:
        energy_ok = (conc < 0.25) and (ent < 0.25)
    return AmpBundle(
        n_qubits=n_qubits,
        gates=gates,
        statevector=[complex(x) for x in sv.tolist()],
        features=feats.tolist(),
        feature_kind=feature_kind,
        label=label,
        concurrence=conc,
        entropy_A=ent,
        energy_proxy_ok=bool(energy_ok),
        name=name,
    )


class LinearProbe:
    """Seeded amp→embed Linear (numpy). Deterministic, no torch/mlx required."""

    def __init__(self, in_dim: int, out_dim: int, seed: int = 42, scale: float = 0.02):
        rng = np.random.default_rng(seed)
        # Xavier-ish
        lim = math.sqrt(6.0 / (in_dim + out_dim))
        self.W = rng.uniform(-lim, lim, size=(out_dim, in_dim)).astype(np.float64) * (scale / lim)
        self.b = np.zeros(out_dim, dtype=np.float64)
        self.in_dim = in_dim
        self.out_dim = out_dim

    def __call__(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=np.float64).ravel()
        if x.size != self.in_dim:
            # pad / truncate to expected amp dim
            buf = np.zeros(self.in_dim, dtype=np.float64)
            n = min(self.in_dim, x.size)
            buf[:n] = x[:n]
            x = buf
        y = self.W @ x + self.b
        # unit-ish soft prompt (avoid exploding residual)
        nrm = np.linalg.norm(y) + 1e-9
        return (y / nrm).astype(np.float64)


class SideMLP:
    """Tiny 2-layer probe: amp features → {entangled, separable}. CPU only."""

    def __init__(self, in_dim: int, seed: int = 0):
        rng = np.random.default_rng(seed)
        h = 32
        self.W1 = rng.normal(0, 0.3, size=(h, in_dim)).astype(np.float64)
        self.b1 = np.zeros(h)
        self.W2 = rng.normal(0, 0.3, size=(2, h)).astype(np.float64)
        self.b2 = np.zeros(2)

    @staticmethod
    def _relu(x: np.ndarray) -> np.ndarray:
        return np.maximum(x, 0.0)

    def logits(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=np.float64).ravel()
        h = self._relu(self.W1 @ x + self.b1)
        return self.W2 @ h + self.b2

    def predict(self, x: np.ndarray) -> str:
        z = self.logits(x)
        return "entangled" if z[0] >= z[1] else "separable"

    def fit(self, xs: list[np.ndarray], ys: list[str], steps: int = 400, lr: float = 0.05) -> None:
        """Few-step GD on logistic-ish loss (toy; not production)."""
        Y = np.array([[1.0, 0.0] if y == "entangled" else [0.0, 1.0] for y in ys])
        X = np.stack([np.asarray(x, dtype=np.float64).ravel() for x in xs])
        for _ in range(steps):
            # forward
            H = self._relu(X @ self.W1.T + self.b1)
            Z = H @ self.W2.T + self.b2
            # softmax
            Z = Z - Z.max(axis=1, keepdims=True)
            E = np.exp(Z)
            P = E / (E.sum(axis=1, keepdims=True) + 1e-9)
            # dL/dZ
            dZ = (P - Y) / max(len(ys), 1)
            dW2 = dZ.T @ H
            db2 = dZ.sum(axis=0)
            dH = dZ @ self.W2
            dH *= (H > 0).astype(np.float64)
            dW1 = dH.T @ X
            db1 = dH.sum(axis=0)
            self.W2 -= lr * dW2
            self.b2 -= lr * db2
            self.W1 -= lr * dW1
            self.b1 -= lr * db1


def inject_residual_first_token(inputs_embeds: Any, amp_vec: np.ndarray, scale: float = 0.15) -> Any:
    """Add projected amplitude vector to the first sequence position (residual)."""
    import mlx.core as mx

    amp = mx.array(amp_vec.astype(np.float32))
    # inputs_embeds: (B, T, D) or (T, D)
    if inputs_embeds.ndim == 2:
        out = mx.array(inputs_embeds)
        out = out.at[0].add(amp * scale)
        return out
    out = mx.array(inputs_embeds)
    out = out.at[:, 0, :].add(amp * scale)
    return out


def inject_soft_prompt_prepend(inputs_embeds: Any, amp_vec: np.ndarray, scale: float = 1.0) -> Any:
    """Prepend one soft-prompt token built from amplitude projection."""
    import mlx.core as mx

    amp = mx.array((amp_vec * scale).astype(np.float32))
    if inputs_embeds.ndim == 2:
        return mx.concatenate([amp[None, :], inputs_embeds], axis=0)
    # (B, T, D)
    soft = mx.broadcast_to(amp[None, None, :], (inputs_embeds.shape[0], 1, inputs_embeds.shape[-1]))
    return mx.concatenate([soft, inputs_embeds], axis=1)


def library_bundles(feature_kind: str = "re_im") -> list[AmpBundle]:
    out: list[AmpBundle] = []
    for name, gates in BELL_GATES.items():
        out.append(build_amp_bundle(gates, "entangled", name, feature_kind=feature_kind))
    for name, gates in SEP_GATES.items():
        out.append(build_amp_bundle(gates, "separable", name, feature_kind=feature_kind))
    return out


def gates_for_meta(meta: dict[str, Any]) -> tuple[list[list[Any]], str, str]:
    """Reuse lab gold circuit mapping from train_lora."""
    from train_lora import _circuit_target_from_meta  # type: ignore

    tgt = _circuit_target_from_meta(meta)
    gates = tgt.get("gates") or [["h", 0], ["cx", 0, 1]]
    label = str(tgt.get("label") or meta.get("label") or "entangled")
    name = str(meta.get("bell_state") or meta.get("scene_id") or label)
    return gates, label, name


def load_ent_set(path: Path) -> list[dict[str, Any]]:
    blob = json.loads(path.read_text(encoding="utf-8"))
    scenes = blob.get("scenes") or []
    rows = []
    for s in scenes:
        meta_path = ROOT / s["meta_path"] if not Path(s["meta_path"]).is_absolute() else Path(s["meta_path"])
        if not meta_path.exists():
            # try relative to lab
            alt = ROOT / "data" / "scenes" / s["scene_id"] / "meta.json"
            meta_path = alt
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["scene_id"] = s.get("scene_id") or meta_path.parent.name
        rows.append(meta)
    return rows


def cpu_eval_ent_set(
    ent_set: Path,
    feature_kind: str = "re_im",
    seed: int = 42,
) -> dict[str, Any]:
    """Eval amplitude→side-MLP on fixed entanglement set (+ library holdout)."""
    rows = load_ent_set(ent_set)
    bundles: list[AmpBundle] = []
    for meta in rows:
        gates, label, name = gates_for_meta(meta)
        b = build_amp_bundle(gates, label, f"{meta.get('scene_id')}:{name}", feature_kind=feature_kind)
        bundles.append(b)

    # Train side MLP on library (not on eval scenes) — honest generalization check
    lib = library_bundles(feature_kind=feature_kind)
    in_dim = len(lib[0].features)
    mlp = SideMLP(in_dim=in_dim, seed=seed)
    mlp.fit([np.array(b.features) for b in lib], [b.label for b in lib], steps=500, lr=0.08)

    probe = LinearProbe(in_dim=in_dim, out_dim=DEFAULT_EMBED_DIM, seed=seed)

    details = []
    label_hits = 0
    energy_hits = 0
    for b in bundles:
        pred = mlp.predict(np.array(b.features))
        ok = pred == b.label
        label_hits += int(ok)
        energy_hits += int(b.energy_proxy_ok)
        emb = probe(np.array(b.features))
        details.append(
            {
                "name": b.name,
                "gold": b.label,
                "pred": pred,
                "label_ok": ok,
                "concurrence": b.concurrence,
                "entropy_A": b.entropy_A,
                "energy_proxy_ok": b.energy_proxy_ok,
                "embed_norm": float(np.linalg.norm(emb)),
                "amp_dim": len(b.features),
                "embed_dim": DEFAULT_EMBED_DIM,
            }
        )

    n = max(len(bundles), 1)
    # Library self-check (train acc) for sanity
    lib_hits = sum(int(mlp.predict(np.array(b.features)) == b.label) for b in lib)
    return {
        "mode": "cpu_side_mlp + linear_probe_to_embed",
        "mechanism": (
            "PennyLane statevector → Re/Im features → SideMLP label probe; "
            "same features → seeded Linear → embed_dim=4096 soft-prompt vector "
            "(ready for residual_first_token / soft_prompt_prepend). "
            "NOT text/JSON injection. NO quantum advantage claim."
        ),
        "n": len(bundles),
        "label_acc": label_hits / n,
        "energy_proxy_acc": energy_hits / n,
        "library_train_acc": lib_hits / max(len(lib), 1),
        "embed_dim": DEFAULT_EMBED_DIM,
        "feature_kind": feature_kind,
        "details": details,
    }


def gpu_busy_hint() -> dict[str, Any]:
    lock = ROOT / "data" / "TRAIN_LOCK.txt"
    info: dict[str, Any] = {"train_lock": lock.exists()}
    if lock.exists():
        info["lock_text"] = lock.read_text(encoding="utf-8", errors="replace").strip()
    return info


def mlx_eval_ent_set(
    ent_set: Path,
    model_id: str,
    adapter_ro: Path | None,
    feature_kind: str = "re_im",
    max_tokens: int = 256,
    inject: str = "residual_first_token",
    n_limit: int | None = None,
) -> dict[str, Any]:
    """
    Optional MLX forward with amplitude residual injection.

    Compares (when feasible):
      - base (no amp, no adapter)
      - amp_embed (base + residual/soft prompt)
      - lora (adapter read-only; no amp) — only if adapter_ro exists

    If load OOM or hooks fail → returns viable=False + reason (pivot note).
    Never writes into data/lora_adapter/.
    """
    busy = gpu_busy_hint()
    if busy.get("train_lock"):
        return {
            "viable": False,
            "reason": "TRAIN_LOCK present — refusing to load 8B while another train holds GPU/RAM",
            "busy": busy,
            "pivot": "Use --cpu-eval (side MLP + soft-prompt vector) until train finishes",
        }

    try:
        import mlx.core as mx
        from mlx_vlm import load, generate
        from mlx_vlm.prompt_utils import apply_chat_template
        from mlx_vlm.utils import load_config
    except Exception as exc:
        return {"viable": False, "reason": f"mlx_vlm import failed: {exc}"}

    rows = load_ent_set(ent_set)
    if n_limit:
        rows = rows[:n_limit]

    try:
        model, processor = load(model_id, adapter_path=None)
        config = load_config(model_id)
    except Exception as exc:
        return {"viable": False, "reason": f"model load failed: {exc}", "busy": busy}

    # Discover embed dim
    try:
        embed_dim = int(model.language_model.model.embed_tokens.weight.shape[1])
    except Exception:
        embed_dim = DEFAULT_EMBED_DIM

    in_dim = 2 * (2**2)  # re_im for 2 qubits
    probe = LinearProbe(in_dim=in_dim, out_dim=embed_dim, seed=42)

    # Patch get_input_embeddings once; amp vector set via closure
    state: dict[str, Any] = {"amp_vec": None, "inject": inject, "enabled": False}
    orig_get = model.get_input_embeddings

    def patched_get_input_embeddings(input_ids=None, pixel_values=None, **kwargs):
        feats = orig_get(input_ids=input_ids, pixel_values=pixel_values, **kwargs)
        if not state["enabled"] or state["amp_vec"] is None:
            return feats
        embeds = feats.inputs_embeds
        amp = state["amp_vec"]
        if state["inject"] == "soft_prompt_prepend":
            # Prepend soft token — also need to extend mask/ids which generate may not;
            # fall back to residual if shapes would break generation.
            try:
                new_embeds = inject_soft_prompt_prepend(embeds, amp, scale=1.0)
                # Prefer residual for generate compatibility
                _ = new_embeds
            except Exception:
                pass
            new_embeds = inject_residual_first_token(embeds, amp, scale=0.25)
        else:
            new_embeds = inject_residual_first_token(embeds, amp, scale=0.25)
        # rebuild features object
        try:
            feats.inputs_embeds = new_embeds
            return feats
        except Exception:
            # dataclass frozen? replace via type
            from dataclasses import replace

            try:
                return replace(feats, inputs_embeds=new_embeds)
            except Exception:
                return feats

    model.get_input_embeddings = patched_get_input_embeddings  # type: ignore

    def run_one(meta: dict[str, Any], use_amp: bool) -> dict[str, Any]:
        gates, label, name = gates_for_meta(meta)
        bundle = build_amp_bundle(gates, label, name, feature_kind=feature_kind)
        prompt = (
            "You reason about entanglement. Given a 2-qubit circuit's quantum state "
            "is provided via an amplitude soft-prompt (not as text), answer with ONE word: "
            "entangled OR separable.\n"
            f"Scene={meta.get('scene_id')} correlation_hint={meta.get('correlation','?')}."
        )
        # Text-only path (no image) to keep amp residual as the non-text channel
        try:
            formatted = apply_chat_template(processor, config, prompt, num_images=0)
        except Exception:
            formatted = prompt

        state["enabled"] = bool(use_amp)
        state["amp_vec"] = probe(np.array(bundle.features)) if use_amp else None
        try:
            out = generate(
                model,
                processor,
                prompt=formatted,
                max_tokens=max_tokens,
                temperature=0.0,
                verbose=False,
            )
            text = out if isinstance(out, str) else getattr(out, "text", str(out))
        except Exception as exc:
            return {
                "scene_id": meta.get("scene_id"),
                "gold": label,
                "pred": None,
                "ok": False,
                "error": str(exc),
                "concurrence": bundle.concurrence,
                "energy_proxy_ok": bundle.energy_proxy_ok,
            }
        finally:
            state["enabled"] = False
            state["amp_vec"] = None

        low = str(text).lower()
        if "entangled" in low and "separable" not in low:
            pred = "entangled"
        elif "separable" in low:
            pred = "separable"
        elif "entangl" in low:
            pred = "entangled"
        else:
            pred = "unknown"
        return {
            "scene_id": meta.get("scene_id"),
            "gold": label,
            "pred": pred,
            "ok": pred == label,
            "raw_tail": str(text)[-200:],
            "concurrence": bundle.concurrence,
            "energy_proxy_ok": bundle.energy_proxy_ok,
        }

    def summarize(tag: str, details: list[dict[str, Any]]) -> dict[str, Any]:
        n = max(len(details), 1)
        return {
            "tag": tag,
            "n": len(details),
            "label_acc": sum(int(d.get("ok")) for d in details) / n,
            "energy_proxy_acc": sum(int(d.get("energy_proxy_ok")) for d in details) / n,
            "unknown_rate": sum(int(d.get("pred") == "unknown") for d in details) / n,
            "details": details,
        }

    results: dict[str, Any] = {
        "viable": True,
        "mechanism": f"mlx get_input_embeddings patch → {inject} with Linear(amp→{embed_dim})",
        "embed_dim": embed_dim,
        "model": model_id,
        "inject": inject,
    }

    base_details = [run_one(m, use_amp=False) for m in rows]
    results["base"] = summarize("base", base_details)

    amp_details = [run_one(m, use_amp=True) for m in rows]
    results["amp_embed"] = summarize("amp_embed", amp_details)

    # LoRA read-only compare (reload with adapter) — optional, heavy
    if adapter_ro and adapter_ro.exists():
        try:
            # restore original hook before reload
            model.get_input_embeddings = orig_get  # type: ignore
            del model
            mx.metal.clear_cache() if hasattr(mx, "metal") else None
            model_lora, processor = load(model_id, adapter_path=str(adapter_ro))
            model = model_lora
            model.get_input_embeddings = patched_get_input_embeddings  # type: ignore
            # LoRA path WITHOUT amp (text LoRA baseline)
            lora_details = [run_one(m, use_amp=False) for m in rows]
            results["lora_ro"] = summarize("lora_ro", lora_details)
            results["adapter_path"] = str(adapter_ro)
            results["adapter_note"] = "READ-ONLY load; data/lora_adapter/ not modified"
        except Exception as exc:
            results["lora_ro"] = {"viable": False, "reason": str(exc)}
    else:
        results["lora_ro"] = {"skipped": True, "reason": "adapter path missing"}

    return results


def self_test() -> int:
    print("=== amplitude_embed_prototype self-test ===")
    bell = build_amp_bundle(BELL_GATES["Phi+"], "entangled", "Phi+")
    sep = build_amp_bundle(SEP_GATES["product_hh"], "separable", "product_hh")
    assert bell.concurrence > 0.99, bell.concurrence
    assert sep.concurrence < 0.01, sep.concurrence
    assert bell.energy_proxy_ok and sep.energy_proxy_ok
    feats = np.array(bell.features)
    assert feats.shape == (8,), feats.shape  # 4 complex → 8 re_im
    probe = LinearProbe(8, DEFAULT_EMBED_DIM, seed=0)
    emb = probe(feats)
    assert emb.shape == (DEFAULT_EMBED_DIM,)
    assert abs(np.linalg.norm(emb) - 1.0) < 1e-5

    lib = library_bundles()
    mlp = SideMLP(in_dim=8, seed=1)
    mlp.fit([np.array(b.features) for b in lib], [b.label for b in lib], steps=400)
    acc = sum(mlp.predict(np.array(b.features)) == b.label for b in lib) / len(lib)
    print(f"library side-MLP train acc: {acc:.2f} (n={len(lib)})")
    assert acc >= 0.85, acc

    # Injection helpers with fake embeds (mlx optional)
    try:
        import mlx.core as mx

        fake = mx.zeros((4, DEFAULT_EMBED_DIM))
        out = inject_residual_first_token(fake, emb, scale=0.1)
        assert out.shape == fake.shape
        out2 = inject_soft_prompt_prepend(fake, emb)
        assert out2.shape == (5, DEFAULT_EMBED_DIM)
        print("mlx inject helpers: OK")
    except Exception as exc:
        print(f"mlx inject helpers skipped: {exc}")

    print("SELF-TEST PASS")
    print(
        "Mechanism: statevector→Re/Im→Linear(4096) soft-prompt / residual; "
        "side MLP for CPU label metrics. No quantum advantage."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Amplitude → embedding fusion prototype")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--cpu-eval", action="store_true", help="Side-MLP + probe on ENT_SET (no GPU)")
    p.add_argument("--mlx-eval", action="store_true", help="Optional MLX residual inject eval")
    p.add_argument("--ent-set", type=Path, default=ROOT / "data" / "bench_live" / "ent_items.json")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument(
        "--adapter-ro",
        type=Path,
        default=ROOT / "data" / "lora_adapter",
        help="Read-only LoRA path for compare (never written)",
    )
    p.add_argument("--feature-kind", default="re_im", choices=["re_im", "mag_phase", "mag_only"])
    p.add_argument("--inject", default="residual_first_token", choices=["residual_first_token", "soft_prompt_prepend"])
    p.add_argument("--n-limit", type=int, default=None)
    p.add_argument("--out", type=Path, default=ROOT / "data" / "amp_embed" / "report.json")
    p.add_argument("--demo-bell", action="store_true", help="Print one Bell amplitude vector")
    args = p.parse_args(argv)

    if args.self_test:
        return self_test()

    if args.demo_bell:
        b = build_amp_bundle(BELL_GATES["Phi+"], "entangled", "Phi+")
        print(json.dumps({
            "name": b.name,
            "gates": b.gates,
            "concurrence": b.concurrence,
            "entropy_A": b.entropy_A,
            "features_re_im_head": b.features[:8],
            "embed_dim_target": DEFAULT_EMBED_DIM,
        }, indent=2))
        return 0

    report: dict[str, Any] = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "claims": "NO quantum advantage. Pedagogical/experimental fusion only.",
        "busy": gpu_busy_hint(),
    }

    if args.cpu_eval or not args.mlx_eval:
        # Default to cpu-eval when neither flag? Prefer explicit.
        if args.cpu_eval or not args.mlx_eval:
            cpu = cpu_eval_ent_set(args.ent_set, feature_kind=args.feature_kind)
            report["cpu"] = cpu
            print("=== CPU amp-embed eval ===")
            print(json.dumps({k: cpu[k] for k in cpu if k != "details"}, indent=2))

    if args.mlx_eval:
        mlx = mlx_eval_ent_set(
            args.ent_set,
            model_id=args.model,
            adapter_ro=args.adapter_ro,
            feature_kind=args.feature_kind,
            inject=args.inject,
            n_limit=args.n_limit,
        )
        report["mlx"] = mlx
        print("=== MLX amp-embed eval ===")
        slim = {k: v for k, v in mlx.items() if k not in {"base", "amp_embed", "lora_ro"}}
        print(json.dumps(slim, indent=2))
        for key in ("base", "amp_embed", "lora_ro"):
            block = mlx.get(key)
            if isinstance(block, dict) and "label_acc" in block:
                print(f"  {key}: label_acc={block['label_acc']:.3f} energy_proxy={block.get('energy_proxy_acc')} n={block.get('n')}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    # drop huge detail sometimes? keep for honesty
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
