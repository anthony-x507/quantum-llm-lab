# FRONTIER — Circuit-graph MoE scaffold HARD expand

**Branch:** `frontier/circuit-graph-scaffold-hard`  
**Written:** 2026-09-24 10:57:26  
**Base:** `frontier/circuit-graph-moe-scaffold` @ `e769d16`

## Claims (cannot-claim)

- **NO** quantum-advantage claims.
- Hard fixtures are **structural sketches** (teleport / small-QFT proxy / parity / cluster / W / traps).
- Alphabet remains `h,x,y,z,cx,ry` — QFT/teleport are classical-graph scaffold targets, not hardware claims.
- Original freeze `data/FRONTIER_CIRCUIT_GRAPH_SCAFFOLD_FREEZE.json` is **kept intact**.
- `data/lora_adapter/` is **READ-ONLY**.

## Hard set ablation

- Router method: `heuristic`
- Polish features: `False`
- Fixtures: n=15 (ent evaluated n=15,
  skipped non-ent n=0)

| Arm | n | parse_rate | structure_rate | solve_rate |
|-----|---|------------|----------------|------------|
| no-scaffold | 15 | 0.933 (14) | 0.933 (14) | 0.267 (4) |
| scaffold | 15 | 1.000 (15) | 1.000 (15) | 0.933 (14) |
| **Δ (on−off)** |  | **+0.067** | **+0.067** | **+0.667** |

**Clear win (hard)?** `True` — rule: `Δsolve≥0.15 OR (Δstructure≥0.15 AND Δparse≥0.05)`

## Original freeze still held?

- **`True`**

## Hard families covered

- teleport (≥3q Bell resource + interaction)
- small QFT proxy (H + RY phase + CX)
- parity / error-detect ancilla CX checks
- multi-qubit non-GHZ (cluster, W-proxy, swap-like)
- product vs entangled traps

## Anti-contamination

```json
{
  "gt_in_scaffold_hints": false,
  "prompt_touches_gt": false,
  "graph_builder_rejects_gt_kwargs": true,
  "lora_adapter_writes": false
}
```

## Reproduce

```bash
python examples/circuit_graph_moe_scaffold.py --hard --cpu-eval
python examples/circuit_graph_moe_scaffold.py --hard --cpu-eval --polish
python examples/circuit_graph_moe_scaffold.py --recheck-original
```

