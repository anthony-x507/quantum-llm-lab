# FRONTIER — tip-inverse-r2 (inverse_cv / choose_safest polish)

**Branch:** `frontier/tip-inverse-r2`  
**Base tip SHA:** `2d13d0a` (`origin/frontier/codigo-vivo-tip`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-inverse-r2` (Mac-111)  
**When:** 2026-09-24 13:43:26 ET  
**Freeze:** `codigo_vivo_tip_inverse_r2_100pct_20260924_134326` @ `0a1439d`
**Scope:** Side-branch only — does **not** fold into tip; avoids tip-cv / tip-hardneg-r10 / tip-vision-ground / tip-motion-r3 / tip-vision-delta.

## LOCK (Anthony / Leader)

- Tip already has collision physics **100%** @ n=40 and inv_cv ~**89.82%**.
- Raise **inverse_cv** toward **≥95%** without dropping mixed floor **1.0** or collision **100%** freeze.
- Retain freezes **r9**, **collision_n**, **motion_r2**, **collision_pred**, **distance_danger** + priors.
- Anti-contam: GT / real consequences **NEVER** at inference.
- Quantum `data/lora_adapter/` = **READ-ONLY**.
- No merge to `main`; no fold into tip.

## What this branch changes

1. **`predict_cv_no_collision` (inverse_cv)** — action-aware: apply hypo action to ego once, then k-step CV with **wall bounce** (no agent-agent elastic / mass resolve). Mid-horizon geometric pairwise overlap, including **third-party** pairs so consequence family can be `third_party_collision_only` (was the dominant miss: `clear` vs third-party).
2. **`predict_emit(..., choose_safest=True)`** — among physics-safe actions prefer **max min-clearance**, then stable order coast→brake→turn_left→turn_right→accelerate.
3. **Eval harness** — passes hypo `action` into inverse_cv predictor.
4. **Probe / freeze** — `data/frontier_tip_inverse_r2_probe.json` + `codigo_vivo_tip_inverse_r2_100pct_*`.

Does **not** reimplement distance-danger / motion; does **not** write adapters; does **not** fold into tip-cv.

## Metrics (CPU physics oracle, GT-only post-hoc)

| | before (collision_n @ tip) | after (this tip) |
|--|---------------------------|------------------|
| n_eval_seqs | **40** | **40** |
| n_queries | **2850** | **2850** |
| seed / split | 24092446 · 160/40 | same |
| **collision_physics** overall | **100.0%** | **100.0%** |
| **inverse_cv** overall | 89.82% | **99.82%** (+10.00 pp) |
| collision_choose_safest | **100.0%** | **100.0%** |
| ablation (phys − inv) | +10.18 pp | +0.18 pp |
| contam self-test | PASS | PASS |
| retrieval train∩eval | ∅ | ∅ |
| mixed floor | **1.0** (assumed; router untouched) | **1.0** |

Horizon breakdown (after):

| predictor | k=1 | k=3 | k=5 | overall |
|-----------|-----|-----|-----|---------|
| **collision_physics** | **100.0** | **100.0** | **100.0** | **100.0** |
| inverse_cv | 100.0 | 99.79 | 99.68 | **99.82** |
| collision_choose_safest | 100.0 | 100.0 | 100.0 | **100.0** |

Source: `data/collision_predictive/EVAL_COLLISION_CPU.json`  
Probe: `data/frontier_tip_inverse_r2_probe.json`  
Audit: `data/eval_audit/collision_20260924_134302.jsonl`

### Honest interpretation

- World **is** the elastic-disk simulator → `collision_physics` @ 100% remains the **CPU oracle / own-delta floor**. **Not** a VLM claim. No quantum-advantage claim.
- Raising inverse_cv shrinks ablation (+10.18 → +0.18 pp): the stronger CV baseline still **never** resolves elastic masses; residual miss is the honest collision-layer delta.
- Dominant pre-fix miss was family mismatch `clear` vs `third_party_collision_only` (ego-safe but other agents overlap under CV) — fixed by pairwise geometric checks without elastic resolve.

## Floor / freezes

- Shared tip router / scaffold paths: **not touched** → tip / mixed floor re-smoke **N/A** (mixed **1.0** assumed held).
- Collision physics freeze: **held 100%** (prior `codigo_vivo_tip_collision_n_100pct_*` retained).
- inverse_cv rise **89.82→99.82** (≥95% target) and ≥80% hold → **freeze written**.
- Retained: r9, collision_n, motion_r2, collision_pred, distance_danger + priors.

## Adapters RO

- `data/lora_adapter/` — **no writes** (`.gitkeep` mtime unchanged).
- `data/lora_adapter_collision/` / `data/lora_adapter_inverse/` untouched (VLM deferred).

## Commands

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-inverse-r2
/Users/anthony/Documents/quantum-llm-lab/.venv/bin/python examples/collision_predictive/generate.py \
  --n-seq 200 --n-train 160 --n-eval 40 --seed 24092446
/Users/anthony/Documents/quantum-llm-lab/.venv/bin/python examples/collision_predictive/eval_harness.py --contam-self-test
```

## Non-goals / avoided

- No merge to `main` / tip / tip-cv.
- No CloudAgent.
- No write to `data/lora_adapter/`.
- No tip-hardneg-r10 / tip-vision-ground / tip-motion-r3 / tip-vision-delta worktrees.
- No fake metrics.

## Blockers

None. Physics 100% held; inverse_cv ≥95%; choose_safest 100%; freeze written.
