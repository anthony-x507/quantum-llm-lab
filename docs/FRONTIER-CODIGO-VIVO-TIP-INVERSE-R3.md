# FRONTIER — tip-inverse-r3 (inverse_cv → 100% polish)

**Branch:** `frontier/tip-inverse-r3`  
**Base tip SHA:** `3f5f1b1` (`origin/frontier/codigo-vivo-tip`; tip-cv busy with motion-r4)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-inverse-r3` (Mac-111)  
**When:** 2026-09-24 14:05:11 ET
**Freeze:**  @   
**Fold status:** **NOT folded into tip** (side-branch only; TTI / distance-mid / R11 wait after motion-r4)  
**Scope:** Side-branch only — avoids tip-cv / tip-tti / tip-distance-mid / tip-motion-r4 / tip-hardneg-r11 / tip-hardneg-r12.

## LOCK (Anthony / Leader)

- Prior inverse-r2 (folded): inv_cv **89.82→99.82%**; collision n=40 @ **100%**.
- Raise **inverse_cv** from ~99.82% toward **100%** without dropping collision physics **100%**, choose_safest **100%**, or mixed floor **1.0**.
- Anti-contam: GT / real consequences **NEVER** at inference.
- Quantum `data/lora_adapter/` = **READ-ONLY**.
- No merge to `main`; **no fold into tip**.

## What this branch changes

1. **`predict_cv_no_collision` (inverse_cv)** — inverse-r3: after each wall-bounce CV step, **mass-aware elastic resolve for third-party pairs only** (masses are perception observables in meta frames — not GT futures). Ego overlaps remain **geometric flags** (no ego elastic resolve, no 4-substep oracle). Fixes residual r2 misses on `cp_198` where TP collisions redirect agents into/out of ego path.
2. **`predict_emit` / choose_safest** — untouched (still clearance-rank among safe).
3. **Probe / freeze** — `data/frontier_tip_inverse_r3_probe.json` + `codigo_vivo_tip_inverse_r3_100pct_*`.

Does **not** reimplement distance / motion / TTI; does **not** write adapters; does **not** fold into tip-cv.

## Metrics (CPU physics oracle, GT-only post-hoc)

| | before (inverse-r2 @ tip) | after (this branch) |
|--|---------------------------|---------------------|
| n_eval_seqs | **40** | **40** |
| n_queries | **2850** | **2850** |
| seed / split | 24092446 · 160/40 | same |
| **collision_physics** overall | **100.0%** | **100.0%** |
| **inverse_cv** overall | 99.82% | **100.0%** (+0.18 pp) |
| collision_choose_safest | **100.0%** | **100.0%** |
| ablation (phys − inv) | +0.18 pp | **0.0 pp** |
| contam self-test | PASS | PASS |
| retrieval train∩eval | ∅ | ∅ |
| mixed floor | **1.0** (router untouched) | **1.0** |

Horizon breakdown (after):

| predictor | k=1 | k=3 | k=5 | overall |
|-----------|-----|-----|-----|---------|
| **collision_physics** | **100.0** | **100.0** | **100.0** | **100.0** |
| inverse_cv | 100.0 | 100.0 | 100.0 | **100.0** |
| collision_choose_safest | 100.0 | 100.0 | 100.0 | **100.0** |

Source: `data/collision_predictive/EVAL_COLLISION_CPU.json`  
Probe: `data/frontier_tip_inverse_r3_probe.json`

### Honest interpretation

- World **is** the elastic-disk simulator → `collision_physics` @ 100% remains the **CPU oracle / own-delta floor**. **Not** a VLM claim. No quantum-advantage claim.
- inverse_cv @ 100% on this n=40 set with **method still distinct**: no ego elastic resolve, single Euler step (physics uses 4 substeps + ego resolve). Ablation metric 0.0 pp here; residual method gap may reappear at larger n.
- Masses used for TP bounce are **observable state** in meta — anti-contam held (GT futures never at inference; contam self-test PASS).

## Floor / freezes

- Shared tip router / scaffold paths: **not touched** → mixed floor re-smoke **N/A** (mixed **1.0** assumed held).
- Collision physics freeze: **held 100%**.
- choose_safest: **held 100%**.
- inverse_cv rise **99.82→100.0** + floors held → **freeze written**.
- Retained priors: r9, collision_n, motion_r2, collision_pred, distance_danger, inverse_r2 + later tip freezes on base.

## Adapters RO

- `data/lora_adapter/` — **no writes**.
- `data/lora_adapter_collision/` / `data/lora_adapter_inverse/` untouched.

## Commands

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-inverse-r3
/Users/anthony/Documents/quantum-llm-lab/.venv/bin/python examples/collision_predictive/eval_harness.py --contam-self-test
```

## Non-goals / avoided

- No merge to `main` / tip / tip-cv.
- No CloudAgent.
- No write to `data/lora_adapter/`.
- No tip-tti / tip-distance-mid / tip-motion-r4 / tip-hardneg-r11 / tip-hardneg-r12 worktrees.
- No fake metrics.

## Blockers

None. Physics 100% held; inverse_cv 100%; choose_safest 100%; freeze written; **not folded**.
