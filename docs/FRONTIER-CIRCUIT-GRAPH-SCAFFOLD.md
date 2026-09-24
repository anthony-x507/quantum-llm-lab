# FRONTIER — Circuit-graph MoE scaffold (entanglement / código-circuito)

**Branch:** `frontier/circuit-graph-moe-scaffold`  
**Written:** 2026-09-24 10:48:50  
**Parent:** `frontier/moe-verifier-codigo-vivo` @ `3eeeb33` + `frontier/circuit-graph` @ `3beef72`

## Claims (cannot-claim)

- **NO** quantum-advantage claims.
- Scaffold uses a **classical** Clifford–Pauli circuit graph + torch-CPU GNN features as *structure hints*.
- Metrics are **own-delta** parse/structure/solve on a CPU heuristic proposer (stand-in for LLM).
- Anti-contam: scaffold hints never include GT / gold / label fields; `build_graph` rejects GT kwargs.
- `data/lora_adapter/` is **READ-ONLY**.

## What shipped

| Piece | Path | Role |
|-------|------|------|
| Circuit-graph adapter | `examples/circuit_graph_adapter/` | Gates → anticomm graph → GNN → Pauli tool (from `frontier/circuit-graph`) |
| MoE scaffold hook | `examples/circuit_graph_moe_scaffold.py` | When router lane=`ent`, inject graph features/hints; CPU ablation ON vs OFF |
| Prior PEFT doc | `docs/FRONTIER-PEFT-ENT.md` | Formalism (arXiv:2503.14448-style) |

## Integration

1. `moe.route(prompt)` → if `ent`, optionally `inject_scaffold(prompt)`.
2. Scaffold block lists prior template **features** (n_nodes, n_edges, anticomm_density,
   gate_hist, fingerprint) + a gate **sketch** — never scene labels.
3. Proposer (CPU heuristic here; VLM later) reads the block to structure JSON `{n_qubits, gates}`.

## CPU ablation results

- Router method: `heuristic`
- Polish features: `False`
- Fixtures: n=24 (ent evaluated n=20,
  skipped non-ent n=4)

| Arm | n | parse_rate | structure_rate | solve_rate |
|-----|---|------------|----------------|------------|
| no-scaffold | 20 | 0.750 (15) | 0.650 (13) | 0.450 (9) |
| scaffold | 20 | 1.000 (20) | 1.000 (20) | 0.900 (18) |
| **Δ (on−off)** |  | **+0.250** | **+0.350** | **+0.450** |

**Clear win?** `True` — rule: `Δsolve≥0.15 OR (Δstructure≥0.15 AND Δparse≥0.05)`

## Honest limits

- CPU heuristic ≠ live Qwen/MLX VLM; Δ is scaffold usability on a stub proposer.
- `solve_ok` uses **prompt-keyword structural goals** (Bell/product/GHZ), not scene GT labels.
- GNN conditioning stubs are still **not** wired into the real VLM (`wired_to_vlm=false`).
- No claim that graph features beat a strong LLM without scaffold on the same items.

## Anti-contamination

```json
{
  "gt_in_scaffold_hints": false,
  "prompt_touches_gt": false,
  "graph_builder_rejects_gt_kwargs": true,
  "lora_adapter_writes": false
}
```

## Hard expand (stacked)

Stacked branch `frontier/circuit-graph-scaffold-hard` adds ≥12 harder fixtures
(teleport, small-QFT proxy, parity/error-detect, cluster/W/swap, product traps)
without touching this freeze.

- Doc: `docs/FRONTIER-CIRCUIT-GRAPH-SCAFFOLD-HARD.md`
- JSON: `data/frontier_circuit_graph_scaffold_hard.json`
- Freeze file above remains the source of truth for the original n=20 set.

## Reproduce

```bash
python examples/circuit_graph_moe_scaffold.py --smoke
python examples/circuit_graph_moe_scaffold.py --cpu-eval --limit 24
python examples/circuit_graph_moe_scaffold.py --cpu-eval --polish --limit 24
```

