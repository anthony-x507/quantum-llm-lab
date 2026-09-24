# Hybrid oracle loop — results (method 4 · tip-of-spear)

**When:** 2026-09-24 04:39 ET · **Claim:** no quantum advantage
**Lock:** train-first / own-delta only (base vs our adapters). No Gemini/GPT compares.
**Prototype:** `examples/hybrid_oracle_loop.py` · revise=gold-free local physics
**ENT_SET:** `data/bench_live/ent_items.json` n=12 · rounds≤2 · proposer=`heuristic`
**Elapsed:** 0.572s (CPU PennyLane) · `data/lora_adapter/` RO

## A) Own-delta — base vs our LoRA RO

| path | n | label_acc | Jev | compile | energy_ok |
|------|---|-----------|-----|---------|-----------|
| base VLM | 10 | 0.0 | 0.0 | 0.0 | 0.0 |
| our LoRA RO | 10 | 0.9 | 1.0 | 1.0 | 1.0 |
| Δ (ours−base) | — | 0.9 | 1.0 | 1.0 | 1.0 |

Source: `/Users/anthony/Documents/quantum-llm-lab/data/eval_compare_rebalance.json` — own-delta base vs our LoRA RO only

## B) Hybrid loop — before / after (gold-free revise)

| path | label_acc | energy_ok | energy_proxy | compile | Jev |
|------|-----------|-----------|--------------|---------|-----|
| single-shot | 0.333 | 1.000 | 0.333 | 1.000 | 0.833 |
| after loop | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** |
| Δ (loop−single) | +0.667 | +0.000 | +0.667 | +0.000 | +0.167 |

## vs our LoRA RO (same-family ref)

| ref | label_acc | Jev | compile | energy_ok | note |
|-----|-----------|-----|---------|-----------|------|
| our LoRA RO cached | 1.0 | 1.0 | 1.0 | 1.0 | cached eval ent subset (not ENT_SET-12) |
| loop − our LoRA label | 0.0 | — | — | — | |

**Scenes improved:** 10/12
**Loop helps vs own single-shot:** YES

## Honest note

Loop improved vs its own single-shot (Δlabel=+0.667, Δjev=+0.167). After-loop label_acc=1.000 ≥ cached LoRA ref (1.000) on this comparison — still classical simulation + repair, not quantum advantage. Oracle is PennyLane default.qubit (CPU classical sim).

Gold-free revise uses local physics (minimal Bell / drop CX / scrub energy), not scene-gold paste. Tip-of-spear; train remains primary. No quantum advantage.

