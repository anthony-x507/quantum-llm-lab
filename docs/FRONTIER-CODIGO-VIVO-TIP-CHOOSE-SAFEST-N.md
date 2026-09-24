# FRONTIER — tip-choose-safest-n (expand choose_safest coverage + hardneg)

**Status:** SIDE FREEZE (do **not** fold into tip)  
**Branch:** `frontier/tip-choose-safest-n`  
**Base tip SHA:** `9a0de24` (`frontier/codigo-vivo-tip` — read-only; tip-cv may be mid-fold)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-choose-safest-n` (Mac-111)  
**When:** see freeze manifest `frozen_at_et`  
**Freeze:** `codigo_vivo_tip_choose_safest_n_100pct_20260924_142733` @ `d3bf164`
**Scope:** Side-branch only — does **not** touch tip-cv / tip-distance-mid|far / tip-hardneg-r12..r15 / tip-inverse-r3 / tip-circ-expand / tip-future-track* / tip-tti.

## LOCK (Anthony / Leader)

- Tip collision at e0f3183 lineage: physics **100%** @ n=40 / 2850; choose_safest **100%**; motion **100%**; TTI **100%**; DZ **100%**.
- Grow **scorable choose_safest** sequences beyond n=40 with **hard negatives** (unsafe-looking but safe / vice versa / near-miss choice) while keeping physics exact.
- Anti-contam: real consequences **NEVER** at inference (GT only for eval).
- Quantum `data/lora_adapter/` = **READ-ONLY**. New adapters → `data/lora_adapter_collision/` only.
- **Do NOT fold into tip.** Fold queue owns mid→R12→inv→far→R13→future-r2→circ→R14→R15.
- No merge `main`. No CloudAgent.

## What this branch changes

1. **Synth defaults** — `generate.py`: `DEFAULT_N=400`, `DEFAULT_TRAIN=320`, `DEFAULT_EVAL=80`, seed `24092447` (was 200 / 160 / 40 / `24092446`).
2. **Hardneg mix** — `unsafe_look_safe` (~22%), `safe_look_unsafe` (~22%), `near_miss_choice` (~16%), baseline remainder (~40%). Meta tag `hardneg_kind` only (not GT).
3. **Re-smoke CPU physics / choose_safest oracle** on expanded eval set.
4. **Probe** — `data/frontier_tip_choose_safest_n_probe.json`.
5. **Freeze** — new choose_safest-n 100% freeze under `data/freeze_manifests/`.

Does **not** reimplement distance / motion / TTI; does **not** write adapters; does **not** fold into tip-cv.

## Metrics (CPU physics oracle, GT-only post-hoc)

| | before (tip @ collision-n) | after (this side) |
|--|----------------------------|-------------------|
| n_eval_seqs | **40** | **80** |
| n_queries | **2850** | **5670** |
| split train/eval | 160 / 40 | 320 / 80 |
| seed | 24092446 | 24092447 |
| hardneg | (baseline only) | mix ~60% hardneg kinds |
| **collision_physics** overall | **100.0%** | **100.0%** |
| **collision_choose_safest** | **100.0%** | **100.0%** |
| inverse_cv overall | 99.82% | 99.86% |
| ablation (phys − inv) | +0.18 pp | +0.14 pp |
| contam self-test | PASS | PASS |
| retrieval train∩eval | ∅ | ∅ |

Horizon breakdown (after):

| predictor | k=1 | k=3 | k=5 | overall |
|-----------|-----|-----|-----|---------|
| **collision_physics** | **100.0** | **100.0** | **100.0** | **100.0** |
| inverse_cv | 99.95 | 99.89 | 99.74 | 99.86 |
| **collision_choose_safest** | **100.0** | **100.0** | **100.0** | **100.0** |

Source: `data/collision_predictive/EVAL_COLLISION_CPU.json`  
Probe: `data/frontier_tip_choose_safest_n_probe.json`

### Honest interpretation

World **is** the elastic-disk simulator → physics / choose_safest @ 100% is the **CPU oracle / own-delta floor** for a future VLM. **Not** a VLM claim. No quantum-advantage claim. Larger n + hardneg mix did **not** drop physics or choose_safest below freeze; **100%** held. Coverage **clearly rose** (40→80 seqs, 2850→5670 queries).

## Floor / freezes

- Distance DZ / motion / TTI: **held by non-touch** (no edits to those modules on this side branch).
- Shared tip router / scaffold paths: **not touched** → tip / mixed floor re-smoke **N/A** (mixed **1.0** assumed held).
- Collision physics + choose_safest freeze: **updated** — prior collision-n freeze retained as history; new `codigo_vivo_tip_choose_safest_n_100pct_*` records n=80 / 5670 @ 100%.
- Metric ≥80% → freeze written (actual **100%**).

## Adapters RO

- `data/lora_adapter/` — **no writes** (`.gitkeep` only on this worktree).
- `data/lora_adapter_collision/` empty (VLM deferred).

## Commands

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-choose-safest-n
/Users/anthony/Documents/quantum-llm-lab/.venv/bin/python examples/collision_predictive/generate.py \
  --n-seq 400 --n-train 320 --n-eval 80 --seed 24092447
/Users/anthony/Documents/quantum-llm-lab/.venv/bin/python examples/collision_predictive/eval_harness.py --contam-self-test
```

## Non-goals / avoided

- No merge to `main` / tip-cv.
- No CloudAgent.
- No write to `data/lora_adapter/`.
- No tip-distance-mid/far / tip-hardneg-r12..r15 / tip-inverse-r3 / tip-circ-expand / tip-future-track* / tip-tti worktrees.
- No fake metrics if physics had dropped.
- **Do not fold** into tip (side-only).

## Blockers

None. Clear coverage rise + floors held → freeze.

