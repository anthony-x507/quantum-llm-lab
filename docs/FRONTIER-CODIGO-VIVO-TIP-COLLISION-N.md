# FRONTIER — tip-collision-n (expand collision-pred eval n)

**Branch:** `frontier/tip-collision-n`  
**Base tip SHA:** `763fb8c` (`frontier/codigo-vivo-tip`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-collision-n` (Mac-111)  
**When:** 2026-09-24 13:25:59 ET  
**Freeze:** `codigo_vivo_tip_collision_n_100pct_20260924_132559` @ `c79ab1a`  
**Scope:** Side-branch only — does **not** touch tip-cv / tip-hardneg-r9 / tip-motion-r2 / tip-distance-danger.

## LOCK (Anthony / Leader)

- Collision already FOLDED on tip @ `4fe070e` lineage; **freeze 100% physics** but n=8 / 555 queries flagged **thin**.
- Expand synth/eval sequences (**≥40 eval** if feasible); hold **≥80%** (ideally ~100%) physics.
- Anti-contam: real consequences **NEVER** at inference (GT only for eval).
- Quantum `data/lora_adapter/` = **READ-ONLY**. New adapters → `data/lora_adapter_collision/` only.
- Distance-danger stubs OK (consume estimates; do not reimplement).
- Mixed floor **1.0** if re-smoke; this branch does not abandon collision 100% freeze — if metric drops below 80% on larger n, report honestly and reinforce; **never fake**.

## What this branch changes

1. **Synth defaults** — `generate.py`: `DEFAULT_N=200`, `DEFAULT_TRAIN=160`, `DEFAULT_EVAL=40`, seed `24092446` (was 40 / 32 / 8 / `24092445`).
2. **Re-smoke CPU physics oracle** on expanded eval set.
3. **Probe** — `data/frontier_tip_collision_n_probe.json` (+ synced pred probe path).
4. **Freeze** — new n-expand 100% freeze under `data/freeze_manifests/`.

Does **not** reimplement distance-danger; does **not** write adapters; does **not** fold into tip-cv.

## Metrics (CPU physics oracle, GT-only post-hoc)

| | before (folded) | after (this tip) |
|--|-----------------|------------------|
| n_eval_seqs | **8** | **40** |
| n_queries | **555** | **2850** |
| split train/eval | 32 / 8 | 160 / 40 |
| seed | 24092445 | 24092446 |
| **collision_physics** overall | **100.0%** | **100.0%** |
| inverse_cv overall | 85.23% | 89.82% |
| collision_choose_safest | 100.0% | 100.0% |
| ablation (phys − inv) | +14.77 pp | +10.18 pp |
| contam self-test | PASS | PASS |
| retrieval train∩eval | ∅ | ∅ |

Horizon breakdown (after):

| predictor | k=1 | k=3 | k=5 | overall |
|-----------|-----|-----|-----|---------|
| **collision_physics** | **100.0** | **100.0** | **100.0** | **100.0** |
| inverse_cv | 96.42 | 89.89 | 83.16 | 89.82 |
| collision_choose_safest | 100.0 | 100.0 | 100.0 | 100.0 |

Source: `data/collision_predictive/EVAL_COLLISION_CPU.json`  
Probe: `data/frontier_tip_collision_n_probe.json`  
Audit: `data/eval_audit/collision_20260924_132553.jsonl`

### Honest interpretation

World **is** the elastic-disk simulator → `collision_physics` @ 100% is the **CPU oracle / own-delta floor** for a future VLM. **Not** a VLM claim. No quantum-advantage claim. Larger n did **not** drop physics below freeze; 100% held. Inverse_cv remains the ablation floor (~90% overall at n=40).

## Floor / freezes

- Shared tip router / scaffold paths: **not touched** → tip / mixed floor re-smoke **N/A** (mixed **1.0** assumed held).
- Collision physics freeze: **updated** — prior n=8 freeze retained as history; new `codigo_vivo_tip_collision_n_100pct_*` records n=40 / 2850 @ 100%.
- Metric ≥80% → freeze written (actual **100%**).

## Adapters RO

- `data/lora_adapter/` — **no writes** (`.gitkeep` only on this worktree).
- `data/lora_adapter_collision/` empty (VLM deferred).

## Commands

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-collision-n
/Users/anthony/Documents/quantum-llm-lab/.venv/bin/python examples/collision_predictive/generate.py \
  --n-seq 200 --n-train 160 --n-eval 40 --seed 24092446
/Users/anthony/Documents/quantum-llm-lab/.venv/bin/python examples/collision_predictive/eval_harness.py --contam-self-test
```

## Non-goals / avoided

- No merge to `main` / tip-cv.
- No CloudAgent.
- No write to `data/lora_adapter/`.
- No tip-hardneg-r9 / tip-motion-r2 / tip-distance-danger worktrees.
- No fake metrics if physics had dropped.

## Blockers

None for this expand. Physics held 100% at n=40.
