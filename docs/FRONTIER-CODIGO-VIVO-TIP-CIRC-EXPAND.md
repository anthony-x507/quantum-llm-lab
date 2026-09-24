# FRONTIER — Código-vivo tip circ-expand (side)

**Status:** **SIDE ONLY — NOT FOLDED** into `frontier/codigo-vivo-tip`  
**Branch:** `frontier/tip-circ-expand`  
**Base tip:** `e70b23a` (post R11 / motion-r4 / vision-ground)  
**When:** 2026-09-24 ~14:12–14:14 ET · Mac-111 (`074c6626-…`)  
**Claim:** NO quantum advantage. Expand grounded circ vision scenes; tip vis stays BASE.

## SHA / setup

| Field | Value |
|-------|-------|
| Tip base SHA | `e70b23a` |
| Branch | `frontier/tip-circ-expand` |
| Host | Mac-111 |
| Model | `mlx-community/Qwen3-VL-8B-Thinking-4bit` |
| Adapters | **READ-ONLY** (`ro_mtime_unchanged=true`) |
| Fold into tip | **false** |

## Why

Tip circ axis sat at **2/2** after vision-ground. This side branch adds **+3 grounded** text-card circuit scenes aligned with circuit-graph motifs (Bell-only, GHZ-3q, X+RY+CNOT) and lightly extends GT-free grounding (anti-invent X; emit each CNOT in a chain; n_qubits match image). No LoRA writes.

AVOIDED worktrees: tip-cv, tip-tti, tip-distance-mid, tip-distance-far, tip-hardneg-r12, tip-hardneg-r13, tip-inverse-r3.

## Coverage before → after

| | before (tip) | after (this side) |
|--|--------------|-------------------|
| Vision BASE | **1.000** (10/10) | **1.000** (13/13) held |
| Circ axis | **2/2** | **5/5** |
| New scenes | — | `vis_circ_03`, `vis_circ_04`, `vis_circ_05` |
| Mixed (d) unified | **1.0** | **1.0** held |

## New scenes

| id | grounded content | expected_gates | n_qubits |
|----|------------------|----------------|----------|
| `vis_circ_03` | Bell H + CNOT only (no X) | H, CNOT | 2 |
| `vis_circ_04` | GHZ H + CNOT + CNOT | H, CNOT | 3 |
| `vis_circ_05` | X + RY(pi/2) + CNOT | X, RY, CNOT | 2 |

Renderer: `examples/vision_circ/render_grounded_circ_scenes.py` (PNGs under shared `QLAB_DATA/bench_live/vision_items/`, gitignored).

## Anti-contam

| Check | Result |
|-------|--------|
| `prompt_touches_gt` | **false** |
| writes to `data/lora_adapter/` | **false** |
| `ro_mtime_unchanged` | **true** |
| tip vis pillar | **BASE** |
| merge main | **no** |
| fold into tip | **no** |

## Freeze?

Manifest: `data/freeze_manifests/codigo_vivo_tip_circ_expand_100pct_20260924_141414.json`

**YES.** Clear circ coverage rise (2/2→5/5) **and** vision BASE 1.0 held **and** mixed floor 1.0 held **and** circ axis 100% ≥80%.

## Reproduce

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-circ-expand
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
unset PYTHONPATH
ln -sfn "$QLAB_DATA/bench_live/vision_items" data/bench_live/vision_items
.venv/bin/python examples/vision_circ/render_grounded_circ_scenes.py --out-dir "$QLAB_DATA/bench_live/vision_items"
.venv/bin/python examples/bench_codigo_vivo.py --skip-python --skip-ent --base-only \
  --out data/frontier_tip_circ_expand_bench_after.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval \
  --bench data/frontier_tip_circ_expand_bench_after.json \
  --out data/frontier_moe_verifier_mixed_cpu_circ_expand.json
.venv/bin/python examples/moe_verifier_mixed_live.py --smoke \
  --out data/frontier_moe_verifier_mixed_smoke_circ_expand.json
```

## What this does NOT do

- No write to `data/lora_adapter/` or any new LoRA directory.
- No merge to `main`. No fold into tip (fold queue is TTI→mid→R12→inv-r3→far→R13).
- No CloudAgent. No quantum-advantage marketing.

**Freeze manifest:** `data/freeze_manifests/codigo_vivo_tip_circ_expand_100pct_20260924_141414.json`
