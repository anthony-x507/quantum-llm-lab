# FRONTIER — Mixed MoE+verifier with circuit-graph scaffold

**Branch:** `frontier/mixed-with-scaffold`  
**Written:** 2026-09-24 10:57:47  
**Parents:** mixed `frontier/moe-verifier-mixed-live` @ `efc5e9d` ∪ scaffold-hard `frontier/circuit-graph-scaffold-hard` @ `ecb7974`

## What changed

- Merged circuit-graph scaffold-hard into the mixed MoE+verifier scoreboard lane.
- When **router→ent**, `--circuit-scaffold` is **DEFAULT ON** (disable with `--no-circuit-scaffold`).
- Injects GT-free Clifford–Pauli circuit-graph hints (`<<<CIRCUIT_GRAPH_SCAFFOLD>>>`) on the ent lane only.
- Python / vision lanes unchanged; python still gets the gold-free verifier ≤2.

## Claims (cannot-claim)

- **NO** quantum-advantage claims.
- Scaffold = classical graph features / structure priors only.
- Ent/vision pillar rates on CPU remain **prior-replay** (freeze-preserving).

## Scoreboard (CPU heuristic) — (a)(b)(c)(d)

| Path | python | ent label_acc | vision | overall |
|------|--------|---------------|--------|---------|
| (a) baseline | 0.000 | 0.000 | 0.900 | **0.3000** |
| (b) MoE alone | 0.000 | **1.000** | 0.900 | **0.6333** |
| (c) verifier-on-python | 1.000 | 0.000 | 0.900 | 0.6333 |
| (d) unified | **1.000** | **1.000** | 0.900 | **0.9667** |

- **Overall before → after:** `0.9667` → `0.9667` (doc display ~0.967)
- **Ent pillar Δ (b vs a):** `+1.000` (held)
- **MoE Δ overall visible:** `True`

## Freezes held?

| Freeze | Floor | Observed | Held |
|--------|-------|----------|------|
| Mixed unified overall | 0.9667 (~0.967 doc) | 0.9667 | **True** |
| Scaffold-hard solve | 0.90 | 0.9 | **True** |
| Scaffold-hard clear-win (Δsolve) | Δ≥0.15 | 0.6666 | **True** |

## Anti-contamination

```json
{
  "prompt_touches_gt": false,
  "leaks": [],
  "policy": "GT only in eval.*; never concatenated into inference prompts",
  "locked_false": true,
  "gt_never_in_inference_prompts": true,
  "ent_never_on_python": true,
  "scaffold_gt_leaks": 0,
  "circuit_scaffold_on_ent": true,
  "lock": "docs/LOCK-ANTI-CONTAMINATION.md"
}
```

- `data/lora_adapter/` **READ-ONLY** (no writes).
- No merge to `main`.

## Reproduce

```bash
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_verifier_mixed_live.py --smoke
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
.venv/bin/python examples/circuit_graph_moe_scaffold.py --recheck-original --polish
.venv/bin/python examples/circuit_graph_moe_scaffold.py --hard --cpu-eval
```

## Evidence

| File | Contents |
|------|----------|
| `data/frontier_mixed_with_scaffold.json` | Rollup (this ship) |
| `data/frontier_moe_verifier_mixed_cpu.json` | Full CPU scoreboard + scaffold meta |
| `data/frontier_moe_verifier_mixed_unified.json` | Unified pointer |
| `data/FRONTIER_CIRCUIT_GRAPH_SCAFFOLD_FREEZE.json` | Scaffold freeze (intact) |
| `data/frontier_circuit_graph_scaffold_hard_recheck.json` | Freeze recheck |
| `examples/moe_verifier_mixed_live.py` | Wiring (`--circuit-scaffold` default ON) |

## Machines

- **Mac-139** (`074c6626-…`): implement / CPU retest (this run).
