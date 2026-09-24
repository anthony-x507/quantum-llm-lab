# FRONTIER — tip-inverse-r2 (inverse_cv / choose_safest polish)

**Status:** **FOLDED** into `frontier/codigo-vivo-tip` (rebase `0a1439d`/`7db813f`/`95b1ad6` onto `fabef2b` → content `6b77248` / pins `343d00a`+`5d4d466` FF)  
**Branch:** `frontier/tip-inverse-r2` (rebased; source kept) · tip `frontier/codigo-vivo-tip`  
**Base tip at fold:** `fabef2b` (post R10) · inverse originally from `2d13d0a`  
**When:** polish ~13:43 ET · fold 2026-09-24 13:49:42 ET · Mac-111 (`074c6626-…`)  
**Freeze:** `codigo_vivo_tip_inverse_r2_100pct_20260924_134326`  
**Claim:** NO quantum advantage. CPU elastic-disk physics oracle + action-aware wall-bounce CV only.

## LOCK (Anthony / Leader)

- Tip already has collision physics **100%** @ n=40 and inv_cv ~**89.82%**.
- Raise **inverse_cv** toward **≥95%** without dropping mixed floor **1.0** or collision **100%** freeze.
- Retain freezes **r9**, **collision_n**, **motion_r2**, **collision_pred**, **distance_danger** + priors.
- Anti-contam: GT / real consequences **NEVER** at inference.
- Quantum `data/lora_adapter/` = **READ-ONLY**.
- No merge to `main`. Fold destination is tip-cv only.

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


## FOLDED into tip

**When:** 2026-09-24 13:49:42 ET · Mac-111 (`074c6626-…`)  
**Method:** rebase `frontier/tip-inverse-r2` (`95b1ad6` / feat `0a1439d`; pins `7db813f`+`95b1ad6`) onto tip `fabef2b` → `6b77248`+`343d00a`+`5d4d466`; FF into tip (STATUS kept both motion-r3 fold + inverse side note; relative mixed_unified primary kept).  
**Prior freezes retained (not abandoned):** platform, mlx_r3, post_polish, R5, label_protect, R6, post_od2, R7, **scaffold_motion**, **R8**, **distance_danger**, **collision_pred**, **motion_r2**, **collision_n**, **R9**, **motion_r3**, **R10** `codigo_vivo_tip_r10_100pct_20260924_134615`.  
**Re-smoke:** mixed (d) **1.0**; collision physics **100%** (n=40 / 2850); inverse_cv **99.82%**; choose_safest **100%**; R10 **52/52·44/44**; motion coverage **97.5%** (138 ind + 57 corr); pillars **26/26**; smoke **12/12**; `wired_to_vlm=true`; `gt_leak=false`; `ent_never_on_python=true`.  
**Not folded:** tip-vision-ground / tip-motion-r4 / tip-hardneg-r11 (active — do not fold).  
**Adapters:** `data/lora_adapter/` RO mtime unchanged (2026-09-24 10:57:00).  
**Freeze:** `codigo_vivo_tip_inverse_r2_100pct_20260924_134326` (pinned on tip after fold).

## Non-goals / avoided

- No merge to `main`.
- No CloudAgent.
- No write to `data/lora_adapter/`.
- No tip-vision-ground / tip-motion-r4 / tip-hardneg-r11 worktree writes.
- No fake metrics.

## Blockers

None. Physics 100% held; inverse_cv ≥95%; choose_safest 100%; freeze written.
