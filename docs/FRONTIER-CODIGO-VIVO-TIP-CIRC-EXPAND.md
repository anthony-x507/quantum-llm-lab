# FRONTIER — tip-circ-expand (grounded circ vision coverage)

**Branch:** `frontier/tip-circ-expand` → **FOLDED** into `frontier/codigo-vivo-tip`  
**Base (side):** tip `e70b23a` (post R11 / motion-r4 / vision-ground)  
**Fold worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-cv` (Mac-111)  
**When (side):** 2026-09-24 ~14:12–14:14 ET · **Fold:** 2026-09-24 ~14:54 ET  
**Side freeze:** `codigo_vivo_tip_circ_expand_100pct_20260924_141414`  
**Fold freeze:** `codigo_vivo_tip_circ_expand_fold_100pct_20260924_145451`  
**Fold feat SHA:** `5defd36` (`5defd36abdba46f278ab77b150579718ddfb3f9c`)  
**Feat SHA (side):** `bf906f9` (`bf906f9e609c81e0880d29ca168680714edd9b9d`)  
**Scope:** Folded into tip-cv. Pillars / R14+ / LP **not** folded.

## LOCK (Anthony)

- Tip vis pillar stays **BASE**. No LoRA writes.
- Mixed (d) **1.0**, R13 **52/52·44/44**, future track **~99.34%**, far MAE **2.600**, DZ/mid/TTI **100%**, inv/collision **100%** — do not regress.
- GT only in eval sidecars; never in prompts / memory / retrieval.
- Quantum `data/lora_adapter/` = **READ-ONLY**.

## What changed

Expand circuit vision coverage with **+3 grounded** text-card scenes + GT-free grounding cues:

1. **Scenes** (`vis_circ_03/04/05`): Bell H+CNOT only (2q); GHZ H+CNOT+CNOT (3q); X+RY(π/2)+CNOT (2q).
2. **Grounding** (`vision/grounding.py`): anti-invent X when absent; emit each CNOT in a chain; `n_qubits` match image.
3. **Bridge** (`examples/llm_quantum_bridge.py`): fallback qubit regex `[1-9] qubits?`.
4. **Renderer:** `examples/vision_circ/render_grounded_circ_scenes.py` (PNGs under shared `QLAB_DATA/bench_live/vision_items/`).

## Metrics (fold re-smoke on tip @ abf0d25)

| | tip before | tip after fold |
|--|------------|----------------|
| Vision BASE | **1.000** (10/10) | **1.000** (13/13) |
| Circ axis | **2/2** | **5/5** |
| Mixed (d) unified | **1.0** | **1.0** held |
| Pillar routing (smoke) | 26/26 | **29/29** |
| Hardneg smoke | 18/18 | **18/18** |

Circ detail after: vis_circ_01…05 all **true** (MLX BASE, Qwen3-VL-8B-Thinking-4bit).

Floors retained (untouched surfaces): R13 **52/52·44/44**; future track **99.34%**; far MAE **2.600 m**; DZ/mid/TTI **100%**; inv_cv/collision/choose_safest **100%** n=40/2850; tip vis **BASE**.

Anti-contam: **CLEAN** (`prompt_touches_gt=false`, adapters RO mtime unchanged).  
Caveat: vision score is BASE VLM + grounding prompts — **not** a VLM-finetune claim. No quantum-advantage claim.

## Adapters RO

- `data/lora_adapter/` — **no writes** (before/after snapshot equal).
- Tip vis stays BASE (`--base-only`).

## Commands

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-cv
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
unset PYTHONPATH
ln -sfn "$QLAB_DATA/bench_live/vision_items"/vis_circ_0{3,4,5}.png data/bench_live/vision_items/
.venv/bin/python examples/bench_codigo_vivo.py --skip-python --skip-ent --base-only \
  --model mlx-community/Qwen3-VL-8B-Thinking-4bit \
  --out data/frontier_tip_circ_expand_fold_bench_after.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval \
  --bench data/frontier_tip_circ_expand_fold_bench_after.json \
  --out data/frontier_moe_verifier_mixed_cpu_circ_expand_fold.json
.venv/bin/python examples/moe_verifier_mixed_live.py --smoke \
  --out data/frontier_moe_verifier_mixed_smoke_circ_expand_fold.json
```

## Non-goals

- No merge to main.
- No CloudAgent.
- No write to `data/lora_adapter/`.
- Pillars @ b536f57 / R14+ / LP remain next-queue only.

## Fold into tip-cv (2026-09-24 ~14:54 ET)

Merge-port side `bf906f9`/`2631d83` onto tip `abf0d25` (post future-track-r3): surgical vision_items + mixed circ routing extras + grounding/bridge/renderer; avoid unicode-noise rewrite of mixed hardnegs. Re-smoke MLX BASE 13/13 · circ 5/5; mixed (d) **1.0**; smoke pillars **29/29** · hardneg **18/18**.

Freeze `codigo_vivo_tip_circ_expand_fold_100pct_20260924_145451`. Floors held. Adapters RO. Tip vis BASE.
