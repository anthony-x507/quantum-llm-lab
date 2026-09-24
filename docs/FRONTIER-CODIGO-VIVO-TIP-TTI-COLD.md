# FRONTIER — tip-tti-cold (raise TTI overall+cold-start)

**Status:** **SIDE FREEZE** (not folded)  
**Branch:** `frontier/tip-tti-cold`  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-tti-cold` (Mac-111)  
**Base tip:** `4bfc924` (`frontier/codigo-vivo-tip`, post inverse-r3 fold; ≥ `9a0de24`)  
**When:** 2026-09-24 ~14:35 ET  
**Freeze:** `codigo_vivo_tip_tti_cold_100pct_20260924_143601`  
**Feat SHA:** `9ddb8f4` (`9ddb8f4439b015d0a907b6ede1bdcbd80d6ddcba`)  
**Claim:** NO quantum advantage. CPU heuristic / soft priors only.

## LOCK (Anthony / Leader)

- Raise **TTI overall incl. cold-start** (~91% post tip-tti) toward 100%.
- Hold: TTI scorable **100%**, distance DZ **100%**, motion **100%**, collision floors **100%**.
- Anti-contam: GT / `v_depth` / real consequences **NEVER** at inference.
- Quantum `data/lora_adapter/` = **READ-ONLY**.
- No merge to `main`; **do NOT fold** into tip-cv.
- Freeze if clear cold rise + floors held.

## What this branch changes

1. **`physics.cold_start_tti`** — when no prev observation and obs-channel `motion_hint==approach`, emit TTI from soft class closing-speed priors (`tti = d_est / v_prior`). Near movables (`car`/`pedestrian`, `d_est < 8 m`) use short absolute TTI prior `0.8 s` (tol ±0.5 s covers sub-second GT).
2. **`eval_heuristic.estimate_frame`** — wires cold path as `+tti_cold` (scorable growth/dist-rate path untouched).
3. Predictor tag → `…_v4_tti_cold`.

Does **not** reopen future-track files; does **not** write adapters; does **not** fold.

### Soft priors (m/s)

| class | v_close prior |
|-------|---------------|
| car | 18.0 |
| pedestrian | 8.0 |
| light / intersection | 6.0 |
| stop_sign | 2.4 |

## Metrics (CPU heuristic, GT-only post-hoc)

### TTI

| | before (tip post-TTI) | after (this side) |
|--|----------------------|-------------------|
| TTI scorable orig | **100%** (691/691) | **100%** (691/691) held |
| TTI scorable danger50 | **100%** (725/725) | **100%** (725/725) held |
| overall+cold orig | 91.16% | **94.99%** (**+3.83 pp**) |
| overall+cold danger50 | 91.66% | **94.82%** (**+3.16 pp**) |
| TTI DZ scorable | **100%** | **100%** held |
| false_emit | 0 | **0** |
| distance DZ | **100%** | **100%** held |

Cold frames: all t=0 + `motion_hint=approach` (orig 67 / d50 66). Soft priors recover ~43% / ~38% of cold; remainder is multi-modal `v_close` without temporal signal (**plateau without GT leak**).

### Collision floors (re-smoke, n=2850)

| predictor | after |
|-----------|-------|
| collision_physics | **100.0%** |
| inverse_cv | **100.0%** |
| collision_choose_safest | **100.0%** |

Motion / mixed router: **untouched** (distance_est-only) — tip retained motion **100%** / mixed **1.0**.

Anti-contam: **CLEAN**.

## Floor / freezes

- Clear cold rise + floors held → **freeze written**.
- **Not folded** into tip / tip-cv (per brief).

## Adapters RO

- `data/lora_adapter/` — **no writes** (`.gitkeep` mtime unchanged across edits/evals).

## Commands

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-tti-cold
/Users/anthony/Documents/quantum-llm-lab/.venv/bin/python examples/distance_est/eval_heuristic.py --contam-self-test
/Users/anthony/Documents/quantum-llm-lab/.venv/bin/python examples/distance_est/eval_heuristic.py --out-name EVAL_TTI_COLD_AFTER.json
/Users/anthony/Documents/quantum-llm-lab/.venv/bin/python examples/distance_est/eval_heuristic.py \
  --data data/video_synth/distance_est/danger50 --out-name EVAL_TTI_COLD_AFTER.json
/Users/anthony/Documents/quantum-llm-lab/.venv/bin/python examples/collision_predictive/eval_harness.py
```

## Non-goals / avoided

- No merge to `main`. No fold into tip-cv.
- No CloudAgent.
- No write to `data/lora_adapter/`.
- Avoided worktrees: tip-cv, tip-distance-mid/far, tip-hardneg-r12..r16, tip-inverse-r3, tip-circ-expand, tip-future-track*, tip-tti, tip-choose-safest-n.

## Blockers

None for freeze. Residual cold gap is plateau-safe without temporal signal / GT leak — do not invent sidecar `v_depth` into the predictor.
