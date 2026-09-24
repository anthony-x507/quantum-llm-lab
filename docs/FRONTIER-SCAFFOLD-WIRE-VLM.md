# FRONTIER — Scaffold wire → VLM (MoE ent lane)

**Branch:** `frontier/scaffold-wire-vlm`  
**Written:** 2026-09-24 12:55:26  
**Parent tip:** `frontier/codigo-vivo-tip` @ `f0fe729`

## Claim scope

- **NO** quantum-advantage claims.
- `wired_to_vlm=true` = GT-free circuit-graph **text scaffold** is attached to the
  prompt the VLM/proposer receives (`channel=text_scaffold_prefix`).
- Companion GNN prefix/cross-attn tensors are packaged alongside;
  `weight_peft_injection=false` (no mlx-vlm weight edit yet).
- Anti-contam: hints never include GT/gold/label; `data/lora_adapter/` READ-ONLY.

## What changed

| Piece | Path | Role |
|-------|------|------|
| VLM wire API | `examples/circuit_graph_adapter/vlm_wire.py` | `build_vlm_scaffold_signal` / `wire_prompt_for_vlm` |
| MoE hook | `examples/circuit_graph_moe_scaffold.py` | `--wire-vlm` CPU smoke + flag in ablation |
| Mixed live | `examples/moe_verifier_mixed_live.py` | ent lane reports `wired_to_vlm` |
| Live mlx ent | `examples/bench_codigo_vivo.py` + mlx pillars | inject scaffold into ent VLM prompt |

## Wire smoke

- `wired_to_vlm`: `True`
- channel: `text_scaffold_prefix`
- weight_peft_injection: `False`
- ent markers: `True`  gt_leak: `False`

## CPU ablation (own-delta; floor check)

| Arm | solve_rate |
|-----|------------|
| no-scaffold | 0.4 |
| scaffold | 0.9 |
| **Δsolve** | **0.5** |

- clear_win: `True`
- original freeze held: `True`
- hard Δsolve (if run): `0.6666`

## Mixed unified floor

- floor ≥0.967 prefer 1.0; observed overall: `1.0`
- floor_held: `True`

## Reproduce

```bash
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/circuit_graph_moe_scaffold.py --wire-vlm --polish
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

