# Hybrid oracle loop — results (method 4)

**When:** 2026-09-24 04:37 ET · **Claim:** no quantum advantage
**Prototype:** `examples/hybrid_oracle_loop.py`
**ENT_SET:** `data/bench_live/ent_items.json` n=12 · rounds≤1 · proposer=`heuristic`
**Elapsed:** 0.61s (CPU PennyLane oracle)

## Before / after (same proposer, oracle revise)

| path | label_acc | energy_ok | energy_proxy | compile | Jev |
|------|-----------|-----------|--------------|---------|-----|
| single-shot (no oracle) | 0.333 | 1.000 | 0.333 | 1.000 | 0.833 |
| after oracle loop | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** |
| Δ (loop − single) | +0.667 | +0.000 | +0.667 | +0.000 | +0.167 |

## vs cached LoRA single-shot (reference)

| ref | label_acc | Jev | compile | energy_ok | note |
|-----|-----------|-----|---------|-----------|------|
| LoRA RO cached | 1.0 | 1.0 | 1.0 | 1.0 | cached eval ent subset (not ENT_SET-12) |
| loop − LoRA label | 0.0 | — | — | — | |

**Scenes improved (label or Jev):** 10/12
**Loop helps vs own single-shot:** YES

## Honest note

Loop improved vs its own single-shot (Δlabel=+0.667, Δjev=+0.167). After-loop label_acc=1.000 ≥ cached LoRA ref (1.000) on this comparison — still classical simulation + repair, not quantum advantage. Oracle is PennyLane default.qubit (CPU classical sim).

## Mechanism

1. Model proposes circuit JSON (heuristic stub while GPU held by `qlora-ent`, or MLX when free).
2. PennyLane oracle: compile, concurrence / S(ρ_A), Jev energy rules → `{errors, suggested_fix}`.
3. Model revises ≤2 rounds applying structured feedback.
4. Metrics vs single-shot on fixed ENT_SET.

`data/lora_adapter/` untouched (READ-ONLY).

