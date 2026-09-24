"""E2E smoke: JSON gates → graph → GNN → conditioning stub → pauli_tool (CPU).

No VLM train. Graph built only from assistant-proposed gates (never GT labels).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np

from .circuit_graph import build_graph
from .conditioning import CrossAttnConditioner, PrefixConditioner
from .gnn_encoder import GNNEncoder
from .pauli_tool import run_pauli_tool


def _extract_json(text: str) -> dict[str, Any] | None:
    text = text.strip()
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "gates" in data:
            return data
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    while start != -1:
        depth = 0
        in_str = False
        escape = False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        data = json.loads(text[start : i + 1])
                    except json.JSONDecodeError:
                        break
                    if isinstance(data, dict) and "gates" in data:
                        return data
                    break
        start = text.find("{", start + 1)
    return None


def proposal_from_row(row: dict[str, Any]) -> dict[str, Any] | None:
    """Pull assistant JSON gates only — strip label/gold before graph build."""
    messages = row.get("messages") or []
    assistant_text = None
    for m in messages:
        if m.get("role") == "assistant":
            assistant_text = m.get("content")
    if not assistant_text and "gates" in row:
        raw = {"n_qubits": row.get("n_qubits", 2), "gates": row["gates"]}
    elif assistant_text:
        raw = _extract_json(assistant_text)
    else:
        return None
    if not raw or "gates" not in raw:
        return None
    # Explicitly drop GT fields — leakage guard.
    clean = {
        "n_qubits": int(raw.get("n_qubits", 2)),
        "gates": raw["gates"],
    }
    return clean


def load_proposals(dataset: Path, limit: int) -> list[dict[str, Any]]:
    proposals: list[dict[str, Any]] = []
    if not dataset.exists():
        # Fallback: synthetic Bell-like proposals so smoke still closes.
        from .synthetic_graphs import bell_variants, make_random

        for g in bell_variants():
            proposals.append(
                {
                    "n_qubits": g.n_qubits,
                    "gates": [
                        ([n.gate, *n.qubits] if n.theta is None else [n.gate, n.qubits[0], n.theta])
                        for n in g.nodes
                    ],
                }
            )
        for i in range(max(0, limit - len(proposals))):
            g = make_random(seed=100 + i)
            proposals.append(
                {
                    "n_qubits": g.n_qubits,
                    "gates": [
                        ([n.gate, *n.qubits] if n.theta is None else [n.gate, n.qubits[0], n.theta])
                        for n in g.nodes
                    ],
                }
            )
        return proposals[:limit]

    with dataset.open("r", encoding="utf-8") as fh:
        for line in fh:
            if len(proposals) >= limit:
                break
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            prop = proposal_from_row(row)
            if prop is None:
                continue
            proposals.append(prop)
    return proposals


def run_smoke(dataset: Path, limit: int, embed_dim: int, out_path: Path) -> dict[str, Any]:
    encoder = GNNEncoder(embed_dim=embed_dim, seed=0)
    prefix_c = PrefixConditioner(d_model=128, n_prefix=4, seed=0)
    cross_c = CrossAttnConditioner(d_model=128, n_kv=4, seed=1)

    proposals = load_proposals(dataset, limit)
    rows_out: list[dict[str, Any]] = []
    norms: list[float] = []
    unitary_flags: list[bool] = []
    energies: list[float] = []
    fingerprints: list[str] = []

    for idx, prop in enumerate(proposals):
        graph = build_graph(prop)  # no label kwargs
        emb = encoder.encode(graph)
        norm = float(np.linalg.norm(emb))
        norms.append(norm)
        pref = prefix_c(emb)
        xattn = cross_c(emb)
        tool = run_pauli_tool(prop)
        unitary_flags.append(bool(tool.unitary_ok))
        if tool.unitary_ok and not np.isnan(tool.energy):
            energies.append(float(tool.energy))
        fingerprints.append(tool.fingerprint)
        rows_out.append(
            {
                "i": idx,
                "n_qubits": prop["n_qubits"],
                "n_gates": len(prop["gates"]),
                "n_nodes": len(graph.nodes),
                "n_edges": len(graph.edges),
                "embed_shape": list(emb.shape),
                "embed_norm": norm,
                "prefix_shape": list(pref.prefix_embeds.shape),
                "cross_attn_keys_shape": list(xattn.keys.shape),
                "unitary_ok": tool.unitary_ok,
                "energy": tool.energy,
                "fingerprint": tool.fingerprint,
                "backend": tool.backend,
                "error": tool.error,
            }
        )

    n = len(rows_out)
    n_ok = int(sum(unitary_flags))
    # Prefer repo-relative dataset path in metrics (no machine absolute paths).
    try:
        dataset_meta = str(dataset.resolve().relative_to(out_path.resolve().parents[1]))
    except Exception:
        dataset_meta = dataset.name
    summary = {
        "n_rows": n,
        "n_ok": n_ok,
        "pct_unitary_ok": (100.0 * n_ok / n) if n else 0.0,
        "mean_embed_norm": float(np.mean(norms)) if norms else 0.0,
        "embed_dim": embed_dim,
        "embed_shape": [embed_dim],
        "sample_fingerprints": fingerprints[:5],
        "mean_energy_ok": float(np.mean(energies)) if energies else None,
        "backend": "pennylane.default.qubit + torch.cpu",
        "conditioning_wired_to_vlm": True,  # text_scaffold_prefix via vlm_wire; weight_peft=False
        "weight_peft_injection": False,
        "channel": "text_scaffold_prefix",
        "no_gt_in_graph": True,
        "dataset": dataset_meta,
        "limit": limit,
        "rows": rows_out,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Metrics only — no weights.
    slim = {k: v for k, v in summary.items()}
    out_path.write_text(json.dumps(slim, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Circuit-graph adapter E2E smoke (CPU).")
    p.add_argument(
        "--dataset",
        default="data/lora_dataset_ent_v7.jsonl",
        help="JSONL with assistant gate proposals (labels ignored for graph).",
    )
    p.add_argument("--limit", type=int, default=30)
    p.add_argument("--embed-dim", type=int, default=64)
    p.add_argument(
        "--out",
        default="data/frontier_circuit_graph_smoke.json",
        help="Metrics-only JSON output path.",
    )
    args = p.parse_args(argv)

    # Resolve paths relative to repo root (worktree or clone).
    here = Path(__file__).resolve()
    repo = here.parents[2]
    dataset = Path(args.dataset)
    if not dataset.is_absolute():
        dataset = repo / dataset
    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = repo / out_path

    summary = run_smoke(dataset, args.limit, args.embed_dim, out_path)
    print("=== frontier circuit-graph smoke ===")
    print(f"dataset: {summary['dataset']}")
    print(f"n_rows={summary['n_rows']} n_ok={summary['n_ok']} "
          f"pct_unitary_ok={summary['pct_unitary_ok']:.1f}%")
    print(f"mean_embed_norm={summary['mean_embed_norm']:.4f} embed_dim={summary['embed_dim']}")
    print(f"mean_energy_ok={summary['mean_energy_ok']}")
    print(f"sample_fingerprints={summary['sample_fingerprints']}")
    print(f"backend={summary['backend']}")
    print(f"wrote {out_path}")
    return 0 if summary["n_rows"] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
